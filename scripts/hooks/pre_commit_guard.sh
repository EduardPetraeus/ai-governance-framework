#!/usr/bin/env bash
#
# pre_commit_guard.sh — Claude Code pre-commit hook
#
# Protects against:
#   1. Direct commits to protected branches (main, master, production)
#   2. Source code commits without CHANGELOG.md updates
#   3. Non-conventional commit message format
#
# Installation:
#   cp scripts/hooks/pre_commit_guard.sh .claude/hooks/
#   chmod +x .claude/hooks/pre_commit_guard.sh
#
#   Add to CLAUDE.md:
#     hooks:
#       pre_commit: .claude/hooks/pre_commit_guard.sh
#
# Exit codes:
#   0 — commit allowed
#   1 — commit blocked (user declined to proceed)

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
GRAY='\033[0;90m'
NC='\033[0m'

# ── Current branch ──────────────────────────────────────────────────────

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# ── Check 1: Protected branch guard ────────────────────────────────────
#
# Warns and prompts if committing directly to main/master/production.
# Blocks by default (requires explicit "y" to proceed).
# In non-interactive environments (CI, piped input), blocks automatically.

PROTECTED_BRANCHES=("main" "master" "production")

for branch in "${PROTECTED_BRANCHES[@]}"; do
    if [ "$CURRENT_BRANCH" = "$branch" ]; then
        echo ""
        echo -e "${RED}======================================================${NC}"
        echo -e "${RED}  WARNING: Direct commit to ${branch}${NC}"
        echo -e "${RED}======================================================${NC}"
        echo ""
        echo -e "  This bypasses PR review. All changes should go"
        echo -e "  through a feature branch and pull request."
        echo ""
        echo -e "  ${GRAY}Recommended:${NC}"
        echo -e "    git checkout -b feature/your-change"
        echo -e "    git push -u origin feature/your-change"
        echo ""

        # Prompt for confirmation (default: No)
        if [ -t 0 ]; then
            echo -ne "${YELLOW}  Proceed with direct commit to ${branch}? [y/N]: ${NC}"
            read -r response
        else
            # Non-interactive: block by default
            response="n"
            echo -e "  ${GRAY}Non-interactive environment — blocking by default.${NC}"
        fi

        case "$response" in
            [yY][eE][sS]|[yY])
                echo -e "${YELLOW}  Proceeding. Create a branch next time.${NC}"
                echo ""
                ;;
            *)
                echo -e "${RED}  Commit blocked.${NC}"
                echo -e "  ${GRAY}Run: git checkout -b feature/your-change${NC}"
                echo ""
                exit 1
                ;;
        esac
        break
    fi
done

# ── Check 2: CHANGELOG.md staleness warning ────────────────────────────
#
# If CHANGELOG.md exists and source code files are staged but CHANGELOG.md
# is not staged, warn the user. This is a WARNING, not a block — the CI
# governance check enforces the hard requirement on PR.

if [ -f "CHANGELOG.md" ]; then
    # Check for staged source code files
    SOURCE_STAGED=$(git diff --cached --name-only 2>/dev/null \
        | grep -E '\.(py|sql|ts|js|jsx|tsx|go|java|rb|rs|cs|swift|kt)$' || true)

    # Check if CHANGELOG.md is also staged
    CHANGELOG_STAGED=$(git diff --cached --name-only 2>/dev/null \
        | grep '^CHANGELOG\.md$' || true)

    if [ -n "$SOURCE_STAGED" ] && [ -z "$CHANGELOG_STAGED" ]; then
        echo ""
        echo -e "${YELLOW}======================================================${NC}"
        echo -e "${YELLOW}  CHANGELOG.md not included in this commit${NC}"
        echo -e "${YELLOW}======================================================${NC}"
        echo ""
        echo -e "  Source files staged:"
        while IFS= read -r file; do
            echo -e "    ${GRAY}${file}${NC}"
        done <<< "$SOURCE_STAGED"
        echo ""
        echo -e "  ${GRAY}This is allowed locally, but the PR governance${NC}"
        echo -e "  ${GRAY}check will require CHANGELOG.md to be updated.${NC}"
        echo -e "  ${GRAY}Run /end-session before your PR to update it.${NC}"
        echo ""
        # Do not exit — this is a warning only
    fi
fi

# ── Check 3: Conventional commits format check ─────────────────────────
#
# Validates that the commit message follows conventional commits format:
#   type(scope): description
#   type: description
#
# Valid types: feat, fix, docs, refactor, test, chore, perf, style, ci, build, revert
#
# This is a WARNING on any branch. On protected branches, it is stronger
# because the earlier check already warned about the branch itself.

# Get the commit message from the commit message file
# In a pre-commit hook context, the message file is .git/COMMIT_EDITMSG
COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"

if [ -f "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG=$(head -1 "$COMMIT_MSG_FILE" 2>/dev/null || echo "")

    if [ -n "$COMMIT_MSG" ]; then
        # Conventional commits pattern: type(optional-scope): description
        CONVENTIONAL_PATTERN='^(feat|fix|docs|refactor|test|chore|perf|style|ci|build|revert)(\([a-zA-Z0-9_-]+\))?: .{3,}'

        if ! echo "$COMMIT_MSG" | grep -qE "$CONVENTIONAL_PATTERN"; then
            echo ""
            echo -e "${YELLOW}  Commit message does not follow conventional format${NC}"
            echo -e "  ${GRAY}Message: \"${COMMIT_MSG}\"${NC}"
            echo -e "  ${GRAY}Expected: type(scope): description${NC}"
            echo -e "  ${GRAY}Types: feat, fix, docs, refactor, test, chore, perf${NC}"
            echo -e "  ${GRAY}Example: feat(api): add user profile endpoint${NC}"
            echo ""

            # Score the message
            SCORE=0
            SCORE_DETAILS=""

            # Check for type prefix
            if echo "$COMMIT_MSG" | grep -qE '^(feat|fix|docs|refactor|test|chore|perf|style|ci|build|revert)'; then
                SCORE=$((SCORE + 1))
            else
                SCORE_DETAILS="${SCORE_DETAILS}missing type prefix, "
            fi

            # Check for scope
            if echo "$COMMIT_MSG" | grep -qE '^\w+\([a-zA-Z0-9_-]+\)'; then
                SCORE=$((SCORE + 1))
            else
                SCORE_DETAILS="${SCORE_DETAILS}missing scope, "
            fi

            # Check for colon-space separator
            if echo "$COMMIT_MSG" | grep -qE ': .{3,}'; then
                SCORE=$((SCORE + 1))
            else
                SCORE_DETAILS="${SCORE_DETAILS}missing 'type: description' format"
            fi

            # Remove trailing comma-space
            SCORE_DETAILS=$(echo "$SCORE_DETAILS" | sed 's/, $//')

            echo -e "  ${GRAY}Message quality: ${SCORE}/3${NC}"
            if [ -n "$SCORE_DETAILS" ]; then
                echo -e "  ${GRAY}Issues: ${SCORE_DETAILS}${NC}"
            fi
            echo ""
            # Do not block — this is a warning
        fi
    fi
fi

# ── Check 4: CLAUDE.md direct-to-main warning ──────────────────────────
#
# CLAUDE.md changes should go through PR review. Warn if committing
# directly to a protected branch.

CLAUDE_MD_STAGED=$(git diff --cached --name-only 2>/dev/null | grep '^CLAUDE\.md$' || true)

if [ -n "$CLAUDE_MD_STAGED" ]; then
    for branch in "${PROTECTED_BRANCHES[@]}"; do
        if [ "$CURRENT_BRANCH" = "$branch" ]; then
            echo -e "${YELLOW}  Note: CLAUDE.md is being committed to ${branch}.${NC}"
            echo -e "${GRAY}  CLAUDE.md changes affect all agent sessions and${NC}"
            echo -e "${GRAY}  should normally go through a reviewed PR.${NC}"
            echo ""
            break
        fi
    done
fi

# ── All checks complete ────────────────────────────────────────────────

echo -e "${GREEN}  Pre-commit: passed (branch: ${CURRENT_BRANCH})${NC}"
exit 0
