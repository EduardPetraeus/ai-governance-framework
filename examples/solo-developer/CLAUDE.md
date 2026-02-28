# CLAUDE.md

project_name: "[Your Project Name]"
description: "[What this project does in one sentence]"
stack: "[Python / TypeScript / etc.]"
owner: "[Your name]"

---

## conventions

naming:
  files: snake_case
  branches: "feature/ | fix/ | docs/"
  commits: "type: description (feat, fix, docs, refactor, test, chore)"

language: English for all code, comments, variable names.

---

## session_protocol

on_session_start:
  1. Read PROJECT_PLAN.md (current status, last session)
  2. Read CHANGELOG.md (last 3 entries)
  3. Present: what was done last session, top 3 recommended tasks
  4. Confirm scope — do not write code before scope is confirmed

on_session_end:
  1. Present session summary (tasks done, files changed)
  2. Update CHANGELOG.md with new session entry
  3. Update PROJECT_PLAN.md (mark completed tasks)
  4. Commit: "docs: update project state after session [NNN]"

---

## security

never_commit:
  - API keys, tokens, or secrets of any kind
  - Passwords or credentials
  - PII: names, emails, phone numbers, IDs
  - Hardcoded production paths or connection strings
  - Real data from any system

If you find a secret in a file: stop, remove it, check if it was committed, rotate if necessary.

---

## verification

Before claiming a task is done:
  - Run the code or test it
  - Verify the file was actually written
  - Check that imports resolve

Never assume a file exists — check first.
