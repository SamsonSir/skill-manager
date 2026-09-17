"""
微信公众号半自动发布工具（方案 B）
工作流：本地写好文章 → 脚本推送到草稿箱 → 后台手动点发布
"""

import json
import struct
import sys
import time
import zlib
import requests
from pathlib import Path

# 注意：不要在模块级重定向 stdout，import 时会导致 conflict

CACHE_DIR = Path(__file__).parent / ".wechat_cache"
TOKEN_FILE = CACHE_DIR / "token.json"
THUMB_FILE = CACHE_DIR / "thumb_media_id.txt"


class WeChatPublisher:
    """公众号草稿管理"""

    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret
        self._token = None
        self._expires_at = 0
        CACHE_DIR.mkdir(exist_ok=True)

    # ═══════════════════════════════ Token ═══════════════════════════════

    def get_token(self):
        """access_token 带缓存，过期自动刷新"""
        self._load_token_cache()
        now = time.time()
        if self._token and now < self._expires_at - 300:
            return self._token

        resp = requests.get(
            "https://api.weixin.qq.com/cgi-bin/token",
            params={"grant_type": "client_credential",
                    "appid": self.appid, "secret": self.secret},
            timeout=10
        ).json()
        if "access_token" not in resp:
            raise RuntimeError(f"Token 获取失败: {resp}")
        self._token = resp["access_token"]
        self._expires_at = now + resp["expires_in"]
        TOKEN_FILE.write_text(json.dumps({"token": self._token, "expires_at": self._expires_at}))
        print(f"[Token] 已刷新，有效期 {resp['expires_in']}s")
        return self._token

    def _load_token_cache(self):
        if TOKEN_FILE.exists():
            d = json.loads(TOKEN_FILE.read_text())
            self._token = d.get("token")
            self._expires_at = d.get("expires_at", 0)

    # ═══════════════════════════════ 封面图 ═══════════════════════════════

    def get_or_create_cover(self, image_path=None, color=None):
        """获取封面 thumb_media_id（优先缓存 → 指定图片 → 生成纯色封面）"""
        # 1. 先看缓存
        if THUMB_FILE.exists():
            mid = THUMB_FILE.read_text().strip()
            if mid:
                print(f"[封面] 使用缓存: {mid}")
                return mid

        # 2. 用户指定图片
        if image_path:
            return self.upload_thumb(image_path)

        # 3. 自动生成纯色封面
        return self._gen_and_upload_cover(color or (24, 119, 212))

    def upload_thumb(self, image_path):
        """上传封面缩略图（永久素材，type=thumb）"""
        token = self.get_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=thumb"
        with open(image_path, "rb") as f:
            resp = requests.post(url, files={"media": f}, timeout=30).json()
        if "media_id" not in resp:
            raise RuntimeError(f"封面上传失败: {resp}")
        self._cache_thumb(resp["media_id"])
        print(f"[封面] 上传成功: {resp['media_id']}")
        return resp["media_id"]

    def _gen_and_upload_cover(self, rgb):
        """生成纯色 PNG 封面并上传"""
        png = _make_png(900, 500, *rgb)
        cover_path = CACHE_DIR / "_auto_cover.png"
        cover_path.write_bytes(png)
        return self.upload_thumb(str(cover_path))

    def _cache_thumb(self, media_id):
        THUMB_FILE.write_text(media_id)

    # ═══════════════════════════════ 图片 ═══════════════════════════════

    def upload_image(self, image_path):
        """上传图文内图片，返回 url（直接嵌入 HTML 的 <img src>）"""
        token = self.get_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        with open(image_path, "rb") as f:
            resp = requests.post(url, files={"media": f}, timeout=30).json()
        if "url" not in resp:
            raise RuntimeError(f"图片上传失败: {resp}")
        print(f"[图片] 上传成功: {resp['url']}")
        return resp["url"]

    # ═══════════════════════════════ 草稿 ═══════════════════════════════

    def create_draft(self, title, content, *, author="老李读书笔记",
                     digest="", thumb_path=None, source_url="",
                     show_cover=1):
        """
        创建草稿 → 去公众号后台「草稿箱」手动发布
        返回 media_id
        """
        thumb_id = self.get_or_create_cover(image_path=thumb_path)
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": source_url,
            "thumb_media_id": thumb_id,
            "show_cover_pic": show_cover,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }
        token = self.get_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        payload = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
        resp = requests.post(url, data=payload,
                            headers={"Content-Type": "application/json; charset=utf-8"},
                            timeout=30).json()
        if "media_id" not in resp:
            raise RuntimeError(f"草稿创建失败: {resp}")
        media_id = resp["media_id"]
        print(f"[草稿] 创建成功! media_id: {media_id}")
        print(f"  → 去公众号后台「草稿箱」发布即可")
        return media_id

    def delete_draft(self, media_id):
        """删除草稿"""
        token = self.get_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"
        resp = requests.post(url, json={"media_id": media_id}, timeout=10).json()
        ok = resp.get("errcode") == 0
        print(f"[删除] {'成功' if ok else '失败'}: {resp}")
        return ok

    def list_drafts(self, offset=0, count=20):
        """列出草稿"""
        token = self.get_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
        resp = requests.post(url, json={"offset": offset, "count": count, "no_content": 1}, timeout=30).json()
        items = resp.get("item", [])
        for it in items:
            media_id = it.get("media_id", "?")
            title = it.get("content", {}).get("news_item", [{}])[0].get("title", "?")
            update = time.strftime("%m-%d %H:%M", time.localtime(it.get("update_time", 0)))
            print(f"  [{update}] {title}  ({media_id})")
        return items


# ═══════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════

def _make_png(width, height, r, g, b):
    """纯 Python 生成纯色 PNG（不依赖 Pillow）"""
    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    raw = b""
    for _ in range(height):
        raw += b"\x00"  # filter: none
        for _ in range(width):
            raw += struct.pack("BBB", r, g, b)
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    return header + ihdr + idat + iend


def html_wrap(body, title=""):
    """把 Markdown 风格的 body 包成微信兼容 HTML"""
    html = f"""<section style="padding:10px;max-width:100%%;box-sizing:border-box;">
{body}
</section>"""
    if title:
        html = f"<h1 style='text-align:center;font-size:22px;'>{title}</h1>\n{html}"
    return html


# ═══════════════════════════════════════════
# 命令行
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    APPID = "YOUR_APPID"
    APPSECRET = "ee3c8dde284af9fcaa7d2fc05ca1e163"
    wp = WeChatPublisher(APPID, APPSECRET)

    if len(sys.argv) < 2:
        print("用法:")
        print("  python wechat_publisher.py list         列出草稿")
        print("  python wechat_publisher.py del <id>     删除草稿")
        print("  python wechat_publisher.py test         创建测试草稿")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "list":
        wp.list_drafts()
    elif cmd == "del" and len(sys.argv) > 2:
        wp.delete_draft(sys.argv[2])
    elif cmd == "test":
        wp.create_draft(
            title="【测试】API 自动发布验证",
            content=html_wrap(
                "<h2>测试文章</h2>"
                "<p>来自阿文的半自动发布系统。</p>"
                "<hr><p><em>—— 老李读书笔记</em></p>"
            ),
            digest="API 自动推送草稿功能验证",
        )
    else:
        print(f"未知命令: {cmd}")
