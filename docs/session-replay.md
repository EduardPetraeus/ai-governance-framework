# Session Replay: Understanding What Went Wrong

## The Problem

Something broke in production. The code was AI-generated three sessions ago. You need to
understand: what was the agent asked to do? What did it actually do? Why did it make that
choice? What context did it have at the time?

Currently: you have CHANGELOG.md entries and git commits. That tells you WHAT changed.
It does not tell you WHY the agent made specific decisions, what context it was operating
from, how confident it was, or what alternatives it considered and rejected.

The gap between "what changed" and "why it was done that way" is where post-incident
investigation gets stuck. Session replay fills that gap.

---

## What Session Replay Captures

Every session produces a replay artifact stored in `.session-logs/`. It records:

**1. Session metadata**: date, session number, model used, developer, duration, tasks
completed vs. scoped, governance compliance score.

**2. Task chain**: each task in sequence with input (what was asked or inferred from the
plan), output (what was produced), and files affected.

**3. Decision points**: where the agent chose between options. The decision, the rationale,
and the alternatives that were not chosen. This is the most valuable section for
post-incident analysis — it reveals whether the agent made a reasonable choice given its
context or whether its reasoning was flawed.

**4. Context used**: which sections of MEMORY.md, ARCHITECTURE.md, PROJECT_PLAN.md were
referenced during the session. This identifies stale context that may have contributed to
incorrect decisions.

**5. Confidence scores**: per-task confidence and any flags raised. Low-confidence tasks
that were approved and later caused problems are a direct signal that the approval process
needs strengthening.

**6. Governance events**: sync results (drift detected?), security scan results, kill switch
triggers (if any), model mismatch flags.

---

## Session Log Format

Auto-generated at session end as `.session-logs/session-YYYY-MM-DD-NNN.md`:

```markdown
# Session Log — YYYY-MM-DD-NNN

## Metadata
- Session: NNN
- Date: YYYY-MM-DD
- Model: [model name and version]
- Developer: [username or initials]
- Duration: [N] minutes
- Tasks completed: [N] / [M scoped]
- Tasks carried over: [list]
- Governance compliance: [percentage or description]

## Scope
Agreed at session start: "[scope confirmed with the human]"
Scope changes during session: [none | description of any scope adjustments]

## Governance Events
- Governance sync: [no drift detected | specific drift flagged]
- Knowledge lifecycle: [no flags | summary of entries flagged]
- Security scans: [N]/[M] clean | [findings if any]
- Kill switch: [not triggered | trigger description and outcome]
- Model mismatch flags: [N]

## Task Chain

### Task 1: [task name]
Input: [what was asked — from PROJECT_PLAN.md or user instruction]
Confidence: [N]%
Files created: [list with paths]
Files modified: [list with paths]
Context used:
  - ARCHITECTURE.md: [sections referenced]
  - MEMORY.md: [entries referenced]
  - ADRs: [ADRs consulted]
Decision: [key decisions made during this task]
Low-confidence areas: [specific areas flagged, if any]

### Task 2: [task name]
[same format]

[continue for all tasks]

## Decisions Made This Session
[non-trivial choices that future sessions or developers need to understand]

1. [Decision title]: [what was chosen] — [why] — [alternatives not chosen]

## Session Summary
[2-4 sentences: what was accomplished, what was deferred, key outcomes]
```

---

## When to Use Session Replay

### Post-Incident Investigation

"A bug appeared in production. Which session introduced it?"

Use session logs to trace backward through sessions by date. For each candidate session,
review the task chain to find tasks that touched the affected component. Check the decision
points for that task — was the bug a direct result of a wrong decision, wrong context,
or an edge case neither the agent nor the human anticipated?

Session replay answers: was this a governance failure (wrong decision given correct context),
a knowledge failure (wrong context misled a correct reasoning process), or an unforeseeable
edge case?

### Compliance Audit

"Prove that AI-assisted changes to this payment flow were properly reviewed."

Session logs show: the session's scope, the tasks performed, the governance events (security
scan results, human approval points, model used for security-sensitive tasks), and the
developer who ran the session.

For compliance purposes: the session log is the AI governance audit trail.

### Learning From Good Sessions

"This session was extremely productive. What made it work well?"

Review sessions where confidence was consistently high, scope was honored, and no kill switch
triggered. Extract the patterns: how was the scope defined? What context was provided? What
decisions were made cleanly vs. with hesitation? These patterns feed back into MEMORY.md and
into session protocol improvements.

### Onboarding Demonstration

"Show a new developer what a well-governed session looks like."

Select a high-quality session log and walk through it. The task chain shows what questions
to ask before starting work. The decision points show the level of reasoning expected. The
governance events show what "clean session" looks like in practice.

---

## Storage and Retention

**Location**: `.session-logs/` directory in the project root.

**Version control**: `.session-logs/` is in `.gitignore` by default. Session logs contain
potentially sensitive context — confidence scores, referenced architectural patterns,
decision rationale — that should not be committed to the main repository.

**Retention**: 90 days locally, then archive or delete. For enterprise compliance: push to
a centralized audit system (separate from the code repository).

**Size**: approximately 2-5 KB per session as text (no diffs — those are in git). A project
with daily sessions for 90 days generates roughly 200-450 KB of session logs.

**Access**: session logs should be accessible to the developer who ran the session, their
tech lead, and any designated auditor. Not visible to all contributors by default.

---

## Generating Session Logs

Session logs are auto-generated by the `/end-session` command. The agent:
1. Compiles the session metadata from the session start
2. Reconstructs the task chain from mandatory task reporting outputs
3. Extracts governance events from the governance sync and security scan outputs
4. Synthesizes the decision points from task-level rationale logging
5. Writes the `.session-logs/session-YYYY-MM-DD-NNN.md` file

For this to work, mandatory task reporting must be running throughout the session.
Sessions that skipped task reporting produce incomplete logs. Incomplete logs are flagged
in the session metadata as `governance_compliance: partial`.

---

## Related

- [patterns/session-replay.md](../patterns/session-replay.md) — implementation pattern
- [docs/kill-switch.md](kill-switch.md) — when kill switch triggers, session log captures the event
- [docs/architecture.md](architecture.md) — Layer 4 (Observability) in the 7-layer stack
- [commands/end-session.md](../commands/end-session.md) — /end-session generates the session log
