---
name: wechat-draft-publisher
display_name: 公众号草稿推送
display_name_en: WeChat Draft Publisher
description: "将本地 HTML 文章推送到微信公众号草稿箱。"
description_zh: "将本地 HTML 文章（含 base64 内嵌图片）推送到微信公众号草稿箱，自动上传图片素材并创建草稿，供后台手动发布。"
description_en: "Push local HTML articles (with base64 images) into the WeChat official account draft box."
category: 办公协同
version: 1.0.0
author: 老李
---

# 公众号草稿推送

将写好的 HTML 文章推送到微信公众号草稿箱，含图片自动上传 + 素材库管理 + 草稿创建。

## 公众号信息

- AppID: `YOUR_APPID`
- AppSecret: `YOUR_APPSECRET`
- 类型: 订阅号
- 发布方式: API 创建草稿 → 后台手动发布（方案 B）

## 使用流程

### 第 1 步：准备 HTML 文章

文章 HTML 必须满足：
- **0 个 `<style>` 标签** — 所有样式用内联 `style=""`
- **不用 `class=""`** — 微信编辑器全部过滤
- **不用 CSS 伪元素** — `::before`、`::after` 不支持
- **图片用 base64 内嵌** — `<img src="data:image/png;base64,..." />`
- **标题放在 `<title>` 标签中**

关键尺寸限制：
- 标题: ≤ 64 个中文字符（实测 API 上限）
- 摘要: 约 50 字节 UTF-8

### 第 2 步：推送草稿（标准模板）

创建 `push_draft.py`：

```python
"""将本地HTML文章推送到公众号草稿箱"""
import re, sys, io, base64, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 加载模块
sys.path.insert(0, os.path.expanduser("~/.workbuddy/skills/wechat-draft-publisher/scripts"))
from wechat_publisher import WeChatPublisher

APPID = "YOUR_APPID"
APPSECRET = "YOUR_APPSECRET"
ARTICLE_HTML = "文章.html"

wp = WeChatPublisher(APPID, APPSECRET)

# 1. 读取 HTML
with open(ARTICLE_HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# 2. 提取 title
title_match = re.search(r'<title>(.+?)</title>', html)
title = title_match.group(1) if title_match else "未命名"

# 3. 提取摘要（第一段正文，限58字）
first_p_match = re.search(r'<p>(.+?)</p>', html)
digest = first_p_match.group(1) if first_p_match else ""
digest = re.sub(r'<[^>]+>', '', digest)
if len(digest) > 58:
    digest = digest[:58] + "..."

# 4. 上传 base64 图片并替换为微信 URL
base64_imgs = re.findall(r'src="data:image/png;base64,([^"]+)"', html)
for i, b64 in enumerate(base64_imgs):
    tmp_path = f".wechat_cache/_upload_{i}.png"
    os.makedirs(".wechat_cache", exist_ok=True)
    with open(tmp_path, "wb") as f:
        f.write(base64.b64decode(b64))
    wx_url = wp.upload_image(tmp_path)
    html = html.replace(f'data:image/png;base64,{b64}', wx_url)
    os.remove(tmp_path)

# 5. 提取 body 内容
body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
content_html = body_match.group(1).strip() if body_match else html

# 6. 创建草稿
media_id = wp.create_draft(title=title, content=content_html, digest=digest)

print(f"DONE - media_id: {media_id}")
print("去公众号后台「草稿箱」手动发布")
```

### 第 3 步：运行推送

```bash
python push_draft.py
```

### 第 4 步：后台发布

登录 mp.weixin.qq.com → 草稿箱 → 预览确认 → 手动点发布

## 踩坑清单

### 致命坑
1. **IP 白名单**: 服务器 IP 必须在公众号后台「设置与开发 → 基本配置 → IP 白名单」中
2. **标题长度**: 超过 64 个中文字符返回 errcode=45003
3. **编码**: 必须用 `ensure_ascii=False` + UTF-8 编码，否则中文变 `\uXXXX`
4. **不要 `<style>` 标签**: 微信编辑器全部过滤，只能用内联 `style=""`

### 编码正确写法
```python
payload = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
resp = requests.post(url, data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30).json()
```

### Windows 终端乱码修复
```python
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
```

## WeChatPublisher 类方法

| 方法 | 用途 |
|------|------|
| `get_token()` | 获取 access_token（自动缓存+刷新） |
| `upload_image(path)` | 上传图文内图片，返回微信 URL |
| `create_draft(title, content, digest=, author=)` | 创建草稿，返回 media_id |
| `delete_draft(media_id)` | 删除草稿 |
| `list_drafts()` | 列出草稿箱中所有草稿 |
| `get_or_create_cover(path)` | 获取/生成封面 thumb_media_id |

## 脚本位置

- 核心类: `scripts/wechat_publisher.py`
- 推送模板: 上面的 `push_draft.py` 模板（每篇文章各自创建）
