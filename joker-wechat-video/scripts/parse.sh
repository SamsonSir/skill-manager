#!/bin/sh
set -eu
if [ "$#" -ne 2 ]; then
  echo 'Usage: parse.sh https://weixin.qq.com/sph/ID /absolute/private-output.json' >&2
  exit 2
fi
{
/usr/bin/python3 -c 'import json,sys;print("const input="+json.dumps({"url":sys.argv[1],"dest":sys.argv[2]})+";")' "$1" "$2"
cat <<'EOF'
const fs=await import('node:fs');
const path=await import('node:path');
if (!/^https:\/\/weixin\.qq\.com\/sph\/[A-Za-z0-9_-]+$/.test(input.url)) throw new Error('Expected a WeChat sph HTTPS link');
if (!path.isAbsolute(input.dest)) throw new Error('Output must be absolute');
const task=await useOrCreateTaskSpace('Joker视频号解析');
await openOrReuseTab('https://yuanbao.tencent.com/',{wait:true,timeout:20});
const result=await js(`(async()=>{
 const r=await fetch('/api/weixin/get_parse_result',{
 method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({type:'video_channel_url',url:${JSON.stringify(input.url)},scene:1})
 });return {status:r.status,data:await r.json()};
})()`);
fs.mkdirSync(path.dirname(input.dest),{recursive:true,mode:0o700});
fs.writeFileSync(input.dest,JSON.stringify(result),{mode:0o600,flag:'wx'});
cliLog({taskSpace:task.id,status:result.status,code:result.data?.code,msg:result.data?.msg,parseSaved:result.status===200 && result.data?.code===0});
EOF
} | ego-browser nodejs
