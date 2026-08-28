# Kimi-Driven Partner Flow (Direction C)

> 本适配器是 partner-skill 的 Kimi 移植（fork 新增，上游只有 A/B 两个方向）。
> 使用场景：SKILL.md 由 Kimi Code CLI 加载，用户要求 Kimi 与 Codex 分工
> （"搭子"、"分工给 codex"、"让 codex 做"、"codex 后台跑"）。
> Kimi 是驾驶员：规划、拆分、质量门禁全部在 Kimi 会话内原生完成；
> Codex 是执行层：通过 `delegate-codex.sh` 后台 job 承担批量执行。
> 目标是省 Kimi 额度而不降质量——Phase 4 的全量审查门禁是保证这一点的核心。

所有辅助脚本在 `$PARTNER_DIR`（见 SKILL.md 的 Tool Location）。
Job 状态在 `<repo>/.partner/jobs/`。

## 与 Direction B（claude-driven）的本质区别

- Kimi **就是**规划者，不需要调用外部 claude CLI，因此：
  - 无 `run-claude-plan.py` / bounded-planning（那是给外部 Claude 进程套的边界）；
  - 无 Claude 会话监控（`references/monitoring.md` 的五信号中 1–4 全部不适用）；
  - receipt 中 `claude_session` 恒为 `none`，`monitoring_level` 恒为 `n/a`（若 schema 不允许则填 `unknown` 并在 Notes 说明）。
- 身份映射：`deep_reasoner` 由 Kimi 驾驶员内联承担（goal 表中身份列写 `-` 或 `kimi`），`fast_worker` 与 `arbiter` 走 `hosts.codex` 配置，经 `delegate-codex.sh` 执行。

## Phase 0 — Preflight

- 确认 Codex CLI：`codex --version`。macOS 上 PATH 里的 npm 版可能损坏（ENOENT），
  ChatGPT/Codex 应用内置 CLI 优先：`/Applications/ChatGPT.app/Contents/Resources/codex`。
  `delegate-codex.sh` 会自动优先发现它；失败则 `export PARTNER_CODEX_BIN=<路径>`。
- 检查目标仓库 `AGENTS.md` 是否含 `DO NOT send optional commentary`；
  没有则征求用户一次后追加（减少 Codex 水词）。不静默改用户仓库文件。
- `git status --short` 记录既有改动，便于之后隔离 Codex 的 diff。

## Phase 1 — Plan and Split（goal 文件）

- 将用户需求提炼为计划，写 `<repo>/.partner/goal.md`（模板 `references/goal-template.md`）。
  存在双宿主并发写风险时用 `scripts/goal-sync.py read`/`write --expect-sha256 <hash>`。
- 逐行判断身份：
  - `fast_worker`：机械、规格明确的工作（批量生成、广域只读扫描、文档生成、样板代码、批量迁移）——可委托的主体。
  - `arbiter`：仅用于盲解仲裁（见下）。
  - `-`（Kimi 内联）：架构、拆分决策本身、跨任务整合、安全/正确性关键路径、终验。
    永不为了省钱把这类工作路由给便宜身份，也永不让驾驶员干机械活。
- 对抗门禁：用 idea-king（点子王）对抗审查本次拆分，回答三个问题：
  每个被委托任务是否真不需要高档位？拆分边界的整合成本是否吃掉节省？
  每行身份是否匹配实际风险（并给出不是更高档的理由）？先修拆分再委托。

## Arbiter Protocol — 盲解仲裁

高风险或有争议的决策（用户说 仲裁 / 有争议 / second opinion，或驾驶员判断有分歧空间）：

1. **同一问题原文**分别给：`deep_reasoner`（Kimi 在会话内独立作答）和
   `arbiter`（`delegate-codex.sh --host codex --role arbiter`，可用 `--read-only`）。
2. **污染规则**：给 Codex 的 packet 不得含 Kimi 的答案、结论或倾向性暗示
   （"X 认为是 A，请验证" already contaminated）。被污染的轮次必须重跑。
3. 比对两份答案。一致 → 采纳并标注 dual-verified；不一致 → 驾驶员裁决，
   分歧点与裁决理由记入 receipt 的 Notes（`roles_used` 含双方）。
4. 跨厂商盲解最强（Kimi vs GPT 系天然满足）。

区别于 idea-king：点子王攻击**已有计划**；仲裁者是**独立重解同一问题**。

## Phase 2 — Delegate

- 按 `references/handoff-template.md` 的 Delegation Packet 构造 prompt：
  why-forward 上下文、一句话任务、可验证验收标准、范围约束、固定输出规则
  （no optional commentary；lessons learned 放最后）。
- 提交后台 job，`--host codex` 读取 `hosts.codex` 路由表：

```bash
prompt=$(mktemp)
# ... 写入 delegation packet ...
bash "$PARTNER_DIR/scripts/delegate-codex.sh" submit \
  --repo "$REPO" --prompt-file "$prompt" --label <task-id> \
  --host codex --role <identity>
```

- 只读扫描/审查类 job 加 `--read-only`。
- jobId 记入 goal 文件任务行；相互独立的任务并行提交。

## Phase 3 — Monitor

- 短任务（预期 <5 分钟）：阻塞等待
  `bash "$PARTNER_DIR/scripts/delegate-codex.sh" status <jobId> --repo "$REPO" --wait --timeout 300`。
- 长任务/多任务：用 Kimi 自己的 `Bash(run_in_background=true)` 轮询循环或
  `CronCreate` 定时检查替代 Claude 的 `/loop`：每 tick 跑
  `delegate-codex.sh status`，尾读 job 的 `log.jsonl` 最后事件，更新 goal 文件状态；
  无运行中 job 时停止循环，进 Phase 4。
- 连续两个 tick 无新 JSONL 事件或 status=FAILED → 监控异常：cancel，读
  `stderr.log`，修正 prompt 重提或由 Kimi 收回完成。异常记入 receipt。

## Phase 4 — Full Review Gate

- 收集结果：`delegate-codex.sh result <jobId> --repo "$REPO"`。
- Kimi 亲自审查完整 diff（`git diff` 限定在 job 触及的文件）+ 最快的相关检查。
  默认全量审查，不抽样。没读过的交付不接受。
- 对照 `.partner/goal.md` 的验收标准审，不是对照 diff 自洽性审——
  先重读任务 brief，再问"这个 diff 满足 brief 吗"。
- 有问题：一轮有边界的修复发回同一 Codex 会话
  `delegate-codex.sh resume <jobId> --repo "$REPO" --prompt-file <fix-notes>`。
- 每个任务最多两轮修复。仍失败：Kimi 收回完成，收回记入 goal 文件与 receipt。

## Phase 5 — Wrap Up

- goal 文件标记完成；停掉监控循环/cron。
- 出 Partner Session Receipt：`direction: kimi-driven`，`host: kimi`，
  `claude_session: none`，`codex_jobs: <数量>`；`roles_used` 从各 job 的
  meta 文件取 `role/model/effort`，`verified` 取 `partner-config.py resolve`，
  未验证的角色如实标 `verified: false`，不得省略。
- 跑 `references/memory-protocol.md`：记录委托了什么、Codex 在各任务类型上
  表现如何、返工轮数、effort 是否匹配——下一次拆分决策因此更聪明。
- 项目若另有 `ops/` 记忆体系（如本项目），把上述教训同时写回对应知识层文件。
