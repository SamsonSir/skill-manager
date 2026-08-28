#!/usr/bin/env python3
"""
从文本中提取核心概念

识别文本中值得单独作为原子概念的关键词
"""

import re
import sys
from pathlib import Path

# 常见的技术概念模式
CONCEPT_PATTERNS = [
    # 首字母大写的术语（如 React, Redux, JWT）
    r'\b[A-Z][a-zA-Z0-9]*\b',
    # 带连字符的术语（如 state-management, deep-learning）
    r'\b[a-z]+-[a-z]+\b',
    # 全大写的缩写（如 API, JWT, SQL）
    r'\b[A-Z]{2,}\b',
    # 常见技术术语
    r'\b(?:useState|useEffect|useContext|useReducer|useCallback|useMemo|useRef)\b',
    r'\b(?:component|hook|function|class|interface|type|module)\b',
    r'\b(?:async|await|promise|callback|event|handler)\b',
    r'\b(?:state|props|context|reducer|action|dispatch)\b',
]

# 停用词（不作为概念）
STOP_WORDS = {
    'The', 'And', 'Or', 'But', 'So', 'For', 'With', 'By', 'From', 'To', 'Of', 'In', 'On', 'At',
    '是', '的', '了', '在', '和', '或', '但是', '所以', '因为', '为了', '用', '从', '到', '中', '上',
    'this', 'that', 'these', 'those', 'it', 'they', 'them',
    '一个', '一种', '一些', '可以', '能够', '应该', '需要', '想要', '使用',
}

def extract_concepts(text: str, min_length: int = 2) -> list:
    """
    从文本中提取核心概念

    Args:
        text: 待分析的文本
        min_length: 概念的最小长度

    Returns:
        概念列表，按出现次数排序
    """
    text_lower = text.lower()

    # 统计概念出现次数
    concept_counts = {}

    for pattern in CONCEPT_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # 过滤停用词和过短的词
            if len(match) < min_length:
                continue
            if match in STOP_WORDS:
                continue

            # 统一大小写进行计数
            key = match.lower()
            concept_counts[key] = concept_counts.get(key, 0) + 1

    # 按出现次数排序
    sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)

    # 返回前 N 个概念
    return [concept for concept, count in sorted_concepts[:10]]

def filter_meaningful_concepts(concepts: list, text: str) -> list:
    """
    过滤出有意义的独立概念

    排除：
    - 只在标题中出现的概念
    - 出现次数过少的概念
    - 过于通用的概念
    """
    text_lower = text.lower()
    meaningful = []

    for concept in concepts:
        # 检查概念在正文中的出现次数
        count = len(re.findall(r'\b' + re.escape(concept.lower()) + r'\b', text_lower))

        # 至少出现 2 次才考虑
        if count >= 2:
            meaningful.append(concept)

    return meaningful

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_concepts.py <text>")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    concepts = extract_concepts(text)
    meaningful = filter_meaningful_concepts(concepts, text)

    # 输出结果
    print("提取的核心概念：")
    for i, concept in enumerate(meaningful, 1):
        print(f"{i}. {concept}")

if __name__ == "__main__":
    main()
