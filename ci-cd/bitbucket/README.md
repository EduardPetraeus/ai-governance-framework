> **Community Contributed — Not Actively Maintained**
>
> These workflows were contributed as reference implementations. They are not
> actively tested or maintained by the core project. GitHub Actions is the
> primary supported CI/CD platform. Community PRs to update these are welcome.

# Bitbucket Pipelines Integration

Bitbucket Pipelines equivalents for all governance workflows. These pipelines enforce the same rules — CHANGELOG updates, AI PR review, test coverage — on Bitbucket repositories.

## Files

| File | Purpose |
|------|---------|
| `bitbucket-pipelines.yml` | Complete Bitbucket Pipelines configuration |

## Setup

```bash
cp ci-cd/bitbucket/bitbucket-pipelines.yml bitbucket-pipelines.yml
```

Commit and push. Bitbucket Pipelines activates automatically when `bitbucket-pipelines.yml` is present in the repository root.

Enable pipelines in **Repository Settings → Pipelines → Settings → Enable Pipelines**.

## Required repository variables

Set in **Repository Settings → Pipelines → Repository variables**:

| Variable | Required | Secured | Notes |
|----------|----------|---------|-------|
| `ANTHROPIC_API_KEY` | For AI review | Yes | Anthropic API key |
| `BB_TOKEN` | For PR comments | Yes | Bitbucket access token with `pullrequest:write` scope |

### Creating a Bitbucket access token

1. Go to **Bitbucket Settings → Access Management → Access tokens**
2. Create a repository access token with scope: `pullrequest:write`
3. Save the token value as the `BB_TOKEN` repository variable

## Pipeline structure

| Pipeline | Triggers | Jobs |
|----------|----------|------|
| `default` | Every push to any branch | governance-check, run-tests |
| `pull-requests/**` | Every pull request | governance-check, ai-pr-review, run-tests |
| `branches/main` | Push to main | governance-check, run-tests |

## Bypass for emergencies

Add a check at the top of the governance-check script for a commit message keyword:

```yaml
- step: &governance-check
    script:
      - apk add --no-cache git
      - |
        if git log -1 --pretty=%B | grep -q "\[skip-governance\]"; then
          echo "Governance bypassed via commit message. Add CHANGELOG entry in follow-up."
          exit 0
        fi
        # ... rest of check
```

## Differences from GitHub Actions

| Feature | GitHub Actions | Bitbucket Pipelines |
|---------|---------------|---------------------|
| Trigger | `pull_request` | `pull-requests/**` section |
| PR number | `github.event.pull_request.number` | `BITBUCKET_PR_ID` |
| Workspace | `github.repository` | `BITBUCKET_WORKSPACE` + `BITBUCKET_REPO_SLUG` |
| Comment API | GitHub Issues API | Bitbucket 2.0 API |
| Token | `github.token` | `BB_TOKEN` (manual) |
| Label skip | PR labels | Commit message keyword |

The governance logic (CHANGELOG check, AI review prompt, verdict format) is identical.

## Cost

Bitbucket Pipelines includes 50 build minutes/month on the free plan, 2,500 on Standard.

The governance check runs in under 1 minute. The AI review adds ~$0.01–$0.05 per PR for the API call (billed by Anthropic, not Bitbucket).
