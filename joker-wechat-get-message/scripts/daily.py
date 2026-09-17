#!/usr/bin/env python3
"""从本机快照生成固定九块群日报（飞书 XML）。结构由脚本决定，不靠 Agent 现写栏目。"""
from __future__ import annotations

import argparse
import datetime
import html as html_lib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import lark_util as lu
import watchlist as wl

TZ = datetime.timezone(datetime.timedelta(hours=8))
CATALOG_PATH = Path(__file__).resolve().parent / "wiki_catalog.json"
OVERLAY_DIR = Path(__file__).resolve().parent / "overlays"
SOURCE_MARK = re.compile(r"来源：\s*#\d+|成员\d+")
TAKEAWAY_BAN = re.compile(r"以上是该时段可读文字摘录|练习前回到原消息上下文")
WXID_RE = re.compile(r"^wxid_", re.I)
URL_RE = re.compile(r"https?://[^\s<>\"']+")
TAG_RE = re.compile(r"<[^>]+>")
PREFIX_RE = re.compile(r"^(?:wxid_[a-z0-9_]+|[A-Za-z][\w.-]{2,32}):\s*")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
STOP = set("的了是在我有个不就这也都和与或到要会能把被这那你他她它们啊哦呢吧嘛让从对为上中下")

TOPIC_BUCKETS = [
    ("提示词与参考图", re.compile(r"提示词|垫图|参考图|反推|seedance|即梦", re.I)),
    ("额度与成本", re.compile(r"额度|套餐|会员|白嫖|重置|多少钱|报价|询价|预算")),
    ("MV与分镜", re.compile(r"\bMV\b|口型|分镜|音频拆分|对口型|剪辑")),
    ("模型与降智", re.compile(r"降智|蒸馏|gpt|claude|codex|grok|kimi|gemini", re.I)),
    ("工具与开源", re.compile(r"github|开源|skill|工具|插件", re.I)),
    ("产品与变现", re.compile(r"产品视频|变现|接单|成交|回款|客户")),
]

BLOCKS = [
    "🧭 一句话总览",
    "📊 群聊数据",
    "🏆 发言排行 Top 5",
    "🔥 热议话题排行",
    "💡 重点讨论",
    "📌 关键进展",
    "💭 思考摘录",
    "🧰 重点工具 / 资源",
    "🔖 关键词",
]


class DailyError(Exception):
    pass


def catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def day_bounds(day: datetime.date) -> tuple[int, int]:
    start = datetime.datetime(day.year, day.month, day.day, tzinfo=TZ)
    end = start + datetime.timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())


def parse_day(text: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise DailyError("日期格式须为 YYYY-MM-DD") from exc


def iter_days(start: datetime.date, end: datetime.date) -> list[datetime.date]:
    if end < start:
        raise DailyError("结束日期早于开始日期")
    days = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += datetime.timedelta(days=1)
    return days


def load_contacts(con) -> dict[str, tuple[str, str]]:
    try:
        rows = con.execute("select username, remark, nick_name from contacts")
    except Exception:
        return {}
    return {str(r[0]): (str(r[1] or ""), str(r[2] or "")) for r in rows}


def looks_bad_name(name: str) -> bool:
    if not name or WXID_RE.match(name) or CONTROL_RE.search(name):
        return True
    if name.startswith("未知"):
        return True
    return False


def display_name(sender_name: str | None, sender_username: str | None, contacts: dict) -> str:
    raw = CONTROL_RE.sub("", str(sender_name or "")).strip()
    username = str(sender_username or "").strip()
    if looks_bad_name(raw) and username in contacts:
        remark, nick = contacts[username]
        raw = CONTROL_RE.sub("", remark or nick or "").strip() or raw
    if looks_bad_name(raw):
        raw = "未备注"
    return raw


def clean_text(value: str | None) -> str:
    text = str(value or "")
    text = TAG_RE.sub(" ", text)
    text = html_lib.unescape(text)
    text = PREFIX_RE.sub("", text)
    text = CONTROL_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def xml_escape(text: str) -> str:
    return html_lib.escape(text, quote=False)


def load_messages(con, chat_username: str, start_ts: int, end_ts: int) -> list[dict]:
    contacts = load_contacts(con)
    rows = con.execute(
        """
        select source_db, source_table, local_id, sender_username, sender_name,
               create_time, local_type, decoded_content
        from messages
        where chat_username = ? and create_time >= ? and create_time < ?
        order by create_time, source_db, source_table, local_id
        """,
        (chat_username, start_ts, end_ts),
    )
    out = []
    for row in rows:
        item = dict(row)
        item["name"] = display_name(item.get("sender_name"), item.get("sender_username"), contacts)
        item["text"] = clean_text(item.get("decoded_content"))
        item["local_type"] = int(item.get("local_type") or 0)
        out.append(item)
    return out


def type_counts(messages: list[dict]) -> dict[str, int]:
    n = Counter(m["local_type"] for m in messages)
    return {
        "text": n.get(1, 0),
        "image": n.get(3, 0),
        "video": n.get(43, 0),
        "sticker": n.get(47, 0),
        "system": n.get(10000, 0),
        "other": sum(v for k, v in n.items() if k not in {1, 3, 43, 47, 10000}),
    }


def speaker_rank(messages: list[dict], limit: int = 5) -> list[tuple[str, int]]:
    c = Counter()
    for m in messages:
        if m["local_type"] == 10000:
            continue
        c[m["name"]] += 1
    return c.most_common(limit)


def speaker_count(messages: list[dict]) -> int:
    return len({m["name"] for m in messages if m["local_type"] != 10000})


def extract_urls(text: str) -> list[str]:
    urls = []
    for match in URL_RE.findall(text or ""):
        url = match.rstrip(").,，。]")
        if url not in urls:
            urls.append(url)
    return urls


def topic_hits(messages: list[dict]) -> list[tuple[str, int]]:
    counts = Counter()
    for m in messages:
        blob = m["text"]
        if not blob:
            continue
        for name, pattern in TOPIC_BUCKETS:
            if pattern.search(blob):
                counts[name] += 1
    return counts.most_common()


def share_count(messages: list[dict]) -> int:
    n = 0
    for m in messages:
        if m["local_type"] in {3, 43, 47} or m["local_type"] > 1000 or extract_urls(m["text"]):
            n += 1
    return n


def clusters(messages: list[dict], window: int = 1200, min_size: int = 6, limit: int = 5) -> list[dict]:
    usable = [m for m in messages if m["local_type"] != 10000]
    if not usable:
        return []
    groups: list[list[dict]] = []
    cur = [usable[0]]
    for item in usable[1:]:
        if item["create_time"] - cur[-1]["create_time"] <= window:
            cur.append(item)
        else:
            groups.append(cur)
            cur = [item]
    groups.append(cur)
    groups.sort(key=len, reverse=True)
    out = []
    for group in groups:
        if len(group) < min_size and out:
            continue
        names = []
        seen = set()
        excerpts = []
        for m in group:
            if m["name"] not in seen:
                seen.add(m["name"])
                names.append(m["name"])
            if m["local_type"] == 1 and len(m["text"]) >= 8 and m["text"] not in excerpts:
                excerpts.append(m["text"][:120])
            if len(excerpts) >= 4:
                break
        start = datetime.datetime.fromtimestamp(group[0]["create_time"], TZ)
        end = datetime.datetime.fromtimestamp(group[-1]["create_time"], TZ)
        hits = topic_hits(group)
        title = hits[0][0] if hits else f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')} 时段"
        takeaway = ""
        for m in group:
            text = m.get("text") or ""
            if m.get("local_type") != 1 or len(text) < 16:
                continue
            if re.search(r"可以|建议|先|不要|关键是|其实|记住|适合|别急", text):
                takeaway = text[:120]
                break
        if TAKEAWAY_BAN.search(takeaway or ""):
            takeaway = ""
        out.append(
            {
                "title": title,
                "count": len(group),
                "names": names[:8],
                "excerpts": excerpts[:4],
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "what": "；".join(excerpts[:4]),
                "takeaway": takeaway,
            }
        )
        if len(out) >= limit:
            break
    return out


def progress_items(messages: list[dict]) -> list[str]:
    items = []
    for m in messages:
        urls = extract_urls(m["text"])
        if urls:
            host = urlparse(urls[0]).netloc or urls[0]
            items.append(f"{m['name']} 分享了 {host}")
        elif re.search(r"询价|报价|多少钱|预算", m["text"]):
            items.append(f"{m['name']} 提到询价/报价，未见成交证据")
        elif re.search(r"开源|github\.com", m["text"], re.I):
            items.append(f"{m['name']} 提到开源或仓库")
        if len(items) >= 6:
            break
    # dedupe keep order
    seen = set()
    uniq = []
    for item in items:
        if item not in seen:
            seen.add(item)
            uniq.append(item)
    return uniq


def thought_items(messages: list[dict]) -> list[tuple[str, str]]:
    out = []
    for m in messages:
        if m["local_type"] != 1:
            continue
        text = m["text"]
        if len(text) < 12:
            continue
        if re.search(r"其实|发现|感觉|教训|不要|坑|关键是|记住", text):
            out.append((m["name"], text[:160]))
        if len(out) >= 6:
            break
    return out


def tool_items(messages: list[dict]) -> list[tuple[str, str]]:
    out = []
    seen = set()
    for m in messages:
        for url in extract_urls(m["text"]):
            if url in seen:
                continue
            seen.add(url)
            host = urlparse(url).netloc or url
            out.append((f"{m['name']} · {host}", url))
            if len(out) >= 8:
                return out
    return out


def keywords(messages: list[dict], topics: list[tuple[str, int]]) -> list[str]:
    words = [name for name, _ in topics[:6]]
    freq: Counter[str] = Counter()
    for m in messages:
        text = m["text"]
        for token in re.findall(r"[\u4e00-\u9fff]{2,6}", text):
            if token in STOP or len(token) < 2:
                continue
            freq[token] += 1
    for token, n in freq.most_common(12):
        if n >= 3 and token not in words:
            words.append(token)
        if len(words) >= 10:
            break
    return words[:10]


def theme_from(topics: list[tuple[str, int]], fallback: str) -> str:
    if not topics:
        return fallback
    return "、".join(name for name, _ in topics[:2])


def build_day(con, chat_username: str, label: str, wiki_title: str, day: datetime.date) -> dict[str, Any]:
    start_ts, end_ts = day_bounds(day)
    messages = load_messages(con, chat_username, start_ts, end_ts)
    if not messages:
        raise DailyError(f"{day.isoformat()} 没有 {label} 的可读消息")
    first = datetime.datetime.fromtimestamp(messages[0]["create_time"], TZ)
    last = datetime.datetime.fromtimestamp(messages[-1]["create_time"], TZ)
    types = type_counts(messages)
    rank = speaker_rank(messages)
    topics = topic_hits(messages)
    theme = theme_from(topics, "群聊摘录")
    title = f"{day.isoformat()}-{wiki_title}-{theme}"
    payload = {
        "date": day.isoformat(),
        "label": label,
        "wiki_title": wiki_title,
        "chat_username": chat_username,
        "title": title,
        "count": len(messages),
        "speakers": speaker_count(messages),
        "rank": rank,
        "topics": topics,
        "types": types,
        "share": share_count(messages),
        "first": first.strftime("%H:%M:%S"),
        "last": last.strftime("%H:%M:%S"),
        "clusters": clusters(messages),
        "progress": progress_items(messages),
        "thoughts": thought_items(messages),
        "tools": tool_items(messages),
        "keywords": keywords(messages, topics),
        "theme": theme,
    }
    dumped = json.dumps(payload, ensure_ascii=False)
    if SOURCE_MARK.search(dumped):
        raise DailyError("日报 payload 含编号来源或成员编码，已中止")
    return payload


def overview_sentence(p: dict[str, Any]) -> str:
    if str(p.get("overview") or "").strip():
        return str(p["overview"]).strip()
    tops = "、".join(f"{name}（{n}条）" for name, n in p["rank"][:3]) or "—"
    topics = "、".join(name for name, _ in p["topics"][:3])
    text = (
        f"当日可读 {p['count']} 条（{p['first']}—{p['last']}），"
        f"活跃 {p['speakers']} 人。发言最多的是{tops}。"
    )
    if topics:
        text += f"热度集中在：{topics}。"
    text += "附件正文未展开。人名来自本机备注/昵称。"
    return text


def render_xml(p: dict[str, Any]) -> str:
    parts = [
        f"<title>{xml_escape(p['title'])}</title>",
        "<blockquote>",
        "<p>📌 <b>每日交流群日报</b></p>",
        f"<p>群：{xml_escape(p['wiki_title'])}</p>",
        f"<p>日期：{xml_escape(p['date'])}</p>",
        "<p>内容：一句话总览、发言与热议排行、重点讨论、关键进展、思考摘录、重点工具/资源。</p>",
        "</blockquote>",
        '<callout emoji="📌" background-color="light-yellow" border-color="yellow">',
        f"<p>本机快照可读范围是 {xml_escape(p['first'])}—{xml_escape(p['last'])}。"
        "图片、视频附件正文未展开。成员名称用数据库备注/昵称。本页由技能脚本按固定九块生成。</p>",
        "</callout>",
        f"<h2>{BLOCKS[0]}</h2>",
        f"<p>{xml_escape(overview_sentence(p))}</p>",
        f"<h2>{BLOCKS[1]}</h2>",
        "<ul>",
        f"<li>消息总数：{p['count']}（含系统、表情、附件）</li>",
        f"<li>活跃发言账号：{p['speakers']}（非系统消息去重）</li>",
        f"<li>热议话题：{len(p['topics'])}</li>",
        f"<li>分享条目：{p['share']}（图/视频/卡片/含链接，可能重复）</li>",
        (
            f"<li>文字 {p['types']['text']} / 图片 {p['types']['image']} / "
            f"视频 {p['types']['video']} / 系统 {p['types']['system']}</li>"
        ),
        f"<li>统计覆盖：{xml_escape(p['date'])} {xml_escape(p['first'])} 至 {xml_escape(p['last'])}（北京时间）</li>",
        "<li>群人数、新增人数：本快照没有可靠字段，不写</li>",
        "</ul>",
        f"<h2>{BLOCKS[2]}</h2>",
        "<ol>",
    ]
    for name, n in p["rank"]:
        parts.append(f'<li seq="auto">{xml_escape(name)} — {n} 条</li>')
    if not p["rank"]:
        parts.append('<li seq="auto">本期无有效发言账号</li>')
    parts.extend(
        [
            "</ol>",
            "<p>按账号计数，同名不合并；昵称来自本机备注。</p>",
            f"<h2>{BLOCKS[3]}</h2>",
            "<ol>",
        ]
    )
    if p["topics"]:
        for name, n in p["topics"][:7]:
            parts.append(f'<li seq="auto">{xml_escape(name)} — 约 {n} 条命中</li>')
    else:
        parts.append('<li seq="auto">关键词桶未命中，热议见重点讨论时段</li>')
    parts.extend(
        [
            "</ol>",
            "<p>条数是关键词规则命中，可多主题，合计不等于消息总数。</p>",
            f"<h2>{BLOCKS[4]}</h2>",
        ]
    )
    if not p["clusters"]:
        parts.append("<p>时段消息不足以切出重点讨论簇，不编空段。</p>")
    for i, cluster in enumerate(p["clusters"], 1):
        parts.append(f"<h3>{i}. {xml_escape(cluster['title'])}</h3>")
        what = cluster.get("what") or "；".join(cluster.get("excerpts") or [])
        if not what:
            what = "该时段以图片/视频/表情为主，正文未展开。"
        names = "、".join(cluster.get("names") or []) or "—"
        takeaway = (cluster.get("takeaway") or "").strip()
        if not takeaway or TAKEAWAY_BAN.search(takeaway):
            takeaway = "该话题还停在晒图或闲聊，没有提炼出可带走的做法。"
        parts.append(f"<p><b>发生了什么：</b>{xml_escape(what)}</p>")
        parts.append(f"<p><b>群友可参考：</b>{xml_escape(takeaway)}</p>")
        parts.append(f"<p>参与：{xml_escape(names)}</p>")
    parts.append(f"<h2>{BLOCKS[5]}</h2>")
    if p["progress"]:
        parts.append("<ul>")
        for item in p["progress"]:
            parts.append(f"<li>{xml_escape(item)}</li>")
        parts.append("</ul>")
    else:
        parts.append("<p>本期未识别到链接、询价或开源进展。</p>")
    parts.append(f"<h2>{BLOCKS[6]}</h2>")
    if p["thoughts"]:
        parts.append("<ul>")
        for name, text in p["thoughts"]:
            parts.append(f"<li><b>{xml_escape(name)}：</b>「{xml_escape(text)}」</li>")
        parts.append("</ul>")
    else:
        parts.append("<p>本期未发现可摘录的心得句。</p>")
    parts.append(f"<h2>{BLOCKS[7]}</h2>")
    if p["tools"]:
        parts.append("<ul>")
        for label, url in p["tools"]:
            parts.append(
                f"<li><b>{xml_escape(label)}：</b>"
                f'<a href="{xml_escape(url)}">{xml_escape(url)}</a></li>'
            )
        parts.append("</ul>")
    else:
        parts.append("<p>本期没有提取到可展示的 http(s) 链接。</p>")
    keys = " · ".join(p["keywords"]) if p["keywords"] else "本期关键词不足"
    parts.extend(
        [
            f"<h2>{BLOCKS[8]}</h2>",
            f"<p>{xml_escape(keys)}</p>",
            "<h2>接到学习地图</h2>",
            "<p>方法练习看本群 01–07 站与资源页。本页只记当天群聊事实，不代替完整 HTML 来源索引。</p>",
        ]
    )
    xml = "\n".join(parts) + "\n"
    if SOURCE_MARK.search(xml):
        raise DailyError("生成 XML 含编号来源或成员编码，已中止")
    if TAKEAWAY_BAN.search(xml):
        raise DailyError("群友可参考写成了摘录套话，已中止")
    if p.get("clusters") and xml.count("<b>群友可参考：</b>") < len(p["clusters"]):
        raise DailyError("重点讨论缺少群友可参考")
    for heading in BLOCKS:
        if heading not in xml:
            raise DailyError(f"缺少固定栏目：{heading}")
    return xml


def clip(text: str, limit: int = 72) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = re.sub(r"[*_`~<>]", "", text)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def render_card(p: dict[str, Any], wiki_url: str = "") -> dict[str, Any]:
    """Card 2.0：九块日报结构。header blue / default / column_set + collapsible + button."""
    overview = clip(overview_sentence(p), 160)
    rank_lines = []
    for i, (name, n) in enumerate(p.get("rank") or [], 1):
        rank_lines.append(f"{i}. {clip(name, 16)} — {n}")
    if not rank_lines:
        rank_lines.append("本期无有效发言账号")
    topic_lines = []
    for name, n in (p.get("topics") or [])[:5]:
        topic_lines.append(f"- {clip(name, 18)} · {n}")
    if not topic_lines:
        topic_lines.append("- 关键词桶未命中")
    types = p.get("types") or {}
    detail_parts = [
        f"**{BLOCKS[1]}**\n"
        f"文字 {types.get('text', 0)} / 图片 {types.get('image', 0)} / "
        f"视频 {types.get('video', 0)} / 系统 {types.get('system', 0)}；"
        f"覆盖 {p.get('first')}–{p.get('last')}",
        f"**{BLOCKS[4]}**",
    ]
    if p.get("clusters"):
        for i, cluster in enumerate(p["clusters"][:4], 1):
            excerpts = "；".join(clip(x, 36) for x in cluster.get("excerpts") or []) or "该时段以附件为主"
            names = "、".join(clip(n, 10) for n in cluster.get("names") or []) or "—"
            takeaway = clip(cluster.get("takeaway") or "该话题没有可带走的做法", 72)
            detail_parts.append(
                f"**{i}. {clip(cluster.get('title') or '讨论', 24)}**\n"
                f"发生了什么：{excerpts}\n"
                f"群友可参考：{takeaway}\n"
                f"参与：{names}"
            )
    else:
        detail_parts.append("时段消息不足以切出重点讨论簇，不编空段。")
    detail_parts.append(f"**{BLOCKS[5]}**")
    if p.get("progress"):
        detail_parts.extend(f"- {clip(item, 48)}" for item in p["progress"][:5])
    else:
        detail_parts.append("本期未识别到链接、询价或开源进展。")
    detail_parts.append(f"**{BLOCKS[6]}**")
    if p.get("thoughts"):
        for name, text in p["thoughts"][:4]:
            detail_parts.append(f"- **{clip(name, 12)}**：{clip(text, 42)}")
    else:
        detail_parts.append("本期未发现可摘录的心得句。")
    detail_parts.append(f"**{BLOCKS[7]}**")
    if p.get("tools"):
        for label, url in p["tools"][:5]:
            host = urlparse(url).netloc or clip(url, 32)
            detail_parts.append(f"- {clip(label, 24)}：{host}")
    else:
        detail_parts.append("本期没有提取到可展示的 http(s) 链接。")
    keys = " · ".join(p.get("keywords") or []) or "本期关键词不足"
    detail_parts.append(f"**{BLOCKS[8]}**\n{clip(keys, 80)}")
    detail_md = "\n\n".join(detail_parts)
    card: dict[str, Any] = {
        "schema": "2.0",
        "config": {
            "update_multi": True,
            "width_mode": "default",
            "style": {
                "text_size": {
                    "title": {"default": "heading-2", "pc": "heading-2", "mobile": "heading-3"},
                    "body": {"default": "normal", "pc": "normal", "mobile": "normal"},
                    "caption": {"default": "notation", "pc": "notation", "mobile": "notation"},
                },
                "color": {
                    "cus-primary": {"light_mode": "rgba(15,76,129,1)", "dark_mode": "rgba(80,150,255,1)"},
                    "cus-primary-bg": {"light_mode": "rgba(15,76,129,0.08)", "dark_mode": "rgba(80,150,255,0.12)"},
                    "cus-muted": {"light_mode": "rgba(100,106,115,1)", "dark_mode": "rgba(150,155,163,1)"},
                },
            },
        },
        "header": {
            "title": {"tag": "plain_text", "content": f"{p['date']} {p['wiki_title']}"},
            "subtitle": {"tag": "plain_text", "content": f"群日报 · {clip(p.get('theme') or '群聊摘录', 24)}"},
            "template": "blue",
            "icon": {"tag": "standard_icon", "token": "myai_colorful"},
            "text_tag_list": [
                {"tag": "text_tag", "text": {"tag": "plain_text", "content": "日报"}, "color": "blue"},
                {"tag": "text_tag", "text": {"tag": "plain_text", "content": "九块"}, "color": "neutral"},
            ],
        },
        "body": {
            "direction": "vertical",
            "padding": "12px 12px 20px 12px",
            "elements": [
                {
                    "tag": "markdown",
                    "element_id": "overview",
                    "margin": "0px 0px 12px 0px",
                    "content": f"**{BLOCKS[0]}**\n{overview}",
                },
                {
                    "tag": "column_set",
                    "element_id": "metrics",
                    "flex_mode": "none",
                    "horizontal_spacing": "12px",
                    "margin": "0px 0px 12px 0px",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "background_style": "grey-50",
                            "padding": "12px",
                            "vertical_spacing": "2px",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"## <font color='blue'>{p['count']}</font>",
                                    "text_align": "center",
                                },
                                {
                                    "tag": "markdown",
                                    "content": "<font color='grey'>消息</font>",
                                    "text_align": "center",
                                    "text_size": "notation",
                                },
                            ],
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "background_style": "grey-50",
                            "padding": "12px",
                            "vertical_spacing": "2px",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"## <font color='blue'>{p['speakers']}</font>",
                                    "text_align": "center",
                                },
                                {
                                    "tag": "markdown",
                                    "content": "<font color='grey'>活跃</font>",
                                    "text_align": "center",
                                    "text_size": "notation",
                                },
                            ],
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "background_style": "grey-50",
                            "padding": "12px",
                            "vertical_spacing": "2px",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"## <font color='blue'>{p.get('share') or 0}</font>",
                                    "text_align": "center",
                                },
                                {
                                    "tag": "markdown",
                                    "content": "<font color='grey'>分享</font>",
                                    "text_align": "center",
                                    "text_size": "notation",
                                },
                            ],
                        },
                    ],
                },
                {
                    "tag": "column_set",
                    "element_id": "ranks",
                    "flex_mode": "none",
                    "horizontal_spacing": "12px",
                    "margin": "0px 0px 12px 0px",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "background_style": "blue-50",
                            "padding": "12px",
                            "vertical_spacing": "4px",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"**<font color='blue'>{BLOCKS[2]}</font>**\n"
                                    + "\n".join(rank_lines),
                                }
                            ],
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "background_style": "grey-50",
                            "padding": "12px",
                            "vertical_spacing": "4px",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"**<font color='blue'>{BLOCKS[3]}</font>**\n"
                                    + "\n".join(topic_lines),
                                }
                            ],
                        },
                    ],
                },
                {
                    "tag": "collapsible_panel",
                    "element_id": "details",
                    "expanded": False,
                    "margin": "0px 0px 12px 0px",
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "重点讨论 / 进展 / 思考 / 工具",
                        }
                    },
                    "elements": [{"tag": "markdown", "content": detail_md}],
                },
            ],
        },
    }
    if wiki_url:
        card["body"]["elements"].append(
            {
                "tag": "button",
                "element_id": "openwiki",
                "text": {"tag": "plain_text", "content": "打开 Wiki 日报"},
                "type": "primary_filled",
                "width": "fill",
                "margin": "0px",
                "behaviors": [
                    {
                        "type": "open_url",
                        "default_url": wiki_url,
                        "pc_url": wiki_url,
                        "ios_url": wiki_url,
                        "android_url": wiki_url,
                    }
                ],
            }
        )
    else:
        card["body"]["elements"][-1]["margin"] = "0px"
    dumped = json.dumps(card, ensure_ascii=False)
    if SOURCE_MARK.search(dumped):
        raise DailyError("卡片含编号来源或成员编码，已中止")
    return card


def send_card(card: dict[str, Any], user_open_id: str | None = None) -> dict[str, Any]:
    notify = catalog().get("notify") or {}
    user_id = user_open_id or notify.get("user_open_id")
    identity = str(notify.get("as") or "bot")
    if not user_id:
        raise DailyError("wiki_catalog.json 缺少 notify.user_open_id")
    proc = subprocess.run(
        [
            "lark-cli",
            "im",
            "+messages-send",
            "--user-id",
            user_id,
            "--msg-type",
            "interactive",
            "--content",
            json.dumps(card, ensure_ascii=False),
            "--as",
            identity,
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise DailyError(f"飞书卡片发送失败：{(proc.stderr or proc.stdout)[:500]}")
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    inner = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(inner, dict):
        payload = inner
    return {
        "message_id": str(payload.get("message_id") or ""),
        "chat_id": str(payload.get("chat_id") or ""),
        "user_id": user_id,
        "as": identity,
    }


def resolve_target(con, chat_username: str | None, name: str | None) -> dict[str, str]:
    data = catalog()
    groups = data["groups"]
    if chat_username:
        meta = groups.get(chat_username)
        if not meta:
            stats = wl.chat_stats(con, chat_username)
            if stats is None:
                raise DailyError(f"快照中没有 {chat_username}")
            return {
                "chat_username": chat_username,
                "label": stats["chat_name"] or chat_username,
                "wiki_title": stats["chat_name"] or chat_username,
                "node_token": "",
            }
        return {"chat_username": chat_username, **meta}
    if name:
        watch = wl.load_watchlist(wl.watchlist_path(), create=False)
        for target in watch.get("targets", []):
            if target.get("label") == name or target.get("chat_username") == name:
                uid = target["chat_username"]
                meta = groups.get(uid, {})
                return {
                    "chat_username": uid,
                    "label": meta.get("label") or target.get("label") or name,
                    "wiki_title": meta.get("wiki_title") or target.get("label") or name,
                    "node_token": meta.get("node_token") or "",
                }
        raise DailyError(f"监控名单中没有：{name}")
    raise DailyError("需要 --id 或 --name")


def write_outputs(payload: dict[str, Any], xml: str, out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)
    stem = f"{payload['date']}-{payload['label']}"
    xml_path = out_dir / f"{stem}.xml"
    json_path = out_dir / f"{stem}.json"
    xml_path.write_text(xml, encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(xml_path, 0o600)
    os.chmod(json_path, 0o600)
    return {"xml": str(xml_path), "json": str(json_path)}


def lark_json(args: list[str]) -> dict[str, Any]:
    try:
        return lu.lark_json(args)
    except lu.LarkError as exc:
        raise DailyError(str(exc)) from exc


def existing_daily(parent: str, title: str) -> dict[str, str] | None:
    space = catalog()["space_id"]
    data = lark_json(
        [
            "lark-cli",
            "wiki",
            "+node-list",
            "--space-id",
            space,
            "--parent-node-token",
            parent,
            "--page-all",
            "--as",
            "user",
            "--format",
            "json",
        ]
    )
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items") or items.get("nodes") or items.get("children") or []
    dated = None
    day = title[:10] if len(title) >= 10 else ""
    for node in items or []:
        node_title = str(node.get("title") or "")
        hit = {
            "node_token": str(node.get("node_token") or node.get("nodeToken") or ""),
            "obj_token": str(node.get("obj_token") or node.get("objToken") or ""),
        }
        if node_title == title:
            return hit
        if day and node_title.startswith(day + "-"):
            dated = hit
    return dated


def publish(payload: dict[str, Any], xml_path: Path, parent: str) -> dict[str, str]:
    if not parent:
        raise DailyError("该会话还没有 Wiki 目录，先按 feishu-wiki.md 建一级目录")
    space = catalog()["space_id"]
    found = existing_daily(parent, payload["title"])
    if found and found.get("obj_token"):
        node, obj = found["node_token"], found["obj_token"]
        created = False
    else:
        created_node = lark_json(
            [
                "lark-cli",
                "wiki",
                "+node-create",
                "--space-id",
                space,
                "--parent-node-token",
                parent,
                "--title",
                payload["title"],
                "--as",
                "user",
                "--format",
                "json",
            ]
        )
        node = str(created_node.get("node_token") or "")
        obj = str(created_node.get("obj_token") or "")
        created = True
        if not obj:
            raise DailyError("wiki +node-create 没有返回 obj_token")
    update = subprocess.run(
        [
            "lark-cli",
            "docs",
            "+update",
            "--doc",
            obj,
            "--command",
            "overwrite",
            "--content",
            "@" + xml_path.name,
            "--as",
            "user",
            "--format",
            "json",
        ],
        cwd=str(xml_path.parent),
        capture_output=True,
        text=True,
    )
    if update.returncode != 0:
        raise DailyError(f"docs +update 失败：{(update.stderr or update.stdout)[:500]}")
    return {
        "created": str(created).lower(),
        "node_token": node,
        "obj_token": obj,
        "url": f"https://my.feishu.cn/wiki/{node}" if node else "",
        "title": payload["title"],
    }


def apply_overlay(payload: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    if overlay.get("overview"):
        data["overview"] = str(overlay["overview"]).strip()
    if overlay.get("theme"):
        data["theme"] = str(overlay["theme"]).strip()
        data["title"] = f"{data['date']}-{data['wiki_title']}-{data['theme']}"
    if overlay.get("topics"):
        topics = []
        for item in overlay["topics"]:
            if isinstance(item, dict):
                topics.append((str(item.get("title") or ""), int(item.get("heat") or 1)))
            elif isinstance(item, (list, tuple)) and item:
                topics.append((str(item[0]), int(item[1]) if len(item) > 1 else 1))
        data["topics"] = topics
    if overlay.get("clusters"):
        clusters = []
        for item in overlay["clusters"]:
            takeaway = str(item.get("takeaway") or "").strip()
            if TAKEAWAY_BAN.search(takeaway):
                raise DailyError("overlay 的群友可参考是套话")
            clusters.append(
                {
                    "title": str(item.get("title") or "未命名讨论"),
                    "count": int(item.get("count") or 0),
                    "names": list(item.get("names") or []),
                    "excerpts": list(item.get("excerpts") or []),
                    "start": str(item.get("start") or ""),
                    "end": str(item.get("end") or ""),
                    "what": str(item.get("what") or item.get("happened") or ""),
                    "takeaway": takeaway,
                }
            )
        data["clusters"] = clusters
    if overlay.get("progress"):
        data["progress"] = [str(x) for x in overlay["progress"]]
    if overlay.get("thoughts"):
        thoughts = []
        for item in overlay["thoughts"]:
            if isinstance(item, dict):
                thoughts.append((str(item.get("name") or ""), str(item.get("text") or "")))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                thoughts.append((str(item[0]), str(item[1])))
        data["thoughts"] = thoughts
    if overlay.get("tools"):
        tools = []
        for item in overlay["tools"]:
            if isinstance(item, dict):
                tools.append((str(item.get("label") or ""), str(item.get("url") or "")))
            elif isinstance(item, (list, tuple)) and item:
                tools.append((str(item[0]), str(item[1]) if len(item) > 1 else ""))
        data["tools"] = tools
    if overlay.get("keywords"):
        data["keywords"] = [str(x) for x in overlay["keywords"]]
    dumped = json.dumps(data, ensure_ascii=False)
    if SOURCE_MARK.search(dumped) or TAKEAWAY_BAN.search(dumped):
        raise DailyError("overlay 含编号来源、成员编码或群友可参考套话")
    data["overlay_applied"] = True
    return data


def overlay_path(label: str, day: datetime.date) -> Path:
    return OVERLAY_DIR / f"{day.isoformat()}-{label}.json"


def attach_overlay(payload: dict[str, Any], overlay_arg: str | None = None) -> dict[str, Any]:
    if overlay_arg:
        path = Path(overlay_arg)
        if not path.is_file():
            raise DailyError(f"找不到 overlay：{path}")
    else:
        path = overlay_path(str(payload.get("label") or ""), parse_day(str(payload.get("date") or "")))
        if not path.is_file():
            return payload
    overlay = json.loads(path.read_text(encoding="utf-8"))
    data = apply_overlay(payload, overlay)
    data["overlay_file"] = str(path)
    return data


def ensure_publishable(payload: dict[str, Any]) -> None:
    label = str(payload.get("label") or "群")
    day = str(payload.get("date") or "")
    expected = overlay_path(label, parse_day(day)) if day else OVERLAY_DIR / f"YYYY-MM-DD-{label}.json"
    if not payload.get("overlay_applied"):
        raise DailyError(
            f"写入飞书必须先套 overlay（{expected}）。"
            "脚本只算统计和排行；总览、事件名、发生了什么、群友可参考由 Agent 按群主模板填写。"
            "换任何 Agent 都走同一份 JSON，不能直接把机械日报覆盖进 Wiki。"
        )
    for cluster in payload.get("clusters") or []:
        takeaway = str(cluster.get("takeaway") or "").strip()
        if not takeaway or TAKEAWAY_BAN.search(takeaway):
            title = cluster.get("title") or "未命名讨论"
            raise DailyError(f"「{title}」缺少可带走的群友可参考")


def default_out_dir() -> Path:
    return Path(
        os.environ.get(
            "JOKER_WECHAT_DAILY_DIR",
            wl.ACCOUNT_ROOT / "学习整理/Joker/dailies",
        )
    )


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if payload.get("url"):
        print(f"{payload.get('title')}  {payload['url']}")
        return
    print(payload.get("title") or json.dumps(payload, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw
    raw = [item for item in raw if item != "--json"]
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_build = sub.add_parser("build", help="按固定九块生成一日或多日日报")
    p_build.add_argument("--id", dest="chat_username")
    p_build.add_argument("--name", help="监控名单中的 label")
    p_build.add_argument("--date", help="单日 YYYY-MM-DD")
    p_build.add_argument("--from-date")
    p_build.add_argument("--to-date")
    p_build.add_argument("--out", help="输出目录")
    p_build.add_argument("--publish", action="store_true", help="写入飞书 Wiki")
    p_build.add_argument("--notify", action="store_true", help="用飞书机器人把日报卡片发给自己")
    p_build.add_argument("--overlay", help="Agent 填写的讨论 overlay JSON")
    args = parser.parse_args(raw)
    args.json = as_json
    con = wl.connect(wl.db_path())
    try:
        target = resolve_target(con, args.chat_username, args.name)
        if args.date:
            days = [parse_day(args.date)]
        elif args.from_date and args.to_date:
            days = iter_days(parse_day(args.from_date), parse_day(args.to_date))
        else:
            raise DailyError("需要 --date 或 --from-date 与 --to-date")
        out_dir = Path(args.out) if args.out else default_out_dir()
        results = []
        for day in days:
            try:
                payload = build_day(
                    con,
                    target["chat_username"],
                    target["label"],
                    target["wiki_title"],
                    day,
                )
            except DailyError as exc:
                if "没有" in str(exc) and "可读消息" in str(exc):
                    results.append({"ok": False, "date": day.isoformat(), "error": str(exc)})
                    continue
                raise
            payload = attach_overlay(payload, getattr(args, "overlay", None))
            xml = render_xml(payload)
            paths = write_outputs(payload, xml, out_dir)
            item = {
                "ok": True,
                "title": payload["title"],
                "count": payload["count"],
                "xml": paths["xml"],
                "json": paths["json"],
                "overlay_applied": bool(payload.get("overlay_applied")),
            }
            if args.publish:
                ensure_publishable(payload)
                pub = publish(payload, Path(paths["xml"]), target.get("node_token") or "")
                item.update(pub)
            item["_payload"] = payload
            results.append(item)
        ok_days = [item for item in results if item.get("ok")]
        if not ok_days:
            raise DailyError("指定范围内没有可读消息")
        if args.notify:
            last = ok_days[-1]
            card = render_card(last["_payload"], last.get("url") or "")
            notice = send_card(card)
            last["notified"] = notice
        for item in results:
            item.pop("_payload", None)
        emit({"ok": True, "days": results} if len(results) != 1 else results[0], args.json)
        return 0
    except DailyError as exc:
        emit({"ok": False, "error": str(exc)}, True)
        return 1
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
