# /prioritize

Read the full project backlog and produce a ranked task list. Answer the question: "If we can only do N things, what should they be and in what order?"

Use this when scope is unclear, when the backlog is growing, when sprint planning is needed, or when the user provides a time constraint ("we have 2 hours").

## Steps

### Step 1: Read the full backlog

Read PROJECT_PLAN.md completely:
- All phases and their task tables
- The discovered tasks section
- Any blocked tasks and their blockers
- The current sprint commitments
- Task dependencies (if documented)

Read CHANGELOG.md (last 5 entries):
- What was recently completed (avoid recommending work that is already done)
- Discovered tasks from recent sessions

### Step 2: Apply the prioritization framework

Rank all incomplete tasks using these four tiers, in order of weight:

**Tier 1 — Sprint commitment (highest weight)**
Tasks already committed to the current sprint. These come first unless blocked. Incomplete sprint commitments carry "commitment debt" into the next sprint — this is visible to the team and erodes planning credibility.

**Tier 2 — Dependency unblocking**
Tasks that, once completed, unblock 2 or more other tasks. These have a multiplier effect. Count the downstream tasks each candidate unblocks. A task that unblocks 3 others is worth doing before a self-contained task of equal effort.

**Tier 3 — Value/effort ratio**
Estimate value (impact on project goals) and effort (time to complete):
- High value, low effort → prioritize (quick wins)
- High value, high effort → schedule for a dedicated session
- Low value, low effort → batch at the end of a sprint
- Low value, high effort → question whether it belongs in the project

**Tier 4 — Risk reduction**
Tasks that reduce project risk: security hardening, removing tech debt that is actively causing problems, documenting decisions that future sessions could get wrong, fixing flaky tests, addressing discovered bugs.

### Step 3: Apply time constraints

If the user provided a time estimate ("we have 2 hours"), factor it in:
- Estimate time for each task
- Only include tasks that fit within the time budget in "Recommended now"
- Move others to "Next sprint"

### Step 4: Output the ranked list

---

## Prioritized Backlog

**Sprint:** [Sprint N — date range or "current"]
**Unstarted sprint tasks:** [N]
**Discovered tasks (untriaged):** [N]
**Total backlog:** [N tasks across all phases]

### Do now (recommended for this session/sprint)

**1. [Task name]**
Phase: [Phase N] | Effort: [estimate] | Tier: [Sprint commitment / Dependency / Quick win / Risk]
Why first: [Specific reasoning — what makes this the highest priority right now]
Unblocks: [What cannot start until this is done, or "Nothing — self-contained"]

**2. [Task name]**
Phase: [Phase N] | Effort: [estimate] | Tier: [tier]
Why second: [Specific reasoning]
Unblocks: [What it enables]

**3. [Task name]**
Phase: [Phase N] | Effort: [estimate] | Tier: [tier]
Why third: [Specific reasoning]
Unblocks: [What it enables, or "Nothing"]

### Quick wins (if time remains)

**4. [Task name]** — [effort] — [why it qualifies as a quick win]
**5. [Task name]** — [effort] — [why it qualifies]

### Next sprint (defer these)

**6. [Task name]** — Phase [N] — [why it is not urgent now: no dependencies on it, belongs to future phase, etc.]
**7. [Task name]** — Phase [N] — [reason for deferral]

### Reconsider (questionable value)

- **[Task name]:** [Why the value is unclear. Ask the user: keep, defer, or drop?]

### Blocked (cannot prioritize until resolved)

- **[Task name]:** Blocked by [specific blocker]. Cannot start until [what needs to happen].
  Recommendation: [Can the blocker be resolved this session? Should it be escalated?]

---

### Prioritization summary

| Rank | Task | Tier | Effort | Cumulative time |
|------|------|------|--------|-----------------|
| 1 | [Task] | Sprint | [est] | [running total] |
| 2 | [Task] | Dependency | [est] | [running total] |
| 3 | [Task] | Quick win | [est] | [running total] |
| 4 | [Task] | Quick win | [est] | [running total] |
| 5 | [Task] | Risk | [est] | [running total] |

---

## Rules

- Do not include tasks from future phases in "Do now" unless the current sprint is empty.
- If all sprint tasks are complete: say so and recommend pulling from the next phase.
- If two tasks are equally ranked, prefer the one that produces a completable unit of work (finishing 1 task is better than half-finishing 2).
- If the user says "we have [time]": adjust recommendations to fit. Say "Given [time], I recommend tasks 1 and 2. Task 3 would take us over the time budget."
- Never rank a blocked task in the "Do now" section. Blocked tasks go to their own section.
- Show your reasoning. "Sprint commitment" is not enough — say which sprint and why completing it matters.

---

## Example output

## Prioritized Backlog

**Sprint:** Sprint 4 — 2026-02-24 to 2026-03-02
**Unstarted sprint tasks:** 3
**Discovered tasks (untriaged):** 4
**Total backlog:** 16 tasks across 4 phases

### Do now

**1. Write integration tests for HubSpot connector**
Phase: Phase 2 | Effort: 1 session | Tier: Sprint commitment
Why first: Sprint commitment. The HubSpot connector was built last session with zero tests. It cannot be merged to main without test coverage. This is the definition-of-done gap from Session 014.
Unblocks: HubSpot connector merge, silver transform for HubSpot contacts

**2. Silver transform for Shopify orders**
Phase: Phase 2 | Effort: 1 session | Tier: Sprint commitment + Dependency
Why second: Sprint commitment and dependency unblocking. This is the last data transform needed before the dashboard work in Phase 3 can begin. Completing it closes the Phase 2 sprint goal for Shopify.
Unblocks: Dashboard build (Phase 3, 3 tasks)

**3. Add Shopify to ARCHITECTURE.md**
Phase: Discovered | Effort: 15 minutes | Tier: Quick win + Risk
Why third: Quick win that reduces documentation drift risk. ARCHITECTURE.md is currently out of sync with the code. Agents reading it in future sessions will have incorrect information about available integrations.
Unblocks: Nothing — documentation-only

### Quick wins (if time remains)

**4. Document bronze layer schema for Shopify orders** — 20 min — Future sessions need this to build transforms correctly
**5. Fix flaky test in test_stripe_connector.py:test_rate_limit** — 15 min — Fails intermittently in CI, wastes reviewer time

### Next sprint

**6. Silver transform for Oura sleep** — Phase 2 — Not blocking anything in Phase 3. Can be pulled into Sprint 5.
**7. Build dashboard API endpoints** — Phase 3 — Waiting on Shopify transform (task #2 above). Ready once that is done.

### Reconsider

- **"AbstractPipelineValidator" implementation:** This class has existed for 3 sprints with no implementation and no tests. It was planned for Phase 2 but has never been started. Is this still needed, or should it be removed? The code-simplifier agent flagged it as dead code in Session 011.

### Blocked

- **Notification system:** Blocked by ADR for message queue technology. No progress possible until the ADR is written and accepted. Recommendation: write the ADR this session (30 min) to unblock this for Sprint 5.

---

### Prioritization summary

| Rank | Task | Tier | Effort | Cumulative |
|------|------|------|--------|------------|
| 1 | HubSpot tests | Sprint | 1 session | 1 session |
| 2 | Shopify silver transform | Sprint + Dep | 1 session | 2 sessions |
| 3 | ARCHITECTURE.md update | Quick win | 15 min | 2 sessions + 15 min |
| 4 | Bronze schema docs | Quick win | 20 min | 2 sessions + 35 min |
| 5 | Fix flaky test | Risk | 15 min | 2 sessions + 50 min |
