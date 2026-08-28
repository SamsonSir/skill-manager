# mono-terminal 风格规范

## 视觉定位

终端单色 / hacker 风格。纯黑底 + 等宽字体 + 三色（荧光绿/警告黄/红）。强辨识度，受众偏开发者。

## 适合内容

- 开发者向工具评测（CLI、Agent、IDE 插件）
- debug / 故障复盘 / 安全话题
- 命令行教程
- 任何带 shell 命令、代码块的文章

## 配色

| 用途 | 色值 |
|------|------|
| 主背景 | `#0A0A0A` |
| 卡片背景 | `#0F0F0F` |
| 边框/分隔 | `#2A2A2A` |
| 正文 | `#C8C8C8` |
| 强调亮 | `#F0F0F0` |
| 次要灰 | `#6A6A6A` |
| 注释灰 | `#4A4A4A` |
| 主强调 荧光绿 | `#00FF88` |
| 警告 黄 | `#FFD23F` |
| 错误 红 | `#FF5E5E` |

## 字体

```
font-family: 'JetBrains Mono', 'Menlo', 'Consolas', 'Courier New', monospace;
```

PC 端优先 JetBrains Mono / Menlo（macOS 默认有 Menlo），移动端自动回退到系统 monospace。**全文都用等宽**，包括标题和正文。

## 字号层级

| 元素 | 字号 |
|------|------|
| 主标题 | 24px / 700 |
| 章节头 | 18px / 700 |
| 正文 | 14px / line-height 1.8 |
| 数据大字 | 22px / 700 |
| 命令框正文 | 13px |
| callout 正文 | 13px |
| 标签/注释 | 11px |
| 极小注释 | 10px |

## 组件清单

| 组件 | 说明 |
|------|------|
| Banner | `$ cat /jokersu/...` 命令行风格 + `&gt;` 前缀大标题 |
| ASCII 分隔线 | `────────` 用 `#2A2A2A` 灰色 |
| 章节头 | `## 01_section` 注释式编号 + 标题 |
| 正文段落 | 等宽 14px，关键词用三色高亮 |
| 命令框 | `#141414` 背景 + 1px `#2A2A2A` 边框 + `~/jokersu $` 前缀 |
| callout 警告 | `#1A1500` 背景 + 3px `#FFD23F` 左边框 + `[WARN]` 标签 |
| callout 错误 | `#1A0808` 背景 + 3px `#FF5E5E` 左边框 + `[ERROR]` 标签 |
| 列表 | `&gt;` 前缀代替 bullet，前缀用绿色 |
| 引用块 | 3px 绿色左边框 + `// — 来源` 注释式署名 |
| 数据格 | 三列等宽 table，数字用绿/黄交替 |
| 结尾 | `$ exit 0` + `// 公众号名` |

## 微信适配硬约束

- 主布局必须 `<table border-collapse: collapse>`
- 所有 `<td>` 加 `border: none`
- 背景色全部实色 hex（不用 `rgba()` 背景，文字 `rgba` 也尽量避免，本模板全用 hex）
- 不用 `display: flex / grid / gap / linear-gradient`
- 等宽字体只能写系统栈，不能 `@font-face`
- ASCII 分隔线必须用 `<span>` 包裹，避免微信吃掉空格

## 与其他模板的差异

- 跟 `dark-tech` 都黑底，但 dark-tech 是产品发布会风（橙红 + 大字），mono-terminal 是终端调试风（绿色 + 等宽）
- 跟 `blue-minimal` 完全相反，一个是杂志感衬线，一个是终端等宽
