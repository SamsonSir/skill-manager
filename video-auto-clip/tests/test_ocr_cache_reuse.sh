#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/batch_clip_nl.sh"
TMP_DIR="$(mktemp -d)"
BIN_DIR="$TMP_DIR/bin"
CACHE_DIR="$TMP_DIR/cache"
COUNT_FILE="$TMP_DIR/ocr_count.txt"
VIDEO_PATH="$TMP_DIR/input.mp4"
OUT_ONE="$TMP_DIR/out_one"
OUT_TWO="$TMP_DIR/out_two"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$BIN_DIR" "$CACHE_DIR"
: > "$COUNT_FILE"

cat > "$BIN_DIR/fake_ocr" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

COUNT_FILE="${TEST_OCR_COUNT_FILE:?}"
MODE="${1:-}"
[[ "$MODE" == "--tsv" ]] || {
  echo "only --tsv is supported" >&2
  exit 1
}
shift

printf '1\n' >> "$COUNT_FILE"
for path in "$@"; do
  printf '%s\t售价99元\n' "$path"
done
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

[[ -n "$OUTPUT_DIR" ]] || exit 1
mkdir -p "$OUTPUT_DIR"
BASE_NAME="$(basename "${INPUT_PATH%.*}")"
: > "$OUTPUT_DIR/$BASE_NAME.srt"
EOF
chmod +x "$BIN_DIR/whisper"

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=720x1280:d=3" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

PATH="$BIN_DIR:$PATH" \
TEST_OCR_COUNT_FILE="$COUNT_FILE" \
VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
VIDEO_AUTO_CLIP_OCR_CACHE_DIR="$CACHE_DIR" \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_ONE" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

FIRST_INVOCATIONS="$(wc -l < "$COUNT_FILE" | tr -d ' ')"
if [[ "$FIRST_INVOCATIONS" == "0" ]]; then
  echo "第一次运行未调用 OCR 包装器" >&2
  exit 1
fi

PATH="$BIN_DIR:$PATH" \
TEST_OCR_COUNT_FILE="$COUNT_FILE" \
VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
VIDEO_AUTO_CLIP_OCR_CACHE_DIR="$CACHE_DIR" \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_TWO" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

SECOND_INVOCATIONS="$(wc -l < "$COUNT_FILE" | tr -d ' ')"
if [[ "$SECOND_INVOCATIONS" != "$FIRST_INVOCATIONS" ]]; then
  echo "第二次运行未完全命中 OCR 缓存: $FIRST_INVOCATIONS -> $SECOND_INVOCATIONS" >&2
  exit 1
fi

SECOND_REPORT="$(find "$OUT_TWO" -type f -name '执行报告.md' | head -n 1)"
grep -Fq 'OCR缓存: hit=' "$SECOND_REPORT" || {
  echo "第二次运行未记录 OCR 缓存命中" >&2
  exit 1
}

SECOND_COARSE_TSV="$(find "$OUT_TWO" -type f -name 'coarse_full.tsv' | head -n 1)"
[[ -n "$SECOND_COARSE_TSV" && -f "$SECOND_COARSE_TSV" ]] || {
  echo "第二次运行未生成 coarse_full.tsv" >&2
  exit 1
}
if ! awk -F'\t' -v root="$OUT_TWO" 'NF >= 1 && index($1, root) != 1 { bad=1 } END { exit bad }' "$SECOND_COARSE_TSV"; then
  echo "OCR 缓存命中后仍保留旧运行目录路径" >&2
  cat "$SECOND_COARSE_TSV" >&2
  exit 1
fi

CACHE_FILE_COUNT="$(find "$CACHE_DIR" -type f -name '*.tsv' | wc -l | tr -d ' ')"
if [[ "$CACHE_FILE_COUNT" -eq 0 ]]; then
  echo "OCR 缓存文件未生成" >&2
  exit 1
fi

echo "test_ocr_cache_reuse: PASS"
