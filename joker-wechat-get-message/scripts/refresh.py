#!/usr/bin/env python3
"""Refresh the local readable WeChat snapshot from live encrypted DBs using existing salt-indexed keys."""
from __future__ import annotations

import argparse
import ctypes
import datetime
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

from message_decode import decode_message_content
import watchlist as wl

TZ = datetime.timezone(datetime.timedelta(hours=8))
VENV_PYTHON = Path(
    "/Users/joker/Library/Caches/WeChatDataAnalysis/joker-local-access/venv/bin/python"
)
SQLITE_HEADER = b"SQLite format 3"


class RefreshError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def keys_path() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_KEYS", wl.ACCOUNT_ROOT / "private/keys.json"))


def live_db_storage() -> Path:
    override = os.environ.get("JOKER_WECHAT_LIVE_STORAGE")
    if override:
        return Path(override)
    live_file = wl.live_message_db()
    return live_file.parent.parent


def clone_dir() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_CLONE_DIR", wl.ACCOUNT_ROOT / "private/encrypted_databases"))


def report_path() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_REPORT", wl.ACCOUNT_ROOT / "验证报告.json"))


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def file_salt(path: Path) -> str | None:
    with path.open("rb") as handle:
        header = handle.read(16)
    if len(header) < 16:
        return None
    if header.startswith(SQLITE_HEADER):
        return None
    return header.hex()


def load_keys(path: Path) -> dict[str, dict]:
    if not path.is_file():
        raise RefreshError("keys_missing", f"找不到已有密钥文件: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise RefreshError("keys_invalid", "密钥文件格式无效")
    out: dict[str, dict] = {}
    for salt, entry in data.items():
        if not isinstance(salt, str) or len(salt) != 32:
            continue
        if not isinstance(entry, dict) or not isinstance(entry.get("key"), str):
            continue
        key = entry["key"]
        if len(key) != 64:
            continue
        out[salt.lower()] = {"key": key.lower(), "mode": entry.get("mode")}
    if not out:
        raise RefreshError("keys_invalid", "密钥文件没有可用的 salt→key 条目")
    return out


def iter_live_dbs(root: Path) -> list[Path]:
    if not root.is_dir():
        raise RefreshError("live_missing", f"找不到活微信加密目录: {root}")
    return sorted(path for path in root.rglob("*.db") if path.is_file())


def salt_coverage(root: Path, keys: dict[str, dict]) -> dict[str, Any]:
    matched: list[str] = []
    missing: list[str] = []
    plain: list[str] = []
    unreadable: list[str] = []
    for path in iter_live_dbs(root):
        rel = str(path.relative_to(root))
        try:
            salt = file_salt(path)
        except OSError:
            unreadable.append(rel)
            continue
        if salt is None:
            plain.append(rel)
            continue
        if salt.lower() in keys:
            matched.append(rel)
        else:
            missing.append(rel)
    return {
        "db_count": len(matched) + len(missing) + len(plain) + len(unreadable),
        "matched_count": len(matched),
        "missing_count": len(missing),
        "plain_sqlite_count": len(plain),
        "unreadable_count": len(unreadable),
        "missing_databases": missing,
        "unreadable_databases": unreadable,
    }


def assert_keys_cover(coverage: dict[str, Any]) -> None:
    if coverage["unreadable_count"]:
        raise RefreshError(
            "live_unreadable",
            "无法读取部分加密库文件头: " + ", ".join(coverage["unreadable_databases"]),
        )
    if coverage["missing_count"]:
        names = ", ".join(coverage["missing_databases"])
        raise RefreshError(
            "keys_rotated",
            f"有 {coverage['missing_count']} 个库的文件头 salt 不在已有密钥中（{names}）。停止刷新，不重新取钥。",
        )
    if coverage["matched_count"] == 0:
        raise RefreshError("keys_rotated", "活库里没有能用已有密钥打开的加密库")


def clone_path_force(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise RefreshError("clone_destination_exists", f"克隆目标已存在: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o700)
    libc = ctypes.CDLL(None, use_errno=True)
    clonefile = libc.clonefile
    clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    clonefile.restype = ctypes.c_int
    if clonefile(os.fsencode(source), os.fsencode(destination), 0) == 0:
        return
    err = ctypes.get_errno()
    if err in {18, 45}:  # EXDEV / EXDEV-like; fall back to physical copy
        shutil.copytree(source, destination, symlinks=False, dirs_exist_ok=False)
        return
    raise RefreshError("clonefile_failed", f"无法克隆活库: {os.strerror(err)}")


def _sqlcipher():
    try:
        from sqlcipher3 import dbapi2 as cipher  # type: ignore
    except ImportError as exc:
        raise RefreshError(
            "sqlcipher_missing",
            f"当前解释器没有 sqlcipher3，请用 {VENV_PYTHON} 运行",
        ) from exc
    return cipher


def connect_cipher(path: Path, keys: dict[str, dict]):
    salt = file_salt(path)
    if salt is None:
        raise RefreshError("not_encrypted", f"不是 SQLCipher 库: {path.name}")
    entry = keys.get(salt.lower())
    if entry is None:
        raise RefreshError("keys_rotated", f"缺少密钥: {path.name}")
    cipher = _sqlcipher()
    conn = cipher.connect(path.as_uri() + "?mode=ro", uri=True)
    conn.execute('PRAGMA key = "x\'' + entry["key"] + '\'"')
    conn.execute("PRAGMA query_only=ON")
    return conn


def verify_cipher(path: Path, rel: str, keys: dict[str, dict]) -> dict[str, Any]:
    conn = connect_cipher(path, keys)
    try:
        tables = [row[0] for row in conn.execute("select name from sqlite_master where type='table'")]
        integrity = conn.execute("pragma cipher_integrity_check").fetchall()
        entry = {
            "database": rel,
            "table_count": len(tables),
            "schema_read_ok": True,
            "cipher_integrity_ok": not integrity,
        }
        try:
            entry["quick_check_ok"] = conn.execute("pragma quick_check").fetchall() == [("ok",)]
        except Exception as exc:
            entry["quick_check_error"] = str(exc)
        if not entry["cipher_integrity_ok"]:
            raise RefreshError("cipher_integrity", f"完整性检查失败: {rel}")
        return entry
    finally:
        conn.close()


def display_name(contacts: dict[str, tuple], username: str) -> str:
    values = contacts.get(username, ())
    for item in values:
        if item:
            return str(item)
    return username


def flatten_snapshot(clone_root: Path, sqlite_target: Path, keys: dict[str, dict]) -> dict[str, Any]:
    contact_db = clone_root / "contact/contact.db"
    if not contact_db.is_file():
        raise RefreshError("contact_missing", "克隆结果里没有 contact/contact.db")

    conn = connect_cipher(contact_db, keys)
    try:
        contacts = {
            row[0]: row[1:]
            for row in conn.execute("select username,remark,nick_name,alias from contact")
        }
    finally:
        conn.close()

    if sqlite_target.exists():
        sqlite_target.unlink()
    out = sqlite3.connect(sqlite_target)
    out.execute("PRAGMA journal_mode=DELETE")
    out.execute("PRAGMA synchronous=FULL")
    out.execute(
        "create table contacts(username text primary key, remark text, nick_name text, alias text)"
    )
    out.executemany(
        "insert into contacts values(?,?,?,?)",
        [(key, *value) for key, value in contacts.items()],
    )

    report: dict[str, Any] = {
        "account": "qq179369161",
        "exported_at": datetime.datetime.now(TZ).isoformat(),
        "source": "local Mac snapshot",
        "databases": [],
        "message_tables": [],
        "decode_empty_text_messages": 0,
    }
    for path in sorted(clone_root.rglob("*.db")):
        rel = str(path.relative_to(clone_root))
        report["databases"].append(verify_cipher(path, rel, keys))

    initialized = False
    expected = 0
    original_cols: list[str] | None = None
    message_root = clone_root / "message"
    for path in sorted(message_root.glob("*.db")):
        rel = str(path.relative_to(clone_root))
        conn = connect_cipher(path, keys)
        try:
            tabs = [
                row[0]
                for row in conn.execute(
                    "select name from sqlite_master where type='table' and name like 'Msg_%'"
                )
            ]
            if not tabs:
                continue
            users = dict(conn.execute("select rowid, user_name from Name2Id"))
            chatmap = {
                "Msg_" + hashlib.md5(username.encode()).hexdigest(): username
                for username in users.values()
            }
            chatmap.update(
                {
                    "Msg_" + hashlib.md5(username.encode()).hexdigest(): username
                    for username in contacts
                }
            )
            for table in tabs:
                schema = list(conn.execute("pragma table_info(" + quote_ident(table) + ")"))
                cols = [item[1] for item in schema]
                if not initialized:
                    original_cols = cols
                    out.execute(
                        "create table messages(source_db TEXT, source_table TEXT, chat_username TEXT, "
                        "chat_name TEXT, sender_username TEXT, sender_name TEXT, decoded_content TEXT,"
                        + ",".join(quote_ident(item[1]) + " " + (item[2] or "BLOB") for item in schema)
                        + ")"
                    )
                    initialized = True
                if cols != original_cols:
                    raise RefreshError("schema_mismatch", f"表结构不一致: {rel} {table}")
                count = conn.execute("select count(*) from " + quote_ident(table)).fetchone()[0]
                expected += count
                chat = chatmap.get(table, table)
                batch: list[tuple] = []
                written = 0
                for row in conn.execute("select * from " + quote_ident(table)):
                    data = dict(zip(cols, row))
                    sender = users.get(data.get("real_sender_id"), "")
                    text = decode_message_content(data.get("compress_content"), data.get("message_content"))
                    if data.get("local_type") == 1 and not text:
                        report["decode_empty_text_messages"] += 1
                    batch.append(
                        (
                            rel,
                            table,
                            chat,
                            display_name(contacts, chat),
                            sender,
                            display_name(contacts, sender),
                            text,
                            *row,
                        )
                    )
                    if len(batch) >= 1000:
                        out.executemany(
                            "insert into messages values(" + ",".join("?" for _ in batch[0]) + ")",
                            batch,
                        )
                        written += len(batch)
                        batch = []
                if batch:
                    out.executemany(
                        "insert into messages values(" + ",".join("?" for _ in batch[0]) + ")",
                        batch,
                    )
                    written += len(batch)
                if written != count:
                    raise RefreshError("count_mismatch", f"写入行数不一致: {rel} {table}")
                report["message_tables"].append(
                    {
                        "database": rel,
                        "table": table,
                        "rows": count,
                        "chat_mapped": chat != table,
                    }
                )
            out.commit()
            print(
                json.dumps({"processed_database": rel, "messages_so_far": expected}, ensure_ascii=False),
                flush=True,
            )
        finally:
            conn.close()

    out.execute("create index messages_chat_time on messages(chat_username, create_time)")
    out.execute("create index messages_time on messages(create_time)")
    out.execute("create index messages_type on messages(local_type)")
    out.commit()
    actual = out.execute("select count(*) from messages").fetchone()[0]
    if actual != expected:
        raise RefreshError("count_mismatch", f"消息总数不一致: written={actual} expected={expected}")
    if out.execute("pragma quick_check").fetchone() != ("ok",):
        raise RefreshError("sqlite_corrupt", "新快照 quick_check 失败")
    first, last = out.execute("select min(create_time), max(create_time) from messages").fetchone()
    report.update(
        message_count=actual,
        chat_count=out.execute("select count(distinct chat_username) from messages").fetchone()[0],
        source_message_table_count=len(report["message_tables"]),
        unmapped_message_tables=sum(not item["chat_mapped"] for item in report["message_tables"]),
        counts_match=True,
        archive_integrity_ok=True,
        first_message=datetime.datetime.fromtimestamp(first, TZ).isoformat() if first else None,
        last_message=datetime.datetime.fromtimestamp(last, TZ).isoformat() if last else None,
        message_types=[
            {"type": type_id, "count": count}
            for type_id, count in out.execute(
                "select local_type, count(*) from messages group by local_type order by count(*) desc"
            )
        ],
    )
    out.close()
    os.chmod(sqlite_target, 0o600)
    return report


def rotate_backup(sqlite_file: Path) -> Path | None:
    if not sqlite_file.is_file():
        return None
    stamp = datetime.datetime.now(TZ).strftime("%Y%m%d-%H%M%S")
    backup = sqlite_file.with_name(f"聊天记录.sqlite.bak-{stamp}")
    os.replace(sqlite_file, backup)
    parent = sqlite_file.parent
    previous = sorted(parent.glob("聊天记录.sqlite.bak-*"))
    for extra in previous[:-1]:
        try:
            extra.unlink()
        except OSError:
            pass
    return backup


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def public_report(report: dict[str, Any]) -> dict[str, Any]:
    skip = {"message_tables", "databases", "message_types"}
    return {key: value for key, value in report.items() if key not in skip}


def contains_secret(payload: str, keys: dict[str, dict]) -> bool:
    for entry in keys.values():
        key = entry.get("key")
        if isinstance(key, str) and len(key) >= 16 and key in payload:
            return True
    return False


def status_payload() -> dict[str, Any]:
    snapshot = wl.db_path()
    live_info = wl.live_encrypted_info(snapshot)
    payload: dict[str, Any] = {
        "snapshot_db": str(snapshot),
        "live_storage": str(live_db_storage()),
        "live_wechat": False,
        "live_encrypted": live_info,
        "refresh_needed": bool(live_info.get("newer_than_snapshot")),
        "keys_file_exists": keys_path().is_file(),
    }
    if snapshot.is_file():
        con = wl.connect(snapshot)
        try:
            payload["snapshot_last_time"] = wl.fmt_ts(wl.snapshot_max_time(con))
            payload["snapshot_message_count"] = con.execute("select count(*) from messages").fetchone()[0]
        finally:
            con.close()
    else:
        payload["snapshot_last_time"] = None
        payload["snapshot_message_count"] = None
    try:
        keys = load_keys(keys_path())
        coverage = salt_coverage(live_db_storage(), keys)
        payload["salt_coverage"] = {
            "db_count": coverage["db_count"],
            "matched_count": coverage["matched_count"],
            "missing_count": coverage["missing_count"],
            "missing_databases": coverage["missing_databases"],
        }
        payload["can_refresh"] = coverage["missing_count"] == 0 and coverage["matched_count"] > 0
    except RefreshError as exc:
        payload["salt_coverage"] = None
        payload["can_refresh"] = False
        payload["error"] = {"code": exc.code, "message": exc.message}
    return payload


def refresh_snapshot(*, dry_run: bool = False) -> dict[str, Any]:
    os.umask(0o077)
    live = live_db_storage()
    keys = load_keys(keys_path())
    coverage = salt_coverage(live, keys)
    assert_keys_cover(coverage)
    snapshot = wl.db_path()
    live_info = wl.live_encrypted_info(snapshot)
    result = {
        "ok": True,
        "dry_run": dry_run,
        "live_wechat": False,
        "live_encrypted": live_info,
        "salt_coverage": {
            "db_count": coverage["db_count"],
            "matched_count": coverage["matched_count"],
            "missing_count": coverage["missing_count"],
        },
    }
    if dry_run:
        result["code"] = "dry_run"
        result["message"] = "已有密钥覆盖全部活库文件头，可以刷新"
        return result

    private = keys_path().parent
    private.mkdir(parents=True, exist_ok=True)
    os.chmod(private, 0o700)
    staging = private / f".encrypted_databases.new.{os.getpid()}"
    if staging.exists():
        shutil.rmtree(staging)
    sqlite_tmp = snapshot.with_name(f".聊天记录.sqlite.new.{os.getpid()}")
    if sqlite_tmp.exists():
        sqlite_tmp.unlink()
    backup = None
    try:
        clone_path_force(live, staging)
        staged_coverage = salt_coverage(staging, keys)
        assert_keys_cover(staged_coverage)
        report = flatten_snapshot(staging, sqlite_tmp, keys)
        dumped = json.dumps(report, ensure_ascii=False)
        if contains_secret(dumped, keys):
            raise RefreshError("secret_in_report", "验证报告含有密钥，已中止替换")
        backup = rotate_backup(snapshot)
        try:
            os.replace(sqlite_tmp, snapshot)
        except Exception:
            if backup is not None and backup.is_file() and not snapshot.exists():
                os.replace(backup, snapshot)
            raise
        os.chmod(snapshot, 0o600)
        write_report(report_path(), report)
        current_clone = clone_dir()
        old_clone = current_clone.with_name(current_clone.name + ".old")
        if old_clone.exists():
            shutil.rmtree(old_clone)
        if current_clone.exists():
            os.replace(current_clone, old_clone)
        os.replace(staging, current_clone)
        if old_clone.exists():
            shutil.rmtree(old_clone)
        result.update(public_report(report))
        result["backup"] = str(backup) if backup else None
        result["code"] = "refreshed"
        return result
    except Exception:
        if sqlite_tmp.exists():
            sqlite_tmp.unlink()
        if staging.exists():
            shutil.rmtree(staging)
        raise


def maybe_reexec_for_sqlcipher(argv: list[str]) -> None:
    if "sqlcipher3" in sys.modules:
        return
    try:
        import sqlcipher3  # noqa: F401
        return
    except ImportError:
        pass
    venv = Path(os.environ.get("JOKER_WECHAT_SQLCIPHER_PYTHON", VENV_PYTHON))
    # venv/bin/python 可能是指向系统 Python 的符号链接，不能用 resolve() 判断已经在 venv 里。
    if venv.is_file() and Path(sys.executable) != venv:
        os.execv(str(venv), [str(venv), str(Path(__file__).resolve()), *argv])


def emit(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if payload.get("error"):
        err = payload["error"]
        print(f"{err.get('code')}: {err.get('message')}")
        return
    if "snapshot_last_time" in payload:
        print(f"快照截止: {payload.get('snapshot_last_time')}（静态导出，不是活微信）")
        live = payload.get("live_encrypted") or {}
        if live.get("newer_than_snapshot"):
            print("活微信加密库新于可读快照，需要先刷新")
        coverage = payload.get("salt_coverage") or {}
        if coverage:
            print(
                f"密钥覆盖: {coverage.get('matched_count')}/{coverage.get('db_count')} "
                f"缺 {coverage.get('missing_count')}"
            )
        if payload.get("can_refresh"):
            print("可以刷新（不重新取钥）")
        return
    if payload.get("dry_run"):
        print(payload.get("message") or "dry-run ok")
        return
    print(
        f"已刷新快照 {payload.get('message_count')} 条，最新 {payload.get('last_message')}"
    )


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw_argv
    parse_argv = [item for item in raw_argv if item != "--json"]
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="比较活库与可读快照，不解密、不打印密钥")
    p_run = sub.add_parser("refresh", help="用已有密钥重新导出可读快照")
    p_run.add_argument("--dry-run", action="store_true", help="只检查 salt 覆盖，不克隆不写库")
    args = parser.parse_args(parse_argv)
    args.json = as_json

    if args.cmd == "refresh" and not args.dry_run:
        maybe_reexec_for_sqlcipher(raw_argv)

    try:
        if args.cmd == "status":
            payload = status_payload()
            emit(payload, as_json=args.json)
            if payload.get("error"):
                return 2
            return 0
        payload = refresh_snapshot(dry_run=args.dry_run)
        emit(payload, as_json=args.json)
        return 0
    except RefreshError as exc:
        payload = {"ok": False, "code": exc.code, "error": {"code": exc.code, "message": exc.message}}
        emit(payload, as_json=True if args.json else False)
        return 2 if exc.code in {"keys_rotated", "keys_missing", "keys_invalid"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
