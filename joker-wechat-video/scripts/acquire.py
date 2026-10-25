#!/usr/bin/env python3
"""Resolve Yuanbao's authenticated parse response and verify playable media."""
import argparse,json,pathlib,urllib.request,urllib.parse,subprocess,os

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--parse-file',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    os.umask(0o077)
    out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    d=json.loads(pathlib.Path(a.parse_file).read_text())
    d=d.get('data',d)
    if d.get('code')!=0:raise RuntimeError('Authenticated parse failed')
    d=d['data'];q=urllib.parse.parse_qs(urllib.parse.urlparse(d['playable_url']).query)
    payload={'baseReq':{'generalToken':q['token'][0]},'exportId':q['eid'][0]}
    req=urllib.request.Request('https://channels.weixin.qq.com/finder-preview/api/feed/get_feed_info',json.dumps(payload).encode(),{'Content-Type':'application/json','Referer':d['playable_url'],'Origin':'https://channels.weixin.qq.com','User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:feed=json.load(r)
    if feed.get('errCode',0)!=0:raise RuntimeError('Channels feed request failed')
    f=feed['data']['feedInfo'];u=f.get('h264VideoInfo',{}).get('videoUrl') or f.get('videoUrl')
    if not u:raise RuntimeError('No video URL; inspect image-post metadata separately')
    video=out/'video.mp4'
    if video.exists():raise FileExistsError('Refuse to replace existing video; use a new output directory')
    with urllib.request.urlopen(u,timeout=60) as r,video.open('wb') as o:
        while b:=r.read(1024*1024):o.write(b)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
    if not any(s.get('codec_type')=='video' for s in probe['streams']):raise RuntimeError('Downloaded file is not playable video')
    # Full decoding detects truncated downloads; metadata alone is insufficient.
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
    metadata={'author':feed['data'].get('authorInfo',{}).get('nickname'),'description':f.get('description'),'duration':probe['format']['duration'],'file':str(video),'decode_verified':True}
    (out/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2));print(json.dumps(metadata,ensure_ascii=False))
if __name__=='__main__':main()
