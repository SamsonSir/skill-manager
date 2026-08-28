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
        printf '%s\td抖音 抖音号：57205855498 Q 财运公主小黄\n' "$path"
      else
        printf '%s\t\n' "$path"
      fi
    done
    ;;
  --regions-jsonl)
    for path in "$@"; do
      if [[ "$path" == *frame_00001.jpg* ]]; then
        printf '{"path":"%s","text":"d抖音 抖音号：57205855498 Q 财运公主小黄","regions":[{"text":"d抖音","x":0.036,"y":0.942,"width":0.192,"height":0.041},{"text":"抖音号：57205855498","x":0.022,"y":0.906,"width":0.369,"height":0.022},{"text":"Q 财运公主小黄","x":0.028,"y":0.873,"width":0.264,"height":0.021}]}\n' "$path"
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
  echo "长抖音号短店铺名左上角平台信息条未接入动态去水印: $DELOGO_COUNT" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
fi

echo "test_dynamic_top_left_delogo_long_id_short_shop: PASS"
