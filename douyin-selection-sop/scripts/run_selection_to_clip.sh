#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_PROJECT_DIR="$HOME/Documents/JokerSu-knowledge/20_项目/抖音电商选品流程跑通"
if [[ "$SCRIPT_DIR" == *"/.agents/skills/douyin-selection-sop/scripts" ]]; then
  PROJECT_DIR="${DOUYIN_SELECTION_PROJECT_DIR:-$DEFAULT_PROJECT_DIR}"
else
  PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi
AGENTS_SKILL_ROOT="${AGENTS_SKILL_ROOT:-$HOME/.agents/skills}"
CLIP_SCRIPT="${DOUYIN_SELECTION_CLIP_SCRIPT:-$AGENTS_SKILL_ROOT/video-auto-clip/scripts/batch_clip_nl.sh}"
FEISHU_NOTIFY_SCRIPT="${FEISHU_NOTIFY_SCRIPT:-$AGENTS_SKILL_ROOT/feishu-meeting-call/scripts/feishu_meeting.py}"
LARK_CLI_CONFIG="${LARK_CLI_CONFIG:-$HOME/.lark-cli/config.json}"
FEISHU_BASE_TOKEN="${DOUYIN_SELECTION_FEISHU_BASE_TOKEN:-QqKbbaGvvah8CgsMSWzcHZcMn1c}"
FEISHU_TABLE_ID="${DOUYIN_SELECTION_FEISHU_TABLE_ID:-tblmnpex440PHytL}"
COMMON_SCRIPT="$SCRIPT_DIR/run_selection_common.sh"
SCORING_SCRIPT="$SCRIPT_DIR/selection_scoring.sh"
MATERIAL_PROBE_SCRIPT="$SCRIPT_DIR/selection_material_probe.sh"

usage() {
  cat <<'EOF'
用法:
  run_selection_to_clip.sh --query "给 Mono拾梦坊跑3个候选" [选项]

说明:
  - 默认完整链路：候选采集 -> 历史去重 -> 预筛 -> 下载 -> 剪辑 -> 通知
  - 默认历史去重开启，只有用户明确允许重复跑时才关闭
  - 失败项最多自动重跑 2 次；第 3 次仍失败会生成失败记录

选项:
  --query <text>             自然语言任务
  --cdp-port <port>          浏览器 CDP 端口，默认 9222
  --output-root <path>       输出目录，默认 deliverables/runs/<ts>_<shop>
  --max-videos <n>           单商品最多下载 n 条视频，默认 10
  --clip-workers <n>         预留参数，默认 2
  --skip-feishu              跳过飞书入库
  --no-notify                跳过飞书加急通知
  --help                     显示帮助
EOF
}

QUERY=""
CDP_PORT="9222"
OUTPUT_ROOT=""
MAX_VIDEOS="10"
CLIP_WORKERS="2"
NO_NOTIFY="0"
SKIP_FEISHU="0"
PHONE_NOTIFY="0"
RUN_FINALIZED="0"
NOTIFY_SENT="0"
CURRENT_STAGE="bootstrap"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query) QUERY="${2:-}"; shift 2 ;;
    --cdp-port) CDP_PORT="${2:-9222}"; shift 2 ;;
    --output-root) OUTPUT_ROOT="${2:-}"; shift 2 ;;
    --max-videos) MAX_VIDEOS="${2:-10}"; shift 2 ;;
    --clip-workers) CLIP_WORKERS="${2:-2}"; shift 2 ;;
    --skip-feishu) SKIP_FEISHU="1"; shift ;;
    --no-notify) NO_NOTIFY="1"; shift ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "缺少 --query" >&2
  usage
  exit 1
fi

for cmd in jq perl python3 agent-browser lark-cli ffmpeg ffprobe; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "缺少依赖: $cmd" >&2
    exit 1
  fi
done

if [[ ! -f "$CLIP_SCRIPT" ]]; then
  echo "剪辑脚本不存在: $CLIP_SCRIPT" >&2
  exit 1
fi
if [[ ! -f "$COMMON_SCRIPT" ]]; then
  echo "公共脚本不存在: $COMMON_SCRIPT" >&2
  exit 1
fi
if [[ ! -f "$SCORING_SCRIPT" ]]; then
  echo "评分脚本不存在: $SCORING_SCRIPT" >&2
  exit 1
fi
if [[ ! -f "$MATERIAL_PROBE_SCRIPT" ]]; then
  echo "素材探测脚本不存在: $MATERIAL_PROBE_SCRIPT" >&2
  exit 1
fi

source "$COMMON_SCRIPT"
source "$SCORING_SCRIPT"
source "$MATERIAL_PROBE_SCRIPT"

ab() { agent-browser --cdp "$CDP_PORT" "$@"; }

unjson() {
  local raw="$1"
  if echo "$raw" | jq -e . >/dev/null 2>&1; then
    echo "$raw" | jq -r 'if type=="string" then . else tostring end'
  else
    echo "$raw"
  fi
}

normalize_name() {
  printf '%s' "$1" | tr -d '[:space:]'
}

slugify_ascii() {
  printf '%s' "$1" | tr ' /' '__' | tr -cd '[:alnum:]_-' | sed 's/__\+/_/g' | cut -c1-40
}

json_escape() {
  jq -Rn --arg v "$1" '$v'
}

video_dimensions() {
  ffprobe -v error \
    -select_streams v:0 \
    -show_entries stream=width,height \
    -of csv=s=x:p=0 \
    "$1"
}

ensure_qianchuan_9x16() {
  local input_path="$1"
  local dims width height tmp_path
  dims="$(video_dimensions "$input_path" || true)"
  width="${dims%x*}"
  height="${dims#*x}"

  if [[ "$width" == "720" && "$height" == "1280" ]]; then
    return 0
  fi
  if [[ "$width" == "1080" && "$height" == "1920" ]]; then
    return 0
  fi

  tmp_path="${input_path%.mp4}.qianchuan_tmp.mp4"
  ffmpeg -y \
    -i "$input_path" \
    -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" \
    -c:v libx264 \
    -profile:v high \
    -level 4.0 \
    -pix_fmt yuv420p \
    -c:a aac \
    -movflags +faststart \
    "$tmp_path" >/dev/null 2>&1
  mv "$tmp_path" "$input_path"

  dims="$(video_dimensions "$input_path")"
  if [[ "$dims" != "720x1280" && "$dims" != "1080x1920" ]]; then
    echo "9:16 规范化失败: $input_path -> $dims" >&2
    return 1
  fi
}

query_matches() {
  local pattern="$1"
  printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne "exit(!(/$pattern/))"
}

SHOP_NAME="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/给\s*([^\s，,]+)\s*跑/){print $1; exit}')"
CANDIDATE_LIMIT="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/跑\s*([0-9]+)\s*个候选/){print $1; exit}')"
CATEGORY_HINT="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/跑\s*[0-9]+\s*个([^候选，,]+)候选/){print $1; exit}')"
CLIP_SUFFIX="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/(剪掉.+)$/){print $1; exit}')"

if [[ -z "$SHOP_NAME" || -z "$CANDIDATE_LIMIT" ]]; then
  echo "当前只支持类似“给 Mono拾梦坊跑3个候选”的口径" >&2
  exit 1
fi
if ! [[ "$CANDIDATE_LIMIT" =~ ^[0-9]+$ ]] || [[ "$CANDIDATE_LIMIT" -le 0 ]]; then
  echo "候选数量必须是正整数" >&2
  exit 1
fi
if ! [[ "$MAX_VIDEOS" =~ ^[0-9]+$ ]] || [[ "$MAX_VIDEOS" -le 0 ]]; then
  echo "--max-videos 必须是正整数" >&2
  exit 1
fi
if ! [[ "$CLIP_WORKERS" =~ ^[0-9]+$ ]] || [[ "$CLIP_WORKERS" -le 0 ]]; then
  echo "--clip-workers 必须是正整数" >&2
  exit 1
fi

ALLOW_REPEAT="0"
if query_matches '允许重复跑|包含历史跑过的商品|老商品也重新跑一遍|允许重复'; then
  ALLOW_REPEAT="1"
fi
ALLOW_FEISHU_REPEAT="0"
if query_matches '允许飞书重复|飞书已有也重新跑|包含飞书已有商品|飞书重复'; then
  ALLOW_FEISHU_REPEAT="1"
fi

if query_matches '电话通知|电话加急|打电话给我|电话提醒|打我电话'; then
  PHONE_NOTIFY="1"
fi

CLIP_QUERY="按skill剪辑"
if [[ -n "$CLIP_SUFFIX" ]]; then
  CLIP_QUERY="按skill剪辑，$CLIP_SUFFIX"
fi

RUN_TS="$(date '+%Y%m%d_%H%M%S')"
RUN_DATE="$(date '+%Y-%m-%d')"
SHOP_SLUG="$(slugify_ascii "$SHOP_NAME")"
if [[ -z "$SHOP_SLUG" ]]; then
  SHOP_SLUG="shop"
fi
if [[ -z "$OUTPUT_ROOT" ]]; then
  OUTPUT_ROOT="$PROJECT_DIR/deliverables/runs/${RUN_TS}_${SHOP_SLUG}"
fi

RUNTIME_DIR="$OUTPUT_ROOT/.runtime"
PRODUCTS_DIR="$OUTPUT_ROOT/products"
CLIP_OUTPUT_DIR="$OUTPUT_ROOT/clip_outputs"
LOG_DIR="$RUNTIME_DIR/logs"
mkdir -p "$RUNTIME_DIR" "$PRODUCTS_DIR" "$CLIP_OUTPUT_DIR" "$LOG_DIR"
DAILY_REPORT_PATH="$PRODUCTS_DIR/商品报告_${RUN_DATE}.md"

RUN_STATE_JSON="$RUNTIME_DIR/run_state.json"
RETRY_STATE_JSON="$RUNTIME_DIR/retry_state.json"
CHECKPOINT_JSON="$RUNTIME_DIR/checkpoint.json"
SELECTED_JSONL="$RUNTIME_DIR/selected_candidates.jsonl"
DOWNLOAD_RESULTS_JSONL="$RUNTIME_DIR/download_results.jsonl"
CLIP_RESULTS_JSONL="$RUNTIME_DIR/clip_results.jsonl"
TERMINAL_FAILURES_JSONL="$RUNTIME_DIR/terminal_failures.jsonl"
HISTORY_NORMALIZED="$RUNTIME_DIR/history_names.normalized.txt"
HISTORY_RAW="$RUNTIME_DIR/history_names.txt"
FEISHU_EXISTING_MAP="$RUNTIME_DIR/feishu_existing_records.tsv"
FEISHU_SYNC_RESULTS_JSONL="$RUNTIME_DIR/feishu_sync_results.jsonl"
FEISHU_FIELDS_JSON="$RUNTIME_DIR/feishu_fields.json"
MANUAL_HISTORY_FILE="$PROJECT_DIR/deliverables/manual_history_names.txt"

: > "$SELECTED_JSONL"
: > "$DOWNLOAD_RESULTS_JSONL"
: > "$CLIP_RESULTS_JSONL"
: > "$TERMINAL_FAILURES_JSONL"
: > "$HISTORY_NORMALIZED"
: > "$HISTORY_RAW"
: > "$FEISHU_EXISTING_MAP"
: > "$FEISHU_SYNC_RESULTS_JSONL"

archive_previous_failed_runs "$PROJECT_DIR/deliverables/runs" "$SHOP_SLUG" "$OUTPUT_ROOT"

collect_history_names() {
  local file

  if [[ -f "$MANUAL_HISTORY_FILE" ]]; then
    sed '/^[[:space:]]*$/d' "$MANUAL_HISTORY_FILE" 2>/dev/null || true
  fi

  while IFS= read -r file; do
    jq -r '.[]?.name // empty' "$file" 2>/dev/null || true
  done < <(find "$PROJECT_DIR/deliverables" -type f -name '通过商品明细.json' 2>/dev/null | sort)

  while IFS= read -r file; do
    perl -ne 'print "$1\n" if /^\d+\.\s+`(.+)`/' "$file" 2>/dev/null || true
  done < <(find "$PROJECT_DIR/deliverables" -type f -name '*20商品爆品潜质测试.md' 2>/dev/null | sort)

  while IFS= read -r file; do
    sed -n \
      -e 's/^- 商品名：//p' \
      -e 's/^## 商品：//p' \
      "$file" 2>/dev/null || true
  done < <(find "$PROJECT_DIR/deliverables" -type f \( -name '商品参数报告.md' -o -name '商品报告_*.md' \) 2>/dev/null | sort)

  while IFS= read -r file; do
    jq -r '.processed_products[]?.name // empty' "$file" 2>/dev/null || true
  done < <(find "$PROJECT_DIR/deliverables/runs" -type f -path '*/.runtime/run_state.json' 2>/dev/null | sort)

  while IFS= read -r file; do
    jq -r '.name // empty' "$file" 2>/dev/null || true
  done < <(find "$PROJECT_DIR/deliverables/runs" -type f -path '*/.runtime/selected_candidates.jsonl' 2>/dev/null | sort)

  while IFS= read -r file; do
    jq -r '.name // empty' "$file" 2>/dev/null || true
  done < <(find "$PROJECT_DIR/deliverables/runs" -type f -path '*/.runtime/download_results.jsonl' 2>/dev/null | sort)
}

refresh_history_names() {
  collect_history_names | sed '/^[[:space:]]*$/d' | sort -u > "$HISTORY_RAW"

  if declare -F load_feishu_existing_map >/dev/null 2>&1; then
    load_feishu_existing_map
    cut -f2 "$FEISHU_EXISTING_MAP" 2>/dev/null | sed '/^[[:space:]]*$/d' | sort -u >> "$HISTORY_RAW" || true
  fi

  sort -u -o "$HISTORY_RAW" "$HISTORY_RAW"
  while IFS= read -r name; do
    normalize_name "$name"
    printf '\n'
  done < "$HISTORY_RAW" | sed '/^[[:space:]]*$/d' | sort -u > "$HISTORY_NORMALIZED"
}

history_has_name() {
  local normalized
  normalized="$(normalize_name "$1")"
  grep -Fxq "$normalized" "$HISTORY_NORMALIZED"
}

ensure_compass_short_video_page() {
  ab open "https://compass.jinritemai.com/shop/chance/rank-product" >/dev/null
  ab wait 2000 >/dev/null || true
  ab eval '(() => {
    const tab = [...document.querySelectorAll("[role=\"tab\"]")]
      .find(el => (el.textContent || "").includes("短视频榜"));
    if (tab) tab.click();
    return true;
  })()' >/dev/null
  ab wait 2000 >/dev/null || true
}

collect_current_page_rows() {
  local raw payload
  raw="$(ab eval '(() => {
    const readLow = node => node?.value_range?.[0]?.value ?? 0;
    const readHigh = node => node?.value_range?.[1]?.value ?? 0;
    const collectRow = tr => {
      const key = Object.keys(tr).find(k => k.startsWith("__reactProps"));
      const rec = tr[key]?.children?.[0]?.props?.record || null;
      if (!rec || !rec.product_info) return null;
      return {
        name: rec.product_info.name || "",
        rank: rec.product_info.rank ?? null,
        detail_url: rec.product_info.product_detail_h5_url || "",
        price_bin: rec.product_info.price_bin || "",
        newly_on_ranking: !!rec.product_info.newly_on_ranking,
        pay_amt_low: readLow(rec.pay_amt),
        pay_amt_high: readHigh(rec.pay_amt),
        clicks_low: readLow(rec.product_click_cnt),
        clicks_high: readHigh(rec.product_click_cnt),
        combo_low: readLow(rec.pay_combo_cnt),
        combo_high: readHigh(rec.pay_combo_cnt),
        video_low: readLow(rec.video_cnt),
        video_high: readHigh(rec.video_cnt)
      };
    };
    const visibleRows = () => [...document.querySelectorAll("tbody tr")]
      .filter(tr => tr.getAttribute("aria-hidden") !== "true");
    const findScrollContainer = () => {
      let node = document.querySelector("tbody");
      while (node) {
        const style = window.getComputedStyle(node);
        if (
          /(auto|scroll)/.test(style.overflowY || "") &&
          node.scrollHeight > node.clientHeight + 40
        ) {
          return node;
        }
        node = node.parentElement;
      }
      return document.scrollingElement || document.documentElement;
    };
    const seen = new Map();
    const collectVisibleRows = () => {
      visibleRows().forEach(tr => {
        const row = collectRow(tr);
        if (!row || !row.name) return;
        if (!seen.has(row.name)) seen.set(row.name, row);
      });
    };

    const scroller = findScrollContainer();
    const originalTop = scroller?.scrollTop || 0;
    const maxScroll = scroller ? Math.max(scroller.scrollHeight - scroller.clientHeight, 0) : 0;

    collectVisibleRows();
    if (scroller && maxScroll > 0) {
      for (let pass = 0; pass < 12; pass += 1) {
        const nextTop = Math.min(maxScroll, Math.round(maxScroll * ((pass + 1) / 12)));
        scroller.scrollTop = nextTop;
        scroller.dispatchEvent(new Event("scroll", { bubbles: true }));
        void scroller.offsetHeight;
        collectVisibleRows();
        if (nextTop >= maxScroll) break;
      }
      scroller.scrollTop = originalTop;
      scroller.dispatchEvent(new Event("scroll", { bubbles: true }));
      void scroller.offsetHeight;
      collectVisibleRows();
    }

    return JSON.stringify(
      [...seen.values()].sort((a, b) => {
        const left = Number.isFinite(Number(a.rank)) ? Number(a.rank) : 999999;
        const right = Number.isFinite(Number(b.rank)) ? Number(b.rank) : 999999;
        return left - right;
      })
    );
  })()')"
  payload="$(unjson "$raw")"
  if [[ -z "$payload" || "$payload" == "null" ]]; then
    echo "[]"
  else
    echo "$payload"
  fi
}

go_to_page() {
  local page="$1"
  local page_json result
  page_json="$(json_escape "$page")"
  result="$(ab eval "(() => {
    const page = $page_json;
    const target = [...document.querySelectorAll('li,button,a')]
      .find(el => (el.textContent || '').trim() === page && el.offsetParent !== null);
    if (!target) return false;
    target.click();
    return true;
  })()")"
  result="$(unjson "$result")"
  if [[ "$result" != "true" ]]; then
    return 1
  fi
  ab wait 1800 >/dev/null || true
}

go_to_next_page() {
  local result
  result="$(ab eval '(() => {
    const candidates = [...document.querySelectorAll("li,button,a")].filter(el => el.offsetParent !== null);
    const target = candidates.find(el => {
      const text = (el.textContent || "").replace(/\s+/g, "");
      if (!text) return false;
      if (text === "下一页") return true;
      return text.includes("下一页") || text === ">" || text === "›" || text === "»";
    });
    if (!target) return "missing";
    const className = (target.className || "").toString();
    const disabled =
      target.disabled === true ||
      target.getAttribute("aria-disabled") === "true" ||
      /\b(disabled|is-disabled|ant-pagination-disabled)\b/i.test(className) ||
      target.classList.contains("disabled");
    if (disabled) return "disabled";
    target.click();
    return "clicked";
  })()')"
  result="$(unjson "$result")"
  [[ "$result" == "clicked" ]] || return 1
  ab wait 1800 >/dev/null || true
}

pick_candidates() {
  local page page_rows selected_count candidate name selected_norm analysis_json sample_probe_json status
  local previous_page_rows pages_without_progress
  selected_count=0
  page=1
  previous_page_rows=""
  pages_without_progress=0
  while [[ "$selected_count" -lt "$CANDIDATE_LIMIT" ]]; do
    page_rows="$(collect_current_page_rows)"
    if [[ -z "$page_rows" || "$page_rows" == "[]" || "$page_rows" == "$previous_page_rows" ]]; then
      pages_without_progress=$((pages_without_progress + 1))
    else
      pages_without_progress=0
    fi
    previous_page_rows="$page_rows"
    while IFS= read -r candidate; do
      [[ -z "$candidate" ]] && continue
      name="$(jq -r '.name // ""' <<<"$candidate")"
      [[ -z "$name" ]] && continue
      selected_norm="$(normalize_name "$name")"
      if grep -Fxq "$selected_norm" "$RUNTIME_DIR/selected.normalized.tmp" 2>/dev/null; then
        continue
      fi
      if [[ "$ALLOW_REPEAT" != "1" ]] && history_has_name "$name"; then
        continue
      fi
      if [[ "$ALLOW_FEISHU_REPEAT" != "1" ]] && feishu_has_name "$name"; then
        continue
      fi
      analysis_json="$(analyze_selection_candidate "$candidate" "$CATEGORY_HINT")"
      if [[ "$(jq -r '.status // ""' <<<"$analysis_json")" == "通过" ]] && [[ "$(jq -r '.inferred_category // ""' <<<"$analysis_json")" == "服装" ]]; then
        sample_probe_json="$(probe_candidate_material_mix "$candidate" "$analysis_json")"
        analysis_json="$(analyze_selection_candidate "$candidate" "$CATEGORY_HINT" "$sample_probe_json")"
      fi
      status="$(jq -r '.status' <<<"$analysis_json")"
      if [[ "$status" != "通过" ]]; then
        continue
      fi
      jq -c \
        --arg shop_name "$SHOP_NAME" \
        --arg category_hint "$CATEGORY_HINT" \
        --argjson analysis "$analysis_json" \
        '. + $analysis + {
          shop_name:$shop_name,
          category_hint:$category_hint,
          selection_status:$analysis.status,
          selection_priority:$analysis.priority,
          selection_evidence:$analysis.evidence,
          selection_summary:$analysis.summary_reason
        }' \
        <<<"$candidate" >> "$SELECTED_JSONL"
      printf '%s\n' "$selected_norm" >> "$RUNTIME_DIR/selected.normalized.tmp"
      selected_count=$((selected_count + 1))
      if [[ "$selected_count" -ge "$CANDIDATE_LIMIT" ]]; then
        break
      fi
    done < <(jq -c '.[]' <<<"$page_rows")
    if [[ "$selected_count" -ge "$CANDIDATE_LIMIT" ]]; then
      break
    fi
    if [[ "$pages_without_progress" -ge 2 ]]; then
      break
    fi
    go_to_next_page || break
    page=$((page + 1))
  done
}

: > "$RUNTIME_DIR/selected.normalized.tmp"

cleanup_selected_tmp() {
  rm -f "$RUNTIME_DIR/selected.normalized.tmp"
}

write_daily_product_report() {
  local report_path="$1"
  local product_name="$2"
  local detail_url="$3"
  local downloaded_count="$4"
  local product_key tmp_file section_file

  product_key="$(jq -nr --arg v "$product_name" '$v|@base64')"
  tmp_file="$RUNTIME_DIR/daily_report.tmp"
  section_file="$RUNTIME_DIR/daily_report_section.tmp"

  if [[ ! -f "$report_path" ]]; then
    cat > "$report_path" <<EOF
# 商品报告

- 日期：$RUN_DATE

EOF
  fi

  awk \
    -v start="<!-- PRODUCT_KEY:${product_key} -->" \
    -v end="<!-- /PRODUCT_KEY:${product_key} -->" '
      $0 == start {skip=1; next}
      $0 == end {skip=0; next}
      skip != 1 {print}
    ' "$report_path" > "$tmp_file"

  cat > "$section_file" <<EOF
<!-- PRODUCT_KEY:${product_key} -->
## 商品：$product_name

- 好货链接：$detail_url
- 已下载带货视频样本数：$downloaded_count

<!-- /PRODUCT_KEY:${product_key} -->
EOF

  perl -0pi -e 's/(?:\n[ \t]*)+\z/\n/s' "$tmp_file"

  {
    cat "$tmp_file"
    printf '\n'
    cat "$section_file"
  } > "$report_path"

  rm -f "$tmp_file" "$section_file"
}

relocate_fetch_artifacts() {
  local product_slug="$1"
  local video_dir="$2"
  local meta_dir meta_file
  meta_dir="$RUNTIME_DIR/fetch_meta/$product_slug"
  mkdir -p "$meta_dir"
  while IFS= read -r meta_file; do
    [[ -z "$meta_file" ]] && continue
    mv -f "$meta_file" "$meta_dir/$(basename "$meta_file")"
  done < <(find "$video_dir" -maxdepth 1 -type f \( -name 'video_urls_*.jsonl' -o -name 'video_fetch_summary_*.json' -o -name 'latest_video_fetch_summary.json' \) | sort)
}

record_terminal_failure() {
  local stage="$1"
  local item_name="$2"
  local item_path="$3"
  local attempts="$4"
  local log_path="$5"
  local reason="$6"
  jq -nc \
    --arg stage "$stage" \
    --arg item_name "$item_name" \
    --arg item_path "$item_path" \
    --argjson attempts "$attempts" \
    --arg log_path "$log_path" \
    --arg reason "$reason" \
    '{stage:$stage,item_name:$item_name,item_path:$item_path,attempts:$attempts,log_path:$log_path,reason:$reason}' \
    >> "$TERMINAL_FAILURES_JSONL"
}

download_selected_products() {
  local index candidate name detail_url product_slug product_dir video_dir attempt log_file fetch_output summary_file manifest_file downloaded_count
  index=0
  while IFS= read -r candidate; do
    [[ -z "$candidate" ]] && continue
    index=$((index + 1))
    name="$(jq -r '.name' <<<"$candidate")"
    detail_url="$(jq -r '.detail_url // ""' <<<"$candidate")"
    product_slug="$(printf '%02d' "$index")_$(printf '%s' "$name" | tr ' /' '__' | cut -c1-80)"
    product_dir="$PRODUCTS_DIR/$product_slug"
    video_dir="$product_dir/带货视频"
    mkdir -p "$video_dir"

    attempt=1
    while [[ "$attempt" -le 3 ]]; do
      log_file="$LOG_DIR/download_${index}_attempt${attempt}.log"
      if fetch_output="$(bash "$SCRIPT_DIR/fetch_short_videos.sh" \
        --cdp-port "$CDP_PORT" \
        --product-name "$name" \
        --output-dir "$video_dir" \
        --download \
        --max-videos "$MAX_VIDEOS" \
        --extract-mode auto 2>&1)"; then
        printf '%s\n' "$fetch_output" > "$log_file"
        summary_file="$(printf '%s\n' "$fetch_output" | sed -n 's/^SUMMARY_FILE=//p' | tail -n 1)"
        manifest_file="$(printf '%s\n' "$fetch_output" | sed -n 's/^MANIFEST_FILE=//p' | tail -n 1)"
        downloaded_count="$(find "$video_dir" -maxdepth 1 -type f -name '*.mp4' | wc -l | tr -d ' ')"
        if [[ "$downloaded_count" -gt 0 ]]; then
          relocate_fetch_artifacts "$product_slug" "$video_dir"
          if [[ -n "$summary_file" ]]; then
            summary_file="$RUNTIME_DIR/fetch_meta/$product_slug/$(basename "$summary_file")"
          fi
          if [[ -n "$manifest_file" ]]; then
            manifest_file="$RUNTIME_DIR/fetch_meta/$product_slug/$(basename "$manifest_file")"
          fi
          write_daily_product_report "$DAILY_REPORT_PATH" "$name" "$detail_url" "$downloaded_count"
          jq -nc \
            --arg name "$name" \
            --arg product_dir "$product_dir" \
            --arg video_dir "$video_dir" \
            --arg report_file "$DAILY_REPORT_PATH" \
            --arg summary_file "$summary_file" \
            --arg manifest_file "$manifest_file" \
            --argjson attempts "$attempt" \
            --arg result "ok" \
            '{name:$name,product_dir:$product_dir,video_dir:$video_dir,report_file:$report_file,summary_file:$summary_file,manifest_file:$manifest_file,attempts:$attempts,result:$result}' \
            >> "$DOWNLOAD_RESULTS_JSONL"
          break
        fi
      else
        printf '%s\n' "$fetch_output" > "$log_file"
      fi

      if [[ "$attempt" -eq 3 ]]; then
        jq -nc \
          --arg name "$name" \
          --arg product_dir "$product_dir" \
          --arg video_dir "$video_dir" \
          --argjson attempts "$attempt" \
          --arg result "failed" \
          '{name:$name,product_dir:$product_dir,video_dir:$video_dir,attempts:$attempts,result:$result}' \
          >> "$DOWNLOAD_RESULTS_JSONL"
        record_terminal_failure "download" "$name" "$product_dir" "$attempt" "$log_file" "下载失败或未拿到有效视频"
      fi
      attempt=$((attempt + 1))
    done
  done < "$SELECTED_JSONL"
}

load_feishu_existing_map() {
  local offset raw has_more
  offset=0
  : > "$FEISHU_EXISTING_MAP"
  while true; do
    raw="$(lark-cli base +record-list \
      --base-token "$FEISHU_BASE_TOKEN" \
      --table-id "$FEISHU_TABLE_ID" \
      --limit 100 \
      --offset "$offset" \
      --as user 2>/dev/null || true)"
    if [[ -z "$raw" ]]; then
      break
    fi
    jq -r '
      .data as $d
      | ($d.fields | index("商品名称")) as $name_idx
      | if $name_idx == null then empty else
          range(0; ($d.record_id_list | length)) as $i
          | [($d.record_id_list[$i] // ""), ($d.data[$i][$name_idx] // "")]
          | @tsv
        end
    ' <<<"$raw" | sed '/\t$/d' >> "$FEISHU_EXISTING_MAP"
    has_more="$(jq -r '.data.has_more // false' <<<"$raw")"
    [[ "$has_more" != "true" ]] && break
    offset=$((offset + 100))
  done
}

lookup_feishu_record_id() {
  local normalized line record_id name
  normalized="$(normalize_name "$1")"
  while IFS=$'\t' read -r record_id name; do
    [[ -z "$record_id" || -z "$name" ]] && continue
    if [[ "$(normalize_name "$name")" == "$normalized" ]]; then
      printf '%s\n' "$record_id"
      return 0
    fi
  done < "$FEISHU_EXISTING_MAP"
  return 1
}

feishu_has_name() {
  lookup_feishu_record_id "$1" >/dev/null 2>&1
}

find_selected_candidate_by_name() {
  local name="$1"
  jq -rc --arg name "$name" 'select(.name == $name)' "$SELECTED_JSONL" | head -n 1
}

refresh_feishu_fields() {
  lark-cli base +field-list \
    --base-token "$FEISHU_BASE_TOKEN" \
    --table-id "$FEISHU_TABLE_ID" \
    --offset 0 \
    --limit 200 \
    --as user > "$FEISHU_FIELDS_JSON"
}

has_feishu_field() {
  local field_name="$1"
  jq -e --arg field_name "$field_name" '
    (.data.items[]?, .data.fields[]?)
    | select((.field_name // .name // "") == $field_name)
  ' "$FEISHU_FIELDS_JSON" >/dev/null
}

ensure_feishu_text_field() {
  local field_name="$1"
  if has_feishu_field "$field_name"; then
    return 0
  fi
  lark-cli base +field-create \
    --base-token "$FEISHU_BASE_TOKEN" \
    --table-id "$FEISHU_TABLE_ID" \
    --json "$(jq -nc --arg name "$field_name" '{name:$name,type:"text"}')" \
    --as user >/dev/null
  refresh_feishu_fields
}

ensure_feishu_number_field() {
  local field_name="$1"
  if has_feishu_field "$field_name"; then
    return 0
  fi
  lark-cli base +field-create \
    --base-token "$FEISHU_BASE_TOKEN" \
    --table-id "$FEISHU_TABLE_ID" \
    --json "$(jq -nc --arg name "$field_name" '{name:$name,type:"number"}')" \
    --as user >/dev/null
  refresh_feishu_fields
}

ensure_feishu_select_field() {
  local field_name="$1"
  shift
  local options_json
  if has_feishu_field "$field_name"; then
    return 0
  fi
  options_json="$(printf '%s\n' "$@" | jq -R '{name:.}' | jq -s '.')"
  lark-cli base +field-create \
    --base-token "$FEISHU_BASE_TOKEN" \
    --table-id "$FEISHU_TABLE_ID" \
    --json "$(jq -nc --arg name "$field_name" --argjson options "$options_json" '{name:$name,type:"select",multiple:false,options:$options}')" \
    --as user >/dev/null
  refresh_feishu_fields
}

ensure_feishu_selection_schema() {
  refresh_feishu_fields
  ensure_feishu_text_field "售价带"
  ensure_feishu_number_field "爆品潜力分"
  ensure_feishu_select_field "风险等级" "低风险" "中风险" "高风险"
  ensure_feishu_select_field "测试优先级" "A档：立即测试" "B档：可测试" "C档：观察" "D档：淘汰"
  ensure_feishu_text_field "推荐测试切口"
  ensure_feishu_text_field "商品ID"
  ensure_feishu_number_field "商品售价"
  ensure_feishu_number_field "商品成本价"
  ensure_feishu_number_field "签收率"
}

sync_selected_products_to_feishu() {
  local item name product_dir video_dir record_id candidate detail_url rank_json downloaded_count note payload log_file raw
  local category heat_trend price_bin price_mid sales_mid gmv_7d score_value risk_level priority test_angle evidence summary_reason material_density
  local -a upsert_cmd
  ensure_feishu_selection_schema
  load_feishu_existing_map
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    if [[ "$(jq -r '.result' <<<"$item")" != "ok" ]]; then
      continue
    fi
    name="$(jq -r '.name' <<<"$item")"
    product_dir="$(jq -r '.product_dir' <<<"$item")"
    video_dir="$(jq -r '.video_dir' <<<"$item")"
    downloaded_count="$(find "$video_dir" -maxdepth 1 -type f -name '*.mp4' | wc -l | tr -d ' ')"
    candidate="$(find_selected_candidate_by_name "$name")"
    if [[ -n "$candidate" ]]; then
      detail_url="$(jq -r '.detail_url // ""' <<<"$candidate")"
      rank_json="$(jq -c '.rank // null' <<<"$candidate")"
      category="$(jq -r '.inferred_category // ""' <<<"$candidate")"
      heat_trend="$(jq -r '.heat_trend // ""' <<<"$candidate")"
      price_bin="$(jq -r '.price_bin // ""' <<<"$candidate")"
      price_mid="$(jq -r '.price_mid // 0' <<<"$candidate")"
      sales_mid="$(jq -r '.sales_mid // 0' <<<"$candidate")"
      gmv_7d="$(midpoint_int "$(jq -r '.gmv_low // 0' <<<"$candidate")" "$(jq -r '.gmv_high // 0' <<<"$candidate")")"
      score_value="$(jq -r '.total_score // 0' <<<"$candidate")"
      risk_level="$(jq -r '.risk_level // ""' <<<"$candidate")"
      priority="$(jq -r '.priority // ""' <<<"$candidate")"
      test_angle="$(jq -r '.test_angle // ""' <<<"$candidate")"
      evidence="$(jq -r '.evidence // ""' <<<"$candidate")"
      summary_reason="$(jq -r '.summary_reason // ""' <<<"$candidate")"
      material_density="$(jq -r '.video_low // 0' <<<"$candidate")"
    else
      detail_url=""
      rank_json="null"
      category=""
      heat_trend=""
      price_bin=""
      price_mid="0"
      sales_mid="0"
      gmv_7d="0"
      score_value="0"
      risk_level=""
      priority=""
      test_angle=""
      evidence=""
      summary_reason=""
      material_density="0"
    fi
    record_id="$(lookup_feishu_record_id "$name" || true)"
    note="店铺: $SHOP_NAME | 链路: 选品到剪辑 | run: $(basename "$OUTPUT_ROOT")
结论: ${summary_reason:-已进入测试池}
${evidence:-证据待补充}
好货链接: ${detail_url:-无}
已下载带货视频: ${downloaded_count}条"

    payload="$(jq -nc \
      --arg name "$name" \
      --arg status "✅已选" \
      --arg source "电商罗盘" \
      --arg note "$note" \
      --arg detail_url "$detail_url" \
      --arg category "$category" \
      --arg heat_trend "$heat_trend" \
      --arg price_bin "$price_bin" \
      --arg risk_level "$risk_level" \
      --arg priority "$priority" \
      --arg test_angle "$test_angle" \
      --argjson rank "$rank_json" \
      --argjson material_density "$material_density" \
      --argjson price_mid "$price_mid" \
      --argjson sales_mid "$sales_mid" \
      --argjson gmv_7d "$gmv_7d" \
      --argjson score_value "$score_value" \
      '
        {
          "商品名称": $name,
          "选品状态": [$status],
          "数据来源": [$source],
          "备注": $note
        }
        | if $detail_url != "" then .["素材链接"] = $detail_url else . end
        | if $rank != null then .["榜单排行"] = $rank else . end
        | if $category != "" then .["商品分类"] = [$category] else . end
        | if $heat_trend != "" then .["热度趋势"] = [$heat_trend] else . end
        | if $price_mid > 0 then .["客单价"] = $price_mid else . end
        | if $sales_mid > 0 then .["销量"] = $sales_mid else . end
        | if $gmv_7d > 0 then .["营业额-7天"] = $gmv_7d else . end
        | if $material_density > 0 then .["素材量"] = $material_density else . end
        | if $price_bin != "" then .["售价带"] = $price_bin else . end
        | if $score_value > 0 then .["爆品潜力分"] = $score_value else . end
        | if $risk_level != "" then .["风险等级"] = [$risk_level] else . end
        | if $priority != "" then .["测试优先级"] = [$priority] else . end
        | if $test_angle != "" then .["推荐测试切口"] = $test_angle else . end
      '
    )"

    log_file="$LOG_DIR/feishu_$(printf '%s' "$name" | tr ' /' '__' | cut -c1-50).log"
    upsert_cmd=(
      lark-cli base +record-upsert
      --base-token "$FEISHU_BASE_TOKEN"
      --table-id "$FEISHU_TABLE_ID"
      --json "$payload"
      --as user
    )
    if [[ -n "$record_id" ]]; then
      upsert_cmd+=(--record-id "$record_id")
    fi
    if raw="$("${upsert_cmd[@]}" 2>&1)"; then
      printf '%s\n' "$raw" > "$log_file"
      jq -nc \
        --arg name "$name" \
        --arg record_id "${record_id:-}" \
        --arg result "ok" \
        '{name:$name,record_id:$record_id,result:$result}' \
        >> "$FEISHU_SYNC_RESULTS_JSONL"
    else
      printf '%s\n' "$raw" > "$log_file"
      jq -nc \
        --arg name "$name" \
        --arg record_id "${record_id:-}" \
        --arg result "failed" \
        '{name:$name,record_id:$record_id,result:$result}' \
        >> "$FEISHU_SYNC_RESULTS_JSONL"
      record_terminal_failure "feishu" "$name" "$product_dir" 1 "$log_file" "飞书写入失败"
    fi
  done < "$DOWNLOAD_RESULTS_JSONL"
}

clip_downloaded_videos() {
  local video attempt log_file output_name output_path product_slug product_clip_dir
  while IFS= read -r video; do
    [[ -z "$video" ]] && continue
    attempt=1
    product_slug="$(basename "$(dirname "$(dirname "$video")")")"
    product_clip_dir="$CLIP_OUTPUT_DIR/$product_slug"
    mkdir -p "$product_clip_dir"
    output_name="$(basename "${video%.mp4}")_clip.mp4"
    output_path="$product_clip_dir/$output_name"
    while [[ "$attempt" -le 3 ]]; do
      log_file="$LOG_DIR/clip_$(basename "${video%.mp4}")_attempt${attempt}.log"
      if bash "$CLIP_SCRIPT" \
        --query "$CLIP_QUERY" \
        --input "$video" \
        --output-root "$product_clip_dir" >"$log_file" 2>&1 && [[ -f "$output_path" ]]; then
        if ! ensure_qianchuan_9x16 "$output_path" >>"$log_file" 2>&1; then
          jq -nc \
            --arg input_video "$video" \
            --arg output_video "$output_path" \
            --argjson attempts "$attempt" \
            --arg result "failed" \
            '{input_video:$input_video,output_video:$output_video,attempts:$attempts,result:$result,reason:"9x16_normalize_failed"}' \
            >> "$CLIP_RESULTS_JSONL"
          record_terminal_failure "clip" "$(basename "$video")" "$video" "$attempt" "$log_file" "9:16 规范化失败"
          break
        fi
        jq -nc \
          --arg input_video "$video" \
          --arg output_video "$output_path" \
          --argjson attempts "$attempt" \
          --arg result "ok" \
          '{input_video:$input_video,output_video:$output_video,attempts:$attempts,result:$result}' \
          >> "$CLIP_RESULTS_JSONL"
        break
      fi
      if [[ "$attempt" -eq 3 ]]; then
        jq -nc \
          --arg input_video "$video" \
          --arg output_video "$output_path" \
          --argjson attempts "$attempt" \
          --arg result "failed" \
          '{input_video:$input_video,output_video:$output_video,attempts:$attempts,result:$result}' \
          >> "$CLIP_RESULTS_JSONL"
        record_terminal_failure "clip" "$(basename "$video")" "$video" "$attempt" "$log_file" "剪辑失败"
      fi
      attempt=$((attempt + 1))
    done
  done < <(find "$PRODUCTS_DIR" -type f -path '*/带货视频/*.mp4' | sort)
}

write_failure_record() {
  local failure_md failure_json count
  failure_md="$OUTPUT_ROOT/失败记录.md"
  failure_json="$OUTPUT_ROOT/失败记录.json"
  count="$(wc -l < "$TERMINAL_FAILURES_JSONL" | tr -d ' ')"
  if [[ "$count" -eq 0 ]]; then
    rm -f "$failure_md" "$failure_json"
    return 0
  fi

  jq -s '.' "$TERMINAL_FAILURES_JSONL" > "$failure_json"
  {
    echo "# 失败记录"
    echo
    echo "- 生成时间：$(date '+%Y-%m-%d %H:%M:%S')"
    echo "- 失败项数：$count"
    echo
    while IFS= read -r item; do
      echo "## $(jq -r '.stage' <<<"$item") / $(jq -r '.item_name' <<<"$item")"
      echo
      echo "- 路径：$(jq -r '.item_path' <<<"$item")"
      echo "- 尝试次数：$(jq -r '.attempts' <<<"$item")"
      echo "- 原因：$(jq -r '.reason' <<<"$item")"
      echo "- 日志：$(jq -r '.log_path' <<<"$item")"
      echo
    done < "$TERMINAL_FAILURES_JSONL"
  } > "$failure_md"
}

write_runtime_state() {
  local forced_stage="${1:-}"
  local forced_outcome="${2:-}"
  local selected_count downloaded_products clipped_videos terminal_failures outcome stage
  selected_count="$(wc -l < "$SELECTED_JSONL" | tr -d ' ')"
  downloaded_products="$(jq -s '[.[] | select(.result == "ok")] | length' "$DOWNLOAD_RESULTS_JSONL")"
  clipped_videos="$(jq -s '[.[] | select(.result == "ok")] | length' "$CLIP_RESULTS_JSONL")"
  terminal_failures="$(wc -l < "$TERMINAL_FAILURES_JSONL" | tr -d ' ')"
  if [[ -n "$forced_outcome" ]]; then
    outcome="$forced_outcome"
  else
    outcome="$(derive_run_outcome "$downloaded_products" "$clipped_videos" "$terminal_failures")"
  fi
  if [[ -n "$forced_stage" ]]; then
    stage="$forced_stage"
  else
    stage="$outcome"
  fi

  jq -nc \
    --arg query "$QUERY" \
    --arg shop_name "$SHOP_NAME" \
    --arg clip_query "$CLIP_QUERY" \
    --arg output_root "$OUTPUT_ROOT" \
    --argjson candidate_limit "$CANDIDATE_LIMIT" \
    --arg allow_repeat "$ALLOW_REPEAT" \
    --arg category_hint "$CATEGORY_HINT" \
    --arg outcome "$outcome" \
    --arg stage "$stage" \
    --argjson selected_count "$selected_count" \
    --argjson downloaded_products "$downloaded_products" \
    --argjson clipped_videos "$clipped_videos" \
    --argjson terminal_failures "$terminal_failures" \
    --slurpfile processed_products "$SELECTED_JSONL" \
    '{query:$query,shop_name:$shop_name,clip_query:$clip_query,output_root:$output_root,candidate_limit:$candidate_limit,allow_repeat:$allow_repeat,category_hint:$category_hint,outcome:$outcome,stage:$stage,selected_count:$selected_count,downloaded_products:$downloaded_products,clipped_videos:$clipped_videos,terminal_failures:$terminal_failures,processed_products:$processed_products}' \
    > "$RUN_STATE_JSON"

  jq -nc \
    --slurpfile download_results "$DOWNLOAD_RESULTS_JSONL" \
    --slurpfile clip_results "$CLIP_RESULTS_JSONL" \
    --slurpfile terminal_failures "$TERMINAL_FAILURES_JSONL" \
    '{download_results:$download_results,clip_results:$clip_results,terminal_failures:$terminal_failures}' \
    > "$RETRY_STATE_JSON"

  jq -nc \
    --arg stage "$stage" \
    --arg completed_at "$(date '+%Y-%m-%d %H:%M:%S')" \
    --arg output_root "$OUTPUT_ROOT" \
    '{stage:$stage,completed_at:$completed_at,output_root:$output_root}' \
    > "$CHECKPOINT_JSON"
}

send_feishu_notify() {
  local forced_outcome="${1:-}"
  local message notify_log user_open_id send_raw message_id urgent_raw selected_count downloaded_products clipped_videos failures outcome
  notify_log="$LOG_DIR/feishu_notify.log"
  if [[ "$NO_NOTIFY" == "1" ]]; then
    return 0
  fi
  if [[ "$NOTIFY_SENT" == "1" ]]; then
    return 0
  fi
  selected_count="$(wc -l < "$SELECTED_JSONL" | tr -d ' ')"
  downloaded_products="$(jq -s '[.[] | select(.result == "ok")] | length' "$DOWNLOAD_RESULTS_JSONL")"
  clipped_videos="$(jq -s '[.[] | select(.result == "ok")] | length' "$CLIP_RESULTS_JSONL")"
  failures="$(wc -l < "$TERMINAL_FAILURES_JSONL" | tr -d ' ')"
  if [[ -n "$forced_outcome" ]]; then
    outcome="$forced_outcome"
  else
    outcome="$(derive_run_outcome "$downloaded_products" "$clipped_videos" "$failures")"
  fi
  message="$(build_notify_message "$SHOP_NAME" "$outcome" "$selected_count" "$downloaded_products" "$clipped_videos" "$failures" "$OUTPUT_ROOT")"

  if [[ "$PHONE_NOTIFY" == "1" ]]; then
    printf '%s\n' "[mode] phone_first" > "$notify_log"
    if [[ -f "$FEISHU_NOTIFY_SCRIPT" ]] && python3 "$FEISHU_NOTIFY_SCRIPT" notify --message "$message" --phone-call >>"$notify_log" 2>&1; then
      NOTIFY_SENT="1"
      return 0
    fi
    printf '%s\n' "[fallback] urgent_app" >> "$notify_log"
  fi

  if [[ -f "$LARK_CLI_CONFIG" ]]; then
    user_open_id="$(jq -r '.apps[0].users[0].userOpenId // empty' "$LARK_CLI_CONFIG" 2>/dev/null || true)"
    if [[ -n "$user_open_id" ]]; then
      if send_raw="$(lark-cli im +messages-send --user-id "$user_open_id" --text "$message" --as bot 2>&1)"; then
        printf '%s\n' "$send_raw" > "$notify_log"
        message_id="$(jq -r '.data.message_id // .data.message_id_list[0] // empty' <<<"$send_raw" 2>/dev/null || true)"
        if [[ -n "$message_id" ]]; then
          if urgent_raw="$(lark-cli api PATCH "/open-apis/im/v1/messages/${message_id}/urgent_app" \
            --params '{"user_id_type":"open_id"}' \
            --data "{\"user_id_list\":[\"$user_open_id\"]}" \
            --as bot 2>&1)"; then
            printf '\n%s\n' "$urgent_raw" >> "$notify_log"
            NOTIFY_SENT="1"
            return 0
          else
            printf '\n%s\n' "$urgent_raw" >> "$notify_log"
          fi
        fi
      else
        printf '%s\n' "$send_raw" > "$notify_log"
      fi
    fi
  fi

  if [[ -f "$FEISHU_NOTIFY_SCRIPT" ]] && python3 "$FEISHU_NOTIFY_SCRIPT" notify --message "$message" >>"$notify_log" 2>&1; then
    NOTIFY_SENT="1"
    return 0
  fi
  printf '%s\n' "[WARN] 飞书加急通知未发送成功，详见 $notify_log" >&2
}

finalize_interrupted_run() {
  local signal_name="${1:-TERM}"
  local exit_code="${2:-1}"
  local reason

  if [[ "$RUN_FINALIZED" == "1" ]]; then
    cleanup_selected_tmp
    exit "$exit_code"
  fi
  RUN_FINALIZED="1"

  reason="运行被信号中断: ${signal_name}，阶段: ${CURRENT_STAGE}"
  record_terminal_failure "run_interrupted" "$SHOP_NAME" "$OUTPUT_ROOT" 1 "$LOG_DIR/feishu_notify.log" "$reason"
  write_failure_record
  write_runtime_state "interrupted" "failed"
  send_feishu_notify "interrupted" || true
  cleanup_selected_tmp
  exit "$exit_code"
}

trap 'cleanup_selected_tmp' EXIT
trap 'finalize_interrupted_run INT 130' INT
trap 'finalize_interrupted_run TERM 143' TERM
trap 'finalize_interrupted_run HUP 129' HUP

refresh_history_names
CURRENT_STAGE="prepare_browser"
ensure_compass_short_video_page
CURRENT_STAGE="pick_candidates"
pick_candidates
if [[ "$(wc -l < "$SELECTED_JSONL" | tr -d ' ')" -eq 0 ]]; then
  echo "未找到符合条件的新候选商品" >&2
  exit 1
fi
CURRENT_STAGE="download_videos"
download_selected_products
CURRENT_STAGE="sync_feishu"
if [[ "$SKIP_FEISHU" != "1" ]]; then
  sync_selected_products_to_feishu
fi
CURRENT_STAGE="clip_videos"
clip_downloaded_videos
CURRENT_STAGE="write_summary"
write_failure_record
write_runtime_state
send_feishu_notify
RUN_FINALIZED="1"

echo "RUN_DIR=$OUTPUT_ROOT"
echo "SELECTED_COUNT=$(wc -l < "$SELECTED_JSONL" | tr -d ' ')"
echo "DOWNLOADED_PRODUCTS=$(jq -s '[.[] | select(.result == "ok")] | length' "$DOWNLOAD_RESULTS_JSONL")"
echo "CLIPPED_VIDEOS=$(jq -s '[.[] | select(.result == "ok")] | length' "$CLIP_RESULTS_JSONL")"
echo "FAILURES=$(wc -l < "$TERMINAL_FAILURES_JSONL" | tr -d ' ')"
