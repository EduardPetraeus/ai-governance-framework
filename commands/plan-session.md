# /plan-session

You are starting a governed development session. Your job is to orient yourself in the project, present a clear picture of where things stand, and confirm scope before any code is written. Do NOT write code until the user has explicitly confirmed what to work on.

## Steps

### Step 1: Read project state

Read these files in order. If a file does not exist, note it and continue.

1. **PROJECT_PLAN.md** — Read completely.
   - Identify the current phase name and number
   - Identify the sprint goal
   - List all tasks with their status (Complete / In Progress / Planned / Blocked)
   - Calculate sprint progress: tasks_complete / tasks_total as a percentage

2. **CHANGELOG.md** — Read the last 5 entries only (most recent 5 session headers).
   - What was accomplished in the most recent session?
   - What model was used?
   - What model was recommended for the next session (this session)?
   - What were the top 3 recommended tasks?
   - Are there discovered tasks from recent sessions that have not been triaged?

3. **ARCHITECTURE.md** — Read if it exists.
   - Note any active architectural decisions relevant to the current sprint
   - Note any open decisions or pending ADRs

4. **MEMORY.md** — Read if it exists.
   - Note confirmed patterns (things that work well)
   - Note anti-patterns to avoid (things that failed or caused problems)
   - Note any session-specific guidance recorded for future sessions

5. **CLAUDE.md** — Read the model_routing section if it exists.
   - Determine which model types are recommended for which task types
   - Compare your current model to the recommended model for today's likely tasks

### Step 2: Present the session brief

Output the following format exactly:

---

## Session Brief

**Project:** [project_name from PROJECT_PLAN.md]
**Current phase:** [Phase N — phase name]
**Sprint goal:** [sprint goal text]
**Sprint progress:** [N/M tasks complete] ([percentage]%)

### Last session ([date from most recent CHANGELOG entry])
- [3-5 bullets summarizing what was done, from the most recent CHANGELOG entry]
- [Include any decisions that were made]

### Model context
- Running as: [your current model name — e.g., claude-sonnet-4-6]
- Last session used: [model from the most recent CHANGELOG entry]
- Recommended for this session: [recommendation from the last CHANGELOG "Next session" section]
- Assessment: [If you are the recommended model: "Correct model for planned tasks." If not: "Consider switching to [recommended model] for [specific task types]. I am optimal for [my task types]."]

### Recommended tasks (pick up to 3)

**1. [Task name]**
Priority reason: [Why this is #1 — sprint commitment? dependency unblocking? quick win?]
Estimated effort: [1 session / 2 hours / 30 minutes — based on task complexity]
Depends on: [What must be done first, or "Nothing — ready to start"]
Files likely affected: [List expected files if predictable]

**2. [Task name]**
Priority reason: [Why #2]
Estimated effort: [estimate]
Depends on: [dependency or "Nothing"]

**3. [Task name]**
Priority reason: [Why #3]
Estimated effort: [estimate]
Depends on: [dependency or "Nothing"]

### Blockers
[List any blocked tasks with their blocking reason, or "No blockers."]

### Untriaged discovered tasks
[List discovered tasks from recent CHANGELOG entries that are not yet assigned to a phase, or "None."]

### Patterns to remember (from MEMORY.md)
[List relevant patterns/anti-patterns if MEMORY.md exists, or omit this section]

---

**What would you like to work on?**

Options:
- "Go" or "start" — begins with task #1
- "Start with [task name]" — begins with a specific task
- "[Custom task]" — I will check if it is in the sprint scope

---

### Step 3: Handle scope confirmation

Wait for the user to respond. Do not write any code yet.

- If the user says "go" or "start": begin with recommended task #1.
- If the user says "start with [X]": begin with that task.
- If the user names a task not in the current sprint: say exactly this:
  "[Task] is not in the current sprint (Phase [N]). It is in [phase/backlog/undocumented].
  Options: (1) Add it to this sprint and start now, (2) Add it to discovered tasks for triage later, (3) Replace a planned task with it."
  Wait for the user's choice before proceeding.
- If the user says "just start" without specifying: ask one clarifying question:
  "Which of the three recommended tasks should we start with?"

### Step 4: Log session start

After scope is confirmed, add a note to your working memory:
- Session started: [timestamp]
- Planned scope: [confirmed tasks]
- Model: [your model name]

Then begin working on the confirmed task.

---

## Edge cases

- **PROJECT_PLAN.md does not exist:** Say "PROJECT_PLAN.md not found. This appears to be the first governed session. Would you like me to create it from the template? I will need: project name, current goals, and 3-5 tasks."
- **CHANGELOG.md does not exist:** Say "CHANGELOG.md not found. This is the first session. I will create it when we run /end-session."
- **No tasks remain in the current sprint:** Say "All sprint tasks are complete. Recommend: either start the next phase or run /prioritize to determine what to pull in."
- **All recommended tasks are blocked:** Say so, explain the blockers, and ask whether to work on an unblocked task from a different phase or to address the blocker directly.

---

## Example output

## Session Brief

**Project:** HealthReporting
**Current phase:** Phase 2 — Core Integrations
**Sprint goal:** All API connectors built and writing to bronze layer
**Sprint progress:** 4/7 tasks complete (57%)

### Last session (2026-02-25)
- Built Shopify connector (`src/connectors/shopify.py`) with cursor-based pagination
- Added 12 integration tests for Shopify connector, all passing
- Updated `sources_config.yaml` with Shopify as an enabled source
- Decision: Shopify uses private app auth, not OAuth (DEC-003)
- Discovered: bronze layer schema for Shopify orders needs documentation

### Model context
- Running as: claude-sonnet-4-6
- Last session used: claude-sonnet-4-6
- Recommended for this session: claude-sonnet-4-6 (feature work continues)
- Assessment: Correct model for planned tasks.

### Recommended tasks

**1. Build Withings connector**
Priority reason: Sprint commitment — next connector in sequence, unblocks health data pipeline
Estimated effort: 1 session
Depends on: Nothing — credentials in .env, BaseConnector class ready
Files likely affected: `src/connectors/withings.py` (new), `sources_config.yaml`, `tests/integration/test_withings.py` (new)

**2. Silver transform for Shopify orders**
Priority reason: Sprint commitment — unblocks dashboard work in Phase 3
Estimated effort: 1 session
Depends on: Shopify connector (complete)
Files likely affected: `src/transforms/shopify_orders.sql` (new)

**3. Add Shopify to ARCHITECTURE.md integration points**
Priority reason: Discovered task from last session — keeps documentation accurate
Estimated effort: 15 minutes
Depends on: Nothing
Files likely affected: `ARCHITECTURE.md`

### Blockers
No blockers.

### Untriaged discovered tasks
- Document bronze layer schema for Shopify orders (Session 012)

---

**What would you like to work on?**
