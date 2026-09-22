#!/usr/bin/env python3
"""Validate an article's structured claim ledger before downstream production."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import yaml
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
    parser.add_argument("--account-id")
    parser.add_argument("--character-id")
    parser.add_argument("--contract", help="Expected account contract, required for production strict mode")
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

    if not isinstance(style, dict):
        return fail(["style review must be an object"])
    if style.get("schema_version") != 1:
        errors.append("style schema_version must be 1")
    if style.get("reviewed_from_final_article") is not True:
        errors.append("style review must be performed from the final article")
    if not isinstance(style.get("contract_ref"), str) or not style["contract_ref"].strip():
        errors.append("style review missing contract_ref")
    elif not (style_path.parent / style["contract_ref"].split("#", 1)[0]).is_file():
        errors.append("style contract_ref file not found")
    anchors = style.get("anchors_read")
    if not isinstance(anchors, list) or not anchors or not all(isinstance(item, str) and item.strip() for item in anchors):
        errors.append("style review must list at least one anchor actually read")
    elif any(not (style_path.parent / item.split("#", 1)[0]).is_file() for item in anchors):
        errors.append("style anchor file not found")
    dimensions = style.get("dimensions")
    if not isinstance(dimensions, dict):
        errors.append("dimensions must be an object")
        dimensions = {}
    required_dimensions = ("stance", "speaking_position", "concreteness", "rhythm", "ending", "recent_structure")
    for name in required_dimensions:
        item = dimensions.get(name)
        if not isinstance(item, dict):
            item = {}
        if item.get("result") != "pass":
            errors.append(f"style dimension {name} did not pass")
        if not isinstance(item.get("article_evidence"), str) or not item["article_evidence"].strip():
            errors.append(f"style dimension {name} missing article_evidence")
        if not isinstance(item.get("anchor_basis"), str) or not item["anchor_basis"].strip():
            errors.append(f"style dimension {name} missing anchor_basis")
    if style.get("overall") != "pass":
        errors.append("style overall result did not pass")

    lines = article_path.read_text(encoding="utf-8").splitlines()
    try:
        packet = json.loads(claims_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail([f"invalid claims ledger: {exc}"])

    if not isinstance(packet, dict):
        return fail(errors + ["claims ledger must be an object"])
    for key, expected in (("account_id", args.account_id), ("character_id", args.character_id)):
        if expected is not None and packet.get(key) != expected:
            errors.append(f"{key}: task context mismatch")
    # Strict mode is used by the workflow; legacy calls remain structural checks only.
    if args.account_id is not None or args.character_id is not None:
        if not args.account_id or not args.character_id:
            errors.append("strict mode requires both account and character")
        if not args.contract:
            errors.append("strict mode requires explicit --contract from account configuration")
        else:
            try:
                contract_path = Path(args.contract).resolve()
                contract = yaml.safe_load(contract_path.read_text())
                if not isinstance(contract, dict):
                    raise ValueError("contract must be an object")
                for key, expected in (("account_id", args.account_id), ("character_id", args.character_id), ("fact_policy", packet.get("fact_policy"))):
                    if contract.get(key) != expected:
                        errors.append(f"contract {key} mismatch")
                if contract.get("status") != "confirmed":
                    errors.append("contract not confirmed")
                if (style_path.parent / str(style.get("contract_ref", "")).split('#', 1)[0]).resolve() != contract_path:
                    errors.append("review uses a different contract")
            except (OSError, ValueError, yaml.YAMLError) as exc:
                errors.append(f"invalid expected contract: {exc}")
        hashes = style.get("reference_sha256", {})
        refs = [style.get("contract_ref")] + (anchors if isinstance(anchors, list) else [])
        for ref in refs:
            if not isinstance(ref, str):
                continue
            file = style_path.parent / ref.split('#', 1)[0]
            if not isinstance(hashes, dict) or not file.is_file() or hashes.get(ref) != hashlib.sha256(file.read_bytes()).hexdigest():
                errors.append("contract/anchor hash missing or changed")
    digest = hashlib.sha256(article_path.read_bytes()).hexdigest()
    for label, document in (("claims", packet), ("style", style)):
        if document.get("article_sha256") != digest:
            errors.append(f"{label}: article_sha256 missing or stale")
    if not any(line.strip() and not line.lstrip().startswith("#") for line in lines):
        errors.append("article body is empty")
    if not isinstance(packet.get("fact_policy"), str) or packet.get("fact_policy") not in {"source_bound", "explicit_fiction"}:
        errors.append("invalid fact_policy")
    if packet.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("account_id", "character_id", "article", "fact_policy"):
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            errors.append(f"missing {key}")
    review = packet.get("semantic_review")
    if not isinstance(review, dict):
        review = {}
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
        if not isinstance(claim, dict):
            errors.append(f"{prefix}: claim must be an object")
            continue
        claim_type = claim.get("type")
        if not isinstance(claim_type, str) or claim_type not in VALID_TYPES:
            errors.append(f"{prefix}: invalid type {claim_type!r}")
            continue
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
        if not isinstance(claim.get("claim"), str) or not claim["claim"].strip():
            errors.append(f"{prefix}: missing claim text")
        if packet.get("fact_policy") == "source_bound" and claim_type in RISK_TYPES:
            if not isinstance(claim.get("source_type"), str) or claim.get("source_type") not in SOURCE_REQUIRED:
                errors.append(f"{prefix}: {claim_type} requires a verified source_type")
            if not isinstance(claim.get("source_ref"), str) or not claim["source_ref"].strip():
                errors.append(f"{prefix}: {claim_type} requires source_ref")

            else:
                source = claim["source_ref"].split("#", 1)[0]
                if not source or not (claims_path.parent / source).is_file():
                    errors.append(f"{prefix}: source_ref must point to an existing local evidence file")

    interaction_lines = packet.get("interaction_lines", [])
    interactions = set()
    if not isinstance(interaction_lines, list):
        errors.append("interaction_lines must be a list of line numbers")
    else:
        for number in interaction_lines:
            if type(number) is not int or not 1 <= number <= len(lines):
                errors.append("invalid interaction line number")
            elif not re.search(r"[？?]$", lines[number - 1].strip()) or FIRST_PERSON.search(lines[number - 1]):
                errors.append(f"line {number}: interaction exemption requires a reader question without first-person claims")
            else:
                interactions.add(number)
    for line_number, line in enumerate(lines, 1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        looks_like_claim = (
            FIRST_PERSON.search(text) and (EVENT_CUE.search(text) or CONCRETE_CUE.search(text))
        ) or IMPLIED_EVENT.search(text)
        if looks_like_claim and line_number not in covered and line_number not in interactions:
            errors.append(f"line {line_number}: possible first-person event is absent from claims ledger: {text[:60]}")

    if errors:
        return fail(errors)
    print(f"PASS: {article_path.name}; {len(claims)} claims; structural checks only; semantic review remains required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
