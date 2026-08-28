#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/batch_clip_nl.sh"
TMP_DIR="$(mktemp -d)"
HOME_DIR="$TMP_DIR/home"
BIN_DIR="$TMP_DIR/bin"
VIDEO_PATH="$TMP_DIR/input.mp4"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$HOME_DIR/Desktop" "$BIN_DIR"

cat > "$BIN_DIR/fake_ocr" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
shift

case "$MODE" in
  --tsv)
    for path in "$@"; do
      printf '%s\t\n' "$path"
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

ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=720x1280:d=2" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

HOME="$HOME_DIR" VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
bash "$SCRIPT_PATH" \
  --root "$ROOT_DIR" \
  --query "把这条视频处理成能投流的版本" \
  --input "$VIDEO_PATH" \
  --dry-run \
  --keep-artifacts

DESKTOP_OUTPUT_ROOT="$HOME_DIR/Desktop/video_outputs"
[[ -d "$DESKTOP_OUTPUT_ROOT" ]] || {
  echo "默认桌面输出目录未创建: $DESKTOP_OUTPUT_ROOT" >&2
  exit 1
}

RUN_DIR_COUNT="$(find "$DESKTOP_OUTPUT_ROOT" -maxdepth 1 -type d -name 'run_*' | wc -l | tr -d ' ')"
if [[ "$RUN_DIR_COUNT" -lt 1 ]]; then
  echo "默认桌面输出目录下未生成 run_* 子目录" >&2
  find "$DESKTOP_OUTPUT_ROOT" -maxdepth 2 -print >&2 || true
  exit 1
fi

echo "test_default_output_root_desktop: PASS"
