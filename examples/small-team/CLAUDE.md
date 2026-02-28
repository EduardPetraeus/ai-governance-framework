# CLAUDE.md — Small Team (3-5 developers)

## project_context
# CUSTOMIZE: Replace with your project details
project_name: "[Your Project Name]"
description: "[What this project does in one sentence]"
stack: "[Languages, frameworks, databases]"
owner: "[Team name]"
repository: "[https://github.com/org/repo]"
current_phase: "[Phase N: Name]"

## conventions
# KEEP: These are enforced by CI — changing them requires updating the governance check.

naming:
  files: snake_case
  branches: "feature/ | fix/ | docs/ | refactor/"
  commits: "type: description (feat, fix, docs, refactor, test, chore)"
  commit_rule: "Every commit message must follow this format. No exceptions."

language: English for all code, comments, docstrings, variable names.

file_structure:
  source_code: src/
  tests: tests/
  docs: docs/
  scripts: scripts/

## session_protocol
# KEEP: Identical to solo, plus mid-session checkpoints for team visibility.

on_session_start:
  1. Read PROJECT_PLAN.md, ARCHITECTURE.md (if exists), CHANGELOG.md (last 5 entries)
  2. Read MEMORY.md if it exists
  3. Present: current sprint/phase, what was done last session, top 3 recommended tasks
  4. State which model you are and which tasks are optimal for that model
  5. Confirm scope — NO CODE before scope is confirmed

during_session:
  - After each completed task: present task status + goal impact
  - After 3+ tasks: full checkpoint (Done / In Progress / Remaining)
  - Ask: "Continue with [X], or adjust scope?"
  - If task not in PROJECT_PLAN.md: "This is not in the current sprint scope.
    Add it to discovered tasks, or is it replacing a planned task?"

on_session_end:
  1. Present full session summary (tasks, files, decisions, discovered tasks)
  2. Update CHANGELOG.md (new session entry)
  3. Update PROJECT_PLAN.md (mark completed, add discovered tasks)
  4. Commit: "docs: update project state after session [NNN]"
  5. Recommend model for next session

on_user_forgets_protocol:
  - Run end-session protocol anyway if user ends without /end-session
  - Ask for scope confirmation if user tries to skip it

## governance_sync
# KEEP: Prevents team members from stepping on each other.
# Critical at team scale — multiple people modify the same repo concurrently.

on_session_start drift_detection:
  - Flag if working outside current sprint phase
  - Flag if architectural change not reflected in ARCHITECTURE.md
  - Flag if new external dependency not discussed with team
  - If drift detected: surface it and ask before proceeding

on_architectural_change:
  - Before implementing: "This changes the architecture. Should I update
    ARCHITECTURE.md first?"
  - If the change contradicts an existing decision in DECISIONS.md:
    surface the contradiction and ask before proceeding

## model_routing
# OPTIONAL: Remove if not cost-sensitive. Useful at Level 2+ when team spend matters.
# CUSTOMIZE: Adjust task-to-model mapping based on your AI provider and pricing.

routing_table:
  architecture_decisions: opus      # High-stakes, cross-system reasoning
  security_review: opus             # Zero tolerance for mistakes
  code_generation: sonnet           # Standard feature work
  code_review: sonnet               # PR review and convention checking
  documentation: sonnet             # Writing and updating docs
  simple_edits: haiku               # Config tweaks, typo fixes

self_routing_rule: |
  At session start: "Running as [model]. Optimal for: [task types]."
  If a task needs a different model tier: say so and recommend starting
  a new session with the appropriate model.
  At session end: recommend the right model for the next session.

## pr_workflow
# KEEP: Non-negotiable for team repos. Agents must follow this — no shortcuts.

rules:
  - All changes through feature branches and PRs. No direct commits to main.
  - Direct commits to main are blocked by branch protection.
  - Every PR must update CHANGELOG.md (enforced by CI governance check).
  - One human reviewer required after AI review passes.
  - CLAUDE.md changes require a second reviewer.

## mandatory_task_reporting
# KEEP: Prevents the yes-man anti-pattern where agents silently complete
# tasks without confirming scope, relevance, or correctness.

after_every_task:
  1. Files changed (with paths)
  2. Goal impact (which sprint task this advances, progress %)
  3. Running session total (tasks done / planned)
  4. Next step — ask to continue or adjust

format: |
  ┌────────────────────────────────────────────┐
  │ Task completed: [name]                     │
  ├────────────────────────────────────────────┤
  │ Changed: [file1], [file2]                  │
  │ Impact:  [sprint task] — [N]% complete     │
  │ Session: [N] / [M] tasks                   │
  │ Next:    [task] — Continue? [Y/adjust]     │
  └────────────────────────────────────────────┘

cannot_be_disabled: true

## security
# KEEP: Same as solo, plus scan triggers for systematic checking.

never_commit:
  - API keys, tokens, secrets of any kind
  - Passwords or credentials
  - PII: names, emails, phone numbers, national IDs
  - Hardcoded production paths or database connection strings
  - Real data samples from any environment

scan_triggers:
  per_file: Scan each modified file before moving to the next task
  per_session_end: Full scan before committing session changes

incident_response:
  if_secret_detected:
    1. STOP immediately
    2. Assess: was it committed? Was it pushed?
    3. Revoke the credential immediately
    4. Clean git history if committed
    5. Document in DECISIONS.md

## verification
before_claiming_done:
  - Run the code or test it
  - Check that imports resolve
  - Verify file was actually written
  - Confirm config is valid syntax

never_assume:
  - That a file exists — check first
  - That previous session's changes are present
  - That "it should work" equals "it does work"

# ─── Upgrade path ────────────────────────────────────────────────────────────
# Add at Level 3 (Enterprise):
#   compliance          — EU AI Act, GDPR, audit trail requirements
#   definition_of_done  — mandatory 8-item checklist before marking tasks complete
#   change_control      — ADR + PR + two reviewers for CLAUDE.md changes
#   escalation_model    — formal incident escalation with contacts
#   review_cadence      — scheduled reviews of CLAUDE.md, ADRs, security policy
#   expanded routing    — 14 task types with auto-review triggers
