---
name: wx-cli
display_name: 微信数据查询 CLI（macOS）
display_name_en: WeChat Local Data Query CLI (macOS)
version: 1.0.0
description: |
  wx-cli is a WeChat macOS local database decryption and query CLI tool (pandorafuture/wx-cli). Use this skill when the user wants to query WeChat chat history, search chat keywords, view WeChat contacts, monitor new messages, decrypt WeChat images/voice/video, or deploy a local WeChat HTTP API.
description_zh: |
  wx-cli 是 macOS 上的微信本地数据库解密与查询 CLI 工具（pandorafuture/wx-cli）。
  让 Agent 能读取、搜索、订阅本地微信聊天记录。
  当用户要求查询微信聊天记录、搜索聊天关键词、查看微信联系人、监听新消息、
  解密微信图片/语音/视频、或部署本地微信 HTTP API 时使用此 skill。
  注意：仅支持 macOS（arm64 / Apple Silicon）+ 微信 4.1.7 及以上；密钥提取需关闭 SIP。
description_en: |
  wx-cli is a WeChat macOS local database decryption and query CLI tool (pandorafuture/wx-cli).
  It lets an Agent read, search and subscribe to local WeChat chat history.
  Use this skill when the user wants to query WeChat chat history, search chat keywords,
  view WeChat contacts, monitor new messages, decrypt WeChat images/voice/video, or deploy
  a local WeChat HTTP API.
  Note: macOS arm64 / Apple Silicon only; requires WeChat 4.1.7 or newer; SIP must be
  disabled for key extraction.
author: 拯救马铃薯
license: MIT
agent_created: true
---

# wx-cli — 微信本地数据查询工具

## Overview

wx-cli 直接读取 macOS 上的微信本地加密数据库，让 Agent 可以查询历史聊天、搜索关键词、获取联系人、解密图片/语音/视频，并通过 REST API 或 SSE 实时订阅新消息。数据默认留在本机，不上传聊天数据库，也不依赖云端导出。

**核心约束：仅 macOS（arm64 / Apple Silicon）+ 微信 4.1.7+。** 在 Windows/Linux 上此 skill 不可执行，只能作为知识参考；若用户环境不符，立即告知并停止操作。

## When to Use This Skill

触发场景：
- 用户问「最近跟谁聊了什么」「某人发过什么消息」「搜聊天记录里的关键词」
- 用户要查微信联系人、解密微信数据库/图片/语音/视频号视频
- 用户要在本地启动微信 HTTP API 服务供其他程序调用
- 用户要实时监听微信新消息（SSE / 轮询）
- 用户要把微信会话导出为 JSON / TXT
- 用户提到 wx-cli / 微信 / WeChat 数据查询相关需求

**不触发：** 仅做微信通用知识问答（无需本地数据）、发微信消息、解析别人导出的聊天截图、修改微信客户端行为。

## 前置条件（必须先确认）

密钥提取**需要 SIP 关闭**（SIP enabled 时 `task_for_pid` 被内核拒绝）。其余命令大多不需要 sudo。

```
csrutil status                     # 检查 SIP
sudo DevToolsSecurity -enable      # LLDB hook 所需
sudo dscl . append /Groups/_developer GroupMembership $USER
xcode-select --install             # 提供 lldb 与 python3
```

`scripts/install.sh` 与 `scripts/doctor.sh` 提供自动化检查/安装脚本。

## Quick Reference（命令速查）

| 需求 | 命令 |
|------|------|
| 当前账号状态 | `wx-cli status` |
| 前置条件检查 | `wx-cli doctor` / `wx-cli doctor --fix` |
| **提取完整数据库密钥（LLDB hook）** | `wx-cli key extract --timeout 120` |
| 手动设置数据库密钥 | `wx-cli key set <account> <64-hex-key>` |
| 手动设置图片密钥 | `wx-cli key set-image <account> <image-key>` |
| 查看已存密钥 | `wx-cli key list` |
| 解密数据库（自动） | `wx-cli decrypt` |
| 增量解密 | `wx-cli decrypt --incremental` |
| 解密图片（自动推导 V2 密钥）| `wx-cli decode-image <路径> -d <account_data_dir> -o output.png` |
| 批量解密图片目录 | `wx-cli decode-image /path/to/dat_dir/ -d <account_data_dir> -o /tmp/out/` |
| 提取语音为 MP3 | `wx-cli media extract-voice --media-dir <dir> <svr_id> -o voice.mp3` |
| 提取原始 SILK | `wx-cli media extract-voice --media-dir <dir> <svr_id> --raw -o voice.silk` |
| 解密视频号视频 | `wx-cli media decrypt-video <file> --seed 2105122989 -o video.mp4` |
| 最近会话列表 | `wx-cli sessions --limit 10` |
| 查看系统路径 | `wx-cli paths` / `wx-cli paths --json` |
| 搜索联系人 | `wx-cli contacts --search 张三` |
| 查某人的消息 | `wx-cli query 张三 --limit 20` |
| 全局关键词搜索 | `wx-cli search 周末 --limit 20` |
| 按类型过滤 | `wx-cli query 张三 --type text` |
| 时间范围过滤 | `wx-cli query 张三 --since 1772600000 --until 1772700000` |
| 锚点上下文查询 | `wx-cli query 张三 --around-sort-seq <seq> --context 10` |
| 增量拉取新消息 | `wx-cli query 张三 --after-sort-seq <seq> --limit 20` |
| 导出会话（TXT） | `wx-cli export 张三 -o /tmp/export/ --all` |
| 导出会话（JSON） | `wx-cli export 张三 -o /tmp/export/ --all --format json` |
| 忽略隐藏配置 | 加 `--show-hidden` |
| **启动 HTTP API（默认 127.0.0.1:9100）** | `wx-cli server run` |
| 远程访问（必须带 token） | `wx-cli server run --host 0.0.0.0 --token mysecret` |
| 服务管理 | `wx-cli server status\|stop\|restart` |
| 实时监听新消息 | `wx-cli watch` |
| 实时监听（轮询） | `wx-cli watch --poll --poll-ms 3000` |
| 实时监听（JSON 行） | `wx-cli watch --format json` |
| 实时监听（文件事件） | `wx-cli watch --fsnotify` |

**通用约定：** 所有查询命令加 `--format json` 获取结构化数据；默认 text 格式展示给用户。`--limit 0` 退回默认值。`--all` 上限 20,000 条。

## 标准工作流

### Step 0 — 确认环境

```bash
uname -m                      # 必须 arm64
sw_vers                       # macOS
csrutil status                # 密钥提取前必须 Disabled
wx-cli doctor                 # 检查 SIP / DevToolsSecurity / lldb / python3
```

若 `wx-cli` 不在 PATH，先跑 `scripts/install.sh`。

### Step 1 — 首次使用：提取密钥

```bash
wx-cli key extract --timeout 120   # LLDB hook，会自动重启 WeChat
wx-cli key list                    # 验证：raw=yes 表示已存完整数据库密钥
```

拿到完整数据库密钥后，`query` / `sessions` / `search` / `contacts` / `server run` / `watch` 可**直接读取加密数据库**，无需先 `decrypt`。如需明文副本再跑 `wx-cli decrypt`。

手动设置（已有密钥时）：

```bash
wx-cli key set <account_id> <32-byte-hex>          # 数据库密钥
wx-cli key set-image <account_id> <image-key>      # 图片 AES 密钥（V2）
```

### Step 2 — 查询 / 搜索

```bash
# 列出最近会话
wx-cli sessions --limit 10

# 搜索联系人（昵称/备注/wxid/手机号均支持模糊匹配）
wx-cli contacts --search 张三

# 查某人消息（时间倒序）
wx-cli query 张三 --limit 20
wx-cli query 张三 --format json --limit 50         # 结构化输出供程序处理

# 全局关键词搜索（用微信自带的全文索引，亚秒级）
wx-cli search 周末 --limit 20

# 群聊
wx-cli query 18819405230@chatroom --limit 10
wx-cli query "周末爬山群" --limit 10
```

### Step 3 — 高级查询（锚点 / 增量 / 时间窗）

```bash
# 定位某条消息前后 10 条（升序）
wx-cli query 张三 --around-sort-seq 1773421188000 --context 10
wx-cli query 张三 --around-server-id 5455993825313690274 --context 10

# 增量拉取（>=sort-seq 的新消息）
wx-cli query 张三 --after-sort-seq 1773421188000 --limit 20

# 时间窗（Unix 秒）
wx-cli query 张三 --since 1772600000 --until 1772700000
```

互斥规则：`around-*` 与 `since/until/all` 互斥；三个 `around-*` / `after-sort-seq` 互斥；锚点查询忽略 `--order`。

### Step 4 — 媒体解密

```bash
# 图片（推荐 -d 自动推导 V2 密钥）
wx-cli decode-image input.dat -d ~/Library/Containers/com.tencent.xinWeChat/Data/.../<account> -o output.png
# 批量目录
wx-cli decode-image /path/dat_dir/ -d <account_data_dir> -o /tmp/out/

# 语音（需 ffmpeg：brew install ffmpeg）
wx-cli media extract-voice --media-dir <dir> <svr_id> -o voice.mp3
# 原始 SILK（无需 ffmpeg）
wx-cli media extract-voice --media-dir <dir> <svr_id> --raw -o voice.silk

# 视频号视频
wx-cli media decrypt-video encrypted.bin --seed 2105122989 -o video.mp4
wx-cli media decrypt-video encrypted.bin --seed 0x7d844e8d -o video.mp4

# Hardlink 路径查询
wx-cli media resolve-path --db /path/hardlink.db <md5_key>
wx-cli media resolve-path --db /path/hardlink.db --media-type video <key>
```

### Step 5 — 实时订阅 / HTTP API

```bash
# CLI 实时监听
wx-cli watch
wx-cli watch --poll --poll-ms 3000        # 轮询模式
wx-cli watch --format json                # 每行一个 JSON 对象

# 启动 HTTP API（默认 127.0.0.1:9100）
wx-cli server run
wx-cli server run --host 0.0.0.0 --token mysecret   # 远程访问（必须 token）

# CLI 命令默认自动复用本机 server（探测 127.0.0.1:9100）
# 强制本地：--no-server；强制远程：--server-only；自定义：--server-url / --server-token
```

REST 端点：`/api/v1/health`、`/api/v1/sessions`、`/api/v1/contacts`、`/api/v1/messages`、`/api/v1/timeline`、`/api/v1/search`、`/api/v1/media`、`/api/v1/events`（SSE）。

- `/api/v1/timeline?since=<unix>&until=<unix>` 一次性拉取时间窗内**全部会话**的消息，适合记忆补全 / 归档 / 日报。
- `/api/v1/media` 图片响应携带 `X-Wechat-Media-Quality: full|thumbnail`，服务优先返回本机已下载的高清图。
- 当前 HTTP API **只读**，没有 send / reply / webhook。

### Step 6 — 导出会话

```bash
wx-cli export 张三 -o /tmp/export/ --all                        # TXT，时间正序（与 query 的 desc 默认相反）
wx-cli export 张三 -o /tmp/export/ --all --format json           # JSON
wx-cli export 张三 -o /tmp/export/ --all --no-media              # 跳过媒体
wx-cli export 张三 -o /tmp/export/ --all --show-emoji            # 表情细节
```

`--all` 会按批次拉完全部结果。

## 联系人隐藏规则（隐私）

配置文件：`~/Library/Application Support/wx-cli/config/settings.toml`

```toml
[accounts."<account_id>"]
ignore_contacts = ["wxid_xxx", "12345@chatroom"]
ignore_tags = ["同事", "客户"]
```

- `query` / `sessions` / `contacts` / `export` / `watch` 默认应用隐藏规则；加 `--show-hidden` 查看全部
- `search` 当前**不会自动应用隐藏配置**，且没有 `--show-hidden`
- **隐私优先：** 输出里出现 `[消息已隐藏]` 时，除非用户明确要求，不主动追加 `--show-hidden`

## 错误自动恢复

| 症状 | 修复 |
|------|------|
| `error: no key for account <account_id>` | `wx-cli status` → `wx-cli key extract --timeout 120` → `wx-cli key list` → 重试 |
| `task_for_pid failed (kern_return=5)` | SIP 仍 enabled，需在 Recovery Mode 执行 `csrutil disable` |
| `warning: ffmpeg not found` | `brew install ffmpeg`，或用 `FFMPEG_PATH=/path/ffmpeg` 启动 |
| 解密后数据库无法打开 | `wx-cli key list` 确认密钥；`wx-cli info <db>` 检查加密状态；确认微信 ≥ 4.1.7 |
| 查询返回空 | 见下文「诊断策略」 |

## 诊断策略（查询为空时）

**不要反复换参数重试**，按顺序：

```bash
# 1. 看 stats.skipped
wx-cli query <contact> --all --format json 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'items={len(d[\"items\"])}, skipped={d[\"stats\"][\"skipped\"]}')"

# 2. skipped > 0 → 重新解密
wx-cli decrypt

# 3. items=0 且 skipped=0 → 检查联系人
wx-cli contacts --search <name> --format json
```

## JSON 输出结构（统一信封）

```json
{
  "items": [...],
  "paging": { "offset": 0, "limit": 20, "returned": 20, "total": 103, "has_more": true },
  "stats": { "scanned": 103, "skipped": 0, "elapsed_ms": 3 }
}
```

| 命令 | item 关键字段 |
|------|---------------|
| sessions | `username`, `display_name`, `avatar_url?`, `summary`, `sort_timestamp`, `direction?` |
| query | `sort_seq`, `server_id`, `msg_type`, `sender`, `content`, `direction` |
| timeline API | `sort_seq`, `server_id`, `msg_type`, `sender`, `talker`, `talker_display_name`, `create_time`, `direction`, `snippet` |
| contacts | `user_name`, `alias`, `remark`, `nick_name`, `avatar_url?`, `phone`, `labels` |
| search | `server_id`, `talker`, `sender`, `snippet`, `hit_type` |

**易混淆：**
- contacts 用 `user_name`（下划线）；sessions 用 `username`（无下划线）
- `avatar_url` 缺头像记录时省略；message 的 `sender` 才是 self/other 判断依据
- `/api/v1/health` 的 `current_account.wxid` 是「我发的」的主事实源

**程序化使用：** JSON 走 stdout，诊断信息走 stderr，必须分离：

```bash
OUTPUT=$(wx-cli query 张三 --format json --limit 5)
echo "$OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['items']))"
```

## 消息类型标签（type=49 结构化解析）

| 变体 | sub_type | 输出 |
|------|---------|------|
| Link | 4, 5, 7, 92 | `[链接] <标题>` |
| File | 6 | `[文件] <文件名>` |
| MiniProgram | 33, 36 | `[小程序] <名称>` |
| MergedMessages | 19 | `[聊天记录] <标题>` |
| Quote | 57 | `[引用 @发送者: 原文] 回复文本` |
| Transfer | 2000 | `[转账] ¥金额` |
| RedEnvelope | 2001, 2003 | `[红包] <标题>` |
| ChannelVideo | 51, 63 | `[视频号] <标题>` |
| Pat | 62 | `[拍一拍]` |

JSON `content` 字段是 tagged union：外层 key 是变体名，值是结构化字段。

## 文件路径（macOS）

| 类别 | 路径 | 用途 | 可删？ |
|------|------|------|------|
| Config | `~/Library/Application Support/wx-cli/config/` | 密钥、设置 | 否（先备份） |
| Cache | `~/Library/Caches/wx-cli/` | 解密后数据库 | 可（重 decrypt 重建） |
| State | `~/Library/Application Support/wx-cli/state/` | 服务运行时元数据 | 可 |
| Logs | `~/Library/Logs/wx-cli/` | 服务日志 | 可 |
| Temp | `$TMPDIR/wx-cli/` | 密钥提取临时文件 | 可 |

清理缓存：`rm -rf ~/Library/Caches/wx-cli/`。完整路径查询：`wx-cli paths --json`。

## 安装与构建

### 一键安装（二进制）

```bash
bash scripts/install.sh
```

脚本从 GitHub Releases 拉取最新 macOS arm64 二进制，部署到 `~/.local/bin/wx-cli` 并写入 PATH 提示。

### 从源码编译（需要 Rust 工具链）

本 skill 仅打包 macOS arm64 预编译二进制。如需自行编译，请访问官方仓库：

```bash
git clone https://github.com/pandorafuture/wx-cli.git
cd wx-cli
cargo build --release
cp target/release/wx-cli ~/.local/bin/
```

### 拉取 npx skills（Claude Code / Codex / Cursor）

```bash
npx skills add pandorafuture/wx-cli
```

## Bundled Resources

### `scripts/`
- `install.sh` — 一键安装（从 GitHub Releases 拉取预编译 macOS arm64 二进制）
- `doctor.sh` — 环境前置条件检查（SIP / DevToolsSecurity / lldb / python3 / ffmpeg）

### `references/`
- `agent-skill.md` — 项目仓库自带的完整 Agent SKILL.md（含 JSON 字段、消息类型变体、REST 端点详情等深度参考）

## 注意事项

- **仅 macOS arm64**：在 Windows / Linux 上命令无法执行，应立即告知用户并停止；本 skill 在非 macOS 环境下只能作为「知识库」提供参考
- WeChat 版本必须 ≥ 4.1.7
- 密钥提取 `key extract` 会重启 WeChat 进程（通过 LLDB hook 捕获 PBKDF2 调用），不需 sudo
- `query` / `sessions` / `contacts` / `export` / `watch` 默认应用隐藏配置；`search` 不应用
- 所有命令自动检测账号和密钥，通常无需 `--account` / `--key`
- 当前 HTTP API **只读**（无 send / reply / webhook）
- 命令执行失败时优先看 stderr，而非反复重试

## 上游与许可

- 项目：https://github.com/pandorafuture/wx-cli
- 许可证：MIT（见 `LICENSE`）
- 本 WorkBuddy skill 由「拯救马铃薯」封装，保留原项目所有版权与许可