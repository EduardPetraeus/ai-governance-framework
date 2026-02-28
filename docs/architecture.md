# The 7-Layer Architecture

This document describes the complete architecture of the AI Governance Framework. Each layer has a specific responsibility. Together, they form a system where AI agents operate at high velocity without losing alignment with the project's goals, conventions, and constraints.

---

## The Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 7: EVOLUTION                                                  │
│  Who updates the rules? How does the system improve itself?          │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 6: TEAM GOVERNANCE                                            │
│  Roles, ownership, conflict resolution. Shared vs. individual.       │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 5: KNOWLEDGE                                                  │
│  Memory hierarchy, ADRs, context propagation. Continuity.            │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4: OBSERVABILITY                                              │
│  Audit trails, decision logs, cost tracking, quality metrics.        │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3: ENFORCEMENT                                                │
│  Pre-commit hooks, CI/CD gates, AI PR review. Deterministic gates.   │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2: ORCHESTRATION                                              │
│  Session protocol, sprint structure, scope management.               │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1: CONSTITUTION                                               │
│  CLAUDE.md, ADRs, security policies, naming conventions.             │
└─────────────────────────────────────────────────────────────────────┘
```

### Data flows up. Rules flow down.

This is the core architectural principle.

**Rules flow down:** The Constitution (Layer 1) defines what is legal. Orchestration (Layer 2) defines how work flows within those rules. Enforcement (Layer 3) makes those rules non-negotiable at the gate. Every higher layer operates within the constraints established by the layers beneath it. You cannot grant a team governance exemption that contradicts the security constitution. You cannot design an evolution process that allows agents to self-modify their own rules without human review.

**Data flows up:** Observability (Layer 4) captures what actually happened. Knowledge (Layer 5) makes that history available to future sessions. Team Governance (Layer 6) uses observable data to resolve disputes and assign ownership. Evolution (Layer 7) uses everything it can observe to decide what rules should change.

The stack is implemented bottom-up for exactly this reason. Enforcement without a Constitution enforces the wrong things. Observability without Orchestration observes chaos. Each layer makes the layer above it meaningful.

---

## Layer 1: Constitution

### What it is

The Constitution is the static rulebook. It is a set of files that define what is legal for agents and humans working in a repository. It does not describe processes or workflows — those belong to Layer 2. It establishes rules that never change session-to-session: what the project is, what it is named, what patterns are required, what is absolutely forbidden.

**CLAUDE.md is not guidance — it is law.**

The distinction matters. Guidance is advisory. An agent can weigh guidance against other considerations and choose differently. Law is not open to interpretation. When `CLAUDE.md` says "no direct commits to main," that rule applies without exception. When it says "all table names use the `stg_` prefix for bronze layer," the agent does not evaluate whether this makes sense for the current task — it follows the rule.

### Why it exists

Without a constitution, an AI agent operates from its training data and the nearest context. Its decisions are locally consistent but globally incoherent. It will name files differently across sessions, adopt different patterns depending on what code it has seen recently, and re-evaluate architectural decisions that were made deliberately weeks ago. The cost is not individual errors — it is structural drift. Over 100 commits, a codebase without a constitution will have 15 different ways of doing the same thing, each one "correct" by the agent's local reasoning.

The Constitution solves this by providing persistent, authoritative global context that overrides local reasoning. The agent's first obligation is to the Constitution, not to what seems elegant in the moment.

### What's in it

**CLAUDE.md** is the primary Constitution file. It contains: project identity (name, type, owner, current phase), code conventions (naming, language, formatting, file structure), architectural principles (patterns, layers, boundaries that may not be crossed), the session protocol (the 4-phase lifecycle defined in Layer 2), a forbidden list (actions the agent may never take), and the definition of done. It is kept under 200 lines. Agents read the entire file at session start, and a long file increases the risk that critical rules at the bottom are lost when context windows are under pressure. Critical rules go at the top.

**Architecture Decision Records (ADRs)** document decisions that have been made and why. They live in `docs/adr/`. An ADR has five fields: Status (Proposed, Accepted, Superseded, Deprecated), Context, Decision, Consequences, and Alternatives considered. Agents may not contradict an Accepted ADR without explicit human authorization. This is how the Constitution prevents decision loops — the same architectural question will not be re-evaluated in session 47 that was settled in session 3.

**Security Constitution** defines what is absolutely forbidden regardless of context: no secrets in code, no hardcoded production paths, no PII in logs or commits, no direct database access bypassing defined interfaces, no unpinned dependency versions. These rules exist separately from CLAUDE.md because they are non-negotiable even when CLAUDE.md is being revised.

**Naming Constitution** provides deterministic, no-interpretation-required rules: snake_case for all identifiers, table prefix conventions (`stg_` bronze, `dim_`/`fct_` silver, `vw_` gold), file names matching table names, all code in English. Deterministic rules produce consistent output from any agent in any session.

### How it connects to adjacent layers

Layer 2 (Orchestration) reads the Constitution at session start and operates within its boundaries. The session protocol is specified in CLAUDE.md — the Constitution defines what the protocol must be; Layer 2 executes it. Layer 3 (Enforcement) makes Constitution compliance mandatory at CI/CD gates. When a pre-commit hook rejects a file with a hardcoded path, it is enforcing the Security Constitution automatically.

### Implementation checklist

- [ ] `CLAUDE.md` exists in repository root, under 200 lines, with critical rules at the top
- [ ] `project_context` section is accurate: correct project name, type, owner, current phase
- [ ] Naming conventions are documented with deterministic, no-ambiguity rules
- [ ] Security forbidden list explicitly enumerates what agents may never do
- [ ] At least one ADR exists for the most significant architectural decision made so far
- [ ] `CLAUDE.md` is versioned in git and changes require PR review

### Common mistakes

- **Writing CLAUDE.md as guidance, not law.** Phrases like "try to" or "it is preferred that" give the agent permission to use its own judgment. Write rules as commands: "Use snake_case. No exceptions."
- **Burying critical rules at the bottom.** In long sessions with large context, the agent may not re-read the entire file. The session protocol, forbidden list, and security rules belong in the first 50 lines.
- **Creating a CLAUDE.md per developer rather than per repository.** The Constitution is the shared rulebook. Individual preferences go in prompts, not in the constitution.

---

## Layer 2: Orchestration

### What it is

Orchestration defines how work flows. Where the Constitution establishes the rules of the game, Orchestration establishes how the game is played: how a session starts, what happens during it, how it ends, and how individual sessions compose into sprints and sprints compose into project phases. Orchestration is the structure that separates governed AI development from ad-hoc agent conversations.

### Why it exists

Without orchestration, AI agents are maximally responsive to the nearest instruction. Ask them to fix a bug, they fix the bug — and possibly refactor three adjacent files, rename a module because the original name was not to their aesthetic preference, and add a feature they inferred you might want. This is not malice. It is agents doing exactly what they are designed to do: be helpful. The problem is that "helpful" and "in scope" are not the same thing.

Orchestration solves the scope problem. Before any code is written, the agent reads the project state, presents its understanding of the current sprint goal, proposes specific tasks within that goal, and waits for confirmation. The human decides what the session will do. The agent executes it. No unilateral scope expansion.

The second problem Orchestration solves is context loss. A session that ends without updating project state means the next session starts from scratch. The agent has no idea what was completed last time, what is still outstanding, or what decisions were made. The session end protocol — updating `CHANGELOG.md` and `PROJECT_PLAN.md` — makes project state persistent across sessions.

### What's in it

**The 4-phase session lifecycle** is the core of Orchestration. Phase 1 is session start: governance sync (read files), model identification, sprint status presentation, scope confirmation. No code before scope is confirmed. Phase 2 is during-session execution: mandatory task reporting after every completed task, checkpoint pause after 3+ tasks, scope creep detection. Phase 3 is session end: summary generation, governance file updates, commit. Phase 4 handles the case where the human forgets to run the protocol — the agent runs it anyway. See [session-protocol.md](session-protocol.md) for the complete specification.

**Sprint structure** applies even to solo developers. A sprint is one week or one logical milestone. A sprint goal is a concrete outcome ("all API connectors built and tested"). Session scope is drawn from the current sprint. This prevents the common failure mode of working on whatever seems interesting in each session without measurable progress toward a defined goal.

**Slash commands** are the interface for Orchestration. `/plan-session` triggers Phase 1. `/end-session` triggers Phase 3. `/sprint-status` produces the current done/in-progress/remaining view. Slash commands standardize the interface so every session starts the same way regardless of which human is running it. See [`commands/`](../commands/) for the complete library.

**Scope management rules** define what the agent may and may not do without explicit approval: no features outside confirmed scope, discovered tasks logged but not executed, cross-layer changes require explicit authorization. These rules live in `CLAUDE.md` (Layer 1) but are enforced operationally during sessions (Layer 2).

### How it connects to adjacent layers

Orchestration executes within the Constitution (Layer 1) — it reads CLAUDE.md, follows its rules, and uses its session protocol specification. It feeds data upward to Observability (Layer 4) — every session generates CHANGELOG entries and updated project state. It is enforced downward by Enforcement (Layer 3) — the CI/CD gate checks that governance files were updated before allowing a merge.

### Implementation checklist

- [ ] `/plan-session` command configured and functional in Claude Code
- [ ] `/end-session` command configured and functional in Claude Code
- [ ] Agent reads `PROJECT_PLAN.md` and `CHANGELOG.md` at every session start
- [ ] No code is written before scope confirmation is received from the human
- [ ] `mandatory_task_reporting` is specified in `CLAUDE.md` and triggers after every task
- [ ] Sprint goals are defined in `PROJECT_PLAN.md` with explicit task breakdowns
- [ ] Session end always produces a governance commit with the standard message format

### Common mistakes

- **Skipping the session start protocol under time pressure.** The entire value of the session protocol is that it runs every time. "I already know what we're working on" is the thought that precedes scope creep.
- **Treating the session end update as optional.** If `CHANGELOG.md` is not updated, the next session starts without accurate history. After 10 sessions, the agent has no useful context about what has been built.
- **Setting sprint goals so large they cannot be completed in a sprint.** A sprint goal that takes 3 weeks is not a sprint goal — it is a phase goal. Break it down until the goal fits inside a week of sessions.

---

## Layer 3: Enforcement

### What it is

Enforcement is the set of automated gates that make governance non-optional. Where the Constitution defines rules and Orchestration specifies processes, Enforcement makes those rules and processes mandatory. An agent can be instructed to follow CLAUDE.md, and it will — until context pressure, a confusingly phrased prompt, or a multistep task causes it to drift. Enforcement catches drift that would otherwise reach the main branch.

**GitHub Actions is the only enforcement that cannot be overridden by an agent.** This is the critical distinction. CLAUDE.md creates probabilistic compliance — the agent should follow it. CI/CD creates deterministic compliance — the code cannot merge without passing. Build your enforcement strategy around this distinction.

### Why it exists

AI agents produce code at speeds that make manual quality control impractical as the primary defense. At 50 commits per session, no human reviewer catches every naming convention violation, every hardcoded path, every file placed in the wrong directory. Automated gates catch these issues consistently, at zero marginal cost per commit, and without reviewer fatigue.

The second reason Enforcement exists is that governance only works if it is universal. If one developer can merge without updating `CHANGELOG.md` because they are in a hurry, the project loses the audit trail for that session. Next week, another developer does the same. After a month, the governance files are out of sync with reality and the agent starts making decisions based on stale context. Enforcement prevents the first exception from becoming the norm.

### What's in it

**Pre-commit hooks** are the first line of defense. They run on the developer's machine before a commit is accepted. They catch the fastest-to-fix problems earliest. A pre-commit hook that rejects a file with a hardcoded path prevents a CI failure minutes later and prevents a secret from ever entering the commit history. The `.pre-commit-config.yaml` in [`ci-cd/`](../ci-cd/) includes hooks for: hardcoded path detection, secret scanning (gitleaks), naming convention validation, and file placement validation.

**CI/CD gates** run on every pull request and operate in four tiers. Tier 1 is syntax and structure (linting with ruff/black/sqlfluff, type checking, naming validation, secret scanning with trufflehog, file structure checks) — fast, deterministic, fails loudly. Tier 2 is tests (unit, integration, data validation) — deterministic, blocks merge on failure. Tier 3 is AI code review — an agent reviews the PR diff against `CLAUDE.md` and `ARCHITECTURE.md`, posting pass/warn/fail comments. Probabilistic but valuable for convention compliance that is hard to express in a linter. Tier 4 is human review — a human approves with agent comments as input. This is the final gate; it requires genuine engagement, not rubber-stamping.

**The governance file check** is a uniquely important gate. If code files were changed in a PR but `CHANGELOG.md` was not updated, the check fails. If new source files were added but `ARCHITECTURE.md` was not updated, the check warns. This enforces the session end protocol at the merge gate — no PR merges without documented project state. The enforcement rule: no merge without a `docs: update project state` commit.

**AI PR review** deserves its own mention. The workflow in [`ci-cd/ai-review.yml`](../ci-cd/ai-review.yml) feeds the PR diff plus `CLAUDE.md` plus `ARCHITECTURE.md` to an agent that returns structured feedback: PASS (follows all conventions), WARN (works but violates a soft convention), or FAIL (violates a hard rule and blocks merge). The agent posts specific line comments, not just a summary verdict. This gives reviewers precise, actionable feedback without requiring them to hold the entire CLAUDE.md rulebook in their head.

### How it connects to adjacent layers

Enforcement validates that the Constitution (Layer 1) was followed — it compares the code against CLAUDE.md rules. It enforces that Orchestration (Layer 2) ran correctly — it checks for governance file updates that should have been produced by the session end protocol. It feeds data to Observability (Layer 4) — CI/CD logs become part of the audit trail, and AI review pass rates become a tracked quality metric.

### Implementation checklist

- [ ] `.pre-commit-config.yaml` installed with at minimum: secret scanning and naming convention check
- [ ] `pre-commit install` run in repository to activate hooks
- [ ] GitHub Actions workflow triggers on all pull requests to main
- [ ] Tier 1 checks (lint, type check, secret scan) configured and blocking
- [ ] Tier 2 checks (unit tests) configured and blocking
- [ ] Governance file update check configured: code changes require CHANGELOG update
- [ ] Branch protection rules configured: no direct pushes to main, required CI pass before merge

### Common mistakes

- **Treating AI review (Tier 3) as a blocker before Tier 1 and 2 are solid.** AI review is probabilistic. It catches nuanced issues. It also generates false positives. Run it in advisory mode first until you trust its signal-to-noise ratio.
- **Not testing pre-commit hooks with an intentional violation.** Install the hooks, then intentionally add a hardcoded path or a `secret = "abc123"` line and verify the hook rejects it. Pre-commit hooks that are not verified often silently fail.
- **Writing governance file checks that are too strict.** A check that fails if *any* commit in the PR does not update CHANGELOG will break documentation-only PRs. Scope the check: if Python or SQL files changed, require a CHANGELOG update.

---

## Layer 4: Observability

### What it is

Observability is the layer that answers the question: what actually happened? Not what was planned, not what the agent said it would do — what happened, verified by evidence. Governance files are the agent's memory. Without them, every session starts from a blank slate and the project's history exists only in git commit messages and the developer's own recollection.

### Why it exists

AI-assisted development has a specific observability problem that does not exist in traditional development. Human developers naturally maintain awareness of project state because they wrote the code slowly enough to internalize it. AI agents write code at 15x speed. The human counterpart approves tasks at 15x speed. At session end: "what did we actually build?" is a genuine question, not a rhetorical one.

The second problem is drift detection. Without observability, architectural drift is invisible until it has compounded for weeks. The agent starts placing files in the wrong directories. Naming conventions start slipping. A silver layer transform starts reading directly from source instead of bronze. Each individual deviation looks minor. Collectively, they undermine the architecture. Observability makes drift visible before it becomes structural.

### What's in it

**CHANGELOG.md** is the session-level audit trail. Every session produces a new entry: date, session number, agent model used, duration estimate, phase, tasks completed (with file paths), tasks carried over, and goal progress percentage. It is append-only. Nothing is deleted or modified — new sessions add new entries. This creates a complete, chronological record of every significant action taken on the project. The HealthReporting implementation produced 137 commits with 100% CHANGELOG coverage because the session end protocol was specified in CLAUDE.md and ran automatically.

**COST_LOG.md** tracks token consumption per session. Columns: date, session, model, input tokens, output tokens, estimated cost. This is how you know whether AI development costs are reasonable, whether model routing is needed (see Layer 6's multi-model principle), and whether a specific spike in cost corresponds to an unusually large session. Without cost tracking, AI API costs are invisible until the invoice arrives.

**DECISIONS.md** captures non-trivial agent decisions that do not rise to the level of a formal ADR but should be recorded. When an agent chooses between two implementation approaches and selects one for specific reasons, that reasoning is logged: date, session, decision, rationale, alternatives considered. This makes the project's reasoning history legible — you can read why the code is written the way it is, not just what it does.

**Quality metrics** are tracked at the session and sprint level: test coverage percentage, lint error rate per commit, AI review pass rate (percentage of PRs that pass agent review on first submission), governance compliance rate (percentage of sessions that completed the full start/end protocol), and rework rate (percentage of tasks that had to be redone). See Layer 7 (Evolution) for how these metrics drive framework improvement.

### How it connects to adjacent layers

Observability is fed by Orchestration (Layer 2) — the session protocol produces CHANGELOG entries automatically. It consumes from Enforcement (Layer 3) — CI/CD logs and AI review results flow into quality metrics. It feeds Knowledge (Layer 5) — the history recorded in CHANGELOG and DECISIONS.md becomes the context that agents read in future sessions to avoid repeating resolved issues.

### Implementation checklist

- [ ] `CHANGELOG.md` exists and has a defined session entry format
- [ ] Session end protocol always produces a CHANGELOG update before committing
- [ ] `COST_LOG.md` exists with at minimum: date, session, model, estimated cost columns
- [ ] `docs/DECISIONS.md` exists for non-ADR decision logging
- [ ] Quality metrics are defined (at minimum: test coverage, governance compliance rate)
- [ ] CHANGELOG entries include "What was NOT done" section for carried-over tasks

### Common mistakes

- **Letting CHANGELOG become a summary of intent rather than a record of fact.** "Built the connector" is not useful. "Created `src/connectors/oura/sleep.py`, added 3 entities to `sources_config.yaml`, ran ingestion smoke test successfully" is useful. File paths, test results, and concrete outcomes.
- **Skipping COST_LOG because costs "seem fine."** Cost visibility is most valuable before there is a problem. By the time costs are visibly wrong, the damage is done.
- **Writing CHANGELOG entries only at session end and losing mid-session detail.** The mandatory_task_reporting protocol in CLAUDE.md accumulates task summaries during the session. Session end consolidates them. This produces richer CHANGELOG entries than trying to reconstruct the session from memory.

---

## Layer 5: Knowledge

### What it is

Knowledge is the layer that gives agents continuity. AI agents have no memory between sessions by default. Each new session is a new conversation with no awareness of previous decisions, previous code, or previous context — unless that context is provided explicitly. Layer 5 is the structured system for providing that context reliably, at the right level of granularity, to every session.

### Why it exists

Without Knowledge, every session begins with a costly and error-prone context-loading process. The human explains what the project does, what was built last time, and what decisions have been made. The agent picks it up imperfectly, misses some nuances, and proceeds. After 10 sessions of this, the agent has accumulated subtle misunderstandings about the project. It reinvents solutions to problems that were solved in session 2. It proposes architectural changes that were explicitly ruled out in session 4. Without persistent knowledge, the 16x velocity gain from AI assistance is partially consumed by repeated context reconstruction.

The second problem Knowledge solves is team continuity. In a team setting, not all developers share the same session history. A developer joining the project in sprint 3 needs to understand the decisions made in sprint 1. A new agent session started by a different developer should produce consistent output with sessions run by their colleagues. This is only possible if the knowledge that governs agent behavior is stored in files, not in individual developers' heads.

### What's in it

**The memory hierarchy** is the structured system for knowledge storage across six levels:

```
Level 1: CLAUDE.md           — Permanent constitution, rarely changed
Level 2: ARCHITECTURE.md     — Project scope and architectural state, updated at milestones
Level 3: PROJECT_PLAN.md     — Current sprint tasks, updated every session
Level 4: CHANGELOG.md        — Append-only session history
Level 5: MEMORY.md           — Claude Code's cross-session context file (auto-generated)
Level 6: Session context     — Disappears when the session closes
```

The hierarchy ensures that different types of knowledge persist at appropriate timescales. Rules that never change live in CLAUDE.md. Current task status lives in PROJECT_PLAN.md. Historical decisions live in CHANGELOG.md. Each file is read at the right moment: CLAUDE.md at every session start, PROJECT_PLAN.md at session start and after every task checkpoint, CHANGELOG.md at session start for context.

**ADRs as knowledge assets** prevent decision loops. Without ADRs, an agent reviewing the codebase in session 20 will notice that DuckDB is used as the local runtime and wonder if PostgreSQL would be better. It might even suggest the switch. This is the same suggestion that was evaluated and rejected in session 3 because of specific trade-offs. An ADR with Status: Accepted documents the decision, the rationale, and the alternatives considered. The agent reads it, sees the decision was made deliberately, and does not reopen it. ADRs are the most undervalued tool in the framework for teams that have been building for more than a few weeks.

**Context propagation** is the mechanism by which knowledge flows between sessions and between developers. In a solo workflow: session N ends by updating CHANGELOG and PROJECT_PLAN; session N+1 starts by reading both. The agent has full context from session N without being told. In a team workflow: Developer A's session ends with a PR that includes CHANGELOG updates; Developer B's next session reads the main branch including those updates; the agent knows what Developer A built. In an enterprise workflow: a master agent reads all PRs and all governance files across the team, maintaining total context across every active thread of work.

### How it connects to adjacent layers

Knowledge is populated by Observability (Layer 4) — CHANGELOG entries, DECISIONS.md, and cost data become the historical knowledge base. It supports Orchestration (Layer 2) — the session start protocol reads knowledge files to orient the agent before work begins. It connects to Team Governance (Layer 6) — knowledge files are the shared context that makes consistent multi-developer, multi-agent collaboration possible.

### Implementation checklist

- [ ] All 6 memory hierarchy levels are present or planned
- [ ] `ARCHITECTURE.md` describes the current state of what has been built, not just what is planned
- [ ] ADRs exist for at least the 2–3 most significant architectural decisions
- [ ] ADR status is maintained: Accepted, Superseded, or Deprecated as appropriate
- [ ] `CLAUDE.md` specifies which files the agent reads at session start (minimum: PROJECT_PLAN.md, CHANGELOG.md)
- [ ] New team members can read the knowledge files and understand why the project is built the way it is

### Common mistakes

- **Writing ARCHITECTURE.md as an aspiration rather than a description.** The file should describe what is actually built, not what the plan says will eventually be built. An agent reading aspirational architecture will make decisions based on a system that does not exist yet.
- **Not maintaining ADR status.** A Superseded ADR that still shows as Accepted will confuse agents and humans alike. When a decision changes, update the old ADR's status and reference the new one.
- **Omitting the "alternatives considered" section from ADRs.** This is the most valuable part of an ADR for agents. Without it, the agent cannot distinguish between "we chose X because we evaluated Y and Z" and "we chose X without evaluating anything else."

---

## Layer 6: Team Governance

### What it is

Team Governance defines how multiple agents and multiple humans work on the same project without producing chaos. It specifies roles, ownership, and conflict resolution protocols. In a solo developer workflow, Layer 6 is minimal — one developer, one agent, clear ownership. In a team of 50, it is the difference between 50 coherent contributors and 50 independent chaos generators.

### Why it exists

The failure mode at the team scale is not individual agent errors — it is divergence. Each developer's agent follows the nearest context. Without shared governance, 10 developers produce 10 implementations of the same pattern, 10 interpretations of the same architectural boundary, and 10 different takes on what the sprint goal means. No individual session is wrong. The aggregate is incoherent.

Team Governance solves divergence through explicit ownership and shared conventions. One person owns CLAUDE.md and is responsible for its accuracy. One person owns the ADRs. One agent role is responsible for security review. These assignments prevent the "everyone is responsible" failure mode where no one actually takes responsibility.

### What's in it

**Agent role specialization** is the structural pattern. Instead of one generalist agent that codes, reviews, documents, and tests, define specialized agents with narrow, well-defined responsibilities:

```
Master Agent         — Read-only. Reviews everything. Flags cross-concern issues. No write access.
Code Agent           — Writes code. Follows CLAUDE.md. Creates feature branches.
Review Agent         — Reviews PRs against ARCHITECTURE.md. Posts structured comments.
Security Agent       — Scans for secrets, PII, unsafe patterns. Can block merge.
Test Agent           — Writes and runs tests. Reports coverage.
Docs Agent           — Updates CHANGELOG, ARCHITECTURE.md, MEMORY.md at session end.
Cost Agent           — Tracks token usage. Alerts on budget overruns.
```

Specialized agents produce better results than generalist agents for the same reason specialized humans do: narrower scope, clearer acceptance criteria, fewer competing priorities. A code agent that only codes cannot accidentally update ARCHITECTURE.md incorrectly because it never touches that file.

**Human role definitions** mirror the agent specialization:

| Role | CLAUDE.md ownership | ADR authority | Agent it works with |
|------|-------------------|---------------|---------------------|
| Tech Lead | Primary owner | Creates and reviews | Master Agent |
| Developer | Cannot modify | Can propose | Code Agent |
| Reviewer | Cannot modify | Reviews | Review Agent |
| Security Lead | Security constitution owner | Creates security ADRs | Security Agent |

**CLAUDE.md ownership model:** There is exactly one person who can approve changes to the main CLAUDE.md. Changes go through a PR, not a direct edit. This is the most important governance rule for teams — a constitution that can be changed by anyone is not a constitution.

**Conflict resolution protocols** define what happens when agents or humans disagree. Agent vs. agent: the master agent mediates; if unresolved, a human makes the final call. Agent vs. human: the agent flags the concern and logs it, the human decides. The agent logs the decision even when overruled. This creates an audit trail of cases where human judgment diverged from agent recommendation — useful data for improving the system over time.

**Branching ownership rules** prevent simultaneous agent sessions on the same branch: one feature branch per developer per session. No two agents write to the same branch at the same time. PRs are the synchronization point.

### How it connects to adjacent layers

Team Governance relies on Observability (Layer 4) to provide the data it needs for conflict resolution and ownership tracking — you cannot resolve a dispute about what happened without a record. It consumes Knowledge (Layer 5) as its shared context. It feeds into Evolution (Layer 7) — the patterns of human-agent conflict, the frequency of CLAUDE.md change proposals, and the consistency of multi-developer output are all inputs to the framework improvement process.

### Implementation checklist

- [ ] CLAUDE.md ownership is explicit: one named person is the constitutional owner
- [ ] Agent roles are defined with explicit scope boundaries (what each agent may and may not do)
- [ ] Branching rules are documented: one developer + agent per feature branch at a time
- [ ] PR review requires at minimum one human approval, regardless of agent review results
- [ ] Conflict resolution protocol is documented for: agent vs. agent, agent vs. human
- [ ] Agents communicate via PR comments and commit messages — never via direct channel messages or shared mutable state outside of git

### Common mistakes

- **Using a generalist agent for everything and then wondering why output is inconsistent.** The cost of defining specialized agents is low. The consistency gain is significant. Invest two hours in defining agent roles and reap the benefit across every subsequent session.
- **Letting multiple developers edit CLAUDE.md without review.** A constitution that changes without review is not a constitution. The first week of undisciplined CLAUDE.md edits will produce contradictions and ambiguities that confuse every subsequent session.
- **Assuming team members understand the session protocol without training.** The protocol only works if everyone runs it the same way. Budget time for onboarding — observe new developers' first three sessions, debrief after each.

---

## Layer 7: Evolution

### What it is

Evolution is the meta-governance layer. It defines how the framework itself improves. Every other layer is subject to Evolution's review: rules that are not working get changed, enforcement that is too strict gets relaxed, enforcement that is too weak gets tightened. Evolution is how the framework stays aligned with reality as the project, the team, and the tooling change over time.

### Why it exists

Without Evolution, governance calcifies. Rules that were correct six months ago become bureaucratic overhead as the project matures. Pre-commit hooks that caught real problems in the early sprint become noise once the team has internalized the conventions. CLAUDE.md accumulates rules that everyone ignores because the project has moved past the problems they were designed to solve. Governance that bremse more than it helps is worse than no governance — it trains the team to route around it.

Evolution solves this by making the framework a subject of deliberate, cadenced review. The goal is not more governance — it is the right governance for the current moment. That changes over time, and the framework must change with it.

### What's in it

**Governance ownership table** specifies who owns which governance file, how changes to it are authorized, and at what cadence it is reviewed:

| File | Owner | Change process | Review cadence |
|------|-------|---------------|----------------|
| `CLAUDE.md` (org-level) | CTO / Tech Lead | ADR + team review | Monthly |
| `CLAUDE.md` (repo-level) | Tech Lead | PR review | Monthly |
| `ARCHITECTURE.md` | Tech Lead | Auto-updated by agent, reviewed by human | Per milestone |
| `PROJECT_PLAN.md` | Product Owner + Tech Lead | Sprint planning | Weekly |
| ADRs | Proposer | PR + team review | Quarterly cleanup |
| Security constitution | Security Lead | Dedicated review | Semi-annually |

**Constitutional change process** is the formal mechanism for evolving CLAUDE.md: a need is identified (by human or agent), a proposed change is documented in an ADR or PR description, the PR is reviewed by relevant stakeholders, it merges, and all agents immediately use the new version because CLAUDE.md is in git. Critically: CLAUDE.md changes require human approval. An agent may propose a change. It may never merge one.

**Anti-bureaucracy rules** are a standing commitment to framework efficiency:
- If a rule is consistently ignored by experienced developers, remove it or make it enforced
- If a CI/CD check always passes, it may be too weak — consider tightening it
- If a CI/CD check causes constant friction without catching real problems, fix or remove it
- Measure governance overhead: time spent on governance processes vs. time spent on product code
- Target: governance overhead under 10% of total development time

**Review cadence** formalizes when each type of review happens so it does not require anyone to remember:
- Monthly: CLAUDE.md review, cost dashboard review
- Quarterly: ADR cleanup (mark Superseded or Deprecated as appropriate), quality metrics review
- Semi-annually: Security constitution audit
- After every incident: add a deterministic check that would have caught the problem

**Learning pipeline** is the structured process for incorporating lessons from sessions, incidents, and team feedback into framework improvements. When the session protocol consistently produces a specific type of missed task, that pattern becomes a new checkpoint rule. When a pre-commit hook consistently fails on legitimate code, that is a signal to tune the hook. When developers find themselves working around a governance rule, that is a signal the rule needs revision.

### How it connects to adjacent layers

Evolution observes all other layers — it requires data from Observability (Layer 4) to know what to change, team feedback from Team Governance (Layer 6) to know what friction points exist, and enforcement logs from Layer 3 to know where rules are effective or ineffective. Its outputs flow down to all layers — a CLAUDE.md update changes the Constitution (Layer 1), a new slash command changes Orchestration (Layer 2), a new CI/CD check changes Enforcement (Layer 3).

### Implementation checklist

- [ ] Governance ownership table is documented (who owns what, who approves changes)
- [ ] CLAUDE.md change process is defined: proposal → review → merge → immediate effect
- [ ] Monthly CLAUDE.md review is calendared as a recurring event
- [ ] Governance overhead is tracked: time in governance processes vs. time in product development
- [ ] Post-incident protocol includes: add a check that would have caught this
- [ ] Anti-bureaucracy rule is documented: consistently ignored rules are removed or enforced

### Common mistakes

- **Treating governance as finished once implemented.** The framework that works for a 3-month sprint will not be the right framework for an 18-month mature project. Build in the review cadence from the start.
- **Letting agents propose and merge changes to CLAUDE.md without human review.** An agent that can change its own rules is not governed — it is self-directed. Constitutional changes require human authorization, always.
- **Adding governance rules faster than removing them.** Every incident produces a new rule. Rules that are no longer needed are never removed. After a year, CLAUDE.md is 600 lines and no one reads it carefully. Prune aggressively and regularly.
