---
name: wechat-mp-auto
version: "1.0.0"
description: 微信公众号自动化 — 将文章保存到草稿箱（支持 HTML 内容 + 封面图）
---

# wechat-mp-auto

微信公众号自动化技能。连接用户已登录的 Chrome（CDP 模式），将文章 HTML 和封面图自动填入编辑器并保存草稿，无需重新扫码登录。

## 前置条件

1. Chrome 已开启远程调试（在地址栏访问 `chrome://inspect/#remote-debugging`，勾选 Allow remote debugging）
2. Chrome 中已登录微信公众号后台（`https://mp.weixin.qq.com`）
3. 已安装依赖：`pip install playwright playwright-stealth && playwright install chromium`

## 安装依赖

```bash
pip install playwright playwright-stealth
playwright install chromium
```

## 命令

### 检查登录状态

```bash
python {baseDir}/scripts/mp.py check-login
```

### 保存草稿（核心命令）

```bash
python {baseDir}/scripts/mp.py save-draft \
  --title "文章标题" \
  --html-file "00_收件箱/draft-YYYY-MM-DD.html" \
  [--cover "封面图路径.jpg"] \
  [--author "JokerSu"] \
  [--digest "文章摘要，最多120字"] \
  [--preview]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--title` | 文章标题 | ✅ |
| `--html-file` | wechat-typesetting 生成的 HTML 文件路径 | ✅ |
| `--cover` | 封面图本地路径（jpg/png） | 可选 |
| `--author` | 作者名 | 可选 |
| `--digest` | 文章摘要（≤120字） | 可选 |
| `--preview` | 预览模式：只截图，不保存草稿 | 可选 |

## 使用示例

```bash
# 预览模式（先确认内容再保存）
python {baseDir}/scripts/mp.py save-draft \
  --title "Claude Code 51万行源码泄露：AI Agent工程内幕大起底" \
  --html-file "/Users/joker/Documents/JokerSu-knowledge/00_收件箱/draft-2026-04-06-v2.html" \
  --author "JokerSu" \
  --preview

# 正式保存草稿
python {baseDir}/scripts/mp.py save-draft \
  --title "Claude Code 51万行源码泄露：AI Agent工程内幕大起底" \
  --html-file "/Users/joker/Documents/JokerSu-knowledge/00_收件箱/draft-2026-04-06-v2.html" \
  --author "JokerSu"
```

## 执行流程

1. **连接 Chrome**：通过 CDP（port 9222）连接用户已登录的 Chrome，复用 session
2. **登录检测**：确认公众号后台处于登录状态
3. **新建图文**：点击「文章」按钮，等待编辑器 tab 打开
4. **填写标题**：定位标题 input，填入内容
5. **填入 HTML**：点击编辑器「源代码」按钮，粘贴 HTML 内容（自动提取 `section[data-role=outer]`）
6. **上传封面图**：如提供封面图路径，通过 file input 上传
7. **保存草稿**：点击「保存草稿」按钮，截图确认

## 与 SOP 集成

在 `daily-content-ops.md` Step 6 之后调用：

```bash
python .claude/skills/wechat-mp-auto/scripts/mp.py save-draft \
  --title "$(文章标题)" \
  --html-file "00_收件箱/draft-$(date +%Y-%m-%d).html" \
  --author "JokerSu"
```

## 技术架构

参考来源：
- **`xhs-auto-cy`**（CY-CHENYUE）— CDP 浏览器管理、session 复用、分层结构
- **`xiaohongshu-skills`**（autoclaw-cc）— 5层架构（core/actions/cli）、选择器多重降级

扩展路线（后续）：
- `actions/publish.py` — 直接发布（需要公众号有发布权限）
- `actions/schedule.py` — 定时发布
- 多平台扩展：小红书/知乎只需新增对应 actions，core 层复用

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Chrome 未在端口 9222 开启` | 未开启远程调试 | 访问 chrome://inspect/#remote-debugging 勾选选项 |
| `未登录微信公众号后台` | session 过期 | 在 Chrome 中重新登录 mp.weixin.qq.com |
| `未找到源代码按钮` | 微信编辑器版本更新 | 提 issue，更新选择器 |
| `未找到保存草稿按钮` | 编辑器未完全加载 | 增加 --preview 先截图确认页面状态 |
