# WeChat Draft Push — Gotchas & Checklist

Concrete failure modes seen in real pushes, with fixes. Read this before debugging a failed push.

## 1. IP whitelist — errcode 40164
**Symptom:** `{"errcode":40164,"errmsg":"invalid ip <IP> ... not in whitelist"}` on the token call.
**Cause:** The Official Account has "API 调用 IP 白名单" enabled (设置与开发 → 基本配置 → IP白名单), and the agent's outbound IP is not listed.
**Fix:** Add the exact IP from the error message to the whitelist and retry. The IP is the agent environment's egress IP and may change between sessions — if it fails again, re-read the new IP from the error and add it.

## 2. GET instead of POST — errcode 43002
**Symptom:** `{"errcode":43002,"errmsg":"require POST method"}` on cover upload or draft creation.
**Cause:** The HTTP client sent GET even though a request body was attached. With Python `urllib`, explicitly setting `method="GET"` while passing `data` causes this.
**Fix:** Leave `method` unset when a body is present — urllib auto-uses POST. Never force GET on a data-carrying request. (The bundled `wx_draft_push.py` already does this correctly.)

## 3. Title length — max 64 bytes
The `title` field is limited to **64 bytes** (≈21 Chinese characters; Latin letters/digits count as 1 byte each, Chinese as 3 bytes). The article's in-body title (inside the HTML hero card) can be longer — only the draft/share-card `title` param is constrained.
**Practice:** Use a short draft title (e.g. the first clause of the article title) and keep the full title inside the HTML body.

## 4. Digest length — max 120 characters
Optional. If omitted, WeChat auto-takes the first part of the content. Keep it under 120 chars.

## 5. Credentials handling (security)
- Read AppID/AppSecret from env vars `WECHAT_APPID` / `WECHAT_SECRET` — never hardcode or write them to logs/memory.
- If the user pastes them in chat, use them only for that session's process and discard.
- Recommend the user set them persistently (`export` in shell profile) or, if concerned about exposure, reset AppSecret afterward (旧 secret 立即失效).

## 6. access_token validity
- Valid 7200s (2h). Re-fetch per push; do not cache long-term.
- One token is enough for the whole push (token → cover → draft in one run).

## 7. Cover image
- Optional. WeChat cover display ratio is 2.35:1 (900×383) for the large card; the API accepts any image and crops. Generate a wide composition (e.g. 1536×1024 via ImageGen) so cropping loses little.
- ImageGen size options are limited to 1024x1024 / 1024x1536 / 1536x1024 — use 1536x1024 (widest) for covers.
- Omit `--cover` to push without a thumbnail if generation is undesirable.

## 8. Body HTML constraints
- All styles must be inline (`style="..."`); WeChat strips `<style>` blocks.
- Images inside the article must use the `mmbiz.qpic.cn` domain (upload them via material API first if needed).
- The olive-journal / gzh-design output (pure `<section>` + `<span leaf>` inline styles) pastes cleanly.

## 9. Windows encoding
When running the script under PowerShell/cmd, GBK stdout can crash on emoji/non-ASCII prints. Set `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1` before invoking python.
