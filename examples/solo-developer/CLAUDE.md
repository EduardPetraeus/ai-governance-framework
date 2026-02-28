# CLAUDE.md — Solo Developer

## project_context
# CUSTOMIZE: Replace with your project details
project_name: "[Your project]"
description: "[One sentence describing what this project does]"
stack: "[Your stack — e.g., Python, FastAPI, PostgreSQL]"
owner: "[Your name]"

## conventions
naming:
  files: snake_case
  branches: "feature/ | fix/ | docs/"
  commits: "type: description (feat, fix, docs, refactor, test, chore)"
language: English for all code, comments, docstrings, and variable names.

## session_protocol
# KEEP: This is the core value of the framework. Without it, every session starts blind.

on_session_start:
  1. Read PROJECT_PLAN.md — current phase and top 3 tasks
  2. Read CHANGELOG.md — what was done last session
  3. Confirm what you will work on before writing any code

on_session_end:
  1. Update CHANGELOG.md with what was done (files changed, decisions made)
  2. Update PROJECT_PLAN.md (mark completed tasks, add discovered tasks)
  3. Commit: "docs: update project state after session"

## security
# KEEP: These rules apply at every level. No exceptions.

never_commit:
  - API keys, tokens, or secrets of any kind
  - Passwords or credentials
  - Personal data (names, emails, phone numbers)
  - Production database connection strings
  - Private keys or certificates
  - Real data samples from any environment

if_secret_found: Stop. Remove it. Check if it was committed. Rotate if necessary.

## verification
# KEEP: Prevents the most common AI agent failure — claiming something works without checking.

before_claiming_done:
  - Run the code — do not assume it works
  - Verify files were actually written to disk
  - Check that imports resolve and dependencies exist
  - Never assume a file exists — check first

# ─── Upgrade path ────────────────────────────────────────────────────────────
# Add at Level 2 (Small Team):
#   model_routing       — when AI spend exceeds $50/month
#   governance_sync     — when working >3 sessions/week on this project
#   mandatory_task_reporting — when you lose track of session progress
#   pr_workflow         — when you add a collaborator
#
# Add at Level 3 (Enterprise):
#   compliance          — when subject to GDPR, EU AI Act, or SOC2
#   definition_of_done  — when "done" needs a formal checklist
#   change_control      — when CLAUDE.md changes affect multiple teams
#   escalation_model    — when you need formal incident response
