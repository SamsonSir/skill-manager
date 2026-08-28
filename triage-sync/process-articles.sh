#!/bin/bash
# 批量处理微信公众号文章脚本
# 用途：将归档的文章重新生成为完整版本，保留所有原文和图片链接

set -e

# 配置
SOURCE_DIR="笔记同步助手"
OUTPUT_DIR="40_知识库/精华文章"
CATEGORIES=("AI工程实践" "AI产品与工具" "AI商业与转型" "知识管理" "工作流与方法论" "Agent技术")

# 分类判断函数
determine_category() {
    local file="$1"
    local content=$(cat "$file")

    # 根据关键词判断分类（更具体的分类放在前面）
    # 注意：不使用通用的"Agent"关键词，只匹配Agent技术的具体特征
    if echo "$content" | grep -qiE "(多Agent|Agent.*搭|Agent.*团队|Agent.*协作|PM Agent|Coding Agent|CodeBanana|A2A|Tool Use|Agent.*架构|Agent.*自主|OpenClaw|计算机视觉|Computer Use)"; then
        echo "Agent技术"
    elif echo "$content" | grep -qiE "(Claude Code|降智|Token|CLAUDE_CODE|settings\.json|隐藏命令|上下文窗口|会话管理|防封号|封号)"; then
        echo "AI工程实践"
    elif echo "$content" | grep -qiE "(Image.?2|Seedance|生图|Lovart|提示词模板|Topview|视频创作|Midjourney|PixVerse|AI视频|产品测评|工具介绍)"; then
        echo "AI产品与工具"
    elif echo "$content" | grep -qiE "(一人公司|OPC|超级个体|创业|商业|门槛|商业模式|行业观察|AI员工|企业.*转型|转型一线)"; then
        echo "AI商业与转型"
    elif echo "$content" | grep -qiE "(知识管理|第二大脑|Obsidian|笔记法|知识体系|OrbitOS)"; then
        echo "知识管理"
    elif echo "$content" | grep -qiE "(SOP|流程|方法论|提示词工程|技巧|最佳实践|Skill|office-hours|做错了|满意答案)"; then
        echo "工作流与方法论"
    elif echo "$content" | grep -qiE "(代码|编程|工程|踩坑|CLI|命令行|开源)"; then
        echo "AI工程实践"
    else
        echo "AI工程实践"  # 默认分类
    fi
}

# 生成文章函数
generate_article() {
    local source_file="$1"
    local category="$2"
    local filename=$(basename "$source_file")

    # 提取元数据
    local author=$(grep "^author:" "$source_file" 2>/dev/null | sed 's/author: //' || echo "未知作者")
    local url=$(grep "^url:" "$source_file" 2>/dev/null | sed 's/url: //' || echo "")
    local saved=$(grep "^saved:" "$source_file" 2>/dev/null | sed 's/saved: //' || echo "")
    local pub_date=$(grep "^发布时间:" "$source_file" 2>/dev/null | sed 's/发布时间: //' || echo "")

    # 生成标题（去掉 .md）
    local title=$(echo "$filename" | sed 's/\.md$//')

    # 输出文件路径
    local output_file="${OUTPUT_DIR}/${category}/${title}.md"
    local output_dir=$(dirname "$output_file")
    mkdir -p "$output_dir"

    # 生成文件
    cat > "$output_file" << EOF
---
source: 笔记同步助手/2026-04/${filename}
author: ${author}
original_url: ${url}
saved: ${saved}
extracted: $(date +%Y-%m-%d)
category: ${category}
tags: [精华文章]
quality: ⭐⭐⭐⭐⭐
---

# ${title}

## TLDR
TODO: 手动填写3-5句精华提炼

## 核心观点
- TODO: 提取核心观点
- TODO: 提取核心观点

## 值得记住的金句
> TODO: 提取金句

## 原文全文

$(cat "$source_file")
EOF

    echo "✅ 已生成: $output_file"
}

# 主处理逻辑
echo "🚀 开始批量处理文章..."
echo "📁 源目录: $SOURCE_DIR"
echo "📂 输出目录: $OUTPUT_DIR"
echo ""

# 查找并统计所有文章文件（排除 attachments 子目录）
total=$(find "$SOURCE_DIR" -mindepth 2 -name "*.md" -type f ! -path "*/attachments/*" | wc -l)

echo "📊 找到 $total 篇文章待处理"
echo ""

if [ $total -eq 0 ]; then
    echo "❌ 没有找到需要处理的文章"
    exit 0
fi

# 逐个处理（使用 while read 正确处理文件名中的空格和特殊字符）
temp_counter=$(mktemp)
echo "0" > "$temp_counter"

find "$SOURCE_DIR" -mindepth 2 -name "*.md" -type f ! -path "*/attachments/*" | sort | while IFS= read -r file; do
    # 跳过已完整处理的文件
    filename=$(basename "$file")
    if grep -q "^## 原文全文" "$file" 2>/dev/null; then
        echo "⏭️  跳过 (已处理): $filename"
        continue
    fi

    echo "⏳ 处理: $filename"

    # 判断分类
    category=$(determine_category "$file")
    echo "   📂 分类: $category"

    # 生成文章
    generate_article "$file" "$category"

    # 更新计数器
    processed=$(cat "$temp_counter")
    echo $((processed + 1)) > "$temp_counter"
    echo ""
done

processed=$(cat "$temp_counter")
rm -f "$temp_counter"

echo "✅ 处理完成！"
echo "📊 共处理 $processed 篇文章"
echo ""
echo "⚠️  注意事项："
echo "   1. TLDR、核心观点、金句部分需要手动完善"
echo "   2. 分类可能需要手动调整"
echo "   3. 原文完整保留，包含所有图片链接"
