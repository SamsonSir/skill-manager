#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/batch_clip_nl.sh"
TMP_DIR="$(mktemp -d)"
BIN_DIR="$TMP_DIR/bin"
CACHE_DIR="$TMP_DIR/cache"
COUNT_FILE="$TMP_DIR/whisper_count.txt"
VIDEO_PATH="$TMP_DIR/input.mp4"
OUT_ONE="$TMP_DIR/out_one"
OUT_TWO="$TMP_DIR/out_two"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$BIN_DIR" "$CACHE_DIR"

cat > "$BIN_DIR/whisper" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

COUNT_FILE="${TEST_WHISPER_COUNT_FILE:?}"
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
printf '1\n' >> "$COUNT_FILE"
BASE_NAME="$(basename "${INPUT_PATH%.*}")"
cat > "$OUTPUT_DIR/$BASE_NAME.srt" <<'SRT'
1
00:00:00,000 --> 00:00:00,500
普通口播内容
SRT
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
TEST_WHISPER_COUNT_FILE="$COUNT_FILE" \
VIDEO_AUTO_CLIP_ASR_CACHE_DIR="$CACHE_DIR" \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_ONE" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

PATH="$BIN_DIR:$PATH" \
TEST_WHISPER_COUNT_FILE="$COUNT_FILE" \
VIDEO_AUTO_CLIP_ASR_CACHE_DIR="$CACHE_DIR" \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_TWO" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

INVOCATIONS="$(wc -l < "$COUNT_FILE" | tr -d ' ')"
if [[ "$INVOCATIONS" != "1" ]]; then
  echo "whisper 调用次数异常: $INVOCATIONS" >&2
  exit 1
fi

SECOND_REPORT="$(find "$OUT_TWO" -type f -name '执行报告.md' | head -n 1)"
grep -Fq 'ASR缓存: hit' "$SECOND_REPORT" || {
  echo "第二次运行未命中 ASR 缓存" >&2
  exit 1
}

CACHE_FILE_COUNT="$(find "$CACHE_DIR" -type f -name '*.srt' | wc -l | tr -d ' ')"
if [[ "$CACHE_FILE_COUNT" != "1" ]]; then
  echo "ASR 缓存文件数量异常: $CACHE_FILE_COUNT" >&2
  exit 1
fi

echo "test_asr_cache_reuse: PASS"
