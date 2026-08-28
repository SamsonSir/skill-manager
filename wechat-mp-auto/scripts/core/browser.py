"""
浏览器管理 — 连接已登录的 Chrome（CDP 模式）
优先复用用户日常 Chrome（port 9222），无需重新登录。
参考 xhs-auto-cy/scripts/core/browser_pool.py 的 CDP 连接模式。
"""
import subprocess
import time
import socket
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from . import config

# 默认 CDP 端口（用户 Chrome 开启了 --remote-debugging-port=9222）
DEFAULT_CDP_PORT = 9222

_browser: Browser | None = None
_context: BrowserContext | None = None
_playwright = None


def _is_port_listening(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except (ConnectionRefusedError, OSError):
        return False


def _auto_launch_chrome_cdp(port: int = DEFAULT_CDP_PORT, wait_seconds: int = 15) -> bool:
    """
    端口没监听时,自动起一个发文专用 Chrome Canary(独立 profile,永远开 CDP)。
    复用 ~/Applications/Chrome (CDP).app 背后的同一套参数:
      --user-data-dir=$HOME/ChromeMP --remote-debugging-port={port}

    用 Google Chrome Canary 而不是稳定版 Chrome —— 因为 Chrome.app 同一时间只能
    锁定一个 user-data-dir,如果发文用稳定版,会和用户日常 Chrome 抢进程,导致日常
    Chrome 的 Google 账号"消失"(其实是被锁在 ChromeMP profile 上)。Canary 是独立
    的 .app,进程完全隔离,可以和稳定版同时运行。

    成功 → 返回 True;wait_seconds 内端口仍不通 → 返回 False。
    """
    home = Path.home()
    user_data_dir = home / "ChromeMP"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    print(f"🚀 端口 {port} 未监听,自动启动 Chrome (CDP) Canary 独立 profile…")
    try:
        subprocess.Popen(
            [
                "open", "-na", "Google Chrome Canary", "--args",
                f"--user-data-dir={user_data_dir}",
                f"--remote-debugging-port={port}",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"⚠️  自动启动失败: {e}")
        return False

    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if _is_port_listening(port):
            print(f"✅ Chrome (CDP) 已就绪（端口 {port}）")
            return True
        time.sleep(0.5)
    print(f"⚠️  等待 {wait_seconds}s 后端口 {port} 仍未监听")
    return False


def get_chrome_ws_url(port: int = DEFAULT_CDP_PORT) -> str:
    """公开版本：解析 Chrome CDP 真实 WebSocket URL,供并行 worker 使用。"""
    return _get_chrome_ws_url(port)


def ensure_cdp_alive(port: int = DEFAULT_CDP_PORT) -> None:
    """确认 CDP 端口在监听。供并行 worker 启动前自检。"""
    if not _is_port_listening(port):
        if _auto_launch_chrome_cdp(port):
            return
        raise RuntimeError(
            f"Chrome 未在端口 {port} 开启远程调试，且自动拉起也失败。\n"
            "手动操作：点 Dock 上的 Chrome (CDP) 图标，或运行：\n"
            "  open -na 'Google Chrome Canary' --args --user-data-dir=$HOME/ChromeMP --remote-debugging-port=9222"
        )


def _get_chrome_ws_url(port: int = DEFAULT_CDP_PORT) -> str:
    """
    获取 Chrome CDP 的真实 WebSocket URL。

    优先走 HTTP /json/version —— 这是 Chrome 进程当前的权威 ws URL，
    不会被任何 stale 的 DevToolsActivePort 文件污染。
    只有 HTTP 不通时，才退回到磁盘文件查找（兼容老路径）。
    """
    # 主路径：HTTP /json/version（权威，永远反映当前进程）
    import urllib.request
    import json
    try:
        data = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2).read()
        ws_url = json.loads(data).get("webSocketDebuggerUrl", "")
        if ws_url:
            return ws_url
    except Exception:
        pass

    # 兜底：DevToolsActivePort 文件
    home = Path.home()
    candidates = [
        home / "ChromeMP/DevToolsActivePort",
        home / "Library/Application Support/Google/Chrome/DevToolsActivePort",
        home / "Library/Application Support/Google/Chrome Canary/DevToolsActivePort",
        home / "Library/Application Support/Chromium/DevToolsActivePort",
    ]
    for p in candidates:
        if p.exists():
            try:
                lines = p.read_text().strip().splitlines()
                file_port = int(lines[0])
                ws_path = lines[1].strip() if len(lines) > 1 else None
                if ws_path:
                    return f"ws://127.0.0.1:{file_port}{ws_path}"
                return f"http://127.0.0.1:{file_port}"
            except Exception:
                continue

    return f"http://127.0.0.1:{port}"


def get_page() -> Page:
    """获取一个新 Page，连接到用户已登录的 Chrome。"""
    global _browser, _context, _playwright

    cdp_port = config.get("cdp_port", DEFAULT_CDP_PORT)

    if not _is_port_listening(cdp_port):
        if not _auto_launch_chrome_cdp(cdp_port):
            raise RuntimeError(
                f"Chrome 未在端口 {cdp_port} 开启远程调试，且自动拉起也失败。\n"
                "手动操作：点 Dock 上的 Chrome (CDP) 图标，或运行：\n"
                "  open -na 'Google Chrome Canary' --args --user-data-dir=$HOME/ChromeMP --remote-debugging-port=9222"
            )

    if _playwright is None:
        _playwright = sync_playwright().start()

    if _browser is None or not _browser.is_connected():
        ws_url = _get_chrome_ws_url(cdp_port)
        _browser = _playwright.chromium.connect_over_cdp(ws_url)

    # 使用第一个 browser context（用户已登录的那个）
    contexts = _browser.contexts
    if contexts:
        _context = contexts[0]
    else:
        _context = _browser.new_context()

    page = _context.new_page()
    return page


def close_page(page: Page):
    """关闭 Page，保留 Chrome 进程和 session。"""
    try:
        page.close()
    except Exception:
        pass


def disconnect():
    """释放 Playwright 资源，不关闭用户 Chrome。"""
    global _browser, _context, _playwright
    try:
        if _browser:
            _browser.close()
    except Exception:
        pass
    try:
        if _playwright:
            _playwright.stop()
    except Exception:
        pass
    _browser = None
    _context = None
    _playwright = None
