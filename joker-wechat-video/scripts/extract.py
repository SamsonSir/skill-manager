#!/usr/bin/env python3
"""Local video probe, dense OCR and evidence export. Does not claim semantic completion."""
import argparse, json, subprocess, pathlib, difflib

def run(args, **kw):
    return subprocess.run(args, check=True, **kw)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('video'); p.add_argument('--output', required=True)
    p.add_argument('--fps', type=float, default=2)
    p.add_argument('--ocr-jsonl', help='Reuse prior batch OCR evidence')
    a=p.parse_args(); out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    if a.fps<=0: p.error('fps must be positive')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',a.video]))
    (out/'probe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2))
    if not any(s['codec_type']=='video' for s in probe['streams']):raise RuntimeError('No video stream')
    if a.ocr_jsonl: raw=pathlib.Path(a.ocr_jsonl)
    else:
        frames=out/'frames';frames.mkdir(exist_ok=True)
        run(['ffmpeg','-v','error','-i',a.video,'-vf',f'fps={a.fps}','-q:v','2',str(frames/'frame-%05d.jpg')])
        binary=out/'vision-ocr'
        run(['swiftc','-O',str(pathlib.Path(__file__).with_name('ocr.swift')),'-o',str(binary)])
        raw=out/'ocr.jsonl'
        with raw.open('w') as f:run([str(binary),*map(str,sorted(frames.glob('frame-*.jpg')))],stdout=f)
    records=[json.loads(s) for s in raw.read_text().splitlines() if s.strip()]
    sections=[]
    for i,r in enumerate(records):
        r['time']=(int(pathlib.Path(r['file']).stem.split('-')[-1])-0.5)/a.fps
        text='\n'.join(x['text'] for x in r.get('lines',[]))
        # Keep full text of every changed screen, never shorten image prose.
        if not sections or difflib.SequenceMatcher(None,text,sections[-1]['text']).ratio()<.96:
            sections.append({'time':r['time'],'file':r['file'],'text':text,'lines':r.get('lines',[]),'error':r.get('error')})
    (out/'screens.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2))
    md=['# 画面文字机器识别','以下内容尚需视觉核对；字幕、页面文字和图片文字可能混合。']
    for r in sections:
        md += [f"\n## {r['time']:.2f} 秒",f"来源：{r['file']}",r['text'] or '[未识别到文字]']
    (out/'画面文字-机器识别.md').write_text('\n\n'.join(md))
    duration=float(probe['format']['duration'])
    status={'duration':duration,'fps':a.fps,'ocr_frames':len(records),'changed_screens':len(sections),'ocr_errors':sum('error'in r for r in records),'review_complete':False,'coverage_note':'Fixed-rate sampling cannot guarantee sub-frame transient text; inspect scene changes and unreadable regions.'}
    (out/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2));print(json.dumps(status))
if __name__=='__main__':main()
