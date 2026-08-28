#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/batch_clip_nl.sh"
TMP_DIR="$(mktemp -d)"
VIDEO_PATH="$TMP_DIR/input.mp4"
LEGACY_OUT="$TMP_DIR/legacy"
COMBINED_OUT="$TMP_DIR/combined"

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

VIDEO_AUTO_CLIP_FRAME_EXTRACTION_MODE=legacy \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$LEGACY_OUT" \
  --query "按skill剪辑，剪掉平台尾卡" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$COMBINED_OUT" \
  --query "按skill剪辑，剪掉平台尾卡" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

legacy_run="$(find "$LEGACY_OUT" -type d -name 'run_*' | head -n 1)"
combined_run="$(find "$COMBINED_OUT" -type d -name 'run_*' | head -n 1)"
[[ -n "$legacy_run" && -n "$combined_run" ]] || {
  echo "未找到运行目录" >&2
  exit 1
}

for bucket in coarse_full coarse_bottom coarse_report; do
  legacy_dir="$legacy_run/input/$bucket"
  combined_dir="$combined_run/input/$bucket"

  legacy_count="$(find "$legacy_dir" -type f -name '*.jpg' | wc -l | tr -d ' ')"
  combined_count="$(find "$combined_dir" -type f -name '*.jpg' | wc -l | tr -d ' ')"
  [[ "$legacy_count" == "$combined_count" ]] || {
    echo "$bucket 抽帧数量不一致: legacy=$legacy_count combined=$combined_count" >&2
    exit 1
  }

  legacy_first="$(find "$legacy_dir" -type f -name '*.jpg' | sort | head -n 1)"
  combined_first="$(find "$combined_dir" -type f -name '*.jpg' | sort | head -n 1)"
  legacy_dims="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$legacy_first")"
  combined_dims="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$combined_first")"
  [[ "$legacy_dims" == "$combined_dims" ]] || {
    echo "$bucket 首帧尺寸不一致: legacy=$legacy_dims combined=$combined_dims" >&2
    exit 1
  }
done

legacy_report="$(find "$LEGACY_OUT" -type f -name '执行报告.md' | head -n 1)"
combined_report="$(find "$COMBINED_OUT" -type f -name '执行报告.md' | head -n 1)"
grep -Fq '实际粗扫抽帧模式: legacy' "$legacy_report" || {
  echo "legacy 模式未写入报告" >&2
  exit 1
}
grep -Fq '实际粗扫抽帧模式: combined' "$combined_report" || {
  echo "combined 模式未写入报告" >&2
  exit 1
}

echo "test_frame_extraction_mode_equivalence: PASS"
