# /status

Show the current project state. This command can be run at any point during a session
to get a snapshot of where things stand: phase progress, session work so far, blockers,
and what to do next.

Output should be quick to read — the user should be able to scan it in 30 seconds.

## Steps

1. Read PROJECT_PLAN.md:
   - Current phase and sprint goal
   - Which tasks are complete, in progress, planned, blocked

2. Read CHANGELOG.md — last 3 entries:
   - Recent momentum (what's been shipped)
   - Discovered tasks not yet triaged

3. Recall session work (from current session context):
   - What has been completed in this session so far
   - What is currently in progress

4. Produce this output:

---

## Project Status

**[Project Name]** | [Current phase] | [YYYY-MM-DD]

### Sprint goal
[Sprint goal from PROJECT_PLAN.md]

### Phase progress
[Phase name]: [N done / M total] [progress bar]
████████░░ 80% — [N remaining tasks]

### Sprint tasks

| Status | Task | Notes |
|--------|------|-------|
| ✅ | [Task] | Completed Session NNN |
| ✅ | [Task] | Completed Session NNN |
| 🔵 | [Task] | In progress this session |
| ⬜ | [Task] | Unstarted |
| ❌ | [Task] | Blocked: [reason] |

### This session
**Started:** [time if known, otherwise "this session"]
**Completed so far:** [N tasks]

[Bullet list of what has been done this session — cumulative]

**Currently working on:** [task name or "nothing yet"]

### Top blockers
[List any blocked tasks from PROJECT_PLAN.md, or "No blockers"]

### Discovered tasks (not yet triaged)
[List any discovered tasks from PROJECT_PLAN.md discovered section, or "None"]

### Recommended next task
**[Task name]** — [one sentence: why this is the right next step]

---

**Want to continue with [recommended task]?**

---

## Notes for the agent

- If PROJECT_PLAN.md has not been read in this session yet, read it before producing output
- The progress bar should use block characters: ████░░░░ (filled/unfilled)
- If no work has been done in this session yet, the "This session" section says "Nothing yet"
- If there are no blockers, say "No blockers" — do not skip the section
- Keep the output tight — this is a status check, not a detailed report
- If the user types `/status` mid-session, they want a quick look, not a 5-minute read

---

## Example output

Project Status

**HealthReporting** | Phase 2 — Core Integrations | 2025-03-15

### Sprint goal
All API connectors built and writing to bronze layer

### Phase progress
Phase 2: [5 done / 7 total]
██████████░░░░ 71% — 2 tasks remaining

### Sprint tasks

| Status | Task | Notes |
|--------|------|-------|
| ✅ | Build Stripe connector | Session 008 |
| ✅ | Build Oura connector | Session 009 |
| ✅ | Build Withings connector | Session 010 |
| ✅ | Build Shopify connector | Session 012 |
| ✅ | Integration tests for all connectors | Session 012 |
| 🔵 | Silver transform for Shopify orders | In progress |
| ⬜ | Silver transform for Oura sleep | Unstarted |

### This session
**Completed so far:** 1 task

- Started silver transform for Shopify orders (src/transforms/shopify_orders.sql — draft in progress)

**Currently working on:** shopify_orders.sql silver transform

### Top blockers
No blockers

### Discovered tasks (not yet triaged)
- Document bronze layer schema for Shopify orders (Session 012)
- Add Shopify to ARCHITECTURE.md integration points (Session 012)

### Recommended next task
**Silver transform for Oura sleep** — This is the last remaining sprint task after the
current transform is complete. Completing it finishes the sprint goal.

Want to continue with silver transform for Oura sleep after finishing the Shopify transform?
