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
      if [[ "$path" == *frame_00001.jpg* ]]; then
        printf '%s\t抖音 抖音号：43838026974 Q a苏姐 身高：165cm 体重：105斤\n' "$path"
      else
        printf '%s\t\n' "$path"
      fi
    done
    ;;
  --regions-jsonl)
    for path in "$@"; do
      if [[ "$path" == *frame_00001.jpg* ]]; then
        printf '{"path":"%s","text":"抖音 抖音号：43838026974 Q a苏姐 身高：165cm 体重：105斤","regions":[{"text":"抖音","x":0.10,"y":0.94,"width":0.12,"height":0.032},{"text":"抖音号：43838026974","x":0.01,"y":0.908,"width":0.39,"height":0.020},{"text":"Q a苏姐","x":0.03,"y":0.873,"width":0.14,"height":0.022},{"text":"身高：165cm","x":0.00,"y":0.842,"width":0.22,"height":0.026},{"text":"体重：105斤","x":0.00,"y":0.801,"width":0.20,"height":0.028}]}\n' "$path"
      else
        printf '{"path":"%s","text":"","regions":[]}\n' "$path"
      fi
    done
    ;;
  *)
    exit 1
    ;;
esac
EOF
chmod +x "$BIN_DIR/fake_ocr"

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=720x1280:d=3" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
VIDEO_AUTO_CLIP_OCR_CACHE_DIR="$TMP_DIR/ocr-cache" \
"$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --output-root "$OUT_DIR" \
  --query "按skill剪辑" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

FILTER_SCRIPT="$(find "$OUT_DIR" -type f -name 'filter_complex.txt' | head -n 1)"
[[ -n "$FILTER_SCRIPT" && -f "$FILTER_SCRIPT" ]] || {
  echo "未生成 filter_complex.txt" >&2
  exit 1
}

DELOGO_COUNT="$(grep -c 'delogo=' "$FILTER_SCRIPT" || true)"
if [[ "$DELOGO_COUNT" -ne 2 ]]; then
  echo "真实左上角平台信息条未接入动态去水印: $DELOGO_COUNT" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
fi

grep -q "enable='between(t,0,5)'" "$FILTER_SCRIPT" || {
  echo "左上角动态去水印缺少前 5 秒限制" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
}

if grep -Eq 'delogo=x=[0-9]+:y=[0-9]+:w=[0-9]+:h=2[5-9][0-9]' "$FILTER_SCRIPT"; then
  echo "左上角去水印框误包含身高体重信息，框过高" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
fi

echo "test_dynamic_top_left_delogo_realistic_stack: PASS"
