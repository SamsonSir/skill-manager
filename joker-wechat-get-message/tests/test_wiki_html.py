#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import wiki_html as wh  # noqa: E402


class WikiHtmlTests(unittest.TestCase):
    def test_xml_to_md_keeps_structure(self):
        xml = (
            "<title>01 先跑通小片</title>"
            "<p>先做一条 <b>10-15 秒</b> 的短片。</p>"
            "<callout emoji='📌'><p>附件未展开。</p></callout>"
            "<ul><li>想法</li><li>画面</li></ul>"
            '<p>相关：<cite doc-id="ABC" title="资源 · 提示词" type="doc"></cite></p>'
        )
        md = wh.xml_to_md(xml)
        self.assertIn("# 01 先跑通小片", md)
        self.assertIn("**10-15 秒**", md)
        self.assertIn("> [!NOTE]", md)
        self.assertIn("- 想法", md)
        self.assertIn("[资源 · 提示词](https://my.feishu.cn/docx/ABC)", md)
        self.assertNotIn("成员01", md)
        self.assertNotIn("来源：#", md)

    def test_station_summary(self):
        md = "# 01 先跑通小片\n\n先做一条短片树立信心。目标是 15 秒。不要先上复杂工作流。\n"
        bullets = wh.station_summary(md)
        self.assertTrue(bullets)
        self.assertTrue(any("短片" in item for item in bullets))


if __name__ == "__main__":
    unittest.main()
