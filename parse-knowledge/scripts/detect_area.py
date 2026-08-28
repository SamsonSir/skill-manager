#!/usr/bin/env python3
"""
智能识别文本所属领域

根据文本内容自动识别最相关的 OrbitOS 领域
"""

import re
import sys
from pathlib import Path

# 领域关键词映射
AREA_KEYWORDS = {
    "SoftwareEngineering": [
        "编程", "代码", "开发", "软件", "算法", "数据结构", "架构", "设计模式",
        "programming", "code", "development", "software", "algorithm", "architecture",
        "react", "vue", "angular", "python", "javascript", "java", "go", "rust",
        "api", "database", "sql", "nosql", "docker", "kubernetes", "cloud",
        "测试", "test", "debug", "调试", "部署", "deploy", "ci/cd"
    ],
    "Finance": [
        "投资", "股票", "基金", "理财", "财务", "金融", "市场", "经济",
        "investment", "stock", "fund", "finance", "financial", "market", "economy",
        "加密货币", "crypto", "blockchain", "区块链", "trading", "交易"
    ],
    "Health": [
        "健康", "运动", "饮食", "睡眠", "医学", "医疗", "锻炼", "营养",
        "health", "fitness", "exercise", "diet", "sleep", "medical", "nutrition",
        "疾病", "disease", "treatment", "治疗", "prevention", "预防"
    ],
    "Writing": [
        "写作", "文章", "博客", "内容", "创作", "编辑", "出版",
        "writing", "article", "blog", "content", "creation", "editing", "publishing",
        "文案", "copywriting", "storytelling", "讲故事", "narrative", "叙事"
    ],
    "Productivity": [
        "效率", "时间管理", "工作流", "工具", "自动化", "流程", "方法",
        "productivity", "time management", "workflow", "tool", "automation", "process",
        "gtd", "番茄", "pomodoro", "todo", "待办", "计划", "planning"
    ],
    "KnowledgeManagement": [
        "知识管理", "笔记", "第二大脑", "obsidian", "notion", "roam",
        "knowledge management", "note", "second brain", "zettelkasten", "pkm",
        "记忆", "memory", "学习", "learning", "总结", "summary", "提炼", "extract"
    ],
    "Business": [
        "商业", "创业", "企业", "管理", "战略", "营销", "销售",
        "business", "startup", "entrepreneur", "management", "strategy", "marketing", "sales",
        "增长", "growth", "用户", "user", "客户", "customer", "市场", "market"
    ],
    "AI": [
        "人工智能", "ai", "machine learning", "机器学习", "deep learning", "深度学习",
        "llm", "大语言模型", "gpt", "claude", "transformer", "neural network", "神经网络",
        "prompt", "提示词", "agent", "智能体", "automation", "自动化", "nlp"
    ]
}

def detect_area(text: str) -> str:
    """
    检测文本所属领域

    Args:
        text: 待分析的文本

    Returns:
        领域名称，如 "SoftwareEngineering"
    """
    text_lower = text.lower()

    scores = {}
    for area, keywords in AREA_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # 统计关键词出现次数
            count = len(re.findall(re.escape(keyword.lower()), text_lower))
            score += count
        scores[area] = score

    # 找到得分最高的领域
    if not scores or max(scores.values()) == 0:
        # 如果没有匹配，返回默认领域
        return "Productivity"

    best_area = max(scores, key=scores.get)
    return best_area

def main():
    if len(sys.argv) < 2:
        print("Usage: detect_area.py <text>")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    area = detect_area(text)
    print(f"[[{area}]]")

if __name__ == "__main__":
    main()
