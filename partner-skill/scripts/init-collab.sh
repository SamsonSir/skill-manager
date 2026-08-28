#!/usr/bin/env bash
# init-collab.sh — 在任意仓库一键初始化三角色协作骨架
# 用法: bash init-collab.sh <repo路径>
# 幂等：已存在的 AGENTS.md 只追加缺失的协议节；PROGRESS.md 不覆盖。
set -euo pipefail

REPO="${1:?用法: init-collab.sh <repo路径>}"
[ -d "$REPO" ] || { echo "错误：目录不存在 $REPO"; exit 1; }

PROTOCOL='## 协作协议（新会话默认遵守，无需触发词）

任何 agent 进入本仓库，默认进入三角色协作模式：

- **人工（Owner / 最终验收）**：定方向、拍板、终验；独占授权
  （git push、真实发布、删除受保护模块、生产变更）。
- **Kimi（任务架构师）**：方案与架构、任务拆解、写任务包
  （.partner/*-packet.md，含边界与可复跑验收标准）、派单监工、
  全量核验（PROGRESS.md 执行记录 + 完整 diff + 亲自复跑验收命令），
  核验通过交人工终验；打回每任务最多两轮，仍败收回自做。
- **Codex（执行 agent）**：按任务包边界施工，完成后把执行过程与
  测试结果写入 PROGRESS.md（改动文件、命令与结果、自验证据、遗留问题）。

流程：人工+Kimi 定方案 → Kimi 拆解出任务包 → Codex 施工并留痕 →
Kimi 核验 → 人工终验。Codex 额度耗尽时 Kimi 收回或暂停，核验标准不降级。'

PROGRESS='# PROGRESS.md — 执行留痕与验收记录

> 唯一留痕处。Codex（执行）完成任务后追加「执行记录」（最新置顶）；
> Kimi（架构师）核验后写「核验意见」；人工（Owner）终验签字。

## 执行记录
'

# 1) AGENTS.md：有则补协议节（幂等），无则新建
if [ -f "$REPO/AGENTS.md" ]; then
  if grep -q "协作协议" "$REPO/AGENTS.md"; then
    echo "AGENTS.md 已含协作协议节，跳过"
  else
    printf '\n\n%s\n' "$PROTOCOL" >> "$REPO/AGENTS.md"
    echo "AGENTS.md 已追加协作协议节"
  fi
else
  printf '# AGENTS.md\n\nDO NOT send optional commentary.\n\n%s\n' "$PROTOCOL" > "$REPO/AGENTS.md"
  echo "AGENTS.md 已创建"
fi

# 2) PROGRESS.md：不覆盖
if [ -f "$REPO/PROGRESS.md" ]; then
  echo "PROGRESS.md 已存在，跳过"
else
  printf '%s' "$PROGRESS" > "$REPO/PROGRESS.md"
  echo "PROGRESS.md 已创建"
fi

# 3) .partner 目录
mkdir -p "$REPO/.partner"
echo ".partner/ 已就绪"
echo "完成：$REPO 协作骨架初始化完毕"
