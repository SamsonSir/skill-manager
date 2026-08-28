#!/usr/bin/env bash
set -euo pipefail

derive_run_outcome() {
  local downloaded="$1"
  local clipped="$2"
  local failures="$3"

  if (( failures > 0 )) && (( downloaded == 0 )) && (( clipped == 0 )); then
    printf '%s\n' "failed"
    return 0
  fi

  if (( failures > 0 )); then
    printf '%s\n' "partial"
    return 0
  fi

  printf '%s\n' "success"
}

build_notify_message() {
  local shop_name="$1"
  local outcome="$2"
  local selected_count="$3"
  local downloaded_products="$4"
  local clipped_videos="$5"
  local failures="$6"
  local output_root="$7"
  local prefix

  case "$outcome" in
    success) prefix="${shop_name}选品到剪辑已完成" ;;
    partial) prefix="${shop_name}选品到剪辑部分完成" ;;
    failed) prefix="${shop_name}选品到剪辑失败/中断" ;;
    interrupted) prefix="${shop_name}选品到剪辑失败/中断" ;;
    *)
      echo "未知结果状态: $outcome" >&2
      return 1
      ;;
  esac

  printf '%s：候选%s个，下载成功%s个商品，剪辑成功%s条视频，失败记录%s项，目录：%s\n' \
    "$prefix" "$selected_count" "$downloaded_products" "$clipped_videos" "$failures" "$output_root"
}

archive_previous_failed_runs() {
  local runs_dir="$1"
  local shop_slug="$2"
  local current_output_root="$3"
  local archive_dir candidate checkpoint_json run_state_json stage clipped failures target

  archive_dir="$current_output_root/失败_中断"
  mkdir -p "$archive_dir"

  while IFS= read -r candidate; do
    [[ -z "$candidate" || "$candidate" == "$current_output_root" ]] && continue

    checkpoint_json="$candidate/.runtime/checkpoint.json"
    run_state_json="$candidate/.runtime/run_state.json"
    [[ -f "$checkpoint_json" && -f "$run_state_json" ]] || continue

    stage="$(jq -r '.stage // empty' "$checkpoint_json" 2>/dev/null || true)"
    [[ "$stage" == "completed" || "$stage" == "success" || "$stage" == "partial" || "$stage" == "failed" || "$stage" == "interrupted" ]] || continue

    clipped="$(jq -r '.clipped_videos // 0' "$run_state_json" 2>/dev/null || true)"
    failures="$(jq -r '.terminal_failures // 0' "$run_state_json" 2>/dev/null || true)"
    [[ "$clipped" =~ ^[0-9]+$ && "$failures" =~ ^[0-9]+$ ]] || continue

    if (( failures > 0 )) && (( clipped == 0 )); then
      target="$archive_dir/$(basename "$candidate")"
      [[ -e "$target" ]] && continue
      mv "$candidate" "$target"
    fi
  done < <(find "$runs_dir" -mindepth 1 -maxdepth 1 -type d -name "*_${shop_slug}" | sort)

  if [[ -z "$(find "$archive_dir" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
    rmdir "$archive_dir" 2>/dev/null || true
  fi
}
