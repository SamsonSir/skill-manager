---
name: lark
description: 飞书/Lark 总入口：凡涉及飞书文档、Wiki 知识库、多维表格、电子表格、消息群聊、日历、会议纪要/妙记、任务、审批、OKR、邮箱、云盘、画板、幻灯片、通讯录，或用户给出 feishu.cn / larksuite.com 链接时使用。先读本文件，再按索引读取对应子 skill 的 SKILL.md 执行。
---

# 飞书总入口

飞书操作统一用 `lark-cli`，不另造 API 客户端。按任务找到下面对应的一行，读取 `~/.claude/skills/<名字>/SKILL.md` 后照它执行。认证、登录、身份（用户/机器人）、权限报错，先读 lark-shared。

| 任务 | 读哪个 |
|---|---|
| 登录、授权、身份切换、权限报错 | lark-shared |
| 云文档 Docx / Wiki 文档读写、图片附件 | lark-doc |
| 知识库：知识空间、成员、节点层级 | lark-wiki |
| 多维表格 Base / bitable：表、字段、记录、视图、仪表盘、workflow | lark-base |
| 电子表格 Sheets：单元格、公式、图表、透视表 | lark-sheets |
| 云盘 Drive：上传下载、移动复制删除、权限、本地文件导入为飞书文档 | lark-drive |
| 飞书原生 Markdown 文件 | lark-markdown |
| 画板 | lark-whiteboard |
| 幻灯片 | lark-slides |
| 消息、群聊、卡片、加急 | lark-im |
| 实时事件订阅 / 监听 | lark-event |
| 日历日程、会议室、忙闲 | lark-calendar |
| 视频会议记录、纪要、逐字稿、妙记（lark-vc / lark-minutes / lark-note / lark-vc-agent 都转到这里） | lark-meeting |
| 一段时间的会议纪要汇总报告 | lark-workflow-meeting-summary |
| 今天/本周日程 + 未完成任务摘要 | lark-workflow-standup-report |
| 任务、清单 | lark-task |
| 审批 | lark-approval |
| OKR | lark-okr |
| 邮箱 | lark-mail |
| 通讯录：姓名/邮箱 ↔ open_id | lark-contact |
| 考勤打卡 | lark-attendance |
| 妙搭应用开发与托管 | lark-apps |
| 上面都覆盖不到，查原生 OpenAPI | lark-openapi-explorer |
| 把飞书操作封装成新 skill | lark-skill-maker |

## 旧版 feishu-* 工具

只在用户点名，或任务正好是它们的专长时用；同类操作优先 lark-*。

| 任务 | 读哪个 |
|---|---|
| WaytoAGI 飞书知识库每日采集 | feishu-agi-collector |
| 批量导出飞书文档为 Markdown/PDF | feishu-doc-exporter |
| 用户只发来飞书文档链接、要自动总结 | feishu-doc-summarizer |
| Markdown 转 Block 写入飞书文档 | feishu-doc-writer |
| 飞书 Wiki 增量提取、提纯、分类同步 | feishu-knowledge-extractor |
| 加急提醒（含电话加急） | feishu-meeting-call |
| 创建知识空间和 Wiki 页面节点 | feishu-wiki |
