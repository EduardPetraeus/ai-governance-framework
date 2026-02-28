#!/usr/bin/env bash
# post_commit.sh
#
# Claude Code hook: runs after each successful commit.
# Logs the commit to a session productivity tracker (.session_log).
# Provides a running count of session commits as immediate feedback.
#
# Installation:
#   1. Copy to .claude/hooks/post_commit.sh in your project
#   2. Make it executable: chmod +x .claude/hooks/post_commit.sh
#   3. Add to CLAUDE.md hooks section:
#      hooks:
#        post_commit: .claude/hooks/post_commit.sh
#
# The .session_log file is ephemeral — it is gitignored and resets when you
# clear it manually. It tracks the current working session only.

set -euo pipefail

# ─── Color helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'

# ─── Session log file ─────────────────────────────────────────────────────────
SESSION_LOG=".session_log"

# ─── Get commit information ───────────────────────────────────────────────────
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
COMMIT_MESSAGE=$(git log -1 --format="%s" 2>/dev/null || echo "")
COMMIT_TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# Count files changed in the commit
FILES_CHANGED=$(git diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')

# Estimate task complexity by word count of commit message
# Short messages (< 5 words) = simple edit
# Medium messages (5-10 words) = standard task
# Long messages (> 10 words) = complex task
WORD_COUNT=$(echo "$COMMIT_MESSAGE" | wc -w | tr -d ' ')
if [ "$WORD_COUNT" -lt 5 ]; then
    COMPLEXITY="simple"
elif [ "$WORD_COUNT" -lt 10 ]; then
    COMPLEXITY="standard"
else
    COMPLEXITY="complex"
fi

# ─── Create or append to session log ─────────────────────────────────────────
# Initialize the log file if it doesn't exist
if [ ! -f "$SESSION_LOG" ]; then
    cat > "$SESSION_LOG" << EOF
# Session Log
# Started: $(date "+%Y-%m-%d %H:%M:%S")
# Branch: ${CURRENT_BRANCH}
# Format: timestamp | hash | files_changed | complexity | message
EOF
fi

# Append this commit to the log
echo "${COMMIT_TIMESTAMP} | ${COMMIT_HASH} | files:${FILES_CHANGED} | ${COMPLEXITY} | ${COMMIT_MESSAGE}" \
    >> "$SESSION_LOG"

# ─── Count commits in this session ────────────────────────────────────────────
# Count lines that look like log entries (not comments)
SESSION_COMMIT_COUNT=$(grep -v "^#" "$SESSION_LOG" 2>/dev/null | grep -c "." || echo "0")

# ─── Print feedback ──────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}Commit logged: ${COMMIT_HASH}${NC}"
echo -e "${CYAN}  Session commits: ${SESSION_COMMIT_COUNT}${NC}"
echo -e "${GRAY}  Branch: ${CURRENT_BRANCH}${NC}"
echo -e "${GRAY}  Files changed: ${FILES_CHANGED} | Complexity: ${COMPLEXITY}${NC}"

# ─── Milestone notifications ──────────────────────────────────────────────────
if [ "$SESSION_COMMIT_COUNT" -eq 10 ]; then
    echo ""
    echo -e "${CYAN}Milestone: 10 commits this session.${NC}"
    echo -e "${GRAY}Consider running /status to review session progress.${NC}"
fi

if [ "$SESSION_COMMIT_COUNT" -eq 25 ]; then
    echo ""
    echo -e "${CYAN}Milestone: 25 commits this session. That is a productive session.${NC}"
    echo -e "${GRAY}When you are done, run /end-session to update CHANGELOG.md.${NC}"
fi

# ─── Remind about session end at larger commit counts ────────────────────────
if [ "$SESSION_COMMIT_COUNT" -gt 30 ] && [ $(( SESSION_COMMIT_COUNT % 10 )) -eq 0 ]; then
    echo ""
    echo -e "${GRAY}Long session detected (${SESSION_COMMIT_COUNT} commits).${NC}"
    echo -e "${GRAY}Remember to run /end-session before you finish to capture session state.${NC}"
fi

echo ""
exit 0
