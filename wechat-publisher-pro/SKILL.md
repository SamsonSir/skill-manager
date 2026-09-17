---
name: wechat-publisher-pro
description: 一键发布 Markdown 到微信公众号草稿箱。支持图文消息（长文）和图片消息（贴图）两种模式。
metadata:
  openclaw:
    emoji: 📱
allowed-tools: null
version: 1.0.0
display_name: "公众号-文章&贴图发布"
display_name_en: "WeChat Publisher"
description_zh: "一键发布 Markdown 到微信公众号草稿箱，支持图文消息（长文）与图片消息（贴图）两种模式"
description_en: "Publish Markdown to your WeChat Official Account drafts: long-form articles and image posts."
---

# wechat-publisher

**一键发布 Markdown 到微信公众号草稿箱**

支持两种发布模式：
- 📝 **图文消息（长文）**：基于 wenyan-cli，支持富文本、代码高亮、多主题
- 🖼️ **图片消息（贴图）**：多图横滑浏览体验，图片由 `image_info` 承载

## 功能概览

| 模式 | 脚本 | 说明 |
|------|------|------|
| 图文消息 | `publish.sh` | wenyan-cli 转换 Markdown → 微信格式，支持代码高亮 |
| 图片消息 | `wechat-image-post.py` | 多图发布为横滑贴图，纯 Python 实现 |

---

## 模式一：图片消息（贴图）✅

直接调用 Python 脚本，无需 wenyan-cli。

### 1. 准备 Markdown 文件

> **格式规范（与小红书笔记对齐）**：所有字段写在 frontmatter（`---` 之间），正文放图片 `![]()` 引用和纯文本 caption。

```markdown
---
title: 今日份的少女图鉴
cover: ./assets/cover.jpg    # 封面图路径（必填，脚本自动处理缩放≤64KB）
tags: ["少女", "写真", "氛围感"]   # 话题标签（可选，仅作记录，微信无原生支持）
author: WorkBuddy           # 作者（可选）
---

一组精选图片，分享给大家。

![](01.jpeg)
![](02.jpeg)
![](03.jpeg)
```

**Frontmatter 字段说明：**

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 文章标题 |
| `cover` | ✅ | 封面图相对路径（脚本自动缩放至 ≤64KB） |
| `tags` | — | 话题标签数组，仅作记录用 |
| `author` | — | 作者 |

**正文格式说明：**
- `![]()` 语法引用本地图片，脚本自动上传并通过 `image_info` 渲染
- 正文文本（不含图片行）作为 caption 显示，**不支持 Markdown 格式**

### 2. 发布命令

```bash
source ~/.wechat-credentials.env  # 或 AutoWork/.wechat-credentials.env
python3 ~/.workbuddy/skills/wechat-publisher/scripts/wechat-image-post.py /path/to/post.md
```

或使用 shell 包装脚本（自动加载凭据）：

```bash
bash ~/.workbuddy/skills/wechat-publisher/scripts/wechat-image-post.sh /path/to/post.md
```

> **注意**：`title`、`cover`、`tags`、`author` 均从 markdown frontmatter 读取，不再通过 CLI 传参。

### 3. 技术细节

- **封面图**：首张图片自动作为封面（需 ≤64KB，自动缩放）
- **图片上传**：全部走 `material/add_material` 永久素材接口
- **Payload 结构**：使用 `article_type=newspic` + `image_info.image_list`
- **正文限制**：`content` 字段为纯文本 caption（newspic 类型不支持 HTML）

### 4. 常见错误排查

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| 40007 | media_id 无效 | 确保所有图片通过 `material/add_material` 上传（永久素材） |
| 45004 | digest/content 超限 | 缩短纯文本 caption，封面图需 ≤64KB |
| 40004 | 编码问题 | 已修复，强制 `ensure_ascii=False` + UTF-8 header |

---

## 模式二：图文消息（长文）📝

基于 wenyan-cli，支持富文本排版。

### 1. 安装 wenyan-cli

```bash
npm install -g @wenyan-md/cli
wenyan --help
```

### 2. 配置 API 凭证

```bash
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret
```

凭据文件：`~/.workbuddy/skills/wechat-publisher/scripts/.env` 或 `~/WorkBuddy/AutoWork/.wechat-credentials.env`

> **注意**：确保 IP 已添加到微信公众号后台白名单！

### 3. 准备 Markdown 文件

```markdown
---
title: 文章标题（必填！）
cover: ./assets/cover.jpg  # 封面图（必填！）
---

# 正文开始

你的内容，支持 Markdown 语法...
```

### 4. 发布命令

```bash
cd ~/.workbuddy/skills/wechat-publisher
./scripts/publish.sh /path/to/article.md
```

---

## 脚本目录结构

```
wechat-publisher/
├── SKILL.md
├── scripts/
│   ├── publish.sh           # 图文长文发布（wenyan-cli）
│   ├── setup.sh             # 环境初始化
│   ├── wechat-image-post.py # 图片贴图发布（Python，2026-03-19 重构）
│   └── wechat-image-post.sh # wechat-image-post.py 的 shell 包装
```

---

## 故障排查

### 1. IP 不在白名单
```bash
curl ifconfig.me  # 获取公网 IP
# 登录微信公众平台 → 开发 → 基本配置 → IP 白名单 → 添加
```

### 2. 环境变量未设置
```bash
source ~/.workbuddy/skills/wechat-publisher/scripts/.env
# 或
source ~/WorkBuddy/AutoWork/.wechat-credentials.env
# 或（凭据可能在其他工作目录，直接 grep 找）
grep -rln "WECHAT_APP_ID" ~/WorkBuddy 2>/dev/null
```

### 3. wenyan-cli 未安装（图文体）
```bash
npm install -g @wenyan-md/cli
```

### 4. macOS：`~/.config/wenyan-md/` 被 provenance xattr 锁住（关键坑）

**症状**：wenyan publish 报 `无法保存 token: EPERM ... token.json.tmp`，且 `xattr -c` 也清不掉。

**原因**：macOS provenance 机制把 `~/.config/wenyan-md/` 的 xattr 锁了，应用通过 atomic write（`.tmp` → rename）写文件时被拒。

**解法**：重定向 HOME 到 `/tmp` 下的临时位置：

```bash
FAKE_HOME=/tmp/fake-home-wenyan
mkdir -p "$FAKE_HOME/.config/wenyan-md"
# 复制现有 token + cache 到新位置
cp ~/.config/wenyan-md/token.json "$FAKE_HOME/.config/wenyan-md/" 2>/dev/null
cp ~/.config/wenyan-md/upload-cache.json "$FAKE_HOME/.config/wenyan-md/" 2>/dev/null

# 跑发布命令时改 HOME
source ~/path/to/.wechat-credentials.env
HOME="$FAKE_HOME" wenyan publish -f article.md -t lapis -h github
```

### 5. 封面图尺寸不符

wenyan-cli 要求 cover **严格 1080×864 像素，且 ≤ 64KB**。一行命令制作：

```bash
magick source.png \
  -resize 1080x864^ -gravity center -extent 1080x864 \
  -quality 70 \
  cover.jpg
```

`-resize 1080x864^` 让短边填满，`-extent` 居中裁切到目标尺寸。`-quality 70` 通常能压到 60KB 左右。如果还超 64KB，降到 65 或 60。

---

## 更新日志

### 2026-03-19 - v1.2.0
- ✅ **格式对齐**：frontmatter 规范与小红书笔记保持一致，新增 `cover`（必填封面图）和 `tags`（可选话题标签）字段
- ✅ **元数据迁移**：`author` 从 CLI `--author` 参数移至 frontmatter，脚本不再接受该参数
- ✅ `parse_frontmatter` 重写：支持 `tags: ["a", "b"]` 数组格式，正确处理带引号的值
- ✅ 发布时打印标签列表

### 2026-03-19 - v1.1.0
- ✅ **新增**：图片消息（贴图）发布支持
- ✅ `wechat-image-post.py` 完整重构，支持 `article_type=newspic`
- ✅ 修复 JSON 中文乱码问题（`ensure_ascii=False`）
- ✅ 修复 thumb_media_id 40007 错误（改用 `image_info.image_list`）
- ✅ 修复 content 超限问题（newspic 类型 content 改为纯文本 caption）
- ✅ 所有图片改用 `material/add_material` 永久素材接口

### 2026-02-05 - v1.0.0
- ✅ 初始版本（图文消息支持）
- ✅ 基于 wenyan-cli 封装
- ✅ 多主题支持

---

## 参考资料

- [wenyan-cli GitHub](https://github.com/caol64/wenyan-cli)
- [wenyan 官网](https://wenyan.yuzhi.tech)
- [微信公众号 draft_add 文档](https://developers.weixin.qq.com/doc/subscription/api/draftbox/draftmanage/api_draft_add.html)
