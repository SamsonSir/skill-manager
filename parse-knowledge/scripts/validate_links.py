#!/usr/bin/env python3
"""
验证 Markdown 文件中的 wikilinks

检查 wikilink 是否正确，目标文件是否存在
"""

import re
import sys
from pathlib import Path

def extract_wikilinks(content: str) -> list:
    """
    从 Markdown 内容中提取所有 wikilinks

    Args:
        content: Markdown 文件内容

    Returns:
        wikilink 列表
    """
    # 匹配 [[Link]] 或 [[Link|Text]] 格式
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, content)

    # 提取纯链接（去掉 |Text 部分）
    links = []
    for match in matches:
        link = match.split('|')[0].strip()
        links.append(link)

    return links

def validate_wikilinks(file_path: Path, vault_root: Path) -> dict:
    """
    验证文件中的所有 wikilinks

    Args:
        file_path: 要验证的文件路径
        vault_root: 知识库根目录

    Returns:
        验证结果字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    wikilinks = extract_wikilinks(content)

    results = {
        'file': str(file_path),
        'total_links': len(wikilinks),
        'valid': 0,
        'invalid': 0,
        'broken_links': []
    }

    for link in wikilinks:
        # 查找目标文件
        target_files = list(vault_root.rglob(f"{link}.md"))

        if target_files:
            results['valid'] += 1
        else:
            results['invalid'] += 1
            results['broken_links'].append(link)

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_links.py <file_path> [vault_root]")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    # 默认知识库根目录
    vault_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    results = validate_wikilinks(file_path, vault_root)

    print(f"\n📊 Wikilink 验证结果：{file_path.name}")
    print("=" * 50)
    print(f"总链接数: {results['total_links']}")
    print(f"✅ 有效: {results['valid']}")
    print(f"❌ 无效: {results['invalid']}")

    if results['broken_links']:
        print(f"\n🔗 断开的链接：")
        for link in results['broken_links']:
            print(f"  - [[{link}]]")
    else:
        print(f"\n✨ 所有链接都有效！")

if __name__ == "__main__":
    main()
