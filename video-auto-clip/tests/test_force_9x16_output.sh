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
  --input "$VIDEO_PATH"

OUTPUT_VIDEO="$(find "$OUT_DIR" -type f -name '*_clip.mp4' | head -n 1)"
if [[ -z "$OUTPUT_VIDEO" ]]; then
  echo "未生成输出视频" >&2
  exit 1
fi

DIMS="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$OUTPUT_VIDEO")"
if [[ "$DIMS" != "720x1280" ]]; then
  echo "输出尺寸异常: $DIMS" >&2
  exit 1
fi

echo "test_force_9x16_output: PASS"
