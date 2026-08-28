# notion-clean 风格规范

## 视觉定位

Notion 干净模板风。纯白底 + 黑灰文字 + emoji 小标题 + 灰色 callout 卡片。极简、工具感、转发友好。这是"反设计"的设计——干净到看不出设计痕迹。

## 适合内容

- 技术教程、清单文、对比评测
- 工具使用手册、设置指南
- 数据/方案对比型文章
- 任何"实用工具"基调的内容

## 配色

| 用途 | 色值 |
|------|------|
| 主背景 | `#FFFFFF` |
| 主文字 | `#1A1A1A` |
| 次要灰 | `#787774` |
| 灰底 callout | `#F1F1EF` |
| 表头灰 | `#F7F7F5` |
| 边框灰 | `#E8E8E6` |
| Notion 蓝（链接/info） | `#2383E2` |
| 蓝色 callout 底 | `#EBF5FE` |
| 黄色 warn 主色 | `#E5A93D` |
| 黄色 callout 底 | `#FDF6E3` |
| 绿色 success 主色 | `#4DAB7E` |
| 绿色 callout 底 | `#EDF7ED` |
| 行内代码红 | `#EB5757` |

## 字体

```
font-family: -apple-system, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

无衬线系统字体。**不用任何花哨的字体**，纯系统栈，所有平台一致。

行内代码用 `'Menlo', monospace`。

## 字号层级

| 元素 | 字号 |
|------|------|
| 主标题 | 28px / 700 |
| 章节标题 (emoji + 标题) | 20px / 700 |
| 正文 | 15px / line-height 1.75 |
| callout 正文 | 14px / line-height 1.7 |
| 列表正文 | 15px |
| 步骤说明 | 14px |
| 表格正文 | 13px |
| 副标题/署名 | 14px |
| 页眉日期 | 12px |
| 行内代码 | 13px |

## 组件清单

| 组件 | 说明 |
|------|------|
| Banner | 顶部 emoji + 公众号名 + 日期 + 大标题（支持换行）+ 副标题 |
| 浅灰分割线 | 1px `#E8E8E6` 横线 |
| 章节头 | emoji + 标题（不用 markdown #，emoji 就是视觉锚点） |
| 正文段落 | 黑色 15px，强调用 `font-weight: 700`，链接用蓝色 + 下边框 |
| callout 蓝 | `#EBF5FE` 底 + 4px `#2383E2` 左色条 + 💡 emoji |
| callout 黄 | `#FDF6E3` 底 + 4px `#E5A93D` 左色条 + ⚠️ emoji |
| callout 绿 | `#EDF7ED` 底 + 4px `#4DAB7E` 左色条 + ✅ emoji |
| 列表 | `•` 前缀 + 文字，不用 `<ul>`（用 table 控制对齐） |
| 编号步骤 | 黑色圆形数字徽章 + 步骤名 + 灰色说明 |
| 引用块 | 3px 黑色左边框 + 斜体引文 + 灰色署名 |
| 对比表格 | 1px 灰色边框 + 表头浅灰底 + 13px 紧凑正文 |
| 行内代码 | 灰底红字 + 4px 圆角 + Menlo 字体 |
| 结尾 | 浅灰分割线 + 灰色 emoji 署名 |

## 微信适配硬约束

- 主布局 `<table border-collapse: collapse>`
- 所有 `<td>` 加 `border: none`（除非显式要边框，如对比表格）
- 背景全部实色 hex
- 不用 `flex / gap / linear-gradient / @font-face`
- callout 的"左色条"用 4px 宽的 `<td>` 实现，不用 `border-left`（兼容更稳）
- 列表用 `<table>` 控制 bullet 和文字对齐，不用 `<ul><li>`（公众号会改样式）
- 圆形数字徽章用 `display: inline-block + width/height/line-height + border-radius: 50%`

## emoji 使用规则

emoji 是 notion-clean 的灵魂，要用对：

| 场景 | emoji | 用途 |
|------|-------|------|
| 章节锚点 | 🔥 💡 🛠️ 📊 🎯 🚀 | 替代 markdown # 小标题 |
| info callout | 💡 📌 ℹ️ | 提示类 |
| warn callout | ⚠️ 🚨 | 警告类 |
| success callout | ✅ ✔️ 🎉 | 成功/最佳实践 |
| 章节签名 | 📝 📬 📩 | Banner 和结尾 |

**禁用**花哨 emoji（💖 🌈 ✨ 等装饰性 emoji），保持工具感。

## 与其他模板的差异

- 跟 `blue-minimal` 都偏极简，但 blue-minimal 是杂志衬线感，notion-clean 是工具无衬线感
- 跟 `dark-tech` 完全相反：一个是黑底重设计，一个是白底反设计
- 跟 `risograph-pop` 也是反向：一个高饱和大色块，一个低饱和留白
