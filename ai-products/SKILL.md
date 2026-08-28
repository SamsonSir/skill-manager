---
name: ai-products
description: 整理 AI 产品发布信息，从 Product Hunt、Hacker News、GitHub 和 Techmeme 多源聚合。当用户调用 /ai-products 或 /start-my-day 需要产品发布信息时触发。智能过滤 AI 相关产品（AI、ML、LLM、GPT、Claude、automation、agent、model 等关键词），去重并按相关性、参与度（votes/points/stars）和内容潜力（教程友好、review-worthy、开源bonus）排序。生成包含精选推荐、LLM 与 AI 模型、开发者工具、生产力与自动化、开源亮点的每日摘要。主动识别有内容创作价值的产品机会（教程机会、抢先报道、深度分析、工具评测、竞品对比）。
---
# AI Product Discovery

Fetch, deduplicate, and rank AI product launches from multiple sources.

## Sources

| Source | URL | Notes |
|--------|-----|-------|
| Product Hunt | `https://www.producthunt.com/feed` | Filter for AI-related |
| Hacker News | `https://hn.algolia.com/api/v1/search?tags=show_hn&numericFilters=created_at_i>TIMESTAMP` | Show HN posts, 24h window |
| GitHub Trending | `https://mshibanami.github.io/GitHubTrendingRSS/daily/python.xml` | Python repos |
| Techmeme | `https://techmeme.com/river` | Product announcements |

## Workflow

1. **Check cache**: Look for `50_资源/产品发布/YYYY-MM/YYYY-MM-DD-摘要.md`. If exists with today's date, return cached.

2. **Fetch sources**: Use WebFetch on each. Extract product name, URL, description, and engagement metrics (votes/points/stars).

3. **Filter**: Keep only AI-related products (keywords: AI, ML, LLM, GPT, Claude, automation, agent, model).

4. **Deduplicate**: Same product across sources = merge. Keep best description, combine metrics, track all sources.

5. **Rank by**:
   - AI relevance
   - Engagement (normalize: PH votes/500, HN points/100, GH stars/1000)
   - Content potential (tutorial-friendly, review-worthy, open source bonus)
   - Recency and novelty

6. **Generate digest**: See [TEMPLATE.md](TEMPLATE.md). Sections:
   - 精选推荐 (3-5) with content angles
   - LLM与AI模型
   - 开发者工具
   - 生产力与自动化
   - 开源亮点

7. **Save files**:
   - `50_资源/产品发布/YYYY-MM/YYYY-MM-DD-摘要.md`
   - `50_资源/产品发布/YYYY-MM/原始数据/YYYY-MM-DD_ProductHunt-Raw.md`
   - `50_资源/产品发布/YYYY-MM/原始数据/YYYY-MM-DD_HackerNews-Raw.md`
   - `50_资源/产品发布/YYYY-MM/原始数据/YYYY-MM-DD_GitHub-Raw.md`

## Output Format

**Manual invocation**: Full digest with all sections.

**From /start-my-day**: Condensed list:
```
**产品发布机会 (5):**
- [产品名] - [内容角度] - [关键指标]
...
完整摘要: [[YYYY-MM-DD-摘要]]
```

## Error Handling

- Source down: Continue with others, note in digest
- <2 sources available: Fall back to yesterday's archive
- Empty results: Create minimal digest noting "今日无新AI产品"

## Content Angle Logic

- High engagement + tutorial-friendly: "教程机会"
- Novel + early stage: "抢先报道优势"
- Open source + complex: "深度分析"
- SaaS + practical: "工具评测"
- Similar to existing: "对比 vs [竞品]"
