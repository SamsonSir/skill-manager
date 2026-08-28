#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  prepare_listing_draft.sh --source-json <完整数据.json> --output-dir <dir> [选项]

选项:
  --source-json <path>   输入的商品完整数据 JSON
  --output-dir <dir>     输出目录
  --price <number>       上架价格，默认 999
  --brand <name>         上架品牌，默认 无品牌
  --help                 显示帮助
EOF
}

SOURCE_JSON=""
OUTPUT_DIR=""
LISTING_PRICE="999"
LISTING_BRAND="无品牌"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-json)
      SOURCE_JSON="${2:-}"; shift 2 ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"; shift 2 ;;
    --price)
      LISTING_PRICE="${2:-}"; shift 2 ;;
    --brand)
      LISTING_BRAND="${2:-}"; shift 2 ;;
    --help|-h)
      usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$SOURCE_JSON" || -z "$OUTPUT_DIR" ]]; then
  echo "缺少必填参数" >&2
  usage
  exit 1
fi

if [[ ! -f "$SOURCE_JSON" ]]; then
  echo "输入文件不存在: $SOURCE_JSON" >&2
  exit 1
fi

for cmd in jq python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "缺少依赖: $cmd" >&2
    exit 1
  fi
done

SOURCE_JSON_ABS="$(cd "$(dirname "$SOURCE_JSON")" && pwd)/$(basename "$SOURCE_JSON")"
SOURCE_DIR="$(cd "$(dirname "$SOURCE_JSON_ABS")" && pwd)"
OUTPUT_DIR_ABS="$(mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd)"

RAW_TITLE="$(jq -r '.detail.title // .candidate.product_name // empty' "$SOURCE_JSON_ABS")"
RAW_BRAND="$(jq -r '.detail.params["品牌"] // empty' "$SOURCE_JSON_ABS")"
CATEGORY_RAW="$(jq -r '.meta.category_raw // empty' "$SOURCE_JSON_ABS")"
SPEC_RAW="$(jq -r '.detail.params["规格类型"] // empty' "$SOURCE_JSON_ABS")"
ORIGIN_RAW="$(jq -r '.detail.params["产地"] // empty' "$SOURCE_JSON_ABS")"
if [[ -z "$ORIGIN_RAW" || "$ORIGIN_RAW" == "null" ]]; then
  ORIGIN_RAW="$(jq -r '.detail.origin // empty' "$SOURCE_JSON_ABS")"
fi
if [[ -z "$ORIGIN_RAW" || "$ORIGIN_RAW" == "null" ]]; then
  ORIGIN_RAW="福建"
fi
SHIPPING_FROM="$(jq -r '.detail.shipping_from // empty' "$SOURCE_JSON_ABS")"
if [[ -z "$SHIPPING_FROM" || "$SHIPPING_FROM" == "null" ]]; then
  SHIPPING_FROM="广东省广州市"
fi

MAIN_IMAGE_DIR="$SOURCE_DIR/主图"
DETAIL_IMAGE_DIR="$SOURCE_DIR/详情图_修正"

if [[ ! -d "$MAIN_IMAGE_DIR" ]]; then
  echo "主图目录不存在: $MAIN_IMAGE_DIR" >&2
  exit 1
fi

if [[ ! -d "$DETAIL_IMAGE_DIR" ]]; then
  echo "详情图目录不存在: $DETAIL_IMAGE_DIR" >&2
  exit 1
fi

MAIN_IMAGES_JSON="$(find "$MAIN_IMAGE_DIR" -maxdepth 1 -type f | sort | jq -R . | jq -s .)"
DETAIL_IMAGES_JSON="$(find "$DETAIL_IMAGE_DIR" -maxdepth 1 -type f | sort | jq -R . | jq -s .)"

sanitize_title() {
  printf '%s' "$1" \
    | sed -E 's/【[^】]*】//g' \
    | sed -E 's/YILAIXI|yilaixi|亿来喜//g' \
    | sed -E 's/正品//g' \
    | sed -E 's/[[:space:]]+/ /g' \
    | sed -E 's/^ +| +$//g'
}

DEFAULT_TITLE="$(sanitize_title "$RAW_TITLE")"
DEFAULT_TITLE="$(printf '%s' "$DEFAULT_TITLE" | sed -E 's/留香//g; s/[[:space:]]+/ /g; s/^ +| +$//g')"

TITLE_OPTION_1="$DEFAULT_TITLE"
TITLE_OPTION_2="家用盘香檀香艾草熏香室内香薰卫生间卧室办公室清香"
TITLE_OPTION_3="手工盘香艾草檀香家居室内熏香卫生间卧室办公室香薰"

TITLE_OPTIONS_JSON="$(jq -nc \
  --arg a "$TITLE_OPTION_1" \
  --arg b "$TITLE_OPTION_2" \
  --arg c "$TITLE_OPTION_3" \
  '[$a,$b,$c]')"

CATEGORY_PATH_JSON="$(printf '%s' "$CATEGORY_RAW" | awk -F'/' '
  BEGIN { printf "[" }
  {
    for (i = 1; i <= NF; i++) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
      if ($i == "") continue
      if (printed) printf ","
      gsub(/"/, "\\\"", $i)
      printf "\"%s\"", $i
      printed = 1
    }
  }
  END { printf "]" }')"

REMOVED_TERMS_JSON='["亿来喜","YILAIXI","正品"]'
RISK_TERMS_JSON='["满屋用半年","免费试用","不满意全退","假一赔三","假一赔十","批准文号","买就送"]'

JSON_PATH="$OUTPUT_DIR_ABS/上架草稿数据.json"
MD_PATH="$OUTPUT_DIR_ABS/自动化上架流程.md"

jq -n \
  --arg generated_at "$(date '+%Y-%m-%d %H:%M:%S')" \
  --arg source_json "$SOURCE_JSON_ABS" \
  --arg raw_title "$RAW_TITLE" \
  --arg raw_brand "$RAW_BRAND" \
  --arg default_title "$DEFAULT_TITLE" \
  --arg listing_brand "$LISTING_BRAND" \
  --argjson listing_price "$LISTING_PRICE" \
  --arg spec "$SPEC_RAW" \
  --arg origin "$ORIGIN_RAW" \
  --arg shipping_from "$SHIPPING_FROM" \
  --arg main_image_dir "$MAIN_IMAGE_DIR" \
  --arg detail_image_dir "$DETAIL_IMAGE_DIR" \
  --argjson main_images "$MAIN_IMAGES_JSON" \
  --argjson detail_images "$DETAIL_IMAGES_JSON" \
  --argjson title_options "$TITLE_OPTIONS_JSON" \
  --argjson category_path "$CATEGORY_PATH_JSON" \
  --argjson removed_terms "$REMOVED_TERMS_JSON" \
  --argjson risk_terms "$RISK_TERMS_JSON" \
  '{
    meta: {
      generated_at: $generated_at,
      source_json: $source_json,
      purpose: "抖店自动化上架准备"
    },
    source: {
      raw_title: $raw_title,
      raw_brand: $raw_brand
    },
    listing: {
      title: $default_title,
      title_options: $title_options,
      brand: $listing_brand,
      price: $listing_price,
      category_path: $category_path,
      spec: $spec,
      origin: $origin,
      shipping_from: $shipping_from
    },
    assets: {
      main_image_dir: $main_image_dir,
      detail_image_dir: $detail_image_dir,
      main_images: $main_images,
      detail_images: $detail_images
    },
    review: {
      removed_terms: $removed_terms,
      risk_terms_for_manual_check: $risk_terms,
      notes: [
        "主图与详情图在真正上架前需要二次人工过滤，避免直接沿用竞品品牌与售后承诺文案。",
        "当前仅固化价格和品牌默认值，不直接替用户执行发布。"
      ]
    }
  }' >"$JSON_PATH"

python3 - <<'PY' "$JSON_PATH" "$MD_PATH"
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])
md_path = Path(sys.argv[2])
data = json.loads(json_path.read_text())

title_options = "\n".join(
    f"{idx}. {title}" for idx, title in enumerate(data["listing"]["title_options"], start=1)
)
main_images = "\n".join(f"- {p}" for p in data["assets"]["main_images"])
detail_images = "\n".join(f"- {p}" for p in data["assets"]["detail_images"][:10])
risk_terms = "\n".join(f"- {term}" for term in data["review"]["risk_terms_for_manual_check"])
removed_terms = "、".join(data["review"]["removed_terms"])
category_path = " / ".join(data["listing"]["category_path"])

content = f"""# 自动化上架流程

## 一、任务定位
- 来源文档：上架步骤流程文档（docx）
- 来源数据：{data["meta"]["source_json"]}
- 目标平台：抖店 `https://fxg.jinritemai.com/ffa/g/list?btm_ppre=a0.b0.c0.d0&btm_pre=a0.b0.c0.d0`
- 本次固定值：品牌：{data["listing"]["brand"]}；价格：{data["listing"]["price"]}

## 二、建议标题
{title_options}

默认标题：{data["listing"]["title"]}

已从标题中去除：{removed_terms}

## 三、建议填写字段
| 字段 | 值 |
|------|------|
| 类目路径 | {category_path} |
| 商品标题 | {data["listing"]["title"]} |
| 品牌 | {data["listing"]["brand"]} |
| 价格 | {data["listing"]["price"]} |
| 主售规格 | {data["listing"]["spec"]} |
| 产地 | {data["listing"]["origin"]} |
| 发货地 | {data["listing"]["shipping_from"]} |

## 四、素材清单
### 主图
{main_images}

### 详情图（前 10 张示例）
{detail_images}

详情图总数：{len(data["assets"]["detail_images"])} 张

## 五、自动化执行顺序
1. 打开抖店商品列表页并进入“创建商品”。
2. 在类目搜索框输入与商品最接近的关键词，优先按 `{category_path}` 路径落类。
3. 上传主图，填入默认标题或从 3 个候选标题中选 1 个。
4. 品牌固定选择“{data["listing"]["brand"]}”，价格固定填写 `{data["listing"]["price"]}`。
5. 规格先按 `{data["listing"]["spec"]}` 建立主售规格，其他规格暂不自动扩展。
6. 详情图从 `{data["assets"]["detail_image_dir"]}` 读取，但上传前先执行人工筛图。
7. 所有必填项完成后提交审核；若驳回，按驳回原因回到标题、图片或详情文案重新修正。

## 六、人工复核重点
- 主图和详情图里若出现品牌词、店铺名，要先清掉再上传。
- 以下高风险文案不要直接沿用，尤其是 OCR 或图片上识别到时必须删改：
{risk_terms}
- 当前商品明确需要重点看 `满屋用半年` 这类带时长承诺的表达。
- “免费试用”“假一赔三/十”“批准文号”等内容没有完成资质核验前，不要自动写入详情。
- docx 中提到的极限词、资质词、明确数值承诺，统一视为人工审核门槛，不直接自动发布。

## 七、给后续自动化脚本的输入
- 结构化草稿 JSON：`{json_path}`
- 主图目录：`{data["assets"]["main_image_dir"]}`
- 详情图目录：`{data["assets"]["detail_image_dir"]}`
- 推荐做法：浏览器自动化只负责填表和上传，标题/详情图选择前加一步人工确认。
"""

md_path.write_text(content)
PY

echo "JSON_PATH=$JSON_PATH"
echo "MD_PATH=$MD_PATH"
