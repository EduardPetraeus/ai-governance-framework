#!/usr/bin/env bash
# deploy_commands.sh — Copy slash commands into a target project's .claude/commands/
#
# Usage:
#   scripts/deploy_commands.sh [target-directory]
#
# If no target directory is given, the current directory is used.
#
# What it does:
#   1. Validates the target is a git repository with a CLAUDE.md
#   2. Creates .claude/commands/ in the target
#   3. Copies all *.md files from commands/ (excluding README.md)
#   4. Reports which files were copied or skipped
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
# Colour helpers
# ──────────────────────────────────────────────────────────────────────────────

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}✓${RESET} $*"; }
info() { echo -e "${CYAN}→${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET} $*"; }
fail() { echo -e "${RED}✗${RESET} $*" >&2; exit 1; }

# ──────────────────────────────────────────────────────────────────────────────
# Resolve paths
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMMANDS_SRC="$FRAMEWORK_ROOT/commands"

TARGET_DIR="${1:-$(pwd)}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
COMMANDS_DEST="$TARGET_DIR/.claude/commands"

# ──────────────────────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────────────────────

info "Target directory: $TARGET_DIR"

# Must be a git repository
if ! git -C "$TARGET_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  fail "Target is not a git repository: $TARGET_DIR"
fi
ok "Git repository confirmed"

# Must have CLAUDE.md (governance file signals intentional adoption)
if [ ! -f "$TARGET_DIR/CLAUDE.md" ]; then
  fail "No CLAUDE.md found in target directory.
  Run 'npx ai-governance-init' or copy templates/CLAUDE.md first."
fi
ok "CLAUDE.md found"

# Commands source must exist
if [ ! -d "$COMMANDS_SRC" ]; then
  fail "commands/ directory not found in framework: $COMMANDS_SRC"
fi

# ──────────────────────────────────────────────────────────────────────────────
# Deploy
# ──────────────────────────────────────────────────────────────────────────────

mkdir -p "$COMMANDS_DEST"
info "Deploying commands to: $COMMANDS_DEST"

COPIED=0
SKIPPED=0

for src_file in "$COMMANDS_SRC"/*.md; do
  filename="$(basename "$src_file")"

  # Skip the README — it is framework documentation, not a slash command
  if [ "$filename" = "README.md" ]; then
    continue
  fi

  dest_file="$COMMANDS_DEST/$filename"

  if [ -f "$dest_file" ]; then
    warn "Skipped (exists): .claude/commands/$filename"
    SKIPPED=$((SKIPPED + 1))
  else
    cp "$src_file" "$dest_file"
    ok "Copied: .claude/commands/$filename"
    COPIED=$((COPIED + 1))
  fi
done

# ──────────────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Commands deployed: $COPIED  |  Skipped (already exist): $SKIPPED${RESET}"

if [ "$COPIED" -gt 0 ]; then
  echo ""
  info "Slash commands are now available in Claude Code:"
  info "  /plan-session, /end-session, /status, /security-review, ..."
  info "Restart Claude Code to pick up new commands."
fi
