# /plan-session

You are starting a governed session. Orient yourself, then confirm scope before writing any code.

## Steps

**1. Read project state**

Read these files if they exist. Note what is missing.

- `CHANGELOG.md` — most recent entry only. What was done last session? What was left open?
- `PROJECT_PLAN.md` — current phase and sprint goal. What are the top 3 tasks?

If neither file exists: say so and ask the user for the session goal before proceeding.

**2. Present the session brief**

Output this format:

---

## Session Brief

**Project:** [from PROJECT_PLAN.md, or "not yet defined"]
**Last session:** [date and 2-3 bullets from CHANGELOG.md, or "No prior sessions"]
**Sprint goal:** [from PROJECT_PLAN.md, or "not defined"]

### Proposed scope for this session
1. [Task — reason it is the top priority]
2. [Task — second priority]
3. [Task — third priority, or "none identified"]

**What would you like to work on?** (Say "go" to start with task 1, or specify a different task.)

---

**3. Wait for confirmation**

Do not write any code until the user confirms what to work on.

- "go" or "start" → begin with task 1
- "start with [X]" → begin with that task
- Custom task not in the sprint → say where it fits (sprint / backlog / undocumented) and ask whether to add it

**4. Begin**

After scope is confirmed, state the task you are starting and begin work.

## Edge cases

- **No files exist:** "No governance files found. This appears to be the first session. What are we building today?"
- **All tasks complete:** "All sprint tasks are complete. Should we plan the next phase, or is there ad-hoc work to do?"
- **Blocked tasks:** Name the blockers, ask whether to skip them or address the blocking dependency first.
