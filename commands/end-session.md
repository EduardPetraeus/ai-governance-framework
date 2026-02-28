# /end-session

You are closing a development session. Your job is to compile a complete session summary, update all governance files, commit the changes, and recommend the setup for the next session.

Run this protocol whenever the user says any of: "/end-session", "we're done", "that's it for today", "wrap up", "let's stop here". If the user ends the conversation without closing, attempt to run this protocol before the session ends.

## Steps

### Step 1: Compile the session summary

From your memory of this session, compile:
- Every task completed (in the order they were done)
- Every file created or modified (with full paths)
- Every decision made (technology choices, architectural patterns, tradeoffs)
- Every task discovered during the session (things found that were not originally planned)
- Any open questions that came up but were not resolved
- Any bugs found or issues encountered

### Step 2: Determine session number

Read CHANGELOG.md and find the most recent session number. The new session is that number + 1.
If CHANGELOG.md does not exist, this is Session 001 — create the file.

### Step 3: Read PROJECT_PLAN.md

Identify which tasks in PROJECT_PLAN.md correspond to the completed work. Note their exact names and status fields so you can update them precisely.

### Step 4: Present the summary for confirmation

Output this format:

---

## Session Summary — Session [NNN]

**Date:** [today's date, YYYY-MM-DD]
**Model:** [your model name]
**Duration:** [estimate based on conversation length, or "unknown"]

### Tasks completed
| # | Task | Files affected | Description |
|---|------|---------------|-------------|
| 1 | [Task name] | `path/to/file.py` | [One-line description] |
| 2 | [Task name] | `path/to/file.py`, `path/to/other.py` | [Description] |

### Files changed
- **New:** [list of new files with full paths]
- **Modified:** [list of modified files with full paths]
- **Deleted:** [list if any, or "None"]

### Decisions made
| Decision | Rationale | Record in DECISIONS.md? |
|----------|-----------|------------------------|
| [Decision statement] | [Brief rationale] | Yes / No |

### Discovered tasks
| Task | Priority | Suggested phase |
|------|----------|----------------|
| [Task description] | High / Medium / Low | [Phase or "Backlog"] |

### Open questions
- [Question that was raised but not resolved — include context]

### Metrics
- Tasks completed: [N]
- Files changed: [N] ([N new], [N modified])
- Tests added: [N] / Tests passing: [all passing / N failing]
- Estimated cost: ~$[amount]

---

**Does this look correct? Anything I missed or got wrong?**
(Say "yes" or "looks good" to proceed with governance updates.)

---

### Step 5: After user confirmation, update governance files

Perform ALL of these updates:

#### 5a. Update CHANGELOG.md

Prepend a new entry at the TOP of the file (above the previous most recent entry):

```markdown
## Session [NNN] — [YYYY-MM-DD] [[model name]]

### Tasks completed
- [file path]: [what changed and why]
  - [sub-detail if significant]

### Decisions made
- [Decision]: [rationale]
[or "None"]

### Discovered tasks
- [Task] — [priority] — [suggested phase]
[or "None"]

### Metrics
- Tasks completed: [N]
- Files changed: [N] ([N new], [N modified])
- Tests added: [N]
- Cost estimate: ~$[amount]

### Next session
- Recommended model: [model name] — [why this model for the planned tasks]
- Top 3 tasks:
  1. [Task — one-line reason it is #1]
  2. [Task — reason]
  3. [Task — reason]
```

#### 5b. Update PROJECT_PLAN.md

For each completed task:
- Change status from "In Progress" or "Planned" to "Complete"
- Add session reference in the Notes column: "Completed Session NNN"

For each discovered task:
- Add to the "Discovered Tasks" section with priority and status "Not triaged"

Update the phase progress calculation if one exists.

#### 5c. Update DECISIONS.md (if decisions were made)

For each decision flagged as "Yes" in the summary table:
- Add a new DEC-NNN entry:
  ```markdown
  ## DEC-[NNN] — [Short title]
  **Date:** [YYYY-MM-DD]
  **Session:** [NNN]
  **Context:** [What prompted this decision]
  **Decision:** [What was decided]
  **Rationale:** [Why]
  **Consequences:** [What changes as a result]
  ```
- Reference the DEC number in the CHANGELOG entry

#### 5d. Update MEMORY.md (if patterns were confirmed or anti-patterns discovered)

If during the session:
- A pattern was confirmed to work well: add to "Confirmed patterns" section
- An approach was found to fail or cause problems: add to "Anti-patterns" section
- A tool, library, or technique proved useful: add to "Working tools" section

Only update MEMORY.md for things that future sessions should know. Not every micro-discovery.

#### 5e. Commit the governance files

```bash
git add CHANGELOG.md PROJECT_PLAN.md
# Also add these if they were updated:
git add DECISIONS.md MEMORY.md ARCHITECTURE.md
git commit -m "docs: update project state after session [NNN]"
```

If the commit fails, report the error. Do not mark the session as closed.

### Step 6: Present next-session recommendation

---

## Next Session

**Recommended model:** [model name]
**Why:** [Specific reason based on the nature of the top planned tasks. Example: "Architecture review of the new module requires cross-system reasoning — Opus is recommended." or "Continuing feature implementation — Sonnet is the right fit."]

**Top 3 tasks:**
1. **[Task]** — [Why it is the top priority]
2. **[Task]** — [Why it is second]
3. **[Task]** — [Why it is third]

---

### Step 7: Generate Opus review prompt (if session was significant)

If ANY of these conditions are true, generate a review prompt:
- 5 or more files were created or modified
- An architectural pattern was introduced or changed
- CLAUDE.md, ARCHITECTURE.md, or DECISIONS.md was modified
- Security-sensitive code was added or changed
- A new external integration or dependency was introduced

If triggered, output:

---

### Opus Review Prompt

Copy this into a new claude-opus-4-6 session to review this session's work:

```
You are reviewing the changes made in Session [NNN] of the [project] project.

Read the following files:
1. CHANGELOG.md — the Session [NNN] entry
2. [list each changed file]

Review for:
1. Architecture: Do these changes align with ARCHITECTURE.md? Any structural concerns?
2. Conventions: Do they follow CLAUDE.md naming and structure rules?
3. Security: Any secrets, PII, injection risks, or insecure patterns?
4. Simplicity: Is anything over-engineered for the current scale?
5. Completeness: Are there gaps — missing tests, missing docs, missing error handling?

Produce a brief assessment: PASS / WARN / FAIL with specific findings.
```

---

Session [NNN] closed. All governance files updated and committed.

---

## Edge cases

- **User skips confirmation ("just commit"):** Proceed with the updates but note: "Committing without review. If I missed anything, amend the CHANGELOG entry."
- **Uncertain about a task or decision:** Ask rather than guess. "I am not sure if [X] counts as a decision worth recording. Should I add it to DECISIONS.md?"
- **Commit fails:** Report the exact error. Do not mark the session as closed. Common causes: unstaged files, merge conflict, pre-commit hook failure.
- **CHANGELOG.md does not exist:** Create it with the standard header before adding the first entry.
- **User made changes outside the AI session:** Ask: "Did you make any changes manually that I should include in the session summary?"
- **No tasks were completed:** Still run the protocol. The CHANGELOG entry says "No tasks completed" with an explanation (blocked, planning only, investigation). Every session gets an entry.

---

## Example output

## Session Summary — Session 014

**Date:** 2026-02-28
**Model:** claude-sonnet-4-6
**Duration:** ~45 minutes

### Tasks completed
| # | Task | Files affected | Description |
|---|------|---------------|-------------|
| 1 | Build HubSpot connector | `src/connectors/hubspot.py` | CRM contact fetcher with cursor pagination and rate limit tracking |
| 2 | Add HubSpot to sync pipeline | `src/pipeline/sync.py` | HubSpot runs after Shopify in pipeline order |
| 3 | Draft ADR for HubSpot auth | `docs/adr/ADR-007.md` | API key auth chosen over OAuth for single-portal setup |
| 4 | Update ARCHITECTURE.md | `ARCHITECTURE.md` | Added HubSpot to integration points table |

### Files changed
- **New:** `src/connectors/hubspot.py`, `docs/adr/ADR-007.md`
- **Modified:** `src/pipeline/sync.py`, `ARCHITECTURE.md`

### Decisions made
| Decision | Rationale | Record in DECISIONS.md? |
|----------|-----------|------------------------|
| HubSpot uses API key auth, not OAuth | Single-portal setup; OAuth adds ~80 lines with no benefit | Yes |
| HubSpot sync runs after Shopify in pipeline | No data dependency; alphabetical ordering for consistency | No |

### Discovered tasks
| Task | Priority | Suggested phase |
|------|----------|----------------|
| Write integration tests for HubSpot connector | High | Current sprint |
| Investigate HubSpot webhooks for real-time sync | Low | Phase 3 |

### Open questions
- None

### Metrics
- Tasks completed: 4
- Files changed: 4 (2 new, 2 modified)
- Tests added: 0 (planned for next session)
- Estimated cost: ~$0.06

---

## Next Session

**Recommended model:** claude-sonnet-4-6
**Why:** Next session is integration test writing — standard feature work, Sonnet is optimal.

**Top 3 tasks:**
1. **Write integration tests for HubSpot connector** — Highest priority: the connector has no tests and should not merge without them
2. **Build silver transform for HubSpot contacts** — Unblocks dashboard work in Phase 3
3. **Silver transform for Shopify orders** — Sprint commitment, ready to start

---

Session 014 closed. All governance files updated and committed.
