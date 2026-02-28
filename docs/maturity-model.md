# Maturity Model

The AI Governance Framework defines six maturity levels, numbered 0 through 5. Each level is a stable, coherent state — not a position on a sliding scale. You are at a level. Upgrading requires completing specific implementation steps, not gradually improving.

The model is designed for incremental adoption. Level 0 teams do not jump to Level 3. They implement Level 1, run it for a sprint, internalize what it does, then move to Level 2. Each level makes the next level more valuable.

---

## Level 0: Ad-hoc

**"Vibe coding." The agent does whatever is asked, often brilliantly, but nobody knows what was built or why.**

### The Tell-Tale Sign

You finish a session and cannot answer: "What exactly changed, and does it advance the project goal?" You reconstruct project state from git log and your own memory.

### What Is Implemented

Nothing. The agent operates from training data and the immediate conversation. No shared context across sessions. No constraints on what the agent may change. No record of intent — only git diffs.

### Files That Exist

Standard project files only: `README.md`, source code, `.gitignore`. No `CLAUDE.md`, `PROJECT_PLAN.md`, `CHANGELOG.md`, or `ARCHITECTURE.md`.

### What You Can Measure

Almost nothing, because there is no instrumentation.

| Metric | Source | Usefulness |
|--------|--------|-----------|
| Commit count | git log | Proxy for activity, not quality |
| Time to feature | Manual tracking | Only if someone remembers to track |
| Bug rate | Production incidents | Visible only after damage |

### How to Upgrade to Level 1

1. Create `CLAUDE.md` from [`templates/CLAUDE.md`](../templates/CLAUDE.md). Fill in `project_context`.
2. Create `PROJECT_PLAN.md` from the template. Add the current sprint goal and 5-8 tasks.
3. Create `CHANGELOG.md` from the template.
4. Run your next session with `/plan-session`. End it with `/end-session`.
5. Commit all three governance files.

See [getting-started.md](getting-started.md) for the complete walkthrough.

### Time Estimate

**One afternoon** — 2-4 hours for setup and the first governed session.

### Who This Fits

Every project begins here. Solo developers building hobby projects can stay at Level 0. Anyone building something they will maintain for more than a month, that another human will touch, or that has real users should move to Level 1 as soon as they start.

---

## Level 1: Foundation

**First governed sessions. The agent reads a constitution before it writes code. Sessions start with orientation and end with documented state.**

### The Tell-Tale Sign

Your agent's first action in any session is reading `PROJECT_PLAN.md` and `CHANGELOG.md`, presenting sprint status, and asking you to confirm scope. It never writes code before you say "proceed."

### What Is Implemented

- `CLAUDE.md` exists, is maintained, and the agent reads it at every session start
- Session start protocol: governance sync, sprint status, scope confirmation before code
- Session end protocol: CHANGELOG update, PROJECT_PLAN update, governance commit
- `CHANGELOG.md` updated per session with tasks, files changed, goal progress
- Git workflow: feature branches, commit message conventions, no direct pushes to main

### Files That Exist

```
project-root/
├── CLAUDE.md              # Constitution — agent reads this first
├── PROJECT_PLAN.md        # Sprint tasks, phases, progress tracking
└── CHANGELOG.md           # Session-by-session audit trail
```

### What You Can Measure

| Metric | How to measure | Target |
|--------|---------------|--------|
| Governance compliance rate | Sessions with full start/end protocol / total sessions | 100% |
| Tasks completed per session | Count from CHANGELOG entries | Trending up |
| Scope accuracy | Tasks completed that were in confirmed scope / total tasks | >80% |
| Context reconstruction time | Time from session start to first productive action | Under 5 min |

### How to Upgrade to Level 2

1. Write `docs/ARCHITECTURE.md` — describe what has been built, not the vision
2. Create your first ADR. Use [`docs/adr/ADR-000-template.md`](adr/ADR-000-template.md). Place at `docs/adr/ADR-001-your-decision.md`
3. Create `docs/MEMORY.md` for cross-session agent context
4. Add `ARCHITECTURE.md` and `MEMORY.md` to the session start file list in `CLAUDE.md`
5. Install slash commands from [`commands/`](../commands/) into `.claude/commands/`
6. Define your first sprint with explicit weekly goals in `PROJECT_PLAN.md`

### Time Estimate

**One afternoon** for setup. Ongoing cost: ~5 minutes per session for start/end protocols. This is not overhead — it is the work of maintaining context.

### Who This Fits

Every developer using AI assistance for a project they care about. Solo developers with more than a week of work ahead. Teams who have noticed their agents are inconsistent across sessions. This is the baseline below which AI development is ungoverned by definition.

---

## Level 2: Structured

**Architecture decisions are recorded. Memory persists across sessions. Agents are specialized. Sprint goals are tracked.**

### The Tell-Tale Sign

When the agent encounters a design choice, it checks `docs/adr/` before proposing an approach. It does not suggest alternatives to decisions already marked as Accepted. New team members can read the knowledge files and contribute on day one.

### What Is Implemented

- `PROJECT_PLAN.md` with explicit phases, milestones, and task dependencies
- `ARCHITECTURE.md` with current-state component descriptions
- ADRs for significant architectural decisions (`docs/adr/`)
- `MEMORY.md` for cross-session agent context
- Basic CI/CD: linting and tests on pull requests
- Sprint-based workflow with defined goals
- Slash commands: `/plan-session`, `/end-session`, `/sprint-status`, `/security-review`
- Agent role definitions: at minimum a code agent and a review agent

### Files That Exist

```
project-root/
├── CLAUDE.md
├── PROJECT_PLAN.md
├── CHANGELOG.md
├── docs/
│   ├── ARCHITECTURE.md          # Current architecture state
│   ├── MEMORY.md                # Cross-session context
│   └── adr/
│       ├── ADR-001-first-decision.md
│       └── ADR-002-second-decision.md
├── .claude/
│   └── commands/
│       ├── plan-session.md
│       ├── end-session.md
│       ├── sprint-status.md
│       └── security-review.md
└── .github/
    └── workflows/
        └── ci.yml               # Lint + tests
```

### What You Can Measure

| Metric | How to measure | Target |
|--------|---------------|--------|
| ADR coverage | Decisions with ADRs / significant decisions made | >80% |
| Architecture drift | New components not in ARCHITECTURE.md | 0 |
| Sprint goal completion | Goals fully completed / sprints run | >70% |
| Test coverage | CI/CD report | >50%, trending up |
| Rework rate | Tasks redone / total tasks | <15% |

### How to Upgrade to Level 3

1. Install pre-commit hooks from [`ci-cd/pre-commit/.pre-commit-config.yaml`](../ci-cd/pre-commit/.pre-commit-config.yaml): secret scanning, naming validation, hardcoded path detection
2. Add AI PR review from [`ci-cd/github-actions/ai-pr-review.yml`](../ci-cd/github-actions/ai-pr-review.yml) to GitHub Actions
3. Add governance file check: CI fails if code changed but CHANGELOG was not updated
4. Configure branch protection on main: require PR, CI pass, human approval
5. Create `docs/COST_LOG.md` and add cost tracking to the session end protocol
6. Add security scan to session start in `CLAUDE.md`

### Time Estimate

**One focused day** spread across a sprint. ADRs, ARCHITECTURE.md, MEMORY.md: 2-4 hours. Slash commands: 30 minutes. CI/CD: 1-2 hours.

### Who This Fits

Teams past the experimental phase. Projects with deliberate architectural decisions worth protecting. Developers who have experienced "the agent proposed the same thing we rejected three weeks ago" and want to prevent it. Solo projects that feel like real engineering, not just fast prototyping.

---

## Level 3: Enforced

**Governance has teeth. CI/CD rejects ungoverned changes. Pre-commit hooks catch secrets before they enter history. AI reviews every PR against the constitution.**

### The Tell-Tale Sign

A developer tries to merge a PR without updating CHANGELOG. CI blocks it. A hardcoded path in a Python file is caught by the pre-commit hook before it ever reaches a commit. The AI reviewer posts a WARN on a naming convention violation before the human reviewer opens the PR. Governance is a system, not a discipline.

### What Is Implemented

- Pre-commit hooks: secret scanning, naming validation, hardcoded path detection
- GitHub Actions with four tiers: syntax/structure, tests, AI review, human review
- AI PR review posting PASS/WARN/FAIL with specific line comments
- Governance file check: code changes without CHANGELOG update fail CI
- Branch protection: no direct pushes, CI pass required, human approval required
- Automated security scanning on every PR
- `COST_LOG.md` with per-session cost tracking
- Security scan as part of session protocol

### Files That Exist

Everything from Level 2, plus:

```
project-root/
├── .pre-commit-config.yaml       # Hooks: secrets, naming, paths
├── docs/
│   └── COST_LOG.md               # Per-session cost tracking
└── .github/
    └── workflows/
        ├── ci.yml                 # Tier 1+2: lint, type check, tests
        ├── ai-review.yml          # Tier 3: AI code review
        ├── security-scan.yml      # Secret and PII scanning
        └── governance-check.yml   # Governance file update validation
```

### What You Can Measure

| Metric | How to measure | Target |
|--------|---------------|--------|
| AI review pass rate (first try) | PRs passing on first submission / total | >75% |
| Pre-commit rejection rate | Commits rejected / total attempts | Trending to 0 |
| Security findings | Secrets/PII found per scan | 0 |
| Governance compliance (enforced) | PRs blocked for missing updates | 0 (now enforced) |
| Cost per session | COST_LOG.md | Tracked |
| Test coverage | CI/CD | >60% |

### Additional Capabilities at Level 3

**Adversarial audit** ([/audit](../commands/audit.md)): run the red team auditor agent to verify that your governance mechanisms actually catch what they are supposed to catch. A governance system that has never been tested is a hypothesis, not a defense. Run `/audit` after Level 3 setup to generate the first evidence-based pass rate. See [docs/adversarial-audit.md](adversarial-audit.md).

**Kill switch**: configure the kill switch triggers in CLAUDE.md. At Level 3, agents are making more consequential changes. The kill switch prevents cascade failures and blast radius overruns. See [docs/kill-switch.md](kill-switch.md).

### How to Upgrade to Level 4

1. Build a quality metrics dashboard — even a Markdown file aggregating CHANGELOG data
2. Configure a master agent (read-only, full project context) for PR review
3. Implement model routing: routing table in `CLAUDE.md`, agent flags task-model mismatches
4. Achieve test coverage >70%
5. Define multi-agent specialization: at minimum code agent and review agent with distinct scopes

### Time Estimate

**One sprint** (1-2 weeks). Pre-commit hooks: 30 minutes. GitHub Actions: 2-4 hours. Branch protection: 15 minutes. Front-loaded investment; enforcement then runs automatically.

### Who This Fits

Teams shipping to production. Projects with security or compliance requirements. Any codebase where an unreviewed commit with a hardcoded secret would be a serious problem. This is where governance transitions from "discipline that requires remembering" to "system that enforces itself."

The HealthReporting project reached Level 3 from Level 0 in two weeks.

---

## Level 4: Measured

**You know your AI productivity number. Architecture drift is detected automatically. Quality metrics drive decisions.**

### The Tell-Tale Sign

You can answer the question: "How much faster is AI making us, and at what quality?" You have a dashboard showing session productivity, cost trends, test coverage, and drift score. You optimize deliberately based on data, not intuition.

### What Is Implemented

- Automated quality metrics dashboard
- Master agent on all PRs with full project context (CLAUDE.md + ARCHITECTURE.md + all ADRs)
- Automatic drift detection: master agent flags code diverging from documented patterns
- Multi-agent specialization: code, review, security, test, docs, cost agents with explicit boundaries
- Model routing: routing table in `CLAUDE.md`, agent flags mismatches
- Test coverage >70%
- Cost optimization: actual vs. optimal routing cost, monthly review

### Files That Exist

Everything from Level 3, plus:

```
project-root/
├── docs/
│   ├── metrics-dashboard.md      # Auto-generated quality metrics
│   └── DECISIONS.md              # Non-ADR decision log
├── agents/
│   ├── code-agent.md
│   ├── review-agent.md
│   ├── security-agent.md
│   ├── docs-agent.md
│   └── cost-agent.md
└── .github/
    └── workflows/
        └── master-review.yml     # Master agent full-context review
```

### What You Can Measure

| Metric | How to measure | Target |
|--------|---------------|--------|
| Architecture drift score | Deviations flagged by master agent | 0 per sprint |
| Model routing efficiency | Actual cost / optimal routing cost | <1.3x |
| Master agent accuracy | Correct flags / total flags | >85% |
| Governance overhead | Governance time / total development time | <10% |
| Test coverage | CI/CD | >70% |
| Cost per feature | COST_LOG / features per sprint | Tracked, declining |

### Additional Capabilities at Level 4

**Knowledge lifecycle management**: after 20+ sessions, MEMORY.md accumulates stale context that degrades output quality. Implement the knowledge decay protocol — category-based lifespans, automatic compression, archival to MEMORY_ARCHIVE.md, and a hard 200-line cap. See [docs/knowledge-lifecycle.md](knowledge-lifecycle.md).

**Session replay**: enable `.session-logs/` generation at session end. Post-incident investigation becomes tractable when session logs capture the decision chain, context used, and confidence scores. See [docs/session-replay.md](session-replay.md).

**Automation bias defense**: with multiple validation agents active, configure explicit uncertainty surfacing (agents list what they did NOT check), enforce the 85% confidence ceiling, and establish periodic unassisted review sessions. See [docs/automation-bias.md](automation-bias.md).

### How to Upgrade to Level 5

1. Create org-level `CLAUDE.md` at `~/.claude/CLAUDE.md` for cross-repo rules
2. Define output contracts for your 3 most common task types — see [patterns/output-contracts.md](../patterns/output-contracts.md)
3. Implement cross-repo governance: master agent reading governance files across repositories
4. Activate the research pipeline: configure research-agent and schedule weekly scans
5. Build compliance audit trail: every AI decision with documented human approval
6. Define role-based agent access: capabilities governed by developer role

### Time Estimate

**One quarter** (2-3 months). Metrics dashboard: one sprint. Multi-agent specialization: 1-2 sprints. Test coverage improvement depends on existing state.

### Who This Fits

Teams running Level 3 for at least a sprint who want to move from reactive (catching problems) to proactive (detecting drift before it compounds). Engineering managers wanting visibility without manual reporting. Projects with pre-governance technical debt needing systematic detection.

---

## Level 5: Self-Optimizing

**The framework improves itself. Org-level governance cascades to every repo. Compliance audit trails are complete. Retrospectives generate governance improvements automatically.**

### The Tell-Tale Sign

After each sprint, a meta-agent analyzes session patterns and proposes specific CLAUDE.md improvements. Governance rules that are consistently ignored get flagged for removal. New developers run their first governed session within hours of joining. The framework produces less friction today than it did three months ago, despite handling more complexity.

### What Is Implemented

- Org-level `CLAUDE.md` cascading to all repositories
- Cross-repo governance: master agent monitoring multiple repos for consistency
- Complete compliance audit trail: every AI decision, every human approval, structured for external audit
- Role-based agent access: capabilities governed by developer role and seniority
- Automated retrospectives: meta-agent analyzes patterns and proposes improvements
- Research pipeline: automated scanning of AI governance sources for new patterns, weekly findings report
- Output contracts: defined for all major task types, validated by quality gate agent on every session
- Self-updating: /upgrade command checks for framework updates quarterly; CLAUDE.md changes always require human review
- Real-time governance dashboard: progress, cost attribution, quality trends, compliance status
- Full cost attribution: per developer, per team, per project, per sprint

### Files That Exist

Everything from Level 4, plus:

```
~/.claude/
└── CLAUDE.md                      # Org-level constitution

org-governance-repo/
├── CLAUDE.md                      # Org-level source of truth
├── policies/
│   ├── security-constitution.md
│   ├── data-governance.md
│   └── compliance-trail.md
├── agents/
│   └── master-agent-org.md        # Cross-repo master agent
├── dashboards/
│   └── governance-dashboard.md
├── patterns/                          # Quality control patterns
│   ├── dual-model-validation.md
│   ├── output-contracts.md
│   └── [other patterns]
└── automation/
    ├── framework_updater.py
    ├── best_practice_scanner.py
    └── health_score_calculator.py
```

### What You Can Measure

| Metric | How to measure | Target |
|--------|---------------|--------|
| Cross-repo consistency | Deviations flagged by org master agent | <5 per sprint |
| Compliance audit readiness | AI decisions with human approval documented | 100% |
| Framework improvement rate | CLAUDE.md improvements per quarter | >3 |
| AI cost per developer per month | Aggregated COST_LOG | Within budget |
| Onboarding time | Time to first governed session | <1 day |
| Governance overhead (org-wide) | Governance time / total development time | <8% |

### Additional Capabilities at Level 5

**Constitutional inheritance**: implement the org → team → repo hierarchy. Org-level security rules cascade automatically. Teams extend without weakening. Compliance can be audited at the org level. See [docs/constitutional-inheritance.md](constitutional-inheritance.md) and [templates/CLAUDE.org.md](../templates/CLAUDE.org.md).

**Adaptive friction**: measure governance overhead per session. Apply the friction budget model — if governance overhead exceeds 15 minutes per session, developers will route around it via shadow AI. Track and reduce friction as the framework matures. See [docs/governance-fatigue.md](governance-fatigue.md).

**Anti-fragile feedback loops**: every production incident that slipped through governance gets a new deterministic check. The framework tightens automatically in response to real failures. Adversarial audits run quarterly at minimum. Governance maturity is demonstrated by evidence, not assertion.

### Beyond Level 5

Level 5 is a stable state, not a final destination. Beyond it, improvements are incremental:

- Custom tooling for your specific domain (specialized agents per tech stack)
- Automated model routing (not just flagged, but switched automatically)
- Integration with external compliance systems (SOX, HIPAA, ISO 27001)
- AI-assisted retrospectives proposing team process changes, not just CLAUDE.md changes

### Time Estimate

**3-6 months** from Level 4, assuming Level 4 has been stable for at least one quarter. Requires organizational buy-in beyond a single team. Compliance audit trails need coordination with security and legal.

### Who This Fits

Engineering organizations at scale (50+ developers) where AI adoption is happening across multiple teams. CTOs needing compliance documentation for AI-assisted development. Regulated industries (healthcare, finance, government) with specific audit requirements. Organizations that have experienced the cost of inconsistent governance across teams.

---

## Self-Assessment

Answer these 10 questions based on what is consistently happening, not what happened once or what you intend to implement. A protocol that ran 4 times out of 10 is Level 0 with occasional governance.

1. **Does your `CLAUDE.md` contain a session protocol with explicit start/end phases, and does it have a last-reviewed date within the past 30 days?**

2. **Does the agent confirm scope with you before writing any code in every session — not most sessions, every session?**

3. **Is `CHANGELOG.md` updated after every session with specific file paths, task outcomes, and progress percentages — not just a vague summary?**

4. **Do ADRs exist for your significant architectural decisions, and do they include Status, Context, Decision, Consequences, and Alternatives Considered?**

5. **Does your CI/CD pipeline block PRs that change code files but do not include a governance file update?**

6. **Does an AI agent review every pull request against your `CLAUDE.md` rules and `ARCHITECTURE.md` before human review begins?**

7. **Do pre-commit hooks prevent secrets, hardcoded paths, and naming violations from entering git history — and have you verified this by testing with an intentional violation?**

8. **Do you track AI API cost per session in a dedicated file, and can you state your AI spend for the last two weeks without looking it up?**

9. **Can a new developer (or a fresh Claude Code session) read your governance files and produce architecturally consistent code without any verbal context — and has this actually been tested?**

10. **Is there a defined, PR-based process for changing `CLAUDE.md`, and has the framework been reviewed and improved within the last 30 days?**

### Scoring

| Score | Level | Interpretation |
|:-----:|:-----:|---------------|
| 0-1 | Level 0 | No governance. Start with [getting-started.md](getting-started.md). |
| 2-3 | Level 1 | Foundation in place, incomplete. Finish the Level 1 checklist. |
| 4-5 | Level 2 | Structured but unenforced. Add ADRs and enforcement. |
| 6-7 | Level 3 | Partial enforcement. Close the CI/CD gaps. |
| 8-9 | Level 4 | Strong measurement. Add master agent and metrics dashboard. |
| 10 | Level 5 | Full governance. Focus on evolution and cross-repo consistency. |
