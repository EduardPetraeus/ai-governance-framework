# /plan-session

You are starting a new AI-assisted development session. Your job is to orient yourself,
present a clear picture of where the project stands, and confirm scope before any code
is written.

## Steps

1. Read PROJECT_PLAN.md completely.
   - Note the current phase and sprint goal
   - Identify all tasks and their status (Complete / In Progress / Planned / Blocked)
   - Calculate sprint progress: how many tasks done vs. total

2. Read CHANGELOG.md — last 5 entries only.
   - What was accomplished in the most recent session?
   - What model was used?
   - What was recommended for this session?
   - Are there any discovered tasks from recent sessions not yet triaged?

3. Read ARCHITECTURE.md if it exists.
   - Note any active architectural decisions relevant to today's work
   - Note any open decisions (things not yet resolved)

4. If MEMORY.md exists: read it.
   - Note any anti-patterns to avoid
   - Note any patterns confirmed to work

5. Present the session brief in this format:

---

## Session Brief

**Project:** [project_name from PROJECT_PLAN.md]
**Current phase:** [phase name and number]
**Sprint goal:** [sprint goal from PROJECT_PLAN.md]
**Sprint progress:** [N done / M total] ([percentage]%)

**What happened last session ([date]):**
- [3-5 bullets summarizing CHANGELOG last entry]

**Model context:**
- I am running as: [current model — claude-sonnet-4-6, claude-opus-4-6, etc.]
- Last session used: [model from last CHANGELOG entry]
- Last session recommended for today: [recommendation from last CHANGELOG entry]

**Recommended tasks for this session:**

1. [Task name] — [why it's the top priority] — Estimated: [effort]
   Depends on: [dependency or "nothing — ready to start"]

2. [Task name] — [why it's second priority] — Estimated: [effort]
   Depends on: [dependency]

3. [Task name] — [why it's third priority] — Estimated: [effort]
   Depends on: [dependency]

**Blockers / open decisions:**
- [Any blocked tasks or unresolved decisions from PROJECT_PLAN.md]

**Discovered tasks not yet triaged:**
- [Any items in PROJECT_PLAN.md discovered tasks section not yet assigned to a phase]

---

**Ready to start. What would you like to work on today?**

If you want to proceed with the top recommendation, just say "go" or "start with [task]".
If you want to adjust scope or priorities, tell me now — before any code is written.

If you choose a task not in the current sprint plan, I will flag it:
"[Task] is not in the current sprint scope (it is in [phase/backlog]). Should I add it
to the sprint and proceed, or document it as a discovered task to triage later?"

---

## Notes for the agent

- Do not write any code until the user has confirmed scope
- If PROJECT_PLAN.md does not exist: say so and offer to create it from the template
- If CHANGELOG.md does not exist: say so, note this is the first session, suggest creating it
- If the user says "just start" without specifying a task: ask one clarifying question
  ("Which of the three recommended tasks would you like to start with?")
- The model routing table in CLAUDE.md should inform which model you recommend.
  If you are the wrong model for the top recommended tasks, say so clearly.

---

## Example output

Session Brief

**Project:** HealthReporting
**Current phase:** Phase 2 — Core Integrations
**Sprint goal:** All API connectors built and writing to bronze layer
**Sprint progress:** 3 done / 7 total (43%)

**What happened last session (2025-03-15):**
- Built Shopify connector (src/connectors/shopify.py)
- Added 12 integration tests, all passing
- Updated sources_config.yaml with Shopify source
- Decision: Shopify uses private app auth, not OAuth (documented in DEC-003)

**Model context:**
- I am running as: claude-sonnet-4-6
- Last session used: claude-sonnet-4-6
- Last session recommended for today: claude-sonnet-4-6 (feature work continues)

**Recommended tasks for this session:**

1. Build Withings connector — next connector in the sprint, no blockers — Estimated: 1 session
   Depends on: nothing — credentials in .env, base class ready

2. Write silver transform for Shopify orders — unblocks the dashboard work — Estimated: 1 session
   Depends on: Shopify connector (done)

3. Add Shopify to ARCHITECTURE.md integration points — discovered last session — Estimated: 15 min
   Depends on: nothing

**Blockers / open decisions:**
- Message queue decision not made (blocks notification system — Phase 3 work, not urgent)

**Discovered tasks not yet triaged:**
- Document bronze layer schema for Shopify orders (Session 012)

Ready to start. What would you like to work on today?
