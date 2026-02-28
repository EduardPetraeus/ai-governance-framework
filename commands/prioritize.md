# /prioritize

Read the full project backlog and produce a ranked list of tasks. The goal is to
answer: "If we can only do 3 things this sprint, what should they be?"

Use this command at sprint planning, when the backlog is growing unwieldy, or when
you need to decide what to put in the next session.

## Steps

1. Read PROJECT_PLAN.md completely:
   - All phases and their task tables
   - The discovered tasks section
   - Any blocked tasks

2. Apply the prioritization framework (in order of weight):

   **Tier 1 — Sprint commitment (highest weight)**
   Tasks already committed to the current sprint. These should be done before anything else
   unless they are blocked. Incomplete sprint commitments carry a "commitment debt" into
   the next sprint.

   **Tier 2 — Dependency unblocking**
   Tasks that, if completed, unblock 2 or more other tasks. These have a multiplier effect.
   A task that unblocks 3 others is worth doing before a self-contained task of equal effort.

   **Tier 3 — Value/effort ratio**
   Estimated value divided by estimated effort.
   - High value, low effort (quick wins): prioritize
   - High value, high effort: schedule for a dedicated session
   - Low value, low effort: batch at sprint end
   - Low value, high effort: reconsider whether they belong in the project at all

   **Tier 4 — Risk reduction**
   Tasks that reduce project risk: security hardening, removing technical debt that is
   actively causing problems, documenting decisions that could be made wrongly by future
   sessions.

3. Produce the ranked list with reasoning:

---

## Prioritized Backlog

**Current sprint:** [Sprint N — dates]
**Unstarted sprint tasks:** [N]
**Discovered tasks awaiting triage:** [N]
**Total backlog:** [N tasks across all phases]

### Recommended for this sprint (do now)

**1. [Task name]**
Phase: [phase] | Estimated: [effort]
Why first: [specific reasoning — sprint commitment, dependency unblocking, etc.]
Blocks if skipped: [what cannot be done until this is done]

**2. [Task name]**
Phase: [phase] | Estimated: [effort]
Why second: [specific reasoning]
Blocks if skipped: [what cannot be done until this is done]

**3. [Task name]**
Phase: [phase] | Estimated: [effort]
Why third: [specific reasoning]
Blocks if skipped: [none / specific]

### Quick wins (do these if there is time remaining)

**4. [Task name]** — [effort] — [why it's a quick win]
**5. [Task name]** — [effort] — [why it's a quick win]

### Scheduled for next sprint

**6. [Task name]** — [phase] — [why it is not urgent now]
**7. [Task name]** — [phase] — [why it is not urgent now]

### Reconsider (low value or unclear)

- [Task name]: [why this task's value is unclear or low — ask whether to keep it]

### Not recommended (blocked)

- [Task name]: Blocked by [reason]. Cannot be prioritized until [what needs to happen].

---

## Notes for the agent

- If PROJECT_PLAN.md has no discovered tasks: the discovered tasks section can be skipped
- If all sprint tasks are complete: say so and prioritize from the next phase
- Do not include tasks from future phases in the "do now" list unless current sprint is empty
- If two tasks are equally prioritized, pick the one that enables better velocity tracking
  (completing a task is better than half-finishing two)
- If the user provides additional context ("we have 2 hours today"), factor that into the
  recommendation: "Given 2 hours, we can realistically complete tasks 1 and 2"

---

## Example output

Prioritized Backlog

**Current sprint:** Sprint 3 — 2025-03-15 to 2025-03-22
**Unstarted sprint tasks:** 3
**Discovered tasks awaiting triage:** 5
**Total backlog:** 14 tasks

### Recommended for this sprint (do now)

**1. Silver transform for Shopify orders**
Phase: Phase 2 | Estimated: 1 session
Why first: Sprint commitment. This is the last data transform task and it directly
enables the dashboard work in Phase 3. Completing it closes the current sprint goal.
Blocks if skipped: Dashboard build (Phase 3, 3 tasks), sprint retrospective

**2. Add Shopify to ARCHITECTURE.md integration points**
Phase: Discovered | Estimated: 15 minutes
Why second: Discovered last session, quick win. ARCHITECTURE.md is currently out of sync
with the code — agents reading it in future sessions will have incorrect information.
Blocks if skipped: Documentation accuracy for future sessions

**3. Write ADR for message queue decision**
Phase: Phase 2 pre-requisite | Estimated: 30 minutes
Why third: The notification system (Phase 3 task 1) cannot start until this decision is made.
Writing the ADR this sprint means Phase 3 can start without a blocking decision.
Blocks if skipped: Notification system build (Phase 3, 2 tasks)

### Quick wins (do these if there is time remaining)

**4. Document bronze layer schema for Shopify orders** — 20 min — Future sessions need this
**5. Add webhook signature verification for Stripe** — 30 min — Security improvement, low effort

### Scheduled for next sprint

**6. Silver transform for Oura sleep** — Phase 2 — Not blocking anything current
**7. Notification system** — Phase 3 — Waiting on ADR decision (item 3 above)

### Reconsider (low value or unclear)

- "AbstractPipelineValidator": This class exists in the codebase but has no implementation
  and no tests. Is this still planned? If not, delete it. If yes, when?

### Not recommended (blocked)

- Payment provider integration: Blocked by ADR for payment provider. No progress possible
  until the technology decision is made.
