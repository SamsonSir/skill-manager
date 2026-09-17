#!/usr/bin/env python3
"""整理一个监控群：刷新快照（如需要）→ 写 Wiki 日报 → 导出 Wiki HTML → 学习地图 → 飞书机器人卡片。"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import daily as dy
import roadmap
import watchlist as wl
import wiki_html as wh

TZ = datetime.timezone(datetime.timedelta(hours=8))
SKILL_DIR = Path(__file__).resolve().parent


class OrganizeError(Exception):
    pass


def today() -> datetime.date:
    return datetime.datetime.now(TZ).date()


def run_refresh() -> dict[str, Any]:
    import refresh as rf

    python = str(rf.VENV_PYTHON if rf.VENV_PYTHON.is_file() else sys.executable)
    proc = subprocess.run(
        [python, str(SKILL_DIR / "refresh.py"), "refresh", "--json"],
        capture_output=True,
        text=True,
        cwd=str(SKILL_DIR),
    )
    text = (proc.stdout or "").strip()
    payload: dict[str, Any]
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"ok": proc.returncode == 0, "raw": text[:400]}
    if proc.returncode != 0:
        err = payload.get("error") or payload.get("raw") or "快照刷新失败"
        if isinstance(err, dict):
            err = err.get("message") or str(err)
        raise OrganizeError(str(err))
    return payload


def maybe_refresh(skip: bool) -> dict[str, Any]:
    con = wl.connect(wl.db_path())
    try:
        status = wl.status_payload(con, wl.load_watchlist(wl.watchlist_path(), create=False))
    finally:
        con.close()
    if skip:
        return {"skipped": True, "refresh_needed": status.get("refresh_needed")}
    if not status.get("refresh_needed"):
        return {"skipped": True, "refresh_needed": False}
    return {"skipped": False, **run_refresh()}


def build_daily(target: dict[str, str], day: datetime.date, skip_publish: bool) -> dict[str, Any]:
    daily_dir = Path(os.environ.get("JOKER_WECHAT_DAILY_DIR", str(dy.default_out_dir())))
    con = wl.connect(wl.db_path())
    try:
        payload = dy.build_day(
            con,
            target["chat_username"],
            target["label"],
            target["wiki_title"],
            day,
        )
    except dy.DailyError as exc:
        if "没有" in str(exc) and "可读消息" in str(exc):
            return {"ok": False, "error": str(exc), "json": "", "xml": "", "url": ""}
        raise
    finally:
        con.close()
    payload = dy.attach_overlay(payload)
    xml = dy.render_xml(payload)
    paths = dy.write_outputs(payload, xml, daily_dir)
    item: dict[str, Any] = {
        "ok": True,
        "title": payload["title"],
        "count": payload["count"],
        "json": paths["json"],
        "xml": paths["xml"],
        "url": "",
        "payload": payload,
        "overlay_applied": bool(payload.get("overlay_applied")),
        "overlay_file": payload.get("overlay_file") or "",
    }
    if not skip_publish:
        try:
            dy.ensure_publishable(payload)
        except dy.DailyError as exc:
            item["publish_skipped"] = str(exc)
        else:
            pub = dy.publish(payload, Path(paths["xml"]), target.get("node_token") or "")
            item["url"] = pub.get("url") or ""
            item["node_token"] = pub.get("node_token") or ""
            item["created"] = pub.get("created")
    return item


def organize(
    *,
    name: str | None,
    chat_username: str | None,
    day: datetime.date,
    out_dir: Path,
    skip_refresh: bool,
    skip_publish: bool,
    skip_html: bool,
    skip_map: bool,
    skip_notify: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": True, "date": day.isoformat(), "out": str(out_dir)}
    result["refresh"] = maybe_refresh(skip_refresh)
    con = wl.connect(wl.db_path())
    try:
        target = dy.resolve_target(con, chat_username, name)
    finally:
        con.close()
    result["label"] = target["label"]
    result["wiki_title"] = target["wiki_title"]

    daily_item = build_daily(target, day, skip_publish)
    payload = daily_item.pop("payload", None)
    result["daily"] = daily_item

    if not skip_html:
        exported = wh.export_group(target["label"], target["chat_username"], out_dir)
        result["html"] = {
            "ok": True,
            "path": exported["html"],
            "md": exported["md"],
            "pages": exported["pages"],
            "url": exported["url"],
            "theme": exported["theme"],
        }
        stations = exported.get("stations") or []
        result["stations"] = [item.get("title") for item in stations]
        if not skip_map:
            source = f"Wiki 01–07 · {datetime.datetime.now(TZ).strftime('%Y-%m-%d')}"
            result["map"] = roadmap.build_map(
                stations,
                out_dir,
                group=target["wiki_title"],
                source=source,
            )
    elif not skip_map:
        raise OrganizeError("生成学习地图需要先导出 Wiki，不能 --skip-html")

    if not skip_notify:
        if not payload:
            result["notify"] = {"ok": False, "error": "当日没有可读消息，未发卡片"}
        elif not payload.get("overlay_applied"):
            result["notify"] = {
                "ok": False,
                "error": "没有 overlay，未发卡片。先写 scripts/overlays/日期-群名.json 再整理。",
            }
        else:
            card = dy.render_card(payload, daily_item.get("url") or "")
            notice = dy.send_card(card)
            out_dir.mkdir(parents=True, exist_ok=True)
            card_path = out_dir / "日报卡片.json"
            card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result["notify"] = {
                "ok": True,
                **notice,
                "card": str(card_path),
                "wiki_url": daily_item.get("url") or "",
            }
    return result


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw
    raw = [item for item in raw if item != "--json"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="chat_username")
    parser.add_argument("--name")
    parser.add_argument("--date")
    parser.add_argument("--out")
    parser.add_argument("--skip-refresh", action="store_true")
    parser.add_argument("--skip-publish", action="store_true")
    parser.add_argument("--skip-html", action="store_true")
    parser.add_argument("--skip-map", action="store_true")
    parser.add_argument("--skip-notify", action="store_true")
    args = parser.parse_args(raw)
    try:
        if not args.chat_username and not args.name:
            raise OrganizeError("需要 --name 或 --id，例如 --name 多多")
        day = dy.parse_day(args.date) if args.date else today()
        label = args.name or args.chat_username or "group"
        out_dir = Path(args.out) if args.out else wh.default_out_dir(label)
        result = organize(
            name=args.name,
            chat_username=args.chat_username,
            day=day,
            out_dir=out_dir,
            skip_refresh=args.skip_refresh,
            skip_publish=args.skip_publish,
            skip_html=args.skip_html,
            skip_map=args.skip_map,
            skip_notify=args.skip_notify,
        )
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"{result.get('label')} {result['date']}")
            if result.get("html", {}).get("path"):
                print(result["html"]["path"])
            if result.get("map", {}).get("png"):
                print(result["map"]["png"])
            if result.get("notify", {}).get("wiki_url"):
                print(result["notify"]["wiki_url"])
        return 0 if result.get("ok") else 1
    except (OrganizeError, dy.DailyError, wh.WikiHtmlError, roadmap.RoadmapError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
