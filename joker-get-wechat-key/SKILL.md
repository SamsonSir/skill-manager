---
name: joker-get-wechat-key
description: 获取用户指定的本机微信账号数据库密钥。用于切换微信账号后重新接入本地读取，采用 macOS Apple Silicon 隔离副本、启动前 LLDB 捕获和逐库只读验证；不修改已有消息读取技能或其他账号配置。
---

# Joker get WeChat key

仅处理用户授权的本机账号。已有明确授权时直接执行，不重复确认；系统管理员密码和手机扫码由用户在系统或微信窗口完成。不要把密钥、数据库页、私聊内容或原始调试日志发到对话、项目、知识库或远程服务。

## 边界与完成标准

- 此实现针对 macOS Apple Silicon、微信 4.x。其他平台或版本必须检查兼容性，不能宣称通用成功。
- 不修改 `/Applications/WeChat.app`，不关闭系统安全保护，不改旧账号的密钥、导出或 `joker-wechat-get-message` 技能。
- 每个账号每次运行使用 `~/Library/Application Support/JokerWeChatKey/<account>/run-*`，私有目录权限 700，输出文件 600。
- 捕获首页校验通过只是中间结果。全部目标数据库的 SQLCipher 加密完整性通过，才报告密钥验证成功；quick_check 单独报告。微信自定义全文搜索分词器可能导致检查器报错，不得把报错改写成通过，也不得据此直接断言密钥无效或数据库损坏。
- 密钥只用于本机已有数据；不等于拥有微信全网搜一搜能力，也不能证明公众号粉丝数量。

## 执行

下文 `SKILL_DIR` 指本 SKILL.md 所在目录。通过 shell 的位置参数或正确引号处理路径，不拼接未经校验的用户文本。

1. 运行 `python3 -B "$SKILL_DIR/scripts/wechat_key.py" identify`。优先使用正式微信已打开数据库识别账号。多个候选且无法从当前授权判定时，只澄清目标账号，不猜测最新目录。
2. 用户已授权本次获取及必要重启时，运行 `prepare --account-folder EXACT_FOLDER --authorized --allow-quit`。此操作退出正式微信，复制当前版本 app 和完整目标账号资料。只复制数据库会缺少登录配置，不采用这种快捷方式。保留返回的 run 路径。
3. 运行 `/usr/bin/lldb --batch -s "$RUN/launch.lldb" > "$RUN/diagnostic.txt" 2>&1`，记录真实进程或终端 session ID。启动时设置私有 umask 077。必须先启动捕获，再提示扫码。
4. 用宿主原生 computer use 检查该 run 的微信副本。系统验证和二维码交由用户处理；登录目标必须与授权账号一致。不点击数据修复，不导入其他账号或测试版数据。若进入非预期账号，停止本次进程并保留现场。
5. 通过 `status --run "$RUN"` 查看脱敏计数，不输出 capture-result.json 或原始日志。用 lsof 检查本次进程实际数据库路径是否为准备好的账号副本；当前 build 会将 Application Support 路径映射到 Library/Containers，prepare 已同时准备此布局。若实际路径仍不同或 salt 不匹配，停止并查明，不重复让用户扫码。等待期间每分钟以内检查一次并保持必要沟通。每次捕获默认最多十分钟；新输入可延长一次明确的登录窗口。到时停止记录的本次 LLDB/副本进程，不使用 killall 或模糊匹配结束其他微信。保留未完成结果以便诊断，不能把超时当成功。
6. 捕获全部目标 salt 后，用装有 `sqlcipher3` 的 Python 运行 `"$SKILL_DIR/scripts/wechat_key.py" verify --run "$RUN"`。本机现有候选运行时为 `~/Library/Caches/WeChatDataAnalysis/joker-local-access/venv/bin/python`，先检查可用性。验证程序以只读方式检查副本，不读取消息正文。`keys_verified=true` 表示全部密钥经加密完整性验证并保存 keys.json；`complete=true` 还要求全部 quick_check 通过。退出码2可能代表完整检查有缺口，必须阅读脱敏报告，不吞掉错误。
7. 无论成功失败，退出本次调试副本并恢复正式微信。检查正式 app 签名有效和原有技能基线未改。失败时保留私有运行目录，不盲目删除或覆盖。
8. 只报告账号、验证数据库数、验证结果和私有密钥文件路径。后续读取用显式账号路径或进程级参数，不覆盖旧技能默认账号。传入其他读取工具前核对密钥文件格式和目标账号。

## 来源及验证状态

见 [来源与实现说明](references/provenance.md)。区分“旧会话成功过”“本次代码已测试”和“当前账号实际验证成功”，三者不能互相替代。
