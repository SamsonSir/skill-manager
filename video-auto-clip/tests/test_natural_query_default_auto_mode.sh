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
  -f lavfi -i "color=c=black:s=720x1280:d=3" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_PATH"

run_case() {
  local query="$1"
  local case_out="$OUT_DIR/$(printf '%s' "$query" | md5 | awk '{print $1}')"

  VIDEO_AUTO_CLIP_OCR_BIN="$BIN_DIR/fake_ocr" \
  "$SCRIPT_PATH" \
    --root "$ROOT_DIR" \
    --output-root "$case_out" \
    --query "$query" \
    --input "$VIDEO_PATH" \
    --dry-run \
    --keep-artifacts

  local report
  report="$(find "$case_out" -type f -name '执行报告.md' | head -n 1)"
  [[ -n "$report" && -f "$report" ]] || {
    echo "未生成执行报告: $query" >&2
    exit 1
  }

  grep -q "自然语言指令: $query" "$report" || {
    echo "自然语言指令未写入报告: $query" >&2
    cat "$report" >&2
    exit 1
  }

  grep -q '自动识别目标: 平台尾卡、价格、便宜、抗菌、食品级、检测报告、功效宣称' "$report" || {
    echo "自然语言默认自动剪辑未启用旧版核心目标: $query" >&2
    cat "$report" >&2
    exit 1
  }
}

run_case "把这条视频处理成能投流的版本"
run_case "帮我剪辑这条视频"
run_case "使用剪辑技能处理这条视频"
run_case "把这批素材批量剪辑一下"

echo "test_natural_query_default_auto_mode: PASS"
