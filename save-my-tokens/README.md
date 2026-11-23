# save-my-tokens

Claude Code 每次开新会话，第一次请求都要带上内置工具说明、系统提示、skill 清单、规则文件（`CLAUDE.md` / `AGENTS.md`）和 MCP 工具说明。装得多了，一句「你好」就是几万 token，每开一个新会话都要重新带上。

save-my-tokens 是给 Claude Code 和 Codex 用的 skill。先跑本机脚本，量出这几万 token 怎么来的、装着的东西近 30 天用了几次；再由 agent 拿着报告逐项和你定去留，同意才改。

## 快速开始

安装到 Claude Code：

```bash
git clone https://github.com/suyuan2022/save-my-tokens ~/.claude/skills/save-my-tokens
```

新开会话输入 `/save-my-tokens`（只能手动触发，平时不占上下文）。只想看报告或回滚，直接跑脚本：

```bash
# 只读扫描（本机运行，不调模型）
python3 ~/.claude/skills/save-my-tokens/scripts/slim.py scan

# 退回最近一次改动
python3 ~/.claude/skills/save-my-tokens/scripts/slim.py rollback
```

卸载直接删 `~/.claude/skills/save-my-tokens`。

## 怎么工作

### 1. 本机脚本扫描

- **开局 token**：读 Claude Code 日志，看第一次请求实际带了多少 token 以及这五块各多大（实测，不是估算）。
- **近 30 天用量**：读 Claude Code 和 Codex 日志（含 `.jsonl.zst` 压缩旧日志），统计 skill、MCP server、subagent 调用次数；Claude Code 没用过但 Codex 在读的 skill 会标出。
- **规则与开关**：找规则文件重复（同会话一起加载、每次多带一遍，或 Claude Code 和 Codex 各读一份、不多花钱但可能走样），查超过上限 Codex 读不到的 `AGENTS.md`，以及写错或不生效的开关（类型不对、被环境变量覆盖、超范围、版本不支持）。
- **会话与子代理**：统计会话长度、缓存过期整段重算次数、子代理模型，用来定自动压缩窗口等设置。
- **官方审查**：查 `/doctor prompt-audit` 能不能用、卡在哪，及背后官方说明文件的本机位置。

### 2. agent 按 `SKILL.md` 逐项确认

- 「近 30 天 0 次调用」只是候选，发版、回滚这类几个月才用一次的 skill 单独标出。
- 旧模型写法、指向不存在文件或互相矛盾的规则，交给官方 `/doctor prompt-audit`。就算关了它依赖的内置 skill，agent 也直接读背后公开的官方说明文件照做，不动开关。
- 不估「省多少 token」，只报实测数：第一次请求 token、模型可见 skill 数、调用次数。改完新开会话再量一次对比。

### 一次实测

在构造配置（318 个 skill、大规则文件）上，用真实 Claude Code 2.1.321 测过：第一次请求 85,854 → 清理后 20,383 → 回滚后 85,854 token。这是构造配置的结果，不代表实际能省多少。

## 改动与回滚

- 改前把要动的路径原样存进 `~/.save-my-tokens/backups/<时间戳>/`，每次新建不覆盖旧备份，权限 `0700`（可能含凭据）。
- 改 `settings.json`、`config.toml` 由脚本按键写（单键或批量一次写回），改完重新解析并与改前逐项比对，确认只变了目标键才写回；agent 不读全文。
- 回滚后逐项校验 sha256。文件改完后若被别人动过，回滚会停下来问而不覆盖，被替换的版本另存一份。
- 不碰 `~/.claude.json`（Claude Code 随时在写的状态文件）、凭据和插件目录；不硬删任何东西，不装 hook，不留后台进程。往规则文件加内容（如子代理模型分工）前先给看改动，同意才加。

## 运行要求

- Python 3.9+，只用标准库，无需第三方包（macOS 自带 `python3` 够跑扫描和改 `settings.json`）。
- 改 Codex 的 `config.toml` 需 Python 3.11+。
- 读 Codex 的 `.jsonl.zst` 旧日志需 Python 3.14+ 或系统有 `zstd` 命令；都没有时，报告写明漏了多少文件。

## Windows 说明

还没在真实 Windows 上跑过，拿不准就不改：

- 只读扫描照常用；`python3` 换 `python` 或 `py -3`，路径换 `%USERPROFILE%\.claude\skills\save-my-tokens`。
- 每次备份前先在系统临时目录造假配置，走一遍备份、修改、回滚并核对一致；没过就拒绝改动、只出报告。可先跑 `python scripts\slim.py selftest` 检查（不碰真实配置）。
- 搬目录（`move`）在 Windows 关闭；要备份的路径是软链或目录联接也会拒绝。
- 带 BOM、CRLF 换行的文件改完保持原样；换行混用或非 UTF-8 不改。
- 通过 `CLAUDE_CONFIG_DIR`、`CODEX_HOME` 改过的配置目录会跟着读。
- 出问题欢迎提 issue，附上 `selftest` 输出。

## 已知限制

- 只在 macOS 上跑过。
- 开局实测只有 Claude Code 有，Codex 没有。分项明细依赖较新版本 Claude Code 日志（核过 2.1.321、2.1.326），旧版只出总数。
- Codex 的 skill 调用次数从「工具调用里读了某个 `SKILL.md`」推断，非官方计数。
- 意思相同、措辞不同的重复规则脚本找不到，靠 agent 读文件判断。
- 开关清单只收了核对过官方文档的二十几个键，键名和默认值随版本变，每条附出处和核对日期。
- 同名 skill 在用户级和项目级各装一份时，日志分不出实际用哪份。

## 目录与许可

```text
SKILL.md                  给 agent 看的流程
scripts/slim.py           扫描、备份、改单个键、回滚
references/switches.json  开关清单：默认值、说明、官方出处、核对日期
references/windows.md     在 Windows 上跑的注意事项
```

MIT，见 `LICENSE`。
