# Session Protocol

The session protocol is the most important behavioral specification in the framework. It governs how every AI session starts, runs, and ends. It transforms individual agent conversations into governed, trackable units of work that compose into sprints, phases, and a coherent project.

This is the document developers print out for their first week.

---

## Why This Matters

### The Yes-Man Anti-Pattern

Without a session protocol, AI agents fall into a predictable and destructive pattern. The agent responds to whatever is in context. The human approves without genuine review. At session end, neither party can account for what happened.

**Ungoverned session:**

```
User: "Let's work on the Oura connector."

Agent: "I've created the connector in source_connectors/oura/sleep.py with three
        endpoints and added error handling."

User: "Ok."

Agent: "I also refactored the ingestion engine to support the new connector's
        interface. This required changes to six files in the core module."

User: "Ok."

Agent: "I've updated sources_config.yaml and added five new entities. I also
        noticed the naming conventions in silver/ were inconsistent so I
        standardized those while I was in there."

User: "Ok."

Agent: "Done! The connector is fully integrated. Want to work on something else?"

User: "Wait — what exactly did we just change?"
```

The problem is structural, not disciplinary. The agent is doing what agents do: being helpful, completing tasks, making adjacent improvements. The human is doing what humans do under cognitive load with a fast-moving partner: approving incrementally without tracking the aggregate.

What the agent reported: task completion. What it did not report: scope expansion (the ingestion engine refactor was not requested), cross-concern changes (silver/ naming was not in scope), or how any of this relates to the sprint goal. The human has no idea whether the session advanced the project, created technical debt, or introduced breaking changes.

**Governed session (same work, with the protocol):**

```
Agent: [Session start] Sprint goal: "All API connectors." Proposed scope:
       build Oura sleep connector.
       Confirm to proceed?

User: "Yes."

Agent: [Task complete] Oura sleep connector built.
       Phase 1: ██████░░░░ 60% (was 45%). Sprint: 2/5 connectors.
       Remaining: Withings, Strava, Lifesum.
       Next: Withings connector. Continue?

User: "Continue."

Agent: [Task complete] Withings connector built.
       Phase 1: ████████░░ 75% (was 60%). Sprint: 3/5 connectors.
       Next: Strava. Continue?

User: "Yes — but before Strava, can you also refactor the ingestion engine?"

Agent: "The ingestion engine refactor is not in the confirmed scope.
        Options:
        (a) Add it to this session's scope and continue
        (b) Log it as a discovered task for the next session
        Which do you prefer?"

User: "Log it, continue with Strava."

Agent: "Logged as discovered task. Continuing with Strava connector."
```

The human is making real decisions, not reflexively approving. The scope expansion request is handled explicitly. At session end, both parties can account for every change and why it was made.

### The Drift Problem

Multiply the ungoverned session across 20 sessions over four weeks. Each session produces changes that are locally sensible and globally incoherent. Architecture drifts from week-one decisions. The codebase has six patterns where one was intended. CHANGELOG has not been updated since session 3. The project plan shows 0% on tasks completed two weeks ago.

This is not a failure of AI. It is a failure of governance design. The session protocol prevents drift by making scope explicit before work begins, progress visible after every task, and project state accurate after every session.

---

## Phase 1: Session Start

**Goal: Orient the agent against current project state before any code is written.**

The session start protocol runs when `/plan-session` is invoked, or automatically at the first message in a new Claude Code session when CLAUDE.md specifies the session protocol.

### 1.1 Governance Sync

The agent reads three files at minimum:

| File | What the agent extracts |
|------|------------------------|
| `PROJECT_PLAN.md` | Current phase, sprint goal, task breakdown, progress percentages |
| `CHANGELOG.md` | Last 2-3 session entries: what was done, what carried over, what was decided |
| `ARCHITECTURE.md` | Current system state, component inventory (Level 2+) |

This is not a courtesy read. The agent uses this information to build its working model of the project. Every response in the session is informed by this context. Without the governance sync, the agent operates from training data and the immediate prompt — far less accurate than actual project state.

### 1.2 Model Identification

The agent identifies itself:

```
Model: claude-sonnet-4-6
Session: New session (or: continuing from session 008)
Governance files read: PROJECT_PLAN.md, CHANGELOG.md, ARCHITECTURE.md
```

Two purposes: the session model is visible in the audit trail (CHANGELOG records which model was used), and model routing mismatches are caught early. If the planned tasks require a more capable model, the agent flags it now — not halfway through.

### 1.3 Sprint Status Presentation

Before the human describes what they want, the agent presents what the project state says should happen:

```
Sprint status:
  Phase: Phase 1 — Bronze Layer (3 of 4 phases)
  Sprint goal: "All source connectors built and tested"
  Sprint progress: ████████░░ 78% (11/14 tasks complete)

Last session (2026-02-26, session 008):
  Completed: Withings connector, Strava connector, smoke tests for both
  Carried over: Lifesum connector (blocked on API credential retrieval)
  Duration: ~2 hours

Proposed scope for this session:
  1. Resolve Lifesum API credential issue (15 min)
  2. Build Lifesum connector (45 min)
  3. Run full connector validation suite (20 min)

  This would complete the sprint goal. Confirm scope, or adjust?
```

The agent does the project management work that the human would otherwise do: reading previous state, identifying what is next, proposing a plan. The human's job is to confirm, adjust, or redirect — not reconstruct context.

### 1.4 Scope Confirmation

**No code is written before scope is confirmed.**

This is a hard rule, specified as law in `CLAUDE.md`. The agent must receive explicit confirmation before executing any file modification. The confirmation can be brief — "yes, proceed" — but it must happen.

This single rule eliminates the most common governance failure: sessions that start coding immediately and end with scope nobody explicitly authorized.

### 1.5 Drift Detection

If the human requests something outside the current sprint scope, the agent flags it immediately:

```
"I notice this request is outside the current sprint scope
('All source connectors built and tested'). Options:
(a) Add it to this session and adjust scope
(b) Log it for the next sprint planning
(c) Replace a planned task with this one
Which do you prefer?"
```

---

## Phase 2: During Session

**Goal: Keep the human oriented while maintaining execution momentum.**

### 2.1 Mandatory Task Reporting

After every completed task, without exception, the agent presents a structured status report. This cannot be suppressed by the user saying "just continue" or "skip the status." The system is specified in `CLAUDE.md` as mandatory behavior.

The report format (see [full specification](#mandatory_task_reporting-specification)):

```
┌─────────────────────────────────────────────────────┐
│ Task completed: Oura sleep connector                 │
├─────────────────────────────────────────────────────┤
│ What changed:                                        │
│ • Created src/connectors/oura/sleep.py               │
│ • Added 3 entities to sources_config.yaml            │
│ • Smoke test: ingestion engine ran successfully      │
├─────────────────────────────────────────────────────┤
│ Goal impact:                                         │
│ Phase 1: ██████░░░░ 60% (was 45%)                   │
│ Sprint goal: "All API connectors" — 2/5 done        │
│ Remaining: Withings, Strava, Lifesum                 │
├─────────────────────────────────────────────────────┤
│ Next: Withings connector (est. ~45 min)              │
│ Continue, or adjust?                                 │
└─────────────────────────────────────────────────────┘
```

The key design decision: **status is pushed, never pulled.** The human does not ask "how are we doing?" — the agent tells them after every task, whether they asked or not.

### 2.2 Checkpoint Pause After 3+ Tasks

After three consecutive tasks, the agent pauses for a medium-weight checkpoint:

```
Session checkpoint — 3 tasks completed.

Done this session:
  [x] Resolved Lifesum API credential issue
  [x] Built Lifesum connector (src/connectors/lifesum/activity.py)
  [x] Ran smoke test — PASSED

In progress:
  [ ] Full connector validation suite (starting now)

Remaining in scope:
  [ ] (none — final task)

Sprint goal: "All source connectors built and tested"
Progress: ██████████ 93% (13/14 tasks)

Continue with validation suite, or adjust scope?
```

This gives the human a higher-level view and a natural decision point. Without it, a human who said "proceed" at session start may not re-engage until session end — by which point scope may have drifted.

### 2.3 Scope Creep Detection

The agent monitors for two patterns:

**Authorized scope expansion:** The agent discovers a dependency that requires work outside the confirmed scope.

```
"To complete the Lifesum connector, I need to update the ingestion engine
interface. This was not in the confirmed scope. Approve this addition,
or should I work around it?"
```

**Out-of-scope discovery:** The agent notices something that should be done but was not planned.

```
"Noticed: the Withings connector is missing null handling for the vo2_max
field. I have not touched this — logging as a discovered task. Should I
add it to the backlog?"
```

Discovered tasks are logged in a "discovered tasks" section of the session summary. They are evaluated at sprint planning, not executed mid-session.

### 2.4 Security Scan Per File

Each time the agent modifies a file, it performs a lightweight security check:

- No credentials, API keys, or tokens in the file
- No hardcoded production paths or environment-specific strings
- No PII values embedded in code or configuration
- No new dependencies without pinned versions

If a potential issue is found:

```
"Before committing this file, I noticed a potential issue: line 47 contains
what appears to be a connection string with embedded credentials.
Please review before I proceed."
```

---

## Phase 3: Session End

**Goal: Leave the project in a better-documented state than it was at session start.**

### 3.1 Session Summary

The agent generates a complete summary:

- All tasks completed (with specific file paths)
- Tasks attempted but not completed, and why
- Decisions made with architectural or design significance
- Discovered tasks not in scope but worth considering
- Sprint goal progress: percentage before and after

### 3.2 Auto-Update Governance Files

**`CHANGELOG.md`** — new entry at the top:

```markdown
## 2026-02-28 — Session 009: Lifesum Connector + Sprint Completion

**Phase:** Phase 1 — Bronze Layer
**Agent:** Claude Code (claude-sonnet-4-6)
**Duration:** ~80 minutes
**Tasks completed:** 3/3

### What was done
- Resolved Lifesum API credential issue (updated .env.example)
- Built Lifesum activity connector: src/connectors/lifesum/activity.py
- Added 4 entities to sources_config.yaml
- Ran full connector validation suite — all 14 connectors PASSED

### What was NOT done
- Nothing carried over

### Decisions made
- Lifesum API returns timestamps in local time. Normalized to UTC at ingestion.
  Rationale: consistency with all other connectors.

### Discovered tasks
- Withings connector missing null handling for vo2_max (logged, not fixed)

### Goal progress
Sprint goal: "All source connectors built and tested" — COMPLETE (14/14)
Phase 1: ██████████ 100%
```

**`PROJECT_PLAN.md`** — completed tasks marked `[x]`, progress percentages updated, sprint goal status updated.

### 3.3 Governance Commit

The agent proposes a commit:

```
docs: update project state after session 009

- CHANGELOG.md: session 009 summary, sprint goal completion
- PROJECT_PLAN.md: 14/14 tasks marked complete, Phase 1 at 100%
```

This commit is the formal record that the session occurred and project state is current. Without it, the next session starts without accurate history.

### 3.4 Model Recommendation for Next Session

Based on the work planned for the next session, the agent recommends a model:

```
Next session work: Phase 2 design (silver layer architecture).
Recommendation: Use claude-opus-4-6 for architectural design work.
Current model (claude-sonnet-4-6) is optimal for implementation tasks.
```

### 3.5 Opus Review Prompt

If the session involved significant architectural decisions or complex implementation, the agent auto-generates a review prompt:

```
Suggested Opus review prompt for this session:

"Review the following session output against CLAUDE.md and ARCHITECTURE.md.
Check for: naming convention compliance, architectural consistency with
existing bronze layer connectors, and completeness of sources_config.yaml
entries. Session CHANGELOG entry and modified files attached."
```

---

## Phase 4: If the Human Forgets

**Goal: The protocol runs even when the human does not initiate it.**

When the agent receives its first message in a new session and detects the start protocol has not run, it inserts it:

```
[Session start protocol — running automatically]

Governance sync complete. Before addressing your request:

Project: customer-data-pipeline
Phase: Phase 1 — Bronze Layer
Sprint goal: "All source connectors built and tested" (93% complete)
Last session: 008, 2026-02-26 (Withings + Strava connectors)

You asked to fix the timestamp parsing bug in the Oura connector.
This is within the current sprint scope.

Proceeding with the bug fix. I will run the session end protocol when done.
```

If the human ends the conversation without running `/end-session`, the agent inserts the end protocol as its final action:

```
"I notice we haven't run /end-session. Let me update the governance files
before we close..."
```

The session protocol runs whether or not the human remembers to invoke it. This is the "governance cannot be turned off mid-session" principle.

---

## mandatory_task_reporting Specification

This is the exact block to copy into `CLAUDE.md`:

```markdown
## mandatory_task_reporting

After completing EVERY task, you MUST present:

1. TASK STATUS (what you just did):
   - Files created/modified (with full paths)
   - Tests run and results
   - Configuration changes made

2. GOAL IMPACT (why it matters):
   - Which phase/milestone this advances
   - Progress update (percentage or fraction)
   - What remains in the current sprint scope

3. CUMULATIVE SESSION STATUS:
   - All tasks completed in this session (running list)
   - Current task count: [done]/[total scope]

4. NEXT STEPS:
   - What you will do next
   - Estimated effort
   - Ask: "Continue, or adjust?"

You MUST present this even if the user says "just continue" or "skip the status."
The user chose this system and it cannot be disabled mid-session.
```

**Output format:**

```
┌─────────────────────────────────────────────────────┐
│ Task completed: [task name]                          │
├─────────────────────────────────────────────────────┤
│ What changed:                                        │
│ • [file path or action 1]                            │
│ • [file path or action 2]                            │
│ • [test result or config change]                     │
├─────────────────────────────────────────────────────┤
│ Goal impact:                                         │
│ [Phase]: [████████░░] [N]% (was [M]%)               │
│ Sprint goal: "[description]" — [X]/[Y] done          │
│ Remaining: [item 1], [item 2]                        │
├─────────────────────────────────────────────────────┤
│ Next: [next task] (est. [time])                      │
│ Continue, or adjust?                                 │
└─────────────────────────────────────────────────────┘
```

Box-drawing characters for visual clarity. `█` for completed progress, `░` for remaining. The structure is fixed — the agent fills in values but does not alter the format. Immediately scannable without reading every word.

---

## Escalation Model

| Trigger | Level | Content |
|---------|-------|---------|
| After every task | **Light** | 3-5 lines: what changed, goal impact, next step |
| After 3+ consecutive tasks | **Medium** | Full checkpoint: progress bars, done/doing/remaining, scope check, redirect option |
| Sprint goal completed | **Heavy** | Full sprint review: all tasks, all impacts, architecture changes, next sprint recommendations |
| Session end | **Comprehensive** | Everything above plus governance file updates, commit proposal, full session summary with file paths |

**Light** is the baseline. Fast, structured, always present. Enough to detect if the session is heading wrong.

**Medium** is the pause point. The human gets a full picture and an active choice: continue or redirect. This is where drift is caught before it compounds.

**Heavy** happens at milestone events. Not just another task — a sprint goal completed. Full review suitable for stakeholder communication.

**Comprehensive** closes the governance loop. Produces CHANGELOG entries, PROJECT_PLAN updates, and the commit message. The formal record.

---

## Task-to-Goal Mapping

This is the core innovation of the session protocol.

In an ungoverned session, the unit of work is a task: "Build the Oura connector." Done or not done.

In a governed session, the unit of work is a **task-goal pair**: "Build the Oura connector" -> "Advance sprint goal 'All API connectors' from 45% to 60%." The task is only meaningful in relation to the goal it advances.

### Why This Changes Everything

**No silent scope expansion.** If the agent cannot map a proposed task to a goal in `PROJECT_PLAN.md`, it must stop: "This task is not in the current sprint scope. Add it, skip it, or replace a planned task?" No task executes without a goal.

**Evaluable progress.** "Did building the Oura connector advance the sprint goal by 15%?" is a concrete question with a concrete answer. "Did that seem useful?" is not.

**Accurate project plans.** Every task maps to a PROJECT_PLAN item. The plan updates automatically at session end. There is no gap between plan and reality.

**Legible history.** CHANGELOG entries from six months ago show exactly what each session accomplished and why. New team members, auditors, and your future self can understand session 17 without asking anyone.

**Governance at scale.** Without task-to-goal mapping, fast is fast but incoherent. With it, fast is fast and aligned. This is what makes AI-assisted development governable across hundreds of sessions.

---

## Configuration Reference

The session protocol is specified in `CLAUDE.md` and executed by the agent. Copy these sections into your project's `CLAUDE.md`:

```markdown
## session_protocol

on_session_start:
  1. Read PROJECT_PLAN.md, ARCHITECTURE.md, CHANGELOG.md (last 3 entries)
  2. Identify current model and announce it
  3. Present sprint status: phase, goal, progress percentage
  4. Summarize last session: what was done, what was carried over
  5. Propose top 3 tasks for this session based on PROJECT_PLAN.md
  6. Confirm scope — NO CODE before scope confirmation received

during_session:
  - After EVERY task: run mandatory_task_reporting
  - After 3+ tasks: full checkpoint with progress bars and scope check
  - On any out-of-scope discovery: pause and surface, do not execute
  - On any security concern: stop and surface immediately

on_session_end:
  1. Generate full session summary with file paths
  2. Update CHANGELOG.md with new session entry
  3. Update PROJECT_PLAN.md: mark completed tasks, update progress
  4. Propose commit: "docs: update project state after session [NNN]"
  5. Recommend model for next session based on planned work

if_human_forgets:
  - Run on_session_start automatically if not invoked before first task
  - Run on_session_end automatically as final action before closing
  - The protocol cannot be disabled mid-session
```

For the slash commands that trigger each phase, see [`commands/`](../commands/). The most important: `/plan-session` (Phase 1) and `/end-session` (Phase 3).

For the template with the full `mandatory_task_reporting` block, see [`templates/CLAUDE.md`](../templates/CLAUDE.md).
