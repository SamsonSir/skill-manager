---
name: aeg-router
description: Mandatory entry for every software task created, dispatched, resumed, or coordinated through ORCA.
aeg-version: 2.0.0
---
Before ORCA creates or dispatches any software Run, Task, Worker, or Worktree, create or resume an AEG session and include its task ID in every worker prompt. Correlate ORCA run/task/worker/worktree ids through verified native receipts. Use `aeg coordinate operation --client orca` and ORCA's native Run/Task/Worker/Worktree surfaces. A launch response is not completion. Reconcile observed lifecycle, preserve dirty failed worktrees and fall back to topological single-Agent execution when ORCA is unavailable. The selected worker also loads its own mandatory global AEG entry (Codex global AGENTS or Grok global rule), so ORCA dispatch is checked at both coordinator and worker boundaries. AEG owns task state, contracts and gates; ORCA owns scheduling; project `AGENTS.md` owns project instructions.

## 默认工具路由

- 涉及飞书的读取、写入、Wiki、文档、表格、消息或其他操作，默认读取对应 Lark Skill 并使用 `lark-cli`，不另造飞书 API 客户端。
- 涉及 Playwright、浏览器自动化、网页交互测试或页面验收，默认读取 `ego-browser` Skill 并使用 `ego-browser`；仅在项目明确要求原生 Playwright 测试文件时保留 Playwright 作为项目测试依赖。
