#!/usr/bin/env python3
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import daily as dy  # noqa: E402
import watchlist as wl  # noqa: E402


class DailyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.db = root / "chat.sqlite"
        con = sqlite3.connect(self.db)
        con.execute(
            "CREATE TABLE contacts (username TEXT PRIMARY KEY, remark TEXT, nick_name TEXT, alias TEXT)"
        )
        con.execute(
            "CREATE TABLE messages (chat_username TEXT, chat_name TEXT, sender_username TEXT, "
            "sender_name TEXT, create_time INTEGER, local_type INTEGER, decoded_content TEXT, "
            "source_db TEXT, source_table TEXT, local_id INTEGER)"
        )
        # 2026-09-07 10:00 +08 = 1788746400? compute via datetime
        import datetime

        tz = datetime.timezone(datetime.timedelta(hours=8))
        base = int(datetime.datetime(2026, 9, 7, 10, 0, tzinfo=tz).timestamp())
        rows = [
            ("g1", "测试群", "u1", "Alice", base, 1, "提示词要和垫图一起用 https://example.com/a", "m", "t", 1),
            ("g1", "测试群", "u2", "Bob", base + 60, 1, "额度不够了，询价还没人回", "m", "t", 2),
            ("g1", "测试群", "u1", "Alice", base + 120, 1, "其实关键是先做一条 15 秒", "m", "t", 3),
            ("g1", "测试群", "u3", "wxid_abc", base + 180, 1, "我发现这个坑了", "m", "t", 4),
            ("g1", "测试群", "sys", "系统", base + 200, 10000, "加入群聊", "m", "t", 5),
            ("g1", "测试群", "u2", "Bob", base + 240, 3, "", "m", "t", 6),
        ]
        for i in range(8):
            rows.append(
                (
                    "g1",
                    "测试群",
                    "u1",
                    "Alice",
                    base + 300 + i * 30,
                    1,
                    f"继续讨论提示词第{i}轮，不要只复制文字",
                    "m",
                    "t",
                    10 + i,
                )
            )
        con.executemany("insert into messages values (?,?,?,?,?,?,?,?,?,?)", rows)
        con.execute("insert into contacts values (?,?,?,?)", ("u3", "陈备注", "陈昵称", ""))
        con.commit()
        con.close()
        self.watch = root / "watchlist.json"
        self.out = root / "out"
        self._old = {k: os.environ.get(k) for k in ("JOKER_WECHAT_DB", "JOKER_WECHAT_WATCHLIST", "JOKER_WECHAT_DAILY_DIR")}
        os.environ["JOKER_WECHAT_DB"] = str(self.db)
        os.environ["JOKER_WECHAT_WATCHLIST"] = str(self.watch)
        os.environ["JOKER_WECHAT_DAILY_DIR"] = str(self.out)
        self.watch.write_text(
            json.dumps(
                {
                    "version": 1,
                    "targets": [
                        {"chat_username": "g1", "label": "测试", "kind": "group", "enabled": True}
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        for key, value in self._old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def test_fixed_blocks_and_real_names(self):
        con = wl.connect(self.db)
        try:
            payload = dy.build_day(con, "g1", "测试", "测试群", date(2026, 9, 7))
        finally:
            con.close()
        xml = dy.render_xml(payload)
        for heading in dy.BLOCKS:
            self.assertIn(heading, xml)
        self.assertIn("Alice", xml)
        self.assertIn("陈备注", xml)
        self.assertNotIn("wxid_abc", xml)
        self.assertNotIn("成员01", xml)
        self.assertNotIn("来源：#", xml)
        self.assertTrue(payload["title"].startswith("2026-09-07-测试群-"))
        self.assertGreaterEqual(payload["count"], 13)
        self.assertEqual(payload["types"]["system"], 1)

    def test_cli_writes_xml(self):
        code = dy.main(
            ["build", "--id", "g1", "--date", "2026-09-07", "--out", str(self.out), "--json"]
        )
        self.assertEqual(code, 0)
        xml_files = list(self.out.glob("*.xml"))
        self.assertEqual(len(xml_files), 1)
        text = xml_files[0].read_text(encoding="utf-8")
        self.assertIn("<title>", text)
        self.assertIn("一句话总览", text)

    def test_empty_day_fails(self):
        con = wl.connect(self.db)
        try:
            with self.assertRaises(dy.DailyError):
                dy.build_day(con, "g1", "测试", "测试群", date(2026, 9, 8))
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
