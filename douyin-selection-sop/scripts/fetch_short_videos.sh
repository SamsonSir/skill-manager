#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  fetch_short_videos.sh --product-name "完整商品名" [选项]

选项:
  --cdp-port <port>        CDP 端口，默认 9222
  --category-3 <name>      三级类目名，搜索不到时回退“全部/不限”
  --output-dir <path>      输出目录，默认当前目录
  --download               立即下载 mp4（默认仅提取 URL）
  --max-videos <n>         最多提取 n 条，默认全部
  --extract-mode <mode>    提取模式：auto | data | tooltip，默认 auto
  --wait-ms <ms>           点击后等待播放器加载时间，默认 1200
  --help                   显示帮助
EOF
}

CDP_PORT="9222"
PRODUCT_NAME=""
CATEGORY_3=""
OUTPUT_DIR="."
DOWNLOAD="0"
MAX_VIDEOS="0"
EXTRACT_MODE="auto"
WAIT_MS="1200"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cdp-port)
      CDP_PORT="${2:-}"; shift 2 ;;
    --product-name)
      PRODUCT_NAME="${2:-}"; shift 2 ;;
    --category-3)
      CATEGORY_3="${2:-}"; shift 2 ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"; shift 2 ;;
    --download)
      DOWNLOAD="1"; shift ;;
    --max-videos)
      MAX_VIDEOS="${2:-0}"; shift 2 ;;
    --extract-mode)
      EXTRACT_MODE="${2:-auto}"; shift 2 ;;
    --wait-ms)
      WAIT_MS="${2:-1200}"; shift 2 ;;
    --help|-h)
      usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1 ;;
  esac
done

case "$EXTRACT_MODE" in
  auto|data|tooltip) ;;
  *)
    echo "--extract-mode 仅支持 auto | data | tooltip" >&2
    exit 1 ;;
esac

if [[ -z "$PRODUCT_NAME" ]]; then
  echo "缺少 --product-name" >&2
  usage
  exit 1
fi

for cmd in agent-browser jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "缺少依赖: $cmd" >&2
    exit 1
  fi
done

ab() { agent-browser --cdp "$CDP_PORT" "$@"; }

unjson() {
  local raw="$1"
  if echo "$raw" | jq -e . >/dev/null 2>&1; then
    echo "$raw" | jq -r 'if type=="string" then . else tostring end'
  else
    echo "$raw"
  fi
}

mkdir -p "$OUTPUT_DIR"
RUN_TS="$(date '+%Y%m%d_%H%M%S')"
MANIFEST_PATH="$OUTPUT_DIR/video_urls_${RUN_TS}.jsonl"
SUMMARY_PATH="$OUTPUT_DIR/video_fetch_summary_${RUN_TS}.json"
LATEST_SUMMARY_PATH="$OUTPUT_DIR/latest_video_fetch_summary.json"
SEEN_PATH="$(mktemp)"
trap 'rm -f "$SEEN_PATH"' EXIT

TAB_LIST="$(ab tab list || true)"
COMPASS_INDEX="$(echo "$TAB_LIST" | sed -nE 's/^[[:space:]]*[→ ]?\[([0-9]+)\].*compass\.jinritemai\.com\/shop\/chance\/rank-product.*/\1/p' | head -n 1)"
if [[ -n "$COMPASS_INDEX" ]]; then
  ab tab "$COMPASS_INDEX" >/dev/null
fi

CURRENT_URL="$(ab get url || true)"
if [[ "$CURRENT_URL" != *"compass.jinritemai.com/shop/chance/rank-product"* ]]; then
  echo "当前不在商品榜单页: $CURRENT_URL" >&2
  exit 1
fi

# 强制切到短视频榜并屏蔽 window.open，避免弹新标签页
ab eval '(() => {
  const tab = [...document.querySelectorAll("[role=\"tab\"]")].find(el => (el.textContent || "").includes("短视频榜"));
  if (tab) tab.click();
  try { window.open = () => null; } catch (_) {}
  return true;
})()' >/dev/null

PRODUCT_JSON="$(printf '%s' "$PRODUCT_NAME" | jq -Rs .)"
SEARCH_SET_RAW="$(ab eval "(() => {
  const input = [...document.querySelectorAll('input')]
    .find(el => (el.placeholder || '').includes('商品名'));
  if (!input) return false;
  input.focus();
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(input, '');
  input.dispatchEvent(new Event('input', { bubbles: true }));
  setter.call(input, $PRODUCT_JSON);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  return input.value;
})()")"
SEARCH_SET_VALUE="$(unjson "$SEARCH_SET_RAW")"
if [[ "$SEARCH_SET_VALUE" == "false" || "$SEARCH_SET_VALUE" != "$PRODUCT_NAME" ]]; then
  echo "商品搜索框写入失败: $PRODUCT_NAME" >&2
  exit 1
fi
ab press Enter >/dev/null || true
ab wait 1200 >/dev/null || true

DATA_PAYLOAD_RAW="$(ab eval "(() => {
  const product = $PRODUCT_JSON;
  const rows = [...document.querySelectorAll('tbody tr')]
    .filter(tr => tr.getAttribute('aria-hidden') !== 'true');
  const row = rows.find(tr => (tr.innerText || '').includes(product));
  const key = row && Object.keys(row).find(k => k.startsWith('__reactProps'));
  const rec = key ? row[key]?.children?.[0]?.props?.record : null;
  return JSON.stringify({
    detail_url: rec?.product_info?.product_detail_h5_url || '',
    rank: rec?.product_info?.rank ?? null,
    video_list: rec?.video_list || []
  });
})()")"
DATA_PAYLOAD="$(unjson "$DATA_PAYLOAD_RAW")"
DATA_TOTAL="$(jq -r '.video_list | length' <<<"$DATA_PAYLOAD" 2>/dev/null || echo 0)"

if [[ "$DATA_TOTAL" -gt 0 ]]; then
  DATA_TARGET_COUNT="$DATA_TOTAL"
  if [[ "$MAX_VIDEOS" -gt 0 ]] && [[ "$MAX_VIDEOS" -lt "$DATA_TARGET_COUNT" ]]; then
    DATA_TARGET_COUNT="$MAX_VIDEOS"
  fi

  SUCCESS_COUNT=0
  SKIP_COUNT=0
  FAIL_COUNT=0

  while IFS= read -r item; do
    INDEX_PADDED="$(printf '%02d' "$(jq -r '.index' <<<"$item")")"
    AWEME_ID="$(jq -r '.video_id // ""' <<<"$item")"
    SRC="$(jq -r '.video_play_url // ""' <<<"$item")"

    if [[ -z "$SRC" || "$SRC" != *"douyinvod.com"* || "$SRC" != *"video_mp4"* ]]; then
      SKIP_COUNT=$((SKIP_COUNT + 1))
      continue
    fi
    if grep -Fxq "$SRC" "$SEEN_PATH"; then
      SKIP_COUNT=$((SKIP_COUNT + 1))
      continue
    fi
    echo "$SRC" >>"$SEEN_PATH"

    FILE_ID="$AWEME_ID"
    if [[ -z "$FILE_ID" ]]; then
      FILE_ID="no_aweme"
    fi
    FILE_NAME="${INDEX_PADDED}_${FILE_ID}.mp4"
    FILE_PATH="$OUTPUT_DIR/$FILE_NAME"

    DOWNLOAD_STATUS="skipped"
    if [[ "$DOWNLOAD" == "1" ]]; then
      if curl -L --fail --retry 2 --retry-delay 1 --connect-timeout 10 --max-time 120 \
        -o "${FILE_PATH}.part" "$SRC" >/dev/null 2>&1; then
        mv "${FILE_PATH}.part" "$FILE_PATH"
        DOWNLOAD_STATUS="ok"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
      else
        rm -f "${FILE_PATH}.part"
        DOWNLOAD_STATUS="failed"
        FAIL_COUNT=$((FAIL_COUNT + 1))
      fi
    else
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi

    jq -nc \
      --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
      --arg product_name "$PRODUCT_NAME" \
      --arg category_3 "$CATEGORY_3" \
      --arg detail_url "$(jq -r '.detail_url // ""' <<<"$DATA_PAYLOAD")" \
      --argjson rank "$(jq -c '.rank // null' <<<"$DATA_PAYLOAD")" \
      --arg aweme_id "$AWEME_ID" \
      --arg video_url "$SRC" \
      --arg file_name "$FILE_NAME" \
      --arg output_dir "$OUTPUT_DIR" \
      --arg extract_method "data" \
      --arg download_status "$DOWNLOAD_STATUS" \
      '{ts:$ts,product_name:$product_name,category_3:$category_3,detail_url:$detail_url,rank:$rank,aweme_id:$aweme_id,video_url:$video_url,file_name:$file_name,output_dir:$output_dir,extract_method:$extract_method,download_status:$download_status}' \
      >>"$MANIFEST_PATH"
  done < <(jq -c --argjson target "$DATA_TARGET_COUNT" '.video_list[:$target] | to_entries[] | {index:(.key + 1), video_id:(.value.video_id // ""), video_play_url:(.value.video_play_url // "")}' <<<"$DATA_PAYLOAD")

  jq -nc \
    --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
    --arg product_name "$PRODUCT_NAME" \
    --arg category_3 "$CATEGORY_3" \
    --arg detail_url "$(jq -r '.detail_url // ""' <<<"$DATA_PAYLOAD")" \
    --argjson rank "$(jq -c '.rank // null' <<<"$DATA_PAYLOAD")" \
    --arg extract_method "data" \
    --argjson total "$DATA_TARGET_COUNT" \
    --argjson success "$SUCCESS_COUNT" \
    --argjson skipped "$SKIP_COUNT" \
    --argjson failed "$FAIL_COUNT" \
    --arg manifest_path "$MANIFEST_PATH" \
    --arg download_enabled "$DOWNLOAD" \
    '{ts:$ts,product_name:$product_name,category_3:$category_3,detail_url:$detail_url,rank:$rank,extract_method:$extract_method,total:$total,success:$success,skipped:$skipped,failed:$failed,download_enabled:($download_enabled=="1"),manifest_path:$manifest_path}' \
    | tee "$SUMMARY_PATH" >"$LATEST_SUMMARY_PATH"

  echo "SUMMARY_FILE=$SUMMARY_PATH"
  echo "MANIFEST_FILE=$MANIFEST_PATH"
  exit 0
fi

if [[ "${ALLOW_DOUYIN_OPEN_FALLBACK:-0}" != "1" ]]; then
  echo "页面数据层未找到 video_list，已跳过点击播放兜底以避免打开抖音前台页: $PRODUCT_NAME" >&2
  exit 1
fi

MORE_COUNT="0"
for _ in 1 2 3 4; do
  MORE_COUNT_RAW="$(ab eval '(() => document.querySelectorAll(".moreVideo-TqvRop").length)()')"
  MORE_COUNT="$(echo "$MORE_COUNT_RAW" | jq -r '.')"
  if [[ "$MORE_COUNT" -gt 0 ]]; then
    break
  fi
  ab wait 900 >/dev/null || true
done

if [[ "$MORE_COUNT" -eq 0 ]] && [[ -n "$CATEGORY_3" ]]; then
  CATEGORY_3_ESCAPED="$(printf '%s' "$CATEGORY_3" | sed "s/'/'\\\\''/g")"
  ab eval "(() => {
    const clickText = (txt) => {
      const node = [...document.querySelectorAll('*')]
        .find(el => (el.textContent || '').trim() === txt && el.offsetParent !== null);
      if (!node) return false;
      node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      return true;
    };
    clickText('$CATEGORY_3_ESCAPED');
    const ok = clickText('全部') || clickText('不限');
    return ok;
  })()" >/dev/null || true

  ab fill "input[placeholder*='商品名']" "$PRODUCT_NAME" >/dev/null || true
  ab press Enter >/dev/null || true
  ab wait 1200 >/dev/null || true
  for _ in 1 2 3 4; do
    MORE_COUNT_RAW="$(ab eval '(() => document.querySelectorAll(".moreVideo-TqvRop").length)()')"
    MORE_COUNT="$(echo "$MORE_COUNT_RAW" | jq -r '.')"
    if [[ "$MORE_COUNT" -gt 0 ]]; then
      break
    fi
    ab wait 900 >/dev/null || true
  done
fi

if [[ "$MORE_COUNT" -eq 0 ]]; then
  echo "搜索后未找到带货短视频入口: $PRODUCT_NAME" >&2
  exit 1
fi

ITEM_COUNT="0"
for _ in 1 2 3 4; do
  ab hover ".moreVideo-TqvRop" >/dev/null || true
  ab eval '(() => {
    const n = document.querySelector(".moreVideo-TqvRop");
    if (!n) return false;
    n.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
    n.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
    return true;
  })()' >/dev/null || true
  ab wait 700 >/dev/null || true
  ITEM_COUNT_RAW="$(ab eval '(() => document.querySelectorAll(".videoItem-RBYWeO").length)()')"
  ITEM_COUNT="$(echo "$ITEM_COUNT_RAW" | jq -r '.')"
  if [[ "$ITEM_COUNT" -gt 0 ]]; then
    break
  fi
done
if [[ "$ITEM_COUNT" -le 0 ]]; then
  echo "tooltip 中未发现 .videoItem-RBYWeO 项" >&2
  exit 1
fi

TARGET_COUNT="$ITEM_COUNT"
if [[ "$MAX_VIDEOS" -gt 0 ]] && [[ "$MAX_VIDEOS" -lt "$TARGET_COUNT" ]]; then
  TARGET_COUNT="$MAX_VIDEOS"
fi

SUCCESS_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0

for ((i=0; i<TARGET_COUNT; i++)); do
  AWEME_RAW="$(ab eval "(() => {
    const items = [...document.querySelectorAll('.videoItem-RBYWeO')];
    const item = items[$i];
    if (!item) return '';
    const html = item.innerHTML || '';
    const m = html.match(/video\\/(\\d{10,20})/);
    return m ? m[1] : '';
  })()")"
  AWEME_ID="$(unjson "$AWEME_RAW")"

  CLICK_RAW="$(ab eval "(() => {
    const btns = [...document.querySelectorAll('.playIcon-TsPgjF')];
    const btn = btns[$i];
    if (!btn) return false;
    btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    return true;
  })()")"
  CLICK_OK="$(echo "$CLICK_RAW" | jq -r '.')"
  if [[ "$CLICK_OK" != "true" ]]; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi

  ab wait "$WAIT_MS" >/dev/null || true
  SRC_RAW="$(ab eval '(() => {
    const v = document.querySelector("video");
    if (!v) return "";
    return v.currentSrc || v.src || "";
  })()')"
  SRC="$(unjson "$SRC_RAW")"

  if [[ -z "$SRC" || "$SRC" != *"douyinvod.com"* || "$SRC" != *"video_mp4"* ]]; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi
  if grep -Fxq "$SRC" "$SEEN_PATH"; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi
  echo "$SRC" >>"$SEEN_PATH"

  INDEX_PADDED="$(printf '%02d' $((i + 1)))"
  FILE_ID="$AWEME_ID"
  if [[ -z "$FILE_ID" ]]; then
    FILE_ID="no_aweme"
  fi
  FILE_NAME="${INDEX_PADDED}_${FILE_ID}.mp4"
  FILE_PATH="$OUTPUT_DIR/$FILE_NAME"

  DOWNLOAD_STATUS="skipped"
  if [[ "$DOWNLOAD" == "1" ]]; then
    if curl -L --fail --retry 2 --retry-delay 1 --connect-timeout 10 --max-time 120 \
      -o "${FILE_PATH}.part" "$SRC" >/dev/null 2>&1; then
      mv "${FILE_PATH}.part" "$FILE_PATH"
      DOWNLOAD_STATUS="ok"
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
      rm -f "${FILE_PATH}.part"
      DOWNLOAD_STATUS="failed"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
  else
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  fi

  jq -nc \
    --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
    --arg product_name "$PRODUCT_NAME" \
    --arg category_3 "$CATEGORY_3" \
    --arg aweme_id "$AWEME_ID" \
    --arg video_url "$SRC" \
    --arg file_name "$FILE_NAME" \
    --arg download_status "$DOWNLOAD_STATUS" \
    '{ts:$ts,product_name:$product_name,category_3:$category_3,aweme_id:$aweme_id,video_url:$video_url,file_name:$file_name,download_status:$download_status}' \
    >>"$MANIFEST_PATH"
done

jq -nc \
  --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
  --arg product_name "$PRODUCT_NAME" \
  --arg category_3 "$CATEGORY_3" \
  --argjson total "$TARGET_COUNT" \
  --argjson success "$SUCCESS_COUNT" \
  --argjson skipped "$SKIP_COUNT" \
  --argjson failed "$FAIL_COUNT" \
  --arg manifest_path "$MANIFEST_PATH" \
  --arg download_enabled "$DOWNLOAD" \
  '{ts:$ts,product_name:$product_name,category_3:$category_3,total:$total,success:$success,skipped:$skipped,failed:$failed,download_enabled:($download_enabled=="1"),manifest_path:$manifest_path}' \
  | tee "$SUMMARY_PATH" >"$LATEST_SUMMARY_PATH"

echo "SUMMARY_FILE=$SUMMARY_PATH"
echo "MANIFEST_FILE=$MANIFEST_PATH"
