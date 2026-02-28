# CI/CD Integration

This directory contains three CI/CD components that enforce governance automatically.
They run on GitHub Actions (on every PR and push) and locally (pre-commit hooks).

## Overview of the three components

| Component | File | Runs when | What it does |
|-----------|------|-----------|--------------|
| Governance check | `github-actions/governance-check.yml` | On PR (push) | Verifies CHANGELOG.md is updated when code changes |
| AI PR review | `github-actions/ai-pr-review.yml` | On PR (opened, updated) | Sends diff to Claude for convention review |
| Pre-commit | `pre-commit/.pre-commit-config.yaml` | On local commit | Scans for secrets, validates YAML/JSON, checks naming |

These three layers create a defense in depth:
- Pre-commit catches the obvious problems before they leave your machine
- Governance check enforces the process (CHANGELOG must be updated)
- AI PR review catches the subtle problems that static analysis misses

## Setup requirements

### For governance-check.yml and ai-pr-review.yml

1. Copy both files to `.github/workflows/` in your repository:
   ```bash
   mkdir -p .github/workflows
   cp ci-cd/github-actions/governance-check.yml .github/workflows/
   cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/
   ```

2. For `ai-pr-review.yml` only: add your Anthropic API key as a GitHub secret:
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `ANTHROPIC_API_KEY`
   - Value: your Anthropic API key (starts with `sk-ant-`)

3. No other secrets or configuration required for `governance-check.yml`.

### For pre-commit

1. Copy the config to your project root:
   ```bash
   cp ci-cd/pre-commit/.pre-commit-config.yaml .
   ```

2. Install pre-commit (if not already installed):
   ```bash
   pip install pre-commit
   # or: brew install pre-commit
   ```

3. Install the hooks:
   ```bash
   pre-commit install
   ```

4. Run against all files to check current state:
   ```bash
   pre-commit run --all-files
   ```

## What each component checks

### governance-check.yml

**Trigger:** Any PR where a `.py`, `.sql`, `.ts`, `.js`, `.go`, or `.java` file changed.

**Checks:**
- If any source code file changed, `CHANGELOG.md` must also have changed in the same PR.
- If `CLAUDE.md` changed, the PR requires a second reviewer (cannot self-approve).

**Why this matters:** The CHANGELOG requirement is the primary enforcement mechanism for
the session protocol. If CHANGELOG must be updated to merge, agents will update it. Without
this gate, the CHANGELOG drifts and agents lose their cross-session memory.

**To satisfy the check:** Run `/end-session` at the end of your session, or manually add
a CHANGELOG entry before submitting the PR.

### ai-pr-review.yml

**Trigger:** Every PR when opened or when new commits are pushed.

**What it does:**
1. Gets the PR diff
2. Reads `CLAUDE.md` from the repository
3. Sends both to the Claude API with a code review prompt
4. Posts the review as a PR comment
5. Fails the workflow if the verdict is FAIL

**Cost:** Each PR review costs approximately $0.01-$0.05 depending on diff size and model.
This is far less than the cost of a human reviewer catching a naming convention violation.

**Requirements:** `ANTHROPIC_API_KEY` secret must be set (see setup above).

### pre-commit/.pre-commit-config.yaml

**Trigger:** Every `git commit` on your local machine.

**Checks:**
- `gitleaks`: Detects secrets, API keys, and tokens in committed files
- `check-yaml`: Validates YAML syntax
- `check-json`: Validates JSON syntax
- `end-of-file-fixer`: Ensures files end with a newline
- `trailing-whitespace`: Removes trailing whitespace
- `detect-private-key`: Blocks commits containing private key material
- `check-snake-case` (custom): Validates that Python files in `src/` use snake_case naming

## How to add to an existing CI pipeline

If you already have CI/CD and want to add just the governance check:

Add this step to your existing workflow:
```yaml
- name: Check CHANGELOG updated
  run: |
    CODE_CHANGED=$(git diff --name-only origin/main...HEAD | grep -E '\.(py|sql|ts|js)$' || true)
    if [ -n "$CODE_CHANGED" ]; then
      CHANGELOG_CHANGED=$(git diff --name-only origin/main...HEAD | grep "CHANGELOG.md" || true)
      if [ -z "$CHANGELOG_CHANGED" ]; then
        echo "Governance check failed: code files changed but CHANGELOG.md was not updated."
        exit 1
      fi
    fi
```

## Disabling a check temporarily

If you need to merge urgently without a CHANGELOG update (hotfix scenario):
1. Add the label `skip-governance` to the PR — the governance check will pass
2. Create a follow-up PR or issue to add the CHANGELOG entry
3. Never make `skip-governance` a habit — it defeats the governance system

The label bypass is intentional: governance should be the default, not a barrier in emergencies.
