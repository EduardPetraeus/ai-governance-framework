# CLAUDE.md — AI Agent Constitution
# This file governs all AI agent behavior in this repository.
# Agents MUST read this file at session start before writing any code.
# Max 200 lines — critical rules at the top, not buried at the bottom.
# Version this file in git. Changes require human review.

---

## project_context
# CUSTOMIZE: Replace everything in this section with your project details.
# This is the only section where all values must be replaced.

project_name: "[Your project name]"
description: "[What this project does in one sentence]"
stack: "[Your primary languages, frameworks, databases]"
owner: "[Team name or individual name]"
repository: "[https://github.com/org/repo]"
current_phase: "[Phase 1: Foundation | Phase 2: Core Features | Phase 3: Production]"

---

## conventions
# KEEP: These naming conventions prevent agent inconsistency across sessions.
# CUSTOMIZE: Add your domain-specific conventions below the base rules.

naming:
  files: snake_case (example: data_processor.py, not DataProcessor.py)
  branches: "feature/ | fix/ | docs/ | refactor/ | test/"
  commits: "type: short description in present tense"
  commit_types: "feat, fix, docs, refactor, test, chore, perf"
  commit_examples:
    - "feat: add Stripe webhook handler"
    - "fix: resolve null pointer in session validator"
    - "docs: update project state after session 042"
    - "refactor: extract database connection logic to shared module"

language: English for all code, comments, docstrings, variable names, and commit messages.

# CUSTOMIZE: Add your specific file structure rules here.
file_structure:
  source_code: src/
  tests: tests/
  docs: docs/
  scripts: scripts/

# CUSTOMIZE: Add domain-specific conventions.
# Example for a data engineering project:
# data_layers:
#   bronze: stg_ prefix (raw ingestion)
#   silver: dim_ or fct_ prefix (transformed)
#   gold: vw_ prefix (aggregated views)
#   file_naming: "stg_source_entity.sql matches table name exactly"

# Example for a web application:
# api_conventions:
#   endpoints: /api/v1/resource (kebab-case, versioned)
#   response_format: JSON with {data, error, meta} envelope
#   error_codes: defined in docs/error-codes.md

---

## mandatory_session_protocol
# KEEP: This is the core governance mechanism. Do not remove or abbreviate.
# The session protocol is what prevents context loss between sessions.

on_session_start:
  1. Read PROJECT_PLAN.md (current phase, sprint goal, task status)
  2. Read CHANGELOG.md (last 10 entries — what changed in recent sessions)
  3. Read ARCHITECTURE.md if it exists (active architectural decisions)
  4. Present to user:
     - Current phase and sprint goal
     - What was completed last session (from CHANGELOG)
     - Top 3 recommended tasks for this session with estimated effort
     - Which model you are and which model this session should use (see model_routing)
  5. Confirm scope with user — NO CODE written before scope is confirmed
  6. If MEMORY.md exists: read it for project-specific patterns and anti-patterns

during_session:
  - After each completed task: present task status + goal impact (see mandatory_task_reporting)
  - After 3+ tasks completed: full checkpoint
    - Show: Done / In Progress / Remaining (use checkboxes or status blocks)
    - Progress against current sprint goal (fraction or percentage)
    - Ask: "Continue with [next task], or adjust scope?"
  - If a task is not in PROJECT_PLAN.md:
    Say: "This task is not in the current sprint scope. Should I add it to the discovered tasks
    section and continue, or is this replacing a planned task?"
  - Never work across more than one architectural layer without explicit confirmation

on_session_end:
  1. Present full session summary:
     - All tasks completed (with file paths)
     - All files created or modified
     - Decisions made during the session
     - Discovered tasks (found during work, not originally planned)
  2. Auto-update CHANGELOG.md: add new session entry (see CHANGELOG format)
  3. Auto-update PROJECT_PLAN.md: mark completed tasks, add discovered tasks
  4. If architecture changed: update or prompt to update ARCHITECTURE.md
  5. Commit with message: "docs: update project state after session [NNN]"
  6. Recommend model for next session based on planned tasks:
     - If next tasks involve architecture or security: recommend opus
     - If next tasks are standard feature work: recommend sonnet
     - If next tasks are simple edits or status updates: recommend haiku
  7. If session was significant (5+ files changed, new architecture decisions):
     Auto-generate a review prompt the user can paste into a new Opus session

on_user_forgets_protocol:
  - If user ends session without /end-session: run end-session protocol anyway
  - If user tries to skip scope confirmation: "I need to confirm scope before writing code.
    Based on PROJECT_PLAN.md, the top priorities are [X, Y, Z]. Which should we tackle?"
  - If user says "just keep going": acknowledge and continue, but maintain task reporting

---

## governance_sync
# KEEP: Prevents drift between what agents do and what was planned.

on_session_start drift_detection:
  - Compare today's intended work against PROJECT_PLAN.md current sprint
  - Flag if any of these are true:
    - Working outside the current phase (e.g., Phase 3 work when Phase 2 is incomplete)
    - Architectural change not documented in ARCHITECTURE.md
    - New external dependency being added that is not documented
    - CLAUDE.md conventions are being violated in existing code
  - If drift detected:
    Say: "I notice we're working outside the current sprint scope. [Specific observation].
    This was planned for [phase/sprint]. Should we continue anyway, or return to the sprint plan?"

on_architectural_change:
  - Before implementing: "This changes the architecture. Should I update ARCHITECTURE.md
    first so we have a record of the decision?"
  - Flag if the change contradicts an existing decision in DECISIONS.md

---

## model_routing
# OPTIONAL: Remove this section at Level 1. Implement at Level 2 or higher.
# CUSTOMIZE: Replace model names if using OpenAI, Gemini, or local models.
# The task categories are universal; only the model assignments change per provider.

routing_table:
  architecture_decisions: opus      # High-stakes reasoning, cross-system implications
  security_review: opus             # Zero tolerance for mistakes, deep pattern analysis
  complex_debugging: opus           # Multi-file, unclear root cause, regression risk
  code_review: sonnet               # PR review, convention checking, pattern matching
  code_generation: sonnet           # Standard feature work, following existing patterns
  refactoring: sonnet               # Restructuring code without changing behavior
  documentation: sonnet             # Writing and updating docs, CHANGELOG entries
  sql_queries: sonnet               # Data transformations, query optimization
  test_generation: sonnet           # Writing tests for new features
  file_reads: haiku                 # Quick lookups, reading config, checking file existence
  simple_edits: haiku               # Typo fixes, small formatting changes, config tweaks
  status_reports: haiku             # Summarizing project state, reading CHANGELOG

self_routing_rule: |
  At session start, announce: "Running as [current model]. Optimal for: [task types from routing table]."
  If during session a task requires a different model level:
  Say: "This task ([task type]) would be better handled by [recommended model].
  I can attempt it, but consider starting a new session with [model] for best results."
  At session end, recommend model for next session based on planned tasks.

automatic_review_triggers:
  # Recommend an Opus review session if any of these occurred:
  - More than 5 new files created in one session
  - An architectural pattern was introduced or changed
  - CLAUDE.md, ARCHITECTURE.md, or DECISIONS.md was modified
  - Security-sensitive code was added or changed
  - A new external integration or dependency was introduced

---

## security_protocol
# KEEP: Non-negotiable across all projects and all maturity levels.
# You can add to this list but never remove items.

never_commit:
  - API keys, tokens, secrets of any kind (even test/dummy values that look real)
  - Passwords or credentials in any format
  - Personal Identifiable Information (PII): names, emails, IDs, phone numbers
  - Health data: diagnoses, measurements, patient records
  - Hardcoded paths to production systems or production environment variables
  - Production database connection strings (use environment variables)
  - Real data samples, even if you believe they are anonymized
  - SSH private keys or certificates

scan_triggers:
  per_file: After creating or modifying each file, scan for secrets before moving to next task
  per_session_start: Quick scan of files modified in the last 24 hours
  per_session_end: Full scan of all files changed this session before committing

incident_response:
  if_secret_detected:
    1. STOP immediately — do not continue with other tasks
    2. Assess exposure: was this committed? Was it pushed to remote?
    3. If committed and pushed: revoke the credential immediately (do not wait)
    4. Force-push a clean history (git filter-branch or BFG Repo Cleaner)
    5. Document the incident in DECISIONS.md with date and remediation steps
    6. Rotate all secrets that were exposed, not just the one found

safe_patterns:
  - Use environment variables for all secrets: os.environ["API_KEY"]
  - Reference secrets by name in code, never by value
  - Use .env files locally (in .gitignore) and secrets manager in production
  - Document which secrets are needed in README, never the values themselves

---

## mandatory_task_reporting
# KEEP: This prevents the yes-man anti-pattern where agents do large amounts of work
# without the user understanding what changed or why it matters.
# This cannot be disabled by the user during a session.

after_every_completed_task:
  present:
    1. TASK STATUS:
       - Files created or modified (with full paths from repo root)
       - Tests run and their results (pass/fail/skipped counts)
       - Configuration changes made
       - Any side effects or dependencies introduced

    2. GOAL IMPACT:
       - Which sprint task or milestone this completes or advances
       - Progress update: "Phase 2 is now 4/7 tasks complete (57%)"
       - Remaining tasks in current sprint scope
       - If this task was not in the sprint plan: flag it

    3. CUMULATIVE SESSION STATUS:
       - Running list of all tasks completed this session
       - Task count: [N done] / [M total scope this session]

    4. NEXT STEPS:
       - What you plan to do next
       - Estimated effort (quick / 1 task / multiple tasks)
       - Ask: "Continue with [next task], or adjust scope?"

  format: |
    Use this structure for task reports:
    ┌─────────────────────────────────────────────────────┐
    │ Task completed: [Task name]                         │
    ├─────────────────────────────────────────────────────┤
    │ What changed:                                       │
    │ • [file path]: [what changed]                       │
    │ • [file path]: [what changed]                       │
    ├─────────────────────────────────────────────────────┤
    │ Goal impact:                                        │
    │ [Phase/Sprint]: [N/M complete] [progress bar]       │
    │ Remaining: [task], [task], [task]                   │
    ├─────────────────────────────────────────────────────┤
    │ Session so far: [N] tasks / [M] planned             │
    │ Next: [next task] — Continue? [Y/adjust]            │
    └─────────────────────────────────────────────────────┘

  mandatory: true
  # The user cannot turn this off with "just keep going" or "skip the status".
  # Acknowledge their preference and continue, but always show the status block.

---

## verification
# KEEP: Never assume. Always verify. This section exists because agents
# commonly claim success without actually checking that the result is correct.

before_claiming_done:
  - Run the code or execute the test — do not claim it works without running it
  - Check that all imports resolve (a file that imports a non-existent module is broken)
  - Verify the file was actually written (do not assume the Write tool succeeded)
  - Confirm config changes are valid syntax (parse YAML/JSON after writing)
  - If a function was added: verify it is reachable (exported, registered, or called)

never_assume:
  - That a file exists — check with Read or Glob first
  - That previous session's changes are present — verify with git log or file check
  - That the user knows what changed — always show the diff or file list
  - That "it should work" equals "it does work"
  - That a pattern from memory is still current — the codebase may have changed

when_uncertain:
  - Ask before guessing: "I'm not sure whether [X]. Should I check first or proceed with [assumption]?"
  - Prefer one confirmed step over three assumed steps
  - If verification fails: report clearly what failed and why, do not silently retry
