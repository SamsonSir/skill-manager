#!/usr/bin/env python3
"""
微信公众号自动化 CLI
用法:
  python mp.py save-draft --title "标题" --html-file draft.html [--cover cover.jpg] [--preview]
  python mp.py batch-save-draft --manifest manifest.json [--delay 4] [--results results.json]
  python mp.py check-login
"""
import argparse
import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# 确保 scripts 目录在 path 里
sys.path.insert(0, str(Path(__file__).parent))

from core import browser, config as cfg
from actions import auth, draft


def cmd_check_login(args):
    print("正在检查登录状态...")
    page = browser.get_page()
    try:
        logged_in = auth.check_login(page)
        if logged_in:
            print("✅ 已登录微信公众号后台")
        else:
            print("❌ 未登录，请在 Chrome 中打开 https://mp.weixin.qq.com 并完成登录")
    finally:
        browser.close_page(page)
        browser.disconnect()


def cmd_save_draft(args):
    # 读取 HTML 文件
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"❌ HTML 文件不存在: {args.html_file}")
        sys.exit(1)
    html_content = html_path.read_text(encoding="utf-8")

    print(f"📄 文章标题: {args.title}")
    print(f"📂 HTML 文件: {args.html_file} ({len(html_content)} 字节)")
    if args.cover:
        print(f"🖼️  封面图: {args.cover}")
    if args.preview:
        print("👁️  预览模式（不实际保存）")

    page = browser.get_page()
    try:
        # 检查登录
        auth.ensure_logged_in(page)

        # 保存草稿
        result = draft.save_draft(
            page=page,
            title=args.title,
            html_content=html_content,
            cover_image_path=args.cover,
            author=args.author or "",
            digest=args.digest or "",
            preview=args.preview,
        )

        print(f"\n{'='*50}")
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        if result.get('screenshots'):
            for s in result['screenshots']:
                print(f"截图: {s}")

        if result['status'] == 'error':
            sys.exit(1)

    finally:
        browser.close_page(page)
        browser.disconnect()


def _process_one_item(page, idx, total, item):
    """单篇处理逻辑（page 已就绪）。返回 entry dict。"""
    item_id = f"{idx:02d}"
    title = item.get("title", "")
    html_file = item.get("html_file", "")

    print(f"\n{'='*50}")
    print(f"[{idx}/{total}] 📄 {title}")
    print(f"{'='*50}")

    entry = {
        "index": idx,
        "title": title,
        "html_file": html_file,
        "status": "pending",
        "message": "",
        "screenshots": [],
    }

    try:
        html_path = Path(html_file)
        if not html_path.exists():
            raise FileNotFoundError(f"HTML 文件不存在: {html_file}")
        html_content = html_path.read_text(encoding="utf-8")

        result = draft.save_draft(
            page=page,
            title=title,
            html_content=html_content,
            cover_image_path=item.get("cover"),
            author=item.get("author", ""),
            digest=item.get("digest", ""),
            preview=False,
            screenshot_prefix=item_id,
        )
        entry["status"] = result["status"]
        entry["message"] = result["message"]
        entry["screenshots"] = result.get("screenshots", [])

        if result["status"] == "success":
            print(f"✅ [{idx}/{total}] 成功")
        else:
            print(f"❌ [{idx}/{total}] 失败: {result['message']}")
    except Exception as e:
        entry["status"] = "error"
        entry["message"] = f"{type(e).__name__}: {e}"
        print(f"❌ [{idx}/{total}] 异常: {entry['message']}")
        traceback.print_exc()

    return entry


def _worker_save_draft(ws_url, idx, total, item, stagger):
    """并行 worker：每个线程独立 sync_playwright + connect_over_cdp + new_page。

    sync Playwright 不允许跨线程共享 dispatcher，故每个 worker 都要自启自停。
    通过 stagger 错开启动时间，避免 Chrome 在同一瞬间被多个 connect 打爆。
    """
    if stagger > 0:
        time.sleep(stagger)
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    page = None
    try:
        b = pw.chromium.connect_over_cdp(ws_url)
        ctx = b.contexts[0] if b.contexts else b.new_context()
        page = ctx.new_page()
        auth.ensure_logged_in(page)
        return _process_one_item(page, idx, total, item)
    except Exception as e:
        traceback.print_exc()
        return {
            "index": idx,
            "title": item.get("title", ""),
            "html_file": item.get("html_file", ""),
            "status": "error",
            "message": f"worker_setup_error: {type(e).__name__}: {e}",
            "screenshots": [],
        }
    finally:
        try:
            if page is not None:
                page.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_batch_save_draft(args):
    """批量保存草稿：读取 manifest，复用同一浏览器 session 循环处理。

    Manifest 格式 (JSON):
      [
        {
          "title": "文章标题",
          "html_file": "/path/to/article.html",
          "cover": "/path/to/cover.jpg",    // 可选
          "author": "作者",                  // 可选
          "digest": "摘要"                   // 可选
        },
        ...
      ]
    """
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"❌ manifest 文件不存在: {args.manifest}")
        sys.exit(1)

    try:
        items = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ manifest 解析失败: {e}")
        sys.exit(1)

    if not isinstance(items, list) or not items:
        print("❌ manifest 必须是非空列表")
        sys.exit(1)

    parallel = max(1, int(args.parallel))
    total = len(items)
    print(f"📦 批量模式：共 {total} 篇文章")
    print(f"🧵 并发: {parallel}")
    if parallel == 1:
        print(f"⏱️  篇间延迟: {args.delay} 秒")
    else:
        print(f"⏱️  worker 启动错峰: 每个 {args.stagger} 秒")
    print(f"{'='*50}")

    results = []

    if parallel == 1:
        # 顺序模式：复用单 page
        page = browser.get_page()
        try:
            auth.ensure_logged_in(page)
            for idx, item in enumerate(items, 1):
                entry = _process_one_item(page, idx, total, item)
                results.append(entry)
                if idx < total:
                    print(f"⏳ 等待 {args.delay} 秒后继续...")
                    time.sleep(args.delay)
        finally:
            browser.close_page(page)
            browser.disconnect()
    else:
        # 并行模式：每个 worker 独立 playwright + page
        browser.ensure_cdp_alive()
        ws_url = browser.get_chrome_ws_url()
        print(f"🔗 CDP WebSocket: {ws_url}")
        with ThreadPoolExecutor(max_workers=parallel) as ex:
            futures = {
                ex.submit(
                    _worker_save_draft,
                    ws_url,
                    idx,
                    total,
                    item,
                    (idx - 1) * args.stagger if (idx - 1) < parallel else 0,
                ): idx
                for idx, item in enumerate(items, 1)
            }
            for fut in as_completed(futures):
                results.append(fut.result())
        results.sort(key=lambda e: e["index"])

    success_count = sum(1 for e in results if e["status"] == "success")
    fail_count = total - success_count

    # 写入 results.json
    results_path = Path(args.results)
    summary = {
        "total": len(items),
        "success": success_count,
        "failed": fail_count,
        "items": results,
    }
    results_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n{'='*50}")
    print(f"📊 批量处理完成: 成功 {success_count} / 失败 {fail_count} / 共 {len(items)}")
    print(f"📄 结果已写入: {results_path}")
    print(f"{'='*50}")

    if fail_count > 0 and success_count == 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="微信公众号自动化工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check-login
    subparsers.add_parser("check-login", help="检查登录状态")

    # save-draft
    draft_parser = subparsers.add_parser("save-draft", help="保存文章到草稿箱")
    draft_parser.add_argument("--title", required=True, help="文章标题")
    draft_parser.add_argument("--html-file", required=True, help="HTML 文件路径（wechat-typesetting 输出）")
    draft_parser.add_argument("--cover", help="封面图本地路径（可选）")
    draft_parser.add_argument("--author", help="作者名（可选）")
    draft_parser.add_argument("--digest", help="摘要，最多120字（可选）")
    draft_parser.add_argument("--preview", action="store_true", help="预览模式，只截图不保存")

    # batch-save-draft
    batch_parser = subparsers.add_parser(
        "batch-save-draft",
        help="批量保存文章到草稿箱（复用同一浏览器 session）",
    )
    batch_parser.add_argument(
        "--manifest",
        required=True,
        help="JSON 文件，数组元素 {title, html_file, cover?, author?, digest?}",
    )
    batch_parser.add_argument(
        "--delay",
        type=float,
        default=4.0,
        help="每篇之间的延时秒数（默认 4 秒）",
    )
    batch_parser.add_argument(
        "--results",
        default="/tmp/mp-batch-results.json",
        help="批量处理结果输出路径（默认 /tmp/mp-batch-results.json）",
    )
    batch_parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="并行 worker 数量（默认 1=顺序）。每个 worker 开独立标签页同时跑。建议 ≤5",
    )
    batch_parser.add_argument(
        "--stagger",
        type=float,
        default=2.0,
        help="并行模式下 worker 启动错峰秒数（避免同时 connect_over_cdp）",
    )

    args = parser.parse_args()

    if args.command == "check-login":
        cmd_check_login(args)
    elif args.command == "save-draft":
        cmd_save_draft(args)
    elif args.command == "batch-save-draft":
        cmd_batch_save_draft(args)


if __name__ == "__main__":
    main()
