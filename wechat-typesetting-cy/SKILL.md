---
name: wechat-typesetting-cy
description: 微信公众号文章多模板排版技能。将纯文本或Markdown转换为精美排版的HTML代码，支持多种视觉风格模板。当用户提到"微信文章"、"公众号文章"、"发公众号"、"帮我排版"、"公众号排版"、"排版成微信格式"、"蓝色模板"、"暗黑模板"、"科技风排版"时触发。
---

# 微信公众号排版

多模板排版系统，根据文章内容自动选择最合适的视觉风格。

## 模板选择

### 可用模板

| 模板 | 视觉风格 | 适合内容 | 关键词 |
|------|----------|----------|--------|
| `blue-minimal` | 白底蓝色，衬线字体，杂志感 | 深度分析、思考、随笔、观点文 | 论述、故事、分析、思考 |
| `dark-tech` | 黑底橙红，无衬线，卡片化 | 产品介绍、科技报道、数据驱动 | 产品、数据、时间线、竞品 |
| `mono-terminal` | 黑底荧光绿，等宽字体，hacker 风 | 开发者向、CLI/Agent 评测、debug、代码教程 | 命令行、CLI、Agent、debug、安全 |
| `risograph-pop` | 奶油纸底，深棕油墨 + 砖红点睛，老报纸双色 tonal | 现象解读、文化长读、周末长文、有温度的话题 | 现象、文化、长读、复古、质感 |
| `notion-clean` | 纯白底，黑灰文字，emoji + 灰色 callout | 技术教程、清单文、对比评测、工具手册 | 教程、清单、对比、how-to、设置 |

### 自动选择逻辑

按以下优先级判断，第一条匹配即选定：

1. **用户指定** → 使用用户指定的模板
2. **CLI、命令行、Agent、debug、安全、代码教程、开发者向工具评测** → `mono-terminal`
3. **教程、how-to、清单、对比评测、设置/配置说明** → `notion-clean`
4. **现象解读、文化长读、周末长文、有温度的话题** → `risograph-pop`
5. **数据、时间线、产品特性、竞品分析、排名** → `dark-tech`
6. **论述、观点、分析、故事、随笔、思考** → `blue-minimal`
7. **不确定** → 问用户："这篇文章是 (a) 深度分析/思考 / (b) 产品科技报道 / (c) 开发者教程 / (d) how-to 清单 / (e) 现象解读？"

## 工作流程

**判断任务类型：**

1. **生成HTML** → 用户给原文，需要输出排版后的HTML代码
2. **检查排版** → 用户给已有HTML，需要检查并给出改进建议

## 生成HTML流程

### Step 1: 选模板

根据"自动选择逻辑"确定使用哪个模板。告知用户选择结果。

### Step 2: 读取模板资源

根据选定模板，读取对应文件：
- 样式规范：`references/{模板名}.md` — 获取配色、字体层级、组件列表
- HTML模板：`assets/templates/{模板名}.html` — 获取 HTML 标记模式和内联样式
- 通用规范：`references/guidelines.md` — 通用排版原则

### Step 3: 分析文章结构

识别以下元素：
- 文章标题、副标题
- 章节划分
- 金句/核心观点
- 数据点/关键数字
- 列表/要点
- 引用/来源
- 时间线事件（如有）
- 结论/行动号召

### Step 4: 将内容映射到模板组件

#### blue-minimal 组件映射

| 文章元素 | 模板组件 | 说明 |
|----------|----------|------|
| 文章标题 | 标签 + 大标题 + 副标题 | 提取关键词做标签，标题可换行 |
| 章节开始 | 蓝色分割线 + 水印章节标题 | 水印编号 01/02/03 |
| 核心金句 | 蓝色金句区块 | 蓝底白字，主句+副句 |
| 关键数据/概念 | 三栏信息卡片 | 3个关键词+说明 |
| 目录/要点列表 | 目录卡片 | 灰底两列编号列表 |
| 正文段落 | 正文段落区块 | 15px，#1A1A1A，衬线字体 |
| 二级要点 | 二级标题 | 16px 蓝色加粗 |
| 文章结尾 | END标记 | 居中灰色 |

#### mono-terminal 组件映射

| 文章元素 | 模板组件 | 说明 |
|----------|----------|------|
| 文章标题 | `$ cat` Banner | 顶部命令行风 + `&gt;` 前缀大标题 |
| 章节开始 | `## 01_section` 注释式编号 | 不用 markdown 大标题，全用注释风 |
| 命令/代码 | 命令框 | `~/jokersu $` 前缀 + 荧光绿命令 |
| 提示/警告 | callout `[WARN]` `[ERROR]` | 三色左边框 |
| 列表 | `&gt;` 前缀代替 bullet | 前缀用绿色 |
| 引用 | 绿色左边框 + `// — 来源` | 注释式署名 |
| 关键数据 | 三列等宽 table | 数字用绿/黄交替 |
| 正文段落 | 14px 等宽 + 三色高亮 | 关键词用 `#00FF88 / #FFD23F / #FF5E5E` |
| 结尾 | `$ exit 0` + `// 公众号名` | 命令行式收尾 |

#### risograph-pop 组件映射

| 文章元素 | 模板组件 | 说明 |
|----------|----------|------|
| 文章标题 | Banner | 砖红期号 + 中棕日期 + 双行衬线大标题（一行深棕一行砖红斜体）|
| 双线分隔 | 4px 深棕 + 2px 空白 + 1px 砖红 | 老报纸刊头分隔感 |
| 章节开始 | `§ 01 · SECTION` + 衬线大标题 | 砖红装饰符 + 深棕衬线 26px |
| 金句/引言 | 引言区 | 深棕底 + 上下砖红 3px 装饰线 + 砖红大引号 + 奶油色斜体衬线金句 |
| 编号要点 | 大数字编号列表 | 48px 砖红斜体衬线编号 + 米灰底分隔线 |
| 核心观点 | 标语板 | 砖红底 + 双线奶油描边 + 印章感 + 衬线大字 |
| 关键数据 | 数据格 | 2px 深棕粗描边 + 中间格反色（深棕底奶油字砖红 label）|
| 关键词强调 | 砖红加粗 / 中棕弱化 | 关键词砖红加粗，副信息中棕弱化，色块底高亮一篇 ≤2-3 处 |
| 结尾 | 深棕底 CTA | `— FIN —` + 衬线公众号名 |

#### notion-clean 组件映射

| 文章元素 | 模板组件 | 说明 |
|----------|----------|------|
| 文章标题 | Banner + emoji 日期行 | 28px 黑色重粗，支持换行 |
| 章节开始 | emoji + 标题 | 不用 markdown #，emoji 就是锚点 |
| 提示信息 | callout 蓝/黄/绿 | 4px 左色条 + emoji + 标题 + 正文 |
| 普通列表 | `•` 前缀 + table 对齐 | 不用 `<ul>` |
| 步骤教程 | 编号步骤 | 黑圆圈数字徽章 + 步骤名 + 灰色说明 |
| 引用 | 3px 黑色左边框 | 斜体引文 |
| 数据对比 | 对比表格 | 1px 灰边 + 表头浅灰底 |
| 命令/代码片段 | 行内代码 | 灰底红字 + Menlo |
| 强调 | `font-weight: 700` | 不用颜色高亮，只用加粗 |
| 结尾 | 灰线 + emoji 署名 | 干净不张扬 |

#### dark-tech 组件映射

| 文章元素 | 模板组件 | 说明 |
|----------|----------|------|
| 文章标题 | 封面Banner | 标签行 + 大字标题 + 副标题 |
| 关键数据 | 三列数据栏 | 嵌套table，橙红大数字 |
| 章节开始 | 章节头（双色标题） | 空格分隔标签 + 白色/橙红双色标题 |
| 功能/能力列表 | 能力卡片 | 绿色左边框，CAPABILITY标签 |
| 时间线事件 | 时间线节点 | 绿色=正面，红色=危机 |
| 引用/观点 | 引用卡片 | 橙红左边框 + 来源标注 |
| 类比/解释 | FEELS LIKE类比卡 | 琥珀标签头 + "所以呢?"框 |
| 排名/竞品 | 排名列表 | 大号彩色数字 + 描述 |
| 事件/案例 | 事件卡片 | 彩色左边框 |
| 结论 | 结尾递进区 | 文字透明度渐增，末句强调色 |

### Step 5: 生成HTML

严格按照模板HTML中的内联样式生成。关键规则：

**通用规则：**
- 所有样式必须内联（不用 `<style>` 标签）
- 不用 class/id 选择器
- 不用 JavaScript

**blue-minimal 专属规则：**
- 字体族：`'Times New Roman', serif`
- 主题色：`#0044FF`
- 正文色：`#1A1A1A`
- 章节间用蓝色分割线分隔
- 强调用蓝色加粗 `color: #0044FF; font-weight: bold` 或蓝色下划线

**dark-tech 专属规则：**
- 字体族：`-apple-system, 'Helvetica Neue', sans-serif`
- 主色：`#FF4500`（OrangeRed）
- 正文色：`#F0EFEB`
- **必须用 `<table>` 做主布局**，每章节一个 `<tr><td>`
- **所有 `<td>` 加 `border: none`**
- **背景色用实色 hex，不用 `rgba()`**（文字颜色的 rgba 可以）
- **不用 `display: flex` / `gap`**，用嵌套 table 代替
- **不用 `linear-gradient`**
- 章节间用分隔带 `<tr><td>` 分隔（`#0d0d0d`，16px高）
- 分隔带加 `font-size: 0; line-height: 0;`

**mono-terminal 专属规则：**
- 字体族：`'JetBrains Mono', 'Menlo', 'Consolas', 'Courier New', monospace`
- 主背景：`#0A0A0A` / 卡片：`#0F0F0F` / 边框：`#2A2A2A`
- 正文：`#C8C8C8` / 强调亮：`#F0F0F0` / 注释灰：`#4A4A4A`
- 三色：荧光绿 `#00FF88` / 警告黄 `#FFD23F` / 红 `#FF5E5E`
- **全文等宽字体**，包括标题
- **背景全部实色 hex**（本模板不用任何 `rgba`）
- ASCII 分隔线 `────────` 必须 `<span>` 包裹
- 命令框前缀 `~/jokersu $`，注释前缀 `// `

**risograph-pop 专属规则（双色 tonal 老报纸版）：**
- **双字体策略**：标题用 `Georgia, 'Songti SC', 'STSong', serif`；正文用 `-apple-system, 'PingFang SC', sans-serif`
- 主背景：`#FBF7EC`（奶油纸）/ 主文字：`#3D2817`（深棕油墨）
- **只有 2 个强调色**：砖红 `#C84B31`（点睛）+ 中棕 `#6B5440`（次要文字）+ 米灰 `#E8DFC9`（分隔线）
- **绝不引入第三个强调色**，任何加绿/加黄/加蓝的冲动都要忍住
- 大数字编号、引言金句、数据格大数字必须用 `font-style: italic`
- 章节标题不用斜体（会变软）
- 数据格中间格反色（深棕底奶油字 + 砖红 label），避免三格全奶油底显平
- 双线分隔用 3 个 `<tr><td>` 横条：4px 深棕 + 2px 奶油 + 1px 砖红
- 不用 `background-image / box-shadow`，全靠颜色和描边出层次

**notion-clean 专属规则：**
- 字体族：`-apple-system, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif`
- 行内代码字体：`'Menlo', monospace`
- 主背景 `#FFFFFF` / 主文字 `#1A1A1A` / 次要灰 `#787774` / 边框灰 `#E8E8E6`
- 链接 / info：Notion 蓝 `#2383E2`（callout 底 `#EBF5FE`）
- 警告：黄 `#E5A93D`（callout 底 `#FDF6E3`）
- 成功：绿 `#4DAB7E`（callout 底 `#EDF7ED`）
- 行内代码：灰底红字 `#F1F1EF` / `#EB5757`
- callout 左色条用 4px 宽 `<td>` 实现，不用 `border-left`
- 列表用 `<table>` 控制 `•` 对齐，不用 `<ul><li>`
- 强调只用 `font-weight: 700`，不用颜色高亮
- emoji 替代 markdown 小标题

### Step 6: 输出并预览

1. 将排版后的内容写入 HTML 文件，保存到 `output/` 目录
2. 文件名用文章主题的 slug（如 `output/ai-agent-analysis.html`）
3. 用 `open` 命令在浏览器中打开预览
4. 告知用户：在浏览器中选中内容区域 → 复制 → 粘贴到公众号编辑器

HTML文件外壳模板（根据模板选择背景色）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>微信公众号排版预览</title>
<style>
  body { margin: 0; padding: 40px; background: {{背景色}}; }
  .preview-wrapper {
    max-width: 677px;
    margin: 0 auto;
    background: {{内容背景色}};
    box-shadow: 0 2px 20px rgba(0,0,0,0.08);
  }
  .tip { background: #fff3cd; padding: 12px; margin-bottom: 20px; border-radius: 4px; font-size: 14px; user-select: none; -webkit-user-select: none; max-width: 677px; margin: 0 auto 20px; }
</style>
</head>
<body>
<div class="tip">选中下方内容 → 复制 → 粘贴到公众号编辑器</div>
<div class="preview-wrapper">

<!-- 排版后的内容放这里 -->

</div>
</body>
</html>
```

背景色参数：
- `blue-minimal`：`background: #f5f5f5`，`内容背景色: #fff`
- `dark-tech`：`background: #222`，`内容背景色: #080808`
- `mono-terminal`：`background: #1a1a1a`，`内容背景色: #0A0A0A`
- `risograph-pop`：`background: #E8E2D0`，`内容背景色: #FBF7EC`
- `notion-clean`：`background: #F5F5F5`，`内容背景色: #FFFFFF`

## 检查排版流程

根据文章使用的模板风格，对照相应规范检查：

### 通用检查项
- [ ] 所有样式是否内联
- [ ] 段落是否过长（>4行）
- [ ] 是否使用了不支持的CSS（position、外部样式表等）

### blue-minimal 检查项
- [ ] 字号是否为15px正文 / 32px大标题 / 22px章节标题
- [ ] 行间距是否为1.75倍
- [ ] 正文颜色是否为 #1A1A1A
- [ ] 字体是否为 Times New Roman, serif
- [ ] 主题色是否统一为 #0044FF
- [ ] 章节间是否有蓝色分割线

### mono-terminal 检查项
- [ ] 字体族是否包含 `'JetBrains Mono', 'Menlo'`
- [ ] 是否所有元素都用了等宽字体（包括标题）
- [ ] 是否用了三色（绿/黄/红），是否克制（一段不超过 2 种）
- [ ] 命令框是否有 `~/jokersu $` 或类似前缀
- [ ] ASCII 分隔线是否被 `<span>` 包裹

### risograph-pop 检查项
- [ ] 是否只用了 2 个强调色（砖红 + 中棕），没有第三个强调色
- [ ] 标题是否用了衬线 `Georgia, 'Songti SC', serif`
- [ ] 正文是否用了无衬线系统字体
- [ ] 大数字编号、引言金句、数据格大数字是否用了 `italic`
- [ ] 章节标题是否**没有**用斜体
- [ ] 数据格中间格是否反色（深棕底）
- [ ] 双线分隔是否用了 4px+2px+1px 三横条结构
- [ ] 是否避免了 `background-image / box-shadow`

### notion-clean 检查项
- [ ] 是否避免了任何强调色（除蓝色链接、callout 主色外）
- [ ] callout 左色条是否用 4px 宽 `<td>` 实现
- [ ] 列表是否用 `<table>` 控制对齐而不是 `<ul><li>`
- [ ] 强调是否只用 `font-weight: 700`
- [ ] 章节小标题是否用 emoji 代替 markdown #

### dark-tech 检查项
- [ ] 主布局是否使用 `<table>`（不用 flex）
- [ ] 所有 `<td>` 是否有 `border: none`
- [ ] 背景色是否全部为实色 hex（不用 rgba 背景）
- [ ] 章节分隔带是否有 `font-size: 0; line-height: 0;`
- [ ] 是否使用了 `linear-gradient`（不允许）
- [ ] 正文色是否为 #F0EFEB
- [ ] 主强调色是否为 #FF4500

详细规范见对应的 `references/{模板名}.md`。

## 扩展新模板

未来添加新模板只需：
1. 添加 `assets/templates/{new-name}.html` — HTML模板
2. 添加 `references/{new-name}.md` — 样式规范
3. 在本文件的"可用模板"表格加一行
4. 在"组件映射"部分加对应的映射表
