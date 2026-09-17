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
        self.regions = 0
        self.void = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        self.text = []
        self.forbidden = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.depth:
            if tag not in self.void:
                self.depth += 1
            if tag in {"button", "script", "style"}:
                self.forbidden.append(tag)
        elif attrs.get("id") == "article":
            self.depth = 1
            self.regions += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.void:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.depth and tag not in self.void:
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
def visible_markdown(line):
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
    line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"^\s{0,3}(?:#{1,6}\s+|>\s*|[-+*]\s+|\d+[.)]\s+)", "", line)
    line = re.sub(r"(\*\*|__|~~|`)(.*?)\1", r"\2", line)
    return line.strip()
paragraphs = [visible_markdown(line) for line in source_lines if line.strip()]
paragraphs = [line for line in paragraphs if line]
preview = Path(args.preview).read_text(encoding="utf-8")
reader = ArticleParser()
reader.feed(preview)
if not reader.text:
    raise SystemExit("FAIL: preview has no #article copy region")
if reader.forbidden:
    raise SystemExit(f"FAIL: copy region contains forbidden tags: {sorted(set(reader.forbidden))}")

layout_text = norm("".join(reader.text))
if reader.regions != 1 or reader.depth:
    raise SystemExit("FAIL: preview requires exactly one closed #article copy region")
expected = norm("".join(paragraphs))
if not expected or layout_text != expected:
    raise SystemExit("FAIL: visible article text differs (missing, extra, reordered text or title)")
print(f"PASS: {len(paragraphs)} source blocks exactly match visible copy-region text")
