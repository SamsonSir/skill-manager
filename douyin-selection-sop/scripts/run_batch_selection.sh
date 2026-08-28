#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
用法:
  run_batch_selection.sh --queue-file <tasks.jsonl|tasks.csv> [选项]

队列字段:
  product_name   必填，完整商品名
  category_3     可选，三级类目（搜索不到会回退全部/不限）
  record_id      可选，飞书记录 ID（提供后会回写）
  status         可选，回写状态，默认 📝待评估

选项:
  --queue-file <path>       任务队列文件（jsonl 或 csv）
  --base-output-dir <path>  批量输出根目录，默认 ./deliverables/batch_<ts>
  --cdp-port <port>         默认 9222
  --download                直接下载视频（默认仅提取 URL）
  --max-videos <n>          单商品最多提取 n 条，默认全部
  --wait-ms <ms>            单次点击等待时长，默认 1200
  --skip-feishu             跳过飞书回写
  --help                    显示帮助
EOF
}

QUEUE_FILE=""
BASE_OUTPUT_DIR=""
CDP_PORT="9222"
DOWNLOAD="0"
MAX_VIDEOS="0"
WAIT_MS="1200"
SKIP_FEISHU="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --queue-file) QUEUE_FILE="${2:-}"; shift 2 ;;
    --base-output-dir) BASE_OUTPUT_DIR="${2:-}"; shift 2 ;;
    --cdp-port) CDP_PORT="${2:-}"; shift 2 ;;
    --download) DOWNLOAD="1"; shift ;;
    --max-videos) MAX_VIDEOS="${2:-0}"; shift 2 ;;
    --wait-ms) WAIT_MS="${2:-1200}"; shift 2 ;;
    --skip-feishu) SKIP_FEISHU="1"; shift ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$QUEUE_FILE" ]]; then
  echo "缺少 --queue-file" >&2
  usage
  exit 1
fi
if [[ ! -f "$QUEUE_FILE" ]]; then
  echo "队列文件不存在: $QUEUE_FILE" >&2
  exit 1
fi

for cmd in jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "缺少依赖: $cmd" >&2
    exit 1
  fi
done

RUN_TS="$(date '+%Y%m%d_%H%M%S')"
if [[ -z "$BASE_OUTPUT_DIR" ]]; then
  BASE_OUTPUT_DIR="$(pwd)/deliverables/batch_${RUN_TS}"
fi
mkdir -p "$BASE_OUTPUT_DIR"

RESULTS_JSONL="$BASE_OUTPUT_DIR/batch_results.jsonl"
SUMMARY_JSON="$BASE_OUTPUT_DIR/batch_summary.json"
: >"$RESULTS_JSONL"

SUCCESS=0
FAILED=0
TOTAL=0

slugify() {
  printf '%s' "$1" | tr ' /' '__' | tr -cd '[:alnum:]_-' | cut -c1-40
}

process_task() {
  local product_name="$1"
  local category_3="$2"
  local record_id="$3"
  local status="$4"

  TOTAL=$((TOTAL + 1))
  if [[ -z "$status" ]]; then
    status="📝待评估"
  fi

  local slug
  slug="$(slugify "$product_name")"
  if [[ -z "$slug" ]]; then
    slug="task_${TOTAL}"
  fi
  local task_dir="$BASE_OUTPUT_DIR/$(printf '%03d' "$TOTAL")_${slug}"
  mkdir -p "$task_dir"

  local fetch_cmd=(
    bash "$SCRIPT_DIR/fetch_short_videos.sh"
    --cdp-port "$CDP_PORT"
    --product-name "$product_name"
    --output-dir "$task_dir/带货视频"
    --max-videos "$MAX_VIDEOS"
    --wait-ms "$WAIT_MS"
  )
  if [[ -n "$category_3" ]]; then
    fetch_cmd+=(--category-3 "$category_3")
  fi
  if [[ "$DOWNLOAD" == "1" ]]; then
    fetch_cmd+=(--download)
  fi

  local fetch_log="$task_dir/fetch.log"
  if "${fetch_cmd[@]}" >"$fetch_log" 2>&1; then
    SUCCESS=$((SUCCESS + 1))
    local summary_file
    summary_file="$(sed -n 's/^SUMMARY_FILE=//p' "$fetch_log" | tail -n1)"
    local note="批量提取完成"
    if [[ -n "$summary_file" ]] && [[ -f "$summary_file" ]]; then
      note="$(jq -r '"批量提取完成: success=\(.success), skipped=\(.skipped), failed=\(.failed), total=\(.total)"' "$summary_file")"
    fi

    if [[ "$SKIP_FEISHU" != "1" ]] && [[ -n "$record_id" ]]; then
      bash "$SCRIPT_DIR/sync_feishu_selection.sh" \
        --record-id "$record_id" \
        --status "$status" \
        --note-append "$note" >/dev/null 2>&1 || true
    fi

    jq -nc \
      --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
      --arg product_name "$product_name" \
      --arg category_3 "$category_3" \
      --arg record_id "$record_id" \
      --arg status "$status" \
      --arg task_dir "$task_dir" \
      --arg fetch_log "$fetch_log" \
      '{ts:$ts,result:"ok",product_name:$product_name,category_3:$category_3,record_id:$record_id,status:$status,task_dir:$task_dir,fetch_log:$fetch_log}' \
      >>"$RESULTS_JSONL"
  else
    FAILED=$((FAILED + 1))
    jq -nc \
      --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
      --arg product_name "$product_name" \
      --arg category_3 "$category_3" \
      --arg record_id "$record_id" \
      --arg status "$status" \
      --arg task_dir "$task_dir" \
      --arg fetch_log "$fetch_log" \
      '{ts:$ts,result:"failed",product_name:$product_name,category_3:$category_3,record_id:$record_id,status:$status,task_dir:$task_dir,fetch_log:$fetch_log}' \
      >>"$RESULTS_JSONL"
  fi
}

if [[ "$QUEUE_FILE" == *.jsonl ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    product_name="$(echo "$line" | jq -r '.product_name // .["商品名称"] // empty')"
    category_3="$(echo "$line" | jq -r '.category_3 // .["三级类目"] // empty')"
    record_id="$(echo "$line" | jq -r '.record_id // .["记录ID"] // empty')"
    status="$(echo "$line" | jq -r '.status // .["选品状态"] // empty')"
    if [[ -z "$product_name" ]]; then
      continue
    fi
    process_task "$product_name" "$category_3" "$record_id" "$status"
  done <"$QUEUE_FILE"
else
  # 轻量 CSV 解析：不处理带引号逗号转义，批量队列建议优先 jsonl
  header="$(head -n 1 "$QUEUE_FILE")"
  IFS=',' read -r -a cols <<<"$header"
  idx_product=-1
  idx_category=-1
  idx_record=-1
  idx_status=-1
  for i in "${!cols[@]}"; do
    name="$(echo "${cols[$i]}" | tr -d '\r' | xargs)"
    [[ "$name" == "product_name" || "$name" == "商品名称" ]] && idx_product="$i"
    [[ "$name" == "category_3" || "$name" == "三级类目" ]] && idx_category="$i"
    [[ "$name" == "record_id" || "$name" == "记录ID" ]] && idx_record="$i"
    [[ "$name" == "status" || "$name" == "选品状态" ]] && idx_status="$i"
  done
  if [[ "$idx_product" -lt 0 ]]; then
    echo "CSV 缺少 product_name/商品名称 列" >&2
    exit 1
  fi
  while IFS=',' read -r -a row; do
    product_name="$(echo "${row[$idx_product]:-}" | xargs)"
    [[ -z "$product_name" ]] && continue
    category_3=""
    record_id=""
    status=""
    [[ "$idx_category" -ge 0 ]] && category_3="$(echo "${row[$idx_category]:-}" | xargs)"
    [[ "$idx_record" -ge 0 ]] && record_id="$(echo "${row[$idx_record]:-}" | xargs)"
    [[ "$idx_status" -ge 0 ]] && status="$(echo "${row[$idx_status]:-}" | xargs)"
    process_task "$product_name" "$category_3" "$record_id" "$status"
  done < <(tail -n +2 "$QUEUE_FILE")
fi

jq -nc \
  --arg ts "$(date '+%Y-%m-%d %H:%M:%S')" \
  --arg queue_file "$QUEUE_FILE" \
  --arg base_output_dir "$BASE_OUTPUT_DIR" \
  --argjson total "$TOTAL" \
  --argjson success "$SUCCESS" \
  --argjson failed "$FAILED" \
  --arg results_jsonl "$RESULTS_JSONL" \
  '{ts:$ts,queue_file:$queue_file,base_output_dir:$base_output_dir,total:$total,success:$success,failed:$failed,results_jsonl:$results_jsonl}' \
  | tee "$SUMMARY_JSON"

echo "BATCH_RESULTS=$RESULTS_JSONL"
echo "BATCH_SUMMARY=$SUMMARY_JSON"
