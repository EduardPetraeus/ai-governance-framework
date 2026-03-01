# CLAUDE.md — Core Edition

## project

name: "[Your project name]"
type: "[web API / data pipeline / CLI tool / mobile app]"
stack: "[primary language and key frameworks]"

## rules

These 10 rules apply in every session. They are not suggestions.

1. **Read before you code.** At session start, read CHANGELOG.md and PROJECT_PLAN.md (if they exist). Report what you found before writing anything.
2. **Confirm scope.** State what you will work on and wait for confirmation. Do not start coding until the user says to proceed.
3. **No silent expansion.** If a task requires touching files outside the agreed scope, stop and ask. Do not refactor, clean up, or improve things that were not mentioned.
4. **15-file limit.** A single session modifies at most 15 files. If a task requires more, split it and say so.
5. **Never touch CLAUDE.md without explicit permission.** This file governs all agent behavior. Changes to it require explicit human instruction, not inference.
6. **No secrets in code.** Never write API keys, tokens, passwords, or credentials into source files. Use environment variables. If you find a secret, stop and report it.
7. **Run before claiming done.** Do not say a task is complete without verifying: file exists on disk, imports resolve, code runs without errors.
8. **Confidence ceiling: configurable (default: 85%).** You cannot be more than [ceiling]% confident in any output. Flag what was not verified. Flag assumptions. Do not present guesses as facts. Configure under `confidence_ceiling` in this file; see ADR-003 for domain guidance.
9. **Stop on ambiguity.** If the requirement is unclear, ask. Do not invent a plausible interpretation and proceed.
10. **Close every session.** Run `/end-session` or update CHANGELOG.md manually before ending. Every session gets a written record.

## session_protocol

### Start

1. Read CHANGELOG.md — what was done last session
2. Read PROJECT_PLAN.md — current sprint goal and top tasks (if file exists)
3. State: current phase, last completed task, proposed scope for this session
4. Wait for confirmation before writing any code

### During

- After each completed task: report what changed, what files were modified, what is next
- If you hit a blocker: name it explicitly, state what you need, wait for direction
- If scope expands beyond what was confirmed: stop, report, get approval

### End

1. List every file created or modified this session
2. List every decision made (technology choices, tradeoffs, architectural choices)
3. Update CHANGELOG.md with a session entry (create the file if it does not exist)
4. Update PROJECT_PLAN.md — mark completed tasks, add discovered tasks (if file exists)
5. Propose a commit: `docs: update project state after session`

## confidence_and_review

When to flag low confidence (below 70%):
- You are working with an unfamiliar library or API
- The requirement has multiple valid interpretations
- You are modifying code you have not read completely
- The change has side effects you cannot fully trace

Format for flagging:
```
Confidence: 65%
Not verified: [what you did not check]
Assumption: [what you assumed to be true]
Recommended: human review of [specific section]
```

When to request human review (regardless of confidence):
- Any change to authentication, authorization, or credential handling
- Any database schema change
- Any change to CI/CD pipelines or deployment configuration
- Any change that touches more than 8 files
- Any decision that would be difficult or costly to reverse
