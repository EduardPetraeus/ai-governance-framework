# PR-Based Governance Workflow

This document explains how to set up pull request governance using GitHub Actions, branch protection rules, and the governance gate workflow.

## Overview

PR-based governance ensures that every code change passes automated quality, security, and governance checks before merging. The workflow prevents ungoverned code from reaching the main branch.

```
Developer pushes branch
        │
        ▼
  PR opened to main
        │
        ▼
  ┌─────────────────────────┐
  │  GitHub Actions trigger  │
  │  governance-gate.yml     │
  └─────────────────────────┘
        │
        ├── Lint (ruff check, ruff format)
        ├── Test (pytest)
        ├── Security Scan (secrets in diff, .gitignore)
        └── Governance Check (CLAUDE.md, quality, drift)
        │
        ▼
  All checks pass?
    ├── Yes → Ready for review
    └── No  → Merge blocked
```

## Step 1: Install the Governance Gate Workflow

Copy the workflow file to your repository:

```bash
mkdir -p .github/workflows
cp ai-governance-framework/templates/ci-cd/github-actions-governance-gate.yml \
   .github/workflows/governance-gate.yml
```

Copy the automation scripts that the workflow references:

```bash
mkdir -p automation
cp ai-governance-framework/automation/content_quality_checker.py automation/
cp ai-governance-framework/automation/drift_detector.py automation/
```

Commit and push:

```bash
git add .github/workflows/governance-gate.yml automation/
git commit -m "chore: add governance gate workflow and automation scripts"
git push
```

## Step 2: Configure Branch Protection Rules

In your GitHub repository settings:

1. Go to **Settings > Branches > Branch protection rules**
2. Click **Add rule**
3. Set **Branch name pattern** to `main`
4. Enable these settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| Require a pull request before merging | Enabled | Prevents direct pushes to main |
| Require approvals | 1 (minimum) | At least one human reviews every change |
| Dismiss stale pull request approvals | Enabled | New pushes invalidate old approvals |
| Require status checks to pass before merging | Enabled | Blocks merge until CI passes |
| Required status checks | `Lint`, `Test`, `Security Scan`, `Governance Check` | All four governance gate jobs |
| Require branches to be up to date before merging | Enabled | Prevents merge conflicts in main |
| Require conversation resolution before merging | Enabled | All review comments must be addressed |
| Do not allow bypassing the above settings | Enabled (recommended) | Even admins must follow the rules |

## Step 3: Set Up Required Reviewers

For teams with specialized roles:

1. Create a `CODEOWNERS` file in your repository root:

```
# Default owner for all files
* @your-team

# Governance files require governance owner review
CLAUDE.md @governance-owner
.github/workflows/ @devops-lead
automation/ @governance-owner
```

2. In branch protection settings, enable **Require review from Code Owners**

This ensures governance file changes are reviewed by the person responsible for governance, not just any team member.

## Step 4: Pre-Merge Checklist

Add this checklist to your PR template (`.github/pull_request_template.md`):

```markdown
## Pre-Merge Checklist

### Automated (enforced by CI)
- [ ] Lint passes (ruff check, ruff format)
- [ ] Tests pass (pytest)
- [ ] No secrets in diff
- [ ] CLAUDE.md exists and passes quality check
- [ ] No governance drift detected

### Manual (enforced by reviewer)
- [ ] Changes match the PR description
- [ ] No scope creep beyond the stated task
- [ ] Architectural decisions documented if applicable
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] No TODO comments without linked issues
```

## Workflow Reference

### Jobs and What They Check

| Job | Checks | Failure Means |
|-----|--------|---------------|
| **Lint** | `ruff check`, `ruff format --check` | Code style violations or formatting issues |
| **Test** | `pytest tests/ -v` | Tests fail or are missing |
| **Security Scan** | Secret patterns in diff, `.gitignore` validation | Potential credentials in code |
| **Governance Check** | CLAUDE.md existence, content quality, drift detection | Governance files missing or degraded |

### Customizing the Workflow

To adjust the governance gate for your project:

- **Change Python version**: Edit the `python-version` field in each job
- **Add dependencies**: Add a `pip install` step before the test job
- **Adjust secret patterns**: Edit the `PATTERNS` array in the security scan job
- **Skip drift detection**: Remove the drift detection step if your project does not use a governance template
- **Add mutation testing**: Add a mutation testing job referencing [docs/mutation-testing-guide.md](../docs/mutation-testing-guide.md)

### Running Locally

Test the governance checks locally before pushing:

```bash
# Lint
ruff check . && ruff format --check .

# Tests
python -m pytest tests/ -v --tb=short

# Content quality
python automation/content_quality_checker.py .

# Drift detection
python automation/drift_detector.py \
  --template templates/CLAUDE.md \
  --target CLAUDE.md
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Governance Check fails but CLAUDE.md exists | CLAUDE.md lacks required sections | Add missing sections — run `drift_detector.py` to see which |
| Security Scan false positive | Pattern matches non-secret content | Exclude the file type in the grep command |
| Drift detection skipped | No `templates/CLAUDE.md` in the repo | Copy the governance template or remove the drift step |
| Status checks not appearing | Workflow file not on the default branch | Merge the workflow file to main first |
