# CI/CD Integration

Four automated enforcement layers that catch governance violations, security issues, and convention problems before they reach production. Each layer catches different things at different stages of the development workflow.

> **Two locations, one purpose.** The `ci-cd/` directory contains the reusable workflow templates — copy these into your own project. The `.github/workflows/` directory at the root of this repository contains the live copies that actually run on this repo. If you modify a workflow, update both.



## The four workflows

| Workflow | File | Trigger | What it blocks | What it catches that humans miss |
|----------|------|---------|----------------|--------------------------------|
| **Governance check** | `governance-check.yml` | PR push | Merge | CHANGELOG.md not updated when code changes. CLAUDE.md changes without second reviewer. |
| **AI PR review** | `ai-pr-review.yml` | PR opened/updated | Merge (on FAIL) | Naming violations, missing tests, ADR contradictions, scope creep, pattern inconsistencies |
| **Release** | `release.yml` | Tag push | Release | Ensures release tags follow semver, changelog exists for the version |
| **Pre-commit** | `pre_commit_guard.sh` | Local commit | Commit | Direct commits to main, missing CHANGELOG updates, non-conventional commit messages |

These layers create defense in depth:
- **Pre-commit** catches problems before they leave your machine (secrets, formatting, direct main commits)
- **Governance check** enforces the process (CHANGELOG must be updated, CLAUDE.md changes need review)
- **AI PR review** catches the subtle problems static analysis misses (naming violations, missing tests, pattern inconsistencies)
- **Release** gates deployment on governance compliance

## Setup requirements

### Governance check (no secrets needed)

```bash
mkdir -p .github/workflows
cp ci-cd/github-actions/governance-check.yml .github/workflows/
```

No secrets or configuration required. Works immediately on push.

### AI PR review (requires API key)

```bash
cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/
```

Then add your Anthropic API key as a GitHub secret:
1. Repository Settings -> Secrets and variables -> Actions
2. New repository secret
3. Name: `ANTHROPIC_API_KEY`
4. Value: your Anthropic API key

**Cost:** Each PR review costs approximately $0.01-$0.05 depending on diff size. At 50 PRs/week, that is $2-10/week -- significantly less than the human time saved by catching convention violations before review.

### Release workflow

```bash
cp ci-cd/github-actions/release.yml .github/workflows/
```

No secrets required. Triggered by version tags (e.g., `v1.2.3`).

### Pre-commit hooks

```bash
# Copy the hook scripts
mkdir -p .claude/hooks
cp scripts/hooks/pre_commit_guard.sh .claude/hooks/
cp scripts/hooks/post_commit.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

Reference in your CLAUDE.md:
```yaml
hooks:
  pre_commit: .claude/hooks/pre_commit_guard.sh
  post_commit: .claude/hooks/post_commit.sh
```

## What each workflow catches

### governance-check.yml

**Trigger:** Any PR where a source code file (`.py`, `.sql`, `.ts`, `.js`, `.go`, `.java`, `.rs`) changed.

**Checks:**
1. If source code changed, CHANGELOG.md must also be modified in the same PR.
2. If CLAUDE.md changed, the PR requires a second reviewer (cannot self-approve).

**Why CHANGELOG enforcement matters:** The CHANGELOG requirement is the keystone of the governance system. If CHANGELOG must be updated to merge, agents update it. If it is optional, it drifts within 3 sessions. Once the CHANGELOG drifts, the next session starts without context, and the governance chain breaks.

**To satisfy:** Run `/end-session` before submitting the PR, or manually add a CHANGELOG entry.

### ai-pr-review.yml

**Trigger:** Every PR when opened or when new commits are pushed.

**Process:**
1. Gets the PR diff
2. Reads CLAUDE.md from the repository for convention rules
3. Sends both to the Claude API with the code-reviewer agent's system prompt
4. Posts the review as a PR comment
5. Sets the check status to PASS, WARN, or FAIL

**What it catches:**
- File naming violations (PascalCase in a snake_case project)
- Commit message format violations (no conventional commits prefix)
- Missing tests for new public functions
- Missing docstrings on public functions
- CHANGELOG.md not updated
- New patterns introduced without ADR
- Scope creep (changes unrelated to the PR description)

### release.yml

**Trigger:** Push of a tag matching `v*` (e.g., `v1.0.0`, `v2.3.1`).

**Checks:**
- Tag follows semantic versioning
- CHANGELOG.md contains an entry for this version
- All CI checks passed on the tagged commit

### pre_commit_guard.sh

**Trigger:** Every local commit.

**Checks:**
- Warns and prompts if committing directly to main/master/production
- Warns if source code changed but CHANGELOG.md is not in the commit
- Warns if CLAUDE.md is being committed directly to main
- Validates commit message follows conventional commits format

## Adding to an existing CI pipeline

If you already have CI/CD and want to add governance incrementally, paste this step into your existing workflow:

```yaml
- name: Governance check — CHANGELOG updated
  run: |
    CODE_CHANGED=$(git diff --name-only origin/main...HEAD \
      | grep -E '\.(py|sql|ts|js|go|java|rs)$' || true)
    if [ -n "$CODE_CHANGED" ]; then
      CHANGELOG_CHANGED=$(git diff --name-only origin/main...HEAD \
        | grep "CHANGELOG.md" || true)
      if [ -z "$CHANGELOG_CHANGED" ]; then
        echo "::error::Code files changed but CHANGELOG.md was not updated."
        echo "Run /end-session or add a CHANGELOG entry before merging."
        exit 1
      fi
    fi
```

This single step enforces the most impactful governance rule (CHANGELOG updates) without requiring any of the other workflows.

## The bypass mechanism

For genuine emergencies (production is down, hotfix needed immediately), a temporary bypass exists:

1. Add the label `skip-governance` to the PR
2. The governance check will pass regardless of CHANGELOG status
3. Create a follow-up PR or issue to add the missing CHANGELOG entry

**Rules for bypass:**
- Bypass is for emergencies, not convenience. If you are using it more than once a month, the governance process needs adjustment, not more bypasses.
- Every bypass must be followed by a CHANGELOG catch-up entry within 48 hours.
- If a team member is using bypass to avoid the process rather than in genuine emergencies, discuss the friction point and fix the root cause.

## Recommended rollout order

Do not enable all four workflows at once. Roll out incrementally:

### Week 1: Governance check only
Start with `governance-check.yml`. This enforces CHANGELOG updates without any AI cost or complexity. The team learns the rhythm of updating CHANGELOG.md with each PR. Resistance is minimal because the fix is simple (add a CHANGELOG entry).

### Week 2: Pre-commit hooks
Add `pre_commit_guard.sh`. This catches direct main commits and missing CHANGELOG updates before they reach the PR. The combination of pre-commit (local) + governance check (CI) means CHANGELOG compliance approaches 100%.

### Week 3: AI PR review
Add `ai-pr-review.yml`. By now the team is used to the governance process. The AI review adds value on top of the existing compliance: it catches naming violations, missing tests, and pattern inconsistencies that the governance check cannot detect.

Set the `ANTHROPIC_API_KEY` secret and monitor the first 10 PR reviews to calibrate. If the AI reviewer is too noisy (flagging things the team considers acceptable), update CLAUDE.md's conventions to be more precise about what is and is not a rule.

### Week 4: Release workflow
Add `release.yml` when you are ready to gate deployments on governance compliance. This is the final layer — it ensures that nothing ships without passing the full governance pipeline.
