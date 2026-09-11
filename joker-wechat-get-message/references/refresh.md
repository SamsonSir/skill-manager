# 可读快照刷新

活微信的 `message_*.db` 是 SQLCipher，不能当 SQLite 查询。整理用的是账号目录里已经摊平的 `聊天记录.sqlite`。这个文件不会自己跟着微信更新。`watchlist.py status` 的 `refresh_needed` 看的是活库相对上次克隆体积是否涨了至少 32KiB（微信在跑时 mtime 会一直变，不能单靠 mtime 决定要不要整库重导）。查询截止时间仍以 sqlite 里 `MAX(create_time)` 为准。

## 何时刷新

出现下面任一说法，或 `watchlist.py status` 显示 `refresh_needed: true`，先刷新再整理：

- 更新微信快照 / 刷新聊天记录 / 重新导出
- 补某天日报，但快照 `MAX(create_time)` 早于要的日期
- 活微信在跑、加密库体积或 mtime 新于可读 sqlite

```bash
python3 "/Users/joker/.skills-manager/skills/joker-wechat-get-message/scripts/watchlist.py" status --json
python3 "/Users/joker/.skills-manager/skills/joker-wechat-get-message/scripts/refresh.py" status --json
```

只检查不写库：

```bash
python3 "/Users/joker/.skills-manager/skills/joker-wechat-get-message/scripts/refresh.py" refresh --dry-run --json
```

真正导出（解释器必须带 sqlcipher3；脚本在缺库时会切到已有 venv）：

```bash
"/Users/joker/Library/Caches/WeChatDataAnalysis/joker-local-access/venv/bin/python" \
  "/Users/joker/.skills-manager/skills/joker-wechat-get-message/scripts/refresh.py" refresh --json
```

成功后再查监控名单和群 `MAX(create_time)`。失败保留旧 sqlite 和 `学习整理/`。

## 做法

1. 读账号 `private/keys.json`（salt 十六进制 → `{key, mode}`），**不要 cat、不要写入日志或回复**。
2. 对活库 `db_storage/**/*.db` 只读文件头 16 字节，用 salt 查已有密钥。缺 salt 或 `cipher_integrity_check` 失败就停。
3. APFS `clonefile` 活目录到临时目录（同卷、目标不得已存在）；失败再物理复制。
4. 用 `sqlcipher3` 只读打开克隆库，解码 `message_content`/`compress_content`，摊平成 `聊天记录.sqlite` 的 `contacts` + `messages`。
5. 旧 sqlite 改名为 `聊天记录.sqlite.bak-时间戳`（只留一份），再原子替换新库，重写 `验证报告.json` 的 `exported_at`。

解码函数在技能内 `scripts/message_decode.py`，不要去 import `wechat_decrypt_tool`。

## 边界

- 活微信加密库更新 ≠ 可读快照已更新；`live_wechat` 永远是 false。
- 不要用 wechat-cli、frida、Debug.app、LLDB、mach 捕获或 `capture-launch`。
- 不要重新取钥、不要打印密钥、不要把密钥写进验证报告。
- 密钥轮换（新库 salt 不在 `keys.json`）时停止，说明缺哪些相对路径，等用户另授取钥权限。
- 不要清空账号目录；`学习整理/`、`读取聊天记录.py`、监控名单原样保留。
- 不要把这次刷新理解成实时监听或定时任务。
