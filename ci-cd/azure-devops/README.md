# Azure DevOps Integration

Azure DevOps Pipelines equivalents for all governance workflows. These pipelines enforce the same rules — CHANGELOG updates, AI PR review, test coverage — on Azure DevOps repositories.

## Files

| File | Purpose |
|------|---------|
| `azure-pipelines.yml` | Complete Azure DevOps pipeline (3 stages) |

## Setup

### 1. Copy the pipeline file

```bash
cp ci-cd/azure-devops/azure-pipelines.yml azure-pipelines.yml
```

### 2. Connect in Azure DevOps

1. Go to **Pipelines → New pipeline**
2. Select your repository source (Azure Repos, GitHub, Bitbucket, etc.)
3. Select **Existing Azure Pipelines YAML file**
4. Set path: `/azure-pipelines.yml`
5. Save and run

### 3. Configure secrets

Create a variable group named `governance-secrets`:

1. **Pipelines → Library → Variable groups → Add variable group**
2. Name: `governance-secrets`
3. Add variables:

| Variable | Required | Secret | Notes |
|----------|----------|--------|-------|
| `ANTHROPIC_API_KEY` | For AI review | Yes | Anthropic API key |
| `AZURE_DEVOPS_TOKEN` | For PR comments | Yes | PAT with Code Read + PR Thread Write permissions |

4. Link the variable group to the pipeline: **Pipeline → Edit → Variables → Variable groups**

### 4. Enable PR triggers

In Azure DevOps, go to **Pipelines → your-pipeline → Edit → Triggers**:
- Enable **Pull request validation**
- Set target branches: `main`, `master`

## Creating an Azure DevOps Personal Access Token

1. Go to **User Settings → Personal Access Tokens**
2. New token with scopes:
   - **Code:** Read
   - **Pull Request Threads:** Read & Write
3. Copy the token and add it as the `AZURE_DEVOPS_TOKEN` variable

## Pipeline stages

| Stage | Condition | Jobs |
|-------|-----------|------|
| Governance | All PR builds | ChangelogCheck |
| AIReview | PRs only, after Governance passes | ClaudeReview |
| Tests | All builds | PythonTests (3.10, 3.11, 3.12 matrix) |

## Bypass for emergencies

Azure DevOps supports build policies that can be bypassed with sufficient permissions.

To add a commit-message based bypass to the pipeline:

```yaml
- script: |
    if git log -1 --pretty=%B | grep -q "\[skip-governance\]"; then
      echo "Governance bypassed via commit message."
      exit 0
    fi
    # ... rest of check
  displayName: Check CHANGELOG updated
```

Alternatively, **mark the stage as optional** in the branch policy: **Project Settings → Repositories → Policies → Build Validation → Optional**.

## Branch policies (recommended)

Configure branch policies on `main`/`master` to enforce the pipeline status:

1. **Project Settings → Repositories → Branches → main → Branch policies**
2. Add **Build validation** pointing to your pipeline
3. Set **Policy requirement: Required** (not optional)
4. Set **Reset conditions: Always reset** (re-run on new commits)

This ensures the governance check and tests must pass before any PR can be merged.

## Differences from GitHub Actions

| Feature | GitHub Actions | Azure DevOps |
|---------|---------------|--------------|
| Trigger | `pull_request` event | `pr:` section in YAML |
| PR number | `github.event.pull_request.number` | `SYSTEM_PULLREQUEST_PULLREQUESTID` |
| PR title | `github.event.pull_request.title` | `SYSTEM_PULLREQUEST_PULLREQUESTTITLE` |
| Base branch | `github.base_ref` | `SYSTEM_PULLREQUEST_TARGETBRANCH` |
| Comment API | GitHub Issues API | Azure DevOps Git PR Threads API |
| Token | `github.token` (automatic) | PAT (manual setup) |
| Test results | Actions artifacts | `PublishTestResults@2` task |

The governance logic (CHANGELOG check, AI review prompt, verdict format) is identical.

## Cost

Azure DevOps includes 1,800 free pipeline minutes/month (Microsoft-hosted agents). The governance check runs under 1 minute. Tests run in 2–3 minutes.

The AI review adds ~$0.01–$0.05 per PR for the Anthropic API call.
