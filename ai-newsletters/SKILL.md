---
name: ai-newsletters
description: 整理 AI 简报内容，智能去重和排序。当用户调用 /ai-newsletters、/日报、/news 或 /start-my-day 需要简报内容时触发。从 TLDR AI、The Rundown AI 和 ai-news-radar 聚合数据（TopHub、Buzzing、NewsNow、AIbase等10+中英文信息源），生成包含精选推荐、AI 动态、生产力工具、WaytoAGI 精选的每日摘要。智能去重、按相关性和新鲜度排序，为高价值内容提供创作角度。主动识别用户对 AI 资讯的需求并提供高质量内容聚合。
---
# AI Newsletter Curation

Fetch, deduplicate, and rank AI newsletter content into a daily digest.

## RSS Sources

- **TLDR AI**: `https://bullrich.dev/tldr-rss/ai.rss`
- **The Rundown AI**: `https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml`

## ai-news-radar 数据源（补充）

除 RSS 外，还需拉取 LearnPrompt/ai-news-radar 的聚合数据作为补充来源：

- **AI 新闻聚合（24h）**: `https://raw.githubusercontent.com/LearnPrompt/ai-news-radar/master/data/latest-24h.json`
  - 字段：`data.items[]` → `title`/`title_zh`/`url`/`site_name`/`source`
  - 10+ 中英文信息源（TopHub、Buzzing、NewsNow、AIbase 等），每 30 分钟更新
- **WaytoAGI 近 7 天**: `https://raw.githubusercontent.com/LearnPrompt/ai-news-radar/master/data/waytoagi-7d.json`
  - 字段：`data.updates_7d[]` → `title`/`url`/`date`
  - 来自 WaytoAGI 飞书知识库的精选 AI 学习资源

## Workflow

1. **Check cache**: Look for `50_资源/Newsletters/YYYY-MM/YYYY-MM-DD-摘要.md`. If exists with today's date, return cached content.

2. **Fetch feeds**: Use WebFetch on both RSS URLs AND the two ai-news-radar JSON URLs. For RSS: extract title, link, pubDate, description. For ai-news-radar JSON: parse `items[]` array (use `title_zh` if available, fallback to `title`). For WaytoAGI JSON: parse `updates_7d[]` array.

3. **Deduplicate**: Merge items with similar titles (80%+ word overlap). Keep longer description, track both sources.

4. **Rank items** by:
   - AI relevance (LLM, GPT, Claude, agents, ML keywords)
   - Productivity relevance (workflow, automation, tools, PKM)
   - Recency (newer = higher)
   - Novelty (check recent archives, penalize repeats)

5. **Generate digest**: See [TEMPLATE.md](TEMPLATE.md) for format. Include:
   - 精选推荐 (3-5 highest scoring) with content creation angles
   - AI动态 section
   - 生产力工具 section
   - WaytoAGI 精选 section (top 5 from WaytoAGI 7d data, with dates)
   - Stats footer (note source counts: RSS + ai-news-radar + WaytoAGI)

6. **Save files**:
   - `50_资源/Newsletters/YYYY-MM/YYYY-MM-DD-摘要.md` (curated)
   - `50_资源/Newsletters/YYYY-MM/原始数据/YYYY-MM-DD_TLDR-AI-Raw.md`
   - `50_资源/Newsletters/YYYY-MM/原始数据/YYYY-MM-DD_Rundown-AI-Raw.md`

## Output Format

**Manual invocation**: Display full digest with all sections.

**From /start-my-day**: Return condensed list:
```
**内容机会 (5):**
- [标题] - [角度]
...
完整摘要: [[YYYY-MM-DD-摘要]]
```

## Error Handling

- One feed down: Continue with other, note in digest
- Both down: Use yesterday's archive with warning
- Empty feeds: Create minimal digest noting "今日无新内容"
