#!/usr/bin/env bash
# pre_commit_guard.sh
#
# Claude Code hook: runs before each commit.
# Protects against committing directly to main and warns if CHANGELOG.md is stale.
#
# Installation:
#   1. Copy this file to .claude/hooks/pre_commit_guard.sh in your project
#   2. Make it executable: chmod +x .claude/hooks/pre_commit_guard.sh
#   3. Add to your CLAUDE.md hooks section:
#      hooks:
#        pre_commit: .claude/hooks/pre_commit_guard.sh
#
# Claude Code will run this script before every commit operation.
# Exit 1 to block the commit. Exit 0 to allow it.

set -euo pipefail

# ─── Color helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── Determine current branch ─────────────────────────────────────────────────
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# ─── Check 1: Block commits to protected branches ─────────────────────────────
PROTECTED_BRANCHES=("main" "master" "production" "release")

for branch in "${PROTECTED_BRANCHES[@]}"; do
    if [ "$CURRENT_BRANCH" = "$branch" ]; then
        echo ""
        echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║         WARNING: Direct commit to protected branch           ║${NC}"
        echo -e "${RED}╠══════════════════════════════════════════════════════════════╣${NC}"
        echo -e "${RED}║                                                              ║${NC}"
        echo -e "${RED}║  Branch: ${CURRENT_BRANCH}${NC}"
        echo -e "${RED}║                                                              ║${NC}"
        echo -e "${RED}║  You are committing directly to '${branch}'. This branch     ║${NC}"
        echo -e "${RED}║  is protected. All changes should go through a feature       ║${NC}"
        echo -e "${RED}║  branch and PR.                                              ║${NC}"
        echo -e "${RED}║                                                              ║${NC}"
        echo -e "${RED}║  Recommended workflow:                                       ║${NC}"
        echo -e "${RED}║    git checkout -b feature/your-feature-name                ║${NC}"
        echo -e "${RED}║    [make your changes]                                       ║${NC}"
        echo -e "${RED}║    git push -u origin feature/your-feature-name             ║${NC}"
        echo -e "${RED}║    [open a PR]                                               ║${NC}"
        echo -e "${RED}║                                                              ║${NC}"
        echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -ne "${YELLOW}Proceed with direct commit to ${branch}? [y/N]: ${NC}"

        # Read user response. In non-interactive environments (CI), default to N.
        if [ -t 0 ]; then
            read -r response
        else
            response="n"
            echo "n (non-interactive environment — blocking by default)"
        fi

        case "$response" in
            [yY][eE][sS]|[yY])
                echo -e "${YELLOW}Proceeding with commit to ${branch}. Consider creating a branch next time.${NC}"
                ;;
            *)
                echo -e "${RED}Commit blocked. Create a feature branch:${NC}"
                echo -e "  git checkout -b feature/$(git log -1 --format='%f' 2>/dev/null || echo 'your-feature')"
                echo ""
                exit 1
                ;;
        esac
        break
    fi
done

# ─── Check 2: Warn if CHANGELOG.md exists but is stale ───────────────────────
if [ -f "CHANGELOG.md" ]; then
    # Check if CHANGELOG.md has been staged in this commit
    CHANGELOG_STAGED=$(git diff --cached --name-only 2>/dev/null | grep "^CHANGELOG\.md$" || true)

    # Check if any source code files are staged
    SOURCE_STAGED=$(git diff --cached --name-only 2>/dev/null \
        | grep -E '\.(py|sql|ts|js|jsx|tsx|go|java|rb|rs|cs)$' || true)

    if [ -n "$SOURCE_STAGED" ] && [ -z "$CHANGELOG_STAGED" ]; then
        # Source code is being committed but CHANGELOG.md is not staged.
        # This is a warning, not a block — the CI/CD governance check will enforce it on PR.
        echo ""
        echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║           CHANGELOG.md not included in this commit           ║${NC}"
        echo -e "${YELLOW}╠══════════════════════════════════════════════════════════════╣${NC}"
        echo -e "${YELLOW}║                                                              ║${NC}"
        echo -e "${YELLOW}║  Source files are being committed but CHANGELOG.md was not  ║${NC}"
        echo -e "${YELLOW}║  updated.                                                    ║${NC}"
        echo -e "${YELLOW}║                                                              ║${NC}"
        echo -e "${YELLOW}║  Source files in this commit:                               ║${NC}"
        while IFS= read -r file; do
            echo -e "${YELLOW}║    • ${file}${NC}"
        done <<< "$SOURCE_STAGED"
        echo -e "${YELLOW}║                                                              ║${NC}"
        echo -e "${YELLOW}║  This is allowed now but will FAIL the PR governance check  ║${NC}"
        echo -e "${YELLOW}║  when you open a pull request.                              ║${NC}"
        echo -e "${YELLOW}║                                                              ║${NC}"
        echo -e "${YELLOW}║  Quick fix: Run /end-session in Claude Code to update       ║${NC}"
        echo -e "${YELLOW}║  CHANGELOG.md automatically before your PR.                 ║${NC}"
        echo -e "${YELLOW}║                                                              ║${NC}"
        echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        # Exit 0 — this is a warning only. The PR gate enforces the requirement.
    fi
fi

# ─── Check 3: Warn if CLAUDE.md is being committed to main without review ─────
CLAUDE_MD_STAGED=$(git diff --cached --name-only 2>/dev/null | grep "^CLAUDE\.md$" || true)
if [ -n "$CLAUDE_MD_STAGED" ] && [ "$CURRENT_BRANCH" = "main" ]; then
    echo ""
    echo -e "${YELLOW}Note: CLAUDE.md is being committed directly to main.${NC}"
    echo -e "${YELLOW}CLAUDE.md changes should normally go through a PR for team review.${NC}"
    echo ""
fi

# ─── All checks passed ────────────────────────────────────────────────────────
echo -e "${GREEN}Pre-commit guard: all checks passed (branch: ${CURRENT_BRANCH})${NC}"
exit 0
