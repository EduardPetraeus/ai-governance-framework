# CircleCI Integration

CircleCI equivalents for all GitHub Actions governance workflows. These pipelines enforce the same governance rules — CHANGELOG updates, AI PR review, test coverage — on CircleCI.

## Files

| File | Purpose |
|------|---------|
| `.circleci/config.yml` | Complete CircleCI pipeline |

## Setup

### New project

```bash
mkdir -p .circleci
cp ci-cd/circleci/.circleci/config.yml .circleci/config.yml
```

Commit and push — CircleCI picks up the pipeline automatically if your repository is connected.

### Existing CircleCI project

Add the governance and test jobs from `.circleci/config.yml` to your existing config. The minimum addition is the `governance-check` job — it requires no secrets and enforces the CHANGELOG update rule.

Minimum addition to an existing workflow:

```yaml
jobs:
  governance-check:
    docker:
      - image: alpine:3.19
    steps:
      - checkout
      - run:
          name: Install git
          command: apk add --no-cache git
      - run:
          name: Check CHANGELOG.md updated
          command: |
            git fetch origin main
            CHANGED=$(git diff --name-only origin/main...HEAD)
            CODE=$(echo "$CHANGED" | grep -E '\.(py|sql|ts|js|go|java|rs)$' || true)
            if [ -n "$CODE" ]; then
              CL=$(echo "$CHANGED" | grep "^CHANGELOG\.md$" || true)
              if [ -z "$CL" ]; then
                echo "ERROR: Code changed but CHANGELOG.md not updated."
                exit 1
              fi
            fi
            echo "Governance check passed."

workflows:
  your-existing-workflow:
    jobs:
      - governance-check
      - your-existing-jobs
```

## Required environment variables

Set in **Project Settings → Environment Variables**:

| Variable | Required | Notes |
|----------|----------|-------|
| `ANTHROPIC_API_KEY` | For AI review | Anthropic API key for Claude |
| `GITHUB_TOKEN` | For PR comments | GitHub token with `repo` scope for posting review comments |

## Limitations vs GitHub Actions

CircleCI does not have native access to GitHub PR metadata the same way GitHub Actions does. The `ai-pr-review` job in the config uses `CIRCLE_PULL_REQUEST` to determine the PR URL and `GITHUB_TOKEN` to post comments.

If you are using CircleCI with a non-GitHub VCS (GitLab, Bitbucket), update the comment-posting logic in the `ai-pr-review` job to use that platform's API.

## Cost

CircleCI's free tier includes 6,000 build minutes/month on Linux. The governance check and test jobs typically run in under 2 minutes each.

The AI review adds ~$0.01–$0.05 per PR run for the Anthropic API call (separate from CircleCI costs).

## Bypass for emergencies

CircleCI does not have a native label system. To bypass governance for urgent hotfixes:

Option 1 — Environment variable bypass:
```yaml
governance-check:
  steps:
    - run:
        command: |
          if [ "$SKIP_GOVERNANCE" = "true" ]; then
            echo "Governance check bypassed."
            exit 0
          fi
          # ... rest of check
```

Set `SKIP_GOVERNANCE=true` in Project Settings temporarily, then remove it after the hotfix.

Option 2 — Commit message bypass:
```yaml
- run:
    command: |
      if git log -1 --pretty=%B | grep -q "\[skip-governance\]"; then
        echo "Governance check bypassed via commit message."
        exit 0
      fi
```

Either way, create a follow-up to add the CHANGELOG entry.
