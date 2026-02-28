# Automation Scripts

This directory contains scripts that automate recurring governance tasks for the AI Governance Framework.

| Script | Purpose |
|--------|---------|
| `governance_dashboard.py` | Generates `DASHBOARD.md` with health score, velocity, cost, ADR coverage, and maturity level |
| `cost_dashboard.py` | Generates `COST_DASHBOARD.md` with cost breakdown by model, session type, and routing efficiency |
| `framework_updater.py` | Checks for new framework releases and shows available updates |
| `best_practice_scanner.py` | Scans configured sources for new AI governance insights |
| `health_score_calculator.py` | Calculates a governance health score (0-100) for a repository |
| `inherits_from_validator.py` | Validates that a CLAUDE.md respects its parent constitutions |
| `token_counter.py` | Estimates session token usage from git history and updates COST_LOG.md |
| `adr_coverage_checker.py` | Identifies architectural decisions that lack a corresponding ADR |

These scripts support the [self-updating framework architecture](../docs/self-updating-framework.md) by gathering data that feeds into Layer 7 (Evolution). They surface information for human review — none of them automatically modify `CLAUDE.md`, security rules, or any governance configuration.

## Prerequisites

- Python 3.10+
- `requests` library (required by `framework_updater.py` and `best_practice_scanner.py`)

```bash
pip install requests
```

All other scripts use the Python standard library only and have no external dependencies.

## Usage

```bash
# Generate the full governance dashboard (DASHBOARD.md)
python3 automation/governance_dashboard.py --repo-path .

# Generate the cost analysis dashboard (COST_DASHBOARD.md)
python3 automation/cost_dashboard.py --repo-path .

# Check for framework updates
python3 automation/framework_updater.py --repo-path .

# Scan for new AI governance insights from the last 14 days
python3 automation/best_practice_scanner.py --days 14

# Calculate governance health score for the current repo
python3 automation/health_score_calculator.py .

# Validate CLAUDE.md constitutional inheritance
python3 automation/inherits_from_validator.py CLAUDE.md

# Estimate token usage since the last COST_LOG.md update
python3 automation/token_counter.py --repo-path .

# Check which decisions lack ADR coverage
python3 automation/adr_coverage_checker.py --repo-path .
```

All scripts accept `--help` for full usage documentation.

## CI/CD Integration

The scripts are designed to run as GitHub Actions jobs. See `.github/workflows/` for live examples.

```yaml
# Example: ADR coverage check on every PR (advisory mode)
jobs:
  adr-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 automation/adr_coverage_checker.py --threshold warn

# Example: scheduled weekly automation
on:
  schedule:
    - cron: "0 9 * * 1"  # Every Monday at 09:00 UTC

jobs:
  governance-automation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests
      - run: python3 automation/health_score_calculator.py . --threshold 40
      - run: python3 automation/token_counter.py --repo-path .
      - run: python3 automation/framework_updater.py --check-only
      - run: python3 automation/best_practice_scanner.py --days 7 --output-file governance-insights.json
      - uses: actions/upload-artifact@v4
        with:
          name: governance-insights
          path: governance-insights.json
```

## Script Reference

### governance_dashboard.py

Generates `DASHBOARD.md` — a full governance dashboard from local governance files. Reads `CHANGELOG.md`, `COST_LOG.md`, `MEMORY.md`, `PROJECT_PLAN.md`, and `docs/adr/`. Calls `health_score_calculator.py` internally for the health score. No external dependencies.

Sections generated: Health Score, Session Velocity, Cost Trend, Knowledge Health, ADR Coverage, Sprint Progress, Governance Maturity Level.

```bash
python3 automation/governance_dashboard.py --repo-path .
python3 automation/governance_dashboard.py --repo-path . --output DASHBOARD.md
python3 automation/governance_dashboard.py --repo-path . --stdout
```

Recommended: run weekly via CI, commit result to track history.

---

### cost_dashboard.py

Generates `COST_DASHBOARD.md` — a cost analysis dashboard from `COST_LOG.md`. Breaks down spend by model, session type, and calendar month. Calculates a model routing efficiency ratio (actual spend / optimal spend) and produces specific routing recommendations.

```bash
python3 automation/cost_dashboard.py --repo-path .
python3 automation/cost_dashboard.py --repo-path . --output COST_DASHBOARD.md
```

Recommended: run monthly before cost review. Review misrouted sessions as a team.

---

### health_score_calculator.py

Calculates a governance health score from 0 to 100 based on maturity model criteria. Checks for the presence and content of governance files: `CLAUDE.md`, `PROJECT_PLAN.md`, `CHANGELOG.md`, `ARCHITECTURE.md`, ADRs, pre-commit hooks, GitHub Actions workflows, agent and command definitions, and more.

```bash
python3 automation/health_score_calculator.py . --threshold 40
python3 automation/health_score_calculator.py . --format json --output-file report.json
```

CI gate: exits 1 if score is below `--threshold`.

---

### inherits_from_validator.py

Reads a `CLAUDE.md`, extracts the `inherits_from` section, fetches each parent constitution (local path or URL), and validates three invariants:

1. The local file does not remove sections required by the parent.
2. The local file does not grant permissions the parent prohibits.
3. The local file does not lower numeric thresholds set by the parent.

```bash
python3 automation/inherits_from_validator.py CLAUDE.md
python3 automation/inherits_from_validator.py CLAUDE.md --parent templates/CLAUDE.org.md
python3 automation/inherits_from_validator.py CLAUDE.md --format json --threshold warn
```

CI gate: exits 1 on any violation when `--threshold strict` (default).

---

### token_counter.py

Parses session entries from `CHANGELOG.md`, queries git for lines added and removed on the session date, and estimates token usage using a calibrated model (8 tokens per added line, 3 per removed line). Appends new rows to `COST_LOG.md` in the standard table format.

```bash
python3 automation/token_counter.py --repo-path .
python3 automation/token_counter.py --dry-run
python3 automation/token_counter.py --format json
```

Use as a post-session hook: add to `scripts/hooks/post_commit.sh`.

---

### adr_coverage_checker.py

Reads decisions from `CHANGELOG.md` ("Decisions made" sections) and `DECISIONS.md` (DEC-NNN entries), then cross-references them against ADR files in `docs/adr/`. Reports decisions that share fewer than two significant keywords with any existing ADR.

```bash
python3 automation/adr_coverage_checker.py --repo-path .
python3 automation/adr_coverage_checker.py --threshold warn --format json
```

CI gate: exits 1 if uncovered decisions exist when `--threshold strict` (default).

---

### framework_updater.py

Queries the GitHub API for new releases of the ai-governance-framework. Compares the upstream version against the local `.governance-version` file and shows what has changed. Never modifies files — output is for human review only.

```bash
python3 automation/framework_updater.py --repo-path .
python3 automation/framework_updater.py --check-only
```

---

### best_practice_scanner.py

Scans Anthropic's blog RSS feed and GitHub trending topics for new AI governance insights. Filters results by configured keywords and relevance score. Outputs findings as JSON for human review via the research agent pipeline.

```bash
python3 automation/best_practice_scanner.py --days 7
python3 automation/best_practice_scanner.py --days 14 --output-file insights.json
```

---

## What These Scripts Do NOT Do

- They never modify `CLAUDE.md` or any security configuration automatically.
- They never apply updates without explicit human approval.
- They never push commits, open pull requests, or merge branches.
- They propose changes and surface information. A human (or a governed agent with explicit write access) makes the decision.
