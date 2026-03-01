> **Community Contributed — Not Actively Maintained**
>
> These workflows were contributed as reference implementations. They are not
> actively tested or maintained by the core project. GitHub Actions is the
> primary supported CI/CD platform. Community PRs to update these are welcome.

# GitLab CI Integration

GitLab CI equivalents for all GitHub Actions governance workflows. These pipelines enforce the same governance rules — CHANGELOG updates, AI MR review, test coverage gates — on GitLab repositories.

## Files

| File | Purpose | Secrets required |
|------|---------|-----------------|
| `.gitlab-ci.yml` | Complete pipeline — governance check + AI review | `ANTHROPIC_API_KEY` (optional) |
| `ai-review.yml` | Standalone AI review job for inclusion in existing pipelines | `ANTHROPIC_API_KEY` |
| `tests.yml` | Python test suite across Python 3.10/3.11/3.12 | None |

## Setup

### Option 1: Full pipeline (recommended for new projects)

Copy the main pipeline file to your repository root:

```bash
cp ci-cd/gitlab/.gitlab-ci.yml .gitlab-ci.yml
```

This activates:
- `governance-check` job on every merge request
- `ai-mr-review` job on every merge request (requires `ANTHROPIC_API_KEY`)

### Option 2: Add to an existing pipeline

If you already have a `.gitlab-ci.yml`, include the governance check as a step or use the `include` directive:

```yaml
# In your existing .gitlab-ci.yml

include:
  - local: 'ci-cd/gitlab/ai-review.yml'

stages:
  - your-existing-stages
  - review  # Add this stage

# Or paste the governance-check job directly:
governance-check:
  stage: test
  image: alpine:3.19
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  before_script:
    - apk add --no-cache git
  script:
    - |
      git fetch origin $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
      CHANGED=$(git diff --name-only origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD)
      CODE_FILES=$(echo "$CHANGED" | grep -E '\.(py|sql|ts|js|go|java|rs)$' || true)
      if [ -n "$CODE_FILES" ]; then
        CHANGELOG=$(echo "$CHANGED" | grep "^CHANGELOG\.md$" || true)
        if [ -z "$CHANGELOG" ]; then
          echo "ERROR: Code changed but CHANGELOG.md not updated."
          exit 1
        fi
      fi
      echo "Governance check passed."
```

### Option 3: Tests only

```yaml
include:
  - local: 'ci-cd/gitlab/tests.yml'
```

## Required CI/CD variables

Set these in **Settings → CI/CD → Variables**:

| Variable | Required | Type | Notes |
|----------|----------|------|-------|
| `ANTHROPIC_API_KEY` | For AI review only | Masked, Protected | Anthropic API key for Claude |
| `GITLAB_TOKEN` | For posting MR notes | Masked, Protected | Personal access token with `api` scope, or use `CI_JOB_TOKEN` with expanded permissions |

### Setting `ANTHROPIC_API_KEY`

1. Go to your project or group: **Settings → CI/CD → Variables**
2. Click **Add variable**
3. Key: `ANTHROPIC_API_KEY`
4. Value: your Anthropic API key
5. Type: Variable
6. Enable **Mask variable** (prevents the key from appearing in job logs)
7. Enable **Protected variable** (limits to protected branches only — recommended)

### Setting `GITLAB_TOKEN` for MR notes

Option A — Use project access token (recommended for teams):
1. **Settings → Access Tokens → Add new token**
2. Scopes: `api`
3. Set as CI/CD variable named `GITLAB_TOKEN`

Option B — Use `CI_JOB_TOKEN` (simpler, but requires expanded permissions):
1. **Settings → CI/CD → Token Access**
2. Enable "Allow CI job tokens from this project to access this project"
3. The `ai-review.yml` falls back to `CI_JOB_TOKEN` automatically

## Merge request approval rules

To enforce CLAUDE.md changes require a second reviewer, configure approval rules in GitLab:

1. **Settings → Merge requests → Approval rules**
2. Add a rule: **Required approvals: 2** when `CLAUDE.md` changes
3. Alternatively, use the Code Owners feature:

```
# .gitlab/CODEOWNERS
CLAUDE.md @your-org/governance-reviewers
```

## Bypass for emergencies

To skip the governance check on an urgent hotfix:

1. Add the label `skip-governance` to the merge request
2. The `governance-check` job checks for this label and exits without failing
3. Create a follow-up issue to add the missing CHANGELOG entry within 48 hours

## Cost

The AI MR review costs approximately $0.01–$0.05 per merge request depending on diff size. At 50 MRs/week, that is $2–10/week.

The governance check, test jobs, and release checks are free (no external API calls).

## Differences from GitHub Actions

| Feature | GitHub Actions | GitLab CI |
|---------|---------------|-----------|
| Trigger name | `pull_request` | `merge_request_event` |
| Base branch variable | `github.base_ref` | `CI_MERGE_REQUEST_TARGET_BRANCH_NAME` |
| PR/MR number | `github.event.pull_request.number` | `CI_MERGE_REQUEST_IID` |
| Token for API calls | `github.token` | `CI_JOB_TOKEN` or `GITLAB_TOKEN` |
| Posting review comments | GitHub Issues API | GitLab MR Notes API |
| Label-based skip | `github.event.pull_request.labels` | `CI_MERGE_REQUEST_LABELS` |

The governance logic (CHANGELOG check, AI review, verdict format) is identical between platforms.
