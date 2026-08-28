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
      printf '%s\t广告\n' "$path"
    done
    ;;
  --regions-jsonl)
    for path in "$@"; do
      printf '{"path":"%s","text":"广告","regions":[{"text":"广告","x":0.8722,"y":0.9578,"width":0.1056,"height":0.0344}]}\n' "$path"
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

grep -q 'delogo=x=609:y=2:w=109:h=78' "$FILTER_SCRIPT" || {
  echo "贴边广告框未正确收边" >&2
  cat "$FILTER_SCRIPT" >&2
  exit 1
}

echo "test_dynamic_top_right_delogo_clamps_edges: PASS"
