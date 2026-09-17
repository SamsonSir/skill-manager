# 来源与实现说明

用户指定参考任务：`01a0759a-80ac-7651-8317-a1a141de674b`。

该任务先使用 Rion-Wu-tech/wechat-intelligence-hub 的 Reader 路线，后采用 LifeArchiveProject/WeChatDataAnalysis 的独立微信副本思路。原生捕获器出现线程异常处理问题后，该任务改成 LLDB 符号断点，在进程启动前捕获 `CCKeyDerivationPBKDF` 参数，并按每个数据库首页进行验证。成功记录为旧账号 20 个数据库首页验证通过，随后执行完整数据库检查。

本技能从该任务留下的成功 callback 恢复捕获逻辑；模板已移除旧账号的路径、数据库页和 salt。运行时才从指定账号快照注入当前数据，敏感运行文件位于技能目录之外。

必要修正包括：完整账号及公共登录配置快照、两个 macOS 资料布局、当前安装版本 app 的独立签名副本、仅副本关闭自动更新、启动前挂载 LLDB、累计全部 salt 而非首次命中即停止。

这不是两个上游仓库未经修改的直接安装版。尤其 LLDB 回调和逐库累积属于参考任务实际修正后的实现。不要把上游项目名当作当前实现已验证的证据。

2026-09-13 实测：当前微信 build269631，指定新账号19个数据库均捕获并通过加密完整性校验，17个通过 quick_check，两个使用 MMFtsTokenizer 的全文索引库 quick_check 报 SQL logic error。密钥有效已确认，两个索引库的完整逻辑检查仍有缺口。

本次发现 macOS 将自定义 Application Support 资料路径映射至 Library/Containers。实际补齐该路径完整快照后捕获成功，prepare 已同步补上这一步。脚本 status、verify 已运行；prepare 最终组合版本尚未为第二账号重新执行完整登录测试，不宣称所有账号和版本均已验证。
