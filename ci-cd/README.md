# CI/CD Integration

Automated governance enforcement that catches convention violations, security issues, and process problems before they reach production. Each layer catches different things at different stages of the development workflow.

> **Two locations, one purpose.** The `ci-cd/` directory contains the reusable workflow templates — copy these into your own project. The `.github/workflows/` directory at the root of this repository contains the live copies that actually run on this repo. If you modify a workflow, update both.

## Platform support

Start with GitHub Actions + pre-commit hooks. Other platforms are reference implementations.

| Platform | Status | Directory | Workflows available |
|----------|--------|-----------|-------------------|
| GitHub Actions | **Actively maintained** | `ci-cd/github-actions/` | governance-check, ai-pr-review, release |
| Pre-commit hooks | **Actively maintained** | `ci-cd/pre-commit/` | Local enforcement before CI |
| GitLab CI | Community contributed | `ci-cd/gitlab/` | governance-check, ai-mr-review, tests |
| CircleCI | Community contributed | `ci-cd/circleci/` | governance, ai-pr-review, tests |
| Bitbucket Pipelines | Community contributed | `ci-cd/bitbucket/` | governance-check, ai-pr-review, tests |
| Azure DevOps | Community contributed | `ci-cd/azure-devops/` | governance, ai-review, tests (3-stage pipeline) |

---

## Quick setup by platform

### GitHub Actions

```bash
mkdir -p .github/workflows
cp ci-cd/github-actions/governance-check.yml .github/workflows/
cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/  # requires ANTHROPIC_API_KEY secret
cp ci-cd/github-actions/release.yml .github/workflows/
```

### GitLab CI

```bash
cp ci-cd/gitlab/.gitlab-ci.yml .gitlab-ci.yml
```

Add variables in **Settings → CI/CD → Variables**: `ANTHROPIC_API_KEY` (masked, protected), `GITLAB_TOKEN` (api scope).

### CircleCI

```bash
mkdir -p .circleci
cp ci-cd/circleci/.circleci/config.yml .circleci/config.yml
```

Add environment variables in **Project Settings → Environment Variables**: `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`.

### Bitbucket Pipelines

```bash
cp ci-cd/bitbucket/bitbucket-pipelines.yml bitbucket-pipelines.yml
```

Add repository variables in **Settings → Pipelines → Repository variables**: `ANTHROPIC_API_KEY`, `BB_TOKEN`.

### Azure DevOps

```bash
cp ci-cd/azure-devops/azure-pipelines.yml azure-pipelines.yml
```

Create variable group `governance-secrets` in **Pipelines → Library** with `ANTHROPIC_API_KEY` and `AZURE_DEVOPS_TOKEN`. See `ci-cd/azure-devops/README.md` for detailed setup.

### Pre-commit hooks

```bash
mkdir -p .claude/hooks
cp scripts/hooks/pre_commit_guard.sh .claude/hooks/
cp scripts/hooks/post_commit.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

---

## Feature comparison matrix

| Feature | GitHub Actions | GitLab CI | CircleCI | Bitbucket | Azure DevOps |
|---------|---------------|-----------|----------|-----------|--------------|
| CHANGELOG enforcement | Yes | Yes | Yes | Yes | Yes |
| AI PR/MR review | Yes | Yes | Yes | Yes | Yes |
| Post review as comment | Yes | Yes | Yes (with GITHUB_TOKEN) | Yes | Yes |
| Release/tag gating | Yes | Configurable | Configurable | Configurable | Configurable |
| Test matrix (3.10/3.11/3.12) | Yes | Yes | Yes (3.10/3.12) | Yes (3.12) | Yes |
| Emergency bypass | Label: skip-governance | Label: skip-governance | Env var or commit msg | Commit msg | Commit msg |
| Secrets required for review | ANTHROPIC_API_KEY | ANTHROPIC_API_KEY + GITLAB_TOKEN | ANTHROPIC_API_KEY + GITHUB_TOKEN | ANTHROPIC_API_KEY + BB_TOKEN | ANTHROPIC_API_KEY + AZURE_DEVOPS_TOKEN |
| Native PR metadata access | Full | Full | Partial | Partial | Full |
| Free tier build minutes | 2,000/month | 400/month | 6,000/month | 50/month | 1,800/month |

---

## The governance workflows

### 1. Governance check (all platforms)

**Trigger:** Every pull request / merge request where source code changed.

**What it enforces:**
- If source code files (`.py`, `.sql`, `.ts`, `.js`, `.go`, `.java`, `.rs`, `.cs`) changed, `CHANGELOG.md` must also be modified in the same PR.
- If `CLAUDE.md` changed, the PR requires a second reviewer (GitHub Actions only — configure branch protection on other platforms).

**Why CHANGELOG enforcement matters:** The CHANGELOG requirement is the keystone of the governance system. If CHANGELOG must be updated to merge, agents update it. If it is optional, it drifts within 3 sessions. Once the CHANGELOG drifts, the next session starts without context, and the governance chain breaks.

**To satisfy:** Run `/end-session` before submitting the PR, or manually add a CHANGELOG entry.

### 2. AI PR review (all platforms)

**Trigger:** Every PR/MR when opened or when new commits are pushed.

**What it catches:**
- File naming violations (PascalCase in a snake_case project)
- Commit message format violations (no conventional commits prefix)
- Missing tests for new public functions
- Missing docstrings on public functions
- CHANGELOG.md not updated
- New patterns introduced without ADR
- Scope creep (changes unrelated to the PR description)

**Verdict system:**
- `FAIL` — must be fixed before merge (blocks the pipeline)
- `WARN` — recommended fixes, does not block
- `PASS` — no violations found

**Cost:** ~$0.01–$0.05 per review (Anthropic API). At 50 PRs/week: $2–10/week.

### 3. Release / tag gating (GitHub Actions)

**Trigger:** Push of a tag matching `v*` (e.g., `v1.0.0`, `v2.3.1`).

**Checks:**
- Tag follows semantic versioning
- CHANGELOG.md contains an entry for this version
- All CI checks passed on the tagged commit

### 4. Pre-commit hooks (local enforcement)

**Trigger:** Every local commit.

**Checks:**
- Warns and prompts if committing directly to main/master/production
- Warns if source code changed but CHANGELOG.md is not in the commit
- Validates commit message follows conventional commits format

---

## Adding governance to an existing pipeline

The minimum addition is this single step — paste it into any platform's existing pipeline:

```bash
# Shell script — works in GitHub Actions, GitLab CI, CircleCI, Bitbucket
git fetch origin main
CHANGED=$(git diff --name-only origin/main...HEAD)
CODE=$(echo "$CHANGED" | grep -E '\.(py|sql|ts|js|go|java|rs)$' || true)
if [ -n "$CODE" ]; then
  CL=$(echo "$CHANGED" | grep "^CHANGELOG\.md$" || true)
  if [ -z "$CL" ]; then
    echo "ERROR: Code files changed but CHANGELOG.md was not updated."
    echo "Run /end-session or add a CHANGELOG entry before merging."
    exit 1
  fi
fi
echo "Governance check passed."
```

This single check enforces the most impactful governance rule without requiring any of the other workflows.

---

## The bypass mechanism

For genuine emergencies (production is down, hotfix needed immediately):

**GitHub Actions / GitLab CI:** Add the label `skip-governance` to the PR/MR.

**CircleCI / Bitbucket / Azure DevOps:** Include `[skip-governance]` in the commit message.

**Rules for bypass:**
- Bypass is for emergencies, not convenience. If you are using it more than once a month, the governance process needs adjustment, not more bypasses.
- Every bypass must be followed by a CHANGELOG catch-up entry within 48 hours.

---

## Recommended rollout order

Do not enable all workflows at once. Roll out incrementally:

### Week 1: Governance check only

Start with the CHANGELOG enforcement check. No secrets required. The team learns the rhythm of updating CHANGELOG.md with each PR. Resistance is minimal because the fix is simple.

### Week 2: Pre-commit hooks

Add local enforcement. The combination of pre-commit (local) + governance check (CI) means CHANGELOG compliance approaches 100%.

### Week 3: AI PR review

By now the team is used to the governance process. The AI review adds value on top: it catches naming violations, missing tests, and pattern inconsistencies that the governance check cannot detect.

Set the `ANTHROPIC_API_KEY` secret and monitor the first 10 PR reviews. If the AI reviewer is too noisy, update CLAUDE.md conventions to be more precise.

### Week 4: Release gating

Gate deployments on governance compliance. This ensures nothing ships without passing the full governance pipeline.

---

## Platform-specific documentation

- GitHub Actions: see `ci-cd/github-actions/` (individual workflow files are self-documented)
- GitLab CI: see `ci-cd/gitlab/README.md`
- CircleCI: see `ci-cd/circleci/README.md`
- Bitbucket Pipelines: see `ci-cd/bitbucket/README.md`
- Azure DevOps: see `ci-cd/azure-devops/README.md`
