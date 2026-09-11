#!/usr/bin/env python3
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import watchlist as wl  # noqa: E402


class WatchlistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.db = root / "chat.sqlite"
        self.list_path = root / "watchlist.json"
        con = sqlite3.connect(self.db)
        con.execute(
            "CREATE TABLE messages (chat_username TEXT, chat_name TEXT, create_time INTEGER, decoded_content TEXT)"
        )
        con.executemany(
            "INSERT INTO messages VALUES (?,?,?,?)",
            [
                ("57947720564@chatroom", "多多AI视频交流群", 100, "secret-a"),
                ("50351187410@chatroom", "夙愿的AI实验室2026", 200, "secret-b"),
                ("wxid_one", "测试联系人", 150, "secret-c"),
                ("111@chatroom", "同名群", 10, "x"),
                ("222@chatroom", "同名群", 20, "y"),
            ],
        )
        con.commit()
        con.close()
        self._old = (
            wl.os.environ.get("JOKER_WECHAT_DB"),
            wl.os.environ.get("JOKER_WECHAT_WATCHLIST"),
            wl.os.environ.get("JOKER_WECHAT_LIVE_DB"),
            wl.os.environ.get("JOKER_WECHAT_CLONE_DB"),
        )
        wl.os.environ["JOKER_WECHAT_DB"] = str(self.db)
        wl.os.environ["JOKER_WECHAT_WATCHLIST"] = str(self.list_path)
        wl.os.environ["JOKER_WECHAT_LIVE_DB"] = str(root / "missing-live.db")
        wl.os.environ["JOKER_WECHAT_CLONE_DB"] = str(root / "missing-clone.db")

    def tearDown(self):
        db, path, live, clone = self._old
        mapping = {
            "JOKER_WECHAT_DB": db,
            "JOKER_WECHAT_WATCHLIST": path,
            "JOKER_WECHAT_LIVE_DB": live,
            "JOKER_WECHAT_CLONE_DB": clone,
        }
        for key, value in mapping.items():
            if value is None:
                wl.os.environ.pop(key, None)
            else:
                wl.os.environ[key] = value
        self.tmp.cleanup()

    def _json(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = wl.main(argv)
        return code, json.loads(buf.getvalue())

    def test_status_defaults_and_hides_bodies(self):
        code, payload = self._json(["--json", "status"])
        self.assertEqual(code, 0)
        self.assertFalse(payload["live_wechat"])
        self.assertFalse(payload["refresh_needed"])
        self.assertFalse(payload["live_encrypted"]["exists"])
        ids = [t["chat_username"] for t in payload["targets"]]
        self.assertEqual(ids, ["57947720564@chatroom", "50351187410@chatroom"])
        self.assertTrue(self.list_path.is_file())
        dumped = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("secret-a", dumped)
        self.assertNotIn("secret-b", dumped)
        self.assertEqual(self.list_path.stat().st_mode & 0o777, 0o600)

    def test_add_contact_exact_id(self):
        wl.main(["init"])
        code = wl.main(["add", "--id", "wxid_one", "--label", "测试联系人"])
        self.assertEqual(code, 0)
        data = json.loads(self.list_path.read_text(encoding="utf-8"))
        self.assertEqual(data["targets"][-1]["chat_username"], "wxid_one")
        self.assertEqual(data["targets"][-1]["kind"], "contact")

    def test_add_refuses_duplicate_names(self):
        wl.main(["init"])
        with self.assertRaises(SystemExit) as ctx:
            wl.main(["add", "--name", "同名群"])
        self.assertEqual(ctx.exception.code, 2)

    def test_add_missing_id(self):
        wl.main(["init"])
        with self.assertRaises(SystemExit):
            wl.main(["add", "--id", "does-not-exist"])

    def test_list_chats_exact_not_substring_id(self):
        code, rows = self._json(["--json", "list-chats", "--query", "57947720564@chatroom"])
        self.assertEqual(code, 0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["match"], "exact")
        self.assertNotIn("decoded_content", rows[0])

    def test_refresh_needed_when_live_mtime_newer(self):
        live = Path(self.tmp.name) / "live.db"
        live.write_bytes(b"x" * 10)
        os.utime(self.db, (100, 100))
        os.utime(live, (200, 200))
        wl.os.environ["JOKER_WECHAT_LIVE_DB"] = str(live)
        code, payload = self._json(["--json", "status"])
        self.assertEqual(code, 0)
        self.assertTrue(payload["refresh_needed"])
        self.assertFalse(payload["live_wechat"])

    def test_refresh_needed_when_live_grew_vs_clone(self):
        live = Path(self.tmp.name) / "live.db"
        clone = Path(self.tmp.name) / "clone.db"
        clone.write_bytes(b"x" * 100)
        live.write_bytes(b"x" * (100 + 40000))
        wl.os.environ["JOKER_WECHAT_LIVE_DB"] = str(live)
        wl.os.environ["JOKER_WECHAT_CLONE_DB"] = str(clone)
        code, payload = self._json(["--json", "status"])
        self.assertEqual(code, 0)
        self.assertTrue(payload["refresh_needed"])
        self.assertGreaterEqual(payload["live_encrypted"]["size_delta"], 32768)


if __name__ == "__main__":
    unittest.main()
