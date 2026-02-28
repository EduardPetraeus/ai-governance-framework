# CLAUDE.md

project_name: "[Your Project Name]"
description: "[What this project does in one sentence]"
stack: "[Languages, frameworks, databases]"
owner: "[Team name]"
repository: "[https://github.com/org/repo]"
current_phase: "[Phase N: Name]"

---

## conventions

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

pr_workflow:
  - All changes go through feature branches and PRs. No direct commits to main.
  - Every PR must update CHANGELOG.md. Governance check enforces this in CI.
  - CLAUDE.md changes require a second reviewer.

---

## mandatory_session_protocol

on_session_start:
  1. Read PROJECT_PLAN.md, ARCHITECTURE.md (if exists), CHANGELOG.md (last 5 entries)
  2. Read MEMORY.md if it exists
  3. Present: current sprint/phase, what was done last session, top 3 recommended tasks
  4. State which model you are and which model this session should use
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
  3. Update PROJECT_PLAN.md (mark completed tasks, add discovered tasks)
  4. Commit: "docs: update project state after session [NNN]"
  5. Recommend model for next session

on_user_forgets_protocol:
  - Run end-session protocol anyway if user ends without /end-session
  - Ask for scope confirmation if user tries to skip it

---

## governance_sync

on_session_start drift_detection:
  - Compare intended work against PROJECT_PLAN.md current sprint
  - Flag if: working outside current phase, architectural change not in ARCHITECTURE.md,
    new dependency not documented
  - If drift detected: "I notice we're working outside the current sprint scope.
    [Observation]. This was planned for [phase]. Continue anyway, or return to plan?"

---

## model_routing

routing_table:
  architecture_decisions: opus      # High-stakes, cross-system reasoning
  security_review: opus             # Zero tolerance for mistakes
  code_generation: sonnet           # Standard feature work
  code_review: sonnet               # PR review and convention checking
  documentation: sonnet             # Writing and updating docs
  simple_edits: haiku               # Config tweaks, typo fixes

self_routing_rule: |
  At session start: "Running as [model]. Optimal for: [task types]."
  If a task needs a different model: say so and recommend starting a new session.
  At session end: recommend the right model for the next session's planned work.

---

## security

never_commit:
  - API keys, tokens, secrets of any kind
  - Passwords or credentials
  - PII: names, emails, phone numbers, national IDs, health data
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

---

## mandatory_task_reporting

After every completed task, present:
  1. Files created/modified (with paths)
  2. Goal impact: which phase/task this advances, progress update
  3. Cumulative session status: tasks done / total scope
  4. Next steps: what comes next, ask "Continue, or adjust?"

This cannot be disabled. Even if user says "just continue", show the status block.

---

## verification

before_claiming_done:
  - Run the code or test
  - Check imports resolve
  - Verify file was actually written
  - Confirm config is valid syntax

never_assume:
  - That a file exists (check first)
  - That previous session's changes are present
  - That the user knows what changed (always show it)
  - That "it should work" equals "it does work"
