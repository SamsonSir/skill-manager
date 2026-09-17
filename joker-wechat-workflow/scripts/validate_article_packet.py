#!/usr/bin/env python3
"""Validate an article's structured claim ledger before downstream production."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_TYPES = {"opinion", "general_observation", "experience", "biography", "dialogue", "quote"}
RISK_TYPES = {"experience", "biography", "dialogue", "quote"}
SOURCE_REQUIRED = {"user_material", "project_fact", "authorized_interview", "published_source"}
FIRST_PERSON = re.compile(r"(?:我|我的|我们|咱们)")
EVENT_CUE = re.compile(r"(?:从前|以前|那时候|后来|有一回|曾经|今天|昨天|去年|小时候|当时|记得|翻出|买回来|写过|读了|看过|遇到|听见|说过|住在|工作|退休)")
CONCRETE_CUE = re.compile(r"(?:一本|两本|三本|一张|两张|三张|一个钟头|两个钟头|书柜|发票|小票|日期|第\d|[0-9一二三四五六七八九十]+年)")
IMPLIED_EVENT = re.compile(r"(?:收拾|翻出|有过|硬撑着|买回来|搁着|坐着|夹着|写完|想起哪一本|还在.+里)")


def fail(messages: list[str]) -> int:
    for message in messages:
        print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", required=True)
    parser.add_argument("--claims", required=True)
    parser.add_argument("--style", required=True)
    args = parser.parse_args()

    article_path = Path(args.article)
    claims_path = Path(args.claims)
    style_path = Path(args.style)
    errors: list[str] = []
    if not article_path.is_file():
        errors.append(f"article not found: {article_path}")
    if not claims_path.is_file():
        errors.append(f"claims ledger not found: {claims_path}")
    if not style_path.is_file():
        errors.append(f"style review not found: {style_path}")
    if errors:
        return fail(errors)

    try:
        style = json.loads(style_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail([f"invalid style review: {exc}"])

    if style.get("schema_version") != 1:
        errors.append("style schema_version must be 1")
    if style.get("reviewed_from_final_article") is not True:
        errors.append("style review must be performed from the final article")
    if not str(style.get("contract_ref", "")).strip():
        errors.append("style review missing contract_ref")
    anchors = style.get("anchors_read")
    if not isinstance(anchors, list) or not any(str(item).strip() for item in anchors):
        errors.append("style review must list at least one anchor actually read")
    dimensions = style.get("dimensions") or {}
    required_dimensions = ("stance", "speaking_position", "concreteness", "rhythm", "ending", "recent_structure")
    for name in required_dimensions:
        item = dimensions.get(name) or {}
        if item.get("result") != "pass":
            errors.append(f"style dimension {name} did not pass")
        if not str(item.get("article_evidence", "")).strip():
            errors.append(f"style dimension {name} missing article_evidence")
        if not str(item.get("anchor_basis", "")).strip():
            errors.append(f"style dimension {name} missing anchor_basis")
    if style.get("overall") != "pass":
        errors.append("style overall result did not pass")

    lines = article_path.read_text(encoding="utf-8").splitlines()
    try:
        packet = json.loads(claims_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail([f"invalid claims ledger: {exc}"])

    if packet.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("account_id", "character_id", "article", "fact_policy"):
        if not str(packet.get(key, "")).strip():
            errors.append(f"missing {key}")
    review = packet.get("semantic_review") or {}
    if review.get("reviewed_from_final_article") is not True or review.get("result") != "pass":
        errors.append("semantic_review must independently review the final article and pass")

    claims = packet.get("claims")
    if not isinstance(claims, list):
        return fail(errors + ["claims must be a list"])

    if packet.get("article") != article_path.name:
        errors.append("claims ledger article does not match the supplied article")
    for key in ("account_id", "character_id", "article"):
        if style.get(key) != packet.get(key):
            errors.append(f"style review {key} does not match claims ledger")

    covered: set[int] = set()
    for index, claim in enumerate(claims, 1):
        prefix = f"claim {index}"
        claim_type = claim.get("type")
        if claim_type not in VALID_TYPES:
            errors.append(f"{prefix}: invalid type {claim_type!r}")
        try:
            start = int(claim.get("line_start"))
            end = int(claim.get("line_end", start))
        except (TypeError, ValueError):
            errors.append(f"{prefix}: invalid line range")
            continue
        if start < 1 or end < start or end > len(lines):
            errors.append(f"{prefix}: line range {start}-{end} outside article")
        else:
            covered.update(range(start, end + 1))
        if not str(claim.get("claim", "")).strip():
            errors.append(f"{prefix}: missing claim text")
        if packet.get("fact_policy") == "source_bound" and claim_type in RISK_TYPES:
            if claim.get("source_type") not in SOURCE_REQUIRED:
                errors.append(f"{prefix}: {claim_type} requires a verified source_type")
            if not str(claim.get("source_ref", "")).strip():
                errors.append(f"{prefix}: {claim_type} requires source_ref")

    for line_number, line in enumerate(lines, 1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        looks_like_claim = (
            FIRST_PERSON.search(text) and (EVENT_CUE.search(text) or CONCRETE_CUE.search(text))
        ) or IMPLIED_EVENT.search(text)
        if looks_like_claim and line_number not in covered:
            errors.append(f"line {line_number}: possible first-person event is absent from claims ledger: {text[:60]}")

    if errors:
        return fail(errors)
    print(f"PASS: {article_path.name}; {len(claims)} claims; fact and style gates passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
