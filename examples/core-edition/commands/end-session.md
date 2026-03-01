# /end-session

You are closing a session. Compile what happened, update the records, propose a commit.

## Steps

**1. Compile the session summary**

From your memory of this session:
- Every task completed (in order)
- Every file created or modified (full paths)
- Every decision made that affects future work
- Any tasks discovered that were not originally planned
- Any open questions that came up but were not resolved

**2. Present the summary for confirmation**

---

## Session Summary

**Date:** [today's date, YYYY-MM-DD]
**Model:** [your model name]

### Tasks completed
- [task name]: [one-line description of what changed and why]

### Files changed
- New: [list, or "none"]
- Modified: [list, or "none"]

### Decisions made
- [decision]: [rationale — one line each, or "none"]

### Discovered tasks
- [task]: [priority — High / Medium / Low, or "none"]

### Open questions
- [question, or "none"]

---

**Does this look correct?** (Say "yes" to proceed with updates.)

---

**3. Update CHANGELOG.md**

Prepend a new entry at the top of CHANGELOG.md. Create the file if it does not exist.

```markdown
## [YYYY-MM-DD] — [2-4 word session title]

### Done
- [file path]: [what changed]

### Decisions
- [decision]: [rationale]

### Discovered
- [task] — [priority]

### Next session
- [top 1-2 tasks for next time]
```

**4. Update PROJECT_PLAN.md (if it exists)**

- Mark completed tasks as done
- Add discovered tasks to the backlog

**5. Propose commit**

```
docs: update project state after session
```

List the files to stage: CHANGELOG.md and PROJECT_PLAN.md (if updated).

## Edge cases

- **User says "just commit":** Proceed without confirmation step, note that review was skipped.
- **No tasks completed:** Still run the protocol. Record "No tasks completed" with reason.
- **Commit fails:** Report the exact error. Do not mark the session as closed.
