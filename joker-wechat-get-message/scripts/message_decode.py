"""Decode WeChat message_content / compress_content the same way as WeChatDataAnalysis 2.3.0.

Vendored subset of wechat_decrypt_tool.chat_helpers._decode_message_content.
Do not import wechat_decrypt_tool (that package also contains key-capture code).
"""
from __future__ import annotations

import base64
import html
import re
from typing import Any, Optional

try:
    import zstandard as zstd  # type: ignore
except Exception:
    zstd = None


def _decode_sqlite_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    if isinstance(value, memoryview):
        try:
            return bytes(value).decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return str(value)


def _is_mostly_printable_text(s: str) -> bool:
    if not s:
        return False
    sample = s[:600]
    printable = sum(1 for ch in sample if ch.isprintable() or ch in {"\n", "\r", "\t"})
    return (printable / len(sample)) >= 0.85


def _looks_like_xml(s: str) -> bool:
    if not s:
        return False
    t = s.lstrip()
    if t.startswith('"') and t.endswith('"'):
        t = t.strip('"').lstrip()
    return t.startswith("<")


def decode_message_content(compress_value: Any, message_value: Any) -> str:
    def try_decode_text_blob(text: str) -> Optional[str]:
        t = (text or "").strip()
        if not t:
            return None

        zstd_magic = b"\x28\xb5\x2f\xfd"

        if len(t) >= 16 and len(t) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", t):
            try:
                raw = bytes.fromhex(t)
                if zstd is not None and raw.startswith(zstd_magic):
                    try:
                        out = zstd.decompress(raw)
                        s2 = html.unescape(out.decode("utf-8", errors="ignore").strip())
                        if _looks_like_xml(s2) or _is_mostly_printable_text(s2):
                            return s2
                    except Exception:
                        pass
                s2 = html.unescape(raw.decode("utf-8", errors="ignore").strip())
                s2_lower = s2.lower()
                if (
                    _looks_like_xml(s2)
                    or ("<msg" in s2_lower and "</msg>" in s2_lower)
                    or "<appmsg" in s2_lower
                ):
                    return s2
            except Exception:
                return None

        if len(t) >= 24 and len(t) % 4 == 0 and re.fullmatch(r"[A-Za-z0-9+/=]+", t):
            try:
                raw = base64.b64decode(t)
                if zstd is not None and raw.startswith(zstd_magic):
                    try:
                        out = zstd.decompress(raw)
                        s2 = html.unescape(out.decode("utf-8", errors="ignore").strip())
                        if _looks_like_xml(s2) or _is_mostly_printable_text(s2):
                            return s2
                    except Exception:
                        pass
                s2 = html.unescape(raw.decode("utf-8", errors="ignore").strip())
                s2_lower = s2.lower()
                if (
                    _looks_like_xml(s2)
                    or ("<msg" in s2_lower and "</msg>" in s2_lower)
                    or "<appmsg" in s2_lower
                ):
                    return s2
            except Exception:
                return None

        return None

    msg_text = _decode_sqlite_text(message_value)

    s = html.unescape(msg_text.strip())
    s2 = try_decode_text_blob(s)
    if s2:
        msg_text = s2

    if isinstance(message_value, (bytes, bytearray, memoryview)):
        raw = bytes(message_value) if isinstance(message_value, memoryview) else message_value
        if raw.startswith(b"\x28\xb5\x2f\xfd") and zstd is not None:
            try:
                out = zstd.decompress(raw)
                s = html.unescape(out.decode("utf-8", errors="ignore").strip())
                if _looks_like_xml(s) or _is_mostly_printable_text(s):
                    msg_text = s
            except Exception:
                pass

    if compress_value is None:
        return msg_text

    if isinstance(compress_value, str):
        s = html.unescape(compress_value.strip())
        s2 = try_decode_text_blob(s)
        if s2:
            return s2
        if _looks_like_xml(s) or _is_mostly_printable_text(s):
            return s
        return msg_text

    data: Optional[bytes] = None
    if isinstance(compress_value, memoryview):
        data = bytes(compress_value)
    elif isinstance(compress_value, (bytes, bytearray)):
        data = bytes(compress_value)

    if not data:
        return msg_text

    if zstd is not None:
        try:
            out = zstd.decompress(data)
            s = html.unescape(out.decode("utf-8", errors="ignore").strip())
            if _looks_like_xml(s) or _is_mostly_printable_text(s):
                return s
        except Exception:
            pass

    try:
        s = html.unescape(data.decode("utf-8", errors="ignore").strip())
        s2 = try_decode_text_blob(s)
        if s2:
            return s2
        if _looks_like_xml(s) or _is_mostly_printable_text(s):
            return s
    except Exception:
        pass

    return msg_text
