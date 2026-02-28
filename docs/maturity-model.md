# Maturity Model

The AI Governance Framework defines six maturity levels, numbered 0 through 5. Each level is a stable, coherent state — not a position on a continuous scale. You are not "between" levels; you are at a level, and upgrading requires completing specific implementation steps.

The model is designed to be implemented incrementally. Level 0 teams do not jump to Level 3. They implement Level 1, run it for a sprint, understand what it does, and then move to Level 2. The framework compounds: each level makes the next level more valuable.

---

## Level 0: Ad-hoc

**"Vibe coding." No governance. The agent does whatever is asked.**

### What's implemented

- Nothing. The agent operates from its training data and the nearest user instruction.
- No shared context across sessions — the agent re-learns the project every time.
- No constraints on what the agent may change — it modifies what it infers should be modified.
- No record of what was built — you would have to read git history to reconstruct the project state.

### Concrete files that exist

- None — or only the standard project files (`README.md`, source code, perhaps a `.gitignore`)
- No `CLAUDE.md`, `PROJECT_PLAN.md`, `CHANGELOG.md`, or `ARCHITECTURE.md`

### Metrics you can track

At Level 0, there is almost nothing to measure because there is no instrumentation. The only available signal is git commit history, which tells you what files changed but not why, what the intent was, or whether it was correct.

- **Commit count:** useful as a proxy for activity, not for quality
- **Time to working feature:** only measurable manually
- **Bug rate:** only visible after bugs surface in production

### How to upgrade to Level 1

1. Create `CLAUDE.md` from the template at [`templates/CLAUDE.md.template`](../templates/CLAUDE.md.template). Fill in the `project_context` section.
2. Create `PROJECT_PLAN.md` from the template. Add your current sprint goal and the next 5–8 tasks.
3. Create `CHANGELOG.md` from the template.
4. Run your next session using the `/plan-session` command and complete the session end with `/end-session`.
5. Commit all three governance files.

That is the complete upgrade. See [getting-started.md](getting-started.md) for step-by-step instructions.

### Estimated time to implement

**One afternoon** — 2–4 hours for initial setup and the first governed session.

### Who it's for

Every team and every project begins at Level 0. The question is how long they stay there. Solo developers building hobby projects can operate at Level 0 indefinitely. Developers building anything they will maintain for more than a month, any codebase another human will touch, or any product with real users will find Level 0 increasingly painful as the project grows.

---

## Level 1: Foundation

**First governed sessions. The agent has a constitution and follows a session protocol.**

### What's implemented

- `CLAUDE.md` exists, is maintained, and the agent reads it at every session start
- Session start protocol: agent reads governance files, presents sprint status, confirms scope before writing code
- Session end protocol: agent updates `CHANGELOG.md` and `PROJECT_PLAN.md`, proposes governance commit
- `CHANGELOG.md` updated per session with tasks completed, files changed, and goal progress
- Git-based workflow: feature branches, commit message conventions, no direct pushes to main

### Concrete files that exist

```
project-root/
├── CLAUDE.md                      # The agent's constitution
├── PROJECT_PLAN.md                # Sprint tasks, phase structure, progress tracking
└── CHANGELOG.md                   # Session-by-session audit trail
```

### Metrics you can track

At Level 1, you have enough instrumentation for the most important baseline metrics:

| Metric | How to measure | Target |
|--------|---------------|--------|
| Governance compliance rate | Sessions with complete start/end protocol ÷ total sessions | 100% |
| Tasks completed per session | Count from CHANGELOG entries | Trending up |
| Scope accuracy | Tasks completed that were in the confirmed scope | >80% |
| Session context reconstruction time | Time to productive work at session start | Under 5 minutes |

You will also notice an immediate qualitative improvement: sessions start with purpose rather than re-orientation, and you leave every session with documented state rather than wondering what was built.

### How to upgrade to Level 2

1. Write `docs/ARCHITECTURE.md` describing what has been built so far (not the vision — the current state)
2. Create your first ADR for the most significant architectural decision made to date. Use the template at [`templates/adr-template.md`](../templates/adr-template.md). Place it at `docs/adr/ADR-001-your-decision.md`.
3. Create `docs/MEMORY.md` — a running file where the agent captures decisions, patterns, and project-specific conventions discovered across sessions
4. Add `ARCHITECTURE.md` and `MEMORY.md` to the files read at session start in `CLAUDE.md`
5. Install the slash commands from [`commands/`](../commands/) into `.claude/commands/`
6. Define your first sprint with explicit week-level goals in `PROJECT_PLAN.md`

### Estimated time to implement

**One afternoon** for initial setup. The ongoing cost is approximately 5 minutes per session for the start and end protocols — this is not overhead, it is the work of maintaining project context.

### Who it's for

Every developer using AI assistance for a project they care about. Solo developers building anything with more than one week of work ahead. Teams who have already noticed that their agents are inconsistent across sessions. This is the baseline below which AI-assisted development is ungoverned by definition.

---

## Level 2: Structured

**Architecture decisions are recorded. The project has memory. Specialized agents and slash commands automate routine workflows.**

### What's implemented

- `PROJECT_PLAN.md` with explicit phases, milestones, and task dependencies
- `ARCHITECTURE.md` with current-state diagrams and component descriptions
- ADRs for significant architectural decisions (`docs/adr/`)
- `MEMORY.md` giving agents cross-session context on project-specific decisions
- Basic CI/CD: linting and tests running on pull requests
- Sprint-based workflow with defined goals and regular retrospectives
- Slash commands for common workflows: `/plan-session`, `/end-session`, `/sprint-status`, `/security-review`
- Initial agent role definitions: at minimum a code agent and a review agent with different scopes

### Concrete files that exist

```
project-root/
├── CLAUDE.md                       # Constitution (extended with agent roles)
├── PROJECT_PLAN.md                 # Phases, milestones, sprint tasks
├── CHANGELOG.md                    # Session audit trail
├── docs/
│   ├── ARCHITECTURE.md             # Current architecture state
│   ├── MEMORY.md                   # Cross-session context and decisions
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
        └── ci.yml                  # Lint + tests
```

### Metrics you can track

In addition to Level 1 metrics:

| Metric | How to measure | Target |
|--------|---------------|--------|
| ADR coverage | Significant decisions with ADRs ÷ significant decisions total | >80% |
| Architecture drift | New components not reflected in ARCHITECTURE.md | 0 |
| Sprint goal completion rate | Sprint goals fully completed ÷ sprints run | >70% |
| Test coverage | From CI/CD report | Trending up; target >50% |
| Rework rate | Tasks redone after completion ÷ total tasks | <15% |

### How to upgrade to Level 3

1. Install pre-commit hooks from [`ci-cd/pre-commit-config.yaml`](../ci-cd/pre-commit-config.yaml): secret scanning (gitleaks), naming convention validation, hardcoded path detection
2. Add the AI PR review workflow from [`ci-cd/ai-review.yml`](../ci-cd/ai-review.yml) to your GitHub Actions
3. Add the governance file update check: CI fails if code files changed but `CHANGELOG.md` was not updated
4. Configure branch protection on main: require PR, require CI pass, require at least one human approval
5. Create `docs/COST_LOG.md` and add cost tracking to the session end protocol
6. Add a security scan to the session start protocol in `CLAUDE.md` (the agent checks recently modified files for secrets and PII patterns)

### Estimated time to implement

**2–4 hours** for initial setup of ADRs, ARCHITECTURE.md, and MEMORY.md. Slash commands take approximately 30 minutes to install. CI/CD setup is 1–2 hours depending on your existing pipeline. Total: **one focused day** spread across the first week of the next sprint.

### Who it's for

Teams past the experimental phase. Projects that have made deliberate architectural decisions and want to protect them. Developers who have experienced the "the agent proposed the same thing we rejected three weeks ago" problem and want to prevent it. This is the level where solo developer projects start to feel like they have genuine engineering discipline rather than fast prototyping.

---

## Level 3: Enforced

**Governance is non-optional. CI/CD gates, AI PR review, pre-commit hooks, and security scanning make the rules deterministic.**

### What's implemented

- Pre-commit hooks running locally before every commit: secret scanning, naming convention validation, hardcoded path detection
- GitHub Actions CI/CD pipeline with four tiers: syntax/structure, tests, AI code review, human review
- AI PR review as a CI check: agent reviews every PR against `CLAUDE.md` and `ARCHITECTURE.md` and posts structured feedback
- Governance file update check: PRs with code changes that do not include a CHANGELOG update fail CI
- Branch protection: no direct pushes to main, required CI pass, required human approval
- Automated security scanning on every PR (gitleaks, trufflehog, or equivalent)
- `COST_LOG.md` with per-session cost tracking
- Security scan as part of session protocol

### Concrete files that exist

Everything from Level 2, plus:

```
project-root/
├── .pre-commit-config.yaml        # Pre-commit hooks: secrets, naming, paths
├── docs/
│   └── COST_LOG.md                # Per-session cost tracking
└── .github/
    └── workflows/
        ├── ci.yml                  # Tier 1 + 2: lint, type check, tests
        ├── ai-review.yml           # Tier 3: AI code review
        ├── security-scan.yml       # Secret and PII scanning
        └── governance-check.yml    # Governance file update validation
```

### Metrics you can track

In addition to Level 2 metrics:

| Metric | How to measure | Target |
|--------|---------------|--------|
| AI review pass rate (first submission) | PRs passing AI review on first try ÷ total PRs | >75% |
| Pre-commit rejection rate | Commits rejected by hooks ÷ total commit attempts | Trending to 0 |
| Security scan findings | Secrets/PII found per scan | 0 (critical finding = immediate fix) |
| Governance compliance (enforced) | PRs blocked for missing governance update ÷ total PRs | 0 (compliance is now enforced, not optional) |
| Cost per session | From COST_LOG.md | Tracked; no specific target at this level |
| Test coverage | From CI/CD | >60% |

### How to upgrade to Level 4

1. Build a quality metrics dashboard — even a simple Markdown file that aggregates CHANGELOG data is sufficient. Automate its generation from `COST_LOG.md` and CHANGELOG entries.
2. Configure the master agent (see [`agents/master-agent.md`](../agents/master-agent.md)) to run on all PRs with full context: PR diff, `CLAUDE.md`, `ARCHITECTURE.md`, all ADRs, recent CHANGELOG.
3. Implement model routing: define which tasks use which model tier, add the routing table to `CLAUDE.md`, configure the agent to flag when a task requires a more capable model than the current session is running.
4. Achieve test coverage above 70% — this is a prerequisite for the automated quality metrics at Level 4 to be meaningful.
5. Define the multi-agent specialization you need for your project. At minimum: a code agent and a review agent with distinct system prompts and file access scopes.

### Estimated time to implement

**One sprint** (1–2 weeks) to implement all enforcement layers. Pre-commit hooks are 30 minutes. GitHub Actions workflows are 2–4 hours. Configuring branch protection is 15 minutes. The time investment is front-loaded; enforcement then runs automatically without ongoing maintenance beyond tuning false positives.

### Who it's for

Teams shipping to production. Projects with security or compliance requirements. Any team where a single unreviewed commit with a hardcoded secret would be a serious problem. This is the level at which governance transitions from "discipline that requires remembering" to "system that enforces itself."

The HealthReporting implementation reached Level 3 from Level 0 in two weeks. For a team with existing CI/CD infrastructure, Level 3 is achievable in a sprint.

---

## Level 4: Measured

**Quality metrics are tracked systematically. The master agent has full context. Architecture drift is detected automatically. Cost is optimized through model routing.**

### What's implemented

- Automated quality metrics dashboard: session productivity, test coverage trend, cost per session, AI review pass rate, governance compliance
- Master agent running on all PRs with full project context — not just code review but architectural consistency checking against all ADRs and `ARCHITECTURE.md`
- Automatic drift detection: the master agent flags when new code diverges from documented architectural patterns
- Multi-agent specialization: dedicated code, review, security, test, docs, and cost agents with explicit role boundaries
- Model routing: routing table in `CLAUDE.md` specifies which model tier is used for which task type; the agent flags mismatches
- Test coverage above 70% with coverage reporting in CI/CD
- Cost optimization: actual cost tracking compared to optimal routing cost; monthly review of over/under-usage of model tiers

### Concrete files that exist

Everything from Level 3, plus:

```
project-root/
├── docs/
│   ├── metrics-dashboard.md       # Auto-generated quality metrics summary
│   └── DECISIONS.md               # Non-ADR agent decision log
├── agents/
│   ├── code-agent.md              # Code agent scope and system prompt
│   ├── review-agent.md            # Review agent scope
│   ├── security-agent.md          # Security agent scope
│   ├── docs-agent.md              # Docs/governance update agent
│   └── cost-agent.md              # Cost tracking and alerting agent
└── .github/
    └── workflows/
        └── master-review.yml      # Master agent with full project context
```

### Metrics you can track

In addition to Level 3 metrics:

| Metric | How to measure | Target |
|--------|---------------|--------|
| Architecture drift score | Deviations from ARCHITECTURE.md flagged by master agent | 0 per sprint |
| Model routing efficiency | Actual cost ÷ optimal routing cost | <1.3 (within 30% of optimal) |
| Master agent review accuracy | Correct flags ÷ total flags (no false positives) | >85% |
| Governance overhead | Time in governance processes ÷ total development time | <10% |
| Test coverage | CI/CD | >70% |
| Cost per feature shipped | COST_LOG.md ÷ features shipped per sprint | Tracked, declining |

### How to upgrade to Level 5

1. Create an org-level `CLAUDE.md` at `~/.claude/CLAUDE.md` that defines security rules, naming conventions, and compliance requirements that apply to all repositories in the organization
2. Implement cross-repo governance: a master agent that reads governance files across multiple repositories and flags inconsistencies
3. Build the compliance audit trail: ensure that every AI-assisted decision has a documented human approval, suitable for external audit
4. Define role-based agent access: different developers have different agent capabilities based on their role (junior developers cannot bypass certain CI gates that senior developers can override with documented justification)
5. Implement the governance dashboard as a real-time view, not just a periodic Markdown file

### Estimated time to implement

**One quarter** (2–3 months) for the full Level 4 implementation. The metrics dashboard can be built in a sprint. Multi-agent specialization takes 1–2 sprints to define and tune. Test coverage above 70% depends heavily on the existing state of the test suite — budget appropriately.

### Who it's for

Teams that have been running Level 3 for at least a sprint and want to move from reactive governance (catching problems) to proactive governance (detecting drift before it compounds). Engineering managers who want visibility into AI development quality without requiring manual reporting. Projects with significant technical debt from pre-governance development that needs systematic detection and remediation.

---

## Level 5: Self-Optimizing

**Organizational governance. Cross-repo consistency. Compliance audit trails. The framework improves itself based on observed patterns.**

### What's implemented

- Org-level `CLAUDE.md` defining security rules, compliance requirements, and naming conventions that cascade to all repositories
- Cross-repo governance: master agent monitors multiple repositories for architectural consistency and naming convention drift
- Compliance audit trail: complete record of every AI-assisted decision, every human approval, every governance override — structured for external audit
- Role-based agent access: agent capabilities are governed by developer role; security-critical operations require senior review regardless of who initiates them
- Automated retrospectives: after each sprint, a meta-agent analyzes session patterns, identifies recurring issues, and proposes specific CLAUDE.md or process improvements
- Governance dashboard with real-time visibility: sprint progress, cost attribution by developer and by repository, quality metrics trend, compliance status
- Full cost attribution: AI cost tracked per developer, per team, per project, per sprint — with budget alerts and optimization recommendations

### Concrete files that exist

Everything from Level 4, plus:

```
~/.claude/
└── CLAUDE.md                       # Org-level constitution: security, compliance, naming

org-governance-repo/
├── CLAUDE.md                       # Org-level (same as above, source of truth)
├── policies/
│   ├── security-constitution.md    # Never-list, classification model
│   ├── data-governance.md          # What may and may not go into AI context
│   └── compliance-trail.md         # Audit trail format and requirements
├── agents/
│   └── master-agent-org.md         # Cross-repo master agent spec
└── dashboards/
    └── governance-dashboard.md     # Org-level governance metrics view
```

### Metrics you can track

In addition to Level 4 metrics:

| Metric | How to measure | Target |
|--------|---------------|--------|
| Cross-repo consistency | Pattern deviations flagged by org master agent | <5 per sprint org-wide |
| Compliance audit readiness | % of AI decisions with human approval documented | 100% |
| Governance framework improvement rate | CLAUDE.md improvements shipped per quarter | >3 (evidence of active evolution) |
| AI cost per developer per month | COST_LOG.md aggregated | Within defined budget |
| Onboarding time for new AI-enabled developers | Time from hire to first governed session | <1 day |
| Governance overhead (org-wide) | Time in governance ÷ total development time | <8% |

### How to upgrade beyond Level 5

Level 5 is not a final destination — it is a stable state from which the framework continues to evolve. Beyond Level 5, the improvements are incremental rather than structural:

- Custom tooling for your specific tech stack (specialized agents for your domain)
- Advanced model routing (automated, not just flagged recommendations)
- Integration with external compliance systems (SOX, HIPAA, ISO 27001 audit tooling)
- AI-assisted retrospectives that propose not just CLAUDE.md changes but team process changes

### Estimated time to implement

**3–6 months** from Level 4, assuming Level 4 has been stable for at least one quarter. The org-level governance layer requires buy-in from across the engineering organization, not just one team's adoption. The compliance audit trail requires coordination with security and legal. The cross-repo master agent requires infrastructure that not all organizations have in place.

### Who it's for

Engineering organizations at significant scale (50+ developers) where AI adoption is happening whether or not governance exists. CTOs who need compliance documentation for AI-assisted development. Organizations in regulated industries (healthcare, finance, government) where AI code generation has specific audit requirements. Teams that have experienced the cost of inconsistent governance across teams and want to solve it systemically rather than repeatedly.

---

## Self-Assessment: Find Your Current Level

Answer these 10 questions. Count how many you can answer "yes" honestly.

1. **Does your repository have a `CLAUDE.md` file that the agent reads at every session start, containing rules about naming conventions, forbidden actions, and a session protocol?**

2. **Do you run a session start command before every AI session, and does the agent confirm scope with you before writing any code?**

3. **Is `CHANGELOG.md` updated after every single session, with specific files changed, tasks completed, and progress percentage — not just a vague summary?**

4. **Are your significant architectural decisions documented in ADRs with status, context, decision, consequences, and alternatives considered?**

5. **Does your CI/CD pipeline block merges when governance files were not updated alongside code changes?**

6. **Does every pull request get reviewed by an AI agent against your `CLAUDE.md` rules before human review?**

7. **Do pre-commit hooks prevent secrets, hardcoded paths, and naming convention violations from entering git history?**

8. **Do you track AI API cost per session, and do you know what you spent on AI assistance in the last two weeks?**

9. **Can a new team member or a new AI session read your governance files and produce code that is architecturally consistent with what was built three months ago — without being told anything verbally?**

10. **Is there a defined process for changing `CLAUDE.md` that requires human review, and has the framework itself been reviewed and improved in the last month?**

**Score interpretation:**

| Score | Level | What it means |
|-------|-------|---------------|
| 0–1 | Level 0 | No governance. Start with [getting-started.md](getting-started.md). |
| 2–3 | Level 1 | Foundation in place but incomplete. Complete the Level 1 checklist. |
| 4–5 | Level 2 | Structured but unenforced. Add ADRs and slash commands. |
| 6–7 | Level 3 | Enforcement is partially in place. Close the gaps in CI/CD. |
| 8–9 | Level 4 | Strong enforcement and measurement. Add master agent and metrics dashboard. |
| 10   | Level 5 | Full self-optimizing governance. Focus on evolution and cross-repo consistency. |

The self-assessment is honest if you answer based on what is consistently happening, not what happened once or what you intend to implement. A session protocol that ran 4 times out of 10 is not implemented at Level 1 — it is a Level 0 project with occasional governance.
