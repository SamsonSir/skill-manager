#!/usr/bin/env bash
# install.sh — 一键安装 wx-cli（macOS arm64，从 GitHub Releases 下载预编译二进制）
#
# 用法：
#   bash scripts/install.sh
#
# 安装位置：~/.local/bin/wx-cli

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { printf "${CYAN}[wx-cli]${NC} %s\n" "$*"; }
ok()    { printf "${GREEN}[wx-cli]${NC} %s\n" "$*"; }
warn()  { printf "${YELLOW}[wx-cli]${NC} %s\n" "$*"; }
err()   { printf "${RED}[wx-cli]${NC} %s\n" "$*" >&2; }

# 1. 平台校验
ARCH="$(uname -m)"
OS="$(uname -s)"
if [[ "$OS" != "Darwin" ]]; then
  err "wx-cli 仅支持 macOS，当前系统：$OS"
  err "本 skill 在非 macOS 环境下只能作为知识参考使用。"
  exit 1
fi
if [[ "$ARCH" != "arm64" ]]; then
  err "wx-cli 仅支持 Apple Silicon (arm64)，当前架构：$ARCH"
  err "Intel Mac 不支持。"
  exit 1
fi

INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# 2. PATH 提示
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  warn "$INSTALL_DIR 不在 PATH 中"
  if [[ -n "${ZSH_VERSION:-}" ]]; then
    warn "执行：echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
  else
    warn "执行：echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
  fi
fi

# 3. 从 GitHub Releases 拉取最新 macOS arm64 二进制
info "从 GitHub Release 下载最新 macOS arm64 二进制"
URL="$(curl -fsSL https://api.github.com/repos/pandorafuture/wx-cli/releases/latest \
      | grep -o '"browser_download_url": "[^"]*macos-arm64[^"]*"' \
      | head -1 | cut -d'"' -f4 || true)"

if [[ -z "$URL" ]]; then
  err "未找到预编译资产。"
  info "备选方案：从源码编译 — git clone https://github.com/pandorafuture/wx-cli.git && cd wx-cli && cargo build --release"
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl -fSL "$URL" -o "$TMP/wx-cli.tar.gz"
tar xzf "$TMP/wx-cli.tar.gz" -C "$TMP"

# 兼容不同 archive 布局
if [[ -x "$TMP/wx-cli" ]]; then
  mv "$TMP/wx-cli" "$INSTALL_DIR/wx-cli"
elif [[ -x "$TMP/wx-cli/wx-cli" ]]; then
  mv "$TMP/wx-cli/wx-cli" "$INSTALL_DIR/wx-cli"
else
  FOUND="$(find "$TMP" -maxdepth 3 -type f -name wx-cli -perm -u+x 2>/dev/null | head -1 || true)"
  if [[ -n "$FOUND" ]]; then
    mv "$FOUND" "$INSTALL_DIR/wx-cli"
  else
    err "下载完成但未找到可执行文件 wx-cli"
    exit 1
  fi
fi
chmod +x "$INSTALL_DIR/wx-cli"

# 4. 验证
if "$INSTALL_DIR/wx-cli" --version >/dev/null 2>&1; then
  ok "安装成功：$("$INSTALL_DIR/wx-cli" --version 2>&1 | head -1)"
  info "下一步：bash scripts/doctor.sh 检查前置环境"
else
  err "安装完成但版本检查失败，请检查 $INSTALL_DIR/wx-cli 是否可执行"
  exit 1
fi