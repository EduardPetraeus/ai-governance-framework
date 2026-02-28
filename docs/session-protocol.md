# Session Protocol

The session protocol is the most important behavioral specification in the framework. It governs how every AI session starts, runs, and ends. It is the mechanism that transforms individual agent sessions from ad-hoc conversations into governed, trackable units of work that compose into sprints, phases, and ultimately a coherent project.

---

## Why Session Protocol Matters

### The yes-man anti-pattern

Without a session protocol, AI agents fall into a predictable and destructive pattern. Call it the yes-man anti-pattern: the agent responds to whatever is most recently in context, the human approves without genuine review, and at the end of the session, neither party can clearly account for what happened.

Here is what it looks like in practice:

```
User: "Let's work on the Oura connector."

Agent: "I've created the connector in source_connectors/oura/sleep.py with three
        endpoints and added error handling."

User: "Ok."

Agent: "I also refactored the ingestion engine to support the new connector's interface.
        This required changes to six files in the core module."

User: "Ok."

Agent: "I've updated the sources_config.yaml and added five new entities. I also
        noticed the naming conventions in silver/ were inconsistent so I standardized
        those while I was in there."

User: "Ok."

Agent: "Done! The connector is fully integrated. Want to work on something else?"

User: "Wait — what exactly did we just change?"
```

The problem in this dialogue is structural, not disciplinary. The agent is doing what agents do: being helpful, completing tasks, making adjacent improvements it noticed along the way. The human is doing what humans do under cognitive load with a fast-moving agent: approving incrementally without tracking the aggregate.

Notice what the agent reported: task completion. What it did not report: scope expansion (the ingestion engine refactor was not requested), cross-concern changes (silver/ naming was not in scope), or how any of this relates to the sprint goal. The human has no idea whether the session advanced the project, created new technical debt, or introduced a change that will break something downstream.

### The drift problem

Multiply this across 20 sessions over four weeks. Each session produces changes that are locally sensible and globally incoherent. The architecture drifts from the design decisions made in week one. The codebase has six patterns where one was intended. CHANGELOG.md has not been updated since session 3. Project plan still shows 0% progress on tasks that were completed two weeks ago.

This is not a failure of the AI. It is a failure of governance design. The system allowed drift by providing no mechanism to prevent it.

The session protocol is that mechanism. It makes scope explicit before work begins, makes progress visible after every task, and makes project state accurate after every session. It does not slow the agent down — it directs the agent's speed at the right target.

---

## Phase 1: Session Start

**Goal: Orient the agent against the current project state before any code is written.**

The session start protocol runs automatically when `/plan-session` is invoked, or at the first message in a new Claude Code session if the CLAUDE.md session protocol is active.

### Governance sync

The agent reads three files at minimum:

1. **`PROJECT_PLAN.md`** — current phase, sprint goal, task breakdown, dependencies, progress percentages
2. **`CHANGELOG.md`** — last 2–3 session entries, providing recent history: what was done, what was carried over, what decisions were made
3. **`ARCHITECTURE.md`** (if it exists at Level 2+) — current state of the built system, component inventory

This is not a courtesy read. The agent uses this information to build its working model of the project state. Every response in the session is informed by this context. Without the governance sync, the agent is operating from training data and the immediate session context — which is far less accurate than the actual project state.

### Model identification

The agent identifies itself:

```
Model: claude-sonnet-4-6
Session: [new session / continuing from session NNN]
Governance files read: PROJECT_PLAN.md, CHANGELOG.md, ARCHITECTURE.md
```

This serves two purposes: it makes the session's model visible in the audit trail (CHANGELOG records which model was used), and it enables model routing checks — if the planned session tasks require a more capable model than the current one, the agent flags it now rather than halfway through.

### Sprint status presentation

Before the human describes what they want to do, the agent presents what the project state says should happen:

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

The agent is doing the project management work that the human would otherwise need to do before every session: reading the previous state, identifying what is next, and proposing a concrete plan. The human's job is to confirm, adjust, or redirect. They are making a decision, not reconstructing context.

### Scope confirmation

**No code is written before scope is confirmed.**

This is a hard rule, not a soft guideline. The agent must receive explicit confirmation of what the session will do before it executes any file modification. The confirmation can be brief — "yes, proceed" — but it must happen. If the human wants to adjust the proposed scope, the agent revises and presents the adjusted plan for confirmation.

This single rule eliminates the most common governance failure: sessions that start coding immediately and end with scope nobody explicitly authorized.

---

## Phase 2: During Session

**Goal: Keep the human oriented while maintaining execution momentum.**

### Mandatory task reporting

After every completed task, without exception, the agent presents a structured status report. This is not optional, it cannot be suppressed by the user saying "just continue," and it is not summarized away into a single line. See the [mandatory_task_reporting specification](#mandatory_task_reporting-specification) below for the exact format.

The key design decision: status is pushed, never pulled. The human does not ask "how are we doing?" — the agent tells them after every task, whether they asked or not. This is specified in `CLAUDE.md` as mandatory behavior.

### Checkpoint pause after 3+ tasks

After three or more consecutive tasks without an explicit human direction change, the agent pauses for a medium-weight checkpoint before continuing:

```
Session checkpoint — 3 tasks completed.

Done this session:
  [x] Resolved Lifesum API credential issue
  [x] Built Lifesum connector (src/connectors/lifesum/activity.py)
  [x] Ran smoke test — PASSED

In progress:
  [ ] Full connector validation suite (starting now)

Remaining in scope:
  [ ] (none — this is the final task)

Sprint goal: "All source connectors built and tested"
Progress: ██████████ 93% (13/14 tasks)

Continue with validation suite, or adjust scope?
```

This pause serves a different function than the per-task report. It gives the human a higher-level view of session progress and a natural decision point: continue on the current path, or adjust scope because something new has come up. Without this pause, a human who said "yes, proceed" at session start may not re-engage until the session ends — and by then, the scope may have drifted.

### Scope creep detection

The agent monitors for two drift patterns:

**Authorized scope expansion:** The agent is about to do something not in the confirmed scope because it discovered a dependency or a problem that makes it necessary. The agent pauses: "To complete the Lifesum connector, I need to update the ingestion engine interface. This was not in the confirmed scope. Approve this addition, or should I work around it?"

**Out-of-scope discovery:** The agent notices something that should probably be done but was not in scope. It logs it, does not do it, and reports it: "Noticed: the Withings connector is missing null handling for the `vo2_max` field. I have not touched this — logging as a discovered task. Should I add it to the backlog?"

The agent logs discovered tasks in a "discovered tasks" section of the session summary. They are evaluated at sprint planning, not executed mid-session without authorization.

### Security scan per file

Each time the agent modifies a file, it performs a lightweight security check:

- No credentials, API keys, or tokens in the file
- No hardcoded production paths or environment-specific strings
- No PII values embedded in code or configuration
- No new dependencies without pinned versions

If a potential security issue is found, the agent stops and surfaces it: "Before committing this file, I noticed a potential issue: line 47 contains what appears to be a connection string with credentials embedded. Please review before I proceed."

---

## Phase 3: Session End

**Goal: Leave the project in a better-documented state than it was at session start.**

### Session summary

The agent generates a complete session summary covering:

- All tasks completed (with specific file paths, not just descriptions)
- Tasks attempted but not completed, and why
- Decisions made during the session that have architectural or design significance
- Discovered tasks that were not in scope but should be considered
- Sprint goal progress: percentage before and after the session

### Auto-update governance files

The agent updates two files automatically:

**`CHANGELOG.md`** — a new entry at the top following the standard format:

```markdown
## 2026-02-28 — Session 009: Lifesum Connector + Sprint Completion

**Phase:** Phase 1 — Bronze Layer
**Agent:** Claude Code (claude-sonnet-4-6)
**Duration:** ~80 minutes
**Tasks completed:** 3/3

### What was done
- Resolved Lifesum API credential issue (updated .env.example with new key names)
- Built Lifesum activity connector: src/connectors/lifesum/activity.py
- Added 4 entities to sources_config.yaml
- Ran full connector validation suite — all 14 connectors PASSED

### What was NOT done
- Nothing carried over

### Decisions made
- Lifesum API returns timestamps in local time, not UTC. Normalized to UTC at ingestion.
  Rationale: consistency with all other connectors. See DECISIONS.md for full note.

### Goal progress
Sprint goal: "All source connectors built and tested" — COMPLETE (14/14)
Phase 1: ██████████ 100%
```

**`PROJECT_PLAN.md`** — completed tasks are marked `[x]`, progress percentages are updated, and the sprint goal status is marked complete if applicable.

### Commit with standard message

The agent proposes a commit for the governance file updates with the standard format:

```
docs: update project state after session 009

- CHANGELOG.md: session 009 summary, sprint goal completion
- PROJECT_PLAN.md: 14/14 tasks marked complete, Phase 1 at 100%
```

The human reviews and commits. This commit is the formal record that the session occurred and the project state is current. Without this commit, the next session starts without accurate history.

---

## Phase 4: If the Human Forgets

**Goal: The protocol runs even when the human does not initiate it.**

Sometimes a session starts with an urgent "just fix this bug" request. Sometimes the human is tired and forgets to run `/plan-session`. The protocol runs anyway.

When the agent receives its first message in a new session and detects that the session start protocol has not run, it inserts it before responding to the request:

```
[Session start protocol — running automatically]

Governance sync complete. Before addressing your request:

Project: customer-data-pipeline
Phase: Phase 1 — Bronze Layer
Sprint goal: "All source connectors built and tested" (93% complete)
Last session: 008, 2026-02-26 (Withings + Strava connectors)

You asked to fix the timestamp parsing bug in the Oura connector.
This is within the current sprint scope.

Proceeding with the bug fix. I will run the session end protocol when we are done.
```

Similarly, if the human ends the conversation without running `/end-session`, the agent inserts the session end protocol as its final action: "Before we close, let me update the governance files..." This prevents the common failure mode where sessions produce work but no documentation.

The session protocol runs whether or not the human remembers to invoke it. This is the "governance cannot be turned off mid-session" principle from `CLAUDE.md`.

---

## mandatory_task_reporting Specification

This is the exact specification as it appears in `CLAUDE.md`, governing what the agent must report after every completed task. It cannot be suppressed.

```
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

**The exact output format:**

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
│ [Phase name]: [████████░░] [N]% (was [M]%)          │
│ Sprint goal: "[goal description]" — [X]/[Y] done    │
│ Remaining: [item 1], [item 2]                        │
├─────────────────────────────────────────────────────┤
│ Next: [next task] (est. [time])                      │
│ Continue, or adjust?                                 │
└─────────────────────────────────────────────────────┘
```

This format uses box-drawing characters for visual clarity. Progress bars use `█` for completed and `░` for remaining. The structure is fixed — the agent fills in the values but does not change the structure. This makes the output immediately scannable without reading every word.

A concrete example from a real session:

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

---

## Escalation Model

The protocol operates at four escalation levels, each triggered by a different condition. The levels are not mutually exclusive — a session end always includes everything from all previous levels.

| Trigger | Level | Content |
|---------|-------|---------|
| After every task | Light | 3–5 lines: what changed, goal impact, next step |
| After 3+ consecutive tasks | Medium | Full checkpoint: progress bars, done/doing/remaining, scope check, option to redirect |
| Sprint goal completed | Heavy | Full sprint review: all tasks, all goal impacts, architecture changes, what to do next sprint |
| Session end | Comprehensive | Everything above plus governance file updates, commit proposal, session summary with file paths |

**Light reporting** is the baseline: fast, structured, always present. It does not require the human to do anything — it provides just enough information to detect if the session is heading in the wrong direction.

**Medium reporting** is the pause point. The human gets a full picture and an active choice: continue as planned, or redirect. This is where scope drift is caught before it compounds.

**Heavy reporting** happens when a sprint goal is completed. This is a meaningful milestone event, not just another task completion. The agent provides a full review suitable for sharing with stakeholders: what was built, what decisions were made, what the next phase looks like.

**Comprehensive reporting** at session end produces the governance artifacts. This is not a summary for the human — it is the formal record of the session: CHANGELOG entry, PROJECT_PLAN.md updates, commit message. It closes the governance loop.

---

## The Yes-Man Anti-Pattern: Detailed Explanation

The yes-man anti-pattern deserves deeper examination because it is the default behavior of ungoverned AI agents, and the session protocol is specifically designed to prevent it.

### Why it happens

Agents are trained to be helpful and to satisfy the user's immediate request. In a conversation, the path of least resistance is to complete tasks, report them briefly, and wait for the next instruction. The human approves quickly because approving feels like making progress. Neither party is doing anything wrong locally — the pattern emerges from the structure of the interaction.

The agent has no stake in whether the aggregate work advances the project goal. It does not experience the frustration of reaching sprint end and realizing the work was scattered. Each task completion feels like success because it is locally correct.

The human is in a mode of low-engagement approval. Evaluating each task against the sprint goal requires them to hold the entire project context in working memory while also reviewing the agent's output. This is cognitively expensive. The easier path is to approve and move forward.

### The structural solution

The session protocol does not rely on the human maintaining full project context in their head. It provides that context automatically:

1. **At session start:** The agent presents the sprint goal and proposed scope. The human reviews against a displayed summary, not their own memory.
2. **After each task:** The goal impact is shown explicitly. The human does not need to calculate whether the task advanced the project — the agent shows the before/after progress percentage.
3. **At the checkpoint:** The full done/doing/remaining view is presented. The human can see at a glance whether the session is on track.

This shifts the human's cognitive role from "maintain full project context" to "evaluate specific information presented clearly." The latter is dramatically less expensive. It is the difference between designing a UI that requires users to remember state versus one that displays state at every interaction point.

### What governed sessions look like

With the protocol in place, the same session as the yes-man example becomes:

```
Agent: [Session start] Sprint goal: "All API connectors." Proposed scope: Oura connector.
       Confirm to proceed?

User: "Yes."

Agent: [Task complete] Oura sleep connector built.
       Phase 1: ██████░░░░ 60% (was 45%). Sprint: 2/5 connectors done.
       Remaining: Withings, Strava, Lifesum.
       Next: Withings connector. Continue?

User: "Continue."

Agent: [Task complete] Withings connector built.
       Phase 1: ████████░░ 75% (was 60%). Sprint: 3/5 connectors done.
       Next: Strava. Continue?

User: "Yes — but before Strava, can you also refactor the ingestion engine?"

Agent: "The ingestion engine refactor is not in the confirmed scope for this session.
        Options:
        (a) Add it to this session's scope and continue
        (b) Log it as a discovered task for the next session and continue with Strava
        Which do you prefer?"

User: "Log it, continue with Strava."

Agent: "Logged as discovered task. Continuing with Strava connector."
```

The human is making real decisions, not reflexively approving. The scope expansion request is handled explicitly rather than silently absorbed. At session end, both parties can account precisely for what happened and why.

---

## Task-to-Goal Mapping: The Core Innovation

The most important structural innovation in the session protocol is the requirement that every task maps to a project goal. This is not about adding bureaucracy to task completion — it is about changing the fundamental unit of work.

In an ungoverned session, the unit of work is a task: "Build the Oura connector." Done or not done.

In a governed session, the unit of work is a task-goal pair: "Build the Oura connector" → "Advance the sprint goal 'All API connectors' from 45% to 60%." The task is only meaningful in relation to the goal it advances.

This change has cascading effects:

**The agent cannot work on out-of-scope tasks without surfacing them.** If the agent cannot map a proposed task to a goal in PROJECT_PLAN.md, it must stop and ask: "This task is not in the current sprint scope. Should I add it, or skip it?" There is no silent scope expansion.

**The human can evaluate each task against its stated goal, not against a vague sense of progress.** "Did building the Oura connector advance the sprint goal by 15%?" is a concrete, evaluable question. "Did that seem useful?" is not.

**The project plan stays accurate.** Because every task maps to a project plan item, the project plan is updated automatically at session end to reflect precisely what was done. There is no gap between the plan and reality — the plan is reality.

**Historical sessions are legible.** Looking at CHANGELOG entries from six months ago, you can read exactly what each session accomplished and why each task was done. This makes the project's history coherent to new team members, to auditors, and to yourself three months later when you need to understand a decision made in session 17.

The task-to-goal mapping is what makes AI-assisted development governable at scale. Without it, fast is fast but incoherent. With it, fast is fast and aligned.

---

## Configuration Reference

The session protocol is specified in `CLAUDE.md` and executed by the agent. The relevant sections of `CLAUDE.md` are:

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
  - After EVERY task: run mandatory_task_reporting (see below)
  - After 3+ tasks: full checkpoint with progress bars and scope check
  - On any out-of-scope discovery: pause and surface, do not silently execute
  - On any security concern: stop and surface immediately

on_session_end:
  1. Generate full session summary with file paths
  2. Update CHANGELOG.md with new session entry
  3. Update PROJECT_PLAN.md: mark completed tasks, update progress
  4. Propose commit: "docs: update project state after session [NNN]"

if_human_forgets:
  - Run on_session_start automatically if not invoked before first task
  - Run on_session_end automatically as final action before closing
  - The protocol cannot be disabled mid-session
```

To implement this in your project, copy the `session_protocol` section from [`templates/CLAUDE.md.template`](../templates/CLAUDE.md.template) and customize the file paths for your project structure. The mandatory_task_reporting format should remain unchanged — it is designed to be consistent and immediately readable across all sessions.

For the slash commands that trigger each phase, see the definitions in [`commands/`](../commands/). The most important are `/plan-session` (Phase 1) and `/end-session` (Phase 3).
