# 来源与本地适配

- 上游：`hoodini/ai-agents-skills` 的 `skills/github-trending/SKILL.md`
- 地址：https://github.com/hoodini/ai-agents-skills/tree/master/skills/github-trending
- 安装方式：只引入单个 Skill，不运行上游安装脚本。
- 本地用途：按自然语言或定时任务生成 GitHub Trending 中文整理。
- 网络范围：GitHub Trending 页面或 GitHub Search API；`GITHUB_TOKEN` 为可选项。
- 输出要求：中文、去重、说明项目用途与适合 Joker 的原因，不展示 Planning 或工具日志。
