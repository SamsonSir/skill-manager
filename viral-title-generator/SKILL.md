---
name: viral-title-generator
display_name: 爆款标题生成器
display_name_en: Viral Title Generator
description: Generate high-CTR titles for a given topic across platforms like Xiaohongshu, Douyin and WeChat. Triggers include 爆款标题, 标题生成, 小红书标题, 抖音标题, 公众号标题, viral title, headline generator.
description_zh: 输入一个主题，一键生成小红书、抖音、公众号等多平台的高点击率标题，内置爆款公式、平台字数规范与违规词过滤，支持批量出 N 个候选。
description_en: Turn one topic into high-CTR titles for Xiaohongshu, Douyin, WeChat and more, with proven formulas, platform length rules and banned-word filtering. Generate N candidates in batch.
category: content-creation
version: 1.0.0
author: 工程师的第二大脑
---

# 爆款标题生成器（Viral Title Generator）

把「一个主题 / 一条素材」一键拆成**多平台、多角度、可直接发**的高点击标题，并自动避开违规词与标题党红线。

## 何时使用

当用户出现以下意图时触发本技能：

- 起标题、爆款标题、标题生成、文案标题、吸睛标题
- 「帮我给这篇文章起个标题」「这个视频起什么标题」「小红书/抖音/公众号标题怎么写」
- 用户给了一个主题或一段内容，想要一批可选的标题

## 核心原则（务必遵守）

1. **先问一轮，别过度追问**：信息不足时最多一次问清 3 件事——目标平台、目标人群、语气（专业/口语/情绪化）。用户说「随便/你定」时默认「小红书 + 面向大众 + 情绪化」，直接产出。
2. **一个主题出多角度**：数字、悬念、反差、痛点、利益、热点、共鸣、对比，至少覆盖 4 种角度，不重复。
3. **按平台适配**：字数、风格、符号、emoji 严格按 `@references/platform-styles.md`。
4. **绝不标题党**：标题必须与内容真实相关，不夸大、不造假、不碰红线（见 `@references/avoid-list.md`）。
5. **给理由**：每条标题附「为什么有效」一句说明，帮助用户理解和选用。

## 工作流程

### 第 1 步：收集信息

一次问清（可合并成一句话）：

- **主题**：用户要写的是什么（文章/视频/帖子/产品）。
- **平台**：小红书 / 抖音 / 公众号 / B站 / 知乎 / 微博 / 多平台都要？
- **语气**：专业干货 / 口语亲切 / 情绪共鸣 / 悬念猎奇？

### 第 2 步：拆解角度

围绕主题套用 `@references/title-formulas.md` 的公式，至少生成 4 种角度：

- 数字清单：「5 个」「3 步」「10 倍」
- 悬念钩子：「别再」「居然」「原来」「这才是」
- 反差对比：「月薪 3k 和 3w 的差别」
- 痛点戳心：「踩过的坑」「没人告诉你」
- 利益承诺：「一招」「白嫖」「直接抄」
- 热点借势：结合近期热词/事件

### 第 3 步：平台适配

按 `@references/platform-styles.md` 调整每个标题的：

- 字数上限（小红书 ≤ 20 字、公众号 ≤ 30 字等）
- 是否带 emoji / 话题标签
- 标点与断句风格

### 第 4 步：合规过滤

逐条过 `@references/avoid-list.md` 的违规词与红线，命中即替换或删除。

### 第 5 步：输出

- **默认输出 Markdown 表格**：平台 | 标题 | 角度 | 为什么有效。
- 用户要求批量时，用 `templates/title-batch.md` 的格式，每平台 5–10 条。
- 每批最后附一句「建议首选 + 原因」。

## 输出示例

| # | 平台 | 标题 | 角度 | 为什么有效 |
|---|---|---|---|---|
| 1 | 小红书 | 5 个让你加薪翻倍的职场习惯 | 数字 | 具体数字 + 利益承诺，点击欲强 |
| 2 | 抖音 | 别再这样写简历了，HR 一看就扔 | 悬念 | 「别再」制造焦虑 + 场景代入 |
| 3 | 公众号 | 月薪 3k 和 3w 的人，差在这 3 个思维 | 反差 | 强烈对比 + 悬念，转发率高 |

## 平台规范

详见 `@references/platform-styles.md`，核心：

- **小红书**：≤ 20 字，可带 1–2 个 emoji + #话题，情绪化、口语化。
- **抖音**：≤ 30 字，强钩子前置，口语短句，多用「你」。
- **公众号**：≤ 30 字，观点鲜明，可带数字或反常识，忌太长。
- **B站**：≤ 40 字，可玩梗、可二创风格。
- **知乎**：用问句，观点 + 具体场景。

## 公式与违规词

- 爆款公式：`@references/title-formulas.md`
- 违规词与红线：`@references/avoid-list.md`

## 边界

- 不编造数据、不承诺无法兑现的效果（如「保证月入 10 万」）。
- 不碰医疗/金融/法律等专业领域的绝对化表述。
- 内容与标题必须真实对应，禁止纯标题党。
- 不生成违法、低俗、引战内容。
