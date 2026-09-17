#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import reader  # noqa: E402


class ReaderTests(unittest.TestCase):
    def test_md_marks_takeaway(self):
        html = reader.md_to_html("### 1. 豆包\n\n**发生了什么：** 跑出 30 秒。\n\n**群友可参考：** 先用 15 秒试效果。\n")
        self.assertIn("field takeaway", html)
        self.assertIn("先用 15 秒试效果", html)
        self.assertIn('class="topic"', html)
        self.assertNotIn("以上是该时段可读文字摘录", html)

    def test_daily_notes_do_not_fill_the_viewport(self):
        html = reader.md_to_html(
            "> 📌 **每日交流群日报**\n"
            "> 群：测试群\n"
            "> 日期：2026-09-08\n"
            "> 内容：一句话总览、发言与热议排行\n"
            "\n"
            "## 🧭 一句话总览\n"
            "\n"
            "先做一条 15 秒。\n"
        )
        self.assertIn("先做一条 15 秒", html)
        self.assertNotIn("每日交流群日报", html)
        self.assertNotIn("<aside class=\"note\"", html)
        self.assertNotIn("height:100vh", html.split(".note")[1][:200] if ".note" in html else "")

    def test_short_daily_label(self):
        label = reader.short_title(
            "2026-09-08-多多的AI视频交流群-三十秒电影感视频提示词实战",
            "daily",
        )
        self.assertTrue(label.startswith("09-08"))
        self.assertIn("三十秒", label)
        self.assertNotIn("多多的AI视频交流群", label)

    def test_reader_is_app_not_article_dump(self):
        tmp = tempfile.TemporaryDirectory()
        out = Path(tmp.name) / "wiki.html"
        path = reader.render_reader(
            title="多多的AI视频交流群",
            wiki_url="https://my.feishu.cn/wiki/demo",
            pages=[
                {"title": "多多的AI视频交流群", "home": True, "_anchor": "home", "_md": "# 首页\n\n先做一条。", "node_token": "a"},
                {"title": "01 先跑通小片", "_anchor": "s01", "_md": "# 01\n\n**群友可参考：** 先做 15 秒。", "node_token": "b"},
                {"title": "2026-09-08-多多的AI视频交流群-三十秒电影感视频提示词实战", "_anchor": "d08", "_md": "# 日报\n\n**群友可参考：** 先锁定两张参考图。", "node_token": "c"},
            ],
            stations=[],
            map_rel="学习地图.png",
            out_path=out,
        )
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn('id="nav"', text)
        self.assertIn('class="rail"', text)
        self.assertIn("application/json", text)
        self.assertIn("先锁定两张参考图", text)
        self.assertIn('data-filter="daily"', text)
        self.assertIn("09-08", text)
        self.assertIn("replaceState", text)
        self.assertNotIn("LEARNING JOURNAL", text)
        self.assertNotIn("baoyu-markdown-to-html", text)
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
