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
        printf '%s\t抖音 抖音号：mxrj_ Q OMEM韩系女主私服店\n' "$path"
      else
        printf '%s\t\n' "$path"
      fi
    done
    ;;
  --regions-jsonl)
    for path in "$@"; do
      if [[ "$path" == *frame_00001.jpg* ]]; then
        printf '{"path":"%s","text":"抖音 抖音号：mxrj_ Q OMEM韩系女主私服店","regions":[{"text":"抖音","x":0.03,"y":0.94,"width":0.19,"height":0.045},{"text":"抖音号：mxrj_","x":0.02,"y":0.904,"width":0.23,"height":0.026},{"text":"Q OMEM韩系女主私服店","x":0.028,"y":0.873,"width":0.42,"height":0.022}]}\n' "$path"
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
  echo "三行左上角平台信息条未接入动态去水印: $DELOGO_COUNT" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
fi

grep -q "enable='between(t,0,5)'" "$FILTER_SCRIPT" || {
  echo "左上角动态去水印缺少前 5 秒限制" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
}

echo "test_dynamic_top_left_delogo_three_line: PASS"
