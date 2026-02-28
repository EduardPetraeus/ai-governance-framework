# Metrics Guide: What to Measure and What Not to Measure

## 1. The Measurement Principle

Measure outcomes, not activity.

This distinction sounds obvious and is routinely ignored. The reason it gets ignored is that activity is easy to count and outcomes are hard to define. AI development amplifies this problem: agents generate enormous amounts of measurable activity — commits, lines of code, tasks, sessions — and almost none of it correlates with the outcomes that matter to the business.

The measurement principle has three corollaries:

1. **Fewer metrics, measured consistently, acted upon.** Ten metrics reviewed monthly produce more value than fifty metrics reviewed never.
2. **A bad metric is worse than no metric.** Metrics that incentivize the wrong behavior are actively harmful. They will be optimized for, and that optimization will damage the real outcomes you care about.
3. **The most important metric is the one that reveals problems early.** A metric that tells you something went wrong three months ago is not useful. A metric that tells you something is going wrong now is.

This guide defines three tiers of metrics. Start with Tier 1. Add Tier 2 when Tier 1 is stable. Tier 3 is for organizations with dedicated analytics infrastructure.

---

## 2. Tier 1: Always Track

These five metrics apply to every team, regardless of size or maturity. They require no special tooling — only consistent discipline in following the session protocol.

### Tasks per Session

**Definition**: The number of meaningful tasks completed in a single AI-assisted session, as documented in `CHANGELOG.md`.

**How to measure**: Count `CHANGELOG.md` entries per session. A task is a discrete, scope-defined unit of work (a connector built, a bug fixed, a document updated). Sub-steps within a task do not count separately.

**Baseline**: Establish in the first two weeks before enforcing governance. Typical range without governance: 1–3 tasks per session (sessions run long and lose focus). With governance: 3–6 tasks per session.

**Target**: The target is not a fixed number — it is consistency. Variance is the warning sign. A week with 8 tasks followed by a week with 1 task indicates either scope control failure (the 8-task week) or blocking problems (the 1-task week).

**Warning signs**:
- Consistently above 7: tasks are defined too granularly (gaming the metric)
- Consistently below 2: scope definition is failing or sessions are running unfocused
- High variance (>50% week-over-week): lack of session discipline

### Rework Rate

**Definition**: The percentage of completed tasks that are redone within 48 hours. "Redone" means a PR is reopened, reverted, or substantially replaced.

**How to measure**: Git log analysis. Count commits that contain "revert", "fix:", or "redo" within 48 hours of the original commit. Compare to total tasks completed.

**Baseline**: Without governance, typical AI-assisted rework rate is 15–25% (agent output not reviewed thoroughly, scope creep causing partial solutions). With governance target: <10%.

**Target**: <10%. Below 5% is excellent. Note: a rework rate of 0% may indicate tasks are too simple or review standards are too low.

**Warning signs**:
- Rising rework rate: scope definition deteriorating, review quality falling, or agent output quality dropping
- Rework always from the same developer: coaching opportunity
- Rework clustered around specific task types: that task type needs better prompt templates

### Governance Compliance

**Definition**: The percentage of sessions that follow the complete start/end protocol, as evidenced by a proper `CHANGELOG.md` entry.

**How to measure**: Audit `CHANGELOG.md` entries. A compliant session has: timestamp, session number, phase, model used, tasks completed, files changed. An entry missing more than two of these fields is non-compliant.

**Baseline**: Before enforcement, expect 40–70% compliance (developers forget or skip when rushed). With governance target: >90%.

**Target**: >90%. 100% is the goal but rarely achieved — enforce consequences for non-compliance rather than accepting chronic low rates.

**Warning signs**:
- Compliance that peaks around review cycles and drops afterward: performative compliance, not genuine adoption
- Teams that are 100% compliant but have no useful content in entries: gaming with boilerplate
- Sudden drop in one team: session protocol has broken down, needs immediate champion attention

### Test Coverage Delta

**Definition**: Change in test coverage percentage per session. Not the absolute coverage number — the direction of change.

**How to measure**: CI/CD report from the test runner (pytest-cov, coverage.py, etc.). Compare coverage percentage at session start (last commit on main) to session end (PR branch).

**Baseline**: Sessions should not decrease test coverage. A session that adds code without tests is a governance failure.

**Target**: Coverage should be flat or increasing per session. A session that significantly decreases coverage (>2 percentage points) requires explanation and remediation.

**Warning signs**:
- Steady decline over multiple sessions: agent is generating code without tests; prompt templates need to include test requirements
- Sudden sharp drop: large feature added without test suite
- Coverage fluctuates without trend: inconsistent test discipline

### Cost per Session

**Definition**: Total estimated AI API cost for a session, in USD.

**How to measure**: Log to `docs/COST_LOG.md` — model used, input tokens, output tokens, estimated cost. Claude Code provides token counts per session.

**Baseline**: Establish in first two sessions. Typical range: $0.10–$1.00 per session depending on model mix and task volume.

**Target**: Not a fixed number — cost should be proportional to value delivered. A $0.80 session that ships a complete feature is excellent. A $0.80 session that produces two config edits is not.

**Warning signs**:
- Cost rising without task count rising: context window is growing too large (too much context loaded per session), or model is being used inefficiently
- High cost on simple sessions: wrong model tier being used (see [Model Routing](./model-routing.md))
- Cost spike: unusually long session or unexpectedly large output — investigate

---

## 3. Tier 2: Mature Teams

Track these once Tier 1 metrics are stable and consistently below their warning thresholds. These metrics require additional tooling or more sophisticated analysis.

### Architecture Drift Score

**Definition**: A count of deviations from `ARCHITECTURE.md` detected in the codebase. Measured by the master agent or a periodic manual review.

**How to measure**: Master agent or review agent scans the repository and flags patterns that contradict `ARCHITECTURE.md`. Each flag is one point of drift. Score of 0 is clean.

**Baseline**: 0 drift is the starting point. Drift accumulates when sessions introduce changes without updating `ARCHITECTURE.md`, or when agents misinterpret architectural constraints.

**Target**: 0 at all times. Any non-zero score requires immediate remediation before the next session.

### PR Pass Rate (First Attempt)

**Definition**: The percentage of PRs that pass all CI checks (including agent review) on the first submission, without changes required.

**How to measure**: GitHub Actions / CI dashboard. Count PRs where the first CI run is fully green.

**Baseline**: Without governance, typically 40–60% first-attempt pass rate. With governance target: >80%.

**Target**: >80%. Higher targets (>95%) may indicate checks are too lenient, not that code quality is extremely high.

### Time to Production

**Definition**: Time from PR creation to merge to main, in hours.

**How to measure**: GitHub API — `created_at` to `merged_at` for all merged PRs.

**Baseline**: Without governance, PR reviews are inconsistent; time to production varies widely. Target range depends on organization culture but should be measurable and improving.

**Target**: Not a fixed number, but a consistent number. High variance is the problem. A team that merges in 2–4 hours consistently is healthier than one that sometimes merges in 30 minutes and sometimes waits three days.

### Prompt Quality Score

**Definition**: A qualitative rating (1–5) of the prompts used in a session, assessed by the champion during retrospective.

**How to measure**: After each session, the champion or the developer rates the session's prompts on:
- Scope clarity (1–5)
- Constraint specification (1–5)
- Acceptance criteria (1–5)
- Average the three scores

**Baseline**: Without training, typical prompt quality is 2–3/5. With governance and training target: >3.5/5.

**Target**: >3.5/5 consistently. Track per developer to identify coaching opportunities.

---

## 4. Tier 3: Enterprise

These metrics require data infrastructure, automated pipelines, and dedicated analytics. Appropriate for organizations that have been running AI governance for 6+ months.

### Cost per Developer per Month

**Definition**: Total AI API spend divided by number of active developers.

**Why it matters**: Enables budget forecasting, ROI conversations with leadership, and identification of teams with unusual cost profiles (potentially indicating misuse or exceptional productivity).

**Data source**: Aggregated `COST_LOG.md` entries across all teams + HR system for developer count.

### AI vs. Human Defect Rate

**Definition**: The rate at which bugs are found in production that originated from AI-generated code vs. human-written code.

**Why it matters**: The primary evidence base for AI code quality at scale. If AI-generated code has a higher defect rate, the review process needs strengthening. If it has a lower defect rate (plausible for certain task types), this is a powerful argument for expanded adoption.

**Data source**: Production incident system + git blame + `Co-Authored-By` metadata in commits.

**Caution**: This metric is only valid if AI-generated code is systematically tagged. Without tagging, you cannot separate AI from human defects.

### Compliance Audit Pass Rate

**Definition**: The percentage of randomly sampled sessions that pass a manual compliance audit (session protocol followed, data governance rules observed, no security violations, governance files updated).

**Why it matters**: Tier 1 governance compliance tells you whether sessions are documented. Audit pass rate tells you whether they are documented correctly and whether the underlying practices match the documentation.

**Data source**: Random sampling + manual review by governance lead or external auditor.

---

## 5. Anti-Metrics: What Not to Optimize

These metrics appear in governance discussions regularly and should be explicitly rejected. Each has a "vanity" version that is easy to measure and dangerous to optimize, and a "real" version that is harder to measure but actually meaningful.

### Lines of Code

**Vanity version**: Total lines of code generated per session.
**The danger**: AI inflates this effortlessly. More lines of code means more code to maintain, more potential bugs, more cognitive load for future developers. Optimizing for this metric produces bloated, over-engineered codebases.
**Real metric**: Working features delivered per sprint.

### Content Volume

**Vanity version**: Number of documentation pages, CHANGELOG entries, or commit messages generated.
**The danger**: AI can produce documentation at industrial scale. Quantity of documentation with no quality standard produces noise that reduces signal. Developers stop reading documentation that is 80% boilerplate.
**Real metric**: Onboarding time for new developers (how long until they can work independently using the documentation that exists).

### Tickets Closed

**Vanity version**: Number of tasks or tickets closed per sprint.
**The danger**: Closing a ticket by deferring the hard part, duplicating an existing solution, or solving a symptom rather than the root cause is activity without value.
**Real metric**: Bugs prevented (defect rate trend), or features shipped that are still live and used after 30 days.

### Commits per Day

**Vanity version**: Number of git commits, measured daily.
**The danger**: AI generates enormous commit volumes. Tracking commits incentivizes micro-commits and session fragmentation. A developer who commits 40 times in a session is not more productive than one who commits 4 times.
**Real metric**: Rework rate (the inverse of commit quality — fewer reverts means commits were right the first time).

---

## 6. Dashboard Design

### Weekly: Tier 1 Dashboard

Updated every Monday, covering the previous week. Takes 15 minutes to prepare from `CHANGELOG.md` and CI reports.

```markdown
# Team AI Governance — Weekly Dashboard
## Week of [date]

| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|--------|
| Tasks/session (avg) | 4.1 | 3.9 | ≥4.0 | OK |
| Rework rate | 7% | 12% | <10% | OK |
| Governance compliance | 92% | 88% | >90% | OK |
| Test coverage (avg delta) | +1.2% | +0.8% | ≥0% | OK |
| Cost/session (avg) | $0.38 | $0.45 | <$0.50 | OK |

### Notable events
- Session 015: scope creep incident — three cross-layer changes in one session. Remediated.
- Session 016: first use of /use-opus for security review. Cost: $0.82. Result: caught auth bypass edge case.

### Next week focus
- Champion to run prompt quality review with Developer A (rework rate above team average)
```

### Monthly: Tier 2 Dashboard

Updated first Monday of each month. Reviewed with the team.

```markdown
# Team AI Governance — Monthly Dashboard
## [Month, Year]

### Tier 1 Summary
[Four-week average of all Tier 1 metrics]

### Tier 2 Metrics
| Metric | This Month | Last Month | Trend |
|--------|------------|------------|-------|
| Architecture drift score | 0 | 0 | Stable |
| PR first-attempt pass rate | 84% | 79% | Improving |
| Time to production (avg) | 3.2 hours | 4.1 hours | Improving |
| Prompt quality score (avg) | 3.8/5 | 3.5/5 | Improving |

### Cost summary
- Total monthly AI cost: $[X]
- Cost/developer: $[X]
- Model breakdown: Haiku [X]%, Sonnet [X]%, Opus [X]%

### Framework health
- CLAUDE.md last updated: [date]
- Active ADRs: [N]
- Security incidents: [N]
```

### Quarterly: Tier 3 Dashboard

For organizations with enterprise-level metrics infrastructure. Reviewed with leadership.

---

## 7. Collection Methods

### Git Log Analysis

Most Tier 1 metrics can be extracted from git log with basic scripting:

```bash
# Sessions per week (count CHANGELOG entries)
git log --oneline --since="7 days ago" | grep "docs: update project state"

# Rework rate (reverts in last 30 days)
git log --oneline --since="30 days ago" | grep -i "revert\|fix:\|redo"

# Time between PR creation and merge (requires GitHub API)
gh pr list --state merged --limit 50 --json createdAt,mergedAt
```

### CI/CD Data

- Test coverage: available from coverage.py report in CI artifacts
- PR pass rate: available from GitHub Actions run history
- Security scan results: available from gitleaks / trufflehog output in CI logs

### Manual Session Logs

The `CHANGELOG.md` session format contains the raw data for most Tier 1 metrics:

```markdown
## 2026-03-01 — Session 012
**Model:** claude-sonnet-4-6
**Duration:** ~2 hours
**Tasks completed:** 4/4
**Files changed:** 7
**Est. cost:** $0.38
```

Consistent format is essential for automated extraction. Define the exact format in `CLAUDE.md` and enforce it.

### Automating Collection

A simple Python script running weekly can extract Tier 1 metrics from `CHANGELOG.md` and generate the weekly dashboard automatically. This eliminates the manual overhead and removes the "it depends on someone remembering to fill it in" failure mode.

At enterprise scale, pipe CI/CD data, git logs, and `CHANGELOG.md` extractions into a lightweight data store (SQLite locally, BigQuery at scale) and generate dashboards automatically.

---

*Related guides: [Productivity Measurement](./productivity-measurement.md) | [Enterprise Playbook](./enterprise-playbook.md) | [Model Routing](./model-routing.md)*
