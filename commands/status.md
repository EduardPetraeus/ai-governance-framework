# /status

Show the current project state as a quick snapshot. This should take 30 seconds to read — it is a status check, not a detailed report. Output must be scannable.

## Steps

1. Read PROJECT_PLAN.md:
   - Current phase and sprint goal
   - Count tasks by status: complete, in progress, planned, blocked

2. Read CHANGELOG.md (last 3 entries):
   - Recent momentum: what shipped in the last 2-3 sessions
   - Any discovered tasks not yet triaged

3. Recall this session's work (from your conversation memory):
   - Tasks completed so far in THIS session
   - What is currently in progress
   - Any blockers encountered

4. Output the status block in the format below.

## Output format

---

## Project Status

**[Project Name]** | Phase [N] — [Phase name] | [YYYY-MM-DD]

### Sprint goal
[Sprint goal from PROJECT_PLAN.md — one line]

### Phase progress
```
Phase [N]: [N/M complete]
[████████████░░░░░░░░] 60%  — [K tasks remaining]
```

Use block characters for the progress bar: 20 characters total, filled (█) and unfilled (░) proportional to completion percentage.

### Sprint tasks

| Status | Task | Notes |
|--------|------|-------|
| ✅ | [Completed task] | Session NNN |
| ✅ | [Completed task] | Session NNN |
| 🔵 | [In progress task] | Started this session |
| ⬜ | [Planned task] | Unstarted |
| ❌ | [Blocked task] | Blocked: [reason] |

### This session
**Completed:** [N tasks]
[Bullet list of what has been done in this session]

**In progress:** [Current task name, or "Nothing — between tasks"]

### Blockers
[List blocked tasks with reasons, or "None."]

### Untriaged discovered tasks
[List from PROJECT_PLAN.md discovered section and recent CHANGELOG entries, or "None."]

### Recommended next
**[Task name]** — [One sentence: why this is the right next step]

---

**Continue with [recommended task]?**

---

## Rules

- If PROJECT_PLAN.md has not been read in this session yet, read it before producing output.
- The progress bar must use exactly 20 characters (█ and ░).
- If no work has been done yet this session, say "Nothing yet" in the "This session" section.
- If there are no blockers, say "None." — do not omit the section.
- Keep the entire output under 40 lines. This is a quick-glance report.
- Do not include explanations of what the sections mean. The format is self-explanatory.

---

## Example output

## Project Status

**HealthReporting** | Phase 2 — Core Integrations | 2026-02-28

### Sprint goal
All API connectors built and writing to bronze layer

### Phase progress
```
Phase 2: [5/7 complete]
[██████████████░░░░░░] 71%  — 2 tasks remaining
```

### Sprint tasks

| Status | Task | Notes |
|--------|------|-------|
| ✅ | Build Stripe connector | Session 008 |
| ✅ | Build Oura connector | Session 009 |
| ✅ | Build Withings connector | Session 010 |
| ✅ | Build Shopify connector | Session 012 |
| ✅ | Build HubSpot connector | This session |
| 🔵 | Silver transform for Shopify | In progress |
| ⬜ | Silver transform for Oura | Unstarted |

### This session
**Completed:** 1 task
- Built HubSpot connector with cursor pagination and rate limit tracking

**In progress:** Silver transform for Shopify orders

### Blockers
None.

### Untriaged discovered tasks
- Document bronze layer schema for Shopify orders (Session 012)
- Investigate HubSpot webhooks for real-time sync (Session 014)

### Recommended next
**Silver transform for Oura sleep** — Last remaining sprint task. Completing it finishes the Phase 2 sprint goal.

---

**Continue with Oura sleep transform after finishing Shopify?**
