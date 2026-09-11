#!/usr/bin/env python3
"""只读查询本机微信快照，维护可配置监控名单。不输出聊天正文，不读密钥。"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ACCOUNT_ROOT = Path("/Users/joker/Documents/微信聊天记录/qq179369161")
DEFAULT_DB = ACCOUNT_ROOT / "聊天记录.sqlite"
DEFAULT_WATCHLIST = ACCOUNT_ROOT / "学习整理/Joker/watchlist.json"
DEFAULT_LIVE_MESSAGE_DB = Path(
    "/Users/joker/Library/Containers/com.tencent.xinWeChat/Data/Documents/"
    "xwechat_files/qq179369161_39db/db_storage/message/message_0.db"
)
DEFAULT_CLONED_MESSAGE_DB = ACCOUNT_ROOT / "private/encrypted_databases/message/message_0.db"
TZ = datetime.timezone(datetime.timedelta(hours=8))

DEFAULT_TARGETS = [
    {
        "chat_username": "57947720564@chatroom",
        "label": "多多",
        "kind": "group",
        "enabled": True,
    },
    {
        "chat_username": "50351187410@chatroom",
        "label": "夙愿",
        "kind": "group",
        "enabled": True,
    },
]


def db_path() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_DB", DEFAULT_DB))


def watchlist_path() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_WATCHLIST", DEFAULT_WATCHLIST))


def live_message_db() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_LIVE_DB", DEFAULT_LIVE_MESSAGE_DB))


def cloned_message_db() -> Path:
    return Path(os.environ.get("JOKER_WECHAT_CLONE_DB", DEFAULT_CLONED_MESSAGE_DB))


def live_encrypted_info(snapshot: Path) -> dict:
    live = live_message_db()
    exists = live.is_file()
    live_stat = live.stat() if exists else None
    snap_stat = snapshot.stat() if snapshot.is_file() else None
    cloned = cloned_message_db()
    clone_stat = cloned.stat() if cloned.is_file() else None
    size_delta = None
    if live_stat is not None and clone_stat is not None:
        size_delta = live_stat.st_size - clone_stat.st_size
        newer = size_delta >= 32768
    else:
        newer = bool(live_stat and snap_stat and live_stat.st_mtime > snap_stat.st_mtime)
    return {
        "exists": exists,
        "path": str(live),
        "size": None if live_stat is None else live_stat.st_size,
        "mtime": None if live_stat is None else fmt_ts(int(live_stat.st_mtime)),
        "clone_size": None if clone_stat is None else clone_stat.st_size,
        "size_delta": size_delta,
        "newer_than_snapshot": newer,
    }


def connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise SystemExit(f"找不到只读数据库: {path}")
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    return con


def kind_of(chat_username: str, kind: str | None = None) -> str:
    if kind in {"group", "contact"}:
        return kind
    return "group" if chat_username.endswith("@chatroom") else "contact"


def default_payload() -> dict:
    return {
        "version": 1,
        "note": "enabled 对象才会在「整理微信群」时默认处理。新增须精确 chat_username。",
        "targets": [dict(item) for item in DEFAULT_TARGETS],
    }


def load_watchlist(path: Path, create: bool = False) -> dict:
    if not path.is_file():
        data = default_payload()
        if create:
            save_watchlist(path, data)
        return data
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise SystemExit(f"监控名单格式无效: {path}")
    targets = data.get("targets")
    if not isinstance(targets, list):
        raise SystemExit(f"监控名单缺少 targets: {path}")
    return data


def save_watchlist(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    data = dict(data)
    data["version"] = 1
    data["updated_at"] = datetime.datetime.now(TZ).isoformat(timespec="seconds")
    raw = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=".watchlist.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def snapshot_max_time(con: sqlite3.Connection) -> int | None:
    row = con.execute("SELECT MAX(create_time) AS last_time FROM messages").fetchone()
    return row["last_time"] if row else None


def chat_stats(con: sqlite3.Connection, chat_username: str) -> dict | None:
    row = con.execute(
        """
        SELECT chat_username, chat_name, COUNT(*) AS records,
               MIN(create_time) AS first_time, MAX(create_time) AS last_time
        FROM messages WHERE chat_username = ?
        GROUP BY chat_username, chat_name
        """,
        (chat_username,),
    ).fetchone()
    return dict(row) if row else None


def fmt_ts(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.datetime.fromtimestamp(ts, TZ).isoformat(sep=" ", timespec="seconds")


def status_payload(con: sqlite3.Connection, data: dict) -> dict:
    max_ts = snapshot_max_time(con)
    items = []
    for target in data.get("targets", []):
        username = target.get("chat_username")
        stats = chat_stats(con, username) if username else None
        items.append(
            {
                "chat_username": username,
                "label": target.get("label") or (stats or {}).get("chat_name"),
                "kind": kind_of(username or "", target.get("kind")),
                "enabled": bool(target.get("enabled", True)),
                "in_snapshot": stats is not None,
                "records": None if stats is None else stats["records"],
                "first_time": None if stats is None else fmt_ts(stats["first_time"]),
                "last_time": None if stats is None else fmt_ts(stats["last_time"]),
                "chat_name": None if stats is None else stats["chat_name"],
            }
        )
    live_info = live_encrypted_info(db_path())
    return {
        "watchlist": str(watchlist_path()),
        "snapshot_db": str(db_path()),
        "snapshot_last_time": fmt_ts(max_ts),
        "live_wechat": False,
        "live_encrypted": live_info,
        "refresh_needed": bool(live_info.get("newer_than_snapshot")),
        "enabled_count": sum(1 for item in items if item["enabled"]),
        "targets": items,
    }


def print_status(payload: dict) -> None:
    print(f"快照截止: {payload['snapshot_last_time']}（静态导出，不是活微信）")
    if payload.get("refresh_needed"):
        print("活微信加密库新于可读快照，整理前先运行 scripts/refresh.py refresh")
    print(f"名单: {payload['watchlist']}")
    print(f"启用 {payload['enabled_count']} / {len(payload['targets'])}")
    for item in payload["targets"]:
        flag = "ON " if item["enabled"] else "OFF"
        last = item["last_time"] or "快照中无此会话"
        records = "—" if item["records"] is None else item["records"]
        print(
            f"  [{flag}] {item['label']}  {item['kind']}  "
            f"{item['chat_username']}  {records}条  最新 {last}"
        )


def list_chats(con: sqlite3.Connection, query: str | None, limit: int) -> list[dict]:
    sql = """
        SELECT chat_username, chat_name, COUNT(*) AS records,
               MAX(create_time) AS last_time
        FROM messages
    """
    args: list = []
    if query:
        sql += " WHERE chat_username = ? OR chat_name = ?"
        args.extend([query, query])
    sql += " GROUP BY chat_username, chat_name ORDER BY records DESC LIMIT ?"
    args.append(limit)
    rows = [dict(r) for r in con.execute(sql, args)]
    if query and not rows:
        like = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        rows = [
            dict(r)
            for r in con.execute(
                """
                SELECT chat_username, chat_name, COUNT(*) AS records,
                       MAX(create_time) AS last_time
                FROM messages
                WHERE chat_name LIKE ? ESCAPE '\\'
                GROUP BY chat_username, chat_name
                ORDER BY records DESC
                LIMIT ?
                """,
                (like, limit),
            )
        ]
        for row in rows:
            row["match"] = "name_contains"
    else:
        for row in rows:
            row["match"] = "exact" if query else "top"
    for row in rows:
        row["last_time"] = fmt_ts(row["last_time"])
        row["kind"] = kind_of(row["chat_username"])
    return rows


def resolve_unique_name(con: sqlite3.Connection, name: str) -> dict:
    rows = [
        dict(r)
        for r in con.execute(
            """
            SELECT chat_username, chat_name, COUNT(*) AS records
            FROM messages WHERE chat_name = ?
            GROUP BY chat_username, chat_name
            """,
            (name,),
        )
    ]
    if len(rows) == 1:
        return rows[0]
    if not rows:
        raise SystemExit(f"快照中没有会话名称完全等于: {name}。用 --id 精确添加，或先 list-chats --query。")
    print("同名会话不唯一，请用 --id 指定:", file=sys.stderr)
    for row in rows:
        print(f"  {row['chat_username']}  {row['records']}条", file=sys.stderr)
    raise SystemExit(2)


def add_target(data: dict, con: sqlite3.Connection, chat_username: str, label: str | None) -> dict:
    stats = chat_stats(con, chat_username)
    if stats is None:
        raise SystemExit(f"快照中没有 chat_username={chat_username}")
    for target in data["targets"]:
        if target.get("chat_username") == chat_username:
            target["enabled"] = True
            if label:
                target["label"] = label
            target["kind"] = kind_of(chat_username, target.get("kind"))
            return target
    item = {
        "chat_username": chat_username,
        "label": label or stats["chat_name"] or chat_username,
        "kind": kind_of(chat_username),
        "enabled": True,
    }
    data["targets"].append(item)
    return item


def set_enabled(data: dict, chat_username: str, enabled: bool) -> dict:
    for target in data["targets"]:
        if target.get("chat_username") == chat_username:
            target["enabled"] = enabled
            return target
    raise SystemExit(f"名单中没有: {chat_username}")


def remove_target(data: dict, chat_username: str) -> None:
    before = len(data["targets"])
    data["targets"] = [t for t in data["targets"] if t.get("chat_username") != chat_username]
    if len(data["targets"]) == before:
        raise SystemExit(f"名单中没有: {chat_username}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="查看监控名单与快照新鲜度")
    sub.add_parser("init", help="若名单不存在则写入默认多多/夙愿")

    p_list = sub.add_parser("list-chats", help="列出或精确查找会话，不含正文")
    p_list.add_argument("--query", help="精确 chat_username 或 chat_name；无精确命中才按名称包含搜索")
    p_list.add_argument("--limit", type=int, default=20)

    p_add = sub.add_parser("add", help="按精确 ID 加入监控；名称必须唯一")
    p_add.add_argument("--id", dest="chat_username", help="精确 chat_username")
    p_add.add_argument("--name", help="会话名称完全匹配且唯一时可用")
    p_add.add_argument("--label", help="名单显示名")

    p_on = sub.add_parser("enable", help="启用名单中的对象")
    p_on.add_argument("--id", dest="chat_username", required=True)
    p_off = sub.add_parser("disable", help="停用但保留在名单中")
    p_off.add_argument("--id", dest="chat_username", required=True)
    p_rm = sub.add_parser("remove", help="从名单删除")
    p_rm.add_argument("--id", dest="chat_username", required=True)

    raw_argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw_argv
    parse_argv = [item for item in raw_argv if item != "--json"]
    args = parser.parse_args(parse_argv)
    args.json = as_json
    path = watchlist_path()

    if args.cmd == "init":
        data = load_watchlist(path, create=True)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"已确保名单存在: {path}")
        return 0

    con = connect(db_path())
    try:
        if args.cmd == "status":
            data = load_watchlist(path, create=True)
            payload = status_payload(con, data)
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print_status(payload)
            return 0

        if args.cmd == "list-chats":
            if args.limit < 1:
                parser.error("--limit 必须 >= 1")
            rows = list_chats(con, args.query, args.limit)
            if args.json:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                if not rows:
                    print("没有匹配会话")
                    return 1
                for row in rows:
                    print(
                        f"{row['kind']}\t{row['records']}\t{row['last_time']}\t"
                        f"{row['chat_username']}\t{row['chat_name']}\t{row['match']}"
                    )
            return 0

        data = load_watchlist(path, create=True)
        if args.cmd == "add":
            if args.chat_username:
                username = args.chat_username
            elif args.name:
                username = resolve_unique_name(con, args.name)["chat_username"]
            else:
                parser.error("add 需要 --id 或唯一 --name")
            item = add_target(data, con, username, args.label)
            save_watchlist(path, data)
            if args.json:
                print(json.dumps(item, ensure_ascii=False, indent=2))
            else:
                print(f"已加入监控: {item['label']}  {item['chat_username']}")
            return 0

        if args.cmd == "enable":
            item = set_enabled(data, args.chat_username, True)
            save_watchlist(path, data)
            print(f"已启用: {item['chat_username']}")
            return 0
        if args.cmd == "disable":
            item = set_enabled(data, args.chat_username, False)
            save_watchlist(path, data)
            print(f"已停用: {item['chat_username']}")
            return 0
        if args.cmd == "remove":
            remove_target(data, args.chat_username)
            save_watchlist(path, data)
            print(f"已移出名单: {args.chat_username}")
            return 0
        parser.error("未知命令")
        return 2
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
