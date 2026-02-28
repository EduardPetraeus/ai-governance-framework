#!/usr/bin/env bash
# post_commit.sh — Post-commit productivity tracker
#
# Runs after each successful commit. Logs the commit to .session_log in the
# repo root and provides immediate feedback: session commit count, milestone
# notifications, and commit message quality scoring.
#
# Installation:
#   1. Copy to .claude/hooks/post_commit.sh (or your hooks directory)
#   2. chmod +x .claude/hooks/post_commit.sh
#   3. Reference in your CLAUDE.md hooks section or git post-commit hook
#
# The .session_log file is ephemeral — add it to .gitignore.

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SESSION_LOG="${REPO_ROOT}/.session_log"
TODAY="$(date +%Y-%m-%d)"

# ─── Color helpers (disabled if stdout is not a terminal) ────────────────────

if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    GRAY='\033[0;90m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' CYAN='' GRAY='' BOLD='' NC=''
fi

# ─── Gather commit information ───────────────────────────────────────────────
# Each git command has a fallback so the script never exits on failure.

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
COMMIT_MSG="$(git log -1 --format='%s' 2>/dev/null || echo "")"
TIMESTAMP="$(date '+%Y-%m-%dT%H:%M:%S')"

# Count files changed in this commit (compared to parent)
FILES_CHANGED="$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | wc -l | tr -d ' ')"

# ─── Append to session log ──────────────────────────────────────────────────
# Format: ISO-timestamp | branch | files-changed | first line of commit message
# The file is created on first use — no separate initialization needed.

if [ ! -f "${SESSION_LOG}" ]; then
    # First commit this session — create the log with a header comment
    echo "# .session_log — created ${TIMESTAMP}" > "${SESSION_LOG}"
fi

echo "${TIMESTAMP}|${BRANCH}|${FILES_CHANGED}|${COMMIT_MSG}" >> "${SESSION_LOG}"

# ─── Count today's commits ──────────────────────────────────────────────────
# Each data line starts with a timestamp. Filter to today's date to get the
# count for this session (assuming one session per day).

TODAYS_COMMITS="$(grep -c "^${TODAY}" "${SESSION_LOG}" 2>/dev/null || echo "0")"

# ─── Print session feedback ─────────────────────────────────────────────────

echo ""
echo -e "${GREEN}${BOLD}Commit ${TODAYS_COMMITS} this session${NC}"
echo -e "${GRAY}  Branch: ${BRANCH} | Files changed: ${FILES_CHANGED}${NC}"

# ─── Milestone notifications ────────────────────────────────────────────────
# Specific messages at 10, 25, and 50 commits. Each milestone escalates in
# urgency — long sessions accumulate rollback complexity.

case "${TODAYS_COMMITS}" in
    10)
        echo ""
        echo -e "${CYAN}10 commits — good session velocity. Run /status to verify scope.${NC}"
        ;;
    25)
        echo ""
        echo -e "${YELLOW}25 commits — substantial session. Consider /end-session soon.${NC}"
        ;;
    50)
        echo ""
        echo -e "${YELLOW}${BOLD}50 commits — long session. Rollback complexity increases. Run /end-session.${NC}"
        ;;
esac

# ─── Commit message quality score (0-3) ─────────────────────────────────────
#
# Three independent checks, each worth one point:
#   +1  Matches conventional commits format: type: description OR type(scope): description
#   +1  Type is a recognized conventional commit type
#   +1  Scope is present (parenthesized qualifier after the type)
#
# The regex is intentionally strict — it enforces the format the team agreed to.

QUALITY=0
MISSING=()

VALID_TYPES="feat|fix|docs|refactor|test|chore|perf|security"

# Check 1: Does it match the basic conventional commits pattern?
# Pattern: word followed by optional (scope), then colon, then space, then description
if echo "${COMMIT_MSG}" | grep -qE '^[a-z]+(\([^)]+\))?: .+'; then
    QUALITY=$((QUALITY + 1))
else
    MISSING+=("conventional format (type: description)")
fi

# Check 2: Is the type one of the recognized types?
EXTRACTED_TYPE="$(echo "${COMMIT_MSG}" | sed -nE 's/^([a-z]+)(\([^)]+\))?: .+/\1/p')"
if [ -n "${EXTRACTED_TYPE}" ] && echo "${EXTRACTED_TYPE}" | grep -qE "^(${VALID_TYPES})$"; then
    QUALITY=$((QUALITY + 1))
else
    MISSING+=("recognized type (${VALID_TYPES})")
fi

# Check 3: Is a scope present?
if echo "${COMMIT_MSG}" | grep -qE '^[a-z]+\([^)]+\): .+'; then
    QUALITY=$((QUALITY + 1))
else
    MISSING+=("scope (e.g., feat(auth): ...)")
fi

# Print the score
echo -e "${GRAY}  Message quality: ${QUALITY}/3${NC}"

if [ "${QUALITY}" -lt 3 ] && [ ${#MISSING[@]} -gt 0 ]; then
    for item in "${MISSING[@]}"; do
        echo -e "${GRAY}    - missing: ${item}${NC}"
    done
fi

echo ""
exit 0
