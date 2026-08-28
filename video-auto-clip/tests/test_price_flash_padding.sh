#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/batch_clip_nl.sh"
TMP_DIR="$(mktemp -d)"
BIN_DIR="$TMP_DIR/bin"
VIDEO_PATH="$TMP_DIR/input.mp4"
OUT_DIR="$TMP_DIR/out"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/fake_ocr" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
shift

case "$MODE" in
  --tsv)
    for path in "$@"; do
      text=""
      if [[ "$path" == *coarse_full/frame_00026.jpg || "$path" == *coarse_full/frame_00027.jpg ]]; then
        text="建议 零售价 ¥398 Suggested price list"
      elif [[ "$path" == *refine_price_25_000000_27_000000/frame_00018.jpg ]]; then
        text="建议 零售价 ¥398 Suggested price list"
      elif [[ "$path" == *refine_price_25_000000_27_000000_report/frame_00047.jpg ]]; then
        text="建议 零售价 ¥398 Suggested price list"
      fi
      printf '%s\t%s\n' "$path" "$text"
    done
    ;;
  --regions-jsonl)
    for path in "$@"; do
      printf '{"path":"%s","text":"","regions":[]}\n' "$path"
    done
    ;;
  *)
    exit 1
    ;;
esac
EOF
chmod +x "$BIN_DIR/fake_ocr"

cat > "$BIN_DIR/whisper" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

input="$1"
shift
output_dir=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output_dir)
      output_dir="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

mkdir -p "$output_dir"
base="$(basename "${input%.*}")"
cat > "$output_dir/$base.srt" <<'SRT'
1
00:00:00,000 --> 00:00:01,000
无敏感内容
SRT
EOF
chmod +x "$BIN_DIR/whisper"

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=720x1280:d=32" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

PATH="$BIN_DIR:$PATH" VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
bash "$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_DIR" \
  --query "帮我剪辑这条视频" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

CUTS_FILE="$(find "$OUT_DIR" -type f -name 'cuts_refined.txt' | head -n 1)"
[[ -n "$CUTS_FILE" && -f "$CUTS_FILE" ]] || {
  echo "未生成 cuts_refined.txt" >&2
  exit 1
}

if ! awk '($1 <= 24.3 && $2 >= 29.1) { found=1 } END { exit !found }' "$CUTS_FILE"; then
  echo "价格闪帧区间扩边不足" >&2
  cat "$CUTS_FILE" >&2
  exit 1
fi

echo "test_price_flash_padding: PASS"
