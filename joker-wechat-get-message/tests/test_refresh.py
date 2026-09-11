#!/usr/bin/env python3
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import refresh as rf  # noqa: E402
from message_decode import decode_message_content  # noqa: E402


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.live = self.root / "live"
        self.live.mkdir()
        self.keys_file = self.root / "keys.json"
        self.secret = "a" * 64
        self.salt = "b" * 32
        (self.live / "message").mkdir()
        db = self.live / "message" / "message_0.db"
        db.write_bytes(bytes.fromhex(self.salt) + b"\x00" * 16)
        self.keys_file.write_text(
            json.dumps({self.salt: {"key": self.secret, "mode": "raw_enc_key"}}),
            encoding="utf-8",
        )
        self._old = {
            key: os.environ.get(key)
            for key in (
                "JOKER_WECHAT_KEYS",
                "JOKER_WECHAT_LIVE_STORAGE",
                "JOKER_WECHAT_LIVE_DB",
                "JOKER_WECHAT_DB",
                "JOKER_WECHAT_WATCHLIST",
                "JOKER_WECHAT_REPORT",
                "JOKER_WECHAT_CLONE_DIR",
                "JOKER_WECHAT_CLONE_DB",
            )
        }
        os.environ["JOKER_WECHAT_KEYS"] = str(self.keys_file)
        os.environ["JOKER_WECHAT_LIVE_STORAGE"] = str(self.live)
        os.environ["JOKER_WECHAT_LIVE_DB"] = str(db)
        os.environ["JOKER_WECHAT_DB"] = str(self.root / "chat.sqlite")
        os.environ["JOKER_WECHAT_WATCHLIST"] = str(self.root / "watchlist.json")
        os.environ["JOKER_WECHAT_REPORT"] = str(self.root / "report.json")
        os.environ["JOKER_WECHAT_CLONE_DIR"] = str(self.root / "clone")
        os.environ["JOKER_WECHAT_CLONE_DB"] = str(self.root / "clone" / "message" / "message_0.db")

    def tearDown(self):
        for key, value in self._old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def test_salt_coverage_matches_header(self):
        keys = rf.load_keys(self.keys_file)
        coverage = rf.salt_coverage(self.live, keys)
        self.assertEqual(coverage["matched_count"], 1)
        self.assertEqual(coverage["missing_count"], 0)
        self.assertNotIn(self.secret, json.dumps(coverage))

    def test_missing_salt_stops_without_refresh(self):
        other = self.live / "message" / "message_1.db"
        other.write_bytes(b"\x11" * 16 + b"\x00" * 16)
        keys = rf.load_keys(self.keys_file)
        coverage = rf.salt_coverage(self.live, keys)
        with self.assertRaises(rf.RefreshError) as ctx:
            rf.assert_keys_cover(coverage)
        self.assertEqual(ctx.exception.code, "keys_rotated")
        self.assertIn("message_1.db", ctx.exception.message)
        self.assertNotIn(self.secret, ctx.exception.message)

    def test_dry_run_stdout_hides_keys(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = rf.main(["--json", "refresh", "--dry-run"])
        self.assertEqual(code, 0)
        dumped = buf.getvalue()
        self.assertNotIn(self.secret, dumped)
        payload = json.loads(dumped)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["live_wechat"])

    def test_source_forbids_capture_paths(self):
        text = Path(rf.__file__).read_text(encoding="utf-8")
        for needle in (
            "import wechat_decrypt_tool",
            "macos_clone_capture",
            "macos_db_key_capture",
            "capture-launch",
        ):
            self.assertNotIn(needle, text)

    def test_decode_plain_text(self):
        self.assertEqual(decode_message_content(None, "hello"), "hello")

    def test_clone_refuses_existing_destination(self):
        dest = self.root / "already"
        dest.mkdir()
        with self.assertRaises(rf.RefreshError) as ctx:
            rf.clone_path_force(self.live, dest)
        self.assertEqual(ctx.exception.code, "clone_destination_exists")


if __name__ == "__main__":
    unittest.main()
