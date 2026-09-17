---
name: baokuan-article-analysis
description: Fetch and analyze WeChat Official Account hot articles / 公众号爆款文章 by sector or keywords. Use when the user asks for 爆款文章分析, 赛道爆款, 公众号爆款数据, reading counts, likes, shares, comments, title patterns, writing style, 爆款原因分析, or writing references for content creation.
---

# 爆款文章分析

## Overview

Use this skill to fetch hot WeChat Official Account article data by sector and generate a daily analysis report. It is for sector-level or keyword-level analysis, not exact historical scraping for one specific account.

The bundled script queries the hot-article data source, merges keywords by sector, deduplicates articles, ranks them, and writes:

- `data.json`: raw structured data
- `report.html`: a minimal visual analysis report with KPI cards, bar charts, ranked article cards, writing style analysis, hot reasons, and writing references

Do not default to Markdown reports. The primary user-facing artifact is `report.html`.

## 数据源与鉴权（重要，2026-09 更新）

本脚本的数据源已变更，请先读这一节：

- **旧接口 `onetotenvip.com` 已失效。** 该域名的 A 记录已于 2026-08-26 被删除（DNS 返回 NODATA），且 ICP 备案失效，阿里云在网络层对该域名一律返回 403 拦截页。任何依赖它的调用都会失败，典型报错为 `[Errno 8] nodename nor servname provided`（DNS 解析不到）或 `CONNECT tunnel failed, response 502`（走代理时代理自行解析失败）。
- **现改为直连上游官方接口 `redfox.hk`（红狐数据），需要 API Key。**

配置 API Key：

```bash
export REDFOX_API_KEY="ak_xxxx..."
```

申请地址：https://redfox.hk/settings/api-keys

未配置 key 时脚本仍会运行，但会向 stderr 打印警告并回退到已失效的旧接口（必然取不到数据）。生成的 `data.json` 中 `backend` 字段标明本次实际使用的后端：`redfox` 或 `legacy-onetotenvip`。**排查取数失败时，先看 `data.json` 的 `errors` 字段和 `backend` 字段 —— 脚本对网络异常做了捕获，退出码为 0 不代表取数成功。**

## Quick Start

配置好 key 后运行：

```bash
python3 ~/.workbuddy/skills/creator-buddy/gzh-Skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector '银发经济=养老金,退休生活,老年健康' \
  --output-dir ./output/baokuan-article-analysis
```

使用默认赛道：

```bash
python3 ~/.codex/skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --output-dir ./output/baokuan-article-analysis
```

Run custom sectors:

```bash
python3 ~/.codex/skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector 'AI Agent=AI Agent,智能体,Agent框架' \
  --sector 'Skill=skill,Skills,AI Skill' \
  --sector 'Claude Code=Claude Code,Codex,AI编程' \
  --output-dir ./output/baokuan-article-analysis
```

Run with a JSON config:

```bash
python3 ~/.codex/skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector-config ~/.codex/skills/baokuan-article-analysis/references/default-sectors.json \
  --days 7 \
  --output-dir ./output/baokuan-article-analysis
```

## Workflow

1. Identify sectors and keywords from the user request.
2. If the user only gives broad sectors, use or adapt `references/default-sectors.json`.
3. Run `scripts/daily_sector_trends.py`.
4. Open the generated `report.html`.
5. Summarize for the user:
   - highest-reading and highest-sharing articles
   - writing style patterns
   - hot article reasons
   - title and topic formulas
   - practical writing references
6. Return the HTML file path as the main artifact.

## Script Options

| Option | Purpose |
|---|---|
| `--sector '赛道=关键词1,关键词2'` | Add one sector. Can repeat. |
| `--sector-config path.json` | Load sectors from JSON object. |
| `--days N` | Lookback window. Default is 7 days. |
| `--start-date YYYY-MM-DD` | Explicit start date. Overrides `--days`. |
| `--max-items-per-sector N` | Limit ranked articles per sector. Default is 10. |
| `--output-dir DIR` | Parent output directory. A date folder is created inside. |
| `--report-date YYYY-MM-DD` | Report date. Default is today. |

## Data Boundaries

- This skill returns hot-list data, not a specific account’s complete recent history.
- `clicksCount` is a public data-source snapshot and may lag behind live WeChat backend reads.
- If a specific account name returns no data, switch to that account’s topic keywords and compare same-sector articles.
- If today’s data is sparse, use `--days 7` or `--days 30`.

## Output Interpretation

Use reading count for reach, share count for spread, comments for discussion, and low-fan high-reading entries for title/structure references. Repeated accounts indicate strong competitors or content sources worth following.
