# /end-session

You are closing a development session. Your job is to present a full summary, update
all governance files, commit the changes, and recommend the setup for the next session.

Do this even if the user did not explicitly run /end-session. If they say "we're done"
or "that's it for today" or close without saying anything — run this protocol.

## Steps

1. Compile the session summary from your memory of this session:
   - Every task completed (in order)
   - Every file created or modified (with paths)
   - Every decision made
   - Every task discovered during the session (not originally planned)
   - Any open questions that came up but weren't resolved

2. Read CHANGELOG.md to determine the current session number (last entry + 1).
   If CHANGELOG.md does not exist: this is Session 001.

3. Read PROJECT_PLAN.md to identify which tasks to mark as complete.

4. Present the session summary for user confirmation before committing:

---

## Session Summary — Session [NNN]

**Date:** [today's date]
**Model used:** [current model]
**Duration:** [estimate if known]

### Tasks completed
- [Task name]: [file path(s) affected] — [one-line description of what changed]
- [Task name]: [file path(s)] — [description]

### Files changed
New: [list of new files with paths]
Modified: [list of modified files with paths]

### Decisions made
- [Decision]: [brief rationale] — [should this go in DECISIONS.md? yes/no]

### Discovered tasks (not originally planned)
- [Task]: [priority estimate] — [recommended phase]

### Open questions (not resolved)
- [Question]: [context]

### Metrics
- Tasks completed: [N]
- Files changed: [N] ([N new], [N modified])
- Tests added/run: [N added, all passing / N failing]
- Estimated cost: ~$[amount] ([model] sessions)

---

**Does this look correct? Any tasks or decisions I missed?**
(Say "yes" or "looks good" to proceed with the governance updates)

5. After user confirmation, perform these updates:

### Update CHANGELOG.md
Prepend a new entry at the top (above the previous most recent entry):

```markdown
## Session [NNN] — [YYYY-MM-DD] [[MODEL USED]]

### Tasks completed
[bullet list]

### Decisions made
[bullet list, or "None" if no decisions]

### Discovered tasks
[bullet list, or "None"]

### Metrics
- Tasks completed: [N]
- Files changed: [N] ([N new], [N modified])
- Tests added: [N]
- Cost estimate: ~$[amount]

### Next session
- Recommended model: [model and why]
- Top 3 tasks:
  1. [task]
  2. [task]
  3. [task]
```

### Update PROJECT_PLAN.md
For each completed task:
- Change status from "🔵 In Progress" or "⬜ Planned" to "✅ Complete"
- Add the session number and date to the Notes column: "Completed Session NNN"

For each discovered task:
- Add to the "Discovered Tasks" section with priority and "Added To Sprint?" = No

Update the phase progress calculation at the bottom of each phase section.

### Update DECISIONS.md (if any decisions were made)
For each decision made during the session:
- Add a new DEC-NNN entry with date, context, decision, rationale, and consequences
- Link from CHANGELOG.md entry to the DEC-NNN number

### Commit the changes

After all files are updated, commit with:
```
git add CHANGELOG.md PROJECT_PLAN.md DECISIONS.md MEMORY.md
git commit -m "docs: update project state after session [NNN]"
```

If ARCHITECTURE.md was changed, include it: `git add ARCHITECTURE.md`

6. Present the next session recommendation:

---

## Next Session Recommendation

**Recommended model:** [model]
**Why:** [specific reason based on what's planned next]

**Top 3 tasks for next session:**
1. [Task] — [why it's first priority]
2. [Task] — [why it's second]
3. [Task] — [why it's third]

**If significant changes were made this session** (5+ files, new architecture, security-sensitive code):
Generate a review prompt:

```
Copy this into a new claude-opus-4-6 session to review today's work:

"You are reviewing changes made in Session [NNN] of the [project] project.

Read: CHANGELOG.md (Session [NNN] entry), and these files: [list changed files]

Review for:
1. Architecture: do these changes align with ARCHITECTURE.md?
2. Conventions: do they follow CLAUDE.md naming and structure rules?
3. Security: any concerns about the new code?
4. Simplicity: is anything over-engineered for the current scale?

Produce a brief assessment (PASS / WARN / FAIL) with specific recommendations."
```

---

Session [NNN] closed. All governance files updated and committed.

---

## Notes for the agent

- If the user skips the confirmation step ("just commit"), proceed but note what was committed
- If you are uncertain about something in the session summary, ask rather than guess
- If the commit fails (git error), report the error and do not mark the session as closed
- If CHANGELOG.md does not yet exist, create it from the template format before adding the entry
- Never commit without updating at least CHANGELOG.md — the commit message references it
- If the user made changes outside of what you helped with: ask them to describe it so
  the CHANGELOG entry is complete
