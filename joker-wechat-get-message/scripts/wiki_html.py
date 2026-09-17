#!/usr/bin/env python3
"""把指定群的 Wiki 子树导出为 Markdown，再用宝玉主题转成一份 HTML。"""
from __future__ import annotations

import argparse
import datetime
import html as html_lib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

import daily as dy
import lark_util as lu
import reader
import watchlist as wl

TZ = datetime.timezone(datetime.timedelta(hours=8))
TAG_RE = re.compile(r"<[^>]+>")
AMP_RE = re.compile(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)")
STATION_RE = re.compile(r"^(\d{2})\s+")
SKIP_TAGS = {
    "sub-page-list",
    "whiteboard",
    "sheet",
    "bitable",
    "synced_reference",
    "vc-transcribe-tab",
}
BAOYU_MAIN = Path.home() / ".grok/skills/baoyu-markdown-to-html/scripts/main.ts"
BUN_CANDIDATES = [
    os.environ.get("BUN"),
    shutil.which("bun"),
    str(Path.home() / ".local/node/bin/bun"),
]


class WikiHtmlError(Exception):
    pass


def bun_bin() -> str:
    for item in BUN_CANDIDATES:
        if item and Path(item).is_file():
            return item
    raise WikiHtmlError("找不到 bun，无法调用 baoyu-markdown-to-html")


def slug(title: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title).strip("-")
    return text[:80] or "page"


def fix_amp(xml: str) -> str:
    return AMP_RE.sub("&amp;", xml)


def inner_md(el: ET.Element) -> str:
    chunks: list[str] = []
    if el.text:
        chunks.append(el.text)
    for child in list(el):
        chunks.append(convert_el(child))
        if child.tail:
            chunks.append(child.tail)
    return "".join(chunks)


def convert_el(el: ET.Element) -> str:
    tag = (el.tag or "").lower()
    if tag in SKIP_TAGS:
        return ""
    if tag in {"b", "strong"}:
        return f"**{inner_md(el).strip()}**"
    if tag in {"i", "em"}:
        return f"*{inner_md(el).strip()}*"
    if tag == "code":
        return f"`{inner_md(el).strip()}`"
    if tag == "br":
        return "\n"
    if tag == "a":
        href = el.attrib.get("href") or ""
        text = inner_md(el).strip() or href
        return f"[{text}]({href})" if href else text
    if tag == "cite":
        title = el.attrib.get("title") or "文档"
        doc_id = el.attrib.get("doc-id") or el.attrib.get("token") or ""
        if doc_id:
            return f"[{title}](https://my.feishu.cn/docx/{doc_id})"
        return title
    if tag == "img":
        src = el.attrib.get("url") or el.attrib.get("src") or ""
        alt = el.attrib.get("alt") or "图片"
        if src:
            return f"![{alt}]({src})"
        token = el.attrib.get("token") or ""
        return f"（图片未展开{(' token=' + token) if token else ''}）"
    if tag in {"p"}:
        text = inner_md(el).strip()
        return f"{text}\n\n" if text else ""
    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(tag[1])
        text = inner_md(el).strip()
        return f"{'#' * level} {text}\n\n" if text else ""
    if tag == "title":
        text = inner_md(el).strip()
        return f"# {text}\n\n" if text else ""
    if tag == "blockquote":
        body = inner_md(el).strip()
        lines = [f"> {line}" if line else ">" for line in body.splitlines()]
        return "\n".join(lines) + "\n\n"
    if tag == "callout":
        body = inner_md(el).strip()
        lines = ["> [!NOTE]"]
        for line in body.splitlines() or [""]:
            lines.append(f"> {line}" if line else ">")
        return "\n".join(lines) + "\n\n"
    if tag in {"ul", "ol"}:
        items = []
        index = 1
        for child in list(el):
            if child.tag.lower() != "li":
                continue
            body = inner_md(child).strip()
            if tag == "ol":
                items.append(f"{index}. {body}")
                index += 1
            else:
                items.append(f"- {body}")
        return ("\n".join(items) + "\n\n") if items else ""
    if tag == "li":
        return inner_md(el).strip()
    if tag == "hr":
        return "\n---\n\n"
    if tag == "pre":
        return f"```\n{inner_md(el).rstrip()}\n```\n\n"
    if tag == "table":
        return table_md(el)
    if tag in {"span", "font", "div", "root"}:
        return inner_md(el)
    return inner_md(el)


def table_md(el: ET.Element) -> str:
    rows: list[list[str]] = []
    for row in el.iter():
        if row.tag.lower() != "tr":
            continue
        cells = []
        for cell in list(row):
            if cell.tag.lower() in {"td", "th"}:
                cells.append(inner_md(cell).replace("\n", " ").strip())
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    norm = [r + [""] * (width - len(r)) for r in rows]
    header = norm[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in norm[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n\n"


def xml_to_md(xml: str) -> str:
    text = (xml or "").strip()
    if not text:
        return ""
    wrapped = f"<root>{fix_amp(text)}</root>"
    try:
        root = ET.fromstring(wrapped)
    except ET.ParseError:
        plain = TAG_RE.sub(" ", html_lib.unescape(text))
        return re.sub(r"\s+", " ", plain).strip() + "\n"
    md = convert_el(root)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md + "\n"


def node_list(space_id: str, parent: str) -> list[dict[str, Any]]:
    payload = lu.lark_json(
        [
            "lark-cli",
            "wiki",
            "+node-list",
            "--space-id",
            space_id,
            "--parent-node-token",
            parent,
            "--page-all",
            "--page-limit",
            "0",
            "--as",
            "user",
            "--format",
            "json",
        ]
    )
    return lu.nodes_from(payload)


def walk_tree(space_id: str, parent: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node in node_list(space_id, parent):
        out.append(node)
        if node.get("has_child"):
            out.extend(walk_tree(space_id, str(node.get("node_token") or "")))
    return out


def fetch_xml(obj_token: str) -> str:
    payload = lu.lark_json(
        [
            "lark-cli",
            "docs",
            "+fetch",
            "--doc",
            obj_token,
            "--doc-format",
            "xml",
            "--as",
            "user",
            "--format",
            "json",
        ]
    )
    document = payload.get("document") if isinstance(payload, dict) else None
    if not isinstance(document, dict):
        document = payload
    return str((document or {}).get("content") or "")


def download_images(md: str, img_dir: Path) -> str:
    img_dir.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(r"!\[([^\]]*)\]\((https?://[^)]+)\)")
    mapping: dict[str, str] = {}
    index = 1
    for alt, url in pattern.findall(md):
        if url in mapping:
            continue
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            ext = ".png"
        name = f"wiki-{index:02d}{ext}"
        dest = img_dir / name
        try:
            with urlopen(url, timeout=20) as resp:
                dest.write_bytes(resp.read())
            mapping[url] = f"imgs/{name}"
            index += 1
        except Exception:
            mapping[url] = url
    if not mapping:
        return md

    def repl(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2)
        return f"![{alt}]({mapping.get(url, url)})"

    return pattern.sub(repl, md)


def station_summary(md: str) -> list[str]:
    lines = []
    for block in re.split(r"\n{2,}", md):
        text = re.sub(r"^#+\s*", "", block).strip()
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = text.replace("**", "").replace("*", "")
        if not text or text.startswith(">") or text.startswith("#"):
            continue
        if text.startswith("title:") or len(text) < 8:
            continue
        if STATION_RE.match(text):
            continue
        for sentence in re.split(r"(?<=[。！？])", text):
            piece = sentence.strip()
            if STATION_RE.match(piece):
                continue
            if 8 <= len(piece) <= 80:
                lines.append(piece)
            elif len(piece) > 80:
                lines.append(piece[:77] + "…")
            if len(lines) >= 4:
                return lines
    return lines[:4]


def baoyu_convert(md_path: Path, title: str) -> dict[str, Any]:
    bun = bun_bin()
    if not BAOYU_MAIN.is_file():
        raise WikiHtmlError(f"找不到宝玉转换脚本：{BAOYU_MAIN}")
    env = os.environ.copy()
    local_bin = str(Path.home() / ".local/node/bin")
    env["PATH"] = local_bin + os.pathsep + env.get("PATH", "")
    proc = subprocess.run(
        [
            bun,
            str(BAOYU_MAIN),
            str(md_path),
            "--theme",
            "grace",
            "--color",
            "blue",
            "--font-family",
            "serif-cjk",
            "--keep-title",
            "--no-mermaid",
            "--title",
            title,
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(md_path.parent),
    )
    if proc.returncode != 0:
        raise WikiHtmlError(f"宝玉 HTML 转换失败：{(proc.stderr or proc.stdout)[:500]}")
    text = (proc.stdout or "").strip()
    try:
        return json.loads(text) if text else {"htmlPath": str(md_path.with_suffix(".html"))}
    except json.JSONDecodeError:
        html_path = md_path.with_suffix(".html")
        if not html_path.is_file():
            raise WikiHtmlError("宝玉转换没有返回 JSON，也没有写出 HTML")
        return {"htmlPath": str(html_path), "raw": text[:200]}


def export_group(label: str | None, chat_username: str | None, out_dir: Path) -> dict[str, Any]:
    con = wl.connect(wl.db_path())
    try:
        target = dy.resolve_target(con, chat_username, label)
    finally:
        con.close()
    parent = target.get("node_token") or ""
    if not parent:
        raise WikiHtmlError(f"{target['label']} 还没有 Wiki 目录")
    catalog = dy.catalog()
    space_id = str(catalog["space_id"])
    home = lu.lark_json(
        [
            "lark-cli",
            "wiki",
            "+node-get",
            "--node-token",
            parent,
            "--as",
            "user",
            "--format",
            "json",
        ]
    )
    home_title = str(home.get("title") or target.get("wiki_title") or target["label"])
    pages = [
        {
            "title": home_title,
            "node_token": str(home.get("node_token") or parent),
            "obj_token": str(home.get("obj_token") or ""),
            "obj_type": str(home.get("obj_type") or "docx"),
            "home": True,
        }
    ]
    for node in walk_tree(space_id, parent):
        pages.append(
            {
                "title": str(node.get("title") or ""),
                "node_token": str(node.get("node_token") or ""),
                "obj_token": str(node.get("obj_token") or ""),
                "obj_type": str(node.get("obj_type") or ""),
                "home": False,
            }
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)
    img_dir = out_dir / "imgs"
    exported: list[dict[str, Any]] = []
    stations: list[dict[str, Any]] = []
    parts = [
        f"# {home_title}",
        "",
        f"> 来源：[飞书 Wiki](https://my.feishu.cn/wiki/{parent}) · {catalog.get('space_name')}",
        f"> 导出时间：{datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %z')}",
        "> 本页是该群 Wiki 子树的完整本地副本，不是另写一份摘要。",
        "",
        "## 目录",
        "",
    ]
    for page in pages:
        if not page.get("obj_token") or page.get("obj_type") not in {"", "docx", "doc"}:
            exported.append({**page, "skipped": True})
            continue
        xml = fetch_xml(page["obj_token"])
        md = xml_to_md(xml)
        if not md.startswith("# "):
            md = f"# {page['title']}\n\n{md}"
        md = download_images(md, img_dir)
        page_md = md
        exported.append({**page, "chars": len(page_md), "skipped": False})
        match = STATION_RE.match(page["title"])
        if match:
            stations.append(
                {
                    "index": match.group(1),
                    "title": page["title"],
                    "node_token": page["node_token"],
                    "url": f"https://my.feishu.cn/wiki/{page['node_token']}",
                    "bullets": station_summary(page_md),
                }
            )
        anchor = slug(page["title"])
        parts.append(f"- [{page['title']}](#{anchor})")
        page["_md"] = page_md
        page["_anchor"] = anchor
    parts.append("")
    parts.append("---")
    parts.append("")
    for page in pages:
        body = page.get("_md")
        if not body:
            continue
        parts.append(f'<a id="{page["_anchor"]}"></a>')
        parts.append("")
        parts.append(body.rstrip())
        parts.append("")
        parts.append("---")
        parts.append("")
    md_text = "\n".join(parts).rstrip() + "\n"
    md_path = out_dir / "wiki.md"
    md_path.write_text(md_text, encoding="utf-8")
    os.chmod(md_path, 0o600)
    html_path = reader.render_reader(
        title=home_title,
        wiki_url=f"https://my.feishu.cn/wiki/{parent}",
        pages=pages,
        stations=stations,
        map_rel="学习地图.png",
        out_path=out_dir / "wiki.html",
    )
    return {
        "ok": True,
        "label": target["label"],
        "wiki_title": home_title,
        "node_token": parent,
        "url": f"https://my.feishu.cn/wiki/{parent}",
        "pages": len(exported),
        "exported": exported,
        "stations": stations,
        "md": str(md_path),
        "html": html_path,
        "theme": "baoyu-design",
        "color": "ink-navy",
        "font": "serif-cjk",
    }


def default_out_dir(label: str) -> Path:
    stamp = datetime.datetime.now(TZ).strftime("%Y%m%d-%H%M%S")
    return wl.ACCOUNT_ROOT / "学习整理" / "Joker" / stamp / label


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw
    raw = [item for item in raw if item != "--json"]
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_export = sub.add_parser("export", help="导出群 Wiki 子树为宝玉主题 HTML")
    p_export.add_argument("--id", dest="chat_username")
    p_export.add_argument("--name")
    p_export.add_argument("--out")
    args = parser.parse_args(raw)
    try:
        if args.cmd != "export":
            raise WikiHtmlError("只支持 export")
        if not args.chat_username and not args.name:
            raise WikiHtmlError("需要 --name 或 --id")
        out_dir = Path(args.out) if args.out else default_out_dir(args.name or "wiki")
        result = export_group(args.name, args.chat_username, out_dir)
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["html"])
        return 0
    except (WikiHtmlError, dy.DailyError, lu.LarkError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
