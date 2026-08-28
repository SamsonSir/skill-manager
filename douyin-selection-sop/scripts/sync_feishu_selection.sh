#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  sync_feishu_selection.sh --record-id <rec_xxx> [选项]

选项:
  --base-token <token>         默认 QqKbbaGvvah8CgsMSWzcHZcMn1c
  --table-id <id>              默认 tblmnpex440PHytL
  --record-id <id>             必填，目标记录 ID
  --status <label>             可选，更新“选品状态”
  --note-append <text>         可选，追加到“备注”末尾
  --eval-time-field <name>     可选，默认“最近评估时间”
  --dry-run                    仅打印将写入 payload，不执行回写
  --help                       显示帮助
EOF
}

BASE_TOKEN="QqKbbaGvvah8CgsMSWzcHZcMn1c"
TABLE_ID="tblmnpex440PHytL"
RECORD_ID=""
STATUS=""
NOTE_APPEND=""
EVAL_TIME_FIELD="最近评估时间"
DRY_RUN="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-token) BASE_TOKEN="${2:-}"; shift 2 ;;
    --table-id) TABLE_ID="${2:-}"; shift 2 ;;
    --record-id) RECORD_ID="${2:-}"; shift 2 ;;
    --status) STATUS="${2:-}"; shift 2 ;;
    --note-append) NOTE_APPEND="${2:-}"; shift 2 ;;
    --eval-time-field) EVAL_TIME_FIELD="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN="1"; shift ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$RECORD_ID" ]]; then
  echo "缺少 --record-id" >&2
  usage
  exit 1
fi

for cmd in lark-cli jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "缺少依赖: $cmd" >&2
    exit 1
  fi
done

FIELDS_JSON="$(lark-cli base +field-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --offset 0 --limit 200)"
RECORD_JSON="$(lark-cli base +record-get --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --record-id "$RECORD_ID")"

EXISTING_NOTE="$(echo "$RECORD_JSON" | jq -r '.data.record["备注"] // ""')"
NOW_TS="$(date '+%Y-%m-%d %H:%M:%S')"

if [[ -n "$NOTE_APPEND" ]]; then
  if [[ -n "$EXISTING_NOTE" ]]; then
    FINAL_NOTE="${EXISTING_NOTE}"$'\n'"[$NOW_TS] $NOTE_APPEND"
  else
    FINAL_NOTE="[$NOW_TS] $NOTE_APPEND"
  fi
else
  FINAL_NOTE="$EXISTING_NOTE"
fi

FIELD_TYPE="$(echo "$FIELDS_JSON" | jq -r --arg f "$EVAL_TIME_FIELD" '.data.items[] | select(.field_name == $f) | .type' | head -n 1 || true)"
HAS_WRITABLE_EVAL_FIELD="false"
if [[ -n "$FIELD_TYPE" ]]; then
  case "$FIELD_TYPE" in
    created_at|updated_at|created_by|modified_by|auto_number|formula|lookup)
      HAS_WRITABLE_EVAL_FIELD="false" ;;
    *)
      HAS_WRITABLE_EVAL_FIELD="true" ;;
  esac
fi

PAYLOAD="$(jq -nc \
  --arg status "$STATUS" \
  --arg final_note "$FINAL_NOTE" \
  --arg eval_field "$EVAL_TIME_FIELD" \
  --arg now_ts "$NOW_TS" \
  --argjson writable_eval "$HAS_WRITABLE_EVAL_FIELD" \
  ' {}
    | if $status != "" then .["选品状态"] = [$status] else . end
    | if $final_note != "" then .["备注"] = $final_note else . end
    | if $writable_eval then .[$eval_field] = $now_ts else . end
  ')"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "$PAYLOAD"
  exit 0
fi

lark-cli base +record-upsert \
  --base-token "$BASE_TOKEN" \
  --table-id "$TABLE_ID" \
  --record-id "$RECORD_ID" \
  --json "$PAYLOAD" >/dev/null

echo "record_id=$RECORD_ID"
echo "updated_at=$NOW_TS"
echo "writable_eval_field=$HAS_WRITABLE_EVAL_FIELD"
