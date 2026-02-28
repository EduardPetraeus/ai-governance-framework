# Automation Scripts

This directory contains three scripts that automate recurring governance tasks for the AI Governance Framework.

| Script | Purpose |
|--------|---------|
| `framework_updater.py` | Checks for new framework releases and shows available updates |
| `best_practice_scanner.py` | Scans configured sources for new AI governance insights |
| `health_score_calculator.py` | Calculates a governance health score (0-100) for a repository |

These scripts support the [self-updating framework architecture](../docs/self-updating-framework.md) by gathering data that feeds into Layer 7 (Evolution). They surface information for human review — none of them automatically modify `CLAUDE.md`, security rules, or any governance configuration.

## Prerequisites

- Python 3.10+
- `requests` library (required by `framework_updater.py` and `best_practice_scanner.py`)

```bash
pip install requests
```

## Usage

```bash
# Check for framework updates
python automation/framework_updater.py --repo-path .

# Scan for new AI governance insights from the last 14 days
python automation/best_practice_scanner.py --days 14

# Calculate governance health score for the current repo
python automation/health_score_calculator.py .
```

## CI/CD Integration

All three scripts are designed to run as scheduled GitHub Actions workflows.

```yaml
# .github/workflows/governance-automation.yml
name: Governance Automation
on:
  schedule:
    - cron: "0 9 * * 1"  # Every Monday at 09:00 UTC
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests
      - run: python automation/health_score_calculator.py . --threshold 40
      - run: python automation/framework_updater.py --check-only
      - run: python automation/best_practice_scanner.py --days 7 --output-file governance-insights.json
      - uses: actions/upload-artifact@v4
        with:
          name: governance-insights
          path: governance-insights.json
```

## What These Scripts Do NOT Do

- They never modify `CLAUDE.md` or any security configuration automatically.
- They never apply updates without explicit human approval.
- They never push commits, open pull requests, or merge branches.
- They propose changes and surface information. A human (or a governed agent with explicit write access) makes the decision.
