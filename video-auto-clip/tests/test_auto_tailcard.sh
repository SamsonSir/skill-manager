#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/batch_clip_nl.sh"
VIDEO_PATH="/Users/joker/Desktop/20260413-224402.mp4"
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
  --query "按skill剪辑，剪掉平台尾卡" \
  --input "$VIDEO_PATH" \
  --keep-artifacts

result_video="$(find "$OUT_DIR" -type f -name '*_剪辑.mp4' | head -n 1)"
if [[ -z "$result_video" ]]; then
  echo "未生成输出视频" >&2
  exit 1
fi

duration="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$result_video")"

awk -v d="$duration" 'BEGIN { exit !(d < 55.0) }'

echo "test_auto_tailcard: PASS"
