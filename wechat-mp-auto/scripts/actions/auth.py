"""
登录状态检测 — 检查微信公众号后台是否已登录
参考 xhs-auto-cy/scripts/actions/auth.py 的分层检测策略。
"""
import time
from playwright.sync_api import Page

MP_HOME = "https://mp.weixin.qq.com"
LOGIN_URL_KEYWORDS = ["passport", "login", "loginpage"]


def check_login(page: Page) -> bool:
    """
    检测公众号后台登录状态。
    策略：导航到后台首页，判断是否被重定向到登录页。
    """
    page.goto(MP_HOME, wait_until="domcontentloaded", timeout=15000)
    time.sleep(2)

    current_url = page.url
    # 如果 URL 包含登录关键词，说明未登录
    if any(kw in current_url.lower() for kw in LOGIN_URL_KEYWORDS):
        return False

    # 检测后台页面特征元素
    try:
        page.wait_for_selector(".weui-desktop-account__nickname, #js_username_display", timeout=3000)
        return True
    except Exception:
        pass

    # 降级：检查 URL 是否还在 mp.weixin.qq.com
    return "mp.weixin.qq.com" in current_url and "login" not in current_url


def ensure_logged_in(page: Page):
    """确保已登录，否则提示用户扫码。"""
    if check_login(page):
        return

    print("⚠️  微信公众号未登录。")
    print("请在 Chrome 中打开 https://mp.weixin.qq.com 并完成登录，然后重新运行。")
    raise RuntimeError("未登录微信公众号后台")
