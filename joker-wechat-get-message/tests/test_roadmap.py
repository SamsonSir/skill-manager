#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import roadmap  # noqa: E402


class RoadmapTests(unittest.TestCase):
    def test_html_uses_wiki_stations(self):
        stations = [
            {"index": "01", "title": "01 先跑通小片", "bullets": ["先做 15 秒。"]},
            {"index": "02", "title": "02 参考图分工", "bullets": ["主体图和场景图分开。"]},
        ]
        html = roadmap.render_html(
            title="AI视频学习地图",
            subtitle="从复刻，到可控出片",
            group="多多的AI视频交流群",
            source="Wiki 01–07",
            slogan="先做出一条，再把它稳定复现。",
            stations=stations,
            closing="真正值得积累的是：创意、观察、可复现的流程。",
        )
        self.assertIn("01 先跑通小片", html)
        self.assertIn("02 参考图分工", html)
        self.assertIn("先做 15 秒。", html)
        self.assertIn("1080px", html)
        self.assertNotIn("成员01", html)


if __name__ == "__main__":
    unittest.main()
