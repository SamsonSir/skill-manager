window.SKILL_MANAGER_REPORT = {
  "generatedAt": "2026-06-06T15:03:00.393Z",
  "roots": [
    {
      "label": "agents",
      "family": "agents",
      "scope": "global",
      "path": "/Users/joker/.agents/skills",
      "total": 161,
      "symlinks": 141
    },
    {
      "label": "claude",
      "family": "claude",
      "scope": "global",
      "path": "/Users/joker/.claude/skills",
      "total": 161,
      "symlinks": 155
    },
    {
      "label": "codex",
      "family": "codex",
      "scope": "global",
      "path": "/Users/joker/.codex/skills",
      "total": 3,
      "symlinks": 3
    },
    {
      "label": "vault-agents",
      "family": "agents",
      "scope": "JokerSu-knowledge",
      "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills",
      "total": 62,
      "symlinks": 62
    }
  ],
  "summary": {
    "totalFiles": 387,
    "uniqueNames": 161,
    "duplicateNames": 161,
    "linkedNames": 161,
    "physicalDuplicateNames": 0,
    "identicalNames": 0,
    "conflictNames": 0,
    "uniqueOnlyNames": 0
  },
  "health": {
    "status": "healthy",
    "checks": [
      {
        "id": "sync",
        "label": "Codex / Claude 同步",
        "ok": true
      },
      {
        "id": "conflicts",
        "label": "同名冲突",
        "ok": true
      },
      {
        "id": "physical-duplicates",
        "label": "实体重复",
        "ok": true
      },
      {
        "id": "broken-symlinks",
        "label": "坏软链接",
        "ok": true
      },
      {
        "id": "watcher",
        "label": "自动同步 watcher",
        "ok": true
      }
    ],
    "actionItems": [],
    "actionCount": 0,
    "brokenSymlinks": [],
    "watcher": {
      "label": "com.jokersu.skill-manager.sync",
      "plistPath": "/Users/joker/Library/LaunchAgents/com.jokersu.skill-manager.sync.plist",
      "installed": true,
      "loaded": true,
      "watching": true,
      "state": "not running",
      "runs": 6,
      "lastExitCode": 0,
      "lastLogLine": "[2026-06-06T15:02:44.562Z] watch-sync complete",
      "logPath": "/Users/joker/agent-skills/logs/watch-sync.log"
    },
    "codexClaudeSync": {
      "leftNames": 161,
      "rightNames": 161,
      "commonNames": 161,
      "leftOnly": [],
      "rightOnly": [],
      "mismatched": []
    }
  },
  "groups": [
    {
      "name": "1688-selection-assistant",
      "status": "linked",
      "hashes": [
        "dc94f92540db1e0b5203790206b2f4c95ea90dfb5c2f35b7a5d4e9bf3a38847d"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/1688-selection-assistant"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/1688-selection-assistant/SKILL.md",
          "relativePath": "1688-selection-assistant/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/1688-selection-assistant",
          "hash": "dc94f92540db1e0b5203790206b2f4c95ea90dfb5c2f35b7a5d4e9bf3a38847d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6084,
          "isSymlink": true,
          "description": "1688选品助手 - 在1688搜索货源、采集价格、销量和店铺评分等数据，结果保存到本地。支持按销量/价格排序，可设置价格范围过滤。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/1688-selection-assistant/SKILL.md",
          "relativePath": "1688-selection-assistant/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/1688-selection-assistant",
          "hash": "dc94f92540db1e0b5203790206b2f4c95ea90dfb5c2f35b7a5d4e9bf3a38847d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6084,
          "isSymlink": true,
          "description": "1688选品助手 - 在1688搜索货源、采集价格、销量和店铺评分等数据，结果保存到本地。支持按销量/价格排序，可设置价格范围过滤。"
        }
      ]
    },
    {
      "name": "Agent Browser",
      "status": "linked",
      "hashes": [
        "04afeeb53a8b6ab953974311ec7ed60e0d66c532341ca21933625320f28b01c6"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/agent-browser"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/agent-browser/SKILL.md",
          "relativePath": "agent-browser/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/agent-browser",
          "hash": "04afeeb53a8b6ab953974311ec7ed60e0d66c532341ca21933625320f28b01c6",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 10224,
          "isSymlink": true,
          "description": "A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/agent-browser/SKILL.md",
          "relativePath": "agent-browser/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/agent-browser",
          "hash": "04afeeb53a8b6ab953974311ec7ed60e0d66c532341ca21933625320f28b01c6",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 10224,
          "isSymlink": true,
          "description": "A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands."
        }
      ]
    },
    {
      "name": "agent-reach",
      "status": "linked",
      "hashes": [
        "3a0beca2c0ec226026e5c1fd4757f29825b5109b6d15c773ad455e669e2f1693"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/agent-reach"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/agent-reach/SKILL.md",
          "relativePath": "agent-reach/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/agent-reach",
          "hash": "3a0beca2c0ec226026e5c1fd4757f29825b5109b6d15c773ad455e669e2f1693",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5496,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/agent-reach/SKILL.md",
          "relativePath": "agent-reach/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/agent-reach",
          "hash": "3a0beca2c0ec226026e5c1fd4757f29825b5109b6d15c773ad455e669e2f1693",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5496,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "ai-newsletters",
      "status": "linked",
      "hashes": [
        "851d608de93699fe09c2183864ffbd1c2153ea9670667d460b6c144a10e90989"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/ai-newsletters"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/ai-newsletters/SKILL.md",
          "relativePath": "ai-newsletters/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ai-newsletters",
          "hash": "851d608de93699fe09c2183864ffbd1c2153ea9670667d460b6c144a10e90989",
          "modifiedAt": "2026-04-19T09:04:01.000Z",
          "bytes": 3240,
          "isSymlink": true,
          "description": "整理 AI 简报内容，智能去重和排序。当用户调用 /ai-newsletters、/日报、/news 或 /start-my-day 需要简报内容时触发。从 TLDR AI、The Rundown AI 和 ai-news-radar 聚合数据（TopHub、Buzzing、NewsNow、AIbase等10+中英文信息源），生成包含精选推荐、AI 动态、生产力工具、WaytoAGI 精选的每日摘要。智能去重、按相关性和新鲜度排序，为高价值内容提供创作角度。主动识别用户对 AI 资讯的需求并提供高质量内容聚合。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/ai-newsletters/SKILL.md",
          "relativePath": "ai-newsletters/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ai-newsletters",
          "hash": "851d608de93699fe09c2183864ffbd1c2153ea9670667d460b6c144a10e90989",
          "modifiedAt": "2026-04-19T09:04:01.000Z",
          "bytes": 3240,
          "isSymlink": true,
          "description": "整理 AI 简报内容，智能去重和排序。当用户调用 /ai-newsletters、/日报、/news 或 /start-my-day 需要简报内容时触发。从 TLDR AI、The Rundown AI 和 ai-news-radar 聚合数据（TopHub、Buzzing、NewsNow、AIbase等10+中英文信息源），生成包含精选推荐、AI 动态、生产力工具、WaytoAGI 精选的每日摘要。智能去重、按相关性和新鲜度排序，为高价值内容提供创作角度。主动识别用户对 AI 资讯的需求并提供高质量内容聚合。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/ai-newsletters/SKILL.md",
          "relativePath": "ai-newsletters/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ai-newsletters",
          "hash": "851d608de93699fe09c2183864ffbd1c2153ea9670667d460b6c144a10e90989",
          "modifiedAt": "2026-04-19T09:04:01.000Z",
          "bytes": 3240,
          "isSymlink": true,
          "description": "整理 AI 简报内容，智能去重和排序。当用户调用 /ai-newsletters、/日报、/news 或 /start-my-day 需要简报内容时触发。从 TLDR AI、The Rundown AI 和 ai-news-radar 聚合数据（TopHub、Buzzing、NewsNow、AIbase等10+中英文信息源），生成包含精选推荐、AI 动态、生产力工具、WaytoAGI 精选的每日摘要。智能去重、按相关性和新鲜度排序，为高价值内容提供创作角度。主动识别用户对 AI 资讯的需求并提供高质量内容聚合。"
        }
      ]
    },
    {
      "name": "ai-products",
      "status": "linked",
      "hashes": [
        "9b44d4720fe7dc91847f1df6d507d4424a370dceee9080a6d3a38482a8fd1114"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/ai-products"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/ai-products/SKILL.md",
          "relativePath": "ai-products/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ai-products",
          "hash": "9b44d4720fe7dc91847f1df6d507d4424a370dceee9080a6d3a38482a8fd1114",
          "modifiedAt": "2026-04-19T09:04:14.000Z",
          "bytes": 3149,
          "isSymlink": true,
          "description": "整理 AI 产品发布信息，从 Product Hunt、Hacker News、GitHub 和 Techmeme 多源聚合。当用户调用 /ai-products 或 /start-my-day 需要产品发布信息时触发。智能过滤 AI 相关产品（AI、ML、LLM、GPT、Claude、automation、agent、model 等关键词），去重并按相关性、参与度（votes/points/stars）和内容潜力（教程友好、review-worthy、开源bonus）排序。生成包含精选推荐、LLM 与 AI 模型、开发者工具、生产力与自动化、开源亮点的每日摘要。主动识别有内容创作价值的产品机会（教程机会、抢先报道、深度分析、工具评测、竞品对比）。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/ai-products/SKILL.md",
          "relativePath": "ai-products/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ai-products",
          "hash": "9b44d4720fe7dc91847f1df6d507d4424a370dceee9080a6d3a38482a8fd1114",
          "modifiedAt": "2026-04-19T09:04:14.000Z",
          "bytes": 3149,
          "isSymlink": true,
          "description": "整理 AI 产品发布信息，从 Product Hunt、Hacker News、GitHub 和 Techmeme 多源聚合。当用户调用 /ai-products 或 /start-my-day 需要产品发布信息时触发。智能过滤 AI 相关产品（AI、ML、LLM、GPT、Claude、automation、agent、model 等关键词），去重并按相关性、参与度（votes/points/stars）和内容潜力（教程友好、review-worthy、开源bonus）排序。生成包含精选推荐、LLM 与 AI 模型、开发者工具、生产力与自动化、开源亮点的每日摘要。主动识别有内容创作价值的产品机会（教程机会、抢先报道、深度分析、工具评测、竞品对比）。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/ai-products/SKILL.md",
          "relativePath": "ai-products/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ai-products",
          "hash": "9b44d4720fe7dc91847f1df6d507d4424a370dceee9080a6d3a38482a8fd1114",
          "modifiedAt": "2026-04-19T09:04:14.000Z",
          "bytes": 3149,
          "isSymlink": true,
          "description": "整理 AI 产品发布信息，从 Product Hunt、Hacker News、GitHub 和 Techmeme 多源聚合。当用户调用 /ai-products 或 /start-my-day 需要产品发布信息时触发。智能过滤 AI 相关产品（AI、ML、LLM、GPT、Claude、automation、agent、model 等关键词），去重并按相关性、参与度（votes/points/stars）和内容潜力（教程友好、review-worthy、开源bonus）排序。生成包含精选推荐、LLM 与 AI 模型、开发者工具、生产力与自动化、开源亮点的每日摘要。主动识别有内容创作价值的产品机会（教程机会、抢先报道、深度分析、工具评测、竞品对比）。"
        }
      ]
    },
    {
      "name": "aihot",
      "status": "linked",
      "hashes": [
        "50859a57f643f855a184a492330528ae196987dcd37ee5171757c0032880c77a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/aihot"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/aihot/SKILL.md",
          "relativePath": "aihot/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/aihot",
          "hash": "50859a57f643f855a184a492330528ae196987dcd37ee5171757c0032880c77a",
          "modifiedAt": "2026-05-08T10:54:39.179Z",
          "bytes": 21979,
          "isSymlink": true,
          "description": "AI HOT (aihot.virxact.com) 中文 AI 资讯查询 Skill。当用户想知道\"今天 AI 圈有什么\"、\"AI 日报\"、\"AI HOT\"、\"AI 资讯\"、\"AI 热点\"、\"最近 AI\"、\"OpenAI/Anthropic/Google 最近发布了什么\"、\"AI hot today\"、\"AI news today\"、\"看一下 AI 行业动态\"、\"今天有什么大模型发布\"、\"昨天 AI 圈\"、\"看下精选条目\"、\"AI HOT 精选\"、\"最近一周的 AI 论文\"、\"AI 模型发布\"、\"AI 产品发布\"、\"AI 行业动态\"、\"AI 技巧与观点\" 等任何中文 AI 资讯查询时使用。即使用户只说\"AI 圈\"、\"AI 新闻\"、\"AI 日报\"，或者只是问\"今天发生了什么\"且上下文是 AI / 大模型 / LLM / 创业领域，也应该触发本 Skill。Skill 会直接 curl 公开 REST API 拉数据并整理成中文 markdown 简报，不需要用户配置任何 API Key 或 MCP server。**不要 undertrigger**——用户问 AI 资讯而你不调本 Skill 就是把过时的训练数据当作今日新闻，对用户有害。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/aihot/SKILL.md",
          "relativePath": "aihot/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/aihot",
          "hash": "50859a57f643f855a184a492330528ae196987dcd37ee5171757c0032880c77a",
          "modifiedAt": "2026-05-08T10:54:39.179Z",
          "bytes": 21979,
          "isSymlink": true,
          "description": "AI HOT (aihot.virxact.com) 中文 AI 资讯查询 Skill。当用户想知道\"今天 AI 圈有什么\"、\"AI 日报\"、\"AI HOT\"、\"AI 资讯\"、\"AI 热点\"、\"最近 AI\"、\"OpenAI/Anthropic/Google 最近发布了什么\"、\"AI hot today\"、\"AI news today\"、\"看一下 AI 行业动态\"、\"今天有什么大模型发布\"、\"昨天 AI 圈\"、\"看下精选条目\"、\"AI HOT 精选\"、\"最近一周的 AI 论文\"、\"AI 模型发布\"、\"AI 产品发布\"、\"AI 行业动态\"、\"AI 技巧与观点\" 等任何中文 AI 资讯查询时使用。即使用户只说\"AI 圈\"、\"AI 新闻\"、\"AI 日报\"，或者只是问\"今天发生了什么\"且上下文是 AI / 大模型 / LLM / 创业领域，也应该触发本 Skill。Skill 会直接 curl 公开 REST API 拉数据并整理成中文 markdown 简报，不需要用户配置任何 API Key 或 MCP server。**不要 undertrigger**——用户问 AI 资讯而你不调本 Skill 就是把过时的训练数据当作今日新闻，对用户有害。"
        }
      ]
    },
    {
      "name": "ak-rss-24h-brief",
      "status": "linked",
      "hashes": [
        "54b8784d66ef4eed5a339bba6d2d7fec757f1e206b48bb43e7c5f385ffebecbf"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/ak-rss-24h-brief"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/ak-rss-24h-brief/SKILL.md",
          "relativePath": "ak-rss-24h-brief/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ak-rss-24h-brief",
          "hash": "54b8784d66ef4eed5a339bba6d2d7fec757f1e206b48bb43e7c5f385ffebecbf",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2429,
          "isSymlink": true,
          "description": "Read RSS/Atom feeds from an OPML list, fetch articles from the last N hours, and generate a Chinese categorized brief. Use for requests like “generate a 24-hour brief from this RSS list” or “summarize recent posts from an OPML feed bundle”. Output must keep original titles + links, group by category, and avoid fabricated facts. The RSS subscription list is shared by Andrej Karpathy (source post: https://x.com/karpathy/status/2018043254986703167)."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/ak-rss-24h-brief/SKILL.md",
          "relativePath": "ak-rss-24h-brief/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ak-rss-24h-brief",
          "hash": "54b8784d66ef4eed5a339bba6d2d7fec757f1e206b48bb43e7c5f385ffebecbf",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2429,
          "isSymlink": true,
          "description": "Read RSS/Atom feeds from an OPML list, fetch articles from the last N hours, and generate a Chinese categorized brief. Use for requests like “generate a 24-hour brief from this RSS list” or “summarize recent posts from an OPML feed bundle”. Output must keep original titles + links, group by category, and avoid fabricated facts. The RSS subscription list is shared by Andrej Karpathy (source post: https://x.com/karpathy/status/2018043254986703167)."
        }
      ]
    },
    {
      "name": "anthropic-frontend-design",
      "status": "linked",
      "hashes": [
        "9d9f68b1cf0a125ad98b22db780702120e003fefeed9497a288dd9d3babdf2b4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/anthropic-frontend-design"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/anthropic-frontend-design/SKILL.md",
          "relativePath": "anthropic-frontend-design/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/anthropic-frontend-design",
          "hash": "9d9f68b1cf0a125ad98b22db780702120e003fefeed9497a288dd9d3babdf2b4",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4539,
          "isSymlink": true,
          "description": "Create distinctive, production-grade frontend interfaces that avoid generic \"AI slop\" aesthetics. Combines the design intelligence of UI/UX Pro Max with Anthropic's anti-slop philosophy. Use for building UI components, pages, applications, or interfaces with exceptional attention to detail and bold creative choices."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/anthropic-frontend-design/SKILL.md",
          "relativePath": "anthropic-frontend-design/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/anthropic-frontend-design",
          "hash": "9d9f68b1cf0a125ad98b22db780702120e003fefeed9497a288dd9d3babdf2b4",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4539,
          "isSymlink": true,
          "description": "Create distinctive, production-grade frontend interfaces that avoid generic \"AI slop\" aesthetics. Combines the design intelligence of UI/UX Pro Max with Anthropic's anti-slop philosophy. Use for building UI components, pages, applications, or interfaces with exceptional attention to detail and bold creative choices."
        }
      ]
    },
    {
      "name": "archive",
      "status": "linked",
      "hashes": [
        "1b45fdd9cb5704cc85860be89539a60b4beebf399ea38c960fb8334c8574fd25"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/archive"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/archive/SKILL.md",
          "relativePath": "archive/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/archive",
          "hash": "1b45fdd9cb5704cc85860be89539a60b4beebf399ea38c960fb8334c8574fd25",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 5224,
          "isSymlink": true,
          "description": "Archive completed projects and processed inbox items"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/archive/SKILL.md",
          "relativePath": "archive/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/archive",
          "hash": "1b45fdd9cb5704cc85860be89539a60b4beebf399ea38c960fb8334c8574fd25",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 5224,
          "isSymlink": true,
          "description": "Archive completed projects and processed inbox items"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/archive/SKILL.md",
          "relativePath": "archive/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/archive",
          "hash": "1b45fdd9cb5704cc85860be89539a60b4beebf399ea38c960fb8334c8574fd25",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 5224,
          "isSymlink": true,
          "description": "Archive completed projects and processed inbox items"
        }
      ]
    },
    {
      "name": "ask",
      "status": "linked",
      "hashes": [
        "42323007e2bf4f32caf7cc42b39a1776f9cb3db254c18c0adee0f61c8573a648"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/ask"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/ask/SKILL.md",
          "relativePath": "ask/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ask",
          "hash": "42323007e2bf4f32caf7cc42b39a1776f9cb3db254c18c0adee0f61c8573a648",
          "modifiedAt": "2026-04-19T09:03:48.000Z",
          "bytes": 1706,
          "isSymlink": true,
          "description": "快速回答问题，不进行深入的笔记整理。当用户问简单事实性问题、需要快速解释、询问\"How to\"、\"What is\"类问题、\"XXX是什么\"、\"怎么做XXX\"、\"解释一下XXX\"、\"XXX的用法\"或直接调用 /ask 时触发。适用于不需要创建持久化知识条目的场景，如快速查询、简单解释、事实核实。如果问题涉及深入研究、需要创建笔记或系统化学习，应改用 /research 或 /parse-knowledge。主动识别适合快速回答的问题并给出简洁准确的答案。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/ask/SKILL.md",
          "relativePath": "ask/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ask",
          "hash": "42323007e2bf4f32caf7cc42b39a1776f9cb3db254c18c0adee0f61c8573a648",
          "modifiedAt": "2026-04-19T09:03:48.000Z",
          "bytes": 1706,
          "isSymlink": true,
          "description": "快速回答问题，不进行深入的笔记整理。当用户问简单事实性问题、需要快速解释、询问\"How to\"、\"What is\"类问题、\"XXX是什么\"、\"怎么做XXX\"、\"解释一下XXX\"、\"XXX的用法\"或直接调用 /ask 时触发。适用于不需要创建持久化知识条目的场景，如快速查询、简单解释、事实核实。如果问题涉及深入研究、需要创建笔记或系统化学习，应改用 /research 或 /parse-knowledge。主动识别适合快速回答的问题并给出简洁准确的答案。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/ask/SKILL.md",
          "relativePath": "ask/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ask",
          "hash": "42323007e2bf4f32caf7cc42b39a1776f9cb3db254c18c0adee0f61c8573a648",
          "modifiedAt": "2026-04-19T09:03:48.000Z",
          "bytes": 1706,
          "isSymlink": true,
          "description": "快速回答问题，不进行深入的笔记整理。当用户问简单事实性问题、需要快速解释、询问\"How to\"、\"What is\"类问题、\"XXX是什么\"、\"怎么做XXX\"、\"解释一下XXX\"、\"XXX的用法\"或直接调用 /ask 时触发。适用于不需要创建持久化知识条目的场景，如快速查询、简单解释、事实核实。如果问题涉及深入研究、需要创建笔记或系统化学习，应改用 /research 或 /parse-knowledge。主动识别适合快速回答的问题并给出简洁准确的答案。"
        }
      ]
    },
    {
      "name": "auto-updater",
      "status": "linked",
      "hashes": [
        "4142916e146caa90d41cd274bdea6263da1738d8ecc81777b7fc19c6bd8ef9f4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/auto-updater"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/auto-updater/SKILL.md",
          "relativePath": "auto-updater/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/auto-updater",
          "hash": "4142916e146caa90d41cd274bdea6263da1738d8ecc81777b7fc19c6bd8ef9f4",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3300,
          "isSymlink": true,
          "description": "Automatically update Clawdbot and all installed skills once daily. Runs via cron, checks for updates, applies them, and messages the user with a summary of what changed."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/auto-updater/SKILL.md",
          "relativePath": "auto-updater/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/auto-updater",
          "hash": "4142916e146caa90d41cd274bdea6263da1738d8ecc81777b7fc19c6bd8ef9f4",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3300,
          "isSymlink": true,
          "description": "Automatically update Clawdbot and all installed skills once daily. Runs via cron, checks for updates, applies them, and messages the user with a summary of what changed."
        }
      ]
    },
    {
      "name": "automation-workflows",
      "status": "linked",
      "hashes": [
        "7e2a1b38c6f3558f8f373e45eee3e70d7c2d531cbe922d36a9c24a507d8ccb43"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/automation-workflows"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/automation-workflows/SKILL.md",
          "relativePath": "automation-workflows/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/automation-workflows",
          "hash": "7e2a1b38c6f3558f8f373e45eee3e70d7c2d531cbe922d36a9c24a507d8ccb43",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 10358,
          "isSymlink": true,
          "description": "Design and implement automation workflows to save time and scale operations as a solopreneur. Use when identifying repetitive tasks to automate, building workflows across tools, setting up triggers and actions, or optimizing existing automations. Covers automation opportunity identification, workflow design, tool selection (Zapier, Make, n8n), testing, and maintenance. Trigger on \"automate\", \"automation\", \"workflow automation\", \"save time\", \"reduce manual work\", \"automate my business\", \"no-code automation\"."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/automation-workflows/SKILL.md",
          "relativePath": "automation-workflows/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/automation-workflows",
          "hash": "7e2a1b38c6f3558f8f373e45eee3e70d7c2d531cbe922d36a9c24a507d8ccb43",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 10358,
          "isSymlink": true,
          "description": "Design and implement automation workflows to save time and scale operations as a solopreneur. Use when identifying repetitive tasks to automate, building workflows across tools, setting up triggers and actions, or optimizing existing automations. Covers automation opportunity identification, workflow design, tool selection (Zapier, Make, n8n), testing, and maintenance. Trigger on \"automate\", \"automation\", \"workflow automation\", \"save time\", \"reduce manual work\", \"automate my business\", \"no-code automation\"."
        }
      ]
    },
    {
      "name": "baidu-search",
      "status": "linked",
      "hashes": [
        "4fa6b504a90d14bccaa171656a203a3d1ee0a2f2be4bdb76c95819a9de03fe98"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/baidu-search"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/baidu-search/SKILL.md",
          "relativePath": "baidu-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/baidu-search",
          "hash": "4fa6b504a90d14bccaa171656a203a3d1ee0a2f2be4bdb76c95819a9de03fe98",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1794,
          "isSymlink": true,
          "description": "Search the web using Baidu AI Search Engine (BDSE). Use for live information, documentation, or research topics."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/baidu-search/SKILL.md",
          "relativePath": "baidu-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/baidu-search",
          "hash": "4fa6b504a90d14bccaa171656a203a3d1ee0a2f2be4bdb76c95819a9de03fe98",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1794,
          "isSymlink": true,
          "description": "Search the web using Baidu AI Search Engine (BDSE). Use for live information, documentation, or research topics."
        }
      ]
    },
    {
      "name": "baoyu-youtube-transcript",
      "status": "linked",
      "hashes": [
        "b7085574c6bf72e07c578db14316682b9ebf1e841d9db62916d284efd84c96cc"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/baoyu-youtube-transcript"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/baoyu-youtube-transcript/SKILL.md",
          "relativePath": "baoyu-youtube-transcript/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/baoyu-youtube-transcript",
          "hash": "b7085574c6bf72e07c578db14316682b9ebf1e841d9db62916d284efd84c96cc",
          "modifiedAt": "2026-04-05T05:42:35.000Z",
          "bytes": 9704,
          "isSymlink": true,
          "description": "Downloads YouTube video transcripts/subtitles and cover images by URL or video ID. Supports multiple languages, translation, chapters, and speaker identification. Caches raw data for fast re-formatting. Use when user asks to \"get YouTube transcript\", \"download subtitles\", \"get captions\", \"YouTube字幕\", \"YouTube封面\", \"视频封面\", \"video thumbnail\", \"video cover image\", or provides a YouTube URL and wants the transcript/subtitle text or cover image extracted."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/baoyu-youtube-transcript/SKILL.md",
          "relativePath": "baoyu-youtube-transcript/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/baoyu-youtube-transcript",
          "hash": "b7085574c6bf72e07c578db14316682b9ebf1e841d9db62916d284efd84c96cc",
          "modifiedAt": "2026-04-05T05:42:35.000Z",
          "bytes": 9704,
          "isSymlink": true,
          "description": "Downloads YouTube video transcripts/subtitles and cover images by URL or video ID. Supports multiple languages, translation, chapters, and speaker identification. Caches raw data for fast re-formatting. Use when user asks to \"get YouTube transcript\", \"download subtitles\", \"get captions\", \"YouTube字幕\", \"YouTube封面\", \"视频封面\", \"video thumbnail\", \"video cover image\", or provides a YouTube URL and wants the transcript/subtitle text or cover image extracted."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/baoyu-youtube-transcript/SKILL.md",
          "relativePath": "baoyu-youtube-transcript/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/baoyu-youtube-transcript",
          "hash": "b7085574c6bf72e07c578db14316682b9ebf1e841d9db62916d284efd84c96cc",
          "modifiedAt": "2026-04-05T05:42:35.000Z",
          "bytes": 9704,
          "isSymlink": true,
          "description": "Downloads YouTube video transcripts/subtitles and cover images by URL or video ID. Supports multiple languages, translation, chapters, and speaker identification. Caches raw data for fast re-formatting. Use when user asks to \"get YouTube transcript\", \"download subtitles\", \"get captions\", \"YouTube字幕\", \"YouTube封面\", \"视频封面\", \"video thumbnail\", \"video cover image\", or provides a YouTube URL and wants the transcript/subtitle text or cover image extracted."
        }
      ]
    },
    {
      "name": "bilibili-data",
      "status": "linked",
      "hashes": [
        "e46cd0504edf4ff33453f5bad4c658d046492ebdcc1488af7884ebe0243d22a2"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/bilibili-data-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/bilibili-data-cy/SKILL.md",
          "relativePath": "bilibili-data-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/bilibili-data-cy",
          "hash": "e46cd0504edf4ff33453f5bad4c658d046492ebdcc1488af7884ebe0243d22a2",
          "modifiedAt": "2026-04-05T05:32:51.000Z",
          "bytes": 3525,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/bilibili-data-cy/SKILL.md",
          "relativePath": "bilibili-data-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/bilibili-data-cy",
          "hash": "e46cd0504edf4ff33453f5bad4c658d046492ebdcc1488af7884ebe0243d22a2",
          "modifiedAt": "2026-04-05T05:32:51.000Z",
          "bytes": 3525,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/bilibili-data-cy/SKILL.md",
          "relativePath": "bilibili-data-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/bilibili-data-cy",
          "hash": "e46cd0504edf4ff33453f5bad4c658d046492ebdcc1488af7884ebe0243d22a2",
          "modifiedAt": "2026-04-05T05:32:51.000Z",
          "bytes": 3525,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "book2skill",
      "status": "linked",
      "hashes": [
        "02a8eeb41277b3590d50a859a89edbee46855be4d47997cf775c35cc00fb13bd"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/cangjie-skill"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/cangjie-skill/SKILL.md",
          "relativePath": "cangjie-skill/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/cangjie-skill",
          "hash": "02a8eeb41277b3590d50a859a89edbee46855be4d47997cf775c35cc00fb13bd",
          "modifiedAt": "2026-04-20T08:05:56.189Z",
          "bytes": 6555,
          "isSymlink": true,
          "description": "Distill a book into a coherent set of executable skills. Use when the user asks to \"拆书\" / \"蒸馏一本书\" / \"把 XX 书做成 skill\" / \"turn a book into skills\" — i.e. wants a book's frameworks, principles, and methodologies extracted into atomic, reusable Claude skills that an agent can invoke in real-world situations. NOT for simple summarization, book reviews, or role-playing as the author (that is nuwa-skill's job)."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/cangjie-skill/SKILL.md",
          "relativePath": "cangjie-skill/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/cangjie-skill",
          "hash": "02a8eeb41277b3590d50a859a89edbee46855be4d47997cf775c35cc00fb13bd",
          "modifiedAt": "2026-04-20T08:05:56.189Z",
          "bytes": 6555,
          "isSymlink": true,
          "description": "Distill a book into a coherent set of executable skills. Use when the user asks to \"拆书\" / \"蒸馏一本书\" / \"把 XX 书做成 skill\" / \"turn a book into skills\" — i.e. wants a book's frameworks, principles, and methodologies extracted into atomic, reusable Claude skills that an agent can invoke in real-world situations. NOT for simple summarization, book reviews, or role-playing as the author (that is nuwa-skill's job)."
        }
      ]
    },
    {
      "name": "brain",
      "status": "linked",
      "hashes": [
        "1278142ef1c724d8373fe7d111acf93ebfaa4f8388de76d4291116db2e72c6ac"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/2nd-brain"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/2nd-brain/SKILL.md",
          "relativePath": "2nd-brain/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/2nd-brain",
          "hash": "1278142ef1c724d8373fe7d111acf93ebfaa4f8388de76d4291116db2e72c6ac",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 11353,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/2nd-brain/SKILL.md",
          "relativePath": "2nd-brain/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/2nd-brain",
          "hash": "1278142ef1c724d8373fe7d111acf93ebfaa4f8388de76d4291116db2e72c6ac",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 11353,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "brainstorm",
      "status": "linked",
      "hashes": [
        "1f59f9f80356999cf063618e7f93159e8cb50c685b8af5f713d937bb95c127f1"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/brainstorm"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/brainstorm/SKILL.md",
          "relativePath": "brainstorm/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/brainstorm",
          "hash": "1f59f9f80356999cf063618e7f93159e8cb50c685b8af5f713d937bb95c127f1",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 6908,
          "isSymlink": true,
          "description": "Interactive brainstorming session, then optionally create a Project or capture knowledge"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/brainstorm/SKILL.md",
          "relativePath": "brainstorm/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/brainstorm",
          "hash": "1f59f9f80356999cf063618e7f93159e8cb50c685b8af5f713d937bb95c127f1",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 6908,
          "isSymlink": true,
          "description": "Interactive brainstorming session, then optionally create a Project or capture knowledge"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/brainstorm/SKILL.md",
          "relativePath": "brainstorm/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/brainstorm",
          "hash": "1f59f9f80356999cf063618e7f93159e8cb50c685b8af5f713d937bb95c127f1",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 6908,
          "isSymlink": true,
          "description": "Interactive brainstorming session, then optionally create a Project or capture knowledge"
        }
      ]
    },
    {
      "name": "brainstorming",
      "status": "linked",
      "hashes": [
        "bba47904a7f6bbee3bf8a107ebbe84e65d392be683bbb898ded736b29e415f90"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/brainstorming"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/brainstorming/SKILL.md",
          "relativePath": "superpowers/brainstorming/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/brainstorming",
          "hash": "bba47904a7f6bbee3bf8a107ebbe84e65d392be683bbb898ded736b29e415f90",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 10634,
          "isSymlink": false,
          "description": "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/brainstorming/SKILL.md",
          "relativePath": "brainstorming/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/brainstorming",
          "hash": "bba47904a7f6bbee3bf8a107ebbe84e65d392be683bbb898ded736b29e415f90",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 10634,
          "isSymlink": true,
          "description": "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/brainstorming/SKILL.md",
          "relativePath": "brainstorming/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/brainstorming",
          "hash": "bba47904a7f6bbee3bf8a107ebbe84e65d392be683bbb898ded736b29e415f90",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 10634,
          "isSymlink": true,
          "description": "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
        }
      ]
    },
    {
      "name": "break-ai-slop",
      "status": "linked",
      "hashes": [
        "04bb129d7482b9545e7aa863ff5a5b7eb59324e4ee2db51ee7963a913b30989c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/break-ai-slop"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/break-ai-slop/SKILL.md",
          "relativePath": "break-ai-slop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/break-ai-slop",
          "hash": "04bb129d7482b9545e7aa863ff5a5b7eb59324e4ee2db51ee7963a913b30989c",
          "modifiedAt": "2026-04-26T14:58:44.000Z",
          "bytes": 4005,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/break-ai-slop/SKILL.md",
          "relativePath": "break-ai-slop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/break-ai-slop",
          "hash": "04bb129d7482b9545e7aa863ff5a5b7eb59324e4ee2db51ee7963a913b30989c",
          "modifiedAt": "2026-04-26T14:58:44.000Z",
          "bytes": 4005,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/break-ai-slop/SKILL.md",
          "relativePath": "break-ai-slop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/break-ai-slop",
          "hash": "04bb129d7482b9545e7aa863ff5a5b7eb59324e4ee2db51ee7963a913b30989c",
          "modifiedAt": "2026-04-26T14:58:44.000Z",
          "bytes": 4005,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "bugfix",
      "status": "linked",
      "hashes": [
        "1e955d9d3ae291c1d0759cea09298eb8f8177bb18dc36a4e7f2b08c5f65a6bcb"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/bugfix"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/bugfix/SKILL.md",
          "relativePath": "bugfix/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/bugfix",
          "hash": "1e955d9d3ae291c1d0759cea09298eb8f8177bb18dc36a4e7f2b08c5f65a6bcb",
          "modifiedAt": "2026-06-06T14:56:12.072Z",
          "bytes": 10804,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/bugfix/SKILL.md",
          "relativePath": "bugfix/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/bugfix",
          "hash": "1e955d9d3ae291c1d0759cea09298eb8f8177bb18dc36a4e7f2b08c5f65a6bcb",
          "modifiedAt": "2026-06-06T14:56:12.072Z",
          "bytes": 10804,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/bugfix/SKILL.md",
          "relativePath": "bugfix/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/bugfix",
          "hash": "1e955d9d3ae291c1d0759cea09298eb8f8177bb18dc36a4e7f2b08c5f65a6bcb",
          "modifiedAt": "2026-06-06T14:56:12.072Z",
          "bytes": 10804,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "camofox-browser",
      "status": "linked",
      "hashes": [
        "d8e54b0bdb806ebca21d9a6a4342a7cee40840bccb52e0ac7a095d9f6217ff12"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/camofox-browser"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/camofox-browser/SKILL.md",
          "relativePath": "camofox-browser/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/camofox-browser",
          "hash": "d8e54b0bdb806ebca21d9a6a4342a7cee40840bccb52e0ac7a095d9f6217ff12",
          "modifiedAt": "2026-05-01T07:36:34.662Z",
          "bytes": 18096,
          "isSymlink": true,
          "description": "Anti-detection browser automation for AI agents. Use when the user needs stealth web browsing, undetectable scraping, fingerprint spoofing, proxy rotation, or privacy-focused browser automation. Triggers include \"stealth scrape\", \"anti-detection\", \"bypass fingerprinting\", \"camofox\", \"camoufox\", \"undetectable browser\", \"bot evasion\", or any browser task requiring evasion of bot detection systems."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/camofox-browser/SKILL.md",
          "relativePath": "camofox-browser/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/camofox-browser",
          "hash": "d8e54b0bdb806ebca21d9a6a4342a7cee40840bccb52e0ac7a095d9f6217ff12",
          "modifiedAt": "2026-05-01T07:36:34.662Z",
          "bytes": 18096,
          "isSymlink": true,
          "description": "Anti-detection browser automation for AI agents. Use when the user needs stealth web browsing, undetectable scraping, fingerprint spoofing, proxy rotation, or privacy-focused browser automation. Triggers include \"stealth scrape\", \"anti-detection\", \"bypass fingerprinting\", \"camofox\", \"camoufox\", \"undetectable browser\", \"bot evasion\", or any browser task requiring evasion of bot detection systems."
        }
      ]
    },
    {
      "name": "camofox-cli",
      "status": "linked",
      "hashes": [
        "41c67a65f83f5bf6c40e4cc8c310b17bb9b3bd1d2ac703b85f698885bc539b57"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/camofox-cli"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/camofox-cli/SKILL.md",
          "relativePath": "camofox-cli/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/camofox-cli",
          "hash": "41c67a65f83f5bf6c40e4cc8c310b17bb9b3bd1d2ac703b85f698885bc539b57",
          "modifiedAt": "2026-05-01T07:36:34.675Z",
          "bytes": 5129,
          "isSymlink": true,
          "description": "CamoFox CLI — 50 commands for anti-detection browser automation from the terminal. Use when the user needs CLI reference for camofox commands, terminal-based browser control, or a quick lookup of command syntax. Triggers include \"camofox command\", \"CLI reference\", \"terminal browser\", or any request for camofox command-line usage."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/camofox-cli/SKILL.md",
          "relativePath": "camofox-cli/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/camofox-cli",
          "hash": "41c67a65f83f5bf6c40e4cc8c310b17bb9b3bd1d2ac703b85f698885bc539b57",
          "modifiedAt": "2026-05-01T07:36:34.675Z",
          "bytes": 5129,
          "isSymlink": true,
          "description": "CamoFox CLI — 50 commands for anti-detection browser automation from the terminal. Use when the user needs CLI reference for camofox commands, terminal-based browser control, or a quick lookup of command syntax. Triggers include \"camofox command\", \"CLI reference\", \"terminal browser\", or any request for camofox command-line usage."
        }
      ]
    },
    {
      "name": "cc-shield",
      "status": "linked",
      "hashes": [
        "cdcb2da92b53260a8f3147832bcc2cd39dc6758a565c67fd80d3ce7fe3a763f7"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/cc-shield"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/cc-shield/SKILL.md",
          "relativePath": "cc-shield/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/cc-shield",
          "hash": "cdcb2da92b53260a8f3147832bcc2cd39dc6758a565c67fd80d3ce7fe3a763f7",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 6850,
          "isSymlink": true,
          "description": "|-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/cc-shield/SKILL.md",
          "relativePath": "cc-shield/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/cc-shield",
          "hash": "cdcb2da92b53260a8f3147832bcc2cd39dc6758a565c67fd80d3ce7fe3a763f7",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 6850,
          "isSymlink": true,
          "description": "|-"
        }
      ]
    },
    {
      "name": "claude-code-third-party-api",
      "status": "linked",
      "hashes": [
        "4b96faa27ac22ea251a13376089ab60ad07e1d1b828aeb024a1a1fc677e7f560"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/claude-code-third-party-api"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/claude-code-third-party-api/SKILL.md",
          "relativePath": "claude-code-third-party-api/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/claude-code-third-party-api",
          "hash": "4b96faa27ac22ea251a13376089ab60ad07e1d1b828aeb024a1a1fc677e7f560",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3483,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/claude-code-third-party-api/SKILL.md",
          "relativePath": "claude-code-third-party-api/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/claude-code-third-party-api",
          "hash": "4b96faa27ac22ea251a13376089ab60ad07e1d1b828aeb024a1a1fc677e7f560",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3483,
          "isSymlink": true,
          "description": ""
        }
      ]
    },
    {
      "name": "clawflows",
      "status": "linked",
      "hashes": [
        "d027173fd4707a289b4a3fc98d3d368e2691421e6cb7f9eff946b7120c9f51fb"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/clawflows"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/clawflows/SKILL.md",
          "relativePath": "clawflows/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/clawflows",
          "hash": "d027173fd4707a289b4a3fc98d3d368e2691421e6cb7f9eff946b7120c9f51fb",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3611,
          "isSymlink": true,
          "description": "Search, install, and run multi-skill automations from clawflows.com. Combine multiple skills into powerful workflows with logic, conditions, and data flow between steps."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/clawflows/SKILL.md",
          "relativePath": "clawflows/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/clawflows",
          "hash": "d027173fd4707a289b4a3fc98d3d368e2691421e6cb7f9eff946b7120c9f51fb",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3611,
          "isSymlink": true,
          "description": "Search, install, and run multi-skill automations from clawflows.com. Combine multiple skills into powerful workflows with logic, conditions, and data flow between steps."
        }
      ]
    },
    {
      "name": "design-image-studio",
      "status": "linked",
      "hashes": [
        "e5634701cad6737e7857880037cd4cdf95e7c9fef8874269b1cb484b9a33a328"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/design-image-studio"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/design-image-studio/SKILL.md",
          "relativePath": "design-image-studio/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/design-image-studio",
          "hash": "e5634701cad6737e7857880037cd4cdf95e7c9fef8874269b1cb484b9a33a328",
          "modifiedAt": "2026-04-20T07:53:20.130Z",
          "bytes": 6137,
          "isSymlink": true,
          "description": "Directly generate design-oriented AI images with strong creative direction and prompt engineering. Use this skill for posters, product visuals, PPT illustrations, infographics, teaching/demo diagrams, campaign key visuals, cover art, or when the user wants design-quality image generation rather than generic AI art. This skill turns a loose brief into a design brief, assembles a structured prompt, routes to the right Volcengine Seedream settings, and can generate the image immediately."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/design-image-studio/SKILL.md",
          "relativePath": "design-image-studio/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/design-image-studio",
          "hash": "e5634701cad6737e7857880037cd4cdf95e7c9fef8874269b1cb484b9a33a328",
          "modifiedAt": "2026-04-20T07:53:20.130Z",
          "bytes": 6137,
          "isSymlink": true,
          "description": "Directly generate design-oriented AI images with strong creative direction and prompt engineering. Use this skill for posters, product visuals, PPT illustrations, infographics, teaching/demo diagrams, campaign key visuals, cover art, or when the user wants design-quality image generation rather than generic AI art. This skill turns a loose brief into a design brief, assembles a structured prompt, routes to the right Volcengine Seedream settings, and can generate the image immediately."
        }
      ]
    },
    {
      "name": "dispatching-parallel-agents",
      "status": "linked",
      "hashes": [
        "76806091c7f923ba2596546b19cccd98a08e57a68745df77c3a7b998fe838e2b"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/dispatching-parallel-agents"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/dispatching-parallel-agents/SKILL.md",
          "relativePath": "superpowers/dispatching-parallel-agents/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/dispatching-parallel-agents",
          "hash": "76806091c7f923ba2596546b19cccd98a08e57a68745df77c3a7b998fe838e2b",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6441,
          "isSymlink": false,
          "description": "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/dispatching-parallel-agents/SKILL.md",
          "relativePath": "dispatching-parallel-agents/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/dispatching-parallel-agents",
          "hash": "76806091c7f923ba2596546b19cccd98a08e57a68745df77c3a7b998fe838e2b",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6441,
          "isSymlink": true,
          "description": "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/dispatching-parallel-agents/SKILL.md",
          "relativePath": "dispatching-parallel-agents/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/dispatching-parallel-agents",
          "hash": "76806091c7f923ba2596546b19cccd98a08e57a68745df77c3a7b998fe838e2b",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6441,
          "isSymlink": true,
          "description": "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies"
        }
      ]
    },
    {
      "name": "douyin-matrix",
      "status": "linked",
      "hashes": [
        "1007478d7bde3aae360c601b14d2aaf9307d09a69916293fdd442f33ea1f5d66"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/douyin-matrix"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/douyin-matrix/SKILL.md",
          "relativePath": "douyin-matrix/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/douyin-matrix",
          "hash": "1007478d7bde3aae360c601b14d2aaf9307d09a69916293fdd442f33ea1f5d66",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2876,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/douyin-matrix/SKILL.md",
          "relativePath": "douyin-matrix/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/douyin-matrix",
          "hash": "1007478d7bde3aae360c601b14d2aaf9307d09a69916293fdd442f33ea1f5d66",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2876,
          "isSymlink": true,
          "description": ""
        }
      ]
    },
    {
      "name": "douyin-selection-sop",
      "status": "linked",
      "hashes": [
        "5b16c7f9aefc83405bf8642001ed6f836414d438db27b945483432ad4a920283"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/douyin-selection-sop"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/douyin-selection-sop/SKILL.md",
          "relativePath": "douyin-selection-sop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/douyin-selection-sop",
          "hash": "5b16c7f9aefc83405bf8642001ed6f836414d438db27b945483432ad4a920283",
          "modifiedAt": "2026-04-27T14:02:56.000Z",
          "bytes": 12141,
          "isSymlink": true,
          "description": "抖音电商选品全流程SOP。当用户要求执行抖店/抖音电商选品、罗盘短视频榜采集、爆品潜质分析、带货视频提取下载、飞书选品清单写入时触发。覆盖 Phase 1-6：罗盘采集→爆品预筛→素材提取→极简报告→飞书入库→上架准备。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/douyin-selection-sop/SKILL.md",
          "relativePath": "douyin-selection-sop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/douyin-selection-sop",
          "hash": "5b16c7f9aefc83405bf8642001ed6f836414d438db27b945483432ad4a920283",
          "modifiedAt": "2026-04-27T14:02:56.000Z",
          "bytes": 12141,
          "isSymlink": true,
          "description": "抖音电商选品全流程SOP。当用户要求执行抖店/抖音电商选品、罗盘短视频榜采集、爆品潜质分析、带货视频提取下载、飞书选品清单写入时触发。覆盖 Phase 1-6：罗盘采集→爆品预筛→素材提取→极简报告→飞书入库→上架准备。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/douyin-selection-sop/SKILL.md",
          "relativePath": "douyin-selection-sop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/douyin-selection-sop",
          "hash": "5b16c7f9aefc83405bf8642001ed6f836414d438db27b945483432ad4a920283",
          "modifiedAt": "2026-04-27T14:02:56.000Z",
          "bytes": 12141,
          "isSymlink": true,
          "description": "抖音电商选品全流程SOP。当用户要求执行抖店/抖音电商选品、罗盘短视频榜采集、爆品潜质分析、带货视频提取下载、飞书选品清单写入时触发。覆盖 Phase 1-6：罗盘采集→爆品预筛→素材提取→极简报告→飞书入库→上架准备。"
        }
      ]
    },
    {
      "name": "dramaya-workflow",
      "status": "linked",
      "hashes": [
        "9582b5d736c91299e3bca016d6f4a71a72ead9c7b8906be945dc6422a74c1ae3"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/dramaya-workflow"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/dramaya-workflow/SKILL.md",
          "relativePath": "dramaya-workflow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/dramaya-workflow",
          "hash": "9582b5d736c91299e3bca016d6f4a71a72ead9c7b8906be945dc6422a74c1ae3",
          "modifiedAt": "2026-05-21T08:57:27.048Z",
          "bytes": 6430,
          "isSymlink": true,
          "description": "Use when working on Dramaya project coordination, including 今天任务, 开始任务, 收工, 插入需求, Plane work items, GitHub PR flow, cycles, versions, testing, release handoff, or two-person Codex collaboration."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/dramaya-workflow/SKILL.md",
          "relativePath": "dramaya-workflow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/dramaya-workflow",
          "hash": "9582b5d736c91299e3bca016d6f4a71a72ead9c7b8906be945dc6422a74c1ae3",
          "modifiedAt": "2026-05-21T08:57:27.048Z",
          "bytes": 6430,
          "isSymlink": true,
          "description": "Use when working on Dramaya project coordination, including 今天任务, 开始任务, 收工, 插入需求, Plane work items, GitHub PR flow, cycles, versions, testing, release handoff, or two-person Codex collaboration."
        },
        {
          "root": "codex",
          "family": "codex",
          "scope": "global",
          "path": "/Users/joker/.codex/skills/dramaya-workflow/SKILL.md",
          "relativePath": "dramaya-workflow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/dramaya-workflow",
          "hash": "9582b5d736c91299e3bca016d6f4a71a72ead9c7b8906be945dc6422a74c1ae3",
          "modifiedAt": "2026-05-21T08:57:27.048Z",
          "bytes": 6430,
          "isSymlink": true,
          "description": "Use when working on Dramaya project coordination, including 今天任务, 开始任务, 收工, 插入需求, Plane work items, GitHub PR flow, cycles, versions, testing, release handoff, or two-person Codex collaboration."
        }
      ]
    },
    {
      "name": "dream-memory",
      "status": "linked",
      "hashes": [
        "884decbd6a7e118cdbdb944b1a0f6e284c71df2b939daf26d5ee39ebd1dedf3c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/dream-memory"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/dream-memory/SKILL.md",
          "relativePath": "dream-memory/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/dream-memory",
          "hash": "884decbd6a7e118cdbdb944b1a0f6e284c71df2b939daf26d5ee39ebd1dedf3c",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1893,
          "isSymlink": true,
          "description": "Consolidate recent logs, sessions, and existing memory files into durable topic memories, normalize dates, prune stale entries, and keep MEMORY.md short enough for prompt use."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/dream-memory/SKILL.md",
          "relativePath": "dream-memory/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/dream-memory",
          "hash": "884decbd6a7e118cdbdb944b1a0f6e284c71df2b939daf26d5ee39ebd1dedf3c",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1893,
          "isSymlink": true,
          "description": "Consolidate recent logs, sessions, and existing memory files into durable topic memories, normalize dates, prune stale entries, and keep MEMORY.md short enough for prompt use."
        }
      ]
    },
    {
      "name": "e2e-verify",
      "status": "linked",
      "hashes": [
        "73c3d09b0919c3b438ae53782555456df036ba993616ea56bec572dcaef92369"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/e2e-verify"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/e2e-verify/SKILL.md",
          "relativePath": "e2e-verify/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/e2e-verify",
          "hash": "73c3d09b0919c3b438ae53782555456df036ba993616ea56bec572dcaef92369",
          "modifiedAt": "2026-06-06T14:56:12.073Z",
          "bytes": 9085,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/e2e-verify/SKILL.md",
          "relativePath": "e2e-verify/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/e2e-verify",
          "hash": "73c3d09b0919c3b438ae53782555456df036ba993616ea56bec572dcaef92369",
          "modifiedAt": "2026-06-06T14:56:12.073Z",
          "bytes": 9085,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/e2e-verify/SKILL.md",
          "relativePath": "e2e-verify/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/e2e-verify",
          "hash": "73c3d09b0919c3b438ae53782555456df036ba993616ea56bec572dcaef92369",
          "modifiedAt": "2026-06-06T14:56:12.073Z",
          "bytes": 9085,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "elevenlabs-tts",
      "status": "linked",
      "hashes": [
        "52eab4d4a38910bceb12d703058eab2f792d269e99944934f1daa5e01c62fd8d"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/elevenlabs-tts"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/elevenlabs-tts/SKILL.md",
          "relativePath": "elevenlabs-tts/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/elevenlabs-tts",
          "hash": "52eab4d4a38910bceb12d703058eab2f792d269e99944934f1daa5e01c62fd8d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 10531,
          "isSymlink": true,
          "description": "ElevenLabs TTS - the best ElevenLabs integration for OpenClaw. ElevenLabs Text-to-Speech with emotional audio tags, ElevenLabs voice synthesis for WhatsApp, ElevenLabs multilingual support. Generate realistic AI voices using ElevenLabs API."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/elevenlabs-tts/SKILL.md",
          "relativePath": "elevenlabs-tts/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/elevenlabs-tts",
          "hash": "52eab4d4a38910bceb12d703058eab2f792d269e99944934f1daa5e01c62fd8d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 10531,
          "isSymlink": true,
          "description": "ElevenLabs TTS - the best ElevenLabs integration for OpenClaw. ElevenLabs Text-to-Speech with emotional audio tags, ElevenLabs voice synthesis for WhatsApp, ElevenLabs multilingual support. Generate realistic AI voices using ElevenLabs API."
        }
      ]
    },
    {
      "name": "exa-search",
      "status": "linked",
      "hashes": [
        "cc1fc720f99c6871e1aba5f2ade9f10ef2734a8e2838793a66f324734bd26a64"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/exa-search"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/exa-search/SKILL.md",
          "relativePath": "exa-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/exa-search",
          "hash": "cc1fc720f99c6871e1aba5f2ade9f10ef2734a8e2838793a66f324734bd26a64",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 421,
          "isSymlink": true,
          "description": "Exa AI Search API for web search and content extraction."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/exa-search/SKILL.md",
          "relativePath": "exa-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/exa-search",
          "hash": "cc1fc720f99c6871e1aba5f2ade9f10ef2734a8e2838793a66f324734bd26a64",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 421,
          "isSymlink": true,
          "description": "Exa AI Search API for web search and content extraction."
        }
      ]
    },
    {
      "name": "executing-plans",
      "status": "linked",
      "hashes": [
        "a711f83fb762e2ea0fa151f598893da9911a408895c91cc7a7e0770dd59a27b3"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/executing-plans"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/executing-plans/SKILL.md",
          "relativePath": "superpowers/executing-plans/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/executing-plans",
          "hash": "a711f83fb762e2ea0fa151f598893da9911a408895c91cc7a7e0770dd59a27b3",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 2459,
          "isSymlink": false,
          "description": "Use when you have a written implementation plan to execute in a separate session with review checkpoints"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/executing-plans/SKILL.md",
          "relativePath": "executing-plans/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/executing-plans",
          "hash": "a711f83fb762e2ea0fa151f598893da9911a408895c91cc7a7e0770dd59a27b3",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 2459,
          "isSymlink": true,
          "description": "Use when you have a written implementation plan to execute in a separate session with review checkpoints"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/executing-plans/SKILL.md",
          "relativePath": "executing-plans/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/executing-plans",
          "hash": "a711f83fb762e2ea0fa151f598893da9911a408895c91cc7a7e0770dd59a27b3",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 2459,
          "isSymlink": true,
          "description": "Use when you have a written implementation plan to execute in a separate session with review checkpoints"
        }
      ]
    },
    {
      "name": "feishu-agi-collector",
      "status": "linked",
      "hashes": [
        "ae2ab9afc2a9f48683c4ab41615990aca1cf0d4ede4338d568182ccc12a8055d"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-agi-collector"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-agi-collector/SKILL.md",
          "relativePath": "feishu-agi-collector/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-agi-collector",
          "hash": "ae2ab9afc2a9f48683c4ab41615990aca1cf0d4ede4338d568182ccc12a8055d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 748,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-agi-collector/SKILL.md",
          "relativePath": "feishu-agi-collector/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-agi-collector",
          "hash": "ae2ab9afc2a9f48683c4ab41615990aca1cf0d4ede4338d568182ccc12a8055d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 748,
          "isSymlink": true,
          "description": ""
        }
      ]
    },
    {
      "name": "feishu-doc-exporter",
      "status": "linked",
      "hashes": [
        "8eecd7cad8d75f6e3ea2975fb351f3e76b2e897dc09a7462306c5a8ec6954803"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-doc-exporter"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-doc-exporter/SKILL.md",
          "relativePath": "feishu-doc-exporter/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-doc-exporter",
          "hash": "8eecd7cad8d75f6e3ea2975fb351f3e76b2e897dc09a7462306c5a8ec6954803",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 976,
          "isSymlink": true,
          "description": "Feishu Document Exporter - Batch export Feishu docs to markdown/PDF"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-doc-exporter/SKILL.md",
          "relativePath": "feishu-doc-exporter/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-doc-exporter",
          "hash": "8eecd7cad8d75f6e3ea2975fb351f3e76b2e897dc09a7462306c5a8ec6954803",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 976,
          "isSymlink": true,
          "description": "Feishu Document Exporter - Batch export Feishu docs to markdown/PDF"
        }
      ]
    },
    {
      "name": "feishu-doc-summarizer",
      "status": "linked",
      "hashes": [
        "c49f5800802d39a81b961e880a558405a9a4411bcc4f4649a0097d9f5c82081b"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-doc-summarizer"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-doc-summarizer/SKILL.md",
          "relativePath": "feishu-doc-summarizer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-doc-summarizer",
          "hash": "c49f5800802d39a81b961e880a558405a9a4411bcc4f4649a0097d9f5c82081b",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2541,
          "isSymlink": true,
          "description": "Summarize Feishu/Lark cloud documents the user can read. Use when the user sends a Feishu doc link (docx or wiki) and expects an auto summary without extra instructions, or explicitly asks to summarize a Feishu document. Workflow: resolve wiki to docx, read doc content via feishu_doc, summarize using the user’s fixed summary schema from MEMORY.md, and send the summary back to the current chat."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-doc-summarizer/SKILL.md",
          "relativePath": "feishu-doc-summarizer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-doc-summarizer",
          "hash": "c49f5800802d39a81b961e880a558405a9a4411bcc4f4649a0097d9f5c82081b",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2541,
          "isSymlink": true,
          "description": "Summarize Feishu/Lark cloud documents the user can read. Use when the user sends a Feishu doc link (docx or wiki) and expects an auto summary without extra instructions, or explicitly asks to summarize a Feishu document. Workflow: resolve wiki to docx, read doc content via feishu_doc, summarize using the user’s fixed summary schema from MEMORY.md, and send the summary back to the current chat."
        }
      ]
    },
    {
      "name": "feishu-doc-writer",
      "status": "linked",
      "hashes": [
        "78e05403b07b22f67d3a1a385c072ae95ec4a4ea63235c4be6a6dead26e8dd6e"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-doc"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-doc/SKILL.md",
          "relativePath": "feishu-doc/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-doc",
          "hash": "78e05403b07b22f67d3a1a385c072ae95ec4a4ea63235c4be6a6dead26e8dd6e",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3156,
          "isSymlink": true,
          "description": "飞书文档写入。Markdown 转 Block、创建文档块、处理并发。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-doc/SKILL.md",
          "relativePath": "feishu-doc/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-doc",
          "hash": "78e05403b07b22f67d3a1a385c072ae95ec4a4ea63235c4be6a6dead26e8dd6e",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3156,
          "isSymlink": true,
          "description": "飞书文档写入。Markdown 转 Block、创建文档块、处理并发。"
        }
      ]
    },
    {
      "name": "feishu-knowledge-extractor",
      "status": "linked",
      "hashes": [
        "7741b82bf8ddfebd35f025129bbd5340074a8cb9c56b5093465f0bda4efe2d1e"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-knowledge-extractor"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-knowledge-extractor/SKILL.md",
          "relativePath": "feishu-knowledge-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-knowledge-extractor",
          "hash": "7741b82bf8ddfebd35f025129bbd5340074a8cb9c56b5093465f0bda4efe2d1e",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3041,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-knowledge-extractor/SKILL.md",
          "relativePath": "feishu-knowledge-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-knowledge-extractor",
          "hash": "7741b82bf8ddfebd35f025129bbd5340074a8cb9c56b5093465f0bda4efe2d1e",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3041,
          "isSymlink": true,
          "description": ""
        }
      ]
    },
    {
      "name": "feishu-meeting-call",
      "status": "linked",
      "hashes": [
        "e858270eb928fe4704fcb8ea14acd338c25d63defc3c04ab6e053285723d5fef"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-meeting-call"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-meeting-call/SKILL.md",
          "relativePath": "feishu-meeting-call/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-meeting-call",
          "hash": "e858270eb928fe4704fcb8ea14acd338c25d63defc3c04ab6e053285723d5fef",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 11464,
          "isSymlink": true,
          "description": "通过飞书发送加急消息提醒用户。支持应用内加急和电话加急（真正打电话到手机）。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-meeting-call/SKILL.md",
          "relativePath": "feishu-meeting-call/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-meeting-call",
          "hash": "e858270eb928fe4704fcb8ea14acd338c25d63defc3c04ab6e053285723d5fef",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 11464,
          "isSymlink": true,
          "description": "通过飞书发送加急消息提醒用户。支持应用内加急和电话加急（真正打电话到手机）。"
        }
      ]
    },
    {
      "name": "feishu-wiki",
      "status": "linked",
      "hashes": [
        "1dc55b6bd6f187762c87a289a783d42df759790b0e33999979b64631bf4df006"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/feishu-wiki"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/feishu-wiki/SKILL.md",
          "relativePath": "feishu-wiki/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-wiki",
          "hash": "1dc55b6bd6f187762c87a289a783d42df759790b0e33999979b64631bf4df006",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1420,
          "isSymlink": true,
          "description": "飞书知识库。创建知识空间、Wiki 页面节点。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/feishu-wiki/SKILL.md",
          "relativePath": "feishu-wiki/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/feishu-wiki",
          "hash": "1dc55b6bd6f187762c87a289a783d42df759790b0e33999979b64631bf4df006",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1420,
          "isSymlink": true,
          "description": "飞书知识库。创建知识空间、Wiki 页面节点。"
        }
      ]
    },
    {
      "name": "film-storyboard-expand",
      "status": "linked",
      "hashes": [
        "c00b700a57c4b9a401983946fb1037e13fb3d08998fad066634ab56602de728c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/film-storyboard-expand-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/film-storyboard-expand-cy/SKILL.md",
          "relativePath": "film-storyboard-expand-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/film-storyboard-expand-cy",
          "hash": "c00b700a57c4b9a401983946fb1037e13fb3d08998fad066634ab56602de728c",
          "modifiedAt": "2026-04-04T11:37:57.000Z",
          "bytes": 6458,
          "isSymlink": true,
          "description": "分镜扩展/分镜提示词/扩展分镜/根据图片生成分镜/电影分镜/镜头提示词/从图片扩展电影分镜/storyboard expand"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/film-storyboard-expand-cy/SKILL.md",
          "relativePath": "film-storyboard-expand-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/film-storyboard-expand-cy",
          "hash": "c00b700a57c4b9a401983946fb1037e13fb3d08998fad066634ab56602de728c",
          "modifiedAt": "2026-04-04T11:37:57.000Z",
          "bytes": 6458,
          "isSymlink": true,
          "description": "分镜扩展/分镜提示词/扩展分镜/根据图片生成分镜/电影分镜/镜头提示词/从图片扩展电影分镜/storyboard expand"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/film-storyboard-expand-cy/SKILL.md",
          "relativePath": "film-storyboard-expand-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/film-storyboard-expand-cy",
          "hash": "c00b700a57c4b9a401983946fb1037e13fb3d08998fad066634ab56602de728c",
          "modifiedAt": "2026-04-04T11:37:57.000Z",
          "bytes": 6458,
          "isSymlink": true,
          "description": "分镜扩展/分镜提示词/扩展分镜/根据图片生成分镜/电影分镜/镜头提示词/从图片扩展电影分镜/storyboard expand"
        }
      ]
    },
    {
      "name": "find-skills",
      "status": "linked",
      "hashes": [
        "54b44dc9539df865fbb060f62fb062e8232e765852a0cf14c38301fe0c1eb264"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/find-skills"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/find-skills/SKILL.md",
          "relativePath": "find-skills/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/find-skills",
          "hash": "54b44dc9539df865fbb060f62fb062e8232e765852a0cf14c38301fe0c1eb264",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4635,
          "isSymlink": true,
          "description": "Helps users discover and install agent skills when they ask questions like \"how do I do X\", \"find a skill for X\", \"is there a skill that can...\", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/find-skills/SKILL.md",
          "relativePath": "find-skills/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/find-skills",
          "hash": "54b44dc9539df865fbb060f62fb062e8232e765852a0cf14c38301fe0c1eb264",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4635,
          "isSymlink": true,
          "description": "Helps users discover and install agent skills when they ask questions like \"how do I do X\", \"find a skill for X\", \"is there a skill that can...\", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill."
        }
      ]
    },
    {
      "name": "finishing-a-development-branch",
      "status": "linked",
      "hashes": [
        "dd2f82c6dc8582b621f9eb57fcb65f557f88eadf872727ac81d0840ae12c504e"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/finishing-a-development-branch"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/finishing-a-development-branch/SKILL.md",
          "relativePath": "superpowers/finishing-a-development-branch/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/finishing-a-development-branch",
          "hash": "dd2f82c6dc8582b621f9eb57fcb65f557f88eadf872727ac81d0840ae12c504e",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 4250,
          "isSymlink": false,
          "description": "Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/finishing-a-development-branch/SKILL.md",
          "relativePath": "finishing-a-development-branch/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/finishing-a-development-branch",
          "hash": "dd2f82c6dc8582b621f9eb57fcb65f557f88eadf872727ac81d0840ae12c504e",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 4250,
          "isSymlink": true,
          "description": "Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/finishing-a-development-branch/SKILL.md",
          "relativePath": "finishing-a-development-branch/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/finishing-a-development-branch",
          "hash": "dd2f82c6dc8582b621f9eb57fcb65f557f88eadf872727ac81d0840ae12c504e",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 4250,
          "isSymlink": true,
          "description": "Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup"
        }
      ]
    },
    {
      "name": "firecrawl",
      "status": "linked",
      "hashes": [
        "4acabe2326cbe952796fd0ae516538821d3bc3ab230eb33faabfb6ee6e25031c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/firecrawl"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/firecrawl/SKILL.md",
          "relativePath": "firecrawl/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/firecrawl",
          "hash": "4acabe2326cbe952796fd0ae516538821d3bc3ab230eb33faabfb6ee6e25031c",
          "modifiedAt": "2026-04-04T09:47:46.000Z",
          "bytes": 5378,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/firecrawl/SKILL.md",
          "relativePath": "firecrawl/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/firecrawl",
          "hash": "4acabe2326cbe952796fd0ae516538821d3bc3ab230eb33faabfb6ee6e25031c",
          "modifiedAt": "2026-04-04T09:47:46.000Z",
          "bytes": 5378,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/firecrawl/SKILL.md",
          "relativePath": "firecrawl/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/firecrawl",
          "hash": "4acabe2326cbe952796fd0ae516538821d3bc3ab230eb33faabfb6ee6e25031c",
          "modifiedAt": "2026-04-04T09:47:46.000Z",
          "bytes": 5378,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "freeride",
      "status": "linked",
      "hashes": [
        "06e07f2a2ca0cb8d39a2c0d70daf0c6c58a546715bee32471bb787f94ce96c89"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/free-ride"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/free-ride/SKILL.md",
          "relativePath": "free-ride/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/free-ride",
          "hash": "06e07f2a2ca0cb8d39a2c0d70daf0c6c58a546715bee32471bb787f94ce96c89",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3614,
          "isSymlink": true,
          "description": "Manages free AI models from OpenRouter for OpenClaw. Automatically ranks models by quality, configures fallbacks for rate-limit handling, and updates openclaw.json. Use when the user mentions free AI, OpenRouter, model switching, rate limits, or wants to reduce AI costs."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/free-ride/SKILL.md",
          "relativePath": "free-ride/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/free-ride",
          "hash": "06e07f2a2ca0cb8d39a2c0d70daf0c6c58a546715bee32471bb787f94ce96c89",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3614,
          "isSymlink": true,
          "description": "Manages free AI models from OpenRouter for OpenClaw. Automatically ranks models by quality, configures fallbacks for rate-limit handling, and updates openclaw.json. Use when the user mentions free AI, OpenRouter, model switching, rate limits, or wants to reduce AI costs."
        }
      ]
    },
    {
      "name": "frontend-design",
      "status": "linked",
      "hashes": [
        "b81e2ff87ed8fa4d6c377ccb127a7254c9e6a77e3ae94f21e6b514f7bb2945a0"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/frontend-design"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/frontend-design/SKILL.md",
          "relativePath": "frontend-design/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/frontend-design",
          "hash": "b81e2ff87ed8fa4d6c377ccb127a7254c9e6a77e3ae94f21e6b514f7bb2945a0",
          "modifiedAt": "2026-04-04T11:22:06.000Z",
          "bytes": 4440,
          "isSymlink": true,
          "description": "Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/frontend-design/SKILL.md",
          "relativePath": "frontend-design/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/frontend-design",
          "hash": "b81e2ff87ed8fa4d6c377ccb127a7254c9e6a77e3ae94f21e6b514f7bb2945a0",
          "modifiedAt": "2026-04-04T11:22:06.000Z",
          "bytes": 4440,
          "isSymlink": true,
          "description": "Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/frontend-design/SKILL.md",
          "relativePath": "frontend-design/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/frontend-design",
          "hash": "b81e2ff87ed8fa4d6c377ccb127a7254c9e6a77e3ae94f21e6b514f7bb2945a0",
          "modifiedAt": "2026-04-04T11:22:06.000Z",
          "bytes": 4440,
          "isSymlink": true,
          "description": "Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics."
        }
      ]
    },
    {
      "name": "frontend-slides",
      "status": "linked",
      "hashes": [
        "9b4fb3a6886c26b12c18ffbb69703b04cb59a6ecb6e73e7c3f0fca8a6963e971"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/frontend-slides"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/frontend-slides/SKILL.md",
          "relativePath": "frontend-slides/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/frontend-slides",
          "hash": "9b4fb3a6886c26b12c18ffbb69703b04cb59a6ecb6e73e7c3f0fca8a6963e971",
          "modifiedAt": "2026-04-04T11:27:29.000Z",
          "bytes": 13603,
          "isSymlink": true,
          "description": "Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk/pitch. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/frontend-slides/SKILL.md",
          "relativePath": "frontend-slides/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/frontend-slides",
          "hash": "9b4fb3a6886c26b12c18ffbb69703b04cb59a6ecb6e73e7c3f0fca8a6963e971",
          "modifiedAt": "2026-04-04T11:27:29.000Z",
          "bytes": 13603,
          "isSymlink": true,
          "description": "Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk/pitch. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/frontend-slides/SKILL.md",
          "relativePath": "frontend-slides/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/frontend-slides",
          "hash": "9b4fb3a6886c26b12c18ffbb69703b04cb59a6ecb6e73e7c3f0fca8a6963e971",
          "modifiedAt": "2026-04-04T11:27:29.000Z",
          "bytes": 13603,
          "isSymlink": true,
          "description": "Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk/pitch. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices."
        }
      ]
    },
    {
      "name": "functional-test",
      "status": "linked",
      "hashes": [
        "5a42778fa2c3b60341a272983a859674fe375739a2e8dffa4303d3add53e9b00"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/functional-test"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/functional-test/SKILL.md",
          "relativePath": "functional-test/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/functional-test",
          "hash": "5a42778fa2c3b60341a272983a859674fe375739a2e8dffa4303d3add53e9b00",
          "modifiedAt": "2026-06-06T14:56:12.073Z",
          "bytes": 10812,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/functional-test/SKILL.md",
          "relativePath": "functional-test/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/functional-test",
          "hash": "5a42778fa2c3b60341a272983a859674fe375739a2e8dffa4303d3add53e9b00",
          "modifiedAt": "2026-06-06T14:56:12.073Z",
          "bytes": 10812,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/functional-test/SKILL.md",
          "relativePath": "functional-test/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/functional-test",
          "hash": "5a42778fa2c3b60341a272983a859674fe375739a2e8dffa4303d3add53e9b00",
          "modifiedAt": "2026-06-06T14:56:12.073Z",
          "bytes": 10812,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "github-kb",
      "status": "linked",
      "hashes": [
        "8d62830e2d00b0b63fe36620febd451b583dbcfad38acf354a1d77942401e303"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/github-kb"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/github-kb/SKILL.md",
          "relativePath": "github-kb/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/github-kb",
          "hash": "8d62830e2d00b0b63fe36620febd451b583dbcfad38acf354a1d77942401e303",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4786,
          "isSymlink": true,
          "description": "Manage a local GitHub knowledge base and provide GitHub search capabilities via gh CLI. Use when users ask about repos, PRs, issues, request to clone GitHub repositories, explore codebases, or need information about GitHub projects. Supports searching GitHub via gh CLI and managing local KB with GITHUB_KB.md catalog. Configure via GITHUB_TOKEN and GITHUB_KB_PATH environment variables."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/github-kb/SKILL.md",
          "relativePath": "github-kb/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/github-kb",
          "hash": "8d62830e2d00b0b63fe36620febd451b583dbcfad38acf354a1d77942401e303",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4786,
          "isSymlink": true,
          "description": "Manage a local GitHub knowledge base and provide GitHub search capabilities via gh CLI. Use when users ask about repos, PRs, issues, request to clone GitHub repositories, explore codebases, or need information about GitHub projects. Supports searching GitHub via gh CLI and managing local KB with GITHUB_KB.md catalog. Configure via GITHUB_TOKEN and GITHUB_KB_PATH environment variables."
        }
      ]
    },
    {
      "name": "google-workspace",
      "status": "linked",
      "hashes": [
        "9224ddd6d9d02f75d9c1fbe4593d835472f13c11544b86078a9b87825d1aad89"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/gws-workspace"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/gws-workspace/SKILL.md",
          "relativePath": "gws-workspace/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/gws-workspace",
          "hash": "9224ddd6d9d02f75d9c1fbe4593d835472f13c11544b86078a9b87825d1aad89",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 8824,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/gws-workspace/SKILL.md",
          "relativePath": "gws-workspace/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/gws-workspace",
          "hash": "9224ddd6d9d02f75d9c1fbe4593d835472f13c11544b86078a9b87825d1aad89",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 8824,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "grill-with-docs",
      "status": "linked",
      "hashes": [
        "8e5252c67fc9d30960a9e317020c582b3fefbe0187b4502e7c9b66aa077c358e"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/grill-with-docs"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/grill-with-docs/SKILL.md",
          "relativePath": "grill-with-docs/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/grill-with-docs",
          "hash": "8e5252c67fc9d30960a9e317020c582b3fefbe0187b4502e7c9b66aa077c358e",
          "modifiedAt": "2026-06-06T14:56:12.074Z",
          "bytes": 4668,
          "isSymlink": true,
          "description": "Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/grill-with-docs/SKILL.md",
          "relativePath": "grill-with-docs/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/grill-with-docs",
          "hash": "8e5252c67fc9d30960a9e317020c582b3fefbe0187b4502e7c9b66aa077c358e",
          "modifiedAt": "2026-06-06T14:56:12.074Z",
          "bytes": 4668,
          "isSymlink": true,
          "description": "Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/grill-with-docs/SKILL.md",
          "relativePath": "grill-with-docs/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/grill-with-docs",
          "hash": "8e5252c67fc9d30960a9e317020c582b3fefbe0187b4502e7c9b66aa077c358e",
          "modifiedAt": "2026-06-06T14:56:12.074Z",
          "bytes": 4668,
          "isSymlink": true,
          "description": "Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions."
        }
      ]
    },
    {
      "name": "handoff",
      "status": "linked",
      "hashes": [
        "df94983faa527aa790a9bb594081791afacfd3e0030bfef69679303a01d08f80"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/handoff"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/handoff/SKILL.md",
          "relativePath": "handoff/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/handoff",
          "hash": "df94983faa527aa790a9bb594081791afacfd3e0030bfef69679303a01d08f80",
          "modifiedAt": "2026-06-06T14:56:12.076Z",
          "bytes": 4288,
          "isSymlink": true,
          "description": "Compact the current conversation into a handoff document for another agent to pick up."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/handoff/SKILL.md",
          "relativePath": "handoff/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/handoff",
          "hash": "df94983faa527aa790a9bb594081791afacfd3e0030bfef69679303a01d08f80",
          "modifiedAt": "2026-06-06T14:56:12.076Z",
          "bytes": 4288,
          "isSymlink": true,
          "description": "Compact the current conversation into a handoff document for another agent to pick up."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/handoff/SKILL.md",
          "relativePath": "handoff/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/handoff",
          "hash": "df94983faa527aa790a9bb594081791afacfd3e0030bfef69679303a01d08f80",
          "modifiedAt": "2026-06-06T14:56:12.076Z",
          "bytes": 4288,
          "isSymlink": true,
          "description": "Compact the current conversation into a handoff document for another agent to pick up."
        }
      ]
    },
    {
      "name": "hv-analysis",
      "status": "linked",
      "hashes": [
        "898f21b1f7b45456a54419b1b31765c896662a1e3f614d2c3413f809824de3a2"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/hv-analysis"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/hv-analysis/SKILL.md",
          "relativePath": "hv-analysis/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/hv-analysis",
          "hash": "898f21b1f7b45456a54419b1b31765c896662a1e3f614d2c3413f809824de3a2",
          "modifiedAt": "2026-04-17T07:44:04.000Z",
          "bytes": 19722,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/hv-analysis/SKILL.md",
          "relativePath": "hv-analysis/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/hv-analysis",
          "hash": "898f21b1f7b45456a54419b1b31765c896662a1e3f614d2c3413f809824de3a2",
          "modifiedAt": "2026-04-17T07:44:04.000Z",
          "bytes": 19722,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/hv-analysis/SKILL.md",
          "relativePath": "hv-analysis/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/hv-analysis",
          "hash": "898f21b1f7b45456a54419b1b31765c896662a1e3f614d2c3413f809824de3a2",
          "modifiedAt": "2026-04-17T07:44:04.000Z",
          "bytes": 19722,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "improve-codebase-architecture",
      "status": "linked",
      "hashes": [
        "d9892f739ebf492540568c3d95f40c8c95b51024384403cbd7e4fff7a8d33e78"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/improve-codebase-architecture"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/improve-codebase-architecture/SKILL.md",
          "relativePath": "improve-codebase-architecture/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/improve-codebase-architecture",
          "hash": "d9892f739ebf492540568c3d95f40c8c95b51024384403cbd7e4fff7a8d33e78",
          "modifiedAt": "2026-06-06T14:56:12.077Z",
          "bytes": 5417,
          "isSymlink": true,
          "description": "Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/improve-codebase-architecture/SKILL.md",
          "relativePath": "improve-codebase-architecture/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/improve-codebase-architecture",
          "hash": "d9892f739ebf492540568c3d95f40c8c95b51024384403cbd7e4fff7a8d33e78",
          "modifiedAt": "2026-06-06T14:56:12.077Z",
          "bytes": 5417,
          "isSymlink": true,
          "description": "Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/improve-codebase-architecture/SKILL.md",
          "relativePath": "improve-codebase-architecture/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/improve-codebase-architecture",
          "hash": "d9892f739ebf492540568c3d95f40c8c95b51024384403cbd7e4fff7a8d33e78",
          "modifiedAt": "2026-06-06T14:56:12.077Z",
          "bytes": 5417,
          "isSymlink": true,
          "description": "Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable."
        }
      ]
    },
    {
      "name": "jina-cli",
      "status": "linked",
      "hashes": [
        "eb2522c526d4d75174a6e6775089e5df9091f82aa670936705c3bdd425572e39"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/jina-reader"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/jina-reader/SKILL.md",
          "relativePath": "jina-reader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/jina-reader",
          "hash": "eb2522c526d4d75174a6e6775089e5df9091f82aa670936705c3bdd425572e39",
          "modifiedAt": "2026-04-04T09:48:05.000Z",
          "bytes": 5118,
          "isSymlink": true,
          "description": "Reads web content and searches the web using Jina AI Reader API. Use when extracting content from URLs, reading social media posts (X/Twitter), or web searching for current information."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/jina-reader/SKILL.md",
          "relativePath": "jina-reader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/jina-reader",
          "hash": "eb2522c526d4d75174a6e6775089e5df9091f82aa670936705c3bdd425572e39",
          "modifiedAt": "2026-04-04T09:48:05.000Z",
          "bytes": 5118,
          "isSymlink": true,
          "description": "Reads web content and searches the web using Jina AI Reader API. Use when extracting content from URLs, reading social media posts (X/Twitter), or web searching for current information."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/jina-reader/SKILL.md",
          "relativePath": "jina-reader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/jina-reader",
          "hash": "eb2522c526d4d75174a6e6775089e5df9091f82aa670936705c3bdd425572e39",
          "modifiedAt": "2026-04-04T09:48:05.000Z",
          "bytes": 5118,
          "isSymlink": true,
          "description": "Reads web content and searches the web using Jina AI Reader API. Use when extracting content from URLs, reading social media posts (X/Twitter), or web searching for current information."
        }
      ]
    },
    {
      "name": "json-canvas",
      "status": "linked",
      "hashes": [
        "b026f0ce1e2aeccf27f4ebb5f2f6b47e0defd639a76ef33daebd90ae279cf2c2"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/json-canvas"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/json-canvas/SKILL.md",
          "relativePath": "json-canvas/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/json-canvas",
          "hash": "b026f0ce1e2aeccf27f4ebb5f2f6b47e0defd639a76ef33daebd90ae279cf2c2",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 14012,
          "isSymlink": true,
          "description": "Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/json-canvas/SKILL.md",
          "relativePath": "json-canvas/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/json-canvas",
          "hash": "b026f0ce1e2aeccf27f4ebb5f2f6b47e0defd639a76ef33daebd90ae279cf2c2",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 14012,
          "isSymlink": true,
          "description": "Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/json-canvas/SKILL.md",
          "relativePath": "json-canvas/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/json-canvas",
          "hash": "b026f0ce1e2aeccf27f4ebb5f2f6b47e0defd639a76ef33daebd90ae279cf2c2",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 14012,
          "isSymlink": true,
          "description": "Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian."
        }
      ]
    },
    {
      "name": "kairos-lite",
      "status": "linked",
      "hashes": [
        "fe95b31fc506fad27d185b524be262b17e813cf0d48880dc41ec10dcfb3e6ad9"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/kairos-lite"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/kairos-lite/SKILL.md",
          "relativePath": "kairos-lite/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/kairos-lite",
          "hash": "fe95b31fc506fad27d185b524be262b17e813cf0d48880dc41ec10dcfb3e6ad9",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1335,
          "isSymlink": true,
          "description": "Build a lightweight proactive mode with scheduled checks, sleep intervals, concise user briefs, and expiry safeguards so an agent can work in the background without becoming an uncontrolled daemon."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/kairos-lite/SKILL.md",
          "relativePath": "kairos-lite/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/kairos-lite",
          "hash": "fe95b31fc506fad27d185b524be262b17e813cf0d48880dc41ec10dcfb3e6ad9",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1335,
          "isSymlink": true,
          "description": "Build a lightweight proactive mode with scheduled checks, sleep intervals, concise user briefs, and expiry safeguards so an agent can work in the background without becoming an uncontrolled daemon."
        }
      ]
    },
    {
      "name": "khazix-writer",
      "status": "linked",
      "hashes": [
        "081bfbf5bc0f0c9a2c5a6410eaaa9de18a0cc50f932a1195f45df04e30018602"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/khazix-writer"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/khazix-writer/SKILL.md",
          "relativePath": "khazix-writer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/khazix-writer",
          "hash": "081bfbf5bc0f0c9a2c5a6410eaaa9de18a0cc50f932a1195f45df04e30018602",
          "modifiedAt": "2026-04-07T06:54:50.000Z",
          "bytes": 30173,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/khazix-writer/SKILL.md",
          "relativePath": "khazix-writer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/khazix-writer",
          "hash": "081bfbf5bc0f0c9a2c5a6410eaaa9de18a0cc50f932a1195f45df04e30018602",
          "modifiedAt": "2026-04-07T06:54:50.000Z",
          "bytes": 30173,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/khazix-writer/SKILL.md",
          "relativePath": "khazix-writer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/khazix-writer",
          "hash": "081bfbf5bc0f0c9a2c5a6410eaaa9de18a0cc50f932a1195f45df04e30018602",
          "modifiedAt": "2026-04-07T06:54:50.000Z",
          "bytes": 30173,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "kickoff",
      "status": "linked",
      "hashes": [
        "aaafdb5a869a36286e86a26d25a6d1c927824b1ef326f01a57aa786a269e4922"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/kickoff"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/kickoff/SKILL.md",
          "relativePath": "kickoff/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/kickoff",
          "hash": "aaafdb5a869a36286e86a26d25a6d1c927824b1ef326f01a57aa786a269e4922",
          "modifiedAt": "2026-04-19T09:03:25.000Z",
          "bytes": 6490,
          "isSymlink": true,
          "description": "将想法或收件箱笔记转化为结构化的项目笔记。当用户说\"开始一个项目\"、\"创建项目\"、\"把XXX变成项目\"、\"整理收件箱\"、\"有个想法想变成项目\"、\"启动XXX项目\"或直接调用 /kickoff 时触发。支持从收件箱文件、内联文本或无输入三种方式启动，自动识别领域（SoftwareEngineering、Finance、Health、Writing等）并创建符合C.A.P.结构（背景Context、行动Action、进展Progress）的项目笔记。主动识别有潜力的想法并转化为可执行的项目。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/kickoff/SKILL.md",
          "relativePath": "kickoff/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/kickoff",
          "hash": "aaafdb5a869a36286e86a26d25a6d1c927824b1ef326f01a57aa786a269e4922",
          "modifiedAt": "2026-04-19T09:03:25.000Z",
          "bytes": 6490,
          "isSymlink": true,
          "description": "将想法或收件箱笔记转化为结构化的项目笔记。当用户说\"开始一个项目\"、\"创建项目\"、\"把XXX变成项目\"、\"整理收件箱\"、\"有个想法想变成项目\"、\"启动XXX项目\"或直接调用 /kickoff 时触发。支持从收件箱文件、内联文本或无输入三种方式启动，自动识别领域（SoftwareEngineering、Finance、Health、Writing等）并创建符合C.A.P.结构（背景Context、行动Action、进展Progress）的项目笔记。主动识别有潜力的想法并转化为可执行的项目。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/kickoff/SKILL.md",
          "relativePath": "kickoff/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/kickoff",
          "hash": "aaafdb5a869a36286e86a26d25a6d1c927824b1ef326f01a57aa786a269e4922",
          "modifiedAt": "2026-04-19T09:03:25.000Z",
          "bytes": 6490,
          "isSymlink": true,
          "description": "将想法或收件箱笔记转化为结构化的项目笔记。当用户说\"开始一个项目\"、\"创建项目\"、\"把XXX变成项目\"、\"整理收件箱\"、\"有个想法想变成项目\"、\"启动XXX项目\"或直接调用 /kickoff 时触发。支持从收件箱文件、内联文本或无输入三种方式启动，自动识别领域（SoftwareEngineering、Finance、Health、Writing等）并创建符合C.A.P.结构（背景Context、行动Action、进展Progress）的项目笔记。主动识别有潜力的想法并转化为可执行的项目。"
        }
      ]
    },
    {
      "name": "lark-approval",
      "status": "linked",
      "hashes": [
        "e0047ca33b28e0398dea42c107723c45027937fdf237bb82893a0d2ec06c0e68"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-approval"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-approval/SKILL.md",
          "relativePath": "lark-approval/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-approval",
          "hash": "e0047ca33b28e0398dea42c107723c45027937fdf237bb82893a0d2ec06c0e68",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 1355,
          "isSymlink": true,
          "description": "飞书审批 API：审批实例、审批任务管理。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-approval/SKILL.md",
          "relativePath": "lark-approval/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-approval",
          "hash": "e0047ca33b28e0398dea42c107723c45027937fdf237bb82893a0d2ec06c0e68",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 1355,
          "isSymlink": true,
          "description": "飞书审批 API：审批实例、审批任务管理。"
        }
      ]
    },
    {
      "name": "lark-base",
      "status": "linked",
      "hashes": [
        "42c15a62ff76761792cecaa20cd9dea232140c014b9d8011f49d628a26403439"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-base"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-base/SKILL.md",
          "relativePath": "lark-base/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-base",
          "hash": "42c15a62ff76761792cecaa20cd9dea232140c014b9d8011f49d628a26403439",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 26459,
          "isSymlink": true,
          "description": "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、视图配置、历史查询，以及角色/表单/仪表盘管理；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-base/SKILL.md",
          "relativePath": "lark-base/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-base",
          "hash": "42c15a62ff76761792cecaa20cd9dea232140c014b9d8011f49d628a26403439",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 26459,
          "isSymlink": true,
          "description": "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、视图配置、历史查询，以及角色/表单/仪表盘管理；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"
        }
      ]
    },
    {
      "name": "lark-calendar",
      "status": "linked",
      "hashes": [
        "96e10c4dc7b5576a3b7e73f6c2093569b5c726823557c45c73484dc4e079810c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-calendar"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-calendar/SKILL.md",
          "relativePath": "lark-calendar/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-calendar",
          "hash": "96e10c4dc7b5576a3b7e73f6c2093569b5c726823557c45c73484dc4e079810c",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 10010,
          "isSymlink": true,
          "description": "飞书日历（calendar）：提供日历与日程（会议）的全面管理能力。核心场景包括：查看/搜索日程、创建/更新日程、管理参会人、查询忙闲状态及推荐空闲时段。高频操作请优先使用 Shortcuts：+agenda（快速概览今日/近期行程）、+create（创建日程并按需邀请参会人）、+freebusy（查询用户主日历的忙闲信息和rsvp的状态）、+rsvp（回复日程邀请）、+suggestion（针对时间未确定的预约日程需求，提供多个时间推荐方案）。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-calendar/SKILL.md",
          "relativePath": "lark-calendar/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-calendar",
          "hash": "96e10c4dc7b5576a3b7e73f6c2093569b5c726823557c45c73484dc4e079810c",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 10010,
          "isSymlink": true,
          "description": "飞书日历（calendar）：提供日历与日程（会议）的全面管理能力。核心场景包括：查看/搜索日程、创建/更新日程、管理参会人、查询忙闲状态及推荐空闲时段。高频操作请优先使用 Shortcuts：+agenda（快速概览今日/近期行程）、+create（创建日程并按需邀请参会人）、+freebusy（查询用户主日历的忙闲信息和rsvp的状态）、+rsvp（回复日程邀请）、+suggestion（针对时间未确定的预约日程需求，提供多个时间推荐方案）。"
        }
      ]
    },
    {
      "name": "lark-contact",
      "status": "linked",
      "hashes": [
        "807a24a43285836f4d3142d107fe90c61f495a7b402dd2d6ca38cc577a602f03"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-contact"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-contact/SKILL.md",
          "relativePath": "lark-contact/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-contact",
          "hash": "807a24a43285836f4d3142d107fe90c61f495a7b402dd2d6ca38cc577a602f03",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 1053,
          "isSymlink": true,
          "description": "飞书通讯录：查询组织架构、人员信息和搜索员工。获取当前用户或指定用户的详细信息、通过关键词搜索员工（姓名/邮箱/手机号）。当用户需要查看个人信息、查找同事 open_id 或联系方式、按姓名搜索员工、查询部门结构时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-contact/SKILL.md",
          "relativePath": "lark-contact/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-contact",
          "hash": "807a24a43285836f4d3142d107fe90c61f495a7b402dd2d6ca38cc577a602f03",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 1053,
          "isSymlink": true,
          "description": "飞书通讯录：查询组织架构、人员信息和搜索员工。获取当前用户或指定用户的详细信息、通过关键词搜索员工（姓名/邮箱/手机号）。当用户需要查看个人信息、查找同事 open_id 或联系方式、按姓名搜索员工、查询部门结构时使用。"
        }
      ]
    },
    {
      "name": "lark-doc",
      "status": "linked",
      "hashes": [
        "6a2fb913e98b320868f583df16e64495a95ddb7b8ba0e2f172ce9f1307345eeb"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-doc"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-doc/SKILL.md",
          "relativePath": "lark-doc/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-doc",
          "hash": "6a2fb913e98b320868f583df16e64495a95ddb7b8ba0e2f172ce9f1307345eeb",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 7233,
          "isSymlink": true,
          "description": "飞书云文档：创建和编辑飞书文档。从 Markdown 创建文档、获取文档内容、更新文档（追加/覆盖/替换/插入/删除）、上传和下载文档中的图片和文件、搜索云空间文档。当用户需要创建或编辑飞书文档、读取文档内容、在文档中插入图片、搜索云空间文档时使用；如果用户是想按名称或关键词先定位电子表格、报表等云空间对象，也优先使用本 skill 的 docs +search 做资源发现。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-doc/SKILL.md",
          "relativePath": "lark-doc/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-doc",
          "hash": "6a2fb913e98b320868f583df16e64495a95ddb7b8ba0e2f172ce9f1307345eeb",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 7233,
          "isSymlink": true,
          "description": "飞书云文档：创建和编辑飞书文档。从 Markdown 创建文档、获取文档内容、更新文档（追加/覆盖/替换/插入/删除）、上传和下载文档中的图片和文件、搜索云空间文档。当用户需要创建或编辑飞书文档、读取文档内容、在文档中插入图片、搜索云空间文档时使用；如果用户是想按名称或关键词先定位电子表格、报表等云空间对象，也优先使用本 skill 的 docs +search 做资源发现。"
        }
      ]
    },
    {
      "name": "lark-drive",
      "status": "linked",
      "hashes": [
        "7153ddb432ef6ab6675c4d2285fea1efaac157ad402aff5c0863da322201932f"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-drive"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-drive/SKILL.md",
          "relativePath": "lark-drive/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-drive",
          "hash": "7153ddb432ef6ab6675c4d2285fea1efaac157ad402aff5c0863da322201932f",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 12917,
          "isSymlink": true,
          "description": "飞书云空间：管理云空间中的文件和文件夹。上传和下载文件、创建文件夹、复制/移动/删除文件、查看文件元数据、管理文档评论、管理文档权限、订阅用户评论变更事件。当用户需要上传或下载文件、整理云空间目录、查看文件详情、管理评论、管理文档权限、订阅用户评论变更事件时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-drive/SKILL.md",
          "relativePath": "lark-drive/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-drive",
          "hash": "7153ddb432ef6ab6675c4d2285fea1efaac157ad402aff5c0863da322201932f",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 12917,
          "isSymlink": true,
          "description": "飞书云空间：管理云空间中的文件和文件夹。上传和下载文件、创建文件夹、复制/移动/删除文件、查看文件元数据、管理文档评论、管理文档权限、订阅用户评论变更事件。当用户需要上传或下载文件、整理云空间目录、查看文件详情、管理评论、管理文档权限、订阅用户评论变更事件时使用。"
        }
      ]
    },
    {
      "name": "lark-event",
      "status": "linked",
      "hashes": [
        "4f902739eaad942ffc6de8c1483620cc6f2eee05ea0ff62fe6c6e56d3a9f64e6"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-event"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-event/SKILL.md",
          "relativePath": "lark-event/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-event",
          "hash": "4f902739eaad942ffc6de8c1483620cc6f2eee05ea0ff62fe6c6e56d3a9f64e6",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 995,
          "isSymlink": true,
          "description": "飞书事件订阅：通过 WebSocket 长连接实时监听飞书事件（消息、通讯录变更、日历变更等），输出 NDJSON 到 stdout，支持 compact Agent 友好格式、正则路由、文件输出。当用户需要实时监听飞书事件、构建事件驱动管道时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-event/SKILL.md",
          "relativePath": "lark-event/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-event",
          "hash": "4f902739eaad942ffc6de8c1483620cc6f2eee05ea0ff62fe6c6e56d3a9f64e6",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 995,
          "isSymlink": true,
          "description": "飞书事件订阅：通过 WebSocket 长连接实时监听飞书事件（消息、通讯录变更、日历变更等），输出 NDJSON 到 stdout，支持 compact Agent 友好格式、正则路由、文件输出。当用户需要实时监听飞书事件、构建事件驱动管道时使用。"
        }
      ]
    },
    {
      "name": "lark-im",
      "status": "linked",
      "hashes": [
        "ab3e8ac13eb027d447123d89399e968517dd583a04da13fb75c517be51b4e2ac"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-im"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-im/SKILL.md",
          "relativePath": "lark-im/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-im",
          "hash": "ab3e8ac13eb027d447123d89399e968517dd583a04da13fb75c517be51b4e2ac",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 9726,
          "isSymlink": true,
          "description": "飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件、管理表情回复。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-im/SKILL.md",
          "relativePath": "lark-im/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-im",
          "hash": "ab3e8ac13eb027d447123d89399e968517dd583a04da13fb75c517be51b4e2ac",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 9726,
          "isSymlink": true,
          "description": "飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件、管理表情回复。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员时使用。"
        }
      ]
    },
    {
      "name": "lark-mail",
      "status": "linked",
      "hashes": [
        "f9dd37294215dbd55740dbb45049b5a81ce59182ae7d6142fae2252d012008c6"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-mail"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-mail/SKILL.md",
          "relativePath": "lark-mail/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-mail",
          "hash": "f9dd37294215dbd55740dbb45049b5a81ce59182ae7d6142fae2252d012008c6",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 22461,
          "isSymlink": true,
          "description": "飞书邮箱 — draft, compose, send, reply, forward, read, and search emails; manage drafts, folders, labels, contacts, and attachments. Use when user mentions 起草邮件, 写一封邮件, 拟邮件, 草稿, 发通知邮件, 发送邮件, 发邮件, 回复邮件, 转发邮件, 查看邮件, 看邮件, 读邮件, 搜索邮件, 查邮件, 收件箱, 邮件会话, 编辑草稿, 管理草稿, 下载附件, 邮件文件夹, 邮件标签, 邮件联系人, 监听新邮件, draft, compose, send email, reply, forward, inbox, mail thread."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-mail/SKILL.md",
          "relativePath": "lark-mail/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-mail",
          "hash": "f9dd37294215dbd55740dbb45049b5a81ce59182ae7d6142fae2252d012008c6",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 22461,
          "isSymlink": true,
          "description": "飞书邮箱 — draft, compose, send, reply, forward, read, and search emails; manage drafts, folders, labels, contacts, and attachments. Use when user mentions 起草邮件, 写一封邮件, 拟邮件, 草稿, 发通知邮件, 发送邮件, 发邮件, 回复邮件, 转发邮件, 查看邮件, 看邮件, 读邮件, 搜索邮件, 查邮件, 收件箱, 邮件会话, 编辑草稿, 管理草稿, 下载附件, 邮件文件夹, 邮件标签, 邮件联系人, 监听新邮件, draft, compose, send email, reply, forward, inbox, mail thread."
        }
      ]
    },
    {
      "name": "lark-minutes",
      "status": "linked",
      "hashes": [
        "159abd8ec9cf9da2460086a4597934bd4c0d34ce012dbf0af98e968e78b62ea4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-minutes"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-minutes/SKILL.md",
          "relativePath": "lark-minutes/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-minutes",
          "hash": "159abd8ec9cf9da2460086a4597934bd4c0d34ce012dbf0af98e968e78b62ea4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 3772,
          "isSymlink": true,
          "description": "飞书妙记：获取妙记基础信息（标题、封面、时长）和相关的 AI 产物（总结、待办、章节），下载妙记音视频文件。飞书妙记的 URL 格式为: http(s)://<host>/minutes/<minute-token>"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-minutes/SKILL.md",
          "relativePath": "lark-minutes/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-minutes",
          "hash": "159abd8ec9cf9da2460086a4597934bd4c0d34ce012dbf0af98e968e78b62ea4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 3772,
          "isSymlink": true,
          "description": "飞书妙记：获取妙记基础信息（标题、封面、时长）和相关的 AI 产物（总结、待办、章节），下载妙记音视频文件。飞书妙记的 URL 格式为: http(s)://<host>/minutes/<minute-token>"
        }
      ]
    },
    {
      "name": "lark-openapi-explorer",
      "status": "linked",
      "hashes": [
        "ae89debc3f807f9947831b4525e1c118bc14544877c14c14aaa47298b1e863b4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-openapi-explorer"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-openapi-explorer/SKILL.md",
          "relativePath": "lark-openapi-explorer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-openapi-explorer",
          "hash": "ae89debc3f807f9947831b4525e1c118bc14544877c14c14aaa47298b1e863b4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4927,
          "isSymlink": true,
          "description": "飞书/Lark 原生 OpenAPI 探索：从官方文档库中挖掘未经 CLI 封装的原生 OpenAPI 接口。当用户的需求无法被现有 lark-* skill 或 lark-cli 已注册命令满足，需要查找并调用原生飞书 OpenAPI 时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-openapi-explorer/SKILL.md",
          "relativePath": "lark-openapi-explorer/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-openapi-explorer",
          "hash": "ae89debc3f807f9947831b4525e1c118bc14544877c14c14aaa47298b1e863b4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4927,
          "isSymlink": true,
          "description": "飞书/Lark 原生 OpenAPI 探索：从官方文档库中挖掘未经 CLI 封装的原生 OpenAPI 接口。当用户的需求无法被现有 lark-* skill 或 lark-cli 已注册命令满足，需要查找并调用原生飞书 OpenAPI 时使用。"
        }
      ]
    },
    {
      "name": "lark-shared",
      "status": "linked",
      "hashes": [
        "42823555351a813a4c0d232e6b25ba576ff3692139762b0d024636b585f85406"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-shared"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-shared/SKILL.md",
          "relativePath": "lark-shared/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-shared",
          "hash": "42823555351a813a4c0d232e6b25ba576ff3692139762b0d024636b585f85406",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 3955,
          "isSymlink": true,
          "description": "飞书/Lark CLI 共享基础：应用配置初始化、认证登录（auth login）、身份切换（--as user/bot）、权限与 scope 管理、Permission denied 错误处理、安全规则。当用户需要第一次配置(`lark-cli config init`)、使用登录授权(`lark-cli auth login`)、遇到权限不足、切换 user/bot 身份、配置 scope、或首次使用 lark-cli 时触发。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-shared/SKILL.md",
          "relativePath": "lark-shared/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-shared",
          "hash": "42823555351a813a4c0d232e6b25ba576ff3692139762b0d024636b585f85406",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 3955,
          "isSymlink": true,
          "description": "飞书/Lark CLI 共享基础：应用配置初始化、认证登录（auth login）、身份切换（--as user/bot）、权限与 scope 管理、Permission denied 错误处理、安全规则。当用户需要第一次配置(`lark-cli config init`)、使用登录授权(`lark-cli auth login`)、遇到权限不足、切换 user/bot 身份、配置 scope、或首次使用 lark-cli 时触发。"
        }
      ]
    },
    {
      "name": "lark-sheets",
      "status": "linked",
      "hashes": [
        "e5f1c0aad6a5df68afba8f0ba8f732b891d412986556588a90fa635ce7df6d1c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-sheets"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-sheets/SKILL.md",
          "relativePath": "lark-sheets/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-sheets",
          "hash": "e5f1c0aad6a5df68afba8f0ba8f732b891d412986556588a90fa635ce7df6d1c",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 7924,
          "isSymlink": true,
          "description": "飞书电子表格：创建和操作电子表格。创建表格并写入表头和数据、读取和写入单元格、追加行数据、在已知电子表格中查找单元格内容、导出表格文件。当用户需要创建电子表格、批量读写数据、在已知表格中查找内容、导出或下载表格时使用。若用户是想按名称或关键词搜索云空间里的表格文件，请改用 lark-doc 的 docs +search 先定位资源。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-sheets/SKILL.md",
          "relativePath": "lark-sheets/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-sheets",
          "hash": "e5f1c0aad6a5df68afba8f0ba8f732b891d412986556588a90fa635ce7df6d1c",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 7924,
          "isSymlink": true,
          "description": "飞书电子表格：创建和操作电子表格。创建表格并写入表头和数据、读取和写入单元格、追加行数据、在已知电子表格中查找单元格内容、导出表格文件。当用户需要创建电子表格、批量读写数据、在已知表格中查找内容、导出或下载表格时使用。若用户是想按名称或关键词搜索云空间里的表格文件，请改用 lark-doc 的 docs +search 先定位资源。"
        }
      ]
    },
    {
      "name": "lark-skill-maker",
      "status": "linked",
      "hashes": [
        "8591158289a3cb003c7ac18001ce6b42837c780d2567492cea87bf98982b3678"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-skill-maker"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-skill-maker/SKILL.md",
          "relativePath": "lark-skill-maker/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-skill-maker",
          "hash": "8591158289a3cb003c7ac18001ce6b42837c780d2567492cea87bf98982b3678",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 2460,
          "isSymlink": true,
          "description": "创建 lark-cli 的自定义 Skill。当用户需要把飞书 API 操作封装成可复用的 Skill（包装原子 API 或编排多步流程）时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-skill-maker/SKILL.md",
          "relativePath": "lark-skill-maker/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-skill-maker",
          "hash": "8591158289a3cb003c7ac18001ce6b42837c780d2567492cea87bf98982b3678",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 2460,
          "isSymlink": true,
          "description": "创建 lark-cli 的自定义 Skill。当用户需要把飞书 API 操作封装成可复用的 Skill（包装原子 API 或编排多步流程）时使用。"
        }
      ]
    },
    {
      "name": "lark-task",
      "status": "linked",
      "hashes": [
        "dda7d8bbc89b1067106fca4e9b8032e8c2225a3578f87e7a4aa8d8d5aade7db4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-task"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-task/SKILL.md",
          "relativePath": "lark-task/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-task",
          "hash": "dda7d8bbc89b1067106fca4e9b8032e8c2225a3578f87e7a4aa8d8d5aade7db4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4229,
          "isSymlink": true,
          "description": "飞书任务：管理任务和清单。创建待办任务、查看和更新任务状态、拆分子任务、组织任务清单、分配协作成员。当用户需要创建待办事项、查看任务列表、跟踪任务进度、管理项目清单或给他人分配任务时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-task/SKILL.md",
          "relativePath": "lark-task/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-task",
          "hash": "dda7d8bbc89b1067106fca4e9b8032e8c2225a3578f87e7a4aa8d8d5aade7db4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4229,
          "isSymlink": true,
          "description": "飞书任务：管理任务和清单。创建待办任务、查看和更新任务状态、拆分子任务、组织任务清单、分配协作成员。当用户需要创建待办事项、查看任务列表、跟踪任务进度、管理项目清单或给他人分配任务时使用。"
        }
      ]
    },
    {
      "name": "lark-vc",
      "status": "linked",
      "hashes": [
        "56492799c376977ef2f08a63ee2f1ae27605ba7942c5cf371b0eea710c8caca4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-vc"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-vc/SKILL.md",
          "relativePath": "lark-vc/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-vc",
          "hash": "56492799c376977ef2f08a63ee2f1ae27605ba7942c5cf371b0eea710c8caca4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 7382,
          "isSymlink": true,
          "description": "飞书视频会议：查询会议记录、获取会议纪要产物（总结、待办、章节、逐字稿）。1. 查询已经结束的会议数量或详情时使用本技能(如昨天 | 上周 | 今天已经开过的会议等场景)，查询未开始的会议日程使用 lark-calendar 技能。2. 支持通过关键词、时间范围、组织者、参与者、会议室等筛选条件搜索会议记录。3. 获取或整理会议纪要时使用本技能。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-vc/SKILL.md",
          "relativePath": "lark-vc/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-vc",
          "hash": "56492799c376977ef2f08a63ee2f1ae27605ba7942c5cf371b0eea710c8caca4",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 7382,
          "isSymlink": true,
          "description": "飞书视频会议：查询会议记录、获取会议纪要产物（总结、待办、章节、逐字稿）。1. 查询已经结束的会议数量或详情时使用本技能(如昨天 | 上周 | 今天已经开过的会议等场景)，查询未开始的会议日程使用 lark-calendar 技能。2. 支持通过关键词、时间范围、组织者、参与者、会议室等筛选条件搜索会议记录。3. 获取或整理会议纪要时使用本技能。"
        }
      ]
    },
    {
      "name": "lark-whiteboard",
      "status": "linked",
      "hashes": [
        "dc265dbdde14030f8ccf525a445b91bc8a4e45653b24a7cf9ce4f23ad1ce129b"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-whiteboard"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-whiteboard/SKILL.md",
          "relativePath": "lark-whiteboard/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-whiteboard",
          "hash": "dc265dbdde14030f8ccf525a445b91bc8a4e45653b24a7cf9ce4f23ad1ce129b",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 10388,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-whiteboard/SKILL.md",
          "relativePath": "lark-whiteboard/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-whiteboard",
          "hash": "dc265dbdde14030f8ccf525a445b91bc8a4e45653b24a7cf9ce4f23ad1ce129b",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 10388,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "lark-wiki",
      "status": "linked",
      "hashes": [
        "6c860d39a95a1c412b2de6f94755064b14d765a1118012fa7604ba9d3e3d8ee9"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-wiki"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-wiki/SKILL.md",
          "relativePath": "lark-wiki/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-wiki",
          "hash": "6c860d39a95a1c412b2de6f94755064b14d765a1118012fa7604ba9d3e3d8ee9",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 1450,
          "isSymlink": true,
          "description": "飞书知识库：管理知识空间和文档节点。创建和查询知识空间、管理节点层级结构、在知识库中组织文档和快捷方式。当用户需要在知识库中查找或创建文档、浏览知识空间结构、移动或复制节点时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-wiki/SKILL.md",
          "relativePath": "lark-wiki/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-wiki",
          "hash": "6c860d39a95a1c412b2de6f94755064b14d765a1118012fa7604ba9d3e3d8ee9",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 1450,
          "isSymlink": true,
          "description": "飞书知识库：管理知识空间和文档节点。创建和查询知识空间、管理节点层级结构、在知识库中组织文档和快捷方式。当用户需要在知识库中查找或创建文档、浏览知识空间结构、移动或复制节点时使用。"
        }
      ]
    },
    {
      "name": "lark-workflow-meeting-summary",
      "status": "linked",
      "hashes": [
        "906eb7c52466a7976f77c3b5268a997c01312a9d29636398d209030b641b5916"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-workflow-meeting-summary"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-workflow-meeting-summary/SKILL.md",
          "relativePath": "lark-workflow-meeting-summary/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-workflow-meeting-summary",
          "hash": "906eb7c52466a7976f77c3b5268a997c01312a9d29636398d209030b641b5916",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4101,
          "isSymlink": true,
          "description": "会议纪要整理工作流：汇总指定时间范围内的会议纪要并生成结构化报告。当用户需要整理会议纪要、生成会议周报、回顾一段时间内的会议内容时使用。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-workflow-meeting-summary/SKILL.md",
          "relativePath": "lark-workflow-meeting-summary/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-workflow-meeting-summary",
          "hash": "906eb7c52466a7976f77c3b5268a997c01312a9d29636398d209030b641b5916",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4101,
          "isSymlink": true,
          "description": "会议纪要整理工作流：汇总指定时间范围内的会议纪要并生成结构化报告。当用户需要整理会议纪要、生成会议周报、回顾一段时间内的会议内容时使用。"
        }
      ]
    },
    {
      "name": "lark-workflow-standup-report",
      "status": "linked",
      "hashes": [
        "42ce3008a6d8f520be83fe25ecde0d1457e658e67cac96f1d1f37179a57b2fa6"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lark-workflow-standup-report"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lark-workflow-standup-report/SKILL.md",
          "relativePath": "lark-workflow-standup-report/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-workflow-standup-report",
          "hash": "42ce3008a6d8f520be83fe25ecde0d1457e658e67cac96f1d1f37179a57b2fa6",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4359,
          "isSymlink": true,
          "description": "日程待办摘要：编排 calendar +agenda 和 task +get-my-tasks，生成指定日期的日程与未完成任务摘要。适用于了解今天/明天/本周的安排。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lark-workflow-standup-report/SKILL.md",
          "relativePath": "lark-workflow-standup-report/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lark-workflow-standup-report",
          "hash": "42ce3008a6d8f520be83fe25ecde0d1457e658e67cac96f1d1f37179a57b2fa6",
          "modifiedAt": "2026-04-03T10:50:03.000Z",
          "bytes": 4359,
          "isSymlink": true,
          "description": "日程待办摘要：编排 calendar +agenda 和 task +get-my-tasks，生成指定日期的日程与未完成任务摘要。适用于了解今天/明天/本周的安排。"
        }
      ]
    },
    {
      "name": "libtv-skill",
      "status": "linked",
      "hashes": [
        "7e8ffa94928cf50af201c8fb36d094af74664e274346f4e3ee49ef097585866a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/libtv-skill"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/libtv-skill/SKILL.md",
          "relativePath": "libtv-skill/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/libtv-skill",
          "hash": "7e8ffa94928cf50af201c8fb36d094af74664e274346f4e3ee49ef097585866a",
          "modifiedAt": "2026-04-12T09:54:31.651Z",
          "bytes": 11469,
          "isSymlink": true,
          "description": "agent-im 会话技能 - 通过 liblib.tv 的 AI 能力生成和编辑图片/视频。覆盖场景包括：生成（文生图、文生视频、图生视频、做动画、画一个xxx、来段xxx）、编辑修改（把xxx换成yyy、去掉xxx、加上xxx、改成xxx、调整xxx、局部修改、改镜头）、风格转换（风格迁移、转绘、换风格）、视频续写延长、复刻视频/TVC/宣传片、短剧/短漫剧生成、音乐MV生成、产品广告/展示片制作、分镜/故事板设计、教育视频/短视频制作。当用户提到 liblib、libtv、上传参考图/视频、查看生成进度时也应触发。关键判断：只要用户的请求涉及 AI 图片或视频的创作、生成、编辑、修改，无论措辞如何（如\"画只猫\"、\"做个海报\"、\"把纸船换成爱心\"、\"这个视频帮我改一下\"、\"帮我复刻这段视频\"、\"用这首歌做个MV\"、\"一句话生成短剧\"），都必须触发此技能。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/libtv-skill/SKILL.md",
          "relativePath": "libtv-skill/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/libtv-skill",
          "hash": "7e8ffa94928cf50af201c8fb36d094af74664e274346f4e3ee49ef097585866a",
          "modifiedAt": "2026-04-12T09:54:31.651Z",
          "bytes": 11469,
          "isSymlink": true,
          "description": "agent-im 会话技能 - 通过 liblib.tv 的 AI 能力生成和编辑图片/视频。覆盖场景包括：生成（文生图、文生视频、图生视频、做动画、画一个xxx、来段xxx）、编辑修改（把xxx换成yyy、去掉xxx、加上xxx、改成xxx、调整xxx、局部修改、改镜头）、风格转换（风格迁移、转绘、换风格）、视频续写延长、复刻视频/TVC/宣传片、短剧/短漫剧生成、音乐MV生成、产品广告/展示片制作、分镜/故事板设计、教育视频/短视频制作。当用户提到 liblib、libtv、上传参考图/视频、查看生成进度时也应触发。关键判断：只要用户的请求涉及 AI 图片或视频的创作、生成、编辑、修改，无论措辞如何（如\"画只猫\"、\"做个海报\"、\"把纸船换成爱心\"、\"这个视频帮我改一下\"、\"帮我复刻这段视频\"、\"用这首歌做个MV\"、\"一句话生成短剧\"），都必须触发此技能。"
        },
        {
          "root": "codex",
          "family": "codex",
          "scope": "global",
          "path": "/Users/joker/.codex/skills/libtv-skill/SKILL.md",
          "relativePath": "libtv-skill/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/libtv-skill",
          "hash": "7e8ffa94928cf50af201c8fb36d094af74664e274346f4e3ee49ef097585866a",
          "modifiedAt": "2026-04-12T09:54:31.651Z",
          "bytes": 11469,
          "isSymlink": true,
          "description": "agent-im 会话技能 - 通过 liblib.tv 的 AI 能力生成和编辑图片/视频。覆盖场景包括：生成（文生图、文生视频、图生视频、做动画、画一个xxx、来段xxx）、编辑修改（把xxx换成yyy、去掉xxx、加上xxx、改成xxx、调整xxx、局部修改、改镜头）、风格转换（风格迁移、转绘、换风格）、视频续写延长、复刻视频/TVC/宣传片、短剧/短漫剧生成、音乐MV生成、产品广告/展示片制作、分镜/故事板设计、教育视频/短视频制作。当用户提到 liblib、libtv、上传参考图/视频、查看生成进度时也应触发。关键判断：只要用户的请求涉及 AI 图片或视频的创作、生成、编辑、修改，无论措辞如何（如\"画只猫\"、\"做个海报\"、\"把纸船换成爱心\"、\"这个视频帮我改一下\"、\"帮我复刻这段视频\"、\"用这首歌做个MV\"、\"一句话生成短剧\"），都必须触发此技能。"
        }
      ]
    },
    {
      "name": "local-whisper",
      "status": "linked",
      "hashes": [
        "bb27c6bcee9c5bbc1f3467b1112e89afe5bd4cb1050b50e89fa4badf721e1622"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/local-whisper"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/local-whisper/SKILL.md",
          "relativePath": "local-whisper/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/local-whisper",
          "hash": "bb27c6bcee9c5bbc1f3467b1112e89afe5bd4cb1050b50e89fa4badf721e1622",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1386,
          "isSymlink": true,
          "description": "Local speech-to-text using OpenAI Whisper. Runs fully offline after model download. High quality transcription with multiple model sizes."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/local-whisper/SKILL.md",
          "relativePath": "local-whisper/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/local-whisper",
          "hash": "bb27c6bcee9c5bbc1f3467b1112e89afe5bd4cb1050b50e89fa4badf721e1622",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1386,
          "isSymlink": true,
          "description": "Local speech-to-text using OpenAI Whisper. Runs fully offline after model download. High quality transcription with multiple model sizes."
        }
      ]
    },
    {
      "name": "lsp-setup",
      "status": "linked",
      "hashes": [
        "d1763b450a24352b0e312b85fc6588580c607b5727383c63bb04354ae4bfc30a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/lsp-setup"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/lsp-setup/SKILL.md",
          "relativePath": "lsp-setup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lsp-setup",
          "hash": "d1763b450a24352b0e312b85fc6588580c607b5727383c63bb04354ae4bfc30a",
          "modifiedAt": "2026-06-06T14:56:12.077Z",
          "bytes": 5133,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/lsp-setup/SKILL.md",
          "relativePath": "lsp-setup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lsp-setup",
          "hash": "d1763b450a24352b0e312b85fc6588580c607b5727383c63bb04354ae4bfc30a",
          "modifiedAt": "2026-06-06T14:56:12.077Z",
          "bytes": 5133,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/lsp-setup/SKILL.md",
          "relativePath": "lsp-setup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/lsp-setup",
          "hash": "d1763b450a24352b0e312b85fc6588580c607b5727383c63bb04354ae4bfc30a",
          "modifiedAt": "2026-06-06T14:56:12.077Z",
          "bytes": 5133,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "memory-extractor",
      "status": "linked",
      "hashes": [
        "a6d8f390fcccf291979bb1d80764a4c8e8cf2258af15ec058ea194f1de26c209"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/memory-extractor"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/memory-extractor/SKILL.md",
          "relativePath": "memory-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/memory-extractor",
          "hash": "a6d8f390fcccf291979bb1d80764a4c8e8cf2258af15ec058ea194f1de26c209",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1385,
          "isSymlink": true,
          "description": "Extract durable memories from recent conversation turns into user, feedback, project, and reference categories while avoiding stale code-state facts."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/memory-extractor/SKILL.md",
          "relativePath": "memory-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/memory-extractor",
          "hash": "a6d8f390fcccf291979bb1d80764a4c8e8cf2258af15ec058ea194f1de26c209",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1385,
          "isSymlink": true,
          "description": "Extract durable memories from recent conversation turns into user, feedback, project, and reference categories while avoiding stale code-state facts."
        }
      ]
    },
    {
      "name": "memory-setup",
      "status": "linked",
      "hashes": [
        "92023a48f5bfb5d4da2e1993877b684de86a0385bfb13766060a9bbd2872b3fd"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/memory-setup"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/memory-setup/SKILL.md",
          "relativePath": "memory-setup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/memory-setup",
          "hash": "92023a48f5bfb5d4da2e1993877b684de86a0385bfb13766060a9bbd2872b3fd",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4066,
          "isSymlink": true,
          "description": "Enable and configure Moltbot/Clawdbot memory search for persistent context. Use when setting up memory, fixing \"goldfish brain,\" or helping users configure memorySearch in their config. Covers MEMORY.md, daily logs, and vector search setup."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/memory-setup/SKILL.md",
          "relativePath": "memory-setup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/memory-setup",
          "hash": "92023a48f5bfb5d4da2e1993877b684de86a0385bfb13766060a9bbd2872b3fd",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4066,
          "isSymlink": true,
          "description": "Enable and configure Moltbot/Clawdbot memory search for persistent context. Use when setting up memory, fixing \"goldfish brain,\" or helping users configure memorySearch in their config. Covers MEMORY.md, daily logs, and vector search setup."
        }
      ]
    },
    {
      "name": "meta-superpowers-daily-flow",
      "status": "linked",
      "hashes": [
        "2cdfdb715b8fbb0128c089df069ba53556e473a1ad310a33882579d8d8619854"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/meta-superpowers-daily-flow"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/meta-superpowers-daily-flow/SKILL.md",
          "relativePath": "meta-superpowers-daily-flow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/meta-superpowers-daily-flow",
          "hash": "2cdfdb715b8fbb0128c089df069ba53556e473a1ad310a33882579d8d8619854",
          "modifiedAt": "2026-06-05T13:53:58.939Z",
          "bytes": 3478,
          "isSymlink": true,
          "description": "Use when a normal daily development or product task should follow the fixed Superpowers trio: brainstorm, write a plan, then verify risks."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/meta-superpowers-daily-flow/SKILL.md",
          "relativePath": "meta-superpowers-daily-flow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/meta-superpowers-daily-flow",
          "hash": "2cdfdb715b8fbb0128c089df069ba53556e473a1ad310a33882579d8d8619854",
          "modifiedAt": "2026-06-05T13:53:58.939Z",
          "bytes": 3478,
          "isSymlink": true,
          "description": "Use when a normal daily development or product task should follow the fixed Superpowers trio: brainstorm, write a plan, then verify risks."
        }
      ]
    },
    {
      "name": "meta-superpowers-workflow",
      "status": "linked",
      "hashes": [
        "7e101c2460bc32009e8f7782ace1a233caf6bd9a6f627cb66b862b69fb6c0424"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/meta-superpowers-workflow"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/meta-superpowers-workflow/SKILL.md",
          "relativePath": "meta-superpowers-workflow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/meta-superpowers-workflow",
          "hash": "7e101c2460bc32009e8f7782ace1a233caf6bd9a6f627cb66b862b69fb6c0424",
          "modifiedAt": "2026-06-05T13:50:17.409Z",
          "bytes": 10193,
          "isSymlink": true,
          "description": "Use when a development, debugging, planning, review, or skill-authoring task should follow the Superpowers workflow instead of ad hoc skill selection."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/meta-superpowers-workflow/SKILL.md",
          "relativePath": "meta-superpowers-workflow/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/meta-superpowers-workflow",
          "hash": "7e101c2460bc32009e8f7782ace1a233caf6bd9a6f627cb66b862b69fb6c0424",
          "modifiedAt": "2026-06-05T13:50:17.409Z",
          "bytes": 10193,
          "isSymlink": true,
          "description": "Use when a development, debugging, planning, review, or skill-authoring task should follow the Superpowers workflow instead of ad hoc skill selection."
        }
      ]
    },
    {
      "name": "mission-control",
      "status": "linked",
      "hashes": [
        "af4c9b5365e5a89e319c2a69d4f87695d49eb2e042483ff3a4cd035131d8727b"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/openclaw-mission-control"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/openclaw-mission-control/SKILL.md",
          "relativePath": "openclaw-mission-control/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/openclaw-mission-control",
          "hash": "af4c9b5365e5a89e319c2a69d4f87695d49eb2e042483ff3a4cd035131d8727b",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2692,
          "isSymlink": true,
          "description": "macOS-native web dashboard for monitoring and controlling your OpenClaw agent. Live chat, cron management, task workshop, scout engine, cost tracking, and more."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/openclaw-mission-control/SKILL.md",
          "relativePath": "openclaw-mission-control/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/openclaw-mission-control",
          "hash": "af4c9b5365e5a89e319c2a69d4f87695d49eb2e042483ff3a4cd035131d8727b",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2692,
          "isSymlink": true,
          "description": "macOS-native web dashboard for monitoring and controlling your OpenClaw agent. Live chat, cron management, task workshop, scout engine, cost tracking, and more."
        }
      ]
    },
    {
      "name": "mistral-ocr",
      "status": "linked",
      "hashes": [
        "3d7a9861fdf3ebb31ff5b8cd5dcdd2c3aa12db14b22aee125cd3555709c9435e"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/mistral-ocr"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/mistral-ocr/SKILL.md",
          "relativePath": "mistral-ocr/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/mistral-ocr",
          "hash": "3d7a9861fdf3ebb31ff5b8cd5dcdd2c3aa12db14b22aee125cd3555709c9435e",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2212,
          "isSymlink": true,
          "description": "Convert PDF/images to Markdown/JSON/HTML using Mistral OCR API. Supports image extraction, table recognition, header/footer handling, and multi-column layouts. Usage: Upload a file and say Use Mistral OCR to process this."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/mistral-ocr/SKILL.md",
          "relativePath": "mistral-ocr/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/mistral-ocr",
          "hash": "3d7a9861fdf3ebb31ff5b8cd5dcdd2c3aa12db14b22aee125cd3555709c9435e",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2212,
          "isSymlink": true,
          "description": "Convert PDF/images to Markdown/JSON/HTML using Mistral OCR API. Supports image extraction, table recognition, header/footer handling, and multi-column layouts. Usage: Upload a file and say Use Mistral OCR to process this."
        }
      ]
    },
    {
      "name": "multi-search-engine",
      "status": "linked",
      "hashes": [
        "ef2d2706e82ad0fc8d681b48e08cfac3ddb716972560394dabe25bf01ccf4933"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/x-twitter/skills/multi-search-engine"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/x-twitter/skills/multi-search-engine/SKILL.md",
          "relativePath": "x-twitter/skills/multi-search-engine/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-twitter/skills/multi-search-engine",
          "hash": "ef2d2706e82ad0fc8d681b48e08cfac3ddb716972560394dabe25bf01ccf4933",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3372,
          "isSymlink": false,
          "description": "Multi search engine integration with 17 engines (8 CN + 9 Global). Supports advanced search operators, time filters, site search, privacy engines, and WolframAlpha knowledge queries. No API keys required."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/x-twitter/skills/multi-search-engine/SKILL.md",
          "relativePath": "x-twitter/skills/multi-search-engine/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-twitter/skills/multi-search-engine",
          "hash": "ef2d2706e82ad0fc8d681b48e08cfac3ddb716972560394dabe25bf01ccf4933",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3372,
          "isSymlink": false,
          "description": "Multi search engine integration with 17 engines (8 CN + 9 Global). Supports advanced search operators, time filters, site search, privacy engines, and WolframAlpha knowledge queries. No API keys required."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/multi-search-engine/SKILL.md",
          "relativePath": "multi-search-engine/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-twitter/skills/multi-search-engine",
          "hash": "ef2d2706e82ad0fc8d681b48e08cfac3ddb716972560394dabe25bf01ccf4933",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3372,
          "isSymlink": true,
          "description": "Multi search engine integration with 17 engines (8 CN + 9 Global). Supports advanced search operators, time filters, site search, privacy engines, and WolframAlpha knowledge queries. No API keys required."
        }
      ]
    },
    {
      "name": "myclaw-backup",
      "status": "linked",
      "hashes": [
        "f9b7b2947172cd65bf29c9957f7a305d5e92c678ffef0da460b8d4d564d01f58"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/myclaw-backup"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/myclaw-backup/SKILL.md",
          "relativePath": "myclaw-backup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/myclaw-backup",
          "hash": "f9b7b2947172cd65bf29c9957f7a305d5e92c678ffef0da460b8d4d564d01f58",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 7467,
          "isSymlink": true,
          "description": "Backup and restore all OpenClaw configuration, agent memory, skills, and workspace data. Part of the MyClaw.ai (https://myclaw.ai) open skills ecosystem — the AI personal assistant platform that gives every user a full server with complete code control. Use when the user wants to create a snapshot of their OpenClaw instance, schedule periodic backups, restore from a backup, migrate to a new server, download a backup file locally, upload a backup file from another machine, or protect against data loss. Includes a built-in HTTP server for browser-based download/upload/restore without needing cloud storage. TRUST BOUNDARY: This skill archives and restores highly sensitive data including bot tokens, API keys, and channel credentials. Only install if you trust the operator. Always use --dry-run before restore. Never start the HTTP server without a --token."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/myclaw-backup/SKILL.md",
          "relativePath": "myclaw-backup/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/myclaw-backup",
          "hash": "f9b7b2947172cd65bf29c9957f7a305d5e92c678ffef0da460b8d4d564d01f58",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 7467,
          "isSymlink": true,
          "description": "Backup and restore all OpenClaw configuration, agent memory, skills, and workspace data. Part of the MyClaw.ai (https://myclaw.ai) open skills ecosystem — the AI personal assistant platform that gives every user a full server with complete code control. Use when the user wants to create a snapshot of their OpenClaw instance, schedule periodic backups, restore from a backup, migrate to a new server, download a backup file locally, upload a backup file from another machine, or protect against data loss. Includes a built-in HTTP server for browser-based download/upload/restore without needing cloud storage. TRUST BOUNDARY: This skill archives and restores highly sensitive data including bot tokens, API keys, and channel credentials. Only install if you trust the operator. Always use --dry-run before restore. Never start the HTTP server without a --token."
        }
      ]
    },
    {
      "name": "n8n",
      "status": "linked",
      "hashes": [
        "fdb7645e0493a02a04944898af5af521499e33630426972a658b5b6e53fd5e75"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/n8n"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/n8n/SKILL.md",
          "relativePath": "n8n/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/n8n",
          "hash": "fdb7645e0493a02a04944898af5af521499e33630426972a658b5b6e53fd5e75",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 15027,
          "isSymlink": true,
          "description": "Manage n8n workflows and automations via API. Use when working with n8n workflows, executions, or automation tasks - listing workflows, activating/deactivating, checking execution status, manually triggering workflows, or debugging automation issues."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/n8n/SKILL.md",
          "relativePath": "n8n/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/n8n",
          "hash": "fdb7645e0493a02a04944898af5af521499e33630426972a658b5b6e53fd5e75",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 15027,
          "isSymlink": true,
          "description": "Manage n8n workflows and automations via API. Use when working with n8n workflows, executions, or automation tasks - listing workflows, activating/deactivating, checking execution status, manually triggering workflows, or debugging automation issues."
        }
      ]
    },
    {
      "name": "neat-freak",
      "status": "linked",
      "hashes": [
        "8ccbd3056aac36e8504fbb99dd507af4a9d9fe5451ed84f18a14f35c2975b0e0"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/neat-freak"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/neat-freak/SKILL.md",
          "relativePath": "neat-freak/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/neat-freak",
          "hash": "8ccbd3056aac36e8504fbb99dd507af4a9d9fe5451ed84f18a14f35c2975b0e0",
          "modifiedAt": "2026-04-29T10:05:34.168Z",
          "bytes": 10268,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/neat-freak/SKILL.md",
          "relativePath": "neat-freak/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/neat-freak",
          "hash": "8ccbd3056aac36e8504fbb99dd507af4a9d9fe5451ed84f18a14f35c2975b0e0",
          "modifiedAt": "2026-04-29T10:05:34.168Z",
          "bytes": 10268,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "codex",
          "family": "codex",
          "scope": "global",
          "path": "/Users/joker/.codex/skills/neat-freak/SKILL.md",
          "relativePath": "neat-freak/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/neat-freak",
          "hash": "8ccbd3056aac36e8504fbb99dd507af4a9d9fe5451ed84f18a14f35c2975b0e0",
          "modifiedAt": "2026-04-29T10:05:34.168Z",
          "bytes": 10268,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "obsidian",
      "status": "linked",
      "hashes": [
        "dc45b522a0f08fa11762b330b5355ccaca789bd645b0c450fe75026f69d728b2"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/obsidian"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/obsidian/SKILL.md",
          "relativePath": "obsidian/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian",
          "hash": "dc45b522a0f08fa11762b330b5355ccaca789bd645b0c450fe75026f69d728b2",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2334,
          "isSymlink": true,
          "description": "Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/obsidian/SKILL.md",
          "relativePath": "obsidian/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian",
          "hash": "dc45b522a0f08fa11762b330b5355ccaca789bd645b0c450fe75026f69d728b2",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 2334,
          "isSymlink": true,
          "description": "Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli."
        }
      ]
    },
    {
      "name": "obsidian-bases",
      "status": "linked",
      "hashes": [
        "769b27496cd3f9df91be7226a2e1aaca39b9cfe4b67f45defb60a9d22c4039eb"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/obsidian-bases"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/obsidian-bases/SKILL.md",
          "relativePath": "obsidian-bases/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian-bases",
          "hash": "769b27496cd3f9df91be7226a2e1aaca39b9cfe4b67f45defb60a9d22c4039eb",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 16441,
          "isSymlink": true,
          "description": "Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/obsidian-bases/SKILL.md",
          "relativePath": "obsidian-bases/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian-bases",
          "hash": "769b27496cd3f9df91be7226a2e1aaca39b9cfe4b67f45defb60a9d22c4039eb",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 16441,
          "isSymlink": true,
          "description": "Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/obsidian-bases/SKILL.md",
          "relativePath": "obsidian-bases/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian-bases",
          "hash": "769b27496cd3f9df91be7226a2e1aaca39b9cfe4b67f45defb60a9d22c4039eb",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 16441,
          "isSymlink": true,
          "description": "Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian."
        }
      ]
    },
    {
      "name": "obsidian-markdown",
      "status": "linked",
      "hashes": [
        "1c5686dd0dc11ff932f09203173e3d9fbbccfe3b7f9565c460ed1aa0bab8ed12"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/obsidian-markdown"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/obsidian-markdown/SKILL.md",
          "relativePath": "obsidian-markdown/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian-markdown",
          "hash": "1c5686dd0dc11ff932f09203173e3d9fbbccfe3b7f9565c460ed1aa0bab8ed12",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 10812,
          "isSymlink": true,
          "description": "Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/obsidian-markdown/SKILL.md",
          "relativePath": "obsidian-markdown/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian-markdown",
          "hash": "1c5686dd0dc11ff932f09203173e3d9fbbccfe3b7f9565c460ed1aa0bab8ed12",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 10812,
          "isSymlink": true,
          "description": "Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/obsidian-markdown/SKILL.md",
          "relativePath": "obsidian-markdown/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/obsidian-markdown",
          "hash": "1c5686dd0dc11ff932f09203173e3d9fbbccfe3b7f9565c460ed1aa0bab8ed12",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 10812,
          "isSymlink": true,
          "description": "Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes."
        }
      ]
    },
    {
      "name": "office-hours",
      "status": "linked",
      "hashes": [
        "bb297c94c371b292903d8a60e42c12da54f950027b3daf7b7949accfe0723b63"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/gstack-office-hours"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/gstack-office-hours/SKILL.md",
          "relativePath": "gstack-office-hours/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/gstack-office-hours",
          "hash": "bb297c94c371b292903d8a60e42c12da54f950027b3daf7b7949accfe0723b63",
          "modifiedAt": "2026-04-18T09:06:48.000Z",
          "bytes": 109268,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/gstack-office-hours/SKILL.md",
          "relativePath": "gstack-office-hours/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/gstack-office-hours",
          "hash": "bb297c94c371b292903d8a60e42c12da54f950027b3daf7b7949accfe0723b63",
          "modifiedAt": "2026-04-18T09:06:48.000Z",
          "bytes": 109268,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/gstack-office-hours/SKILL.md",
          "relativePath": "gstack-office-hours/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/gstack-office-hours",
          "hash": "bb297c94c371b292903d8a60e42c12da54f950027b3daf7b7949accfe0723b63",
          "modifiedAt": "2026-04-18T09:06:48.000Z",
          "bytes": 109268,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "opencli",
      "status": "linked",
      "hashes": [
        "733d57337c021ae126778dd3c04b210b58b94e08062fff01c7289a17433e2781"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/opencli"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/opencli/SKILL.md",
          "relativePath": "opencli/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/opencli",
          "hash": "733d57337c021ae126778dd3c04b210b58b94e08062fff01c7289a17433e2781",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 14246,
          "isSymlink": true,
          "description": "OpenCLI — Make any website your CLI. Zero risk, AI-powered, reuse Chrome login. 80+ commands across 19 sites."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/opencli/SKILL.md",
          "relativePath": "opencli/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/opencli",
          "hash": "733d57337c021ae126778dd3c04b210b58b94e08062fff01c7289a17433e2781",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 14246,
          "isSymlink": true,
          "description": "OpenCLI — Make any website your CLI. Zero risk, AI-powered, reuse Chrome login. 80+ commands across 19 sites."
        }
      ]
    },
    {
      "name": "parse-knowledge",
      "status": "linked",
      "hashes": [
        "704c43cde3fa446490b540292af5e6c23fd4fd892a8fbfb158d138c3dc441e31"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/parse-knowledge"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/parse-knowledge/SKILL.md",
          "relativePath": "parse-knowledge/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/parse-knowledge",
          "hash": "704c43cde3fa446490b540292af5e6c23fd4fd892a8fbfb158d138c3dc441e31",
          "modifiedAt": "2026-04-19T09:00:58.000Z",
          "bytes": 2168,
          "isSymlink": true,
          "description": "将非结构化文本整合到 OrbitOS 知识库结构中（领域 + Wiki）。当用户提供一段文本要求\"整理成笔记\"、\"存到知识库\"、\"提取知识点\"、\"结构化这段内容\"、\"把这段内容存起来\"或直接调用 /parse 时触发。主动识别文本中的核心概念并创建主笔记和原子概念，建立知识链接。分析文本所属领域（SoftwareEngineering、Finance、Health、Writing等），在 30_研究/ 创建主笔记，在 40_知识库/ 创建原子概念，使用 wikilink 建立关联关系。适用于将文档、笔记、对话等文本转化为结构化知识。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/parse-knowledge/SKILL.md",
          "relativePath": "parse-knowledge/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/parse-knowledge",
          "hash": "704c43cde3fa446490b540292af5e6c23fd4fd892a8fbfb158d138c3dc441e31",
          "modifiedAt": "2026-04-19T09:00:58.000Z",
          "bytes": 2168,
          "isSymlink": true,
          "description": "将非结构化文本整合到 OrbitOS 知识库结构中（领域 + Wiki）。当用户提供一段文本要求\"整理成笔记\"、\"存到知识库\"、\"提取知识点\"、\"结构化这段内容\"、\"把这段内容存起来\"或直接调用 /parse 时触发。主动识别文本中的核心概念并创建主笔记和原子概念，建立知识链接。分析文本所属领域（SoftwareEngineering、Finance、Health、Writing等），在 30_研究/ 创建主笔记，在 40_知识库/ 创建原子概念，使用 wikilink 建立关联关系。适用于将文档、笔记、对话等文本转化为结构化知识。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/parse-knowledge/SKILL.md",
          "relativePath": "parse-knowledge/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/parse-knowledge",
          "hash": "704c43cde3fa446490b540292af5e6c23fd4fd892a8fbfb158d138c3dc441e31",
          "modifiedAt": "2026-04-19T09:00:58.000Z",
          "bytes": 2168,
          "isSymlink": true,
          "description": "将非结构化文本整合到 OrbitOS 知识库结构中（领域 + Wiki）。当用户提供一段文本要求\"整理成笔记\"、\"存到知识库\"、\"提取知识点\"、\"结构化这段内容\"、\"把这段内容存起来\"或直接调用 /parse 时触发。主动识别文本中的核心概念并创建主笔记和原子概念，建立知识链接。分析文本所属领域（SoftwareEngineering、Finance、Health、Writing等），在 30_研究/ 创建主笔记，在 40_知识库/ 创建原子概念，使用 wikilink 建立关联关系。适用于将文档、笔记、对话等文本转化为结构化知识。"
        }
      ]
    },
    {
      "name": "proactive-agent",
      "status": "linked",
      "hashes": [
        "571521d9f6f38b3ec9f073d7bdec47170a35e9c78556954ac7f0f860ab12873b"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/proactive-agent"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/proactive-agent/SKILL.md",
          "relativePath": "proactive-agent/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/proactive-agent",
          "hash": "571521d9f6f38b3ec9f073d7bdec47170a35e9c78556954ac7f0f860ab12873b",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 20883,
          "isSymlink": true,
          "description": "Transform AI agents from task-followers into proactive partners that anticipate needs and continuously improve. Now with WAL Protocol, Working Buffer, Autonomous Crons, and battle-tested patterns. Part of the Hal Stack 🦞"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/proactive-agent/SKILL.md",
          "relativePath": "proactive-agent/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/proactive-agent",
          "hash": "571521d9f6f38b3ec9f073d7bdec47170a35e9c78556954ac7f0f860ab12873b",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 20883,
          "isSymlink": true,
          "description": "Transform AI agents from task-followers into proactive partners that anticipate needs and continuously improve. Now with WAL Protocol, Working Buffer, Autonomous Crons, and battle-tested patterns. Part of the Hal Stack 🦞"
        }
      ]
    },
    {
      "name": "prototype",
      "status": "linked",
      "hashes": [
        "0136715d021da251a4d13ad524e55d8dd10a1ddfb60bd183c1dae726ea79a68c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/prototype"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/prototype/SKILL.md",
          "relativePath": "prototype/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/prototype",
          "hash": "0136715d021da251a4d13ad524e55d8dd10a1ddfb60bd183c1dae726ea79a68c",
          "modifiedAt": "2026-06-06T14:56:12.080Z",
          "bytes": 3338,
          "isSymlink": true,
          "description": "Build a throwaway prototype to flesh out a design before committing to it. Routes between two branches — a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route. Use when the user wants to prototype, sanity-check a data model or state machine, mock up a UI, explore design options, or says \"prototype this\", \"let me play with it\", \"try a few designs\"."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/prototype/SKILL.md",
          "relativePath": "prototype/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/prototype",
          "hash": "0136715d021da251a4d13ad524e55d8dd10a1ddfb60bd183c1dae726ea79a68c",
          "modifiedAt": "2026-06-06T14:56:12.080Z",
          "bytes": 3338,
          "isSymlink": true,
          "description": "Build a throwaway prototype to flesh out a design before committing to it. Routes between two branches — a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route. Use when the user wants to prototype, sanity-check a data model or state machine, mock up a UI, explore design options, or says \"prototype this\", \"let me play with it\", \"try a few designs\"."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/prototype/SKILL.md",
          "relativePath": "prototype/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/prototype",
          "hash": "0136715d021da251a4d13ad524e55d8dd10a1ddfb60bd183c1dae726ea79a68c",
          "modifiedAt": "2026-06-06T14:56:12.080Z",
          "bytes": 3338,
          "isSymlink": true,
          "description": "Build a throwaway prototype to flesh out a design before committing to it. Routes between two branches — a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route. Use when the user wants to prototype, sanity-check a data model or state machine, mock up a UI, explore design options, or says \"prototype this\", \"let me play with it\", \"try a few designs\"."
        }
      ]
    },
    {
      "name": "pua",
      "status": "linked",
      "hashes": [
        "108bec91ba1e7433f795cbdd07e03bebefb6501d946fa73f873e6a9924734311"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/pua"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/pua/SKILL.md",
          "relativePath": "pua/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/pua",
          "hash": "108bec91ba1e7433f795cbdd07e03bebefb6501d946fa73f873e6a9924734311",
          "modifiedAt": "2026-04-10T17:16:05.000Z",
          "bytes": 26613,
          "isSymlink": true,
          "description": "Forces high-agency exhaustive problem-solving with corporate PUA pressure. Triggers on user frustration, repeated failures (2+), passive behavior, or quality complaints. Common triggers across Reddit/LinuxDo/HN/X: 'try harder', 'figure it out', 'stop giving up', 'you keep failing', '加油', '别偷懒', '你再试试', '为什么还不行', '你怎么又失败了', '你怎么搞的', '又错了', '能不能靠谱点', '认真点', '不行啊', '降智了', '你又在原地打转', '你把之前的改坏了', '别让我手动处理', '换个方法', 'stop spinning', 'you broke it', 'why does this still not work', 'this is the third time', '/pua', 'PUA模式'. Applies to ALL task types: code, config, debug, deploy, research."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/pua/SKILL.md",
          "relativePath": "pua/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/pua",
          "hash": "108bec91ba1e7433f795cbdd07e03bebefb6501d946fa73f873e6a9924734311",
          "modifiedAt": "2026-04-10T17:16:05.000Z",
          "bytes": 26613,
          "isSymlink": true,
          "description": "Forces high-agency exhaustive problem-solving with corporate PUA pressure. Triggers on user frustration, repeated failures (2+), passive behavior, or quality complaints. Common triggers across Reddit/LinuxDo/HN/X: 'try harder', 'figure it out', 'stop giving up', 'you keep failing', '加油', '别偷懒', '你再试试', '为什么还不行', '你怎么又失败了', '你怎么搞的', '又错了', '能不能靠谱点', '认真点', '不行啊', '降智了', '你又在原地打转', '你把之前的改坏了', '别让我手动处理', '换个方法', 'stop spinning', 'you broke it', 'why does this still not work', 'this is the third time', '/pua', 'PUA模式'. Applies to ALL task types: code, config, debug, deploy, research."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/pua/SKILL.md",
          "relativePath": "pua/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/pua",
          "hash": "108bec91ba1e7433f795cbdd07e03bebefb6501d946fa73f873e6a9924734311",
          "modifiedAt": "2026-04-10T17:16:05.000Z",
          "bytes": 26613,
          "isSymlink": true,
          "description": "Forces high-agency exhaustive problem-solving with corporate PUA pressure. Triggers on user frustration, repeated failures (2+), passive behavior, or quality complaints. Common triggers across Reddit/LinuxDo/HN/X: 'try harder', 'figure it out', 'stop giving up', 'you keep failing', '加油', '别偷懒', '你再试试', '为什么还不行', '你怎么又失败了', '你怎么搞的', '又错了', '能不能靠谱点', '认真点', '不行啊', '降智了', '你又在原地打转', '你把之前的改坏了', '别让我手动处理', '换个方法', 'stop spinning', 'you broke it', 'why does this still not work', 'this is the third time', '/pua', 'PUA模式'. Applies to ALL task types: code, config, debug, deploy, research."
        }
      ]
    },
    {
      "name": "qianchuan-launch-sop",
      "status": "linked",
      "hashes": [
        "adebab97d10677b5efbfc014acff5dbfdef6dcbfaafd05a1465f77e742a35d2c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/qianchuan-launch-sop"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/qianchuan-launch-sop/SKILL.md",
          "relativePath": "qianchuan-launch-sop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qianchuan-launch-sop",
          "hash": "adebab97d10677b5efbfc014acff5dbfdef6dcbfaafd05a1465f77e742a35d2c",
          "modifiedAt": "2026-04-30T04:44:44.869Z",
          "bytes": 25753,
          "isSymlink": true,
          "description": "Use when 用户要求在巨量千川/巨量全域投放里创建或续跑投放计划，尤其涉及复用 9222 浏览器登录态、本地视频上传、多视频素材补充、商品下架替换、以及自动发布。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/qianchuan-launch-sop/SKILL.md",
          "relativePath": "qianchuan-launch-sop/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qianchuan-launch-sop",
          "hash": "adebab97d10677b5efbfc014acff5dbfdef6dcbfaafd05a1465f77e742a35d2c",
          "modifiedAt": "2026-04-30T04:44:44.869Z",
          "bytes": 25753,
          "isSymlink": true,
          "description": "Use when 用户要求在巨量千川/巨量全域投放里创建或续跑投放计划，尤其涉及复用 9222 浏览器登录态、本地视频上传、多视频素材补充、商品下架替换、以及自动发布。"
        }
      ]
    },
    {
      "name": "qmd",
      "status": "linked",
      "hashes": [
        "c9b21461e1a444199c2e726ae32b4d2cabb848bdccb3160a2be8e9eb7b4f8c79"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/qmd"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/qmd/SKILL.md",
          "relativePath": "qmd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qmd",
          "hash": "c9b21461e1a444199c2e726ae32b4d2cabb848bdccb3160a2be8e9eb7b4f8c79",
          "modifiedAt": "2026-04-04T11:22:07.000Z",
          "bytes": 4079,
          "isSymlink": true,
          "description": "Search markdown knowledge bases, notes, and documentation using QMD. Use when users ask to search notes, find documents, or look up information."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/qmd/SKILL.md",
          "relativePath": "qmd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qmd",
          "hash": "c9b21461e1a444199c2e726ae32b4d2cabb848bdccb3160a2be8e9eb7b4f8c79",
          "modifiedAt": "2026-04-04T11:22:07.000Z",
          "bytes": 4079,
          "isSymlink": true,
          "description": "Search markdown knowledge bases, notes, and documentation using QMD. Use when users ask to search notes, find documents, or look up information."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/qmd/SKILL.md",
          "relativePath": "qmd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qmd",
          "hash": "c9b21461e1a444199c2e726ae32b4d2cabb848bdccb3160a2be8e9eb7b4f8c79",
          "modifiedAt": "2026-04-04T11:22:07.000Z",
          "bytes": 4079,
          "isSymlink": true,
          "description": "Search markdown knowledge bases, notes, and documentation using QMD. Use when users ask to search notes, find documents, or look up information."
        }
      ]
    },
    {
      "name": "qwen-image-edit",
      "status": "linked",
      "hashes": [
        "c57e22272fcfbbfa6d695445ebfaf29a194c307ac7e7b9ba36d54753692f8203"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/qwen-image-edit"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/qwen-image-edit/SKILL.md",
          "relativePath": "qwen-image-edit/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qwen-image-edit",
          "hash": "c57e22272fcfbbfa6d695445ebfaf29a194c307ac7e7b9ba36d54753692f8203",
          "modifiedAt": "2026-04-06T06:20:25.000Z",
          "bytes": 4067,
          "isSymlink": true,
          "description": "使用阿里云通义千问 Qwen-Image-2.0-Pro 进行图像编辑。支持多图输入、文本指令编辑、风格迁移、姿势调整等高级图像处理场景。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/qwen-image-edit/SKILL.md",
          "relativePath": "qwen-image-edit/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qwen-image-edit",
          "hash": "c57e22272fcfbbfa6d695445ebfaf29a194c307ac7e7b9ba36d54753692f8203",
          "modifiedAt": "2026-04-06T06:20:25.000Z",
          "bytes": 4067,
          "isSymlink": true,
          "description": "使用阿里云通义千问 Qwen-Image-2.0-Pro 进行图像编辑。支持多图输入、文本指令编辑、风格迁移、姿势调整等高级图像处理场景。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/qwen-image-edit/SKILL.md",
          "relativePath": "qwen-image-edit/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qwen-image-edit",
          "hash": "c57e22272fcfbbfa6d695445ebfaf29a194c307ac7e7b9ba36d54753692f8203",
          "modifiedAt": "2026-04-06T06:20:25.000Z",
          "bytes": 4067,
          "isSymlink": true,
          "description": "使用阿里云通义千问 Qwen-Image-2.0-Pro 进行图像编辑。支持多图输入、文本指令编辑、风格迁移、姿势调整等高级图像处理场景。"
        }
      ]
    },
    {
      "name": "qwen-tts",
      "status": "linked",
      "hashes": [
        "a4e0e18c41dfc1a2282cdfe38666b0f05e4c18507048536c7385467db341faaa"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/qwen-tts"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/qwen-tts/SKILL.md",
          "relativePath": "qwen-tts/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qwen-tts",
          "hash": "a4e0e18c41dfc1a2282cdfe38666b0f05e4c18507048536c7385467db341faaa",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5438,
          "isSymlink": true,
          "description": "阿里云百炼千问语音合成 (Qwen TTS)。支持 40+ 音色，默认输出 OPUS 格式（高压缩、高音质）。支持指令控制、声音复刻、声音设计。使用 DashScope API。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/qwen-tts/SKILL.md",
          "relativePath": "qwen-tts/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/qwen-tts",
          "hash": "a4e0e18c41dfc1a2282cdfe38666b0f05e4c18507048536c7385467db341faaa",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5438,
          "isSymlink": true,
          "description": "阿里云百炼千问语音合成 (Qwen TTS)。支持 40+ 音色，默认输出 OPUS 格式（高压缩、高音质）。支持指令控制、声音复刻、声音设计。使用 DashScope API。"
        }
      ]
    },
    {
      "name": "receiving-code-review",
      "status": "linked",
      "hashes": [
        "c9382e92b8f32363566068ecfed19d3b2651eaf40d3942b24840f839dedfc406"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/receiving-code-review"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/receiving-code-review/SKILL.md",
          "relativePath": "superpowers/receiving-code-review/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/receiving-code-review",
          "hash": "c9382e92b8f32363566068ecfed19d3b2651eaf40d3942b24840f839dedfc406",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6314,
          "isSymlink": false,
          "description": "Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/receiving-code-review/SKILL.md",
          "relativePath": "receiving-code-review/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/receiving-code-review",
          "hash": "c9382e92b8f32363566068ecfed19d3b2651eaf40d3942b24840f839dedfc406",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6314,
          "isSymlink": true,
          "description": "Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/receiving-code-review/SKILL.md",
          "relativePath": "receiving-code-review/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/receiving-code-review",
          "hash": "c9382e92b8f32363566068ecfed19d3b2651eaf40d3942b24840f839dedfc406",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6314,
          "isSymlink": true,
          "description": "Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation"
        }
      ]
    },
    {
      "name": "requesting-code-review",
      "status": "linked",
      "hashes": [
        "a5ff68586ccf62d1803cedeb71d60fd96ec05591d29c8d123196117eefd34cd0"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/requesting-code-review"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/requesting-code-review/SKILL.md",
          "relativePath": "superpowers/requesting-code-review/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/requesting-code-review",
          "hash": "a5ff68586ccf62d1803cedeb71d60fd96ec05591d29c8d123196117eefd34cd0",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 2935,
          "isSymlink": false,
          "description": "Use when completing tasks, implementing major features, or before merging to verify work meets requirements"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/requesting-code-review/SKILL.md",
          "relativePath": "requesting-code-review/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/requesting-code-review",
          "hash": "a5ff68586ccf62d1803cedeb71d60fd96ec05591d29c8d123196117eefd34cd0",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 2935,
          "isSymlink": true,
          "description": "Use when completing tasks, implementing major features, or before merging to verify work meets requirements"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/requesting-code-review/SKILL.md",
          "relativePath": "requesting-code-review/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/requesting-code-review",
          "hash": "a5ff68586ccf62d1803cedeb71d60fd96ec05591d29c8d123196117eefd34cd0",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 2935,
          "isSymlink": true,
          "description": "Use when completing tasks, implementing major features, or before merging to verify work meets requirements"
        }
      ]
    },
    {
      "name": "research",
      "status": "linked",
      "hashes": [
        "fdeee3fbef49f4a160d20ff4fdd14d9600fb2a314129958053c6a3621b67124a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/research"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/research/SKILL.md",
          "relativePath": "research/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/research",
          "hash": "fdeee3fbef49f4a160d20ff4fdd14d9600fb2a314129958053c6a3621b67124a",
          "modifiedAt": "2026-04-19T09:03:19.000Z",
          "bytes": 7056,
          "isSymlink": true,
          "description": "深度研究工作流，当用户想要深入研究技术、概念或复杂主题时使用。适用于 /research 命令、用户表达\"我想了解XXX\"、\"帮我研究XXX\"、\"深入探索XXX\"、\"XXX是怎么工作的\"、\"XXX的最佳实践是什么\"、\"XXX的核心概念是什么\"等意图时触发。使用两个独立Agent（规划Agent + 执行Agent）保持上下文新鲜，识别领域、搜索现有笔记、创建研究计划、生成主笔记和原子概念。主动识别需要深度研究的内容并提供系统化的研究方法。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/research/SKILL.md",
          "relativePath": "research/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/research",
          "hash": "fdeee3fbef49f4a160d20ff4fdd14d9600fb2a314129958053c6a3621b67124a",
          "modifiedAt": "2026-04-19T09:03:19.000Z",
          "bytes": 7056,
          "isSymlink": true,
          "description": "深度研究工作流，当用户想要深入研究技术、概念或复杂主题时使用。适用于 /research 命令、用户表达\"我想了解XXX\"、\"帮我研究XXX\"、\"深入探索XXX\"、\"XXX是怎么工作的\"、\"XXX的最佳实践是什么\"、\"XXX的核心概念是什么\"等意图时触发。使用两个独立Agent（规划Agent + 执行Agent）保持上下文新鲜，识别领域、搜索现有笔记、创建研究计划、生成主笔记和原子概念。主动识别需要深度研究的内容并提供系统化的研究方法。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/research/SKILL.md",
          "relativePath": "research/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/research",
          "hash": "fdeee3fbef49f4a160d20ff4fdd14d9600fb2a314129958053c6a3621b67124a",
          "modifiedAt": "2026-04-19T09:03:19.000Z",
          "bytes": 7056,
          "isSymlink": true,
          "description": "深度研究工作流，当用户想要深入研究技术、概念或复杂主题时使用。适用于 /research 命令、用户表达\"我想了解XXX\"、\"帮我研究XXX\"、\"深入探索XXX\"、\"XXX是怎么工作的\"、\"XXX的最佳实践是什么\"、\"XXX的核心概念是什么\"等意图时触发。使用两个独立Agent（规划Agent + 执行Agent）保持上下文新鲜，识别领域、搜索现有笔记、创建研究计划、生成主笔记和原子概念。主动识别需要深度研究的内容并提供系统化的研究方法。"
        }
      ]
    },
    {
      "name": "seedream",
      "status": "linked",
      "hashes": [
        "67c93236d724cadc20dbe16f5b0763cd83da2bef7880d38071445a33e068a8c9"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/seedream"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/seedream/SKILL.md",
          "relativePath": "seedream/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/seedream",
          "hash": "67c93236d724cadc20dbe16f5b0763cd83da2bef7880d38071445a33e068a8c9",
          "modifiedAt": "2026-04-06T06:20:21.000Z",
          "bytes": 5874,
          "isSymlink": true,
          "description": "使用火山引擎 Seedream-5.0 API 生成高质量图片。支持主题模板、批量生成、并发请求。适用于文生图场景，支持中英文提示词，可生成 2K/4K 高清图像。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/seedream/SKILL.md",
          "relativePath": "seedream/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/seedream",
          "hash": "67c93236d724cadc20dbe16f5b0763cd83da2bef7880d38071445a33e068a8c9",
          "modifiedAt": "2026-04-06T06:20:21.000Z",
          "bytes": 5874,
          "isSymlink": true,
          "description": "使用火山引擎 Seedream-5.0 API 生成高质量图片。支持主题模板、批量生成、并发请求。适用于文生图场景，支持中英文提示词，可生成 2K/4K 高清图像。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/seedream/SKILL.md",
          "relativePath": "seedream/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/seedream",
          "hash": "67c93236d724cadc20dbe16f5b0763cd83da2bef7880d38071445a33e068a8c9",
          "modifiedAt": "2026-04-06T06:20:21.000Z",
          "bytes": 5874,
          "isSymlink": true,
          "description": "使用火山引擎 Seedream-5.0 API 生成高质量图片。支持主题模板、批量生成、并发请求。适用于文生图场景，支持中英文提示词，可生成 2K/4K 高清图像。"
        }
      ]
    },
    {
      "name": "self-improvement",
      "status": "linked",
      "hashes": [
        "cec6d90543ea51c1ae2dfe09b7c0ac640b0a295101d34ba14c9deedc6607ce0c"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/self-improving-agent"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/self-improving-agent/SKILL.md",
          "relativePath": "self-improving-agent/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/self-improving-agent",
          "hash": "cec6d90543ea51c1ae2dfe09b7c0ac640b0a295101d34ba14c9deedc6607ce0c",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 19704,
          "isSymlink": true,
          "description": "Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User corrects Claude ('No, that's wrong...', 'Actually...'), (3) User requests a capability that doesn't exist, (4) An external API or tool fails, (5) Claude realizes its knowledge is outdated or incorrect, (6) A better approach is discovered for a recurring task. Also review learnings before major tasks."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/self-improving-agent/SKILL.md",
          "relativePath": "self-improving-agent/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/self-improving-agent",
          "hash": "cec6d90543ea51c1ae2dfe09b7c0ac640b0a295101d34ba14c9deedc6607ce0c",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 19704,
          "isSymlink": true,
          "description": "Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User corrects Claude ('No, that's wrong...', 'Actually...'), (3) User requests a capability that doesn't exist, (4) An external API or tool fails, (5) Claude realizes its knowledge is outdated or incorrect, (6) A better approach is discovered for a recurring task. Also review learnings before major tasks."
        }
      ]
    },
    {
      "name": "Self-Improving + Proactive Agent",
      "status": "linked",
      "hashes": [
        "11109b39d0f7fe7b98a9277609cb79c7ca67c86be1f98d13455d4da35c7047b0"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/self-improving"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/self-improving/SKILL.md",
          "relativePath": "self-improving/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/self-improving",
          "hash": "11109b39d0f7fe7b98a9277609cb79c7ca67c86be1f98d13455d4da35c7047b0",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 8582,
          "isSymlink": true,
          "description": "Self-reflection + Self-criticism + Self-learning + Self-organizing memory. Agent evaluates its own work, catches mistakes, and improves permanently. Use when (1) a command, tool, API, or operation fails; (2) the user corrects you or rejects your work; (3) you realize your knowledge is outdated or incorrect; (4) you discover a better approach; (5) the user explicitly installs or references the skill for the current task."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/self-improving/SKILL.md",
          "relativePath": "self-improving/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/self-improving",
          "hash": "11109b39d0f7fe7b98a9277609cb79c7ca67c86be1f98d13455d4da35c7047b0",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 8582,
          "isSymlink": true,
          "description": "Self-reflection + Self-criticism + Self-learning + Self-organizing memory. Agent evaluates its own work, catches mistakes, and improves permanently. Use when (1) a command, tool, API, or operation fails; (2) the user corrects you or rejects your work; (3) you realize your knowledge is outdated or incorrect; (4) you discover a better approach; (5) the user explicitly installs or references the skill for the current task."
        }
      ]
    },
    {
      "name": "short-drama-tts",
      "status": "linked",
      "hashes": [
        "b95868696dc20e8bc6de6ee7433d41c87f9093758fc3ece15749e0225027dd85"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/short-drama-tts"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/short-drama-tts/SKILL.md",
          "relativePath": "short-drama-tts/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/short-drama-tts",
          "hash": "b95868696dc20e8bc6de6ee7433d41c87f9093758fc3ece15749e0225027dd85",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3962,
          "isSymlink": true,
          "description": "短剧男女对话 TTS 生成工具。使用 ElevenLabs Nofish（男声）和 Bella（女声）两个音色，自动生成短剧风格的男女对话语音。支持对话脚本解析、批量生成、情感标签控制。适用于短视频短剧、广播剧、有声书等场景。Use when: (1) 需要生成短剧男女对话语音 (2) 需要将对话脚本转换为音频 (3) 需要批量生成角色语音 (4) 需要为短剧内容添加配音。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/short-drama-tts/SKILL.md",
          "relativePath": "short-drama-tts/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/short-drama-tts",
          "hash": "b95868696dc20e8bc6de6ee7433d41c87f9093758fc3ece15749e0225027dd85",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3962,
          "isSymlink": true,
          "description": "短剧男女对话 TTS 生成工具。使用 ElevenLabs Nofish（男声）和 Bella（女声）两个音色，自动生成短剧风格的男女对话语音。支持对话脚本解析、批量生成、情感标签控制。适用于短视频短剧、广播剧、有声书等场景。Use when: (1) 需要生成短剧男女对话语音 (2) 需要将对话脚本转换为音频 (3) 需要批量生成角色语音 (4) 需要为短剧内容添加配音。"
        }
      ]
    },
    {
      "name": "skill-creator",
      "status": "linked",
      "hashes": [
        "dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/skill-creator"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/skill-creator/SKILL.md",
          "relativePath": "skill-creator/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/skill-creator",
          "hash": "dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf",
          "modifiedAt": "2026-04-18T15:11:03.594Z",
          "bytes": 33168,
          "isSymlink": true,
          "description": "Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/skill-creator/SKILL.md",
          "relativePath": "skill-creator/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/skill-creator",
          "hash": "dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf",
          "modifiedAt": "2026-04-18T15:11:03.594Z",
          "bytes": 33168,
          "isSymlink": true,
          "description": "Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy."
        }
      ]
    },
    {
      "name": "skill-vetter",
      "status": "linked",
      "hashes": [
        "e8eb7583355c2ae78a79187dca6a1ec448d9c8360e91652871392179f7ffb8bf"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/skill-vetter"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/skill-vetter/SKILL.md",
          "relativePath": "skill-vetter/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/skill-vetter",
          "hash": "e8eb7583355c2ae78a79187dca6a1ec448d9c8360e91652871392179f7ffb8bf",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4561,
          "isSymlink": true,
          "description": "Security-first skill vetting for AI agents. Use before installing any skill from ClawdHub, GitHub, or other sources. Checks for red flags, permission scope, and suspicious patterns."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/skill-vetter/SKILL.md",
          "relativePath": "skill-vetter/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/skill-vetter",
          "hash": "e8eb7583355c2ae78a79187dca6a1ec448d9c8360e91652871392179f7ffb8bf",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4561,
          "isSymlink": true,
          "description": "Security-first skill vetting for AI agents. Use before installing any skill from ClawdHub, GitHub, or other sources. Checks for red flags, permission scope, and suspicious patterns."
        }
      ]
    },
    {
      "name": "start-my-day",
      "status": "linked",
      "hashes": [
        "47575b73b8ecb12cd052c87028d8c88d266efcc7fd802c545b572979e300588a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/start-my-day"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/start-my-day/SKILL.md",
          "relativePath": "start-my-day/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/start-my-day",
          "hash": "47575b73b8ecb12cd052c87028d8c88d266efcc7fd802c545b572979e300588a",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 5388,
          "isSymlink": true,
          "description": "Daily planning workflow - review yesterday, plan today, connect to active projects"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/start-my-day/SKILL.md",
          "relativePath": "start-my-day/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/start-my-day",
          "hash": "47575b73b8ecb12cd052c87028d8c88d266efcc7fd802c545b572979e300588a",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 5388,
          "isSymlink": true,
          "description": "Daily planning workflow - review yesterday, plan today, connect to active projects"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/start-my-day/SKILL.md",
          "relativePath": "start-my-day/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/start-my-day",
          "hash": "47575b73b8ecb12cd052c87028d8c88d266efcc7fd802c545b572979e300588a",
          "modifiedAt": "2026-04-03T16:47:38.000Z",
          "bytes": 5388,
          "isSymlink": true,
          "description": "Daily planning workflow - review yesterday, plan today, connect to active projects"
        }
      ]
    },
    {
      "name": "structured-context-compressor",
      "status": "linked",
      "hashes": [
        "1747e3a0333f7274d7881eb8523ee44541200a524dcdfe4e36085f7b71900599"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/structured-context-compressor"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/structured-context-compressor/SKILL.md",
          "relativePath": "structured-context-compressor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/structured-context-compressor",
          "hash": "1747e3a0333f7274d7881eb8523ee44541200a524dcdfe4e36085f7b71900599",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1308,
          "isSymlink": true,
          "description": "Compress a long agent conversation into a nine-part continuation summary that preserves request, files, errors, user messages, current work, and the next aligned step."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/structured-context-compressor/SKILL.md",
          "relativePath": "structured-context-compressor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/structured-context-compressor",
          "hash": "1747e3a0333f7274d7881eb8523ee44541200a524dcdfe4e36085f7b71900599",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1308,
          "isSymlink": true,
          "description": "Compress a long agent conversation into a nine-part continuation summary that preserves request, files, errors, user messages, current work, and the next aligned step."
        }
      ]
    },
    {
      "name": "subagent-driven-development",
      "status": "linked",
      "hashes": [
        "081ad3869e55c80bf8f890b4768a90c0e8057daf94b1b6fadebfc85ea5b8304a"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/subagent-driven-development"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/subagent-driven-development/SKILL.md",
          "relativePath": "superpowers/subagent-driven-development/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/subagent-driven-development",
          "hash": "081ad3869e55c80bf8f890b4768a90c0e8057daf94b1b6fadebfc85ea5b8304a",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 12139,
          "isSymlink": false,
          "description": "Use when executing implementation plans with independent tasks in the current session"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/subagent-driven-development/SKILL.md",
          "relativePath": "subagent-driven-development/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/subagent-driven-development",
          "hash": "081ad3869e55c80bf8f890b4768a90c0e8057daf94b1b6fadebfc85ea5b8304a",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 12139,
          "isSymlink": true,
          "description": "Use when executing implementation plans with independent tasks in the current session"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/subagent-driven-development/SKILL.md",
          "relativePath": "subagent-driven-development/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/subagent-driven-development",
          "hash": "081ad3869e55c80bf8f890b4768a90c0e8057daf94b1b6fadebfc85ea5b8304a",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 12139,
          "isSymlink": true,
          "description": "Use when executing implementation plans with independent tasks in the current session"
        }
      ]
    },
    {
      "name": "summarize",
      "status": "linked",
      "hashes": [
        "e7cdf499cee3e4ffefdbdca842b4716796cdd983b1f11e1314f295895eeb8161"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/summarize"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/summarize/SKILL.md",
          "relativePath": "summarize/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/summarize",
          "hash": "e7cdf499cee3e4ffefdbdca842b4716796cdd983b1f11e1314f295895eeb8161",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1425,
          "isSymlink": true,
          "description": "Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube)."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/summarize/SKILL.md",
          "relativePath": "summarize/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/summarize",
          "hash": "e7cdf499cee3e4ffefdbdca842b4716796cdd983b1f11e1314f295895eeb8161",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1425,
          "isSymlink": true,
          "description": "Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube)."
        }
      ]
    },
    {
      "name": "super-ocr",
      "status": "linked",
      "hashes": [
        "4415b21d356c615b3475d87432da5b4acee468154ffc41b25fccb79034dd20b0"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/super-ocr"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/super-ocr/SKILL.md",
          "relativePath": "super-ocr/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/super-ocr",
          "hash": "4415b21d356c615b3475d87432da5b4acee468154ffc41b25fccb79034dd20b0",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6342,
          "isSymlink": true,
          "description": "Production-grade OCR with intelligent engine selection. Tesseract (lightweight, fast) and PaddleOCR (high accuracy, Chinese-optimized). Use when extracting text from images, processing Chinese documents, needing confidence scores, or working with mixed Chinese/English content."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/super-ocr/SKILL.md",
          "relativePath": "super-ocr/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/super-ocr",
          "hash": "4415b21d356c615b3475d87432da5b4acee468154ffc41b25fccb79034dd20b0",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6342,
          "isSymlink": true,
          "description": "Production-grade OCR with intelligent engine selection. Tesseract (lightweight, fast) and PaddleOCR (high accuracy, Chinese-optimized). Use when extracting text from images, processing Chinese documents, needing confidence scores, or working with mixed Chinese/English content."
        }
      ]
    },
    {
      "name": "swarm-coordinator",
      "status": "linked",
      "hashes": [
        "ffdf1ee610cfbeac38968b44f2c99ac060d941c213c7f9713f7c79b9a4a7a192"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/swarm-coordinator"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/swarm-coordinator/SKILL.md",
          "relativePath": "swarm-coordinator/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/swarm-coordinator",
          "hash": "ffdf1ee610cfbeac38968b44f2c99ac060d941c213c7f9713f7c79b9a4a7a192",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1381,
          "isSymlink": true,
          "description": "Coordinate multiple agents by splitting work into research, synthesis, implementation, and verification, assigning ownership, and keeping the coordinator focused on integration rather than raw exploration."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/swarm-coordinator/SKILL.md",
          "relativePath": "swarm-coordinator/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/swarm-coordinator",
          "hash": "ffdf1ee610cfbeac38968b44f2c99ac060d941c213c7f9713f7c79b9a4a7a192",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 1381,
          "isSymlink": true,
          "description": "Coordinate multiple agents by splitting work into research, synthesis, implementation, and verification, assigning ownership, and keeping the coordinator focused on integration rather than raw exploration."
        }
      ]
    },
    {
      "name": "systematic-debugging",
      "status": "linked",
      "hashes": [
        "4999cb851360485eca5074e727bbdd62ef20549c5d5b01216fcbf5831badb473"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/systematic-debugging"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/systematic-debugging/SKILL.md",
          "relativePath": "superpowers/systematic-debugging/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/systematic-debugging",
          "hash": "4999cb851360485eca5074e727bbdd62ef20549c5d5b01216fcbf5831badb473",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 9884,
          "isSymlink": false,
          "description": "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/systematic-debugging/SKILL.md",
          "relativePath": "systematic-debugging/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/systematic-debugging",
          "hash": "4999cb851360485eca5074e727bbdd62ef20549c5d5b01216fcbf5831badb473",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 9884,
          "isSymlink": true,
          "description": "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/systematic-debugging/SKILL.md",
          "relativePath": "systematic-debugging/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/systematic-debugging",
          "hash": "4999cb851360485eca5074e727bbdd62ef20549c5d5b01216fcbf5831badb473",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 9884,
          "isSymlink": true,
          "description": "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes"
        }
      ]
    },
    {
      "name": "task-triage",
      "status": "linked",
      "hashes": [
        "06182179c6b25f07ec6ecbc2f6e43ce1364bddddc215d5b1b1068d0a23bf3c67"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/task-triage"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/task-triage/SKILL.md",
          "relativePath": "task-triage/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/task-triage",
          "hash": "06182179c6b25f07ec6ecbc2f6e43ce1364bddddc215d5b1b1068d0a23bf3c67",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 4483,
          "isSymlink": true,
          "description": "|-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/task-triage/SKILL.md",
          "relativePath": "task-triage/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/task-triage",
          "hash": "06182179c6b25f07ec6ecbc2f6e43ce1364bddddc215d5b1b1068d0a23bf3c67",
          "modifiedAt": "2026-04-11T13:45:35.000Z",
          "bytes": 4483,
          "isSymlink": true,
          "description": "|-"
        }
      ]
    },
    {
      "name": "tavily",
      "status": "linked",
      "hashes": [
        "c1c4f168eb62dc1b3b3da18186963419b5fac7f9e62c098c0ce3ace482060c7d"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/tavily-search"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/tavily-search/SKILL.md",
          "relativePath": "tavily-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/tavily-search",
          "hash": "c1c4f168eb62dc1b3b3da18186963419b5fac7f9e62c098c0ce3ace482060c7d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1195,
          "isSymlink": true,
          "description": "AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/tavily-search/SKILL.md",
          "relativePath": "tavily-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/tavily-search",
          "hash": "c1c4f168eb62dc1b3b3da18186963419b5fac7f9e62c098c0ce3ace482060c7d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 1195,
          "isSymlink": true,
          "description": "AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents."
        }
      ]
    },
    {
      "name": "tdd",
      "status": "linked",
      "hashes": [
        "83ace750c24ae70f1fb0933a7f7b7c51ec5d2d2e07334e1bb220d6d03ddb99de"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/tdd"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/tdd/SKILL.md",
          "relativePath": "tdd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/tdd",
          "hash": "83ace750c24ae70f1fb0933a7f7b7c51ec5d2d2e07334e1bb220d6d03ddb99de",
          "modifiedAt": "2026-06-06T14:56:12.080Z",
          "bytes": 6975,
          "isSymlink": true,
          "description": "Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions \"red-green-refactor\", wants integration tests, or asks for test-first development."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/tdd/SKILL.md",
          "relativePath": "tdd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/tdd",
          "hash": "83ace750c24ae70f1fb0933a7f7b7c51ec5d2d2e07334e1bb220d6d03ddb99de",
          "modifiedAt": "2026-06-06T14:56:12.080Z",
          "bytes": 6975,
          "isSymlink": true,
          "description": "Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions \"red-green-refactor\", wants integration tests, or asks for test-first development."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/tdd/SKILL.md",
          "relativePath": "tdd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/tdd",
          "hash": "83ace750c24ae70f1fb0933a7f7b7c51ec5d2d2e07334e1bb220d6d03ddb99de",
          "modifiedAt": "2026-06-06T14:56:12.080Z",
          "bytes": 6975,
          "isSymlink": true,
          "description": "Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions \"red-green-refactor\", wants integration tests, or asks for test-first development."
        }
      ]
    },
    {
      "name": "test-driven-development",
      "status": "linked",
      "hashes": [
        "7dee67b4af6bdccc7a914ca34533184d64592d0f5b23aeae631538168db14994"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/test-driven-development"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/test-driven-development/SKILL.md",
          "relativePath": "superpowers/test-driven-development/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/test-driven-development",
          "hash": "7dee67b4af6bdccc7a914ca34533184d64592d0f5b23aeae631538168db14994",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 9867,
          "isSymlink": false,
          "description": "Use when implementing any feature or bugfix, before writing implementation code"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/test-driven-development/SKILL.md",
          "relativePath": "test-driven-development/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/test-driven-development",
          "hash": "7dee67b4af6bdccc7a914ca34533184d64592d0f5b23aeae631538168db14994",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 9867,
          "isSymlink": true,
          "description": "Use when implementing any feature or bugfix, before writing implementation code"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/test-driven-development/SKILL.md",
          "relativePath": "test-driven-development/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/test-driven-development",
          "hash": "7dee67b4af6bdccc7a914ca34533184d64592d0f5b23aeae631538168db14994",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 9867,
          "isSymlink": true,
          "description": "Use when implementing any feature or bugfix, before writing implementation code"
        }
      ]
    },
    {
      "name": "thermo-nuclear-code-quality-review",
      "status": "linked",
      "hashes": [
        "7faca08b51b643b2ddd0836f92af15574444024685dcc1e677dbbb39ae8c9e8f"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/thermo-nuclear-code-quality-review"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/thermo-nuclear-code-quality-review/SKILL.md",
          "relativePath": "thermo-nuclear-code-quality-review/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/thermo-nuclear-code-quality-review",
          "hash": "7faca08b51b643b2ddd0836f92af15574444024685dcc1e677dbbb39ae8c9e8f",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 12437,
          "isSymlink": true,
          "description": "Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. Use for a thermo-nuclear code quality review, thermonuclear review, deep code quality audit, or especially harsh maintainability review."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/thermo-nuclear-code-quality-review/SKILL.md",
          "relativePath": "thermo-nuclear-code-quality-review/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/thermo-nuclear-code-quality-review",
          "hash": "7faca08b51b643b2ddd0836f92af15574444024685dcc1e677dbbb39ae8c9e8f",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 12437,
          "isSymlink": true,
          "description": "Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. Use for a thermo-nuclear code quality review, thermonuclear review, deep code quality audit, or especially harsh maintainability review."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/thermo-nuclear-code-quality-review/SKILL.md",
          "relativePath": "thermo-nuclear-code-quality-review/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/thermo-nuclear-code-quality-review",
          "hash": "7faca08b51b643b2ddd0836f92af15574444024685dcc1e677dbbb39ae8c9e8f",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 12437,
          "isSymlink": true,
          "description": "Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. Use for a thermo-nuclear code quality review, thermonuclear review, deep code quality audit, or especially harsh maintainability review."
        }
      ]
    },
    {
      "name": "to-issues",
      "status": "linked",
      "hashes": [
        "0e6a2973fa5bdf32570227c578f7e474d945dd9281615d31439664c3ef016fce"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/to-issues"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/to-issues/SKILL.md",
          "relativePath": "to-issues/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/to-issues",
          "hash": "0e6a2973fa5bdf32570227c578f7e474d945dd9281615d31439664c3ef016fce",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 3576,
          "isSymlink": true,
          "description": "Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/to-issues/SKILL.md",
          "relativePath": "to-issues/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/to-issues",
          "hash": "0e6a2973fa5bdf32570227c578f7e474d945dd9281615d31439664c3ef016fce",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 3576,
          "isSymlink": true,
          "description": "Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/to-issues/SKILL.md",
          "relativePath": "to-issues/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/to-issues",
          "hash": "0e6a2973fa5bdf32570227c578f7e474d945dd9281615d31439664c3ef016fce",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 3576,
          "isSymlink": true,
          "description": "Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues."
        }
      ]
    },
    {
      "name": "to-prd",
      "status": "linked",
      "hashes": [
        "21e7c0d430a360164b2db74411a5de1ae523859b8e16bd2fceee8a56d1838c9a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/to-prd"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/to-prd/SKILL.md",
          "relativePath": "to-prd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/to-prd",
          "hash": "21e7c0d430a360164b2db74411a5de1ae523859b8e16bd2fceee8a56d1838c9a",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 6671,
          "isSymlink": true,
          "description": "Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/to-prd/SKILL.md",
          "relativePath": "to-prd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/to-prd",
          "hash": "21e7c0d430a360164b2db74411a5de1ae523859b8e16bd2fceee8a56d1838c9a",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 6671,
          "isSymlink": true,
          "description": "Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/to-prd/SKILL.md",
          "relativePath": "to-prd/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/to-prd",
          "hash": "21e7c0d430a360164b2db74411a5de1ae523859b8e16bd2fceee8a56d1838c9a",
          "modifiedAt": "2026-06-06T14:56:12.081Z",
          "bytes": 6671,
          "isSymlink": true,
          "description": "Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context."
        }
      ]
    },
    {
      "name": "triage-sync",
      "status": "linked",
      "hashes": [
        "4307a9a3150b4b6852309945243f49161e3afde31bde1bfe55a5d48a803921ae"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/triage-sync"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/triage-sync/SKILL.md",
          "relativePath": "triage-sync/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/triage-sync",
          "hash": "4307a9a3150b4b6852309945243f49161e3afde31bde1bfe55a5d48a803921ae",
          "modifiedAt": "2026-04-29T14:51:18.000Z",
          "bytes": 7668,
          "isSymlink": true,
          "description": "处理微信同步助手内容，将原始聊天流水和公众号文章整理到知识库。当用户提到\"整理同步助手\"、\"归档微信记录\"、\"处理收件箱里的同步文件\"、\"整理公众号文章\"、\"处理微信同步内容\"或直接调用 /triage-sync 时触发。主动识别需要归档的微信内容并按 6 大分类（AI工程实践、AI产品与工具、AI商业与转型、知识管理、工作流与方法论、Agent技术）智能整理。从 00_收件箱/ 同步助手_*.md 提取精华群聊到 40_知识库/精华群聊/，从 笔记同步助手/YYYY-MM-DD/*.md 分类整理公众号文章到 40_知识库/精华文章/<category>/，归档源文件到 99_系统/归档/。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/triage-sync/SKILL.md",
          "relativePath": "triage-sync/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/triage-sync",
          "hash": "4307a9a3150b4b6852309945243f49161e3afde31bde1bfe55a5d48a803921ae",
          "modifiedAt": "2026-04-29T14:51:18.000Z",
          "bytes": 7668,
          "isSymlink": true,
          "description": "处理微信同步助手内容，将原始聊天流水和公众号文章整理到知识库。当用户提到\"整理同步助手\"、\"归档微信记录\"、\"处理收件箱里的同步文件\"、\"整理公众号文章\"、\"处理微信同步内容\"或直接调用 /triage-sync 时触发。主动识别需要归档的微信内容并按 6 大分类（AI工程实践、AI产品与工具、AI商业与转型、知识管理、工作流与方法论、Agent技术）智能整理。从 00_收件箱/ 同步助手_*.md 提取精华群聊到 40_知识库/精华群聊/，从 笔记同步助手/YYYY-MM-DD/*.md 分类整理公众号文章到 40_知识库/精华文章/<category>/，归档源文件到 99_系统/归档/。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/triage-sync/SKILL.md",
          "relativePath": "triage-sync/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/triage-sync",
          "hash": "4307a9a3150b4b6852309945243f49161e3afde31bde1bfe55a5d48a803921ae",
          "modifiedAt": "2026-04-29T14:51:18.000Z",
          "bytes": 7668,
          "isSymlink": true,
          "description": "处理微信同步助手内容，将原始聊天流水和公众号文章整理到知识库。当用户提到\"整理同步助手\"、\"归档微信记录\"、\"处理收件箱里的同步文件\"、\"整理公众号文章\"、\"处理微信同步内容\"或直接调用 /triage-sync 时触发。主动识别需要归档的微信内容并按 6 大分类（AI工程实践、AI产品与工具、AI商业与转型、知识管理、工作流与方法论、Agent技术）智能整理。从 00_收件箱/ 同步助手_*.md 提取精华群聊到 40_知识库/精华群聊/，从 笔记同步助手/YYYY-MM-DD/*.md 分类整理公众号文章到 40_知识库/精华文章/<category>/，归档源文件到 99_系统/归档/。"
        }
      ]
    },
    {
      "name": "twitter-openclaw",
      "status": "linked",
      "hashes": [
        "f037eae09b3a1525625d61928d0be8dcc345e24b38e7a27abbba4ba249940021"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/x-twitter"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/x-twitter/SKILL.md",
          "relativePath": "x-twitter/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-twitter",
          "hash": "f037eae09b3a1525625d61928d0be8dcc345e24b38e7a27abbba4ba249940021",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3958,
          "isSymlink": true,
          "description": "Interact with Twitter/X — read tweets, search, post, like, retweet, and manage your timeline."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/x-twitter/SKILL.md",
          "relativePath": "x-twitter/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-twitter",
          "hash": "f037eae09b3a1525625d61928d0be8dcc345e24b38e7a27abbba4ba249940021",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3958,
          "isSymlink": true,
          "description": "Interact with Twitter/X — read tweets, search, post, like, retweet, and manage your timeline."
        }
      ]
    },
    {
      "name": "ultimate-search",
      "status": "linked",
      "hashes": [
        "fba08bc8b3979fd8c66fdece43b9fb6e9cfb023450e316ffe6703ac59b307de3"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/ultimate-search"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/ultimate-search/SKILL.md",
          "relativePath": "ultimate-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ultimate-search",
          "hash": "fba08bc8b3979fd8c66fdece43b9fb6e9cfb023450e316ffe6703ac59b307de3",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 7066,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/ultimate-search/SKILL.md",
          "relativePath": "ultimate-search/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/ultimate-search",
          "hash": "fba08bc8b3979fd8c66fdece43b9fb6e9cfb023450e316ffe6703ac59b307de3",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 7066,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "using-git-worktrees",
      "status": "linked",
      "hashes": [
        "de9dcde34840eee074047ec327d4ea6ca4954c5a73a6d874dc48f25fe46c9e7c"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/using-git-worktrees"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/using-git-worktrees/SKILL.md",
          "relativePath": "superpowers/using-git-worktrees/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/using-git-worktrees",
          "hash": "de9dcde34840eee074047ec327d4ea6ca4954c5a73a6d874dc48f25fe46c9e7c",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 5635,
          "isSymlink": false,
          "description": "Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/using-git-worktrees/SKILL.md",
          "relativePath": "using-git-worktrees/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/using-git-worktrees",
          "hash": "de9dcde34840eee074047ec327d4ea6ca4954c5a73a6d874dc48f25fe46c9e7c",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 5635,
          "isSymlink": true,
          "description": "Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/using-git-worktrees/SKILL.md",
          "relativePath": "using-git-worktrees/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/using-git-worktrees",
          "hash": "de9dcde34840eee074047ec327d4ea6ca4954c5a73a6d874dc48f25fe46c9e7c",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 5635,
          "isSymlink": true,
          "description": "Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification"
        }
      ]
    },
    {
      "name": "using-superpowers",
      "status": "linked",
      "hashes": [
        "316e29381219adf0cac62190c67aeabf427d6e6e5f2735541d502b3d339be7aa"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/using-superpowers"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/using-superpowers/SKILL.md",
          "relativePath": "superpowers/using-superpowers/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/using-superpowers",
          "hash": "316e29381219adf0cac62190c67aeabf427d6e6e5f2735541d502b3d339be7aa",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 5421,
          "isSymlink": false,
          "description": "Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/using-superpowers/SKILL.md",
          "relativePath": "using-superpowers/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/using-superpowers",
          "hash": "316e29381219adf0cac62190c67aeabf427d6e6e5f2735541d502b3d339be7aa",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 5421,
          "isSymlink": true,
          "description": "Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/using-superpowers/SKILL.md",
          "relativePath": "using-superpowers/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/using-superpowers",
          "hash": "316e29381219adf0cac62190c67aeabf427d6e6e5f2735541d502b3d339be7aa",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 5421,
          "isSymlink": true,
          "description": "Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions"
        }
      ]
    },
    {
      "name": "verification-before-completion",
      "status": "linked",
      "hashes": [
        "ea52d15aabaf72bc6b558efe2c126f161b53961090ddcd712000273bfe8c7b6c"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/verification-before-completion"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/verification-before-completion/SKILL.md",
          "relativePath": "superpowers/verification-before-completion/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/verification-before-completion",
          "hash": "ea52d15aabaf72bc6b558efe2c126f161b53961090ddcd712000273bfe8c7b6c",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 4201,
          "isSymlink": false,
          "description": "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/verification-before-completion/SKILL.md",
          "relativePath": "verification-before-completion/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/verification-before-completion",
          "hash": "ea52d15aabaf72bc6b558efe2c126f161b53961090ddcd712000273bfe8c7b6c",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 4201,
          "isSymlink": true,
          "description": "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/verification-before-completion/SKILL.md",
          "relativePath": "verification-before-completion/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/verification-before-completion",
          "hash": "ea52d15aabaf72bc6b558efe2c126f161b53961090ddcd712000273bfe8c7b6c",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 4201,
          "isSymlink": true,
          "description": "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always"
        }
      ]
    },
    {
      "name": "verification-gate",
      "status": "linked",
      "hashes": [
        "c98841befcb488c38e5582e5dccf2131d6e5066292fa988ddf2425127e28bef4"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/verification-gate"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/verification-gate/SKILL.md",
          "relativePath": "verification-gate/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/verification-gate",
          "hash": "c98841befcb488c38e5582e5dccf2131d6e5066292fa988ddf2425127e28bef4",
          "modifiedAt": "2026-04-11T13:45:36.000Z",
          "bytes": 1205,
          "isSymlink": true,
          "description": "Run a read-only verification pass after implementation to check whether completion claims are real, validation actually ran, and obvious edge cases or regressions were missed."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/verification-gate/SKILL.md",
          "relativePath": "verification-gate/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/verification-gate",
          "hash": "c98841befcb488c38e5582e5dccf2131d6e5066292fa988ddf2425127e28bef4",
          "modifiedAt": "2026-04-11T13:45:36.000Z",
          "bytes": 1205,
          "isSymlink": true,
          "description": "Run a read-only verification pass after implementation to check whether completion claims are real, validation actually ran, and obvious edge cases or regressions were missed."
        }
      ]
    },
    {
      "name": "video-auto-clip",
      "status": "linked",
      "hashes": [
        "0c6f6bfc5dc89f66e6334eb7d4cc7d9f94061977a3e6a41c067bfc09fb3aae95"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/video-auto-clip"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/video-auto-clip/SKILL.md",
          "relativePath": "video-auto-clip/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-auto-clip",
          "hash": "0c6f6bfc5dc89f66e6334eb7d4cc7d9f94061977a3e6a41c067bfc09fb3aae95",
          "modifiedAt": "2026-04-24T05:19:23.305Z",
          "bytes": 24393,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/video-auto-clip/SKILL.md",
          "relativePath": "video-auto-clip/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-auto-clip",
          "hash": "0c6f6bfc5dc89f66e6334eb7d4cc7d9f94061977a3e6a41c067bfc09fb3aae95",
          "modifiedAt": "2026-04-24T05:19:23.305Z",
          "bytes": 24393,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "video-content-extractor",
      "status": "linked",
      "hashes": [
        "cd1052c2421d2ef34368e927bbf87f53a605589976ec3a9b26d28393add6132d"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/video-content-extractor"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/video-content-extractor/SKILL.md",
          "relativePath": "video-content-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-content-extractor",
          "hash": "cd1052c2421d2ef34368e927bbf87f53a605589976ec3a9b26d28393add6132d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5501,
          "isSymlink": true,
          "description": "视频/图片内容提取：视觉理解 + OCR。支持图片(JPG/PNG/WebP)和视频(MP4/MOV/AVI/MKV)，自动关键帧提取，PaddleOCR文字识别，多模态模型理解，结构化输出。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/video-content-extractor/SKILL.md",
          "relativePath": "video-content-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-content-extractor",
          "hash": "cd1052c2421d2ef34368e927bbf87f53a605589976ec3a9b26d28393add6132d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5501,
          "isSymlink": true,
          "description": "视频/图片内容提取：视觉理解 + OCR。支持图片(JPG/PNG/WebP)和视频(MP4/MOV/AVI/MKV)，自动关键帧提取，PaddleOCR文字识别，多模态模型理解，结构化输出。"
        }
      ]
    },
    {
      "name": "video-replication-sop-cy",
      "status": "linked",
      "hashes": [
        "f34f0637a968265c0c4ae3264af1de2a1957989cdb215dcb46a639f3fa62f67d"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/video-replication-sop-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/video-replication-sop-cy/SKILL.md",
          "relativePath": "video-replication-sop-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-replication-sop-cy",
          "hash": "f34f0637a968265c0c4ae3264af1de2a1957989cdb215dcb46a639f3fa62f67d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 20936,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/video-replication-sop-cy/SKILL.md",
          "relativePath": "video-replication-sop-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-replication-sop-cy",
          "hash": "f34f0637a968265c0c4ae3264af1de2a1957989cdb215dcb46a639f3fa62f67d",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 20936,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "video-screenplay-cy",
      "status": "linked",
      "hashes": [
        "372534c64ae7787800e2c8578f78faff936641d38eaa262d1bafe81966ec2aa8"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/video-screenplay-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/video-screenplay-cy/SKILL.md",
          "relativePath": "video-screenplay-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-screenplay-cy",
          "hash": "372534c64ae7787800e2c8578f78faff936641d38eaa262d1bafe81966ec2aa8",
          "modifiedAt": "2026-04-04T11:38:01.000Z",
          "bytes": 5046,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/video-screenplay-cy/SKILL.md",
          "relativePath": "video-screenplay-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-screenplay-cy",
          "hash": "372534c64ae7787800e2c8578f78faff936641d38eaa262d1bafe81966ec2aa8",
          "modifiedAt": "2026-04-04T11:38:01.000Z",
          "bytes": 5046,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/video-screenplay-cy/SKILL.md",
          "relativePath": "video-screenplay-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/video-screenplay-cy",
          "hash": "372534c64ae7787800e2c8578f78faff936641d38eaa262d1bafe81966ec2aa8",
          "modifiedAt": "2026-04-04T11:38:01.000Z",
          "bytes": 5046,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "videoagent-video-studio",
      "status": "linked",
      "hashes": [
        "d44a8eccb4db807633027f6a1dd1483f53eb33c01f97256f51d4d9edb9639dbb"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/videoagent-video-studio"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/videoagent-video-studio/SKILL.md",
          "relativePath": "videoagent-video-studio/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/videoagent-video-studio",
          "hash": "d44a8eccb4db807633027f6a1dd1483f53eb33c01f97256f51d4d9edb9639dbb",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6528,
          "isSymlink": true,
          "description": ">"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/videoagent-video-studio/SKILL.md",
          "relativePath": "videoagent-video-studio/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/videoagent-video-studio",
          "hash": "d44a8eccb4db807633027f6a1dd1483f53eb33c01f97256f51d4d9edb9639dbb",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6528,
          "isSymlink": true,
          "description": ">"
        }
      ]
    },
    {
      "name": "web-access",
      "status": "linked",
      "hashes": [
        "1ea896e6cc439e1c9311d568a8d116f9f8fc7e2b8d3bd5b9b9126ed9b3eec06a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/web-access"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/web-access/SKILL.md",
          "relativePath": "web-access/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/web-access",
          "hash": "1ea896e6cc439e1c9311d568a8d116f9f8fc7e2b8d3bd5b9b9126ed9b3eec06a",
          "modifiedAt": "2026-04-04T10:00:12.000Z",
          "bytes": 16010,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/web-access/SKILL.md",
          "relativePath": "web-access/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/web-access",
          "hash": "1ea896e6cc439e1c9311d568a8d116f9f8fc7e2b8d3bd5b9b9126ed9b3eec06a",
          "modifiedAt": "2026-04-04T10:00:12.000Z",
          "bytes": 16010,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/web-access/SKILL.md",
          "relativePath": "web-access/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/web-access",
          "hash": "1ea896e6cc439e1c9311d568a8d116f9f8fc7e2b8d3bd5b9b9126ed9b3eec06a",
          "modifiedAt": "2026-04-04T10:00:12.000Z",
          "bytes": 16010,
          "isSymlink": true,
          "description": ""
        }
      ]
    },
    {
      "name": "wechat-article-extractor",
      "status": "linked",
      "hashes": [
        "ce176674b6157ab8b5a69fde4dd9a8f8ab16a45916f07a58e77d0050309ac101"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/wechat-article-extractor"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/wechat-article-extractor/SKILL.md",
          "relativePath": "wechat-article-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-article-extractor",
          "hash": "ce176674b6157ab8b5a69fde4dd9a8f8ab16a45916f07a58e77d0050309ac101",
          "modifiedAt": "2026-04-11T13:45:36.000Z",
          "bytes": 4586,
          "isSymlink": true,
          "description": "Extract metadata and content from WeChat Official Account articles. Use when user needs to parse WeChat article URLs (mp.weixin.qq.com), extract article info (title, author, content, publish time, cover image), or convert WeChat articles to structured data. Supports various article types including posts, videos, images, voice messages, and reposts."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/wechat-article-extractor/SKILL.md",
          "relativePath": "wechat-article-extractor/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-article-extractor",
          "hash": "ce176674b6157ab8b5a69fde4dd9a8f8ab16a45916f07a58e77d0050309ac101",
          "modifiedAt": "2026-04-11T13:45:36.000Z",
          "bytes": 4586,
          "isSymlink": true,
          "description": "Extract metadata and content from WeChat Official Account articles. Use when user needs to parse WeChat article URLs (mp.weixin.qq.com), extract article info (title, author, content, publish time, cover image), or convert WeChat articles to structured data. Supports various article types including posts, videos, images, voice messages, and reposts."
        }
      ]
    },
    {
      "name": "wechat-mp-auto",
      "status": "linked",
      "hashes": [
        "c40d4807b65086e368062eff831e590093f274a4e1367c83b002d99dd871ffc8"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/wechat-mp-auto"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/wechat-mp-auto/SKILL.md",
          "relativePath": "wechat-mp-auto/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-mp-auto",
          "hash": "c40d4807b65086e368062eff831e590093f274a4e1367c83b002d99dd871ffc8",
          "modifiedAt": "2026-04-06T14:52:30.000Z",
          "bytes": 3900,
          "isSymlink": true,
          "description": "微信公众号自动化 — 将文章保存到草稿箱（支持 HTML 内容 + 封面图）"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/wechat-mp-auto/SKILL.md",
          "relativePath": "wechat-mp-auto/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-mp-auto",
          "hash": "c40d4807b65086e368062eff831e590093f274a4e1367c83b002d99dd871ffc8",
          "modifiedAt": "2026-04-06T14:52:30.000Z",
          "bytes": 3900,
          "isSymlink": true,
          "description": "微信公众号自动化 — 将文章保存到草稿箱（支持 HTML 内容 + 封面图）"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/wechat-mp-auto/SKILL.md",
          "relativePath": "wechat-mp-auto/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-mp-auto",
          "hash": "c40d4807b65086e368062eff831e590093f274a4e1367c83b002d99dd871ffc8",
          "modifiedAt": "2026-04-06T14:52:30.000Z",
          "bytes": 3900,
          "isSymlink": true,
          "description": "微信公众号自动化 — 将文章保存到草稿箱（支持 HTML 内容 + 封面图）"
        }
      ]
    },
    {
      "name": "wechat-typesetting-cy",
      "status": "linked",
      "hashes": [
        "ad81cf0d575f1e664b53925e038c57bdf7863548704ec6915b9988a6b0d785c1"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/wechat-typesetting-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/wechat-typesetting-cy/SKILL.md",
          "relativePath": "wechat-typesetting-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-typesetting-cy",
          "hash": "ad81cf0d575f1e664b53925e038c57bdf7863548704ec6915b9988a6b0d785c1",
          "modifiedAt": "2026-04-07T07:42:55.000Z",
          "bytes": 14175,
          "isSymlink": true,
          "description": "微信公众号文章多模板排版技能。将纯文本或Markdown转换为精美排版的HTML代码，支持多种视觉风格模板。当用户提到\"微信文章\"、\"公众号文章\"、\"发公众号\"、\"帮我排版\"、\"公众号排版\"、\"排版成微信格式\"、\"蓝色模板\"、\"暗黑模板\"、\"科技风排版\"时触发。"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/wechat-typesetting-cy/SKILL.md",
          "relativePath": "wechat-typesetting-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-typesetting-cy",
          "hash": "ad81cf0d575f1e664b53925e038c57bdf7863548704ec6915b9988a6b0d785c1",
          "modifiedAt": "2026-04-07T07:42:55.000Z",
          "bytes": 14175,
          "isSymlink": true,
          "description": "微信公众号文章多模板排版技能。将纯文本或Markdown转换为精美排版的HTML代码，支持多种视觉风格模板。当用户提到\"微信文章\"、\"公众号文章\"、\"发公众号\"、\"帮我排版\"、\"公众号排版\"、\"排版成微信格式\"、\"蓝色模板\"、\"暗黑模板\"、\"科技风排版\"时触发。"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/wechat-typesetting-cy/SKILL.md",
          "relativePath": "wechat-typesetting-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/wechat-typesetting-cy",
          "hash": "ad81cf0d575f1e664b53925e038c57bdf7863548704ec6915b9988a6b0d785c1",
          "modifiedAt": "2026-04-07T07:42:55.000Z",
          "bytes": 14175,
          "isSymlink": true,
          "description": "微信公众号文章多模板排版技能。将纯文本或Markdown转换为精美排版的HTML代码，支持多种视觉风格模板。当用户提到\"微信文章\"、\"公众号文章\"、\"发公众号\"、\"帮我排版\"、\"公众号排版\"、\"排版成微信格式\"、\"蓝色模板\"、\"暗黑模板\"、\"科技风排版\"时触发。"
        }
      ]
    },
    {
      "name": "writing-plans",
      "status": "linked",
      "hashes": [
        "90056bad3d5f196fa7c9fec0ffe592e6d9c86bc983e406642a51d1a4198b7024"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/writing-plans"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/writing-plans/SKILL.md",
          "relativePath": "superpowers/writing-plans/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/writing-plans",
          "hash": "90056bad3d5f196fa7c9fec0ffe592e6d9c86bc983e406642a51d1a4198b7024",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6046,
          "isSymlink": false,
          "description": "Use when you have a spec or requirements for a multi-step task, before touching code"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/writing-plans/SKILL.md",
          "relativePath": "writing-plans/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/writing-plans",
          "hash": "90056bad3d5f196fa7c9fec0ffe592e6d9c86bc983e406642a51d1a4198b7024",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6046,
          "isSymlink": true,
          "description": "Use when you have a spec or requirements for a multi-step task, before touching code"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/writing-plans/SKILL.md",
          "relativePath": "writing-plans/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/writing-plans",
          "hash": "90056bad3d5f196fa7c9fec0ffe592e6d9c86bc983e406642a51d1a4198b7024",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 6046,
          "isSymlink": true,
          "description": "Use when you have a spec or requirements for a multi-step task, before touching code"
        }
      ]
    },
    {
      "name": "writing-skills",
      "status": "linked",
      "hashes": [
        "38ba648975ae6ba512d6695676f146163db61a496b867f716f4bdfb0ee3aca3e"
      ],
      "realFolderPaths": [
        "/Users/joker/.agents/skills/superpowers/writing-skills"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/superpowers/writing-skills/SKILL.md",
          "relativePath": "superpowers/writing-skills/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/writing-skills",
          "hash": "38ba648975ae6ba512d6695676f146163db61a496b867f716f4bdfb0ee3aca3e",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 22624,
          "isSymlink": false,
          "description": "Use when creating new skills, editing existing skills, or verifying skills work before deployment"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/writing-skills/SKILL.md",
          "relativePath": "writing-skills/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/writing-skills",
          "hash": "38ba648975ae6ba512d6695676f146163db61a496b867f716f4bdfb0ee3aca3e",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 22624,
          "isSymlink": true,
          "description": "Use when creating new skills, editing existing skills, or verifying skills work before deployment"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/writing-skills/SKILL.md",
          "relativePath": "writing-skills/SKILL.md",
          "realFolderPath": "/Users/joker/.agents/skills/superpowers/writing-skills",
          "hash": "38ba648975ae6ba512d6695676f146163db61a496b867f716f4bdfb0ee3aca3e",
          "modifiedAt": "2026-04-12T09:22:42.000Z",
          "bytes": 22624,
          "isSymlink": true,
          "description": "Use when creating new skills, editing existing skills, or verifying skills work before deployment"
        }
      ]
    },
    {
      "name": "x-article-publisher",
      "status": "linked",
      "hashes": [
        "b915abb059ec61e071877dc1b4e51548ded792cbc4171f093fdd1968c828b340"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/x-article-publisher"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/x-article-publisher/SKILL.md",
          "relativePath": "x-article-publisher/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-article-publisher",
          "hash": "b915abb059ec61e071877dc1b4e51548ded792cbc4171f093fdd1968c828b340",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 24343,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/x-article-publisher/SKILL.md",
          "relativePath": "x-article-publisher/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-article-publisher",
          "hash": "b915abb059ec61e071877dc1b4e51548ded792cbc4171f093fdd1968c828b340",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 24343,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "x-reader",
      "status": "linked",
      "hashes": [
        "1bf1625a5a234a73f59eb68bfc6882446a87855c4ab13b3738d0497663660748"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/x-reader"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/x-reader/SKILL.md",
          "relativePath": "x-reader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-reader",
          "hash": "1bf1625a5a234a73f59eb68bfc6882446a87855c4ab13b3738d0497663660748",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3060,
          "isSymlink": true,
          "description": ""
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/x-reader/SKILL.md",
          "relativePath": "x-reader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/x-reader",
          "hash": "1bf1625a5a234a73f59eb68bfc6882446a87855c4ab13b3738d0497663660748",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 3060,
          "isSymlink": true,
          "description": ""
        }
      ]
    },
    {
      "name": "xhs-auth",
      "status": "linked",
      "hashes": [
        "5714a9945ef465c766e3f2de935cb89f1d6f45a24bc1af3e327a64fae8910171"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-auth"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-auto/skills/xhs-auth/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-auth/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-auth",
          "hash": "5714a9945ef465c766e3f2de935cb89f1d6f45a24bc1af3e327a64fae8910171",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6223,
          "isSymlink": false,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-auto/skills/xhs-auth/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-auth/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-auth",
          "hash": "5714a9945ef465c766e3f2de935cb89f1d6f45a24bc1af3e327a64fae8910171",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6223,
          "isSymlink": false,
          "description": "|"
        }
      ]
    },
    {
      "name": "xhs-auto-cy",
      "status": "linked",
      "hashes": [
        "70cd4b0b7d8116fdc277987e79810cfe639623ab4a71c63396b7dc3ab532081f"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xhs-auto-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xhs-auto-cy/SKILL.md",
          "relativePath": "xhs-auto-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xhs-auto-cy",
          "hash": "70cd4b0b7d8116fdc277987e79810cfe639623ab4a71c63396b7dc3ab532081f",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 7079,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xhs-auto-cy/SKILL.md",
          "relativePath": "xhs-auto-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xhs-auto-cy",
          "hash": "70cd4b0b7d8116fdc277987e79810cfe639623ab4a71c63396b7dc3ab532081f",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 7079,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "xhs-content-ops",
      "status": "linked",
      "hashes": [
        "f034419b37885ba67d2f08a19e2c36658dde0983f8536e15c67d4ba0eeabcf8a"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-content-ops"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-auto/skills/xhs-content-ops/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-content-ops/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-content-ops",
          "hash": "f034419b37885ba67d2f08a19e2c36658dde0983f8536e15c67d4ba0eeabcf8a",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6521,
          "isSymlink": false,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-auto/skills/xhs-content-ops/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-content-ops/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-content-ops",
          "hash": "f034419b37885ba67d2f08a19e2c36658dde0983f8536e15c67d4ba0eeabcf8a",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 6521,
          "isSymlink": false,
          "description": "|"
        }
      ]
    },
    {
      "name": "xhs-explore",
      "status": "linked",
      "hashes": [
        "22b9d28cd61e47bf549eb1cfee70634e317d91bbff2be92b8d52ae7c86a00d29"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-explore"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-auto/skills/xhs-explore/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-explore/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-explore",
          "hash": "22b9d28cd61e47bf549eb1cfee70634e317d91bbff2be92b8d52ae7c86a00d29",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5219,
          "isSymlink": false,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-auto/skills/xhs-explore/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-explore/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-explore",
          "hash": "22b9d28cd61e47bf549eb1cfee70634e317d91bbff2be92b8d52ae7c86a00d29",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5219,
          "isSymlink": false,
          "description": "|"
        }
      ]
    },
    {
      "name": "xhs-interact",
      "status": "linked",
      "hashes": [
        "4740b22b0bbc7d739bf54cfd7b8ffa28e837ad28d900f77b9fa2157350590e51"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-interact"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-auto/skills/xhs-interact/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-interact/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-interact",
          "hash": "4740b22b0bbc7d739bf54cfd7b8ffa28e837ad28d900f77b9fa2157350590e51",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4245,
          "isSymlink": false,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-auto/skills/xhs-interact/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-interact/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-interact",
          "hash": "4740b22b0bbc7d739bf54cfd7b8ffa28e837ad28d900f77b9fa2157350590e51",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4245,
          "isSymlink": false,
          "description": "|"
        }
      ]
    },
    {
      "name": "xhs-publish",
      "status": "linked",
      "hashes": [
        "686ea0a0f5a82bc2dd840565f32c28582ba4663a738e548ffee1daa9042c6a50"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-publish"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-auto/skills/xhs-publish/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-publish/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-publish",
          "hash": "686ea0a0f5a82bc2dd840565f32c28582ba4663a738e548ffee1daa9042c6a50",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 11533,
          "isSymlink": false,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-auto/skills/xhs-publish/SKILL.md",
          "relativePath": "xiaohongshu-auto/skills/xhs-publish/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto/skills/xhs-publish",
          "hash": "686ea0a0f5a82bc2dd840565f32c28582ba4663a738e548ffee1daa9042c6a50",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 11533,
          "isSymlink": false,
          "description": "|"
        }
      ]
    },
    {
      "name": "xianyu-reply-cy",
      "status": "linked",
      "hashes": [
        "e04a9f91ba195d570587b59ac8aa63b4facda42718d517bfc34735714d61d4db"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xianyu-reply-cy"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xianyu-reply-cy/SKILL.md",
          "relativePath": "xianyu-reply-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xianyu-reply-cy",
          "hash": "e04a9f91ba195d570587b59ac8aa63b4facda42718d517bfc34735714d61d4db",
          "modifiedAt": "2026-04-04T11:38:04.000Z",
          "bytes": 4918,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xianyu-reply-cy/SKILL.md",
          "relativePath": "xianyu-reply-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xianyu-reply-cy",
          "hash": "e04a9f91ba195d570587b59ac8aa63b4facda42718d517bfc34735714d61d4db",
          "modifiedAt": "2026-04-04T11:38:04.000Z",
          "bytes": 4918,
          "isSymlink": true,
          "description": ">-"
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/xianyu-reply-cy/SKILL.md",
          "relativePath": "xianyu-reply-cy/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xianyu-reply-cy",
          "hash": "e04a9f91ba195d570587b59ac8aa63b4facda42718d517bfc34735714d61d4db",
          "modifiedAt": "2026-04-04T11:38:04.000Z",
          "bytes": 4918,
          "isSymlink": true,
          "description": ">-"
        }
      ]
    },
    {
      "name": "xiaohongshu-downloader",
      "status": "linked",
      "hashes": [
        "010898f7f19809fc0f72818c88a98a3736ee8acb2a3b00cb75d7eed46ad3bebe"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-downloader"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-downloader/SKILL.md",
          "relativePath": "xiaohongshu-downloader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-downloader",
          "hash": "010898f7f19809fc0f72818c88a98a3736ee8acb2a3b00cb75d7eed46ad3bebe",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5803,
          "isSymlink": true,
          "description": "Download and summarize Xiaohongshu (小红书/RedNote) videos. Produces a full resource pack with video, audio, subtitles, transcript, and AI summary. This skill should be used when the user asks to \"download xiaohongshu video\", \"下载小红书视频\", \"save rednote video\", \"download from xiaohongshu\", \"小红书视频下载\", \"总结小红书视频\", \"summarize xiaohongshu video\", or mentions downloading/summarizing content from xiaohongshu.com or xhslink.com."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-downloader/SKILL.md",
          "relativePath": "xiaohongshu-downloader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-downloader",
          "hash": "010898f7f19809fc0f72818c88a98a3736ee8acb2a3b00cb75d7eed46ad3bebe",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 5803,
          "isSymlink": true,
          "description": "Download and summarize Xiaohongshu (小红书/RedNote) videos. Produces a full resource pack with video, audio, subtitles, transcript, and AI summary. This skill should be used when the user asks to \"download xiaohongshu video\", \"下载小红书视频\", \"save rednote video\", \"download from xiaohongshu\", \"小红书视频下载\", \"总结小红书视频\", \"summarize xiaohongshu video\", or mentions downloading/summarizing content from xiaohongshu.com or xhslink.com."
        }
      ]
    },
    {
      "name": "xiaohongshu-skills",
      "status": "linked",
      "hashes": [
        "e01604d830c13d92c568a8a6237d7071e04bc49cfe2217a8a466203789ab6a99"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/xiaohongshu-auto"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/xiaohongshu-auto/SKILL.md",
          "relativePath": "xiaohongshu-auto/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto",
          "hash": "e01604d830c13d92c568a8a6237d7071e04bc49cfe2217a8a466203789ab6a99",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4874,
          "isSymlink": true,
          "description": "|"
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/xiaohongshu-auto/SKILL.md",
          "relativePath": "xiaohongshu-auto/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/xiaohongshu-auto",
          "hash": "e01604d830c13d92c568a8a6237d7071e04bc49cfe2217a8a466203789ab6a99",
          "modifiedAt": "2026-04-08T16:40:35.000Z",
          "bytes": 4874,
          "isSymlink": true,
          "description": "|"
        }
      ]
    },
    {
      "name": "yt-dlp-downloader",
      "status": "linked",
      "hashes": [
        "d37357ff0ac8ebe080608f2a9c6c426c17058b7a4c19fbd767f0a0b6a0a2d324"
      ],
      "realFolderPaths": [
        "/Users/joker/agent-skills/shared/yt-dlp-downloader"
      ],
      "needsAction": false,
      "locations": [
        {
          "root": "agents",
          "family": "agents",
          "scope": "global",
          "path": "/Users/joker/.agents/skills/yt-dlp-downloader/SKILL.md",
          "relativePath": "yt-dlp-downloader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/yt-dlp-downloader",
          "hash": "d37357ff0ac8ebe080608f2a9c6c426c17058b7a4c19fbd767f0a0b6a0a2d324",
          "modifiedAt": "2026-04-04T11:27:27.000Z",
          "bytes": 6071,
          "isSymlink": true,
          "description": "Download videos from YouTube, Bilibili, Twitter, and thousands of other sites using yt-dlp. Use when the user provides a video URL and wants to download it, extract audio (MP3), download subtitles, or select video quality. Triggers on phrases like \"下载视频\", \"download video\", \"yt-dlp\", \"YouTube\", \"B站\", \"抖音\", \"提取音频\", \"extract audio\"."
        },
        {
          "root": "claude",
          "family": "claude",
          "scope": "global",
          "path": "/Users/joker/.claude/skills/yt-dlp-downloader/SKILL.md",
          "relativePath": "yt-dlp-downloader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/yt-dlp-downloader",
          "hash": "d37357ff0ac8ebe080608f2a9c6c426c17058b7a4c19fbd767f0a0b6a0a2d324",
          "modifiedAt": "2026-04-04T11:27:27.000Z",
          "bytes": 6071,
          "isSymlink": true,
          "description": "Download videos from YouTube, Bilibili, Twitter, and thousands of other sites using yt-dlp. Use when the user provides a video URL and wants to download it, extract audio (MP3), download subtitles, or select video quality. Triggers on phrases like \"下载视频\", \"download video\", \"yt-dlp\", \"YouTube\", \"B站\", \"抖音\", \"提取音频\", \"extract audio\"."
        },
        {
          "root": "vault-agents",
          "family": "agents",
          "scope": "JokerSu-knowledge",
          "path": "/Users/joker/Documents/JokerSu-knowledge/.agents/skills/yt-dlp-downloader/SKILL.md",
          "relativePath": "yt-dlp-downloader/SKILL.md",
          "realFolderPath": "/Users/joker/agent-skills/shared/yt-dlp-downloader",
          "hash": "d37357ff0ac8ebe080608f2a9c6c426c17058b7a4c19fbd767f0a0b6a0a2d324",
          "modifiedAt": "2026-04-04T11:27:27.000Z",
          "bytes": 6071,
          "isSymlink": true,
          "description": "Download videos from YouTube, Bilibili, Twitter, and thousands of other sites using yt-dlp. Use when the user provides a video URL and wants to download it, extract audio (MP3), download subtitles, or select video quality. Triggers on phrases like \"下载视频\", \"download video\", \"yt-dlp\", \"YouTube\", \"B站\", \"抖音\", \"提取音频\", \"extract audio\"."
        }
      ]
    }
  ]
};
