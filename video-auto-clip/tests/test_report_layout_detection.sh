#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/batch_clip_nl.sh"
VIDEO_PATH="/Users/joker/.openclaw/workspace/outputs/2026-04-09-选品SOP/03_dukaka防晒面罩/带货视频/03_dukaka防晒面罩_视频3.mp4"
OUT_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$OUT_DIR"
}
trap cleanup EXIT

if [[ ! -f "$VIDEO_PATH" ]]; then
  echo "测试视频不存在: $VIDEO_PATH" >&2
  exit 1
fi

"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_DIR" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

CUTS_FILE="$(find "$OUT_DIR" -type f -name 'cuts_refined.txt' | head -n 1)"
if [[ -z "$CUTS_FILE" ]]; then
  echo "未生成 cuts_refined.txt" >&2
  exit 1
fi

if ! awk '($1 <= 24.5 && $2 >= 25.0) || ($1 <= 25.0 && $2 >= 24.5) { found=1 } END { exit !found }' "$CUTS_FILE"; then
  echo "报告图区间未被剪掉" >&2
  cat "$CUTS_FILE" >&2
  exit 1
fi

if ! awk '($1 <= 25.3 && $2 >= 25.5) || ($1 <= 25.5 && $2 >= 25.3) { found=1 } END { exit !found }' "$CUTS_FILE"; then
  echo "报告图区间结束边界过早，仍可能残留" >&2
  cat "$CUTS_FILE" >&2
  exit 1
fi

echo "test_report_layout_detection: PASS"
