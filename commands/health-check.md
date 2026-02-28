# /health-check

Full assessment of governance health in the current repository. This command answers: "How well is governance actually working in this project, and what should I fix next?"

Unlike `/validate` (which checks the last task), `/health-check` evaluates the entire governance setup: file completeness, enforcement configuration, quality control, agent and command coverage, and progress since the last health check. It produces a scored report with ranked recommendations.

## Usage

```
/health-check
```

No arguments needed. The command reads all governance files and produces a comprehensive assessment.

## Steps

### Step 1: Activate drift detection

Invoke the [drift-detector-agent](../agents/drift-detector-agent.md) to scan all governance files. The drift detector checks 8 dimensions:

1. CLAUDE.md completeness (required sections, line count, critical rules placement)
2. Session protocol compliance (CHANGELOG freshness, PROJECT_PLAN currency, governance commits)
3. Security configuration (.gitignore, forbidden list, pre-commit hooks, CI/CD security)
4. Agent availability (referenced agents exist with real content)
5. Command availability (referenced commands exist with real content)
6. ADR coverage (significant decisions have ADRs with maintained statuses)
7. Memory freshness (MEMORY.md and ARCHITECTURE.md are current)
8. Cross-reference validity (all relative links resolve to existing files)

See [agents/drift-detector-agent.md](../agents/drift-detector-agent.md) for the full check specifications and scoring methodology.

### Step 2: Assess maturity level

Compare the project's implemented governance against the maturity model criteria in [docs/maturity-model.md](../docs/maturity-model.md):

**Level 1 criteria:**
- CLAUDE.md exists and has project_context, conventions, session protocol, security rules
- PROJECT_PLAN.md exists with a current sprint goal and task tracking
- CHANGELOG.md exists with recent session entries
- Session start and end protocols are being followed (evidence in CHANGELOG)

**Level 2 criteria:**
- ARCHITECTURE.md exists with current-state descriptions
- ADRs exist for significant architectural decisions
- MEMORY.md exists for cross-session context
- Slash commands installed: /plan-session, /end-session, /status, /security-review
- At least 2 agent definitions with distinct roles

**Level 3 criteria:**
- Pre-commit hooks configured (secret scanning, naming validation)
- CI/CD pipeline includes governance checks
- AI PR review configured and running
- Branch protection enabled
- COST_LOG.md tracking session costs

**Level 4 criteria:**
- Quality metrics dashboard exists
- Master agent configured for PR review
- Model routing defined
- Test coverage above 70%
- Multi-agent specialization (3+ agents with explicit scope boundaries)

**Level 5 criteria:**
- Org-level CLAUDE.md exists
- Cross-repo governance monitoring
- Compliance audit trail
- Role-based agent access
- Automated retrospectives

Assign the highest level where ALL criteria are met. Partial implementation of a higher level is noted but does not count.

### Step 3: Calculate health score

Use the drift detector's scoring:
- Start at 100
- Each CRITICAL dimension: -20
- Each DEGRADED dimension: -8
- Each specific CRITICAL drift item beyond the dimension score: -5
- Each specific WARNING drift item beyond the dimension score: -2
- Minimum score: 0

Adjust the score with judgment: a single critical gap (e.g., no .gitignore in a production project) can justify a lower score than the formula produces.

### Step 4: Rank recommendations by impact

For each identified gap, estimate the score improvement that fixing it would produce. Rank recommendations by:
1. Score impact (how many points fixing this would add)
2. Effort required (time estimate for the fix)
3. Risk reduction (does this close a security or compliance gap?)

Present the top 5 recommendations. For each, include:
- Expected score improvement
- Estimated effort
- Specific file reference or command to use
- Why this recommendation ranks where it does

### Step 5: Show progress since last health check

Search CHANGELOG.md for previous health check entries (entries containing "health check" or "governance health"). If a previous health check exists:
- Compare the current score to the previous score
- Note which previous recommendations were implemented
- Note which previous recommendations are still open

If no previous health check exists, skip this section.

### Step 6: Produce the report

Compile all findings into the output format below.

## Output Format

```
Governance Health Check
==========================
Project: [project name from CLAUDE.md or PROJECT_PLAN.md]
Date: [current date]
Level assessment: Level [N] -- [level name]

Score: [N]/100

Governance files:
[status] CLAUDE.md: [detail]
[status] PROJECT_PLAN.md: [detail]
[status] CHANGELOG.md: [detail]
[status] ARCHITECTURE.md: [detail]
[status] MEMORY.md: [detail]

Enforcement:
[status] Pre-commit hooks: [detail]
[status] Branch protection: [detail]
[status] AI PR review: [detail]
[status] Governance file check: [detail]

Quality control:
[status] Output contracts: [detail]
[status] Tests: [detail]
[status] Security scan: [detail]

Agents configured: [N]/[total available] ([list of configured agents])
Commands configured: [N]/[total available] ([list of configured commands])

Top 5 recommendations (ranked by impact):
1. [+N pts] [recommendation] ([effort estimate], see [file reference])
2. [+N pts] [recommendation] ([effort estimate], see [file reference])
3. [+N pts] [recommendation] ([effort estimate], see [file reference])
4. [+N pts] [recommendation] ([effort estimate], see [file reference])
5. [+N pts] [recommendation] ([effort estimate], see [file reference])

Run again after implementing recommendations to track progress.
```

Use these status indicators:
- Pass: green checkmark description
- Warning: warning description with specifics
- Fail: red X description with specifics

## Rules

- Always run the full check. Do not skip dimensions because "they were fine last time." Governance can degrade between checks.
- Always produce the complete report format. Never abbreviate or skip sections. An incomplete health check is worse than none because it creates false confidence.
- Every recommendation must include a specific file reference or command. "Improve test coverage" is not actionable. "Increase test coverage from 31% to 50% by adding tests for src/connectors/ (see patterns/output-contracts.md for test contract patterns)" is actionable.
- Score interpretation must be honest. If governance is in poor shape, say so. A health check that always reports "good enough" teaches the team to ignore it.
- If the project scores above 90, acknowledge the good governance explicitly. Positive reinforcement encourages continued maintenance.
- If the project scores below 50, recommend a dedicated governance remediation session before continuing feature work. Building features on degraded governance compounds the drift.
- The health check does not fix problems. It diagnoses them and ranks the fixes. The developer decides what to address and when.
- Log the health check results in CHANGELOG.md so future health checks can show progress.

---

## Example Output

```
Governance Health Check
==========================
Project: data-pipeline
Date: 2026-02-28
Level assessment: Level 2 -- Structured

Score: 68/100

Governance files:
  CLAUDE.md: 7/7 required sections present, 156 lines (within limit)
  PROJECT_PLAN.md: current sprint defined, 8 tasks tracked (3 complete, 5 planned)
  CHANGELOG.md: 14 sessions logged, consistent format, last entry is Session 014
  ARCHITECTURE.md: exists but last updated Session 008 (6 sessions ago)
  MEMORY.md: not present

Enforcement:
  Pre-commit hooks: secret scanning active and tested
  Branch protection: CI pass required, human approval required
  AI PR review: configured but failed on last 3 PRs (check .github/workflows/ai-review.yml)
  Governance file check: not configured

Quality control:
  Output contracts: none defined
  Tests: 31% coverage (target: 70%)
  Security scan: 0 findings in last 10 sessions

Agents configured: 3/6 available (code-reviewer, quality-gate-agent, drift-detector-agent)
Commands configured: 4/7 available (plan-session, end-session, status, security-review)

Top 5 recommendations (ranked by impact):
1. [+12 pts] Configure governance file check in CI -- block PRs that change code
   without updating CHANGELOG.md (30 min, see ci-cd/github-actions/governance-check.yml)
2. [+8 pts] Define output contracts for top 3 task types -- connector builds, transforms,
   and test suites (2 hrs, see patterns/output-contracts.md)
3. [+6 pts] Create MEMORY.md to track cross-session context -- confirmed patterns, anti-
   patterns, and working tools (1 hr, see templates/MEMORY.md)
4. [+5 pts] Fix AI PR review action -- review .github/workflows/ai-review.yml logs for
   authentication or trigger configuration errors (30 min)
5. [+4 pts] Update ARCHITECTURE.md to reflect changes from Sessions 009-014 -- 3 new
   connectors and a schema change are not documented (45 min)

Previous health check: none found in CHANGELOG. This is the baseline.

Run again after implementing recommendations to track progress.
```

### Example: High-scoring project

```
Governance Health Check
==========================
Project: acme-platform
Date: 2026-02-28
Level assessment: Level 3 -- Enforced

Score: 92/100

Governance files:
  CLAUDE.md: 7/7 sections, 178 lines, security rules in first 40 lines
  PROJECT_PLAN.md: Sprint 6 active, 12 tasks (8 complete, 3 in progress, 1 planned)
  CHANGELOG.md: 42 sessions logged, last entry is Session 042 (today)
  ARCHITECTURE.md: updated Session 041 (current)
  MEMORY.md: updated Session 040 (current, within 5-session threshold)

Enforcement:
  Pre-commit hooks: secret scanning + naming validation active
  Branch protection: CI pass + human approval required on main
  AI PR review: running, 94% of PRs reviewed in last sprint
  Governance file check: active, blocked 2 PRs last sprint for missing CHANGELOG

Quality control:
  Output contracts: defined for 4 of 6 task types
  Tests: 73% coverage (above 70% target)
  Security scan: 0 findings in last 20 sessions

Agents configured: 5/6 available (code-reviewer, quality-gate-agent, drift-detector-agent,
  master-agent, research-agent)
Commands configured: 6/7 available (plan-session, end-session, status, security-review,
  prioritize, validate)

Top 5 recommendations (ranked by impact):
1. [+3 pts] Define output contracts for remaining 2 task types (documentation updates,
   ADR writing) -- brings contract coverage to 100% (1 hr, see patterns/output-contracts.md)
2. [+2 pts] Install /health-check and /upgrade commands to reach full command coverage
   (15 min, see commands/health-check.md and commands/upgrade.md)
3. [+2 pts] Add the research-agent to weekly workflow for framework currency
   (15 min, see agents/research-agent.md)
4. [+1 pt] Review CLAUDE.md for rules that are now consistently followed and could be
   removed to reduce file length from 178 to under 150 lines (30 min)
5. [+1 pt] Begin Level 4 preparation: configure quality metrics dashboard
   (2 hrs, see docs/maturity-model.md Level 4 upgrade path)

Previous health check (Session 036): Score was 84/100. Implemented recommendations 1
(pre-commit hooks), 2 (governance file check), and 4 (ARCHITECTURE.md update) from that
check. Score improved by 8 points.

Governance is in strong shape. Focus on the Level 4 upgrade path when ready.
```
