# Skill Control Center

本地优先的 Agent Skill 同步健康控制台，用来确认 Codex、Claude 和共享主库是否读取同一套技能。

## 页面重点

- 同步健康：一眼确认 Codex / Claude 是否一致。
- 异常队列：只显示冲突、实体重复、坏软链和内容不一致。
- 同步对比：列出 Codex-only、Claude-only、hash 不一致。
- watcher 状态：展示 LaunchAgent 是否安装、加载、监听中，以及最近一次运行日志。
- 技能库存：查看每个 skill 的入口、真实路径和建议动作。

## 更新数据

在 Obsidian 知识库根目录运行：

```bash
node tools/skill-manager/scripts/scan.mjs
```

然后打开：

```bash
open tools/skill-manager/index.html
```

## 自动同步

安装或刷新 macOS LaunchAgent watcher：

```bash
node tools/skill-manager/scripts/install-launchd.mjs --install
```

watcher 会监听：

```text
~/agent-skills/shared
~/.agents/skills
~/.claude/skills
~/.codex/skills
```

触发后会运行：

```bash
node tools/skill-manager/scripts/watch-sync.mjs --apply
```

它会先同步新技能，再确保 Claude 入口可以从 shared / Codex 主源恢复。

## 手动修复

补齐 Claude 软链接入口：

```bash
node tools/skill-manager/scripts/ensure-agent-links.mjs --apply
```

同步新安装的实体技能到 shared：

```bash
node tools/skill-manager/scripts/sync-new.mjs --apply
```

卸载 watcher：

```bash
node tools/skill-manager/scripts/install-launchd.mjs --uninstall
```

日志位置：

```text
~/agent-skills/logs/
```

## GitHub Pages

这个目录是纯静态页面，外网访问只需要发布 `tools/skill-manager` 目录。

注意：`data/report.js` 会包含本机技能名和本机路径。公开部署前要确认这些信息可以被外网看到。
