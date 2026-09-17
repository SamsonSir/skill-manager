#!/usr/bin/env python3
"""把 Wiki 01–07 方法站渲染成学习地图 HTML，并用 Chrome 截成 PNG。"""
from __future__ import annotations

import argparse
import datetime
import html as html_lib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

TZ = datetime.timezone(datetime.timedelta(hours=8))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PIPELINE = ["创意", "分镜", "参考资产", "生成", "声音与剪辑", "复盘"]


class RoadmapError(Exception):
    pass


def esc(text: str) -> str:
    return html_lib.escape(text or "", quote=True)


def poster_height(station_count: int) -> int:
    return 640 + max(station_count, 1) * 230 + 160


def render_html(
    *,
    title: str,
    subtitle: str,
    group: str,
    source: str,
    slogan: str,
    stations: list[dict[str, Any]],
    closing: str,
) -> str:
    cards = []
    for item in stations:
        bullets = item.get("bullets") or ["本站正文见 Wiki。"]
        lis = "\n".join(f"<li>{esc(str(b))}</li>" for b in bullets[:4])
        cards.append(
            f"""
<section class="station">
  <div class="num">{esc(str(item.get("index") or ""))}</div>
  <div class="body">
    <h2>{esc(str(item.get("title") or ""))}</h2>
    <ul>{lis}</ul>
  </div>
</section>
"""
        )
    steps = []
    for i, name in enumerate(PIPELINE):
        arrow = '<span class="arrow">→</span>' if i < len(PIPELINE) - 1 else ""
        steps.append(
            f'<div class="step"><div class="dot">{i + 1}</div><span>{esc(name)}</span></div>{arrow}'
        )
    height = poster_height(len(stations))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>{esc(title)}</title>
<style>
  html, body {{
    margin: 0; padding: 0;
    width: 1080px;
    background: #F3EBDD;
    color: #1F2A32;
    font-family: "Songti SC", "Noto Serif SC", "Source Han Serif SC", Palatino, serif;
  }}
  .poster {{
    width: 1080px;
    min-height: {height}px;
    box-sizing: border-box;
    padding: 56px 52px 48px;
    background:
      radial-gradient(circle at 88% 8%, #f7d9b8 0, transparent 28%),
      linear-gradient(#F6EFE3, #F1E6D4);
  }}
  .kicker {{
    letter-spacing: 0.28em;
    font-size: 13px;
    color: #8A5A32;
    margin: 0 0 10px;
  }}
  h1 {{
    font-size: 54px;
    line-height: 1.12;
    margin: 0 0 8px;
    color: #17364A;
    font-weight: 700;
  }}
  .subtitle {{
    font-size: 28px;
    color: #C45C26;
    margin: 0 0 18px;
  }}
  .meta {{
    font-size: 16px;
    color: #5C6670;
    margin: 0 0 28px;
  }}
  .slogan {{
    font-size: 30px;
    color: #17364A;
    border-top: 2px solid #17364A;
    border-bottom: 2px solid #17364A;
    padding: 16px 0;
    margin: 0 0 32px;
    font-weight: 700;
  }}
  .pipeline {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin: 0 0 36px;
    padding: 18px 8px 8px;
  }}
  .step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #3A4650;
    min-width: 88px;
    text-align: center;
  }}
  .dot {{
    width: 36px; height: 36px; border-radius: 50%;
    border: 2px solid #17364A; display: flex; align-items: center; justify-content: center;
    font-family: "Avenir Next", "PingFang SC", sans-serif;
    font-size: 14px;
    background: #fff;
  }}
  .arrow {{ color: #C45C26; font-size: 20px; }}
  .station {{
    display: grid;
    grid-template-columns: 92px 1fr;
    gap: 18px;
    padding: 22px 0;
    border-bottom: 1px solid rgba(23, 54, 74, 0.12);
  }}
  .num {{
    font-size: 42px;
    color: #C45C26;
    font-weight: 700;
    font-family: "Avenir Next Condensed", "Avenir Next", sans-serif;
    padding-top: 4px;
  }}
  .station h2 {{
    margin: 0 0 10px;
    font-size: 26px;
    color: #17364A;
  }}
  .station ul {{
    margin: 0;
    padding-left: 18px;
    font-size: 17px;
    line-height: 1.55;
    color: #2C3640;
  }}
  .station li + li {{ margin-top: 6px; }}
  footer {{
    margin-top: 28px;
    padding-top: 18px;
    border-top: 3px solid #C45C26;
    font-size: 16px;
    color: #17364A;
  }}
  .close {{
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
  }}
  .note {{ font-size: 13px; color: #6A7380; }}
</style>
</head>
<body>
<article class="poster">
  <p class="kicker">LEARNING MAP</p>
  <h1>{esc(title)}</h1>
  <p class="subtitle">{esc(subtitle)}</p>
  <p class="meta">{esc(group)} · {esc(source)}</p>
  <p class="slogan">{esc(slogan)}</p>
  <div class="pipeline">{''.join(steps)}</div>
  {''.join(cards)}
  <footer>
    <div class="close">{esc(closing)}</div>
    <div class="note">方法正文以飞书 Wiki 01–07 为准。本图只保留可练习的路线，不把群聊流水画进去。</div>
  </footer>
</article>
</body>
</html>
"""


def screenshot(html_path: Path, png_path: Path, height: int) -> None:
    if not Path(CHROME).is_file():
        raise RoadmapError("本机没有 Google Chrome，无法把学习地图截成 PNG")
    profile = tempfile.mkdtemp(prefix="wechat-map-chrome-")
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={profile}",
        "--force-device-scale-factor=2",
        f"--window-size=1080,{height}",
        f"--screenshot={png_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired as exc:
        proc = exc
        if png_path.is_file() and png_path.stat().st_size > 1024:
            return
        raise RoadmapError("Chrome 截图超时，且没有写出 PNG") from exc
    if png_path.is_file() and png_path.stat().st_size > 1024:
        return
    err = ""
    if not isinstance(proc, subprocess.TimeoutExpired):
        err = ((proc.stderr or proc.stdout) or "").strip()
    raise RoadmapError(f"Chrome 截图失败：{err[:400]}")


def build_map(
    stations: list[dict[str, Any]],
    out_dir: Path,
    *,
    group: str,
    source: str,
) -> dict[str, Any]:
    if not stations:
        raise RoadmapError("Wiki 里没有 01–07 方法站，无法生成学习地图")
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)
    html = render_html(
        title="AI视频学习地图",
        subtitle="从复刻，到可控出片",
        group=group,
        source=source,
        slogan="先做出一条，再把它稳定复现。",
        stations=stations,
        closing="真正值得积累的是：创意、观察、可复现的流程。",
    )
    html_path = out_dir / "学习地图.html"
    png_path = out_dir / "学习地图.png"
    html_path.write_text(html, encoding="utf-8")
    os.chmod(html_path, 0o600)
    height = poster_height(len(stations))
    screenshot(html_path, png_path, height)
    os.chmod(png_path, 0o600)
    return {
        "ok": True,
        "html": str(html_path),
        "png": str(png_path),
        "stations": [item.get("title") for item in stations],
    }


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw
    raw = [item for item in raw if item != "--json"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stations-json", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--group", default="")
    parser.add_argument("--source", default="")
    args = parser.parse_args(raw)
    try:
        stations = json.loads(Path(args.stations_json).read_text(encoding="utf-8"))
        result = build_map(stations, Path(args.out), group=args.group, source=args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2) if as_json else result["png"])
        return 0
    except (RoadmapError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
