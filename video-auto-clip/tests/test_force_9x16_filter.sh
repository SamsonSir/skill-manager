#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/batch_clip_nl.sh"
TMP_DIR="$(mktemp -d)"
VIDEO_PATH="$TMP_DIR/horizontal_input.mp4"
OUT_DIR="$TMP_DIR/out"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=1280x720:d=3" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_DIR" \
  --query "保留前2秒" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

FILTER_SCRIPT="$(find "$OUT_DIR" -type f -name 'filter_complex.txt' | head -n 1)"
if [[ -z "$FILTER_SCRIPT" ]]; then
  echo "未生成 filter_complex.txt" >&2
  exit 1
fi

if ! grep -Fq 'scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280' "$FILTER_SCRIPT"; then
  echo "主输出未内联 9:16 规范化" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
fi

echo "test_force_9x16_filter: PASS"
