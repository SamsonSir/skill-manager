#!/usr/bin/env bash
# doctor.sh — wx-cli 前置环境检查
#
# 检查项：
  - 平台与架构（macOS arm64）
  - SIP 状态（密钥提取需要 Disabled）
  - DevToolsSecurity（LLDB hook 需要）
  - _developer 用户组（LLDB 调试需要）
  - xcode-select / lldb / python3
  - ffmpeg（语音转码可选）
  - wx-cli 是否在 PATH 中

set -uo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
PASS=0; FAIL=0; WARN=0

pass() { printf "${GREEN}✓${NC} %s\n" "$*"; PASS=$((PASS+1)); }
fail() { printf "${RED}✗${NC} %s\n" "$*"; FAIL=$((FAIL+1)); }
warn() { printf "${YELLOW}!${NC} %s\n" "$*"; WARN=$((WARN+1)); }
info() { printf "${CYAN}i${NC} %s\n" "$*"; }

echo "═══════════════════════════════════════════════"
echo "  wx-cli 环境检查"
echo "═══════════════════════════════════════════════"

# 1. 平台
OS="$(uname -s)"
ARCH="$(uname -m)"
if [[ "$OS" == "Darwin" && "$ARCH" == "arm64" ]]; then
  pass "平台：macOS arm64"
else
  fail "平台：$OS $ARCH（需要 macOS arm64）"
  info "wx-cli 不支持当前平台，仅作为知识参考。"
fi

# 2. SIP
SIP_STATUS="$(csrutil status 2>/dev/null | awk -F': ' '/System Integrity Protection status:/ {print $2}' || echo unknown)"
if [[ "$SIP_STATUS" == "disabled" ]]; then
  pass "SIP：disabled（可提取密钥）"
elif [[ "$SIP_STATUS" == "enabled" ]]; then
  fail "SIP：enabled（密钥提取会被 task_for_pid 拒绝）"
  info "修复：重启 → Recovery Mode → 终端执行 csrutil disable"
else
  warn "SIP：状态未知（$SIP_STATUS）"
fi

# 3. DevToolsSecurity
if sudo -n DevToolsSecurity -query 2>/dev/null | grep -q "enabled"; then
  pass "DevToolsSecurity：enabled"
else
  fail "DevToolsSecurity：未启用"
  info "修复：sudo DevToolsSecurity -enable"
fi

# 4. _developer 用户组
if groups "$USER" 2>/dev/null | grep -q "_developer"; then
  pass "_developer 用户组成员"
else
  fail "_developer 用户组未包含当前用户"
  info "修复：sudo dscl . append /Groups/_developer GroupMembership $USER"
fi

# 5. xcode-select / lldb
if command -v xcode-select >/dev/null 2>&1; then
  XPATH="$(xcode-select -p 2>/dev/null || echo none)"
  if [[ "$XPATH" != "none" ]]; then
    pass "xcode-select：$XPATH"
  else
    fail "xcode-select：未配置"
    info "修复：xcode-select --install"
  fi
else
  fail "xcode-select：未安装"
  info "修复：xcode-select --install"
fi

if command -v lldb >/dev/null 2>&1; then
  pass "lldb：$(command -v lldb)"
else
  fail "lldb：未找到"
  info "修复：xcode-select --install 或 brew install --cask llvm"
fi

# 6. python3
if command -v python3 >/dev/null 2>&1; then
  PYV="$(python3 --version 2>&1)"
  pass "python3：$PYV"
else
  fail "python3：未找到"
  info "修复：brew install python 或安装 CommandLineTools（xcode-select --install）"
fi

# 7. ffmpeg（可选）
if command -v ffmpeg >/dev/null 2>&1; then
  pass "ffmpeg：$(ffmpeg -version 2>&1 | head -1)"
else
  warn "ffmpeg：未安装（语音转 MP3 需要）"
  info "可选：brew install ffmpeg，或用 --raw 输出 SILK 格式绕过"
fi

# 8. wx-cli 二进制
if command -v wx-cli >/dev/null 2>&1; then
  WXV="$(wx-cli --version 2>&1 | head -1)"
  pass "wx-cli：$WXV（位于 $(command -v wx-cli)）"
else
  warn "wx-cli：不在 PATH 中"
  info "修复：bash scripts/install.sh"
fi

echo "═══════════════════════════════════════════════"
printf "结果：${GREEN}%d pass${NC} / ${YELLOW}%d warn${NC} / ${RED}%d fail${NC}\n" "$PASS" "$WARN" "$FAIL"
echo "═══════════════════════════════════════════════"

# fail > 0 时退出码非零
[[ $FAIL -eq 0 ]]