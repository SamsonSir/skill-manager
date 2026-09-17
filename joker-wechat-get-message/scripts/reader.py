#!/usr/bin/env python3
"""把 Wiki 子树收成一份可交互阅读页。不用公众号长文主题。"""
from __future__ import annotations

import html as html_lib
import json
import os
import re
from pathlib import Path
from typing import Any

STATION_RE = re.compile(r"^(\d{2})\s+")
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
DAILY_TITLE_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})-(?:.+?)-(.+)$"
)


def esc(text: str) -> str:
    return html_lib.escape(text or "", quote=True)


def short_title(title: str, kind: str) -> str:
    if kind == "daily":
        matched = DAILY_TITLE_RE.match(title or "")
        if matched:
            theme = matched.group(4).strip()
            if len(theme) > 22:
                theme = theme[:21] + "…"
            return f"{matched.group(2)}-{matched.group(3)}  {theme}"
        matched = DATE_RE.match(title or "")
        if matched:
            return title[5:10]
    return title or "未命名"


def md_to_html(md: str) -> str:
    lines = (md or "").splitlines()
    out: list[str] = []
    buf: list[str] = []
    mode = None

    def flush_p() -> None:
        nonlocal buf
        if buf:
            out.append("<p>" + "<br>".join(inline(x) for x in buf) + "</p>")
            buf = []

    def flush_list() -> None:
        nonlocal mode
        if mode == "ul":
            out.append("</ul>")
        elif mode == "ol":
            out.append("</ol>")
        mode = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_p()
            flush_list()
            continue
        if line.strip() in {"> [!NOTE]", "> [!WARNING]", "> [!TIP]", ">"}:
            continue
        if line.startswith(">"):
            flush_p()
            flush_list()
            text = line[1:].lstrip()
            if text:
                out.append(f'<p class="note">{inline(text)}</p>')
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            flush_p()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2)
            hid = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")[:40]
            out.append(f'<h{level} id="{esc(hid)}">{inline(text)}</h{level}>')
            continue
        if line.startswith("- "):
            flush_p()
            if mode != "ul":
                flush_list()
                out.append("<ul>")
                mode = "ul"
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        numbered = re.match(r"^\d+\.\s+(.*)$", line)
        if numbered:
            flush_p()
            if mode != "ol":
                flush_list()
                out.append("<ol>")
                mode = "ol"
            out.append(f"<li>{inline(numbered.group(1))}</li>")
            continue
        if line.strip() == "---":
            flush_p()
            flush_list()
            out.append("<hr>")
            continue
        flush_list()
        buf.append(line)
    flush_p()
    flush_list()
    html = "\n".join(out)
    html = html.replace("<p><strong>发生了什么：</strong>", '<p class="field happened"><span>发生了什么</span> ')
    html = html.replace("<p><strong>群友可参考：</strong>", '<p class="field takeaway"><span>群友可参考</span> ')
    html = html.replace("<p>参与：", '<p class="field people"><span>参与</span> ')
    return wrap_topics(strip_wiki_chrome(html))


def strip_wiki_chrome(html: str) -> str:
    html = re.sub(
        r'<p class="note">(?:📌\s*)?(?:<strong>)?每日交流群日报(?:</strong>)?</p>\s*',
        "",
        html,
    )
    html = re.sub(r'<p class="note">群：.*?</p>\s*', "", html)
    html = re.sub(r'<p class="note">日期：.*?</p>\s*', "", html)
    html = re.sub(r'<p class="note">内容：.*?</p>\s*', "", html)
    return html


def wrap_topics(html: str) -> str:
    parts = re.split(r"(<h3\b[^>]*>.*?</h3>)", html)
    out: list[str] = []
    index = 0
    while index < len(parts):
        chunk = parts[index]
        if chunk.startswith("<h3") and index + 1 < len(parts):
            body = parts[index + 1]
            split_at = re.search(r"<h[12]\b", body)
            head, rest = (body[: split_at.start()], body[split_at.start() :]) if split_at else (body, "")
            out.append('<section class="topic">')
            out.append(chunk)
            out.append(head)
            out.append("</section>")
            out.append(rest)
            index += 2
        else:
            out.append(chunk)
            index += 1
    return "".join(out)


def inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noreferrer">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def kind_of(title: str, home: bool = False) -> str:
    if home:
        return "home"
    if STATION_RE.match(title or ""):
        return "station"
    if (title or "").startswith("资源"):
        return "resource"
    if DATE_RE.match(title or ""):
        return "daily"
    if title == "索引":
        return "index"
    return "page"


def render_reader(
    *,
    title: str,
    wiki_url: str,
    pages: list[dict[str, Any]],
    stations: list[dict[str, Any]],
    map_rel: str,
    out_path: Path,
) -> str:
    items = []
    for page in pages:
        body = page.get("_md") or page.get("md") or ""
        if not body:
            continue
        page_title = page.get("title") or title
        kind = kind_of(page_title, bool(page.get("home")))
        slug = page.get("_anchor") or re.sub(r"[^\w\u4e00-\u9fff]+", "-", page_title).strip("-")
        items.append(
            {
                "id": slug,
                "title": page_title,
                "label": short_title(page_title, kind),
                "kind": kind,
                "html": page.get("html") or page.get("_html") or md_to_html(body),
                "url": f"https://my.feishu.cn/wiki/{page.get('node_token') or ''}",
            }
        )
    payload = json.dumps(items, ensure_ascii=False)
    nav_home = next((p for p in items if p["kind"] == "home"), items[0] if items else None)
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>
:root {{
  --stage:#11100e;
  --rail:#191714;
  --paper:#f6f1e8;
  --ink:#16130f;
  --mute:#6f675d;
  --line:rgba(22,19,15,.1);
  --tungsten:#d08a3a;
  --mark:#9c3b1e;
  --chip:#efe6d8;
  --sans:-apple-system,"Avenir Next","PingFang SC","Noto Sans SC",sans-serif;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; height:100%; background:var(--stage); color:var(--ink); }}
body {{
  display:grid;
  grid-template-columns:272px 1fr;
  min-height:100vh;
  font:16px/1.75 var(--sans);
}}
.rail {{
  background:var(--rail);
  color:#efe7d8;
  padding:22px 16px 28px;
  display:flex; flex-direction:column; gap:14px;
  position:sticky; top:0; height:100vh; overflow:auto;
  border-right:1px solid rgba(255,255,255,.04);
}}
.brand {{
  display:flex; justify-content:space-between; align-items:baseline;
  font-size:11px; letter-spacing:.22em; text-transform:uppercase; color:var(--tungsten);
}}
.rail h1 {{ font-size:20px; line-height:1.3; margin:0; font-weight:620; }}
.search input, .filters button {{
  font:13px/1.3 var(--sans);
}}
.search input {{
  width:100%; border:0; border-radius:8px; padding:10px 12px;
  background:#241f1b; color:#fff; outline:none;
}}
.search input:focus {{ box-shadow:0 0 0 1px var(--tungsten); }}
.filters {{ display:flex; flex-wrap:wrap; gap:6px; }}
.filters button {{
  appearance:none; border:1px solid rgba(255,255,255,.08); background:transparent;
  color:#cbbba4; border-radius:999px; padding:4px 10px; cursor:pointer;
}}
.filters button[aria-pressed="true"] {{ background:#2b241e; color:#fff; border-color:var(--tungsten); }}
nav {{ display:flex; flex-direction:column; gap:4px; flex:1; }}
nav .group {{
  margin:12px 0 4px; font-size:10px; letter-spacing:.18em; color:#8a8074; text-transform:uppercase;
}}
nav button {{
  appearance:none; border:0; background:transparent; color:#d8ccba;
  text-align:left; padding:8px 10px; border-radius:8px; cursor:pointer;
  font:13px/1.4 var(--sans); width:100%;
}}
nav button:hover {{ background:#241f1b; color:#fff; }}
nav button[aria-current="page"] {{ background:#2f281f; color:#fff; }}
.wiki {{ color:var(--tungsten); font-size:12px; text-decoration:none; }}
.hint {{ color:#8a8074; font-size:11px; }}
main {{
  background:var(--paper);
  overflow:auto;
  position:relative;
}}
.sheet {{
  max-width:820px; margin:0 auto; padding:40px 36px 96px;
}}
.hero {{
  display:flex; justify-content:space-between; gap:16px; align-items:end;
  margin-bottom:28px; padding-bottom:18px; border-bottom:1px solid var(--line);
}}
.kicker {{ font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--mark); }}
.hero h2 {{ font-size:32px; line-height:1.2; margin:6px 0 0; font-weight:650; max-width:18ch; text-wrap:pretty; }}
.pager {{ display:flex; gap:8px; }}
.pager button {{
  appearance:none; border:1px solid var(--line); background:transparent;
  padding:6px 10px; border-radius:8px; cursor:pointer; color:var(--ink); font:12px var(--sans);
}}
.pager button:disabled {{ opacity:.35; cursor:default; }}
article h1 {{ display:none; }}
article h2 {{
  font-size:13px; letter-spacing:.16em; text-transform:uppercase;
  color:var(--mark); margin:36px 0 12px; font-weight:650;
}}
article h3 {{ font-size:20px; margin:0 0 12px; font-weight:650; }}
article p, article li {{ color:#2a261f; }}
article a {{ color:var(--mark); }}
.note {{
  display:block; color:var(--mute); font-size:13px; margin:0 0 16px;
  padding:0; background:none; border:0; height:auto; position:static; overflow:visible;
}}
.topic {{
  background:#fffdf8;
  border:1px solid var(--line);
  padding:18px 20px 8px;
  margin:0 0 16px;
  display:grid; gap:10px;
}}
.field {{ margin:0 0 12px; }}
.field span {{
  display:block; font-size:11px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--mute); margin-bottom:4px;
}}
.field.takeaway {{
  background:#1c1814; color:#f6efe4; padding:14px 16px;
}}
.field.takeaway span {{ color:var(--tungsten); }}
.field.people {{ color:var(--mute); font-size:13px; }}
.mapwrap {{ margin:0 0 22px; }}
.mapwrap img {{ width:100%; height:auto; display:block; }}
.empty {{ color:var(--mute); }}
.toc {{
  display:flex; flex-wrap:wrap; gap:8px; margin:0 0 22px;
}}
.toc a {{
  color:var(--mute); text-decoration:none; font-size:12px; border-bottom:1px solid var(--line);
}}
hr {{ border:0; border-top:1px solid var(--line); margin:28px 0; }}
@media (max-width: 900px) {{
  body {{ grid-template-columns:1fr; }}
  .rail {{ height:auto; position:relative; }}
  .sheet {{ padding:24px 16px 64px; }}
  .hero h2 {{ font-size:26px; }}
}}
</style>
</head>
<body>
<aside class="rail">
  <div class="brand"><span>Studio Reader</span><span>Wiki</span></div>
  <h1>{esc(title)}</h1>
  <div class="search"><input id="q" type="search" placeholder="搜索，或按 /" aria-label="搜索"></div>
  <div class="filters" id="filters">
    <button type="button" data-filter="all" aria-pressed="true">全部</button>
    <button type="button" data-filter="daily">日报</button>
    <button type="button" data-filter="station">方法站</button>
    <button type="button" data-filter="resource">资源</button>
  </div>
  <nav id="nav"></nav>
  <a class="wiki" href="{esc(wiki_url)}" target="_blank" rel="noreferrer">打开飞书 Wiki</a>
  <div class="hint">j / k 换页 · / 搜索</div>
</aside>
<main>
  <div class="sheet">
    <div class="hero">
      <div>
        <div class="kicker" id="kicker">阅读</div>
        <h2 id="heading">{esc(title)}</h2>
      </div>
      <div class="pager">
        <button type="button" id="prev" aria-label="上一篇">上一篇</button>
        <button type="button" id="next" aria-label="下一篇">下一篇</button>
      </div>
    </div>
    <div class="mapwrap" id="map" hidden>
      <img src="{esc(map_rel)}" alt="学习地图">
    </div>
    <div class="toc" id="toc"></div>
    <article id="article"></article>
  </div>
</main>
<script id="data" type="application/json">{payload}</script>
<script>
const pages = JSON.parse(document.getElementById('data').textContent);
const nav = document.getElementById('nav');
const article = document.getElementById('article');
const heading = document.getElementById('heading');
const kicker = document.getElementById('kicker');
const map = document.getElementById('map');
const toc = document.getElementById('toc');
const groups = [
  ['home', '总览'],
  ['daily', '群日报'],
  ['station', '方法站'],
  ['resource', '资源'],
  ['index', '索引'],
  ['page', '其他']
];
const kickers = {{home:'总览', daily:'群日报', station:'方法站', resource:'资源', index:'索引', page:'阅读'}};
let filter = 'all';
let currentId = '';
function query() {{ return (document.getElementById('q').value || '').trim(); }}
function visible() {{
  const q = query();
  return pages.filter(p => {{
    if (filter !== 'all' && p.kind !== filter && !(filter === 'daily' && p.kind === 'home')) return false;
    if (!q) return true;
    return (p.title + p.label + p.html).includes(q);
  }});
}}
function grouped() {{
  const vis = visible();
  return groups.map(([kind, label]) => ({{
    kind, label, items: vis.filter(p => p.kind === kind)
  }})).filter(g => g.items.length);
}}
function renderNav(active) {{
  nav.innerHTML = grouped().map(g => {{
    const buttons = g.items.map(p => `<button type="button" data-go="${{p.id}}" ${{p.id===active?'aria-current="page"':''}}>${{p.label}}</button>`).join('');
    return `<div class="group">${{g.label}}</div>${{buttons}}`;
  }}).join('') || '<p class="hint">没有匹配的页。</p>';
}}
function renderToc() {{
  const heads = [...article.querySelectorAll('h2')].slice(0, 9);
  toc.innerHTML = heads.map(h => `<a href="#${{h.id}}" data-scroll="${{h.id}}">${{h.textContent}}</a>`).join('');
}}
function show(id) {{
  const list = visible();
  const wanted = decodeURIComponent(id || '');
  const page = pages.find(p => p.id === wanted) || list[0] || pages[0];
  if (!page) return;
  heading.textContent = page.title;
  kicker.textContent = kickers[page.kind] || '阅读';
  article.innerHTML = page.html || '<p class="empty">这一页没有正文。</p>';
  map.hidden = !(page.kind === 'home' || (page.kind === 'station' && page.title.startsWith('01')));
  const nextHash = '#' + encodeURIComponent(page.id);
  if (location.hash !== nextHash && location.hash !== '#' + page.id) {{
    history.replaceState(null, '', nextHash);
  }}
  renderNav(page.id);
  renderToc();
  currentId = page.id;
  const ids = list.map(p => p.id);
  const at = ids.indexOf(page.id);
  document.getElementById('prev').disabled = at <= 0;
  document.getElementById('next').disabled = at < 0 || at >= ids.length - 1;
  document.getElementById('prev').dataset.go = at > 0 ? ids[at-1] : '';
  document.getElementById('next').dataset.go = at >= 0 && at < ids.length - 1 ? ids[at+1] : '';
  document.querySelector('main').scrollTo({{top:0}});
}}
function neighbor(delta) {{
  const ids = visible().map(p => p.id);
  const at = ids.indexOf(currentId);
  const next = ids[at + delta];
  if (next) show(next);
}}
nav.addEventListener('click', (e) => {{
  const btn = e.target.closest('button[data-go]');
  if (btn) show(btn.getAttribute('data-go'));
}});
document.getElementById('filters').addEventListener('click', (e) => {{
  const btn = e.target.closest('button[data-filter]');
  if (!btn) return;
  filter = btn.getAttribute('data-filter');
  [...document.getElementById('filters').children].forEach(el => el.setAttribute('aria-pressed', el === btn ? 'true' : 'false'));
  const first = visible()[0];
  renderNav((location.hash || '').slice(1));
  if (first) show(first.id);
}});
document.getElementById('q').addEventListener('input', () => renderNav((location.hash || '').slice(1)));
document.getElementById('prev').addEventListener('click', () => neighbor(-1));
document.getElementById('next').addEventListener('click', () => neighbor(1));
toc.addEventListener('click', (e) => {{
  const a = e.target.closest('a[data-scroll]');
  if (!a) return;
  e.preventDefault();
  const el = article.querySelector('#' + CSS.escape(a.getAttribute('data-scroll')));
  if (el) el.scrollIntoView({{block:'start'}});
}});
function startId() {{
  const params = new URLSearchParams(location.search);
  const idx = params.get('i');
  if (idx !== null && pages[Number(idx)]) return pages[Number(idx)].id;
  return params.get('p') || (location.hash || '').slice(1) || {json.dumps(nav_home["id"] if nav_home else "")};
}}
window.addEventListener('hashchange', () => {{
  const raw = decodeURIComponent((location.hash || '').slice(1));
  if (raw && raw !== currentId) show(raw);
}});
document.addEventListener('keydown', (e) => {{
  if (e.key === '/' && document.activeElement.id !== 'q') {{ e.preventDefault(); document.getElementById('q').focus(); }}
  if (e.key === 'j') neighbor(1);
  if (e.key === 'k') neighbor(-1);
}});
show(startId());
</script>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    os.chmod(out_path, 0o600)
    return str(out_path)
