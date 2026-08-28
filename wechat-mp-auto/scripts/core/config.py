"""配置存储 — 保存 CDP 端口、session 等跨调用状态"""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".wechat-mp-auto"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load() -> dict:
    CONFIG_DIR.mkdir(exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}

def save(data: dict):
    CONFIG_DIR.mkdir(exist_ok=True)
    current = load()
    current.update(data)
    CONFIG_FILE.write_text(json.dumps(current, indent=2, ensure_ascii=False))

def get(key: str, default=None):
    return load().get(key, default)
