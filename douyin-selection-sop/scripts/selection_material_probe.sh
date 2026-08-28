#!/usr/bin/env bash
set -euo pipefail

AGENTS_SKILL_ROOT="${AGENTS_SKILL_ROOT:-$HOME/.agents/skills}"
MATERIAL_PROBE_OCR_BIN="${DOUYIN_SELECTION_MATERIAL_OCR_BIN:-$AGENTS_SKILL_ROOT/video-auto-clip/tools/vision_ocr.swift}"

probe_classify_apparel_ocr_tsv() {
  local tsv_path="${1:-}"
  local goods_hits style_hits nonempty_frames total_chars

  if [[ -z "$tsv_path" || ! -s "$tsv_path" ]]; then
    printf 'editorial\n'
    return 0
  fi

  goods_hits="$(
    awk -F'\t' '
      BEGIN { count = 0 }
      tolower($0) ~ /(显瘦|速干|防晒|垂感|冰丝|凉感|透气|弹力|高腰|小个子|百搭|显高|阔腿|直筒|收腹|提臀|上身|对比|面料|遮胯|遮肉|防走光|梨形|胯宽|腿粗|腰粗|肚子|版型|松紧|弹性|穿法|两穿|腰线|通勤必备)/ { count++ }
      END { print count + 0 }
    ' "$tsv_path"
  )"
  style_hits="$(
    awk -F'\t' '
      BEGIN { count = 0 }
      tolower($0) ~ /(高级感|设计感|韩版|慵懒|气质|轻奢|法式|复古|洋气|氛围感|穿搭|ootd|look|搭配|套装|通勤穿搭|千金|时髦|ins)/ { count++ }
      END { print count + 0 }
    ' "$tsv_path"
  )"
  nonempty_frames="$(
    awk -F'\t' '
      NF > 1 && $2 !~ /^[[:space:]]*$/ { count++ }
      END { print count + 0 }
    ' "$tsv_path"
  )"
  total_chars="$(
    awk -F'\t' '
      NF > 1 { sum += length($2) }
      END { print sum + 0 }
    ' "$tsv_path"
  )"

  if (( goods_hits >= 2 )); then
    printf 'goods\n'
  elif (( style_hits >= 2 && goods_hits == 0 )); then
    printf 'editorial\n'
  elif (( goods_hits == 0 && nonempty_frames <= 1 )); then
    printf 'editorial\n'
  elif (( goods_hits == 0 && total_chars < 12 )); then
    printf 'editorial\n'
  else
    printf 'neutral\n'
  fi
}

probe_detect_transport_warning_tsv() {
  local tsv_path="${1:-}"
  local hit_count

  if [[ -z "$tsv_path" || ! -s "$tsv_path" ]]; then
    printf '0\n'
    return 0
  fi

  hit_count="$(
    awk -F'\t' '
      BEGIN { count = 0 }
      NR <= 5 {
        text = $2
        gsub(/[[:space:]]+/, "", text)
        if (index(text, "谨防搬运货不对版") > 0) {
          count++
        }
      }
      END { print count + 0 }
    ' "$tsv_path"
  )"

  if (( hit_count > 0 )); then
    printf '1\n'
  else
    printf '0\n'
  fi
}

probe_material_mix_risk() {
  local editorial_count="${1:-0}"
  local goods_count="${2:-0}"
  local neutral_count="${3:-0}"
  local checked_count="${4:-0}"
  local transport_warning_hits="${5:-0}"

  if (( transport_warning_hits >= 1 )); then
    printf '前3条素材命中“谨防搬运货不对版”字幕风险（命中%d条）\n' "$transport_warning_hits"
    return 0
  fi

  if (( checked_count == 3 && editorial_count >= 2 && editorial_count > goods_count )); then
    printf '画报型素材前3条占优（前3条: 画报%d / 货感%d / 中性%d）\n' "$editorial_count" "$goods_count" "$neutral_count"
    return 0
  fi

  if (( checked_count >= 3 && editorial_count >= 3 && goods_count <= 1 )); then
    printf '画报型素材占优（前%d条: 画报%d / 货感%d / 中性%d）\n' "$checked_count" "$editorial_count" "$goods_count" "$neutral_count"
    return 0
  fi

  if (( checked_count >= 4 && editorial_count > goods_count && editorial_count >= 3 )); then
    printf '画报型素材偏多（前%d条: 画报%d / 货感%d / 中性%d）\n' "$checked_count" "$editorial_count" "$goods_count" "$neutral_count"
  fi
}

probe_should_expand_material_sample() {
  local editorial_count="${1:-0}"
  local goods_count="${2:-0}"
  local neutral_count="${3:-0}"
  local checked_count="${4:-0}"

  neutral_count="$neutral_count"
  if (( checked_count < 3 )); then
    return 0
  fi
  if (( editorial_count >= 2 && editorial_count > goods_count )); then
    return 1
  fi
  if (( goods_count >= 2 && goods_count > editorial_count )); then
    return 1
  fi
  return 0
}

probe_video_material_style() {
  local video_path="${1:-}"
  local work_dir="${2:-}"
  local frames_dir ocr_tsv classification result_file transport_warning_hit

  frames_dir="$work_dir/frames"
  ocr_tsv="$work_dir/ocr.tsv"
  result_file="$work_dir/result.json"
  mkdir -p "$frames_dir"

  if [[ -s "$result_file" ]]; then
    cat "$result_file"
    return 0
  fi

  ffmpeg -nostdin -hide_banner -loglevel error \
    -ss 0 -t 8 -i "$video_path" \
    -vf fps=1 -q:v 3 \
    "$frames_dir/frame_%03d.jpg" -y >/dev/null 2>&1 || {
      jq -nc --arg classification "neutral" --arg video_path "$video_path" '{video_path:$video_path,classification:$classification}' | tee "$result_file"
      return 0
    }

  if compgen -G "$frames_dir/*.jpg" >/dev/null 2>&1; then
    "$MATERIAL_PROBE_OCR_BIN" --tsv "$frames_dir"/*.jpg > "$ocr_tsv" 2>/dev/null || true
  fi

  classification="$(probe_classify_apparel_ocr_tsv "$ocr_tsv")"
  transport_warning_hit="$(probe_detect_transport_warning_tsv "$ocr_tsv")"
  jq -nc \
    --arg video_path "$video_path" \
    --arg classification "$classification" \
    --argjson transport_warning_hit "$transport_warning_hit" \
    '{video_path:$video_path,classification:$classification,transport_warning_hit:$transport_warning_hit}' | tee "$result_file"
}

probe_collect_material_counts() {
  local videos_dir="${1:-}"
  local probe_dir="${2:-}"
  local limit="${3:-3}"
  local video_path result_json classification checked_count editorial_count goods_count neutral_count transport_warning_hits

  checked_count=0
  editorial_count=0
  goods_count=0
  neutral_count=0
  transport_warning_hits=0

  while IFS= read -r video_path; do
    [[ -z "$video_path" ]] && continue
    checked_count=$((checked_count + 1))
    result_json="$(probe_video_material_style "$video_path" "$probe_dir/$(basename "${video_path%.mp4}")")"
    classification="$(jq -r '.classification // "neutral"' <<<"$result_json")"
    case "$classification" in
      editorial) editorial_count=$((editorial_count + 1)) ;;
      goods) goods_count=$((goods_count + 1)) ;;
      *) neutral_count=$((neutral_count + 1)) ;;
    esac
    if (( checked_count <= 3 )) && [[ "$(jq -r '.transport_warning_hit // 0' <<<"$result_json")" == "1" ]]; then
      transport_warning_hits=$((transport_warning_hits + 1))
    fi
  done < <(find "$videos_dir" -maxdepth 1 -type f -name '*.mp4' | sort | sed -n "1,${limit}p")

  jq -nc \
    --argjson sample_videos_checked "$checked_count" \
    --argjson sample_editorial_count "$editorial_count" \
    --argjson sample_goods_count "$goods_count" \
    --argjson sample_neutral_count "$neutral_count" \
    --argjson sample_transport_warning_hits "$transport_warning_hits" \
    '{
      sample_videos_checked:$sample_videos_checked,
      sample_editorial_count:$sample_editorial_count,
      sample_goods_count:$sample_goods_count,
      sample_neutral_count:$sample_neutral_count,
      sample_transport_warning_hits:$sample_transport_warning_hits
    }'
}

ensure_probe_videos() {
  local name="${1:-}"
  local videos_dir="${2:-}"
  local probe_dir="${3:-}"
  local target_count="${4:-3}"
  local existing_count fetch_output log_file

  log_file="$probe_dir/fetch.log"
  mkdir -p "$videos_dir"
  existing_count="$(find "$videos_dir" -maxdepth 1 -type f -name '*.mp4' | wc -l | tr -d ' ')"
  if (( existing_count >= target_count )); then
    return 0
  fi

  if fetch_output="$(bash "$SCRIPT_DIR/fetch_short_videos.sh" \
    --cdp-port "$CDP_PORT" \
    --product-name "$name" \
    --output-dir "$videos_dir" \
    --download \
    --max-videos "$target_count" \
    --extract-mode auto 2>&1)"; then
    printf '%s\n' "$fetch_output" > "$log_file"
    return 0
  fi
  printf '%s\n' "$fetch_output" > "$log_file"
  return 1
}

probe_candidate_material_mix() {
  local candidate_json="${1:-}"
  local analysis_json="${2:-}"
  local name probe_root probe_slug probe_dir videos_dir summary_json
  local checked_count editorial_count goods_count neutral_count sample_risk transport_warning_hits

  if [[ "$(jq -r '.inferred_category // ""' <<<"$analysis_json")" != "服装" ]]; then
    printf '{}\n'
    return 0
  fi
  if [[ "$(jq -r '.status // ""' <<<"$analysis_json")" != "通过" ]]; then
    printf '{}\n'
    return 0
  fi

  name="$(jq -r '.name // ""' <<<"$candidate_json")"
  [[ -n "$name" ]] || {
    printf '{}\n'
    return 0
  }

  probe_root="$RUNTIME_DIR/material_probe"
  probe_slug="$(printf '%s' "$name" | tr ' /' '__' | cut -c1-80)"
  probe_dir="$probe_root/$probe_slug"
  videos_dir="$probe_dir/videos"

  mkdir -p "$videos_dir"
  if [[ ! -f "$probe_dir/summary.json" ]]; then
    if ! ensure_probe_videos "$name" "$videos_dir" "$probe_dir" 3; then
      printf '{}\n' > "$probe_dir/summary.json"
      printf '{}\n'
      return 0
    fi

    summary_json="$(probe_collect_material_counts "$videos_dir" "$probe_dir" 3)"
    checked_count="$(jq -r '.sample_videos_checked // 0' <<<"$summary_json")"
    editorial_count="$(jq -r '.sample_editorial_count // 0' <<<"$summary_json")"
    goods_count="$(jq -r '.sample_goods_count // 0' <<<"$summary_json")"
    neutral_count="$(jq -r '.sample_neutral_count // 0' <<<"$summary_json")"
    transport_warning_hits="$(jq -r '.sample_transport_warning_hits // 0' <<<"$summary_json")"

    if (( transport_warning_hits == 0 )) && probe_should_expand_material_sample "$editorial_count" "$goods_count" "$neutral_count" "$checked_count"; then
      if ensure_probe_videos "$name" "$videos_dir" "$probe_dir" 5; then
        summary_json="$(probe_collect_material_counts "$videos_dir" "$probe_dir" 5)"
        checked_count="$(jq -r '.sample_videos_checked // 0' <<<"$summary_json")"
        editorial_count="$(jq -r '.sample_editorial_count // 0' <<<"$summary_json")"
        goods_count="$(jq -r '.sample_goods_count // 0' <<<"$summary_json")"
        neutral_count="$(jq -r '.sample_neutral_count // 0' <<<"$summary_json")"
        transport_warning_hits="$(jq -r '.sample_transport_warning_hits // 0' <<<"$summary_json")"
      fi
    fi

    sample_risk="$(probe_material_mix_risk "$editorial_count" "$goods_count" "$neutral_count" "$checked_count" "$transport_warning_hits")"
    jq -nc \
      --arg sample_material_risk "$sample_risk" \
      --argjson sample_videos_checked "$checked_count" \
      --argjson sample_editorial_count "$editorial_count" \
      --argjson sample_goods_count "$goods_count" \
      --argjson sample_neutral_count "$neutral_count" \
      --argjson sample_transport_warning_hits "$transport_warning_hits" \
      '{
        sample_material_risk:$sample_material_risk,
        sample_videos_checked:$sample_videos_checked,
        sample_editorial_count:$sample_editorial_count,
        sample_goods_count:$sample_goods_count,
        sample_neutral_count:$sample_neutral_count,
        sample_transport_warning_hits:$sample_transport_warning_hits
      }' > "$probe_dir/summary.json"
  fi

  cat "$probe_dir/summary.json"
}
