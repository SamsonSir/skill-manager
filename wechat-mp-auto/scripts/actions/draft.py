"""
保存草稿 — 将文章（标题 + HTML 内容 + 封面图）保存到微信公众号草稿箱
参考 xhs-auto-cy/scripts/actions/publish_image.py 的发布流程。

微信公众号编辑器要点：
- 编辑器为自定义富文本，支持「源代码」模式粘贴 HTML
- 标题为普通 input
- 封面图通过上传对话框设置
- 「保存草稿」按钮 id = js_save_article_draft
"""
import time
import re
from pathlib import Path
from playwright.sync_api import Page

MP_HOME = "https://mp.weixin.qq.com"


def _wait(page: Page, ms: int = 1000):
    page.wait_for_timeout(ms)


def _get_token(page: Page) -> str:
    """从当前页面 URL 提取 token 参数。"""
    url = page.url
    m = re.search(r"token=(\d+)", url)
    return m.group(1) if m else ""


def save_draft(
    page: Page,
    title: str,
    html_content: str,
    cover_image_path: str | None = None,
    author: str = "",
    digest: str = "",
    preview: bool = False,
    screenshot_prefix: str = "",
) -> dict:
    """
    将文章保存为草稿。

    Args:
        page: Playwright Page（已连接到已登录的 Chrome）
        title: 文章标题
        html_content: 文章正文 HTML（wechat-typesetting 生成的 section 内容）
        cover_image_path: 封面图本地路径（可选）
        author: 作者名（可选）
        digest: 摘要（可选，最多120字）
        preview: True 时只截图预览，不实际保存
        screenshot_prefix: 截图文件名前缀（批量模式下用于区分多篇文章）

    Returns:
        {"status": "success"|"error", "message": str, "screenshot": str}
    """
    screenshots = []

    def _shot(tag: str) -> str:
        """生成截图路径，带可选前缀避免批量模式下互相覆盖。"""
        if screenshot_prefix:
            return f"/tmp/mp-{screenshot_prefix}-{tag}.png"
        return f"/tmp/mp-{tag}.png"

    # ── 1. 导航到新建图文页 ──────────────────────────────────────────────
    page.goto(MP_HOME, wait_until="domcontentloaded", timeout=15000)
    _wait(page, 1500)

    token = _get_token(page)
    if not token:
        # 尝试从 cookie 或其他方式获取
        pass

    # 点击「文章」按钮创建新图文（监听新 tab 打开）
    with page.context.expect_page() as new_page_info:
        page.click("text=文章")

    editor_page = new_page_info.value
    editor_page.wait_for_load_state("domcontentloaded")
    _wait(editor_page, 2000)

    if preview:
        shot = _shot("preview-editor")
        editor_page.screenshot(path=shot)
        screenshots.append(shot)
        print(f"[PREVIEW] 编辑器已打开，截图: {shot}")

    # ── 2. 填写标题 ─────────────────────────────────────────────────────
    title_selectors = [
        "#title",
        "input[placeholder*='标题']",
        ".title-input input",
        "[data-placeholder*='标题']",
    ]
    title_input = None
    for sel in title_selectors:
        try:
            title_input = editor_page.wait_for_selector(sel, timeout=3000)
            break
        except Exception:
            continue

    if title_input:
        title_input.click()
        title_input.fill("")
        title_input.type(title, delay=30)
        print(f"✅ 标题已填写: {title}")
    else:
        print("⚠️  未找到标题输入框，跳过")

    _wait(editor_page, 500)

    # ── 3. 向 ProseMirror 编辑器注入 HTML ──────────────────────────────
    # 微信 MP 编辑器使用 ProseMirror，通过模拟 ClipboardEvent paste
    # 传入 text/html 数据，ProseMirror 会正确解析并渲染 HTML 内容。
    inner_html = _extract_wechat_content(html_content)
    injected = _inject_html_to_prosemirror(editor_page, inner_html)
    if injected:
        print("✅ HTML 内容已注入编辑器")
    else:
        print("⚠️  ProseMirror 注入失败，尝试降级粘贴")
        _paste_to_editor(editor_page, inner_html)

    # ── 4. 封面图：从正文选择（等待编辑器处理图片）────────────────────────
    _wait(editor_page, 3000)  # 等待编辑器下载处理正文中的远程图片
    _try_select_first_image_as_cover(editor_page)

    # ── 5. 填写作者（可选）──────────────────────────────────────────────
    if author:
        author_selectors = [
            "#author",
            "input[placeholder*='作者']",
            ".author-input input",
        ]
        for sel in author_selectors:
            try:
                inp = editor_page.wait_for_selector(sel, timeout=2000)
                inp.fill(author)
                print(f"✅ 作者: {author}")
                break
            except Exception:
                continue

    # ── 6. 填写摘要（可选）──────────────────────────────────────────────
    if digest:
        digest_selectors = [
            "#digest",
            "textarea[placeholder*='摘要']",
            ".digest-input textarea",
        ]
        for sel in digest_selectors:
            try:
                inp = editor_page.wait_for_selector(sel, timeout=2000)
                inp.fill(digest[:120])
                print(f"✅ 摘要已填写")
                break
            except Exception:
                continue

    # ── 6.5 填写创作来源 ─────────────────────────────────────────────────
    _fill_creation_source(editor_page)

    # ── 7. 截图预览 ──────────────────────────────────────────────────────
    if preview:
        shot = _shot("preview-filled")
        editor_page.screenshot(path=shot, full_page=True)
        screenshots.append(shot)
        print(f"[PREVIEW] 已填充内容截图: {shot}")
        editor_page.close()
        return {"status": "preview", "message": "预览模式，未保存", "screenshots": screenshots}

    # ── 8. 保存草稿 ──────────────────────────────────────────────────────
    # 先滚动到底部让按钮可见，再用 JS 直接点击 #js_submit
    editor_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    _wait(editor_page, 800)

    saved = editor_page.evaluate("""
    () => {
        // 优先用 id 定位
        let btn = document.getElementById('js_submit');
        if (btn) { btn.scrollIntoView(); btn.click(); return 'js_submit'; }
        // 降级：文字匹配
        const all = Array.from(document.querySelectorAll('span,button,a'));
        btn = all.find(el => el.textContent.trim() === '保存为草稿' && el.offsetParent);
        if (btn) { btn.scrollIntoView(); btn.click(); return 'text-match'; }
        return null;
    }
    """)
    if saved:
        print(f"✅ 已点击「保存草稿」（via {saved}）")

    if not saved:
        shot = _shot("save-failed")
        editor_page.screenshot(path=shot, full_page=True)
        editor_page.close()
        return {
            "status": "error",
            "message": f"未找到「保存草稿」按钮，截图已保存到 {shot}",
            "screenshots": [shot],
        }

    _wait(editor_page, 2000)

    # 验证保存成功
    shot = _shot("draft-saved")
    editor_page.screenshot(path=shot)
    screenshots.append(shot)

    # 检测成功提示
    success = False
    success_signals = [
        "text=保存成功",
        "text=草稿已保存",
        ".success-toast",
    ]
    for sig in success_signals:
        try:
            editor_page.wait_for_selector(sig, timeout=3000)
            success = True
            break
        except Exception:
            continue

    editor_page.close()

    if success:
        print(f"✅ 草稿保存成功！截图: {shot}")
        return {"status": "success", "message": "草稿已保存到公众号草稿箱", "screenshots": screenshots}
    else:
        return {"status": "success", "message": "已点击保存草稿（请在公众号后台确认）", "screenshots": screenshots}


def _extract_wechat_content(html: str) -> str:
    """
    从 wechat-typesetting 生成的完整 HTML 中提取 section[data-role=outer] 内容。
    正确处理嵌套 section 标签（非贪婪 .*? 会在第一个 </section> 就停止，导致内容截断）。
    """
    import re
    # 找到 outer section 的起始位置
    outer_match = re.search(r'<section[^>]*data-role=["\']outer["\']', html, re.IGNORECASE)
    if outer_match:
        start = html.rfind('<section', 0, outer_match.end())
        # 通过计数嵌套深度找到匹配的 </section>
        depth = 0
        tag_re = re.compile(r'<(/?)section[\s>]', re.IGNORECASE)
        for m in tag_re.finditer(html[start:]):
            if m.group(1) == '':
                depth += 1
            else:
                depth -= 1
            if depth == 0:
                end_pos = start + m.start()
                close_end = html.find('>', end_pos) + 1
                return html[start:close_end]
    # 降级：提取 <body> 内容
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return html


def _inject_html_to_prosemirror(page: Page, html: str) -> bool:
    """
    向微信 ProseMirror 编辑器注入 HTML 内容。
    策略：先尝试 ClipboardEvent paste（ProseMirror 原生解析），
    若内容丢失严重则降级为 innerHTML 直注。
    """
    import json
    try:
        editor = page.wait_for_selector(".ProseMirror", timeout=5000)
        editor.click()
        page.wait_for_timeout(300)

        # 清空
        page.keyboard.press("Meta+a")
        page.wait_for_timeout(200)
        page.keyboard.press("Delete")
        page.wait_for_timeout(200)

        escaped = json.dumps(html)

        # 方案 1：ClipboardEvent paste
        result = page.evaluate(f"""
        (function() {{
            const editor = document.querySelector('.ProseMirror');
            if (!editor) return {{ok: false, reason: 'editor not found'}};
            editor.focus();
            const dt = new DataTransfer();
            dt.setData('text/html', {escaped});
            dt.setData('text/plain', '');
            const ev = new ClipboardEvent('paste', {{
                clipboardData: dt, bubbles: true, cancelable: true
            }});
            editor.dispatchEvent(ev);
            return {{ok: true, len: editor.innerHTML.length}};
        }})()
        """)

        paste_len = result.get("len", 0) if result else 0
        html_len = len(html)

        # 如果 paste 保留了足够内容（> 原始 HTML 的 30%），接受
        if paste_len > html_len * 0.3:
            print(f"   → ClipboardEvent 注入成功 ({paste_len} 字符)")
            return True

        print(f"   → ClipboardEvent 内容不全 ({paste_len}/{html_len})，降级 innerHTML 直注")

        # 方案 2：innerHTML 直注 + 触发 ProseMirror 同步
        result2 = page.evaluate(f"""
        (function() {{
            const editor = document.querySelector('.ProseMirror');
            if (!editor) return {{ok: false}};

            // 保存 ProseMirror 的 contenteditable 属性
            const wasEditable = editor.contentEditable;
            editor.contentEditable = 'true';

            // 直接写入 innerHTML
            editor.innerHTML = {escaped};

            // 触发 input 事件让 WeChat 编辑器感知变化
            editor.dispatchEvent(new Event('input', {{bubbles: true}}));
            editor.dispatchEvent(new Event('change', {{bubbles: true}}));

            // 模拟键盘事件让 ProseMirror 同步内部状态
            editor.dispatchEvent(new KeyboardEvent('keydown', {{key: 'End', bubbles: true}}));
            editor.dispatchEvent(new KeyboardEvent('keyup', {{key: 'End', bubbles: true}}));

            return {{ok: true, len: editor.innerHTML.length}};
        }})()
        """)

        if result2 and result2.get("ok"):
            length = result2.get("len", 0)
            print(f"   → innerHTML 直注成功 ({length} 字符)")
            return length > 100

        return False

    except Exception as e:
        print(f"   → ProseMirror 注入异常: {e}")
        return False


def _paste_to_editor(page: Page, html: str):
    """降级方案：直接操作编辑区 contenteditable，插入纯文本。"""
    editor_selectors = [
        ".edui-editor-body",
        "#ueditor_0",
        "[contenteditable='true']",
    ]
    for sel in editor_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=2000)
            el.click()
            page.keyboard.press("Control+a")
            page.keyboard.type(html[:500] + "...(内容已截断，请手动粘贴)")
            print("⚠️  已插入截断内容，建议手动粘贴完整 HTML")
            return
        except Exception:
            continue
    print("⚠️  未找到编辑区，跳过内容填充")


def _upload_cover(page: Page, image_path: str):
    """
    上传封面图。优先「从正文选择」（正文中已有 seedream 配图），
    降级为通过 file input 直接上传。
    """
    # 先尝试从正文选择（正文中通常已有配图）
    if _try_select_first_image_as_cover(page):
        return

    # 降级：通过隐藏的 file input 直接上传
    try:
        page.evaluate("document.getElementById('js_cover_area')?.scrollIntoView()")
        page.wait_for_timeout(500)

        # 找到页面中所有 file input，设置文件
        uploaded = page.evaluate("""
        () => {
            const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
            const imgInput = inputs.find(el => !el.accept || el.accept.includes('image'));
            if (imgInput) return { found: true, accept: imgInput.accept, id: imgInput.id };
            return { found: false };
        }
        """)

        if uploaded and uploaded.get("found"):
            with page.expect_file_chooser(timeout=5000) as fc_info:
                page.evaluate("""
                () => {
                    const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                    const imgInput = inputs.find(el => !el.accept || el.accept.includes('image'));
                    if (imgInput) imgInput.click();
                }
                """)
            file_chooser = fc_info.value
            file_chooser.set_files(image_path)
            page.wait_for_timeout(3000)
            print(f"✅ 封面图已通过 file input 上传: {Path(image_path).name}")
        else:
            print("⚠️  未找到 file input，请手动设置封面图")

    except Exception as e:
        print(f"⚠️  封面图上传失败: {e}")


def _try_select_first_image_as_cover(page: Page) -> bool:
    """
    尝试从正文中选第一张图作为封面。
    返回 True 表示成功选择了封面。
    """
    try:
        # 先关闭任何已打开的弹窗
        page.evaluate("""
        () => {
            const close = document.querySelector('.weui-desktop-dialog .weui-desktop-icon-close');
            if (close) close.click();
            // 也尝试 Escape 关闭
        }
        """)
        page.wait_for_timeout(500)

        page.evaluate("document.getElementById('js_cover_area')?.scrollIntoView()")
        page.wait_for_timeout(500)

        # 直接用 JS 点击「从正文选择」按钮（在 hover 菜单中，class=js_selectCoverFromContent）
        clicked = page.evaluate("""
        () => {
            const btn = document.querySelector('.js_selectCoverFromContent');
            if (btn) { btn.click(); return true; }
            return false;
        }
        """)

        if not clicked:
            print("⚠️  未找到「从正文选择」菜单项")
            return False

        page.wait_for_timeout(2000)

        # 在弹出的图片列表中选择第一张
        # 注意：图片是 span.appmsg_content_img 用 background-image 显示的，不是 <img> 标签
        selected = page.evaluate("""
        () => {
            // 方式1：点击正文图片项（li.appmsg_content_img_item）
            const items = Array.from(document.querySelectorAll('.appmsg_content_img_item'));
            if (items.length > 0) { items[0].click(); return 'clicked-item'; }
            // 方式2：点击 span.appmsg_content_img
            const spans = Array.from(document.querySelectorAll('.appmsg_content_img'));
            if (spans.length > 0) { spans[0].click(); return 'clicked-span'; }
            // 方式3：找弹窗中有 background-image 的元素
            const dialog = Array.from(document.querySelectorAll('.weui-desktop-dialog')).filter(d => d.offsetParent !== null).pop();
            if (dialog) {
                const bgEls = Array.from(dialog.querySelectorAll('*')).filter(el => {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    return bg && bg !== 'none' && bg.includes('mmbiz');
                });
                if (bgEls.length > 0) { bgEls[0].click(); return 'clicked-bg'; }
            }
            return null;
        }
        """)

        if not selected:
            # 调试：输出弹窗内容
            debug = page.evaluate("""
            () => {
                const dialogs = Array.from(document.querySelectorAll('.weui-desktop-dialog')).filter(d => d.offsetParent !== null);
                if (!dialogs.length) return 'no dialog';
                const d = dialogs[dialogs.length - 1];
                const imgs = d.querySelectorAll('img');
                const texts = Array.from(d.querySelectorAll('*')).filter(el => el.children.length === 0 && el.textContent.trim()).map(el => el.textContent.trim()).slice(0, 10);
                return { imgCount: imgs.length, texts };
            }
            """)
            print(f"⚠️  从正文选择弹窗中未找到图片 (debug: {debug})")
            # 关闭弹窗
            page.evaluate("""
            () => {
                const close = document.querySelector('.weui-desktop-dialog .weui-desktop-icon-close');
                if (close) close.click();
                const cancel = Array.from(document.querySelectorAll('button, a')).find(
                    el => el.textContent.trim() === '取消'
                );
                if (cancel) cancel.click();
            }
            """)
            page.wait_for_timeout(500)
            return False

        page.wait_for_timeout(1000)

        # 点「下一步」按钮（选中图片后变为可点击）
        page.evaluate("""
        () => {
            const btns = Array.from(document.querySelectorAll('button'));
            const next = btns.find(el => el.textContent.trim() === '下一步' && el.offsetParent !== null);
            if (next) next.click();
        }
        """)
        page.wait_for_timeout(2000)

        # 进入裁剪/编辑封面页面，点击「完成」按钮
        # 弹窗标题可能是「编辑封面」，按钮在弹窗底部
        for attempt in range(3):
            done_clicked = page.evaluate("""
            () => {
                const dialogs = Array.from(document.querySelectorAll('.weui-desktop-dialog')).filter(d => d.offsetParent !== null);
                for (const d of dialogs) {
                    const btn = d.querySelector('.weui-desktop-btn_primary');
                    if (btn && btn.offsetParent !== null) {
                        btn.scrollIntoView();
                        btn.click();
                        return btn.textContent.trim();
                    }
                }
                return null;
            }
            """)
            if done_clicked:
                print(f"   → 封面弹窗点击: {done_clicked}")
            page.wait_for_timeout(2000)

            # 检查弹窗是否关闭
            still_open = page.evaluate("""
            () => {
                const dialogs = Array.from(document.querySelectorAll('.weui-desktop-dialog')).filter(d => d.offsetParent !== null);
                return dialogs.some(d => {
                    const t = d.textContent;
                    return t.includes('选择图片') || t.includes('编辑封面') || t.includes('裁剪');
                });
            }
            """)
            if not still_open:
                break
            page.wait_for_timeout(1000)

        print(f"✅ 封面图已从正文选择（{selected}）")
        return True

    except Exception as e:
        print(f"⚠️  自动选择封面图失败: {e}")
        return False


def _fill_creation_source(page: Page):
    """填写创作来源为「个人观点，仅供参考」。"""
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)

        # 点击「创作来源」行的「未添加 >」区域打开弹窗
        page.evaluate("""
        () => {
            const desc = document.querySelector('.js_claim_source_desc');
            if (desc) desc.click();
        }
        """)
        page.wait_for_timeout(2000)

        # 在弹窗中用 Playwright 原生点击选择「个人观点，仅供参考」
        try:
            page.click("text=个人观点，仅供参考", timeout=3000)
        except Exception:
            page.evaluate("""
            () => {
                const options = Array.from(document.querySelectorAll('.weui-desktop-form__check-content'));
                const target = options.find(el => el.textContent.trim() === '个人观点，仅供参考');
                if (target) {
                    const label = target.closest('label') || target.parentElement;
                    if (label) label.click();
                    else target.click();
                }
            }
            """)
        page.wait_for_timeout(1000)

        # 精确点击创作来源弹窗内的「确认」按钮
        page.evaluate("""
        () => {
            // 找到创作来源弹窗
            const dialogs = Array.from(document.querySelectorAll('.weui-desktop-dialog')).filter(d => d.offsetParent !== null);
            const srcDialog = dialogs.find(d => {
                const title = d.querySelector('h3, .weui-desktop-dialog__title');
                return title && title.textContent.includes('创作来源');
            });
            if (srcDialog) {
                const btn = srcDialog.querySelector('.weui-desktop-btn_primary');
                if (btn) {
                    btn.scrollIntoView();
                    btn.click();
                }
            }
        }
        """)

        # 等待弹窗关闭
        page.wait_for_timeout(2000)
        for _ in range(5):
            still_open = page.evaluate("""
            () => {
                const dialogs = Array.from(document.querySelectorAll('.weui-desktop-dialog')).filter(d => d.offsetParent !== null);
                return dialogs.some(d => d.textContent.includes('创作来源'));
            }
            """)
            if not still_open:
                break
            page.wait_for_timeout(1000)

        print("✅ 创作来源: 个人观点，仅供参考")

    except Exception as e:
        print(f"⚠️  填写创作来源失败: {e}")
