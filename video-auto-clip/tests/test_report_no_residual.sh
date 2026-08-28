#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/batch_clip_nl.sh"
VIDEO_PATH="/Users/joker/.openclaw/workspace/outputs/2026-04-09-选品SOP/03_dukaka防晒面罩/带货视频/03_dukaka防晒面罩_视频3.mp4"
OUT_DIR="$(mktemp -d)"
SECOND_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$OUT_DIR" "$SECOND_DIR"
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
  --keep-artifacts

OUTPUT_VIDEO="$(find "$OUT_DIR" -type f -name '*_剪辑.mp4' | head -n 1)"
if [[ -z "$OUTPUT_VIDEO" ]]; then
  echo "未生成剪辑后视频" >&2
  exit 1
fi

"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$SECOND_DIR" \
  --query "按skill剪辑" \
  --input "$OUTPUT_VIDEO" \
  --dry-run \
  --keep-artifacts

VISUAL_HITS="$(find "$SECOND_DIR" -type f -name 'visual_hits.txt' | head -n 1)"
if [[ -z "$VISUAL_HITS" ]]; then
  echo "未生成 visual_hits.txt" >&2
  exit 1
fi

if grep -Eq 'report_(layout|visual|roi)' "$VISUAL_HITS"; then
  echo "剪辑后视频仍命中 report 相关视觉信号" >&2
  cat "$VISUAL_HITS" >&2
  exit 1
fi

echo "test_report_no_residual: PASS"
