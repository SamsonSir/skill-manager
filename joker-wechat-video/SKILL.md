---
name: joker-wechat-video
description: 解析微信视频号 sph 分享链接，取得并验证可播放视频，提取完整语音、字幕与画面图片文案，按时间码核对和交付。适合用户粘贴历史视频号链接后询问视频正文或图片完整文字；使用已授权的腾讯元宝登录态，不上传微信数据库或数据库密钥。
---

# Joker 视频号正文与图片文案

## 当前状态

链接解析、下载、全片解码、语音转写及画面OCR已通过真实用例验证，见 `references/validation.md`。源画面被遮挡的文字不能保证恢复；必须把运行完成和文字无缺口分开报告。

## 获取视频

优先复用用户已授权的腾讯元宝登录态。跨站登录未获授权时说明目的并询问；验证码和手机扫码交由用户。用 ego-browser 时先读取其 SKILL.md，沿用已有空间和元宝页，不关闭用户其他标签。

用户已授权复用元宝登录态时，优先使用实测入口：

```bash
sh scripts/parse.sh 'https://weixin.qq.com/sph/ID' /absolute/private-scratch/parse-private.json
python3 scripts/acquire.py --parse-file /absolute/private-scratch/parse-private.json --output NEW_OUTPUT_DIRECTORY
```

parse.sh 使用专属 ego 空间“Joker视频号解析”，不覆盖已有输出。失败时留在登录页供用户处理；成功后同一轮任务完成时按 ego 技能关闭本次专属空间，用户原有空间与标签不得关闭。

接口变化需要诊断时，在元宝页面的浏览器上下文调用下列接口；公开分享链接可发送给腾讯，私聊数据库和数据库密钥不可发送。凭据、签名媒体地址、接口原始响应只留本机任务私有 scratch，不写入技能、报告或公开日志。

```javascript
const d = await js(`(async()=>{
 const r=await fetch('/api/weixin/get_parse_result',{
  method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({type:'video_channel_url',url:SAFE_JSON_URL,scene:1})
 }); return {status:r.status,data:await r.json()};
})()`);
// SAFE_JSON_URL 用 JSON.stringify(已校验的 https://weixin.qq.com/sph/... 链接) 替换。
// 在 ego 的 Node 上下文用 import('node:fs') 将 d 保存为 mode 0600 的 parse-private.json。
// 只输出状态码和字段名称，不打印整个响应。
```

用 Python 3.10+ 执行：

```bash
python3 scripts/acquire.py --parse-file PRIVATE_PARSE_JSON --output NEW_OUTPUT_DIRECTORY
```

401 表示登录态失效；code 非0表示解析失败。下载成功不等于解密成功：脚本必须 ffprobe 成功且 ffmpeg 全片解码通过。数据库密钥只用于本机记录，不可当作视频 decodeKey。若返回加密文件，保留诊断，查当前解析接口变化，不猜 seed、不反复取数据库钥、不安装拦截证书或改系统代理。

## 内容提取与完整性

1. Apple Silicon 优先使用实测 MLX 路径：`uv run --python 3.12 --with mlx-whisper python scripts/transcribe.py VIDEO --output OUTPUT`。模型默认 `mlx-community/whisper-large-v3-turbo`，复用本机缓存；可用 `--model LOCAL_MODEL_DIRECTORY` 指定已有模型。不要同时启动CPU与MLX大模型造成资源争抢。其他环境读取 local-whisper 技能，保留时间戳 JSON。无音轨则跳过，不能虚构转写。机器转写须结合画面校对专名，不将机器转写声称为逐字人工核对。
2. `python3 scripts/extract.py VIDEO --output NEW_DIRECTORY`：默认每秒2帧，macOS Vision 批量OCR，保留文字、真实置信度、坐标和帧来源。脚本结果是机器识别证据，不自动等于完整文案。
3. 查看整片时间覆盖及变化画面，另用 ffmpeg 场景切换检测找短暂页面；对切换附近加密抽帧，避免固定采样漏掉闪现文字。各独立图片/幻灯片选择最清晰完整帧。
4. 图片长文按阅读顺序逐字复核；字体小的区域放大或裁切后再识别，可使用 super-ocr 的第二引擎。滚动页面用相邻帧重叠文字拼接，保留真实顺序，不删除看似重复但实际不同的句子。
5. 对照原画面核对开头结尾、每行、列表序号、数字、标点和遮挡处。低置信度不能直接补写。无法读清、从未完整显示、被遮挡的文字明确标 `[无法辨认]` 或 `[画面未展示]`，说明时间段和具体缺口。不能承诺任何视频都能无损恢复原图文字。
6. 分开交付“语音正文”“图片/页面文案全文”“内容总结”；字幕如果只是语音重复，可在整理正文去重，但原始证据仍保留。不能只给摘要冒充全文。

## 交付与恢复

保存可播放视频、语音时间戳JSON、全部OCR证据、选定关键帧及完整报告。报告链接回用户源URL；公开报告不包含私聊成员或签名参数。处理第三方视频不自动当作个人AI原创归档。

技能运行状态至少区分：登录待完成、视频获取失败、可播放视频已验证、提取进行中、存在文字缺口、完整核对通过。保存真实断点，不在失败时重新下载或重跑已成功部分；未通过本例验收不得把技能描述为已成熟跑通。

临时文件遵守本机 AEG scratch；任务失败保留诊断及有效成果。不要清理用户原件、其他账号或其他任务的文件。
