#!/usr/bin/env python3
"""lark-cli JSON helpers. Do not print tokens or chat bodies."""
from __future__ import annotations

import json
import subprocess
import time
from typing import Any

RETRY_MARKS = ("EOF", "rate_limit", "transport", "temporarily unavailable", "TIMEOUT")


class LarkError(Exception):
    pass


def lark_json(args: list[str], *, cwd: str | None = None, retries: int = 4) -> dict[str, Any]:
    last = ""
    for attempt in range(retries):
        proc = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
        text = (proc.stdout or "").strip()
        err = (proc.stderr or proc.stdout or "").strip()
        if proc.returncode == 0:
            if not text:
                return {}
            payload = json.loads(text)
            inner = payload.get("data") if isinstance(payload, dict) else None
            if isinstance(inner, dict):
                return inner
            return payload if isinstance(payload, dict) else {}
        last = err
        if attempt + 1 < retries and any(mark in err for mark in RETRY_MARKS):
            time.sleep(1.2 * (attempt + 1))
            continue
        raise LarkError(f"lark-cli 失败：{err[:500]}")
    raise LarkError(f"lark-cli 失败：{last[:500]}")


def nodes_from(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("data", payload) if isinstance(payload, dict) else payload
    if isinstance(items, dict):
        items = items.get("items") or items.get("nodes") or items.get("children") or []
    return list(items or [])
