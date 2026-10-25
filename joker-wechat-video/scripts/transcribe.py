#!/usr/bin/env python3
"""Apple Silicon local Whisper with timestamp evidence."""
import argparse,json,pathlib
def main():
    p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--output',required=True)
    p.add_argument('--model',default='mlx-community/whisper-large-v3-turbo');a=p.parse_args()
    import mlx_whisper
    out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    r=mlx_whisper.transcribe(a.video,path_or_hf_repo=a.model,language='zh')
    (out/'transcript.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
    lines=['# 口播逐段机器转写','保留时间戳；专名、同音字和数字需与音频及画面交叉核对，不能当作已逐字人工校对。']
    for s in r['segments']:lines.append(f"\n[{s['start']:.2f}–{s['end']:.2f} 秒] {s['text']}")
    (out/'口播逐段-机器转写.md').write_text('\n\n'.join(lines))
    print(json.dumps({'segments':len(r['segments']),'last_end':r['segments'][-1]['end'] if r['segments'] else None,'characters':len(r['text'])}))
if __name__=='__main__':main()
