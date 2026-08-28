#!/usr/bin/env bash
set -euo pipefail

json_number_field() {
  local json_text="${1:-{}}"
  local field_name="${2:-}"
  local value
  value="$(jq -r --arg field_name "$field_name" '.[$field_name] // 0' <<<"${json_text:-{}}" 2>/dev/null || true)"
  if [[ ! "$value" =~ ^[0-9]+$ ]]; then
    value=0
  fi
  printf '%s\n' "$value"
}

normalize_gmv_yuan() {
  local raw="${1:-0}"
  if [[ ! "$raw" =~ ^[0-9]+$ ]]; then
    printf '0\n'
    return 0
  fi
  printf '%s\n' $((raw / 1000))
}

normalize_sales_count() {
  local raw="${1:-0}"
  if [[ ! "$raw" =~ ^[0-9]+$ ]]; then
    printf '0\n'
    return 0
  fi
  printf '%s\n' $((raw / 10))
}

normalize_clicks_count() {
  local raw="${1:-0}"
  if [[ ! "$raw" =~ ^[0-9]+$ ]]; then
    printf '0\n'
    return 0
  fi
  printf '%s\n' $((raw / 10))
}

midpoint_int() {
  local low="${1:-0}"
  local high="${2:-0}"
  if [[ ! "$low" =~ ^[0-9]+$ ]]; then low=0; fi
  if [[ ! "$high" =~ ^[0-9]+$ ]]; then high=0; fi
  if (( high <= 0 )); then
    printf '%s\n' "$low"
    return 0
  fi
  printf '%s\n' $(((low + high) / 2))
}

normalize_category_bucket() {
  local text="${1:-}"
  if [[ "$text" =~ 服|裙|裤|衫|T恤|西装|连衣裙|女装|男装|套装|外套|卫衣|针织|衬衫|背心|短袖|长袖 ]]; then
    printf '服装\n'
  elif [[ "$text" =~ 零食|食品|饮料|面包|饼干|坚果|茶|咖啡|火锅|糕点 ]]; then
    printf '食品\n'
  elif [[ "$text" =~ 美妆|口红|粉底|面膜|眼影|香水|精华|护肤|洗面奶|彩妆 ]]; then
    printf '美妆\n'
  elif [[ "$text" =~ 家居|收纳|厨房|清洁|锅|床|枕|家纺|毛巾|拖把|置物架 ]]; then
    printf '家居\n'
  elif [[ "$text" =~ 手机|耳机|电脑|键盘|鼠标|充电|数据线|数码|音箱|平板 ]]; then
    printf '数码\n'
  else
    printf '百货-非服装\n'
  fi
}

price_midpoint_from_bin() {
  local price_bin="${1:-}"
  local nums
  nums="$(printf '%s' "$price_bin" | perl -nE 'say join(" ", /([0-9]+(?:\.[0-9]+)?)/g)')"
  if [[ -z "$nums" ]]; then
    printf '0\n'
    return 0
  fi
  set -- $nums
  if [[ $# -eq 1 ]]; then
    printf '%s\n' "${1%.*}"
    return 0
  fi
  awk -v a="$1" -v b="$2" 'BEGIN { printf "%d\n", int((a+b)/2 + 0.5) }'
}

infer_heat_trend() {
  local newly_on_ranking="${1:-false}"
  if [[ "$newly_on_ranking" == "true" || "$newly_on_ranking" == "1" ]]; then
    printf '🔥上升\n'
  else
    printf '➡️平稳\n'
  fi
}

score_demand_strength() {
  local sales_mid="${1:-0}"
  if (( sales_mid >= 5000 )); then printf '5\n'
  elif (( sales_mid >= 2500 )); then printf '4\n'
  elif (( sales_mid >= 1000 )); then printf '3\n'
  elif (( sales_mid >= 500 )); then printf '2\n'
  elif (( sales_mid >= 200 )); then printf '1\n'
  else printf '0\n'; fi
}

score_click_strength() {
  local clicks_mid="${1:-0}"
  if (( clicks_mid >= 50000 )); then printf '5\n'
  elif (( clicks_mid >= 25000 )); then printf '4\n'
  elif (( clicks_mid >= 10000 )); then printf '3\n'
  elif (( clicks_mid >= 5000 )); then printf '2\n'
  elif (( clicks_mid >= 2000 )); then printf '1\n'
  else printf '0\n'; fi
}

score_content_density() {
  local video_low="${1:-0}"
  if (( video_low >= 500 && video_low <= 1500 )); then printf '5\n'
  elif (( video_low >= 250 )); then printf '4\n'
  elif (( video_low >= 100 )); then printf '3\n'
  elif (( video_low >= 40 )); then printf '2\n'
  elif (( video_low >= 20 )); then printf '1\n'
  else printf '0\n'; fi
}

score_rank_strength() {
  local rank="${1:-9999}"
  if (( rank <= 10 )); then printf '5\n'
  elif (( rank <= 30 )); then printf '4\n'
  elif (( rank <= 60 )); then printf '3\n'
  elif (( rank <= 100 )); then printf '2\n'
  elif (( rank <= 200 )); then printf '1\n'
  else printf '0\n'; fi
}

score_price_fit() {
  local category="${1:-百货-非服装}"
  local price_mid="${2:-0}"
  if (( price_mid <= 0 )); then
    printf '2\n'
    return 0
  fi

  if [[ "$category" == "服装" ]]; then
    if (( price_mid >= 49 && price_mid <= 159 )); then printf '5\n'
    elif (( price_mid >= 39 && price_mid <= 199 )); then printf '4\n'
    elif (( price_mid >= 29 && price_mid <= 259 )); then printf '3\n'
    elif (( price_mid >= 19 && price_mid <= 299 )); then printf '2\n'
    else printf '1\n'; fi
  else
    if (( price_mid >= 19 && price_mid <= 129 )); then printf '4\n'
    elif (( price_mid >= 9 && price_mid <= 199 )); then printf '3\n'
    else printf '2\n'; fi
  fi
}

score_executability() {
  local detail_url="${1:-}"
  local video_low="${2:-0}"
  local newly_on_ranking="${3:-false}"
  local score=0

  if [[ -n "$detail_url" ]]; then
    score=$((score + 2))
  fi
  if (( video_low >= 100 )); then
    score=$((score + 2))
  elif (( video_low >= 40 )); then
    score=$((score + 1))
  fi
  if [[ "$newly_on_ranking" == "true" || "$newly_on_ranking" == "1" ]]; then
    score=$((score + 1))
  fi

  if (( score > 5 )); then score=5; fi
  printf '%s\n' "$score"
}

detect_editorial_seed_risk() {
  local name="${1:-}"
  local category="${2:-百货-非服装}"
  local price_mid="${3:-0}"
  local video_low="${4:-0}"
  local style_hits=0
  local function_hits=0
  local suit_hits=0

  [[ "$category" == "服装" ]] || return 0

  [[ "$name" =~ 高级感|设计|设计感|韩版|慵懒|气质|轻奢|法式|复古|洋气|通勤|小众 ]] && style_hits=$((style_hits + 1))
  [[ "$name" =~ 冰丝|速干|显瘦|垂感|遮胯|凉感|防晒|透气|弹力|宽松|小个子|高腰|百搭|显高|显腿长|直筒|阔腿|收腹|提臀 ]] && function_hits=$((function_hits + 1))
  [[ "$name" =~ 西装|套装|小西服 ]] && suit_hits=$((suit_hits + 1))

  if (( suit_hits >= 1 )) && (( style_hits >= 1 )) && (( function_hits == 0 )) && (( price_mid >= 159 )); then
    printf '画报型种草素材风险高\n'
    return 0
  fi

  if (( style_hits > function_hits )) && (( price_mid >= 179 )) && (( video_low >= 150 )); then
    printf '画报型种草素材风险高\n'
  fi
}

competition_level_from_video_count() {
  local video_low="${1:-0}"
  if (( video_low >= 1200 )); then
    printf '高\n'
  elif (( video_low >= 500 )); then
    printf '中\n'
  else
    printf '低\n'
  fi
}

determine_risk_level() {
  local hard_filter="${1:-}"
  local detail_url="${2:-}"
  local video_low="${3:-0}"
  local price_mid="${4:-0}"
  local category="${5:-百货-非服装}"
  local competition_level="${6:-低}"
  local editorial_seed_risk="${7:-}"
  local sample_material_risk="${8:-}"

  if [[ -n "$hard_filter" ]]; then
    printf '高风险\n'
    return 0
  fi

  if [[ -n "$editorial_seed_risk" ]]; then
    printf '中风险\n'
    return 0
  fi

  if [[ -n "$sample_material_risk" ]]; then
    printf '中风险\n'
    return 0
  fi

  if [[ -z "$detail_url" || "$competition_level" == "高" ]]; then
    printf '中风险\n'
    return 0
  fi

  if [[ "$category" == "服装" && "$price_mid" -gt 199 ]]; then
    printf '中风险\n'
    return 0
  fi

  if (( video_low < 100 )); then
    printf '中风险\n'
    return 0
  fi

  printf '低风险\n'
}

recommend_test_angle() {
  local category="${1:-百货-非服装}"
  local price_mid="${2:-0}"
  local video_low="${3:-0}"
  local competition_level="${4:-低}"

  if [[ "$category" == "服装" ]]; then
    if (( video_low >= 500 )); then
      printf '上身对比 / 一整套通勤穿搭 / 显瘦前后对比\n'
    elif (( price_mid >= 100 )); then
      printf '面料质感 / 垂感细节 / 通勤场景展示\n'
    else
      printf '3秒上身 / 显瘦对比 / 日常百搭穿搭\n'
    fi
    return 0
  fi

  if [[ "$competition_level" == "高" ]]; then
    printf '差异化卖点 / 使用场景对比 / 痛点直给\n'
  else
    printf '核心卖点直给 / 使用前后对比 / 高频场景种草\n'
  fi
}

priority_from_score_and_risk() {
  local total_score="${1:-0}"
  local risk_level="${2:-低风险}"
  local hard_filter="${3:-}"
  local editorial_seed_risk="${4:-}"
  local sample_material_risk="${5:-}"

  if [[ -n "$hard_filter" ]]; then
    printf 'D档：淘汰\n'
    return 0
  fi

  if [[ -n "$editorial_seed_risk" ]]; then
    if (( total_score >= 18 )); then
      printf 'C档：观察\n'
    else
      printf 'D档：淘汰\n'
    fi
    return 0
  fi

  if [[ -n "$sample_material_risk" ]]; then
    if (( total_score >= 18 )); then
      printf 'C档：观察\n'
    else
      printf 'D档：淘汰\n'
    fi
    return 0
  fi

  if (( total_score >= 24 )) && [[ "$risk_level" == "低风险" ]]; then
    printf 'A档：立即测试\n'
  elif (( total_score >= 18 )) && [[ "$risk_level" != "高风险" ]]; then
    printf 'B档：可测试\n'
  elif (( total_score >= 12 )); then
    printf 'C档：观察\n'
  else
    printf 'D档：淘汰\n'
  fi
}

analyze_selection_candidate() {
  local candidate_json="$1"
  local category_hint="${2:-}"
  local sample_probe_json="${3:-}"
  local name rank detail_url video_low pay_amt_low pay_amt_high combo_low combo_high clicks_low clicks_high price_bin newly_on_ranking
  local inferred_category normalized_hint hard_filter_reason risk_level competition_level editorial_seed_risk sample_material_risk
  local gmv_low gmv_high sales_low sales_high sales_mid clicks_mid price_mid heat_trend
  local sample_videos_checked sample_editorial_count sample_goods_count sample_neutral_count
  local s1 s2 s3 s4 s5 s6 total_score priority test_angle evidence summary_reason

  name="$(jq -r '.name // ""' <<<"$candidate_json")"
  rank="$(jq -r '.rank // 9999' <<<"$candidate_json")"
  detail_url="$(jq -r '.detail_url // ""' <<<"$candidate_json")"
  video_low="$(jq -r '.video_low // 0' <<<"$candidate_json")"
  pay_amt_low="$(jq -r '.pay_amt_low // 0' <<<"$candidate_json")"
  pay_amt_high="$(jq -r '.pay_amt_high // 0' <<<"$candidate_json")"
  combo_low="$(jq -r '.combo_low // 0' <<<"$candidate_json")"
  combo_high="$(jq -r '.combo_high // 0' <<<"$candidate_json")"
  clicks_low="$(jq -r '.clicks_low // 0' <<<"$candidate_json")"
  clicks_high="$(jq -r '.clicks_high // 0' <<<"$candidate_json")"
  price_bin="$(jq -r '.price_bin // ""' <<<"$candidate_json")"
  newly_on_ranking="$(jq -r '.newly_on_ranking // false' <<<"$candidate_json")"

  inferred_category="$(normalize_category_bucket "$name")"
  normalized_hint="$(normalize_category_bucket "$category_hint")"
  gmv_low="$(normalize_gmv_yuan "$pay_amt_low")"
  gmv_high="$(normalize_gmv_yuan "$pay_amt_high")"
  sales_low="$(normalize_sales_count "$combo_low")"
  sales_high="$(normalize_sales_count "$combo_high")"
  sales_mid="$(midpoint_int "$sales_low" "$sales_high")"
  clicks_mid="$(midpoint_int "$(normalize_clicks_count "$clicks_low")" "$(normalize_clicks_count "$clicks_high")")"
  price_mid="$(price_midpoint_from_bin "$price_bin")"
  heat_trend="$(infer_heat_trend "$newly_on_ranking")"
  sample_material_risk="$(jq -r '.sample_material_risk // ""' <<<"${sample_probe_json:-{}}" 2>/dev/null || true)"
  sample_videos_checked="$(json_number_field "${sample_probe_json:-{}}" "sample_videos_checked")"
  sample_editorial_count="$(json_number_field "${sample_probe_json:-{}}" "sample_editorial_count")"
  sample_goods_count="$(json_number_field "${sample_probe_json:-{}}" "sample_goods_count")"
  sample_neutral_count="$(json_number_field "${sample_probe_json:-{}}" "sample_neutral_count")"

  hard_filter_reason=""
  if [[ -n "$category_hint" && "$normalized_hint" != "$inferred_category" ]]; then
    hard_filter_reason="类目不符"
  elif (( video_low < 40 )); then
    hard_filter_reason="素材不足"
  elif [[ "$inferred_category" == "服装" && "$price_mid" -gt 299 ]]; then
    hard_filter_reason="客单不符"
  elif (( rank > 300 && sales_mid < 500 )); then
    hard_filter_reason="其他"
  fi

  s1="$(score_demand_strength "$sales_mid")"
  s2="$(score_click_strength "$clicks_mid")"
  s3="$(score_content_density "$video_low")"
  s4="$(score_rank_strength "$rank")"
  s5="$(score_price_fit "$inferred_category" "$price_mid")"
  s6="$(score_executability "$detail_url" "$video_low" "$newly_on_ranking")"
  total_score=$((s1 + s2 + s3 + s4 + s5 + s6))

  competition_level="$(competition_level_from_video_count "$video_low")"
  editorial_seed_risk="$(detect_editorial_seed_risk "$name" "$inferred_category" "$price_mid" "$video_low")"
  risk_level="$(determine_risk_level "$hard_filter_reason" "$detail_url" "$video_low" "$price_mid" "$inferred_category" "$competition_level" "$editorial_seed_risk" "$sample_material_risk")"
  priority="$(priority_from_score_and_risk "$total_score" "$risk_level" "$hard_filter_reason" "$editorial_seed_risk" "$sample_material_risk")"
  test_angle="$(recommend_test_angle "$inferred_category" "$price_mid" "$video_low" "$competition_level")"

  if [[ -n "$hard_filter_reason" ]]; then
    summary_reason="硬过滤命中：$hard_filter_reason"
  elif [[ -n "$sample_material_risk" ]]; then
    summary_reason="素材抽样风险：${sample_material_risk}，偏穿搭画报/种草，不建议直接作为爆品测试池"
  elif [[ -n "$editorial_seed_risk" ]]; then
    summary_reason="素材打法风险：${editorial_seed_risk}，偏穿搭画报/种草，不建议直接作为爆品测试池"
  else
    summary_reason="可进入测试池，优先级$priority"
  fi

  evidence="证据: 排名#${rank} | 7天营业额约${gmv_low}-${gmv_high}元 | 7天销量约${sales_low}-${sales_high}单 | 点击约$(normalize_clicks_count "$clicks_low")-$(normalize_clicks_count "$clicks_high") | 素材量${video_low}+ | 售价带${price_bin:-未知} | 竞争度${competition_level}"
  if [[ -n "$sample_material_risk" ]]; then
    evidence="${evidence} | 素材抽样:${sample_editorial_count}/${sample_videos_checked}画报, ${sample_goods_count}/${sample_videos_checked}货感"
  fi
  if [[ -n "$editorial_seed_risk" ]]; then
    evidence="${evidence} | 素材打法风险:${editorial_seed_risk}"
  fi

  jq -nc \
    --arg inferred_category "$inferred_category" \
    --arg heat_trend "$heat_trend" \
    --arg price_bin "$price_bin" \
    --arg risk_level "$risk_level" \
    --arg priority "$priority" \
    --arg test_angle "$test_angle" \
    --arg hard_filter_reason "$hard_filter_reason" \
    --arg editorial_seed_risk "$editorial_seed_risk" \
    --arg sample_material_risk "$sample_material_risk" \
    --arg evidence "$evidence" \
    --arg summary_reason "$summary_reason" \
    --arg competition_level "$competition_level" \
    --arg status "$(if [[ "$priority" == A档* || "$priority" == B档* ]]; then printf '通过'; else printf '观察'; fi)" \
    --argjson gmv_low "$gmv_low" \
    --argjson gmv_high "$gmv_high" \
    --argjson sales_low "$sales_low" \
    --argjson sales_high "$sales_high" \
    --argjson sales_mid "$sales_mid" \
    --argjson clicks_mid "$clicks_mid" \
    --argjson price_mid "$price_mid" \
    --argjson total_score "$total_score" \
    --argjson sample_videos_checked "$sample_videos_checked" \
    --argjson sample_editorial_count "$sample_editorial_count" \
    --argjson sample_goods_count "$sample_goods_count" \
    --argjson sample_neutral_count "$sample_neutral_count" \
    --argjson demand_strength "$s1" \
    --argjson click_strength "$s2" \
    --argjson content_density "$s3" \
    --argjson rank_strength "$s4" \
    --argjson price_fit "$s5" \
    --argjson executability "$s6" \
    '{
      inferred_category:$inferred_category,
      heat_trend:$heat_trend,
      price_bin:$price_bin,
      price_mid:$price_mid,
      gmv_low:$gmv_low,
      gmv_high:$gmv_high,
      sales_low:$sales_low,
      sales_high:$sales_high,
      sales_mid:$sales_mid,
      clicks_mid:$clicks_mid,
      demand_strength:$demand_strength,
      click_strength:$click_strength,
      content_density:$content_density,
      rank_strength:$rank_strength,
      price_fit:$price_fit,
      executability:$executability,
      total_score:$total_score,
      risk_level:$risk_level,
      priority:$priority,
      competition_level:$competition_level,
      test_angle:$test_angle,
      hard_filter_reason:$hard_filter_reason,
      editorial_seed_risk:$editorial_seed_risk,
      sample_material_risk:$sample_material_risk,
      sample_videos_checked:$sample_videos_checked,
      sample_editorial_count:$sample_editorial_count,
      sample_goods_count:$sample_goods_count,
      sample_neutral_count:$sample_neutral_count,
      evidence:$evidence,
      summary_reason:$summary_reason,
      status:$status
    }'
}
