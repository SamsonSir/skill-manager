---
name: aeg-router
description: Route software work through shared AEG policies.
aeg-version: 2.1.0
---
# AEG Router

新建可维护项目、多文件功能、生产变更或多人交接，先建立 AEG Session。范围明确、低风险、可逆的小修改和一次性配置维护直接完成并针对性验证，不初始化治理目录；已有项目门禁仍有效。普通问答、解释和纯资料整理直接回答。

- 使用 aeg session start --text "USER_REQUEST" --cwd "CURRENT_DIRECTORY" --client codex 进入任务；它优先续接同一原生任务并返回下一步。用户明确要求新的独立任务时用 session create。 宿主未自动提供原生 ID 时显式传 --native-id，不能仅凭 cwd 恢复其他任务。
- 需要澄清时只处理当前一个实质问题；已有上下文或授权已明确的事项不重复询问。用户补充要求时保留仍有效的决定。
- cwd 只是工作区候选；用户已明确指定的项目可以绑定。普通对话和小修改不因当前目录存在项目而升级为完整开发。
- 遵守项目内更具体的 AGENTS.md 和 .agent/project.yaml；用 aeg policies --ids 加载返回的必要策略，不注入整个规范库。
- Demo 是交付模式，MVP 可以正式上线；分别检查项目规模、任务影响和操作风险。低风险子需求不能降低真实高风险操作的要求。
- 单文件可逆 Demo 保持轻量，不运行完整 init；使用实际运行或浏览器证据。可维护项目才使用项目治理模板，按返回结果加载必要策略包。
- 修改前明确目标、允许范围与验收；完成前运行实际 Diff Gate 和所需验证。轻量任务使用 session verify --commands JSON --files PATHS，验证后 session complete --evidence EVIDENCE_ID；可信项目使用 trust evidence 的实际证据。
- 原生子任务或 worktree 只在用户明确要求或当前宿主允许时创建；优先复用当前任务。实际使用协调器时关联真实操作回执；原生任务成功不等于工程验证通过。
- 失败保留工作区和有效结果；接续与切换客户端不得丢失合约、风险和项目绑定。

## 默认工具路由

- 涉及飞书读取、写入、Wiki、文档、表格或消息，读取对应 Lark Skill 并使用 lark-cli，不另造飞书 API 客户端。
- 公开资料检索和文档阅读优先搜索或页面读取；登录态、表单交互和网页验收默认使用 ego-browser。用户或项目指定工具时遵循指定。

## 文件生命周期管理

- 本机任务文件遵守 AEG 文件生命周期管理；轻量任务无需初始化工程目录。创建临时文件前运行 aeg files init --id TASK_ID，使用返回的专属 scratch；已有 Session 复用其 ID，轻量任务使用唯一 ID。用户原件、正式成果、凭据、登录态和工程验证证据不得混入可清理临时目录。
- 确需覆盖原文件时用 aeg files backup --id TASK_ID --file ABSOLUTE_PATH；内容相同复用备份，禁止备份的备份和反复整目录复制。多 Agent 复用同一任务 ID 或分别使用唯一 ID，不清理其他任务目录。
- 交付前把有效成果移到正式位置；需暂留的 scratch 文件运行 aeg files keep --id TASK_ID --file RELATIVE_PATH --reason REASON。Session 完成时自动清理专属 scratch；轻量任务自行运行 aeg files complete --id TASK_ID --write 并报告结果。失败任务保留诊断材料并说明，不能冒充完成。
- 历史残留只盘点、不删除。自动清理仅限新机制登记的 scratch 与受管备份；活动任务、未知归属和最近恢复点受保护。新备份保留最近三份及三十天内版本，只有关联任务已完成的过期版本可清理。个人 AI 成品继续遵守现有归档规则，原件不删除。
