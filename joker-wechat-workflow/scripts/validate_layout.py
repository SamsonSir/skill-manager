#!/usr/bin/env python3
import argparse
import html
import re
from html.parser import HTMLParser
from pathlib import Path


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.text = []
        self.forbidden = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.depth:
            self.depth += 1
            if tag in {"button", "script", "style"}:
                self.forbidden.append(tag)
        elif attrs.get("id") == "article":
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.text.append(data)


def norm(value):
    return re.sub(r"\s+", "", html.unescape(value))


parser = argparse.ArgumentParser()
parser.add_argument("--article", required=True)
parser.add_argument("--preview", required=True)
args = parser.parse_args()

source_lines = Path(args.article).read_text(encoding="utf-8").splitlines()
paragraphs = [line.strip() for line in source_lines if line.strip() and not line.startswith("#")]
preview = Path(args.preview).read_text(encoding="utf-8")
reader = ArticleParser()
reader.feed(preview)
if not reader.text:
    raise SystemExit("FAIL: preview has no #article copy region")
if reader.forbidden:
    raise SystemExit(f"FAIL: copy region contains forbidden tags: {sorted(set(reader.forbidden))}")

layout_text = norm("".join(reader.text))
cursor = 0
for paragraph in paragraphs:
    needle = norm(paragraph)
    index = layout_text.find(needle, cursor)
    if index < 0:
        raise SystemExit(f"FAIL: missing or reordered paragraph: {paragraph[:30]}")
    cursor = index + len(needle)
print(f"PASS: {len(paragraphs)} article paragraphs present in order; copy region has no toolbar/script/style")
