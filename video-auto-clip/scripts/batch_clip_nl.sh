#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=""
OUTPUT_ROOT=""
QUERY=""
LIMIT=0
DRY_RUN=0
INPUT_FILE=""
KEEP_ARTIFACTS=0
WORKERS=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OCR_SWIFT="${VIDEO_AUTO_CLIP_OCR_BIN:-$SKILL_DIR/tools/vision_ocr.swift}"
DIFF_SWIFT="$SKILL_DIR/tools/image_diff.swift"
WHISPER_BIN="$(command -v whisper || true)"
ASR_CACHE_DIR="${VIDEO_AUTO_CLIP_ASR_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/video-auto-clip/asr}"
OCR_CACHE_DIR="${VIDEO_AUTO_CLIP_OCR_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/video-auto-clip/ocr}"

AUTO_MODE=0
TARGET_TAILCARD=0
TARGET_PRICE=0
TARGET_CHEAP=0
TARGET_ANTIBACTERIAL=0
TARGET_FOODGRADE=0
TARGET_REPORT=0
TARGET_EFFICACY=0
TARGET_AI_GENERATED=0
TARGET_AD=0

MANUAL_TAIL_SEC=""
MANUAL_HEAD_SEC=""
MANUAL_KEEP_FIRST_SEC=""
FRAME_EXTRACTION_MODE="${VIDEO_AUTO_CLIP_FRAME_EXTRACTION_MODE:-combined}"
LAST_FRAME_EXTRACTION_MODE=""
LAST_FRAME_EXTRACTION_NOTE=""
LAST_COARSE_DIR=""
LAST_COARSE_ROI_DIR=""
LAST_COARSE_REPORT_DIR=""
LAST_ASR_CACHE_STATUS=""
LAST_ASR_SRT=""
OCR_CACHE_HIT_COUNT=0
OCR_CACHE_MISS_COUNT=0

usage() {
  cat <<'USAGE'
用法:
  batch_clip_nl.sh --query "自然语言指令" [--root 路径] [--output-root 路径] [--limit N] [--workers N] [--input 文件] [--dry-run] [--keep-artifacts]

说明:
  - 默认 root: 当前脚本所在目录
  - 默认 output-root: ~/Desktop/video_outputs
  - 自动扫描: <root>/**/带货视频/*.mp4
  - 指定 --input 时，仅处理该单文件
  - --workers 可开启批量并行；默认 1（串行）
  - 默认只保留剪辑后视频；加 --keep-artifacts 可保留报告和中间文件
  - 环境变量 `VIDEO_AUTO_CLIP_FRAME_EXTRACTION_MODE=legacy` 可回退到旧版三次独立粗扫抽帧
  - 环境变量 `VIDEO_AUTO_CLIP_ASR_CACHE_DIR=/path/to/cache` 可复用历史 ASR 结果
  - 环境变量 `VIDEO_AUTO_CLIP_OCR_BIN=/path/to/ocr` 可覆盖默认 OCR 执行器
  - 环境变量 `VIDEO_AUTO_CLIP_OCR_CACHE_DIR=/path/to/cache` 可复用历史 OCR 结果

支持方式:
  1) 时间规则: 剪掉最后N秒 / 剪掉开头N秒 / 保留前N秒 / 删除A-B秒
  2) skill 风格目标: 平台尾卡 / 价格 / 便宜 / 抗菌 / 食品级 / 检测报告 / 功效宣称 / AI生成 / 广告
  3) 使用“按skill剪辑”或更自然的话术（如“帮我剪辑”“使用剪辑技能”“批量剪辑”“处理成投流版”“过一遍合规剪辑”）且未指定目标时，默认启用旧版核心目标（平台尾卡 / 价格 / 便宜 / 抗菌 / 食品级 / 检测报告 / 功效宣称）

  示例:
  batch_clip_nl.sh --query "帮我剪辑这条视频"
  batch_clip_nl.sh --query "把这条视频处理成能投流的版本，剪掉平台尾卡"
  batch_clip_nl.sh --query "把这条视频处理成投流版，剪掉价格、便宜、抗菌、食品级、检测报告、功效宣称、AI生成、广告、平台尾卡"
  batch_clip_nl.sh --query "去片尾导流，并删除10-15秒"
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT_DIR="$2"; shift 2 ;;
    --output-root)
      OUTPUT_ROOT="$2"; shift 2 ;;
    --query)
      QUERY="$2"; shift 2 ;;
    --limit)
      LIMIT="$2"; shift 2 ;;
    --workers)
      WORKERS="$2"; shift 2 ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    --input)
      INPUT_FILE="$2"; shift 2 ;;
    --keep-artifacts)
      KEEP_ARTIFACTS=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1 ;;
  esac
done

ROOT_DIR="${ROOT_DIR:-$SKILL_DIR}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$HOME/Desktop/video_outputs}"

if [[ -z "$QUERY" ]]; then
  echo "必须提供 --query" >&2
  usage
  exit 1
fi

if ! [[ "$WORKERS" =~ ^[0-9]+$ ]] || [[ "$WORKERS" -lt 1 ]]; then
  echo "--workers 必须是大于等于 1 的整数" >&2
  exit 1
fi
if [[ "$FRAME_EXTRACTION_MODE" != "combined" && "$FRAME_EXTRACTION_MODE" != "legacy" ]]; then
  echo "VIDEO_AUTO_CLIP_FRAME_EXTRACTION_MODE 只支持 combined 或 legacy" >&2
  exit 1
fi

mkdir -p "$OUTPUT_ROOT"
RUN_DIR="$OUTPUT_ROOT/run_$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "$RUN_DIR"
REPORT="$RUN_DIR/执行报告.md"
RANGE_FILE_RAW="$RUN_DIR/区间_原始.txt"

echo "# 批量剪辑执行报告" > "$REPORT"
echo "" >> "$REPORT"
echo "- 执行时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT"
echo "- 根目录: $ROOT_DIR" >> "$REPORT"
echo "- 输出目录: $RUN_DIR" >> "$REPORT"
echo "- 自然语言指令: $QUERY" >> "$REPORT"
echo "- 粗扫抽帧模式(配置): $FRAME_EXTRACTION_MODE" >> "$REPORT"

query_matches() {
  local pattern="$1"
  printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne "exit(!(/$pattern/))"
}

parse_query() {
  MANUAL_TAIL_SEC="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/(?:剪掉|去掉|删除|移除|去除)?[^\n]{0,10}最后\s*([0-9]+(?:\.[0-9]+)?)\s*秒/){print $1; exit}')"
  MANUAL_HEAD_SEC="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/(?:剪掉|去掉|删除|移除|去除)?[^\n]{0,10}开头\s*([0-9]+(?:\.[0-9]+)?)\s*秒/){print $1; exit}')"
  MANUAL_KEEP_FIRST_SEC="$(printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'if(/保留前\s*([0-9]+(?:\.[0-9]+)?)\s*秒/){print $1; exit}')"
  printf '%s' "$QUERY" | perl -Mutf8 -CSDA -ne 'while(/([0-9]+(?:\.[0-9]+)?)\s*(?:-|~|到|至)\s*([0-9]+(?:\.[0-9]+)?)\s*秒?/g){print "$1 $2\n"}' > "$RANGE_FILE_RAW"

  if query_matches '按skill剪辑|自动剪辑|敏感词|合规|投流版|过审版|处理成能投流|处理成投流|过一遍合规剪辑|过一下合规|过一下视频|过一遍视频|处理一下视频|处理一下素材|清理一下视频|清理一下素材|帮我剪辑|使用剪辑技能|批量剪辑'; then
    AUTO_MODE=1
  fi
  if query_matches '平台尾卡|片尾导流|尾卡|导流|去片尾|去尾卡|去导流|去掉导流|平台账号片尾'; then
    AUTO_MODE=1
    TARGET_TAILCARD=1
  fi
  if query_matches '价格|到手价|仅需|多少钱'; then
    AUTO_MODE=1
    TARGET_PRICE=1
  fi
  if query_matches '便宜|实惠|划算'; then
    AUTO_MODE=1
    TARGET_CHEAP=1
  fi
  if query_matches '抗菌|10A抗菌|抗菌效果|抗菌底裆'; then
    AUTO_MODE=1
    TARGET_ANTIBACTERIAL=1
  fi
  if query_matches '食品级'; then
    AUTO_MODE=1
    TARGET_FOODGRADE=1
  fi
  if query_matches '检测报告|机构检测|CNAS|CMA|检测'; then
    AUTO_MODE=1
    TARGET_REPORT=1
  fi
  if query_matches '功效宣称|功效|宣称|玻尿酸|防晒|补水|保湿|修护|修复|舒缓|紧致|抗皱|抗衰|抗老|美白|提亮|祛痘|抗痘|淡斑|控油'; then
    AUTO_MODE=1
    TARGET_EFFICACY=1
  fi
  if query_matches 'AI生成|AI制作|AIGC|数字人生成|内容由AI生成'; then
    AUTO_MODE=1
    TARGET_AI_GENERATED=1
  fi
  if query_matches '广告|推广|赞助|商务合作|品牌合作|广告声明|推广声明'; then
    AUTO_MODE=1
    TARGET_AD=1
  fi

  if [[ "$AUTO_MODE" -eq 1 ]] \
    && [[ "$TARGET_TAILCARD" -eq 0 ]] \
    && [[ "$TARGET_PRICE" -eq 0 ]] \
    && [[ "$TARGET_CHEAP" -eq 0 ]] \
    && [[ "$TARGET_ANTIBACTERIAL" -eq 0 ]] \
    && [[ "$TARGET_FOODGRADE" -eq 0 ]] \
    && [[ "$TARGET_REPORT" -eq 0 ]] \
    && [[ "$TARGET_EFFICACY" -eq 0 ]] \
    && [[ "$TARGET_AI_GENERATED" -eq 0 ]] \
    && [[ "$TARGET_AD" -eq 0 ]]; then
    TARGET_TAILCARD=1
    TARGET_PRICE=1
    TARGET_CHEAP=1
    TARGET_ANTIBACTERIAL=1
    TARGET_FOODGRADE=1
    TARGET_REPORT=1
    TARGET_EFFICACY=1
  fi
}

targets_summary() {
  local parts=()
  [[ "$TARGET_TAILCARD" -eq 1 ]] && parts+=("平台尾卡")
  [[ "$TARGET_PRICE" -eq 1 ]] && parts+=("价格")
  [[ "$TARGET_CHEAP" -eq 1 ]] && parts+=("便宜")
  [[ "$TARGET_ANTIBACTERIAL" -eq 1 ]] && parts+=("抗菌")
  [[ "$TARGET_FOODGRADE" -eq 1 ]] && parts+=("食品级")
  [[ "$TARGET_REPORT" -eq 1 ]] && parts+=("检测报告")
  [[ "$TARGET_EFFICACY" -eq 1 ]] && parts+=("功效宣称")
  [[ "$TARGET_AI_GENERATED" -eq 1 ]] && parts+=("AI生成")
  [[ "$TARGET_AD" -eq 1 ]] && parts+=("广告")
  if [[ "${#parts[@]}" -eq 0 ]]; then
    printf '无'
  else
    local IFS='、'
    printf '%s' "${parts[*]}"
  fi
}

needs_visual_detection() {
  [[ "$AUTO_MODE" -eq 1 ]]
}

needs_asr_detection() {
  [[ "$TARGET_PRICE" -eq 1 ]] || [[ "$TARGET_CHEAP" -eq 1 ]] || [[ "$TARGET_ANTIBACTERIAL" -eq 1 ]] || [[ "$TARGET_FOODGRADE" -eq 1 ]] || [[ "$TARGET_REPORT" -eq 1 ]] || [[ "$TARGET_EFFICACY" -eq 1 ]] || [[ "$TARGET_AI_GENERATED" -eq 1 ]] || [[ "$TARGET_AD" -eq 1 ]]
}

append_interval() {
  local file="$1"
  local start="$2"
  local end="$3"
  local reason="$4"
  awk -v s="$start" -v e="$end" -v r="$reason" 'BEGIN { printf "%.6f %.6f %s\n", s, e, r }' >> "$file"
}

target_regex() {
  case "$1" in
    tailcard) printf '抖音搜索|来抖音|发现更多创作者|创作者|福利链接|换季福利|福利|链接|抓紧|多囤|囤两件|冲两件|品牌活动|说没就没' ;;
    price) printf '([¥￥$]\\s*[0-9]+(?:\\.[0-9]+)?)|([0-9]+(?:\\.[0-9]+)?\\s*(元|块|¥|￥))|([0-9]{1,3}\\.[0-9])|(^|[^0-9A-Za-z])([1-9][0-9]{1,3})([^0-9A-Za-z]|$)|([A-Za-z]{0,3}[1-9][0-9]{1,3}\\s*(的|多)?\\s*(莱|来|菜)[赛塞]?尔)|([0-9]{2,4}\\s*多(?:\\s*[0-9]{2,4}\\s*多)?)|[一二三四五六七八九十两百零几0-9]+块[一二三四五六七八九十两百零几0-9]*|卖[一二三四五六七八九十两百零几0-9]+的|(?:才|就|卖你|卖|只要)?[一二三四五六七八九十两百零几0-9]+张|(?:卖你|卖|才|就|只要)[一二三四五六七八九十两百零几0-9]{2,}(?:百多|千多|百[一二三四五六七八九十零几0-9]{1,3})|好?几百|好?几千|[一二三四五六七八九十两]{1,3}(?:百多|千多)|[一二三四五六七八九十两百零几]{2,}\\s*(的)?\\s*(莱|来|菜)[赛塞虽]?(尔|然)?|建议.?零售价|零售价|售价|吊牌价|标价|活动价|福利价|原价|现价|到手价|仅需|只要|到手|价格|多少钱|块钱|降价|降价了|减卖|Suggested price|suggested price' ;;
    cheap) printf '便宜|实惠|划算|减便|简便' ;;
    antibacterial) printf '抗菌|抗军|10A抗菌|抗菌效果|抗菌底裆|抗军效果' ;;
    foodgrade) printf '食品级' ;;
    report) printf '检测报告|报告|机构检测|CNAS|CMA|检测' ;;
    efficacy) printf '功效|功效宣称|玻尿酸|内护颜外防晒|美颜防护|防晒|补水|保湿|锁水|修护|修复|舒缓|紧致|抗皱|抗衰|抗老|淡纹|美白|提亮|祛痘|抗痘|淡斑|去黄|嫩肤|控油|去黑头|舒敏|抗敏|防紫外线|抗UV|UPF\\s*[0-9+]+' ;;
    ai_generated) printf 'AI生成|AI制作|AIGC|数字人生成|内容由AI生成|由AI生成|智能生成' ;;
    ad) printf '广告|推广|赞助|商务合作|品牌合作|广告声明|推广声明' ;;
    *) return 1 ;;
  esac
}

sanitize_price_text() {
  perl -Mutf8 -CSDA -pe '
    s/抖音\s*抖音号[:：]?.*$//;
    s/抖音号[:：]?\s*[0-9A-Za-z_-]+.*$//;
    s/[Qq]\s*小.*?漂亮服装//g;
  ' <<<"${1:-}"
}

price_text_matches() {
  local text
  text="$(sanitize_price_text "${1:-}")"
  printf '%s' "$text" | grep -Eq "$(target_regex price)"
}

report_roi_regex() {
  printf 'CTC|TEST|T.?ST|REPORT|RPOI|RPORT|CMA|CNAS|检验|检测'
}

target_list() {
  local list=()
  [[ "$TARGET_TAILCARD" -eq 1 ]] && list+=("tailcard")
  [[ "$TARGET_PRICE" -eq 1 ]] && list+=("price")
  [[ "$TARGET_CHEAP" -eq 1 ]] && list+=("cheap")
  [[ "$TARGET_ANTIBACTERIAL" -eq 1 ]] && list+=("antibacterial")
  [[ "$TARGET_FOODGRADE" -eq 1 ]] && list+=("foodgrade")
  [[ "$TARGET_REPORT" -eq 1 ]] && list+=("report")
  [[ "$TARGET_EFFICACY" -eq 1 ]] && list+=("efficacy")
  [[ "$TARGET_AI_GENERATED" -eq 1 ]] && list+=("ai_generated")
  [[ "$TARGET_AD" -eq 1 ]] && list+=("ad")
  printf '%s\n' "${list[@]}"
}

ocr_dir_to_tsv() {
  local dir="$1"
  local out="$2"
  : > "$out"
  if [[ ! -d "$dir" ]]; then
    return 0
  fi
  while IFS= read -r chunk; do
    [[ -z "$chunk" ]] && continue
    "$OCR_SWIFT" --tsv $chunk >> "$out"
  done < <(find "$dir" -type f \( -name '*.jpg' -o -name '*.png' \) | sort | awk '
    {
      buf = (buf == "" ? "\"" $0 "\"" : buf " \"" $0 "\"")
      count++
      if (count == 20) {
        print buf
        buf = ""
        count = 0
      }
    }
    END {
      if (buf != "") print buf
    }')
}

ocr_dir_to_tsv_safe() {
  local dir="$1"
  local out="$2"
  : > "$out"
  if [[ -z "$dir" || ! -d "$dir" ]]; then
    return 0
  fi
  if ! find "$dir" -type f \( -name '*.jpg' -o -name '*.png' \) -print -quit | grep -q .; then
    return 0
  fi
  while IFS= read -r file; do
    printf '%s\0' "$file"
  done < <(find "$dir" -type f \( -name '*.jpg' -o -name '*.png' \) | sort) \
    | xargs -0 -n 20 "$OCR_SWIFT" --tsv >> "$out"
}

ocr_cache_key() {
  local dir="$1"
  local ocr_sig="-"
  local file hash

  if [[ -f "$OCR_SWIFT" ]]; then
    ocr_sig="$(shasum -a 256 "$OCR_SWIFT" | awk '{print $1}')"
  fi

  {
    printf 'ocr=%s\n' "$ocr_sig"
    while IFS= read -r file; do
      hash="$(shasum -a 256 "$file" | awk '{print $1}')"
      printf '%s\t%s\n' "$(basename "$file")" "$hash"
    done < <(find "$dir" -type f \( -name '*.jpg' -o -name '*.png' \) | sort)
	  } | shasum -a 256 | awk '{print $1}'
}

rewrite_cached_ocr_paths() {
  local dir="$1"
  local in_tsv="$2"
  local out_tsv="$3"
  local map_file
  map_file="$(mktemp)"
  find "$dir" -type f \( -name '*.jpg' -o -name '*.png' \) | sort | awk '{
    n=$0
    sub(/^.*\//, "", n)
    print n "\t" $0
  }' > "$map_file"
  awk -F'\t' -v OFS='\t' '
    NR==FNR { path[$1]=$2; next }
    {
      name=$1
      sub(/^.*\//, "", name)
      if (name in path) $1=path[name]
      print
    }
  ' "$map_file" "$in_tsv" > "$out_tsv"
  rm -f "$map_file"
}

ocr_dir_to_tsv_cached() {
  local dir="$1"
  local out="$2"
  local cache_key cache_tsv
  : > "$out"

  if [[ -z "$dir" || ! -d "$dir" ]]; then
    return 0
  fi
  if ! find "$dir" -type f \( -name '*.jpg' -o -name '*.png' \) -print -quit | grep -q .; then
    return 0
  fi

  mkdir -p "$OCR_CACHE_DIR"
	  cache_key="$(ocr_cache_key "$dir")"
	  cache_tsv="$OCR_CACHE_DIR/${cache_key}.tsv"
	  if [[ -f "$cache_tsv" ]]; then
	    rewrite_cached_ocr_paths "$dir" "$cache_tsv" "$out"
	    OCR_CACHE_HIT_COUNT=$((OCR_CACHE_HIT_COUNT + 1))
	    return 0
	  fi

  ocr_dir_to_tsv_safe "$dir" "$out"
  cp -f "$out" "$cache_tsv"
  OCR_CACHE_MISS_COUNT=$((OCR_CACHE_MISS_COUNT + 1))
}

ocr_files_to_regions_jsonl_safe() {
  local list_file="$1"
  local out="$2"
  : > "$out"
  if [[ -z "$list_file" || ! -f "$list_file" || ! -s "$list_file" ]]; then
    return 0
  fi
  while IFS= read -r file; do
    printf '%s\0' "$file"
  done < "$list_file" | xargs -0 -n 10 "$OCR_SWIFT" --regions-jsonl >> "$out"
}

detect_top_right_ad_box() {
  local coarse_tsv="$1"
  local width="$2"
  local height="$3"
  local work_dir="$4"
  local candidates_file regions_jsonl

  [[ -s "$coarse_tsv" ]] || return 0

  candidates_file="$work_dir/top_right_ad_candidates.txt"
  regions_jsonl="$work_dir/top_right_ad_regions.jsonl"

  awk -F'\t' 'index($2, "广告") > 0 { print $1 }' "$coarse_tsv" | head -n 16 > "$candidates_file"
  [[ -s "$candidates_file" ]] || return 0

  ocr_files_to_regions_jsonl_safe "$candidates_file" "$regions_jsonl"
  [[ -s "$regions_jsonl" ]] || return 0

  python3 - "$regions_jsonl" "$width" "$height" <<'PY'
import json
import math
import sys

path, width, height = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
regions = []

with open(path, "r", encoding="utf-8") as fh:
    for raw in fh:
        raw = raw.strip()
        if not raw:
            continue
        data = json.loads(raw)
        for region in data.get("regions", []):
            text = str(region.get("text", "")).strip()
            if "广告" not in text:
                continue
            x = float(region.get("x", 0.0))
            y = float(region.get("y", 0.0))
            w = float(region.get("width", 0.0))
            h = float(region.get("height", 0.0))
            if x < 0.72:
                continue
            top = 1.0 - (y + h)
            if top > 0.10:
                continue
            regions.append((x, y, w, h))

if not regions:
    raise SystemExit(0)

min_x = min(x for x, _, _, _ in regions)
min_y = min(y for _, y, _, _ in regions)
max_x = max(x + w for x, _, w, _ in regions)
max_y = max(y + h for _, y, _, h in regions)

pad_x = 0.025
pad_top = 0.012
pad_bottom = 0.018

left = max(0.0, min_x - pad_x)
right = min(1.0, max_x + pad_x)
top = max(0.0, 1.0 - max_y - pad_top)
bottom = min(1.0, 1.0 - min_y + pad_bottom)

x_px = max(2, int(math.floor(left * width)))
y_px = max(2, int(math.floor(top * height)))
max_w = max(0, width - x_px - 2)
max_h = max(0, height - y_px - 2)
w_px = min(max_w, int(math.ceil((right - left) * width)))
h_px = min(max_h, int(math.ceil((bottom - top) * height)))

if w_px < 24 or h_px < 16:
    raise SystemExit(0)

print(f"{x_px} {y_px} {w_px} {h_px}")
PY
}

detect_top_left_info_box() {
  local coarse_tsv="$1"
  local width="$2"
  local height="$3"
  local work_dir="$4"
  local candidates_file regions_jsonl

  [[ -s "$coarse_tsv" ]] || return 0

  candidates_file="$work_dir/top_left_info_candidates.txt"
  regions_jsonl="$work_dir/top_left_info_regions.jsonl"

  awk -F'\t' '$2 ~ /(抖音|搜索|搜一搜|抖音号|账号)/ { print $1 }' "$coarse_tsv" | head -n 16 > "$candidates_file"
  [[ -s "$candidates_file" ]] || return 0

  ocr_files_to_regions_jsonl_safe "$candidates_file" "$regions_jsonl"
  [[ -s "$regions_jsonl" ]] || return 0

  python3 - "$regions_jsonl" "$width" "$height" <<'PY'
import json
import math
import re
import sys

path, width, height = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
keyword_re = re.compile(r"(抖音|搜索|搜一搜|抖音号|账号)")
regions = []

with open(path, "r", encoding="utf-8") as fh:
    for raw in fh:
        raw = raw.strip()
        if not raw:
            continue
        data = json.loads(raw)
        parsed = []
        for region in data.get("regions", []):
            text = str(region.get("text", "")).strip()
            if not text:
                continue
            x = float(region.get("x", 0.0))
            y = float(region.get("y", 0.0))
            w = float(region.get("width", 0.0))
            h = float(region.get("height", 0.0))
            top = 1.0 - (y + h)
            parsed.append((text, x, y, w, h, top))
        has_left_top_keyword = False
        for text, x, y, w, h, top in parsed:
            if not keyword_re.search(text):
                continue
            if x > 0.40:
                continue
            if top > 0.12:
                continue
            if h > 0.10:
                continue
            has_left_top_keyword = True
            break
        if not has_left_top_keyword:
            continue
        for text, x, y, w, h, top in parsed:
            if x > 0.50:
                continue
            # Keep the compact platform/search account strip only. Some videos
            # have body metadata (height/weight/location) directly below the
            # account strip; including that text makes the delogo box too tall
            # and causes valid platform strips to be dropped.
            if top > 0.125:
                continue
            if h > 0.10:
                continue
            regions.append((x, y, w, h))

if not regions:
    raise SystemExit(0)

min_x = min(x for x, _, _, _ in regions)
min_y = min(y for _, y, _, _ in regions)
max_x = max(x + w for x, _, w, _ in regions)
max_y = max(y + h for _, y, _, h in regions)

pad_left = 0.02
pad_right = 0.02
pad_top = 0.012
pad_bottom = 0.045

left = max(0.0, min_x - pad_left)
right = min(1.0, max_x + pad_right)
top = max(0.0, 1.0 - max_y - pad_top)
bottom = min(1.0, 1.0 - min_y + pad_bottom)

x_px = max(2, int(math.floor(left * width)))
y_px = max(2, int(math.floor(top * height)))
max_w = max(0, width - x_px - 2)
max_h = max(0, height - y_px - 2)
w_px = min(max_w, int(math.ceil((right - left) * width)))
h_px = min(max_h, int(math.ceil((bottom - top) * height)))

if w_px < 48 or h_px < 18:
    raise SystemExit(0)
if h_px > int(height * 0.19):
    raise SystemExit(0)
if w_px < 80:
    raise SystemExit(0)

print(f"{x_px} {y_px} {w_px} {h_px}")
PY
}

image_diff_to_tsv_safe() {
  local reference="$1"
  local out="$2"
  shift 2
  : > "$out"
  if [[ ! -f "$reference" ]] || [[ $# -eq 0 ]]; then
    return 0
  fi
  /usr/bin/swift "$DIFF_SWIFT" "$reference" "$@" > "$out" 2>/dev/null || : > "$out"
}

report_similarity_threshold() {
  printf '0.100000'
}

frame_index_to_second() {
  local file="$1"
  local idx
  idx="$(basename "$file" | sed -E 's/.*_0*([0-9]+)\.(jpg|png)/\1/')"
  if [[ -z "$idx" ]]; then
    printf '0'
  else
    awk -v i="$idx" 'BEGIN { printf "%.3f", i - 1 }'
  fi
}

asr_cache_key() {
  shasum -a 256 "$1" | awk '{print $1}'
}

ensure_asr_transcript() {
  local input="$1"
  local work_dir="$2"
  local asr_dir="$work_dir/asr"
  local base_name cache_key cache_srt srt

  mkdir -p "$asr_dir"
  base_name="$(basename "${input%.*}")"
  cache_key="$(asr_cache_key "$input")"
  cache_srt="$ASR_CACHE_DIR/${cache_key}.srt"
  LAST_ASR_CACHE_STATUS="miss"
  LAST_ASR_SRT=""

  if [[ -s "$cache_srt" ]]; then
    cp -f "$cache_srt" "$asr_dir/${base_name}.srt"
    LAST_ASR_CACHE_STATUS="hit"
    LAST_ASR_SRT="$asr_dir/${base_name}.srt"
    return 0
  fi

  "$WHISPER_BIN" "$input" --model tiny --language zh --task transcribe --output_format srt --output_dir "$asr_dir" >/dev/null 2>&1 || {
    LAST_ASR_CACHE_STATUS="error"
    return 1
  }

  srt="$(find "$asr_dir" -type f -name '*.srt' | head -n 1)"
  if [[ -n "$srt" && -s "$srt" ]]; then
    mkdir -p "$ASR_CACHE_DIR"
    cp -f "$srt" "$cache_srt"
    LAST_ASR_CACHE_STATUS="stored"
    LAST_ASR_SRT="$srt"
    return 0
  fi

  LAST_ASR_CACHE_STATUS="empty"
  return 1
}

hit_frame_time() {
  local file="$1"
  local win_start="$2"
  local fps="$3"
  local idx
  idx="$(basename "$file" | sed -E 's/.*_0*([0-9]+)\.(jpg|png)/\1/')"
  awk -v ws="$win_start" -v i="$idx" -v fps="$fps" 'BEGIN { printf "%.3f", ws + ((i - 1) / fps) }'
}

extract_coarse_frames() {
  local input="$1"
  local work_dir="$2"
  local coarse_dir="$work_dir/coarse_full"
  mkdir -p "$coarse_dir"
  ffmpeg -nostdin -hide_banner -loglevel error -i "$input" -vf fps=1 -q:v 2 "$coarse_dir/frame_%05d.jpg" -y
  printf '%s' "$coarse_dir"
}

extract_bottom_roi_frames() {
  local input="$1"
  local work_dir="$2"
  local roi_dir="$work_dir/coarse_bottom"
  mkdir -p "$roi_dir"
  ffmpeg -nostdin -hide_banner -loglevel error -i "$input" -vf "fps=1,crop=iw:floor(ih*0.38):0:floor(ih*0.62)" -q:v 2 "$roi_dir/frame_%05d.jpg" -y
  printf '%s' "$roi_dir"
}

extract_report_roi_frames() {
  local input="$1"
  local work_dir="$2"
  local roi_dir="$work_dir/coarse_report"
  mkdir -p "$roi_dir"
  ffmpeg -nostdin -hide_banner -loglevel error -i "$input" -vf "fps=1,crop=iw*0.70:ih*0.36:iw*0.15:ih*0.08,scale=iw*4:ih*4" -q:v 2 "$roi_dir/frame_%05d.jpg" -y
  printf '%s' "$roi_dir"
}

extract_visual_frame_sets_legacy() {
  local input="$1"
  local work_dir="$2"
  local coarse_dir coarse_roi coarse_report
  coarse_dir="$(extract_coarse_frames "$input" "$work_dir")"
  coarse_roi="$(extract_bottom_roi_frames "$input" "$work_dir")"
  coarse_report="$(extract_report_roi_frames "$input" "$work_dir")"
  printf '%s\n%s\n%s\n' "$coarse_dir" "$coarse_roi" "$coarse_report"
}

extract_visual_frame_sets_combined() {
  local input="$1"
  local work_dir="$2"
  local coarse_dir="$work_dir/coarse_full"
  local roi_dir="$work_dir/coarse_bottom"
  local report_dir="$work_dir/coarse_report"
  mkdir -p "$coarse_dir" "$roi_dir" "$report_dir"

  ffmpeg -nostdin -hide_banner -loglevel error -y \
    -i "$input" \
    -filter_complex "[0:v]split=3[vfull][vbottom][vreport];[vfull]fps=1[full];[vbottom]fps=1,crop=iw:floor(ih*0.38):0:floor(ih*0.62)[bottom];[vreport]fps=1,crop=iw*0.70:ih*0.36:iw*0.15:ih*0.08,scale=iw*4:ih*4[report]" \
    -map "[full]" -q:v:0 2 "$coarse_dir/frame_%05d.jpg" \
    -map "[bottom]" -q:v:1 2 "$roi_dir/frame_%05d.jpg" \
    -map "[report]" -q:v:2 2 "$report_dir/frame_%05d.jpg"

  printf '%s\n%s\n%s\n' "$coarse_dir" "$roi_dir" "$report_dir"
}

extract_visual_frame_sets() {
  local input="$1"
  local work_dir="$2"
  local frame_sets=""

  LAST_FRAME_EXTRACTION_MODE=""
  LAST_FRAME_EXTRACTION_NOTE=""
  LAST_COARSE_DIR=""
  LAST_COARSE_ROI_DIR=""
  LAST_COARSE_REPORT_DIR=""

  if [[ "$FRAME_EXTRACTION_MODE" == "legacy" ]]; then
    frame_sets="$(extract_visual_frame_sets_legacy "$input" "$work_dir")"
    LAST_FRAME_EXTRACTION_MODE="legacy"
  elif frame_sets="$(extract_visual_frame_sets_combined "$input" "$work_dir")"; then
    LAST_FRAME_EXTRACTION_MODE="combined"
  else
    LAST_FRAME_EXTRACTION_MODE="legacy_fallback"
    LAST_FRAME_EXTRACTION_NOTE="组合抽帧失败，已自动回退 legacy"
    frame_sets="$(extract_visual_frame_sets_legacy "$input" "$work_dir")"
  fi

  LAST_COARSE_DIR="$(sed -n '1p' <<<"$frame_sets")"
  LAST_COARSE_ROI_DIR="$(sed -n '2p' <<<"$frame_sets")"
  LAST_COARSE_REPORT_DIR="$(sed -n '3p' <<<"$frame_sets")"
  return 0
}

collect_visual_hits() {
  local coarse_tsv="$1"
  local roi_tsv="$2"
  local report_tsv="$3"
  local out="$4"
  : > "$out"

  while IFS=$'\t' read -r path text; do
    [[ -z "$path" ]] && continue
    local sec
    sec="$(frame_index_to_second "$path")"

    if [[ "$TARGET_TAILCARD" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex tailcard)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "tailcard_visual"
    fi
    if [[ "$TARGET_REPORT" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex report)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "report_visual"
    fi
    if [[ "$TARGET_PRICE" -eq 1 ]] && price_text_matches "$text"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "price_visual"
    fi
    if [[ "$TARGET_CHEAP" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex cheap)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "cheap_visual"
    fi
    if [[ "$TARGET_ANTIBACTERIAL" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex antibacterial)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "antibacterial_visual"
    fi
    if [[ "$TARGET_FOODGRADE" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex foodgrade)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "foodgrade_visual"
    fi
    if [[ "$TARGET_EFFICACY" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex efficacy)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "efficacy_visual"
    fi
    if [[ "$TARGET_AI_GENERATED" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex ai_generated)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "ai_generated_visual"
    fi
    if [[ "$TARGET_AD" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex ad)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "ad_visual"
    fi
  done < "$coarse_tsv"

  while IFS=$'\t' read -r path text; do
    [[ -z "$path" ]] && continue
    local sec
    sec="$(frame_index_to_second "$path")"
    if [[ "$TARGET_REPORT" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex report)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "report_roi"
    fi
    if [[ "$TARGET_PRICE" -eq 1 ]] && price_text_matches "$text"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "price_roi"
    fi
    if [[ "$TARGET_CHEAP" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex cheap)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "cheap_roi"
    fi
    if [[ "$TARGET_ANTIBACTERIAL" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex antibacterial)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "antibacterial_roi"
    fi
    if [[ "$TARGET_FOODGRADE" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex foodgrade)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "foodgrade_roi"
    fi
    if [[ "$TARGET_EFFICACY" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex efficacy)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "efficacy_roi"
    fi
    if [[ "$TARGET_AI_GENERATED" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex ai_generated)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "ai_generated_roi"
    fi
    if [[ "$TARGET_AD" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(target_regex ad)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "ad_roi"
    fi
  done < "$roi_tsv"

  while IFS=$'\t' read -r path text; do
    [[ -z "$path" ]] && continue
    local sec
    sec="$(frame_index_to_second "$path")"
    if [[ "$TARGET_REPORT" -eq 1 ]] && printf '%s' "$text" | grep -Eq "$(report_roi_regex)"; then
      append_interval "$out" "$sec" "$(awk -v s="$sec" 'BEGIN { printf "%.3f", s + 1 }')" "report_layout"
    fi
  done < "$report_tsv"
}

collect_asr_hits() {
  local input="$1"
  local work_dir="$2"
  local out="$3"
  : > "$out"
  if [[ -z "$WHISPER_BIN" ]]; then
    echo "- ASR: 未找到 whisper，跳过口播识别" >> "$REPORT"
    return 0
  fi

  ensure_asr_transcript "$input" "$work_dir" || {
    echo "- ASR: whisper 执行失败，跳过口播识别" >> "$REPORT"
    return 0
  }
  echo "- ASR缓存: ${LAST_ASR_CACHE_STATUS}" >> "$REPORT"

  local srt="$LAST_ASR_SRT"
  [[ -z "$srt" ]] && return 0

  while IFS= read -r target; do
    [[ -z "$target" || "$target" == "tailcard" ]] && continue
    local rx
    rx="$(target_regex "$target")"
    RX="$rx" LABEL="${target}_asr" perl -Mutf8 -MEncode=decode -CSDA -0ne '
      my $rx = decode("UTF-8", $ENV{RX});
      sub ts {
        my ($t) = @_;
        $t =~ /(\d+):(\d+):(\d+),(\d+)/ or return 0;
        return $1 * 3600 + $2 * 60 + $3 + $4 / 1000.0;
      }
      while (/^\d+\s*\n(\d\d:\d\d:\d\d,\d+)\s+-->\s+(\d\d:\d\d:\d\d,\d+)\s*\n(.*?)(?:\n{2,}|\z)/msg) {
        my ($s, $e, $txt) = ($1, $2, $3);
        $txt =~ s/\n/ /g;
        if ($txt =~ /$rx/) {
          my $ss = ts($s) - 0.15;
          my $ee = ts($e) + 0.15;
          $ss = 0 if $ss < 0;
          printf "%.6f %.6f %s\n", $ss, $ee, $ENV{LABEL};
        }
      }
    ' "$srt" >> "$out"
  done < <(target_list)
}

refine_visual_interval() {
  local input="$1"
  local duration="$2"
  local coarse_start="$3"
  local coarse_end="$4"
  local target="$5"
  local work_dir="$6"

  local win_start win_end win_duration zone_dir zone_roi_dir zone_report_dir zone_tsv zone_roi_tsv zone_report_tsv
  win_start="$(awk -v s="$coarse_start" 'BEGIN { v=s-1.5; if (v<0) v=0; printf "%.3f", v }')"
  win_end="$(awk -v e="$coarse_end" -v d="$duration" 'BEGIN { v=e+1.5; if (v>d) v=d; printf "%.3f", v }')"
  win_duration="$(awk -v a="$win_start" -v b="$win_end" 'BEGIN { printf "%.3f", b-a }')"
  zone_dir="$work_dir/refine_${target}_$(printf '%s_%s' "$coarse_start" "$coarse_end" | tr '.' '_')"
  zone_roi_dir="${zone_dir}_roi"
  zone_report_dir="${zone_dir}_report"
  mkdir -p "$zone_dir" "$zone_roi_dir" "$zone_report_dir"

  ffmpeg -nostdin -hide_banner -loglevel error -ss "$win_start" -i "$input" -t "$win_duration" -vf fps=10 -q:v 2 "$zone_dir/frame_%05d.jpg" -y
  ffmpeg -nostdin -hide_banner -loglevel error -ss "$win_start" -i "$input" -t "$win_duration" -vf "fps=10,crop=iw:floor(ih*0.38):0:floor(ih*0.62)" -q:v 2 "$zone_roi_dir/frame_%05d.jpg" -y
  ffmpeg -nostdin -hide_banner -loglevel error -ss "$win_start" -i "$input" -t "$win_duration" -vf "fps=10,crop=iw*0.70:ih*0.36:iw*0.15:ih*0.08,scale=iw*4:ih*4" -q:v 2 "$zone_report_dir/frame_%05d.jpg" -y

  zone_tsv="$zone_dir/ocr.tsv"
  zone_roi_tsv="$zone_roi_dir/ocr.tsv"
  zone_report_tsv="$zone_report_dir/ocr.tsv"
  ocr_dir_to_tsv_cached "$zone_dir" "$zone_tsv"
  ocr_dir_to_tsv_cached "$zone_roi_dir" "$zone_roi_tsv"
  ocr_dir_to_tsv_cached "$zone_report_dir" "$zone_report_tsv"

  local rx
  rx="$(target_regex "$target")"
  local first="" last=""
  local -a report_hit_paths=()
  while IFS=$'\t' read -r path text; do
    [[ -z "$path" ]] && continue
    if { [[ "$target" == "price" ]] && price_text_matches "$text"; } || { [[ "$target" != "price" ]] && printf '%s' "$text" | grep -Eq "$rx"; }; then
      local t
      t="$(hit_frame_time "$path" "$win_start" 10)"
      [[ -z "$first" ]] && first="$t"
      last="$t"
    fi
  done < "$zone_tsv"

  if [[ "$target" != "tailcard" ]]; then
    while IFS=$'\t' read -r path text; do
      [[ -z "$path" ]] && continue
      if { [[ "$target" == "price" ]] && price_text_matches "$text"; } || { [[ "$target" != "price" ]] && printf '%s' "$text" | grep -Eq "$rx"; }; then
        local t
        t="$(hit_frame_time "$path" "$win_start" 10)"
        if [[ -z "$first" ]] || awk -v a="$t" -v b="$first" 'BEGIN { exit !(a < b) }'; then
          first="$t"
        fi
        if [[ -z "$last" ]] || awk -v a="$t" -v b="$last" 'BEGIN { exit !(a > b) }'; then
          last="$t"
        fi
      fi
    done < "$zone_roi_tsv"
  fi

  if [[ "$target" == "report" ]]; then
    while IFS=$'\t' read -r path text; do
      [[ -z "$path" ]] && continue
      if printf '%s' "$text" | grep -Eq "$(report_roi_regex)"; then
        report_hit_paths+=("$path")
        local t
        t="$(hit_frame_time "$path" "$win_start" 10)"
        if [[ -z "$first" ]] || awk -v a="$t" -v b="$first" 'BEGIN { exit !(a < b) }'; then
          first="$t"
        fi
        if [[ -z "$last" ]] || awk -v a="$t" -v b="$last" 'BEGIN { exit !(a > b) }'; then
          last="$t"
        fi
      fi
    done < "$zone_report_tsv"
  elif [[ "$target" == "price" ]]; then
    while IFS=$'\t' read -r path text; do
      [[ -z "$path" ]] && continue
      if price_text_matches "$text"; then
        local t
        t="$(hit_frame_time "$path" "$win_start" 10)"
        if [[ -z "$first" ]] || awk -v a="$t" -v b="$first" 'BEGIN { exit !(a < b) }'; then
          first="$t"
        fi
        if [[ -z "$last" ]] || awk -v a="$t" -v b="$last" 'BEGIN { exit !(a > b) }'; then
          last="$t"
        fi
      fi
    done < "$zone_report_tsv"
  fi

  if [[ "$target" == "report" ]] && [[ "${#report_hit_paths[@]}" -gt 0 ]]; then
    local -a zone_report_paths first_scores last_scores
    zone_report_paths=("$zone_report_dir"/frame_*.jpg)

    local first_anchor="${report_hit_paths[0]}"
    local last_anchor="${report_hit_paths[$((${#report_hit_paths[@]} - 1))]}"
    local first_diff_tsv="$zone_report_dir/diff_from_first.tsv"
    local last_diff_tsv="$zone_report_dir/diff_from_last.tsv"
    local threshold
    threshold="$(report_similarity_threshold)"

    image_diff_to_tsv_safe "$first_anchor" "$first_diff_tsv" "${zone_report_paths[@]}"
    image_diff_to_tsv_safe "$last_anchor" "$last_diff_tsv" "${zone_report_paths[@]}"

    while IFS=$'\t' read -r _ score; do
      first_scores+=("$score")
    done < "$first_diff_tsv"

    while IFS=$'\t' read -r _ score; do
      last_scores+=("$score")
    done < "$last_diff_tsv"

    local first_anchor_pos=-1
    local last_anchor_pos=-1
    local i
    for ((i=0; i<${#zone_report_paths[@]}; i++)); do
      [[ "${zone_report_paths[$i]}" == "$first_anchor" ]] && first_anchor_pos="$i"
      [[ "${zone_report_paths[$i]}" == "$last_anchor" ]] && last_anchor_pos="$i"
    done

    if [[ "$first_anchor_pos" -ge 0 ]] && [[ "${#first_scores[@]}" -eq "${#zone_report_paths[@]}" ]]; then
      for ((i=first_anchor_pos-1; i>=0; i--)); do
        if awk -v s="${first_scores[$i]}" -v th="$threshold" 'BEGIN { exit !(s <= th) }'; then
          first="$(hit_frame_time "${zone_report_paths[$i]}" "$win_start" 10)"
        else
          break
        fi
      done
    fi

    if [[ "$last_anchor_pos" -ge 0 ]] && [[ "${#last_scores[@]}" -eq "${#zone_report_paths[@]}" ]]; then
      for ((i=last_anchor_pos+1; i<${#zone_report_paths[@]}; i++)); do
        if awk -v s="${last_scores[$i]}" -v th="$threshold" 'BEGIN { exit !(s <= th) }'; then
          last="$(hit_frame_time "${zone_report_paths[$i]}" "$win_start" 10)"
        else
          break
        fi
      done
    fi
  fi

  if [[ -z "$first" ]]; then
    printf '%.6f %.6f\n' "$coarse_start" "$coarse_end"
    return 0
  fi

  if [[ "$target" == "tailcard" ]]; then
    awk -v f="$first" -v l="$last" -v d="$duration" 'BEGIN {
      s=f-0.1; if (s<0) s=0;
      if (f >= d - 8) {
        e=d;
      } else {
        e=l+0.2;
        if (e>d) e=d;
      }
      printf "%.6f %.6f\n", s, e
    }'
  elif [[ "$target" == "report" ]]; then
    awk -v f="$first" -v l="$last" -v d="$duration" 'BEGIN {
      s=f-0.15; e=l+0.2;
      if (s<0) s=0;
      if (e>d) e=d;
      printf "%.6f %.6f\n", s, e
    }'
  elif [[ "$target" == "price" ]]; then
    awk -v f="$first" -v l="$last" -v d="$duration" 'BEGIN {
      s=f-1.0; e=l+1.9;
      if (s<0) s=0;
      if (e>d) e=d;
      printf "%.6f %.6f\n", s, e
    }'
  else
    awk -v f="$first" -v l="$last" -v d="$duration" 'BEGIN {
      s=f-0.1; e=l+0.2;
      if (s<0) s=0;
      if (e>d) e=d;
      printf "%.6f %.6f\n", s, e
    }'
  fi
}

merge_cuts() {
  local in_file="$1"
  local out_file="$2"
  local duration="$3"
  awk -v d="$duration" '
    {
      s=$1+0; e=$2+0;
      if (s>e) {tmp=s; s=e; e=tmp}
      if (e<=0 || s>=d) next
      if (s<0) s=0
      if (e>d) e=d
      if (e-s<0.05) next
      printf "%.6f %.6f\n", s, e
    }
  ' "$in_file" | sort -n -k1,1 -k2,2 > "${out_file}.norm"

  if [[ -s "${out_file}.norm" ]]; then
    awk '
      NR==1 { s=$1; e=$2; next }
      {
        if ($1 <= e + 0.000001) {
          if ($2 > e) e=$2
        } else {
          printf "%.6f %.6f\n", s, e
          s=$1; e=$2
        }
      }
      END {
        if (NR>0) printf "%.6f %.6f\n", s, e
      }
    ' "${out_file}.norm" > "$out_file"
  else
    : > "$out_file"
  fi
}

merge_reasoned_hits() {
  local in_file="$1"
  local out_file="$2"
  : > "$out_file"
  if [[ ! -s "$in_file" ]]; then
    return 0
  fi

  while IFS= read -r target; do
    [[ -z "$target" ]] && continue
    awk -v t="$target" '
      $3 ~ ("^" t "_") {
        printf "%.6f %.6f\n", $1, $2
      }
    ' "$in_file" | sort -n -k1,1 -k2,2 > "${out_file}.${target}.norm"

    if [[ -s "${out_file}.${target}.norm" ]]; then
      awk -v target="$target" '
        NR==1 { s=$1; e=$2; next }
        {
          if ($1 <= e + 0.25) {
            if ($2 > e) e=$2
          } else {
            printf "%.6f %.6f %s_merged\n", s, e, target
            s=$1; e=$2
          }
        }
        END {
          if (NR>0) printf "%.6f %.6f %s_merged\n", s, e, target
        }
      ' "${out_file}.${target}.norm" >> "$out_file"
    fi
  done < <(target_list)
}

build_video_chain_prefix() {
  local width="$1"
  local height="$2"
  local duration="$3"
  local top_left_box="${4:-}"
  local top_right_box="${5:-}"
  local br_x br_y br_w br_h chain_in chain_out
  local tl_x tl_y tl_w tl_h tr_x tr_y tr_w tr_h
  local chain_idx=1

  br_x="$(awk -v w="$width" 'BEGIN { v=int(w*0.590); if (v > w-30) v = w-30; print v }')"
  br_y="$(awk -v h="$height" 'BEGIN { v=int(h*0.855); if (v > h-30) v = h-30; print v }')"
  br_w="$(awk -v w="$width" 'BEGIN { v=int(w*0.396); if (v > w-20) v = w-20; print v }')"
  br_h="$(awk -v h="$height" 'BEGIN { v=int(h*0.141); if (v > h-20) v = h-20; print v }')"

  chain_in='[0:v]'
  if [[ -n "$top_left_box" ]]; then
    read -r tl_x tl_y tl_w tl_h <<< "$top_left_box"
    chain_out="[dl${chain_idx}]"
    printf "%sdelogo=x=%s:y=%s:w=%s:h=%s:enable='between(t,0,5)'%s;\n" "$chain_in" "$tl_x" "$tl_y" "$tl_w" "$tl_h" "$chain_out"
    chain_in="$chain_out"
    chain_idx=$((chain_idx + 1))
  fi
  if [[ -n "$top_right_box" ]]; then
    read -r tr_x tr_y tr_w tr_h <<< "$top_right_box"
    chain_out="[dl${chain_idx}]"
    printf "%sdelogo=x=%s:y=%s:w=%s:h=%s%s;\n" "$chain_in" "$tr_x" "$tr_y" "$tr_w" "$tr_h" "$chain_out"
    chain_in="$chain_out"
  fi
  printf "%sdelogo=x=%s:y=%s:w=%s:h=%s[dv];\n" "$chain_in" "$br_x" "$br_y" "$br_w" "$br_h"
  printf '[dv]'
}

build_keeps() {
  local cuts_file="$1"
  local keeps_file="$2"
  local duration="$3"
  if [[ -s "$cuts_file" ]]; then
    awk -v d="$duration" '
      BEGIN { prev=0 }
      {
        if ($1 > prev + 0.000001) printf "%.6f %.6f\n", prev, $1
        if ($2 > prev) prev=$2
      }
      END {
        if (d > prev + 0.000001) printf "%.6f %.6f\n", prev, d
      }
    ' "$cuts_file" | awk '{ if (($2-$1) >= 0.20) print }' > "$keeps_file"
  else
    printf '0 %.6f\n' "$duration" > "$keeps_file"
  fi
}

needs_qianchuan_normalize() {
  local width="$1"
  local height="$2"
  if [[ "$width" == "720" && "$height" == "1280" ]]; then
    return 1
  fi
  if [[ "$width" == "1080" && "$height" == "1920" ]]; then
    return 1
  fi
  return 0
}

build_filter_script() {
  local keeps="$1"
  local filter_script="$2"
  local width="$3"
  local height="$4"
  local duration="$5"
  local top_left_box="${6:-}"
  local top_right_box="${7:-}"
  local seg_count
  seg_count=$(wc -l < "$keeps" | tr -d ' ')
  {
    build_video_chain_prefix "$width" "$height" "$duration" "$top_left_box" "$top_right_box"
    printf 'split=%d' "$seg_count"
    for ((i=0; i<seg_count; i++)); do printf '[vin%d]' "$i"; done
    printf ';\n'
    printf '[0:a]asplit=%d' "$seg_count"
    for ((i=0; i<seg_count; i++)); do printf '[ain%d]' "$i"; done
    printf ';\n'
    i=0
    while read -r s e; do
      local s_fmt e_fmt dur audio_chain fade_out_start
      s_fmt="$(awk -v x="$s" 'BEGIN { printf "%.3f", x }')"
      e_fmt="$(awk -v x="$e" 'BEGIN { printf "%.3f", x }')"
      dur="$(awk -v a="$s" -v b="$e" 'BEGIN { printf "%.3f", b-a }')"
      printf '[vin%d]trim=start=%s:end=%s,setpts=PTS-STARTPTS[v%d];\n' "$i" "$s_fmt" "$e_fmt" "$i"
      audio_chain="atrim=start=${s_fmt}:end=${e_fmt},asetpts=PTS-STARTPTS"
      if [[ "$i" -gt 0 ]] && awk -v d="$dur" 'BEGIN { exit !(d > 0.30) }'; then
        audio_chain+=",afade=t=in:st=0:d=0.12"
      fi
      if [[ "$i" -lt $((seg_count-1)) ]] && awk -v d="$dur" 'BEGIN { exit !(d > 0.40) }'; then
        fade_out_start="$(awk -v d="$dur" 'BEGIN { st=d-0.18; if (st<0) st=0; printf "%.3f", st }')"
        audio_chain+=",afade=t=out:st=${fade_out_start}:d=0.18"
      fi
      printf '[ain%d]%s[a%d];\n' "$i" "$audio_chain" "$i"
      i=$((i+1))
    done < "$keeps"
    local concat_inputs=""
    for ((i=0; i<seg_count; i++)); do
      concat_inputs+="[v${i}][a${i}]"
    done
    if needs_qianchuan_normalize "$width" "$height"; then
      printf '%sconcat=n=%d:v=1:a=1[outv_raw][outa];\n' "$concat_inputs" "$seg_count"
      printf '[outv_raw]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[outv]\n'
    else
      printf '%sconcat=n=%d:v=1:a=1[outv][outa]\n' "$concat_inputs" "$seg_count"
    fi
  } > "$filter_script"
}

process_one() {
  local input="$1"
  local name base duration width height work_dir cuts_raw coarse_merged refined_cuts keeps filter_script out_mp4
  local top_left_info_box=""
  local top_right_ad_box=""
  name="$(basename "$input")"
  base="${name%.mp4}"
  duration="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$input")"
  width="$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=nw=1:nk=1 "$input")"
  height="$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=nw=1:nk=1 "$input")"
  [[ -z "$duration" ]] && return 1

  work_dir="$RUN_DIR/$base"
  mkdir -p "$work_dir"
  cuts_raw="$work_dir/cuts_raw.txt"
  coarse_merged="$work_dir/cuts_coarse_merged.txt"
  refined_cuts="$work_dir/cuts_refined.txt"
  keeps="$work_dir/keeps.txt"
  filter_script="$work_dir/filter_complex.txt"
  out_mp4="$RUN_DIR/${base}_clip.mp4"
  : > "$cuts_raw"

  if [[ -n "$MANUAL_HEAD_SEC" ]]; then
    append_interval "$cuts_raw" 0 "$MANUAL_HEAD_SEC" "manual_head"
  fi
  if [[ -n "$MANUAL_TAIL_SEC" ]]; then
    append_interval "$cuts_raw" "$(awk -v d="$duration" -v t="$MANUAL_TAIL_SEC" 'BEGIN { s=d-t; if (s<0) s=0; print s }')" "$duration" "manual_tail"
  fi
  if [[ -n "$MANUAL_KEEP_FIRST_SEC" ]]; then
    append_interval "$cuts_raw" "$MANUAL_KEEP_FIRST_SEC" "$duration" "manual_keep_first"
  fi
  if [[ -s "$RANGE_FILE_RAW" ]]; then
    while read -r s e; do
      append_interval "$cuts_raw" "$s" "$e" "manual_range"
    done < "$RANGE_FILE_RAW"
  fi

  if needs_visual_detection; then
    local coarse_dir coarse_roi coarse_report coarse_tsv coarse_roi_tsv coarse_report_tsv visual_hits
    local ocr_cache_hits_before ocr_cache_misses_before
    ocr_cache_hits_before="$OCR_CACHE_HIT_COUNT"
    ocr_cache_misses_before="$OCR_CACHE_MISS_COUNT"
    extract_visual_frame_sets "$input" "$work_dir"
    coarse_dir="$LAST_COARSE_DIR"
    coarse_roi="$LAST_COARSE_ROI_DIR"
    coarse_report="$LAST_COARSE_REPORT_DIR"
    coarse_tsv="$work_dir/coarse_full.tsv"
    coarse_roi_tsv="$work_dir/coarse_bottom.tsv"
    coarse_report_tsv="$work_dir/coarse_report.tsv"
    visual_hits="$work_dir/visual_hits.txt"
    echo "- $name: 实际粗扫抽帧模式: ${LAST_FRAME_EXTRACTION_MODE:-unknown}" >> "$REPORT"
    if [[ -n "$LAST_FRAME_EXTRACTION_NOTE" ]]; then
      echo "  - 说明: $LAST_FRAME_EXTRACTION_NOTE" >> "$REPORT"
    fi
    ocr_dir_to_tsv_cached "$coarse_dir" "$coarse_tsv"
    ocr_dir_to_tsv_cached "$coarse_roi" "$coarse_roi_tsv"
    ocr_dir_to_tsv_cached "$coarse_report" "$coarse_report_tsv"
    collect_visual_hits "$coarse_tsv" "$coarse_roi_tsv" "$coarse_report_tsv" "$visual_hits"
    top_left_info_box="$(detect_top_left_info_box "$coarse_tsv" "$width" "$height" "$work_dir" || true)"
    top_right_ad_box="$(detect_top_right_ad_box "$coarse_tsv" "$width" "$height" "$work_dir" || true)"

    if [[ -s "$visual_hits" ]]; then
      merge_reasoned_hits "$visual_hits" "$coarse_merged"
      while read -r s e reason; do
        local target refined
        target="${reason%%_*}"
        refined="$(refine_visual_interval "$input" "$duration" "$s" "$e" "$target" "$work_dir")"
        append_interval "$cuts_raw" "$(printf '%s' "$refined" | awk '{print $1}')" "$(printf '%s' "$refined" | awk '{print $2}')" "$reason"
      done < "$coarse_merged"
    fi
    echo "- OCR缓存: hit=$((OCR_CACHE_HIT_COUNT - ocr_cache_hits_before)) miss=$((OCR_CACHE_MISS_COUNT - ocr_cache_misses_before))" >> "$REPORT"
  fi

  if needs_asr_detection; then
    local asr_hits
    asr_hits="$work_dir/asr_hits.txt"
    collect_asr_hits "$input" "$work_dir" "$asr_hits"
    if [[ -s "$asr_hits" ]]; then
      cat "$asr_hits" >> "$cuts_raw"
    fi
  fi

  merge_cuts "$cuts_raw" "$refined_cuts" "$duration"
  build_keeps "$refined_cuts" "$keeps" "$duration"

  local seg_count
  seg_count=$(wc -l < "$keeps" | tr -d ' ')
  if [[ "$seg_count" -eq 0 ]]; then
    echo "- $name: 无可保留片段（规则过严）" >> "$REPORT"
    return 0
  fi

  build_filter_script "$keeps" "$filter_script" "$width" "$height" "$duration" "$top_left_info_box" "$top_right_ad_box"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[DRY-RUN] $name => $out_mp4"
  else
    ffmpeg -nostdin -hide_banner -loglevel error -y -i "$input" \
      -filter_complex_script "$filter_script" \
      -map '[outv]' -map '[outa]' \
      -c:v libx264 -profile:v high -level 4.0 -crf 18 -preset medium \
      -c:a aac -b:a 128k -ar 44100 \
      -pix_fmt yuv420p -movflags +faststart \
      "$out_mp4"
  fi

  local out_dur
  if [[ "$DRY_RUN" -eq 0 ]]; then
    out_dur="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$out_mp4")"
  else
    out_dur="dry-run"
  fi

  {
    echo ""
    echo "### $name"
    echo "- 输入: $input"
    echo "- 输出: $out_mp4"
    echo "- 原始时长: $(awk -v x="$duration" 'BEGIN { printf "%.2f", x }')s"
    echo "- 检测目标: $(targets_summary)"
    if [[ -n "$top_left_info_box" ]]; then
      echo "- 顶部左侧去水印: $top_left_info_box"
    else
      echo "- 顶部左侧去水印: 未检测到"
    fi
    if [[ -n "$top_right_ad_box" ]]; then
      echo "- 顶部右侧去水印: $top_right_ad_box"
    else
      echo "- 顶部右侧去水印: 未检测到"
    fi
    if [[ "$DRY_RUN" -eq 0 ]]; then
      echo "- 输出时长: $(awk -v x="$out_dur" 'BEGIN { printf "%.2f", x }')s"
    else
      echo "- 输出时长: dry-run"
    fi
    echo "- 最终 CUT:"
    if [[ -s "$refined_cuts" ]]; then
      while read -r s e; do
        echo "  - $(awk -v x="$s" 'BEGIN { printf "%.2f", x }')s ~ $(awk -v x="$e" 'BEGIN { printf "%.2f", x }')s"
      done < "$refined_cuts"
    else
      echo "  - 无"
    fi
  } >> "$REPORT"

  return 0
}

run_parallel_batch() {
  local worker_output_root worker_log_root idx log_file status_file input_file status
  worker_output_root="$RUN_DIR/worker_outputs"
  worker_log_root="$RUN_DIR/worker_logs"
  mkdir -p "$worker_output_root" "$worker_log_root"

  idx=0
  while IFS= read -r video; do
    idx=$((idx+1))
    log_file="$worker_log_root/$(printf '%03d' "$idx").log"
    status_file="$worker_log_root/$(printf '%03d' "$idx").status"
    input_file="$worker_log_root/$(printf '%03d' "$idx").input"
    printf '%s\n' "$video" > "$input_file"

    (
      if bash "$0" \
        --query "$QUERY" \
        --input "$video" \
        --output-root "$worker_output_root" \
        --workers 1 \
        $([[ "$DRY_RUN" -eq 1 ]] && printf '%s' '--dry-run') \
        $([[ "$KEEP_ARTIFACTS" -eq 1 ]] && printf '%s' '--keep-artifacts') \
        > "$log_file" 2>&1; then
        printf 'ok\n' > "$status_file"
      else
        printf 'fail\n' > "$status_file"
      fi
    ) &

    while [[ "$(jobs -pr | wc -l | tr -d ' ')" -ge "$WORKERS" ]]; do
      sleep 0.2
    done
  done < "$VIDEO_LIST"

  wait

  ok=0
  fail=0
  while IFS= read -r status_file; do
    status="$(cat "$status_file" 2>/dev/null || true)"
    if [[ "$status" == "ok" ]]; then
      ok=$((ok+1))
    else
      fail=$((fail+1))
    fi
  done < <(find "$worker_log_root" -type f -name '*.status' | sort)

  if [[ $((ok + fail)) -lt "$SELECTED" ]]; then
    fail=$((SELECTED - ok))
  fi

  {
    echo ""
    echo "## 并行批量"
    echo "- 并行 worker 数: $WORKERS"
    echo "- worker 输出目录: $worker_output_root"
    echo "- worker 日志目录: $worker_log_root"
  } >> "$REPORT"
}

parse_query

echo "" >> "$REPORT"
echo "## 规则解析" >> "$REPORT"
echo "- 开头裁剪秒数: ${MANUAL_HEAD_SEC:-无}" >> "$REPORT"
echo "- 结尾裁剪秒数: ${MANUAL_TAIL_SEC:-无}" >> "$REPORT"
echo "- 保留前N秒: ${MANUAL_KEEP_FIRST_SEC:-无}" >> "$REPORT"
echo "- 自动识别目标: $(targets_summary)" >> "$REPORT"
if [[ -s "$RANGE_FILE_RAW" ]]; then
  echo "- 显式删除区间:" >> "$REPORT"
  while read -r s e; do
    echo "  - ${s}s ~ ${e}s" >> "$REPORT"
  done < "$RANGE_FILE_RAW"
else
  echo "- 显式删除区间: 无" >> "$REPORT"
fi

VIDEO_LIST="$RUN_DIR/待处理视频.txt"
if [[ -n "$INPUT_FILE" ]]; then
  if [[ ! -f "$INPUT_FILE" ]]; then
    echo "--input 指定文件不存在: $INPUT_FILE" >&2
    exit 1
  fi
  printf '%s\n' "$INPUT_FILE" > "$VIDEO_LIST"
else
  find "$ROOT_DIR" -type f -path '*/带货视频/*.mp4' | sort > "$VIDEO_LIST"
fi

TOTAL_VIDEOS=$(wc -l < "$VIDEO_LIST" | tr -d ' ')
if [[ "$TOTAL_VIDEOS" -eq 0 ]]; then
  echo "未发现任何带货视频: $ROOT_DIR" >&2
  exit 1
fi
if [[ "$LIMIT" -gt 0 ]]; then
  head -n "$LIMIT" "$VIDEO_LIST" > "$VIDEO_LIST.tmp"
  mv "$VIDEO_LIST.tmp" "$VIDEO_LIST"
fi

SELECTED=$(wc -l < "$VIDEO_LIST" | tr -d ' ')
echo "" >> "$REPORT"
echo "## 视频选择" >> "$REPORT"
echo "- 扫描到视频总数: $TOTAL_VIDEOS" >> "$REPORT"
echo "- 本次处理数量: $SELECTED" >> "$REPORT"

ok=0
fail=0
if [[ "$WORKERS" -gt 1 ]] && [[ "$SELECTED" -gt 1 ]] && [[ -z "$INPUT_FILE" ]]; then
  run_parallel_batch
else
  while IFS= read -r video; do
    if process_one "$video"; then
      ok=$((ok+1))
    else
      fail=$((fail+1))
    fi
  done < "$VIDEO_LIST"
fi

echo "" >> "$REPORT"
echo "## 汇总" >> "$REPORT"
echo "- 成功: $ok" >> "$REPORT"
echo "- 失败: $fail" >> "$REPORT"

FINAL_OUTPUT_NOTE=""
if [[ "$KEEP_ARTIFACTS" -eq 0 ]]; then
  _out_files=()
  while IFS= read -r _f; do
    _out_files+=("$_f")
  done < <(find "$RUN_DIR" -type f -name '*_clip.mp4' | sort)
  out_count="${#_out_files[@]}"

  if [[ "$out_count" -gt 0 ]]; then
    for _f in "${_out_files[@]}"; do
      mv -f "$_f" "$OUTPUT_ROOT/$(basename "$_f")"
    done
    rm -rf "$RUN_DIR"
    if [[ "$out_count" -eq 1 ]]; then
      FINAL_OUTPUT_NOTE="$OUTPUT_ROOT/$(basename "${_out_files[0]}")"
    else
      FINAL_OUTPUT_NOTE="$OUTPUT_ROOT"
    fi
  fi
fi

echo "执行完成。输出目录: ${FINAL_OUTPUT_NOTE:-$RUN_DIR}"
if [[ -f "$REPORT" ]]; then
  echo "报告文件: $REPORT"
fi
if [[ -n "$FINAL_OUTPUT_NOTE" ]]; then
  echo "最终保留: $FINAL_OUTPUT_NOTE"
fi
