#!/usr/bin/env bash
# install.sh — One-liner installer for the AI Governance Framework
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/EduardPetraeus/ai-governance-framework/main/install.sh | bash
#
# What it does:
#   1. Checks prerequisites (git, node)
#   2. Clones the framework to a temp directory
#   3. Runs bin/ai-governance-init in the current directory
#   4. Cleans up the temp directory
#
# Works on macOS and Linux.
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
# Colour helpers
# ──────────────────────────────────────────────────────────────────────────────

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
BLUE="\033[34m"
DIM="\033[2m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}✓${RESET} $*"; }
info() { echo -e "${CYAN}→${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET} $*"; }
fail() { echo -e "${RED}✗${RESET} $*" >&2; exit 1; }
head() { echo -e "\n${BOLD}${BLUE}$*${RESET}"; }

# ──────────────────────────────────────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────────────────────────────────────

echo -e "
${BOLD}${BLUE}╔══════════════════════════════════════════════════════╗
║        AI Governance Framework — Installer           ║
╚══════════════════════════════════════════════════════╝${RESET}
"

# ──────────────────────────────────────────────────────────────────────────────
# Prerequisites
# ──────────────────────────────────────────────────────────────────────────────

head "Checking prerequisites"

command -v git >/dev/null 2>&1 || fail "git not found. Install git and retry."
ok "git $(git --version | awk '{print $3}')"

command -v node >/dev/null 2>&1 || fail "Node.js not found. Install Node.js 14+ from https://nodejs.org and retry."
NODE_VERSION=$(node --version)
ok "Node.js $NODE_VERSION"

# Verify we are inside a git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  fail "No git repository found in the current directory.
  Run: git init && git commit --allow-empty -m init
  Then re-run this installer."
fi
ok "Git repository detected"

# ──────────────────────────────────────────────────────────────────────────────
# Clone framework to temp dir
# ──────────────────────────────────────────────────────────────────────────────

REPO_URL="https://github.com/EduardPetraeus/ai-governance-framework.git"
TMPDIR_BASE="${TMPDIR:-/tmp}"
FRAMEWORK_TMP="$TMPDIR_BASE/ai-governance-framework-install-$$"

head "Downloading framework"
info "Cloning into temporary directory..."

cleanup() {
  if [ -d "$FRAMEWORK_TMP" ]; then
    rm -rf "$FRAMEWORK_TMP"
  fi
}
trap cleanup EXIT

git clone --depth 1 --quiet "$REPO_URL" "$FRAMEWORK_TMP" \
  || fail "Failed to clone repository. Check your internet connection and retry."

ok "Framework downloaded"

# ──────────────────────────────────────────────────────────────────────────────
# Run interactive wizard
# ──────────────────────────────────────────────────────────────────────────────

head "Starting setup wizard"
info "Running bin/ai-governance-init in: $(pwd)"
echo ""

node "$FRAMEWORK_TMP/bin/ai-governance-init" "$@"

# ──────────────────────────────────────────────────────────────────────────────
# Done — cleanup is handled by trap
# ──────────────────────────────────────────────────────────────────────────────
