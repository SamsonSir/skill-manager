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
      if [[ "$path" == *coarse_full/frame_00002.jpg || "$path" == *coarse_bottom/frame_00002.jpg ]]; then
        text="卖你300多200多呢"
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
00:00:01,000 --> 00:00:03,000
你三百都是两百多
SRT
EOF
chmod +x "$BIN_DIR/whisper"

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

VISUAL_HITS="$(find "$OUT_DIR" -type f -name 'visual_hits.txt' | head -n 1)"
ASR_HITS="$(find "$OUT_DIR" -type f -name 'asr_hits.txt' | head -n 1)"

[[ -n "$VISUAL_HITS" && -f "$VISUAL_HITS" ]] || {
  echo "未生成 visual_hits.txt" >&2
  exit 1
}
[[ -n "$ASR_HITS" && -f "$ASR_HITS" ]] || {
  echo "未生成 asr_hits.txt" >&2
  exit 1
}

grep -q 'price_visual' "$VISUAL_HITS" || {
  echo "未命中 OCR 无单位多价位价格表达" >&2
  cat "$VISUAL_HITS" >&2 || true
  exit 1
}

grep -q 'price_asr' "$ASR_HITS" || {
  echo "未命中 ASR 中文多价位价格表达" >&2
  cat "$ASR_HITS" >&2 || true
  exit 1
}

echo "test_price_more_than_variants: PASS"
