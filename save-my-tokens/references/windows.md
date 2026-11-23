# 在 Windows 上跑

这个脚本没有在真实的 Windows 上跑过。所以在 Windows 上，扫描照常用，改动先过本机自检，过不了就只看报告。

- **怎么调用**：`python3` 在 Windows 上常常是一个跳转到应用商店的空壳。依次试 `python`、`py -3`，用第一个能打印版本号的。
- **扫描**：`slim scan` 只读，和其他系统一样用。输出是 UTF-8，按 UTF-8 读。
- **改之前**：`slim backup` 在 Windows 上会先自动自检（约 1 秒，进度打在 stderr）：在系统临时目录里造一份假配置，走一遍备份、改、回滚，核对回滚后每个文件和改前一致。自检没过，`backup` 会拒绝，这台机器上就只用扫描报告，改动告诉用户怎么手动做。想先看一眼可以单独跑 `slim selftest`，它不碰真实配置。
- **备份只列具体文件**，不列目录。Windows 上 skill 目录里常有软链和目录联接（junction），要备份的路径是这类东西、或者里面有，`backup` 会拒绝。
- **`slim move` 不可用**，一定会被拒。skill 要下沉到项目，把步骤告诉用户，由他手动搬。
- **回滚报「被拒绝」**（退出码 5）：文件正被 Claude Code、Codex 或编辑器占用。请用户关掉占用它的程序，再跑一次同样的 `rollback`；这一次如果说文件「又变过」，是上次还原到一半造成的，加 `--force`。
- **命令行里的 JSON**：PowerShell 5.1 会吃掉参数里的双引号。改很多个键时用 `slim set --many <文件>`，改 skill 状态用 `slim skills`，这两个都不用在命令行里写 JSON。只改一个键时在 Git Bash 里跑（Claude Code 在 Windows 上的 Bash 工具就是它）。
- **配置不在默认位置**：脚本自己认 `CLAUDE_CONFIG_DIR` 和 `CODEX_HOME` 这两个环境变量，不要再传 `--home`，传了会忽略它们。
- stderr 里「注意：」开头的行（HOME 和 USERPROFILE 不一致、按环境变量换了配置目录、这次不读 `.claude.json`）原样转告用户。
