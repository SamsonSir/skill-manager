---
name: wechat-draft-push
description: 'Push an article (HTML) into a WeChat Official Account (微信公众号) draft box via the WeChat API. Use when the user says "发布到公众号", "推送到公众号", "发到公众号", "上传到公众号", "发布文章", or wants a finished HTML article uploaded as a draft. Handles access_token, optional cover-image upload, and draft creation end-to-end. Credentials are read from WECHAT_APPID / WECHAT_SECRET env vars.'
version: 1.0.0
display_name: "公众号草稿推送"
display_name_en: "WeChat Draft Push"
description_zh: "通过微信公众号 API 将 HTML 文章推送到草稿箱，支持封面图上传、access_token 管理，凭据从环境变量读取。"
description_en: "Push HTML articles to WeChat Official Account draft box via API, with optional cover image upload and env-var credential management."
---

# WeChat Draft Push

Upload a finished HTML article to a WeChat Official Account draft box (草稿箱), optionally with a generated cover image. This is the "publish" step that follows article writing/typesetting (e.g. the gzh-design / olive-journal output).

## Workflow

1. **Collect parameters.** Required: `--html <path>` (the article HTML, inline styles only), `--title` (short, ≤64 bytes), `--digest` (≤120 chars). Optional: `--cover <img>` (local cover image path).
2. **Get credentials.** Read `WECHAT_APPID` and `WECHAT_SECRET` from env. If missing, ask the user to provide them (or set env vars and retry). Do NOT hardcode or log secrets.
3. **(Optional) Generate cover.** If no cover supplied and one is wanted, use ImageGen to make a wide (1536×1024) on-brand cover and save it locally.
4. **Push.** Run the bundled script:
   ```
   python scripts/wx_draft_push.py --html <path> --title "<title>" --digest "<digest>" [--cover <img>]
   ```
   Pass credentials via env in the same command (PowerShell example):
   ```
   $env:WECHAT_APPID="..."; $env:WECHAT_SECRET="..."; $env:WECHAT_AUTHOR="映星视界"; $env:PYTHONIOENCODING="utf-8"; $env:PYTHONUTF8="1"
   & python scripts/wx_draft_push.py --html article.html --title "短标题" --digest "摘要" --cover cover.png
   ```
5. **Report.** On `DRAFT_OK media_id: ...`, tell the user to open mp.weixin.qq.com → 内容管理 → 草稿箱, preview, then publish. The API does not return a direct article URL.

## Parameters
- `title` — draft/share-card title, **≤64 bytes** (≈21 Chinese chars). Keep the full title inside the HTML body; use a short clause here.
- `digest` — share-card summary, ≤120 chars. Optional.
- `content_html` — the article HTML. Must use inline styles; WeChat strips `<style>`. The gzh-design olive-journal output is compatible.
- `cover_image_path` — local image. Optional; if omitted, draft has no thumbnail.

## Known failure modes
Read [references/gotchas.md](references/gotchas.md) when a push fails. The big two:
- **40164 invalid ip** → add the agent's egress IP to the account's API IP whitelist (设置与开发 → 基本配置 → IP白名单).
- **43002 require POST** → the HTTP client sent GET with a body; the bundled script already avoids this.

## Security
- Credentials come from env vars only. Never store AppID/AppSecret in memory files or logs.
- If the user pastes a secret in chat, use it for the session and suggest resetting it afterward.
