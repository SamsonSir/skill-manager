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

cat > "$BIN_DIR/whisper" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

INPUT_PATH="$1"
shift

OUTPUT_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output_dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

[[ -n "$OUTPUT_DIR" ]] || {
  echo "missing --output_dir" >&2
  exit 1
}

mkdir -p "$OUTPUT_DIR"
BASE_NAME="$(basename "${INPUT_PATH%.*}")"
cat > "$OUTPUT_DIR/$BASE_NAME.srt" <<'SRT'
1
00:00:00,000 --> 00:00:01,000
这真是纯准减便一件大漏了

2
00:00:01,000 --> 00:00:02,000
之前这一条至少都卖八十九的

3
00:00:02,000 --> 00:00:03,000
裤子今天降价了哦

4
00:00:03,000 --> 00:00:04,000
这条裤子二十九张

5
00:00:04,000 --> 00:00:05,000
才二十来块钱的减卖
SRT
EOF
chmod +x "$BIN_DIR/whisper"

cat > "$BIN_DIR/fake_ocr" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
[[ "$MODE" == "--tsv" ]] || exit 1
shift
for path in "$@"; do
  printf '%s\t\n' "$path"
done
EOF
chmod +x "$BIN_DIR/fake_ocr"

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=720x1280:d=6" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

PATH="$BIN_DIR:$PATH" \
VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_DIR" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --keep-artifacts

ASR_HITS="$(find "$OUT_DIR" -type f -name 'asr_hits.txt' | head -n 1)"
[[ -n "$ASR_HITS" && -f "$ASR_HITS" ]] || {
  echo "未生成 asr_hits.txt" >&2
  exit 1
}

grep -q 'cheap_asr' "$ASR_HITS" || {
  echo "未命中错字便宜变体" >&2
  cat "$ASR_HITS" >&2 || true
  exit 1
}

PRICE_COUNT="$(grep -c 'price_asr' "$ASR_HITS" || true)"
if [[ "$PRICE_COUNT" -lt 4 ]]; then
  echo "价格口语变体命中不足: $PRICE_COUNT" >&2
  cat "$ASR_HITS" >&2 || true
  exit 1
fi

echo "test_asr_sales_variants: PASS"
