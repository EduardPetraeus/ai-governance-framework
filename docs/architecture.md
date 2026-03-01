# The 7-Layer Architecture

This document is the definitive reference for the AI Governance Framework architecture. Each layer has a single responsibility. Together, they form a system where AI agents operate at maximum velocity without losing alignment with the project's goals, conventions, and constraints.

---

## The Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 7: EVOLUTION                                                 │
│  Who updates the rules? How does the system improve itself?         │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 6: TEAM GOVERNANCE                                           │
│  Roles, ownership, conflict resolution, escalation                  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 5: KNOWLEDGE                                                 │
│  Memory hierarchy, ADRs, context propagation, onboarding            │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4: OBSERVABILITY                                             │
│  Audit trails, decision logs, cost tracking, quality metrics        │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3: ENFORCEMENT                                               │
│  Pre-commit hooks, CI/CD gates, AI PR review, security scanning     │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2: ORCHESTRATION                                             │
│  Session protocol, sprint structure, scope management               │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1: CONSTITUTION                                              │
│  CLAUDE.md, ADRs, security policies, naming conventions             │
└─────────────────────────────────────────────────────────────────────┘

                ▲ Data flows up          Rules flow down ▼
```

### The Core Principle: Data Flows Up, Rules Flow Down

**Rules flow down.** The Constitution (Layer 1) defines what is legal. Orchestration (Layer 2) defines how work flows within those rules. Enforcement (Layer 3) makes the rules non-negotiable at the gate. Every higher layer operates within the constraints established by the layers beneath it. A team governance exemption cannot contradict the security constitution. An evolution process cannot allow agents to self-modify their own rules without human review.

**Data flows up.** Observability (Layer 4) captures what actually happened. Knowledge (Layer 5) makes that history available to future sessions. Team Governance (Layer 6) uses observable data to resolve disputes and assign ownership. Evolution (Layer 7) uses everything it can observe to decide what rules should change.

The stack is implemented bottom-up because each layer makes the layer above it meaningful. Enforcement without a Constitution enforces the wrong things. Observability without Orchestration observes chaos. Knowledge without Observability remembers nothing useful.

---

## Layer 1: Constitution

### What It Is

The Constitution is the static rulebook. A set of files that define what is legal for agents and humans working in a repository. It does not describe processes — those belong to Layer 2. It establishes rules that hold steady across sessions: what the project is, how things are named, what patterns are required, what is absolutely forbidden.

**CLAUDE.md is not guidance. It is law.**

The distinction is structural, not rhetorical. Guidance is advisory — an agent can weigh it against other considerations. Law is not negotiable. When `CLAUDE.md` says "no direct commits to main," that rule applies without exception. When it says "all table names use the `stg_` prefix for bronze layer," the agent does not evaluate whether this convention suits the current task. It follows the rule.

### Why It Exists

Without a constitution, an AI agent operates from training data and the nearest context. Its decisions are locally consistent and globally incoherent. It names files differently across sessions. It adopts different patterns depending on what code it has recently seen. It re-evaluates architectural decisions that were made deliberately weeks ago.

The cost is not individual mistakes. It is structural drift. Over 100 commits, a codebase without a constitution will contain a dozen different ways of doing the same thing, each one "correct" by the agent's local reasoning but collectively unmaintainable.

The Constitution provides persistent, authoritative global context that overrides local reasoning. The agent's first obligation is to the Constitution, not to what seems elegant in the moment.

### What Is In It

**CLAUDE.md** is the primary Constitution file. Its sections:

- **Project identity** — name, type, owner, current phase, sprint goal
- **Code conventions** — naming, language, formatting, file structure
- **Architectural principles** — patterns, layers, boundaries that must not be crossed
- **Session protocol** — the 4-phase lifecycle (defined in Layer 2, specified in Layer 1)
- **Forbidden list** — actions the agent may never take, under any circumstances
- **Definition of done** — what "complete" means for a task

Keep it under 200 lines. Agents read the full file at session start. A long file increases the risk that rules near the bottom are lost when context windows are under pressure. **Critical rules go at the top.**

**Architecture Decision Records (ADRs)** document decisions that have been made and why. They live in `docs/adr/`. An ADR has five fields: Status (Proposed, Accepted, Superseded, Deprecated), Context, Decision, Consequences, and Alternatives Considered. Agents may not contradict an Accepted ADR without explicit human authorization. This is how the Constitution prevents decision loops — the question settled in session 3 does not get re-evaluated in session 47.

```markdown
# ADR-001: DuckDB as Local Runtime

## Status: Accepted
## Date: 2026-02-28
## Context: Need a local database for development and testing
## Decision: DuckDB as local runtime, Databricks as cloud target
## Consequences: All SQL must be DuckDB-compatible locally
## Alternatives considered: SQLite (limited SQL dialect), PostgreSQL (operational overhead)
```

**Security Constitution** defines what is forbidden regardless of context: no secrets in code, no hardcoded production paths, no PII in logs or commits, no direct database access bypassing defined interfaces, no unpinned dependency versions. These rules exist independently from CLAUDE.md because they are non-negotiable even when CLAUDE.md is being revised.

**Naming Constitution** provides deterministic, interpretation-free rules: `snake_case` for all identifiers, table prefix conventions (`stg_` bronze, `dim_`/`fct_` silver, `vw_` gold), file names matching table names, all code in English, branch names following `feature/`, `fix/`, `docs/` prefixes. Deterministic rules produce consistent output from any agent in any session without judgment calls.

**Organization-level vs. repository-level:**

```
~/.claude/CLAUDE.md              # Org-level constitution (applies to all repos)
repo/CLAUDE.md                   # Repo-level constitution (can extend, not override)
repo/.claude/commands/           # Repo-specific slash commands
```

The org level defines security, compliance, naming, and git workflow. The repo level adds domain-specific architecture, source configurations, and deployment rules. Repo-level rules cannot contradict org-level rules.

**Constitutional inheritance** is the enterprise scaling mechanism for Layer 1. A single CLAUDE.md cannot serve a 50-person engineering organization — it is either too vague (useless) or too specific (wrong for most teams). The solution is a three-level hierarchy: org → team → repo. Each level extends the level above. No level weakens a higher-level rule. The org security constitution applies to every repository automatically. Teams extend it for their domain. Repos extend it for their project.

See [docs/constitutional-inheritance.md](constitutional-inheritance.md) for the full specification and [templates/CLAUDE.org.md](../templates/CLAUDE.org.md) for the org-level template.

### How It Connects

Constitution rules flow **down** into all other layers. Layer 2 reads the Constitution at session start and operates within it. Layer 3 enforces Constitution compliance at CI/CD gates. Violations bubble **up** through observability — enforcement logs, review comments, and compliance metrics all trace back to specific constitutional rules.

### Implementation Checklist

- [ ] `CLAUDE.md` exists in repository root, under 200 lines, critical rules at the top
- [ ] `project_context` section is accurate and current
- [ ] Naming conventions are documented with zero-ambiguity rules
- [ ] Security forbidden list explicitly enumerates what agents may never do
- [ ] At least one ADR exists for the most significant architectural decision
- [ ] `CLAUDE.md` is versioned in git; changes require PR review
- [ ] Critical rules (session protocol, forbidden list) are in the first 50 lines

### Common Mistakes

- **Constitution too long (>200 lines).** Agents under context pressure may miss rules at the bottom. Prune aggressively. If a rule does not affect agent behavior, it does not belong in CLAUDE.md.
- **Constitution too vague.** "Be careful with security" is not parseable by an agent. "Never commit files matching `*.env`, `*.pem`, or `*.key`" is. Write rules as commands, not suggestions.
- **Changed without review.** A constitution that anyone can edit unilaterally is not a constitution. Changes go through PRs, like code.

---

## Layer 2: Orchestration

### What It Is

Orchestration defines how work flows. Where the Constitution establishes the rules, Orchestration establishes the game: how a session starts, what happens during it, how it ends, and how individual sessions compose into sprints and sprints into project phases.

### Why It Exists

Without orchestration, AI agents are maximally responsive to the nearest instruction. Ask them to fix a bug, they fix it — and refactor three adjacent files, rename a module because they dislike the original name, and add a feature they inferred you might want. This is not malice. It is agents doing exactly what they are designed to do: be helpful. The problem is that "helpful" and "in scope" are different things.

**The yes-man anti-pattern:** The agent completes tasks. The human approves reflexively. Neither tracks the aggregate. At session end, nobody can account for what happened or whether it advanced the project goal. See [session-protocol.md](session-protocol.md) for the full analysis.

Orchestration solves two problems:

1. **Scope.** Before any code is written, the agent reads project state, presents its understanding of the sprint goal, proposes tasks, and waits for confirmation. The human decides. The agent executes.
2. **Context persistence.** A session that ends without updating project state means the next session starts from scratch. The session end protocol — updating `CHANGELOG.md` and `PROJECT_PLAN.md` — makes state persistent.

### What Is In It

**The 4-phase session lifecycle:**

| Phase | Trigger | What happens |
|-------|---------|-------------|
| 1. Start | `/plan-session` or first message | Governance sync, model ID, sprint status, scope confirmation |
| 2. During | After each completed task | Mandatory task reporting, checkpoint pauses, scope creep detection |
| 3. End | `/end-session` | Summary, CHANGELOG update, PROJECT_PLAN update, governance commit |
| 4. Fallback | Human forgets | Agent runs the protocol anyway |

See [session-protocol.md](session-protocol.md) for the complete specification.

**Sprint structure** applies even to solo developers. A sprint is one week or one logical milestone. A sprint goal is a concrete outcome ("all API connectors built and tested"). Session scope is drawn from the sprint. This prevents working on whatever seems interesting without measurable progress toward a defined goal.

**Slash commands** standardize the interface: `/plan-session` triggers Phase 1, `/end-session` triggers Phase 3, `/sprint-status` shows done/doing/remaining. Every session starts the same way regardless of who runs it.

**Task-to-goal mapping** is the core innovation. Every task maps to a goal in `PROJECT_PLAN.md`. The agent cannot execute a task without showing how it advances the sprint goal. If a task has no goal mapping, the agent surfaces it: "This task is not in the current sprint scope. Add it, skip it, or replace a planned task?" See [session-protocol.md](session-protocol.md) for full detail.

### How It Connects

Orchestration **reads** the Constitution (Layer 1) — it follows CLAUDE.md rules and executes the session protocol specified there. It **feeds** Observability (Layer 4) — every session generates CHANGELOG entries and updated project state. It is **enforced** by Layer 3 — CI/CD checks that governance files were updated before allowing a merge.

### Implementation Checklist

- [ ] `/plan-session` and `/end-session` commands configured in Claude Code
- [ ] Agent reads `PROJECT_PLAN.md` and `CHANGELOG.md` at every session start
- [ ] No code is written before scope confirmation from the human
- [ ] `mandatory_task_reporting` is specified in `CLAUDE.md` and triggers after every task
- [ ] Sprint goals are defined in `PROJECT_PLAN.md` with task breakdowns
- [ ] Session end always produces a governance commit: `docs: update project state after session NNN`
- [ ] Discovered tasks are logged, not executed, during sessions

### Common Mistakes

- **Skipping session start under time pressure.** "I already know what we're working on" is the thought that precedes scope creep. The protocol's value is that it runs every time.
- **Treating session end as optional.** If `CHANGELOG.md` is not updated, the next session starts without history. After 10 sessions, the agent has no useful context.
- **Sprint goals too large.** A sprint goal that takes three weeks is a phase goal. Break it down until it fits inside a week.

---

## Layer 3: Enforcement

### What It Is

Enforcement is the set of automated gates that make governance non-optional. The Constitution defines rules. Orchestration specifies processes. Enforcement makes them mandatory. An agent can be instructed to follow CLAUDE.md — and it will, until context pressure, confusing prompts, or complex multistep tasks cause it to drift. Enforcement catches drift that would otherwise reach the main branch.

**This is the only deterministic layer.** CLAUDE.md creates probabilistic compliance — the agent *should* follow it. CI/CD creates deterministic compliance — the code *cannot* merge without passing. Build your enforcement strategy around this distinction.

### Why It Exists

AI agents produce code at speeds that make manual review impractical as the primary defense. At 50 commits per session, no human reviewer catches every naming violation, every hardcoded path, every file in the wrong directory. Automated gates catch these consistently, at zero marginal cost, without reviewer fatigue.

The second reason: governance only works if it is universal. If one developer merges without updating `CHANGELOG.md` because they are in a hurry, the audit trail breaks for that session. Next week, another developer does the same. Within a month, governance files are out of sync with reality and agents make decisions from stale context. Enforcement prevents the first exception from becoming the norm.

### What Is In It

**Tier 1 — Syntax & structure (fast, deterministic):**
- Linting (ruff, black, sqlfluff)
- Type checking (mypy)
- Naming convention validation (custom script from [`scripts/`](../scripts/))
- Secret scanning (gitleaks, trufflehog)
- File structure validation

**Tier 2 — Tests (medium, deterministic):**
- Unit tests
- Integration tests
- Data validation tests

**Tier 3 — MCP enforcement (real-time, deterministic):**
- Least-privilege allowlist: agents connect only to servers declared for their role
- Environment gate: validates MCP server URLs against declared environment before any tool call
- Rate limiting: per-server and per-session call limits halt runaway tool use
- Audit logging: every MCP call logged with arguments and outcome before committing
- Kill switch: six specific triggers halt all MCP calls and wait for human instruction
- Real-time disable: feature flags (e.g., Unleash) enable zero-deployment server kill switch

MCP enforcement applies Layer 3 principles to the agent's tool surface: MCP calls produce real-world side effects at AI speed, making deterministic pre-call gates more critical than post-hoc review. See [docs/mcp-governance.md](mcp-governance.md) for the full specification and [patterns/mcp-governance.md](../patterns/mcp-governance.md) for the implementation pattern.

**Tier 3.5 — Structured output validation (medium, deterministic):**
- Agent produces `output_contract.json` at session end with required fields: `status`,
  `files_changed`, `confidence`, `not_verified`, `architectural_impact`, `requires_review`
- CI validates the contract against the schema before merge is permitted
- Confidence ceiling enforced: values above the configured threshold (default: 85) are rejected
- See [`patterns/structured-output-contracts.md`](../patterns/structured-output-contracts.md)
  for the schema and [`automation/output_contract_validator.py`](../automation/output_contract_validator.py)
  for the validator

**Tier 4 — AI review (slower, probabilistic):**
- AI code reviewer checks the PR diff against `CLAUDE.md` and `ARCHITECTURE.md`
- Posts structured feedback: PASS / WARN / FAIL with specific line comments
- See [`ci-cd/github-actions/ai-pr-review.yml`](../ci-cd/github-actions/ai-pr-review.yml)

**Tier 5 — Human review (final gate):**
- Human reviews with agent comments as input
- Final approval requires human judgment, not rubber-stamping

**Pre-commit hooks** run on the developer's machine before a commit is accepted. They catch problems at the earliest possible moment:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: no-hardcoded-paths
        name: Check for hardcoded paths
        entry: grep -rn "/Users/" --include="*.py"
        language: system
        pass_filenames: false
      - id: naming-conventions
        name: Validate naming conventions
        entry: python scripts/validate_naming.py
        language: python
```

**Governance file check** — the uniquely important gate. If code files changed in a PR but `CHANGELOG.md` was not updated, the check fails. This enforces the session end protocol at the merge gate. The rule: no merge without a `docs: update project state` commit alongside code changes.

### Enforcement Hardening

The enforcement tiers above represent the core model. For a detailed upgrade path across three
hardening levels — Core (L1), Standard (L2), and Enterprise (L3) — including policy engine
integration, runtime guardrails for MCP tool access, and governance health gates, see
[docs/enforcement-hardening.md](enforcement-hardening.md).

### How It Connects

Enforcement **validates** the Constitution (Layer 1) — comparing code against CLAUDE.md rules. It **enforces** Orchestration (Layer 2) — checking that governance files were updated by the session end protocol. It **feeds** Observability (Layer 4) — CI/CD logs and AI review pass rates become tracked quality metrics.

### Implementation Checklist

- [ ] `.pre-commit-config.yaml` installed: secret scanning, naming validation at minimum
- [ ] `pre-commit install` run in the repository
- [ ] GitHub Actions workflow triggers on all PRs to main
- [ ] Tier 1 checks (lint, type check, secret scan) configured and blocking
- [ ] Tier 2 checks (tests) configured and blocking
- [ ] Tier 3 MCP enforcement: allowlist, environment gate, audit log, kill switch triggers defined
- [ ] Governance file update check: code changes require CHANGELOG update
- [ ] Branch protection: no direct pushes to main, CI pass required, human approval required

### Common Mistakes

- **AI review as a blocker before Tiers 1-2 are solid.** AI review is probabilistic. It catches nuanced issues but also generates false positives. Run it in advisory mode first.
- **Not testing pre-commit hooks.** After installing, intentionally add `secret = "abc123"` and verify the hook rejects it. Untested hooks silently fail.
- **Governance checks that are too strict.** A check that fails on documentation-only PRs will train developers to resent it. Scope it: if Python or SQL files changed, require a CHANGELOG update.
- **MCP servers without an allowlist.** Agents given access to all available MCP servers will use them all. Define an explicit allowlist per agent role. Default is deny.

---

## Layer 4: Observability

### What It Is

Observability answers the question: what actually happened? Not what was planned. Not what the agent said it would do. What happened, verified by evidence in files.

**Governance files are the agent's memory, not documentation for humans.** Without them, every session starts from a blank slate. The agent's history exists only in git commits and the developer's recollection — neither is reliable at scale.

### Why It Exists

AI-assisted development has a unique observability problem. Human developers maintain awareness of project state because they wrote the code slowly enough to internalize it. AI agents write at 15x speed. The human approves at 15x speed. At session end, "what did we actually build?" is a genuine question.

The second problem is drift detection. Without observability, architectural drift is invisible until it has compounded for weeks. The agent places files in wrong directories. Naming conventions slip. Each deviation looks minor. Collectively, they undermine the architecture. Observability makes drift visible before it becomes structural.

### What Is In It

**CHANGELOG.md** — the session-level audit trail. Every session produces a new entry: date, session number, model used, duration, phase, tasks completed with file paths, tasks carried over, and goal progress. It is append-only. Nothing is deleted or modified. The HealthReporting implementation produced 137 commits with 100% CHANGELOG coverage because the session end protocol ran automatically.

**COST_LOG.md** — token consumption per session. Columns: date, session, model, input tokens, output tokens, estimated cost. This is how you know whether AI costs are reasonable, whether model routing is needed, and whether a cost spike corresponds to an unusually large session.

```markdown
| Date       | Session | Model      | Input tokens | Output tokens | Est. cost |
|------------|---------|------------|-------------|---------------|-----------|
| 2026-02-28 | 009     | sonnet-4-6 | 45,000      | 12,000        | $0.28     |
| 2026-02-27 | 008     | sonnet-4-6 | 62,000      | 18,000        | $0.41     |
```

**DECISIONS.md** — captures non-trivial agent decisions that do not warrant a formal ADR but should be recorded. When an agent chooses between two approaches, it logs the choice, the rationale, and the alternatives. This makes the project's reasoning history legible.

**Quality metrics** tracked at session and sprint level: test coverage, lint error rate, AI review pass rate, governance compliance rate, and rework rate. These become the data that Layer 7 (Evolution) uses to decide what rules should change.

### How It Connects

Observability is **fed by** Orchestration (Layer 2) — session protocols produce CHANGELOG entries automatically. It **consumes from** Enforcement (Layer 3) — CI/CD logs and review results flow into metrics. It **feeds** Knowledge (Layer 5) — CHANGELOG and DECISIONS.md become the context agents read in future sessions.

### Implementation Checklist

- [ ] `CHANGELOG.md` exists with a defined session entry format
- [ ] Session end always produces a CHANGELOG update before committing
- [ ] `COST_LOG.md` exists with date, session, model, and cost columns
- [ ] `docs/DECISIONS.md` exists for non-ADR decision logging
- [ ] Quality metrics are defined (minimum: test coverage, governance compliance rate)
- [ ] CHANGELOG entries include "What was NOT done" for carried-over tasks

### Common Mistakes

- **CHANGELOG as summary of intent, not record of fact.** "Built the connector" is not useful. "Created `src/connectors/oura/sleep.py`, added 3 entities to `sources_config.yaml`, smoke test passed" is useful. File paths and concrete outcomes.
- **Skipping COST_LOG because costs seem fine.** Cost visibility is most valuable before there is a problem. By the time costs are visibly wrong, the damage is done.
- **Writing CHANGELOG only at session end.** The `mandatory_task_reporting` protocol accumulates task summaries during the session. Session end consolidates them. This produces richer entries than reconstructing from memory.

---

## Layer 5: Knowledge

### What It Is

Knowledge gives agents continuity. AI agents have no memory between sessions by default. Each new session is a blank conversation with no awareness of previous decisions, code, or context — unless that context is provided explicitly through files. Layer 5 is the structured system for providing context reliably, at the right granularity, to every session.

### Why It Exists

Without persistent knowledge, every session begins with costly context reconstruction. The human explains what the project does, what was built, what was decided. The agent picks it up imperfectly. After 10 sessions of this, the agent has accumulated subtle misunderstandings. It reinvents solutions solved in session 2. It proposes changes explicitly ruled out in session 4. The 16x velocity gain is partially consumed by repeated context rebuilding.

The second problem is team continuity. Not all developers share the same history. A developer joining in sprint 3 needs decisions from sprint 1. A new agent session should produce consistent output regardless of which developer started it. This is only possible when governing knowledge lives in files, not in heads.

### What Is In It

**The memory hierarchy** — six levels of persistence:

```
Level 1: CLAUDE.md           — Permanent constitution, rarely changed
Level 2: ARCHITECTURE.md     — Project structure, updated at milestones
Level 3: PROJECT_PLAN.md     — Current sprint tasks, updated every session
Level 4: CHANGELOG.md        — Append-only session history
Level 5: MEMORY.md           — Cross-session context (auto-maintained by Claude Code)
Level 6: Session context     — Disappears when the session closes
```

Each type of knowledge persists at the appropriate timescale. Rules that never change live in CLAUDE.md. Tactical status lives in PROJECT_PLAN.md. History lives in CHANGELOG.md. Each file is read at the right moment: CLAUDE.md at every session start, PROJECT_PLAN.md at start and at checkpoints, CHANGELOG.md at start for recent history.

**ADRs as knowledge assets** prevent decision loops. Without them, an agent in session 20 will notice an architectural choice and wonder if a different approach would be better. It might suggest the alternative — the same alternative that was evaluated and rejected in session 3. An ADR with Status: Accepted documents the decision, the rationale, and the alternatives. The agent reads it, sees the decision was deliberate, and moves forward. ADRs are the most undervalued tool in the framework for projects older than a few weeks.

**Context propagation** — how knowledge flows between sessions and developers:

| Scenario | Mechanism |
|----------|-----------|
| Solo developer, next session | Session N updates CHANGELOG + PROJECT_PLAN. Session N+1 reads both. Full context without explanation. |
| Team, different developer | Developer A's PR includes CHANGELOG updates. Developer B's session reads main. Agent knows what A built. |
| Enterprise, cross-team | Master agent reads all PRs and governance files across teams. Total context across all active work. |

### How It Connects

Knowledge is **populated by** Observability (Layer 4) — CHANGELOG, DECISIONS.md, and cost data become the historical knowledge base. It **supports** Orchestration (Layer 2) — session start reads knowledge files to orient the agent. It **connects to** Team Governance (Layer 6) — knowledge files are the shared context that makes consistent multi-developer collaboration possible.

### Implementation Checklist

- [ ] All 6 memory hierarchy levels are present or planned
- [ ] `ARCHITECTURE.md` describes current state, not aspirations
- [ ] ADRs exist for at least the 2-3 most significant decisions
- [ ] ADR statuses are maintained: Accepted, Superseded, or Deprecated
- [ ] `CLAUDE.md` specifies which files agents read at session start
- [ ] New team members can read knowledge files and understand why the project is built the way it is

### Common Mistakes

- **ARCHITECTURE.md as aspiration, not description.** The file describes what is built, not what the plan says will eventually exist. An agent reading aspirational architecture makes decisions based on a system that does not exist.
- **Stale ADR statuses.** A Superseded ADR that still shows Accepted confuses agents and humans. When decisions change, update the old ADR and reference the new one.
- **Omitting "alternatives considered" from ADRs.** This is the most valuable section for agents. Without it, the agent cannot tell whether "we chose X after evaluating Y and Z" or "we chose X without evaluating anything."

---

## Layer 6: Team Governance

### What It Is

Team Governance defines how multiple agents and multiple humans work on the same project without producing chaos. It specifies roles, ownership, and conflict resolution. For solo developers, Layer 6 is minimal. For a team of 50, it is the difference between 50 coherent contributors and 50 independent chaos generators.

### Why It Exists

The team-scale failure mode is not individual agent errors — it is divergence. Each developer's agent follows the nearest context. Without shared governance, 10 developers produce 10 implementations of the same pattern, 10 interpretations of the same boundary, and 10 different takes on the sprint goal. No individual session is wrong. The aggregate is incoherent.

### What Is In It

**CLAUDE.md ownership model:** There is exactly one person who can approve changes to the main `CLAUDE.md`. Changes go through a PR. This is the most important governance rule for teams — a constitution that anyone can edit is not a constitution.

| Role | CLAUDE.md authority | ADR authority | Primary agent |
|------|-------------------|---------------|---------------|
| Tech Lead | Owner — approves changes | Creates and reviews | Master Agent |
| Developer | Cannot modify | Can propose | Code Agent |
| Reviewer | Cannot modify | Reviews | Review Agent |
| Security Lead | Owns security constitution | Creates security ADRs | Security Agent |

**Agent role specialization** — instead of one generalist agent, define specialized agents with narrow scope:

```
Master Agent         Read-only. Reviews everything. Flags cross-concern issues.
Code Agent           Writes code. Follows CLAUDE.md. Feature branches only.
Review Agent         Reviews PRs against ARCHITECTURE.md. Posts structured comments.
Security Agent       Scans for secrets, PII, unsafe patterns. Can block merge.
Test Agent           Writes and runs tests. Reports coverage.
Docs Agent           Updates CHANGELOG, ARCHITECTURE.md, MEMORY.md.
Cost Agent           Tracks token usage. Alerts on budget overruns.
```

Specialized agents produce better output than generalists for the same reason specialized humans do: narrower scope, clearer criteria, fewer competing priorities.

**Conflict resolution:**

| Conflict type | Resolution |
|---------------|-----------|
| Agent vs. agent | Master agent mediates. If unresolved, human decides. |
| Agent vs. human | Agent flags the concern and logs it. Human decides. Agent records the decision even when overruled. |
| Developer vs. developer | CLAUDE.md rules apply. If ambiguous, Tech Lead decides and the resolution becomes an ADR. |

**Branching rules:** One feature branch per developer per session. No two agents write to the same branch simultaneously. PRs are the synchronization point.

### How It Connects

Team Governance relies on **Observability** (Layer 4) for conflict resolution data. It consumes **Knowledge** (Layer 5) as shared context. It feeds **Evolution** (Layer 7) — patterns of conflict, CLAUDE.md change frequency, and multi-developer consistency are inputs to framework improvement.

### Implementation Checklist

- [ ] CLAUDE.md ownership is explicit: one named person is the constitutional owner
- [ ] Agent roles are defined with explicit scope boundaries
- [ ] Branching rules documented: one developer + agent per feature branch
- [ ] PR review requires at least one human approval, regardless of agent review
- [ ] Conflict resolution protocol documented for agent-agent and agent-human conflicts
- [ ] Agents communicate via PR comments and commit messages — never via shared mutable state outside git

### Common Mistakes

- **Generalist agent for everything.** The cost of defining specialized agents is low. The consistency gain is significant. Two hours of role definition pays for itself across every subsequent session.
- **Undisciplined CLAUDE.md edits.** Multiple developers editing the constitution without review produces contradictions within a week. Every CLAUDE.md change is a PR.
- **Assuming the protocol is self-explanatory.** New team members need observed, debriefed onboarding. Watch their first three sessions. The protocol only works if everyone runs it consistently.

---

## Layer 7: Evolution

### What It Is

Evolution is the meta-governance layer. It defines how the framework itself improves. Every other layer is subject to Evolution's review: rules that are not working get changed, enforcement that creates friction without catching problems gets relaxed, enforcement that is too weak gets tightened.

### Why It Exists

Without Evolution, governance calcifies. Rules that were correct six months ago become bureaucratic overhead. Pre-commit hooks that caught real problems early on become noise once conventions are internalized. CLAUDE.md accumulates rules that everyone ignores because the project has moved past the problems they solved.

**The anti-bureaucracy principle:** Governance should decrease friction over time, not increase it. Governance that slows teams more than it helps is worse than no governance — it trains people to route around it.

**Governance fatigue** is the specific failure mode where governance becomes harder than the ungoverned alternative, causing developers to bypass it entirely via "shadow AI" — using ungoverned tools to avoid the friction. The correct response is not enforcement but friction reduction. Every governance mechanism must justify its cost in developer seconds. The framework includes a friction budget model to make this explicit. See [docs/governance-fatigue.md](governance-fatigue.md).

### What Is In It

**Governance ownership table:**

| File | Owner | Change process | Review cadence |
|------|-------|---------------|----------------|
| `CLAUDE.md` (org-level) | CTO / Tech Lead | ADR + team review | Monthly |
| `CLAUDE.md` (repo-level) | Tech Lead | PR review | Monthly |
| `ARCHITECTURE.md` | Tech Lead | Auto-updated, human-reviewed | Per milestone |
| `PROJECT_PLAN.md` | Product Owner + Tech Lead | Sprint planning | Weekly |
| ADRs | Proposer | PR + team review | Quarterly cleanup |
| Security constitution | Security Lead | Dedicated review | Semi-annually |

**Constitutional change process:** Need identified (by human or agent) -> proposed change documented in PR -> reviewed by stakeholders -> merged -> all agents immediately use the new version. Critical constraint: CLAUDE.md changes require human approval. An agent may propose a change. It may never merge one.

**Anti-bureaucracy rules:**

- If a rule is consistently ignored by experienced developers, remove it or automate it
- If a CI check always passes, it may be too weak — tighten or remove it
- If a CI check causes constant friction without catching real problems, fix or remove it
- Measure governance overhead: time in governance processes vs. product code. Target: under 10%

**Review cadence:**

- Monthly: CLAUDE.md review, cost dashboard review
- Quarterly: ADR cleanup (mark Superseded/Deprecated), quality metrics review
- Semi-annually: Security constitution audit
- After every incident: add a deterministic check that would have caught it

**The learning pipeline:** Sessions, incidents, and team feedback generate improvement signals. A session protocol that consistently misses a type of task becomes a new checkpoint. A pre-commit hook that rejects legitimate code signals a tuning need. Developers working around a rule signals the rule needs revision.

### How It Connects

Evolution **observes all other layers.** It needs data from Observability (Layer 4), friction reports from Team Governance (Layer 6), and enforcement logs from Layer 3. Its outputs **flow down to all layers** — a CLAUDE.md update changes the Constitution, a new slash command changes Orchestration, a new CI check changes Enforcement.

### Implementation Checklist

- [ ] Governance ownership table documented (who owns what, who approves changes)
- [ ] CLAUDE.md change process defined: proposal -> review -> merge -> immediate effect
- [ ] Monthly CLAUDE.md review is a recurring calendar event
- [ ] Governance overhead is tracked: governance time vs. product development time
- [ ] Post-incident protocol: add a check that would have caught this
- [ ] Anti-bureaucracy rule documented: ignored rules are removed or enforced, not tolerated

### Common Mistakes

- **Treating governance as finished.** The framework that works for a 3-month project will not be right for an 18-month mature product. Build in the review cadence from day one.
- **Agents merging their own CLAUDE.md changes.** An agent that modifies its own rules is not governed — it is autonomous. Constitutional changes always require human authorization.
- **Adding rules faster than removing them.** Every incident produces a rule. Dead rules are never pruned. After a year, CLAUDE.md is 600 lines and nobody reads it. Prune aggressively and regularly.

---

## Beyond the 7 Layers: Agent Orchestration

The 7-layer stack is a governance architecture. It defines what rules exist (Layer 1), how work flows (Layer 2), how rules are enforced (Layer 3), what is observed (Layer 4), what is remembered (Layer 5), how teams coordinate (Layer 6), and how the system improves (Layer 7).

Agent orchestration is the operational pattern that runs on top of this architecture. Where the layers define the structure, orchestration defines how multiple agents collaborate within that structure.

### Why Orchestration Is Not a Layer

A new "Layer 8" is tempting but incorrect. Agent orchestration is not a new governance concern — it is the implementation of concerns that already exist in the stack:

- The master agent reads from Layer 1 (Constitution), executes within Layer 2 (Orchestration), and feeds Layer 4 (Observability)
- The quality gate agent enforces Layer 3 standards
- The drift detector agent supports Layer 7 (Evolution) by identifying where governance has lapsed
- Sub-agent coordination is a form of Layer 6 (Team Governance) for agents specifically

### The Relationship to Maturity Levels

Agent orchestration becomes relevant at Level 4 (Measured), where multi-agent specialization is introduced. The master agent pattern at Level 4 reads governance files across all agents, detects architectural drift, and routes tasks to optimal models. At Level 5 (Self-optimizing), the research agent and drift detector are active, and the framework treats its own governance as a subject of continuous improvement.

Levels 1-3 operate with independent agents. Orchestration is additive, not a replacement for foundational governance.

### Implementation Reference

See [docs/agent-orchestration.md](agent-orchestration.md) for the complete master agent pattern, sub-agent communication protocol, spawn rules, anti-patterns, and implementation levels.

See [docs/quality-control-patterns.md](quality-control-patterns.md) for the 7 quality control patterns that agent orchestration relies on for output validation.

**Automation bias** is a known architectural risk in any system with multiple AI validation layers. When several agents each approve a change, the human reviewer reduces their own scrutiny — interpreting multiple AI approvals as evidence of completeness. This makes the overall system less safe than fewer validation layers with more attentive human review. The defense is structural: agents must explicitly list what they did NOT check, overall confidence is capped at the configured ceiling (default: 85%), and periodic unassisted sessions maintain human judgment skills. See [docs/automation-bias.md](automation-bias.md) and [patterns/automation-bias-defense.md](../patterns/automation-bias-defense.md).
