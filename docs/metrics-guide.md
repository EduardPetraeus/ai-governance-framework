# Metrics Guide: What to Measure, What Not to Measure, and Why

## 1. The Measurement Principle

Measure outcomes, not activity.

This distinction sounds obvious and is routinely ignored. The reason: activity is easy to count (commits, lines, sessions) and outcomes are hard to define (working features, prevented defects, maintained architecture). AI development amplifies this problem catastrophically. Agents generate enormous amounts of measurable activity — commits, lines of code, documentation pages, tasks — and almost none of it correlates reliably with the outcomes that matter to the business.

Three corollaries follow from the measurement principle:

1. **Fewer metrics, measured consistently, acted upon.** Ten metrics reviewed weekly and used to drive decisions produce more value than fifty metrics reviewed never. Every metric you add dilutes attention from the metrics that matter. If you cannot describe the specific action you would take when a metric crosses a threshold, you do not need that metric.

2. **A bad metric is worse than no metric.** Metrics that incentivize the wrong behavior are actively harmful. They will be optimized for — developers are rational agents who respond to incentives — and that optimization will damage the real outcomes you care about. Lines of code is the canonical example: optimizing for it produces bloated codebases.

3. **The most important metric is the one that reveals problems early.** A metric that tells you something went wrong three months ago is a post-mortem artifact. A metric that tells you something is going wrong *now* is an intervention opportunity. Rework rate is valuable because it reveals quality problems within 48 hours, not at the end of the quarter.

This guide defines three tiers of metrics. Start with Tier 1. Add Tier 2 when Tier 1 is stable and consistently below warning thresholds. Tier 3 is for organizations with dedicated analytics infrastructure and 6+ months of governance data.

---

## 2. Tier 1: Always Track

These five metrics apply to every team, regardless of size or maturity. They require no special tooling — only consistent discipline in following the session protocol and maintaining `CHANGELOG.md`.

### Tasks per Session

**Definition:** The number of meaningful tasks completed in a single AI-assisted session, as documented in `CHANGELOG.md`. A task is a discrete, scope-defined unit of work: a connector built, a bug fixed, a document updated, a test suite created. Sub-steps within a task (e.g., "created the file," "added imports") do not count separately.

**How to measure:** Count `CHANGELOG.md` entries per session. The session protocol requires each session to list completed tasks.

**Baseline:** Establish in the first two weeks before enforcing governance. Typical range without governance: 1-3 tasks per session (sessions run long, lose focus, and drift). With governance: 3-6 tasks per session (sessions are scoped, focused, and bounded).

**Target:** Not a fixed number — **consistency is the target**. A week with 8 tasks followed by a week with 1 task indicates either scope control failure (the 8-task week had tasks defined too granularly) or blocking problems (the 1-task week hit unresolved dependencies). Week-over-week variance greater than 50% is a warning sign regardless of the absolute number.

**Warning signs:**
- Consistently above 7: tasks are defined too granularly — the metric is being gamed
- Consistently below 2: scope definition is failing, sessions are unfocused, or the codebase has blockers
- High variance (>50% week-over-week): lack of session discipline or unpredictable task complexity
- Sudden drop to 0-1 for a developer who was previously at 4-5: investigate — blocked? Burned out? Struggling with a new part of the codebase?

### Rework Rate

**Definition:** The percentage of completed tasks that are redone, reverted, or substantially corrected within 48 hours. "Redone" means: a PR is reopened, a commit is reverted, a follow-up commit with "fix:" or "redo" in the message appears, or a task reappears in the next session's scope after being marked complete.

**How to measure:** Git log analysis. Count commits containing "revert", "fix:", "redo", "correct" within 48 hours of the original commit's timestamp. Compare to total tasks completed in the same period.

```bash
# Count reverts and fixes in last 30 days
git log --oneline --since="30 days ago" --grep="revert\|fix:\|redo\|correct:" -i | wc -l

# Count total tasks (approximate: count session entries in CHANGELOG)
grep -c "^## " docs/CHANGELOG.md
```

**Why this is the most important metric:** Rework rate is the single most reliable indicator of governance health. High rework means one or more of: poor prompt quality (vague scope leads to wrong output), insufficient review (bugs pass into main and are caught later), scope creep (changes extend beyond what was tested), or architectural drift (agent produces code that conflicts with patterns established elsewhere).

**Baseline:** Without governance, typical AI-assisted rework rate is 15-25%. With governance: target <10%.

**Target:** <10%. Below 5% is excellent — but note: 0% may indicate tasks are trivially easy or review standards are too low. Some rework is a sign of a team that catches its mistakes; zero rework in a complex codebase is suspicious.

**Warning signs:**
- Rising rework rate over 3+ weeks: scope definition deteriorating, review quality falling, or codebase complexity increasing without governance adaptation
- Rework consistently from one developer: coaching opportunity — check their prompt quality and review practices
- Rework clustered around a specific task type: that task type needs a better prompt template or a different model tier

### Governance Compliance

**Definition:** The percentage of sessions that follow the complete governance protocol, as evidenced by proper `CHANGELOG.md` entries. A compliant session has: timestamp, session number, model used, tasks completed, files changed, and governance files updated.

**How to measure:** Audit `CHANGELOG.md` entries. A session entry missing more than two of the required fields is non-compliant. This can be automated with a simple parser.

```bash
# Simple compliance check: does each session entry have required fields?
python scripts/check_changelog_compliance.py docs/CHANGELOG.md
```

**Baseline:** Before enforcement, expect 40-70% compliance (developers forget or skip when rushed). With governance: target >90%.

**Target:** >90%. 100% is the aspiration but rarely sustained — enforce remediation for non-compliance rather than accepting chronically low rates.

**Warning signs:**
- Compliance that peaks around review cycles and drops afterward: performative compliance, not genuine adoption. The team follows the protocol when being watched and abandons it when not
- Teams at 100% with entries that are copy-pasted boilerplate: gaming the metric. The entries exist but contain no useful information
- Sudden drop in one team: session protocol has broken down — needs immediate champion attention

### Test Coverage Delta

**Definition:** Change in test coverage percentage per session. Not the absolute coverage number — the direction of change.

**How to measure:** CI/CD report from the test runner (pytest-cov, coverage.py, Istanbul, etc.). Compare coverage percentage at session start (last commit on main) to session end (PR branch).

**Baseline:** Sessions should not decrease test coverage. A session that adds code without tests is a governance failure — it creates untested surface area that will produce bugs.

**Target:** Flat or increasing per session. A session that decreases coverage by more than 2 percentage points requires explanation in the `CHANGELOG.md` entry and remediation in the next session.

**Warning signs:**
- Steady decline over multiple sessions: agent is generating code without tests because the prompt templates do not require tests
- Sudden sharp drop: large feature added without any test suite — this is a governance failure, not a test failure
- Coverage increases but rework rate also increases: the tests are not testing the right things (testing what the code does, not what it should do)

### Cost per Session

**Definition:** Total estimated AI API cost for a session, in USD.

**How to measure:** Log to `docs/COST_LOG.md`: model used, approximate input tokens, approximate output tokens, estimated cost. Claude Code provides token usage information per session.

```markdown
| Date | Session | Model | Input Tokens | Output Tokens | Est. Cost |
|------|---------|-------|--------------|---------------|-----------|
| 2026-03-01 | 012 | sonnet | 45,000 | 12,000 | $0.31 |
| 2026-03-01 | 012 | opus | 8,000 | 3,500 | $0.38 |
```

**Baseline:** Establish in first two sessions. Typical range: $0.10-$1.00 per session depending on model mix, task volume, and context window usage.

**Target:** Not a fixed number — cost should be proportional to value delivered. A $0.80 session that ships a complete, tested feature is excellent. A $0.80 session that produces two config edits is misrouted (see [Model Routing](./model-routing.md)).

**Warning signs:**
- Cost rising without task count rising: context window is growing too large (too much context loaded), or the model is being used inefficiently (long conversations instead of focused tasks)
- High cost on simple sessions: wrong model tier — Opus being used for tasks Sonnet handles identically
- Cost spike with no explanation: unusually long session, regeneration loops (agent produced wrong output repeatedly), or unexpectedly large codebase loaded into context

---

## 3. Tier 2: Mature Teams

Track these once Tier 1 metrics are stable and consistently below their warning thresholds for at least 4 consecutive weeks. These metrics require more setup or more sophisticated analysis.

### Architecture Drift Score

**Definition:** A count of deviations between `ARCHITECTURE.md` and the actual codebase. Each deviation is one point of drift. Measured by the master agent, a review agent, or a periodic manual review.

**How to measure:** An agent (or human) scans the repository and flags patterns that contradict `ARCHITECTURE.md`: files in the wrong directory, patterns that violate stated conventions, layers that bypass stated boundaries, dependencies that should not exist.

**Target:** 0 at all times. Any non-zero score requires immediate remediation before the next session. Drift compounds — one deviation becomes the precedent for the next.

### PR Pass Rate (First Attempt)

**Definition:** The percentage of PRs that pass all CI checks (including agent review, if configured) on the first submission, without modifications required.

**How to measure:** GitHub Actions run history. Count PRs where the first CI run completes with all checks green.

**Baseline:** Without governance, typically 40-60% first-attempt pass rate. With governance: target >80%.

**Interpretation:** >95% may indicate checks are too lenient, not that code quality is exceptional. If every PR passes on first attempt, the checks are not catching anything, which means they are not providing value.

### Time to Production

**Definition:** Time from PR creation to merge to main, in hours.

**How to measure:** GitHub API — `created_at` to `merged_at` for all merged PRs.

```bash
gh pr list --state merged --limit 50 --json createdAt,mergedAt \
  --jq '.[] | "\(.createdAt) -> \(.mergedAt)"'
```

**Target:** Not a fixed number, but a **consistent** number. High variance is the problem. A team that merges in 2-4 hours consistently is healthier than one that sometimes merges in 30 minutes (rubber-stamping) and sometimes waits three days (review bottleneck).

### Prompt Quality Score

**Definition:** A qualitative rating (1-5) of the prompts used in a session, assessed by the champion during weekly review or retrospective.

**How to measure:** The champion reviews 2-3 prompts per session on three dimensions:
- Scope clarity (1-5): is it clear what can and cannot change?
- Constraint specification (1-5): are MUST NOT / MUST / SHOULD specified?
- Acceptance criteria (1-5): is "done" defined in verifiable terms?

Average the three scores.

**Baseline:** Without training, typical prompt quality is 2-3/5. With governance and shared prompt library: target >3.5/5.

**Action:** Track per developer to identify coaching opportunities. A developer consistently at 2/5 needs prompt training, not performance management.

---

## 4. Tier 3: Enterprise

These metrics require data infrastructure, automated pipelines, and dedicated analytics. Appropriate for organizations with 6+ months of governance data and dedicated platform support.

### Cost per Developer per Month

**Definition:** Total AI API spend divided by number of active developers.

**Why it matters:** Enables budget forecasting, ROI conversations with leadership, and identification of teams with unusual cost profiles — either exceptionally efficient (learn from them) or misrouted (coach them).

**Data source:** Aggregated `COST_LOG.md` entries across all teams, cross-referenced with HR system for developer count.

### AI vs. Human Defect Rate

**Definition:** The rate at which production bugs originate from AI-generated code vs. human-written code.

**Why it matters:** This is the primary evidence base for AI code quality at scale. If AI-generated code has a higher defect rate, the review process needs strengthening. If it has a lower defect rate (plausible for certain well-structured task types), this is a powerful argument for expanded adoption.

**Data source:** Production incident system + `git blame` + `Co-Authored-By` metadata in commits. Only valid if AI-generated code is systematically tagged.

**Caution:** Without consistent `Co-Authored-By` tagging, this metric cannot be calculated. Ensure tagging is in place before attempting to measure this.

### Compliance Audit Pass Rate

**Definition:** The percentage of randomly sampled sessions that pass a manual compliance audit: session protocol followed, data governance rules observed, no security violations, governance files updated correctly, human review was meaningful (not rubber-stamped).

**Why it matters:** Tier 1 governance compliance tells you whether sessions are documented. Audit pass rate tells you whether they are documented correctly and whether the underlying practices match the documentation. This is the metric that regulators care about.

**Data source:** Random sampling (5-10% of sessions per quarter) + manual review by governance lead or external auditor.

---

## 5. Anti-Metrics: The Danger Table

For every real metric, there is a vanity version that is easy to measure, satisfying to report, and dangerous to optimize for. These anti-metrics appear regularly in governance discussions and must be explicitly rejected.

| Real Metric | Vanity Version | What Gaming Looks Like | Why It's Dangerous |
|-------------|---------------|----------------------|-------------------|
| Working features delivered per sprint | Lines of code generated | Agent generates verbose, over-engineered code. Developer does not consolidate. | More lines = more maintenance, more bugs, more cognitive load |
| Rework rate (% of tasks redone) | Commits per day | Developer makes micro-commits. Each commit is trivially small. Commit count goes up, actual progress does not. | Incentivizes activity over quality |
| Onboarding time to productivity | Documentation pages generated | AI produces 50 pages of documentation. Nobody reads it. Onboarding time unchanged. | Volume of documentation without quality standard is noise |
| Features still live after 30 days | Tickets closed per sprint | Tickets closed by deferring the hard part, duplicating existing solutions, or solving symptoms not causes. | Closing a ticket is not the same as solving a problem |
| Defects caught in review | Speed of PR approval | PRs approved in under 5 minutes. Zero comments. Zero questions. | Incentivizes rubber-stamping — the opposite of meaningful review |
| Cost per working feature | Cost per session (alone) | Sessions are artificially shortened to lower cost. Quality drops. Rework increases. Net cost rises. | Optimizing session cost without tracking value delivered misses the point |

**The rule:** For every metric you report, identify its gaming vector. If you cannot describe how the metric could be gamed, you do not understand the metric well enough to use it.

---

## 6. Dashboard Design

### Weekly: Tier 1 Dashboard (Developers and Team Leads)

Updated every Monday. Takes 15 minutes to prepare from `CHANGELOG.md`, `COST_LOG.md`, and CI reports.

```markdown
# Team AI Governance — Weekly Dashboard
## Week of 2026-03-03

| Metric | This Week | Last Week | 4-Week Avg | Target | Status |
|--------|-----------|-----------|------------|--------|--------|
| Tasks/session (avg) | 4.1 | 3.9 | 4.0 | >=4.0 | On target |
| Rework rate | 7% | 12% | 9% | <10% | Improved |
| Governance compliance | 92% | 88% | 89% | >90% | On target |
| Test coverage delta | +1.2% | +0.8% | +0.7% | >=0% | Good |
| Cost/session (avg) | $0.38 | $0.45 | $0.40 | <$0.50 | Good |

### Notable Events
- Session 015: scope creep incident — three cross-layer changes in one session. Caught by champion. Remediated: session split into three follow-ups.
- Session 016: first use of /use-opus for security review. Cost: $0.82. Result: caught auth bypass edge case in token validation.
- Developer C onboarding: completed 3 supervised sessions. Certification quiz scheduled for Friday.

### Action Items
- [ ] Champion: prompt quality review with Developer A (rework rate above team avg for 3 weeks)
- [ ] Update SQL transform prompt template — current version does not specify deduplication strategy
```

### Monthly: Tier 2 Dashboard (Engineering Managers)

Updated first Monday of each month. Reviewed with the team in a 30-minute meeting.

```markdown
# Team AI Governance — Monthly Dashboard
## March 2026

### Tier 1 Summary (4-week averages)
| Tasks/Session | Rework | Compliance | Coverage Delta | Cost/Session |
|---------------|--------|------------|----------------|--------------|
| 4.0 | 9% | 89% | +0.7% | $0.40 |

### Tier 2 Metrics
| Metric | This Month | Last Month | Trend | Target |
|--------|------------|------------|-------|--------|
| Architecture drift score | 0 | 1 | Improved | 0 |
| PR first-attempt pass rate | 84% | 79% | Improving | >80% |
| Time to production (avg) | 3.2 hours | 4.1 hours | Improving | <4 hours |
| Prompt quality score (avg) | 3.8/5 | 3.5/5 | Improving | >3.5 |

### Cost Summary
- Total monthly AI cost: $47.20
- Cost/developer: $9.44
- Model breakdown: Haiku 35%, Sonnet 45%, Opus 20%
- Routing efficiency: 2 sessions flagged as mis-routed (Opus used for documentation)

### Framework Health
- CLAUDE.md last updated: 2026-02-28 (version 1.3)
- Active ADRs: 7
- Security incidents: 0
- Champion status: active, attending monthly syncs
```

### Quarterly: Tier 3 Dashboard (VPs and Leadership)

For organizations with enterprise-level metrics. Reviewed with leadership as part of quarterly business review.

```markdown
# AI Governance — Quarterly Report
## Q1 2026

### Organization Overview
| Metric | Q1 2026 | Q4 2025 | Change |
|--------|---------|---------|--------|
| Active governed teams | 8 | 3 | +167% |
| Total AI spend | $1,240 | $890 | +39% |
| Cost per developer/month | $12.40 | $14.80 | -16% |
| Org rework rate (avg) | 8.5% | 14.2% | -40% |
| Security incidents | 0 | 2 | -100% |
| Compliance audit pass rate | 94% | N/A | Baseline |

### ROI Summary
- Estimated rework hours saved: 320 hours (vs. pre-governance baseline)
- Estimated security incident cost avoided: $25,000-$50,000 (2 incidents in Q4, 0 in Q1)
- Developer satisfaction: 3.8/5 (up from 3.2/5)

### Risks and Recommendations
- 2 teams below 80% compliance — champion intervention underway
- Opus cost trending up — recommend routing audit for teams 4 and 7
- New hire onboarding gap — 3 developers started without completing certification
```

---

## 7. Dashboard Generation

Manually prepared dashboards decay. The human who maintained them leaves, the schedule slips, and the dashboard sits at last quarter's numbers while the team makes decisions based on stale data. Automated generation eliminates this failure mode.

### governance_dashboard.py

Generates `DASHBOARD.md` — a full governance dashboard from local governance files. No external dependencies, no API calls. Readable in any Markdown viewer, renderable in CI artifacts.

```bash
python3 automation/governance_dashboard.py --repo-path .
```

**What it generates:**

| Section | Source Data | Key Signals |
|---------|-------------|-------------|
| Health Score | `CLAUDE.md`, all governance files | Score/100, maturity level, missing checks |
| Session Velocity | `CHANGELOG.md` | Tasks/session trend, sparkline, avg |
| Cost Trend | `COST_LOG.md` | Cost per session, sparkline, model distribution |
| Knowledge Health | `MEMORY.md` | Last updated, freshness rating, placeholder count |
| ADR Coverage | `docs/adr/` | ADR count, list of recorded decisions |
| Sprint Progress | `PROJECT_PLAN.md` | Phase completion %, sprint goal |
| Governance Maturity | All governance files | Current level, evidence, upgrade path |

**Recommended cadence:** Run weekly via CI or manually at the start of each sprint planning session.

```yaml
# Add to .github/workflows/governance-health.yml
- name: Generate governance dashboard
  run: python3 automation/governance_dashboard.py --repo-path .
- name: Commit dashboard
  run: |
    git add DASHBOARD.md
    git commit -m "chore: update governance dashboard" || echo "No changes"
```

### cost_dashboard.py

Generates `COST_DASHBOARD.md` — a focused cost analysis from `COST_LOG.md`.

```bash
python3 automation/cost_dashboard.py --repo-path .
```

**What it generates:**

| Section | Key Signals |
|---------|-------------|
| Summary | Total cost, avg/session, cost/task, trend |
| Cost by Model | Per-model breakdown with bar charts |
| Cost by Session Type | Feature vs. security vs. architecture vs. docs |
| Cost by Time Period | Monthly trend with bar charts |
| Model Routing Efficiency | Actual vs. optimal cost, efficiency ratio, misrouted sessions |
| Recommendations | Where to switch to Haiku; where Opus is required |

**Model routing efficiency score:** Compares actual spend to estimated optimal spend given your task mix. A score of 1.0x is perfect. Scores above 1.3x indicate significant misrouting — typically Opus used for documentation or feature work that Sonnet handles equally well.

**Recommended cadence:** Run monthly before the cost review meeting. Review misrouted sessions as a team to calibrate routing decisions.

### Dashboard Template

`templates/DASHBOARD.md` provides a reference format for teams that prefer manual dashboards or want to customize the generated output. It shows all section headings, ASCII chart format, and table structures with placeholder data.

---

## 8. Collection Methods

### Git Log Analysis

Most Tier 1 metrics can be extracted from git log with basic scripting:

```bash
# Count sessions per week (CHANGELOG entries with session markers)
git log --oneline --since="7 days ago" -- docs/CHANGELOG.md | wc -l

# Count reverts and fixes in last 30 days (rework proxy)
git log --oneline --since="30 days ago" --grep="revert\|fix:\|redo" -i | wc -l

# Count total tasks completed (approximate: CHANGELOG task entries)
grep -c "\- \[x\]\|^- " docs/CHANGELOG.md

# Time between PR creation and merge
gh pr list --state merged --limit 50 --json number,createdAt,mergedAt \
  --jq '.[] | {pr: .number, hours: (((.mergedAt | fromdateiso8601) - (.createdAt | fromdateiso8601)) / 3600 | floor)}'

# PR first-attempt pass rate
gh run list --limit 100 --json conclusion,event \
  --jq '[.[] | select(.event == "pull_request")] | group_by(.conclusion) | map({(.[0].conclusion): length}) | add'
```

### CI/CD Data

- **Test coverage:** Available from coverage.py / pytest-cov report in CI artifacts
- **PR pass rate:** Available from GitHub Actions run history via `gh api`
- **Security scan results:** Available from gitleaks / trufflehog output in CI logs
- **Build time:** Available from CI timestamps — useful for detecting bloating

### Automated Dashboard Generation

A simple Python script running weekly can extract Tier 1 metrics from `CHANGELOG.md` and `COST_LOG.md`, query the GitHub API for PR data, and generate the weekly dashboard automatically:

```python
# scripts/generate_dashboard.py
"""
Generate weekly Tier 1 dashboard from governance files and GitHub API.
Run every Monday via cron or GitHub Actions.
Output: docs/dashboard/weekly-YYYY-MM-DD.md
"""
import subprocess
import json
from datetime import datetime, timedelta

def count_sessions_this_week():
    result = subprocess.run(
        ["git", "log", "--oneline", "--since=7 days ago", "--", "docs/CHANGELOG.md"],
        capture_output=True, text=True
    )
    return len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

def count_rework_this_week():
    result = subprocess.run(
        ["git", "log", "--oneline", "--since=7 days ago", "--grep=revert\\|fix:\\|redo", "-i"],
        capture_output=True, text=True
    )
    return len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

def get_pr_metrics():
    result = subprocess.run(
        ["gh", "pr", "list", "--state=merged", "--limit=20",
         "--json", "createdAt,mergedAt"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.stdout else []

# ... extend with COST_LOG.md parsing, coverage report parsing, etc.
```

At enterprise scale, pipe CI/CD data, git logs, and governance file extractions into a lightweight data store (SQLite locally, BigQuery or Databricks at scale) and generate dashboards automatically. Eliminate the "someone forgot to update the dashboard" failure mode.

---

*Related guides: [Enterprise Playbook](./enterprise-playbook.md) | [Model Routing](./model-routing.md) | [Prompt Engineering](./prompt-engineering.md) | [AI Code Quality](./ai-code-quality.md)*
