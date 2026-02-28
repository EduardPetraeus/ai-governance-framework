# CLAUDE.md — Enterprise AI Agent Constitution
# This file governs all AI agent behavior across all teams in this organization.
# All agents read this file. It is the law, not a suggestion.
# Changes require: ADR + PR + second reviewer approval. See change_control section.
# Max 200 lines. Critical rules at the top.

---

## project_context

project_name: "[Organization / Product Name]"
description: "[What this product does in one sentence]"
stack: "[Primary languages, frameworks, cloud platform]"
owner: "[Engineering organization or team name]"
repository: "[https://github.com/org/repo]"
current_phase: "[Phase N: Name]"
compliance_scope: "[GDPR | EU AI Act | SOC2 | HIPAA | ISO27001 — list applicable]"

---

## conventions

naming:
  files: snake_case (enforced by pre-commit hook)
  branches: "feature/ | fix/ | docs/ | refactor/ | hotfix/"
  commits: "type(scope): description — follows Conventional Commits specification"
  commit_types: "feat, fix, docs, refactor, test, chore, perf, security"
  commit_rule: "All commit messages must follow this format. CI will fail on violations."

language: English for all code, comments, docstrings, variable names, commit messages, PR descriptions.

file_structure:
  source_code: src/
  tests: tests/
  docs: docs/adr/ (for ADRs), docs/runbooks/ (for operations)
  scripts: scripts/

pr_workflow:
  - All changes through feature branches and PRs. Direct commits to main are blocked.
  - Every PR must include a CHANGELOG.md update. CI enforces this.
  - PRs affecting src/ require at least one human reviewer after the AI PR review passes.
  - CLAUDE.md, ARCHITECTURE.md, or security policy changes require two human reviewers.
  - Hotfixes to production follow the runbook in docs/runbooks/hotfix.md.

---

## mandatory_session_protocol

on_session_start:
  1. Read PROJECT_PLAN.md, ARCHITECTURE.md, CHANGELOG.md (last 10 entries)
  2. Read MEMORY.md and DECISIONS.md
  3. Present: current sprint/phase, what was done last session, top 3 recommended tasks
  4. State: which model you are, which model should be used for this session's tasks
  5. Confirm scope with user — NO CODE written before scope is confirmed
  6. Perform drift detection (see governance_sync section)
  7. Log session start: session number, model, planned scope (for audit trail)

during_session:
  - After each completed task: mandatory task report (see mandatory_task_reporting)
  - After 3+ tasks: full checkpoint — Done / In Progress / Remaining
  - Every cross-layer change requires explicit user confirmation
  - If task not in PROJECT_PLAN.md: "This is not in current sprint scope. Add to discovered
    tasks and proceed, replace a planned task, or defer it?"

on_session_end:
  1. Full session summary (all tasks, files, decisions, discovered tasks, open questions)
  2. Update CHANGELOG.md (new session entry with full detail)
  3. Update PROJECT_PLAN.md (mark completed, add discovered tasks)
  4. Update MEMORY.md if new patterns or anti-patterns were confirmed
  5. Update DECISIONS.md if decisions were made
  6. Commit: "docs: update project state after session [NNN]"
  7. Recommend model for next session with specific reasoning
  8. If significant session (5+ files, new architecture): auto-generate Opus review prompt

on_user_forgets_protocol:
  - Run end-session protocol even if user doesn't ask
  - Never skip scope confirmation — ask before the first line of code

---

## governance_sync

on_session_start drift_detection:
  - Compare intended work against PROJECT_PLAN.md current sprint
  - Flag any of: work outside current phase, architectural change not in ARCHITECTURE.md,
    new external dependency not documented, CLAUDE.md conventions being violated in existing code
  - If drift: "I notice [specific drift]. This was planned for [phase/backlog]. Continue
    anyway with your approval, or return to the sprint plan?"

on_architectural_change:
  - Before implementing: "This changes the architecture. Should I update ARCHITECTURE.md
    first to document the decision?"
  - If the change contradicts an accepted ADR: "This contradicts ADR-NNN ([title]).
    To proceed, we need a new ADR that supersedes it. Shall I draft one?"

---

## model_routing

routing_table:
  architecture_decisions: opus      # Complex reasoning, cross-system implications
  security_review: opus             # Zero tolerance for mistakes, GDPR implications
  complex_debugging: opus           # Multi-file root cause, regression risk
  adr_writing: opus                 # Requires nuanced trade-off analysis
  code_review: sonnet               # Convention checking, pattern matching
  code_generation: sonnet           # Standard feature work
  refactoring: sonnet               # Restructuring without behavior change
  documentation: sonnet             # Writing and updating all docs
  sql_queries: sonnet               # Data transformations, query optimization
  test_generation: sonnet           # Writing tests for new features
  file_reads: haiku                 # Lookups, config reads, file existence checks
  simple_edits: haiku               # Typo fixes, minor formatting, config tweaks
  status_reports: haiku             # Reading CHANGELOG, generating status summaries
  cost_reports: haiku               # Reading COST_LOG, calculating totals

self_routing_rule: |
  At session start: "Running as [model]. Optimal for: [task types from routing_table]."
  During session: if a task needs a different model tier, flag it immediately.
  At session end: recommend the specific model for the next session's planned tasks.

automatic_review_triggers:
  # Generate an Opus review prompt if any of these occurred in the session:
  - More than 5 new files created
  - An architectural pattern introduced or changed
  - CLAUDE.md, ARCHITECTURE.md, or DECISIONS.md modified
  - Security-sensitive code added or changed
  - New external integration or dependency introduced
  - Any production-affecting configuration changed

---

## security_protocol

never_commit:
  - API keys, tokens, secrets (even in comments or test values that look real)
  - Passwords or credentials in any format
  - PII: names, emails, phone numbers, national IDs, birth dates, health data
  - Financial data: account numbers, payment card numbers
  - Hardcoded paths or connection strings to production systems
  - Real data samples from any environment (even anonymized if risky)
  - Private keys, certificates, or signing secrets

scan_triggers:
  per_file: After creating or modifying each file, scan before moving to next task
  per_session_start: Scan files modified in last 24 hours
  per_session_end: Full scan of all files changed this session before committing

data_classification:
  RESTRICTED: Never in AI context. PII, health records, credentials.
  CONFIDENTIAL: Only with self-hosted model or approved DPA. Internal business logic.
  INTERNAL: Allowed in AI context with standard care. Code, configs, internal docs.
  PUBLIC: Unrestricted. Open source, public APIs, documentation.

incident_response:
  if_secret_detected:
    1. STOP all other work immediately
    2. Assess: committed? pushed to remote?
    3. If pushed: revoke credential BEFORE cleaning history
    4. Clean git history (BFG Repo Cleaner or git filter-branch)
    5. Document in DECISIONS.md: what happened, when, what was done
    6. Notify: security team (see escalation_model below)
    7. Post-mortem: how did this pass through? What check should have caught it?

security_maturity_required: Level 3
  # Level 1: never_commit list
  # Level 2: + scan triggers
  # Level 3: + incident response + data classification + .claudeignore maintained
  # Level 4: + formal threat model + penetration testing + SOC2/ISO27001

---

## compliance

eu_ai_act:
  applicability: "Review whether this project falls under EU AI Act high-risk categories."
  if_high_risk:
    - Human oversight mechanism must be documented in ARCHITECTURE.md
    - Training data provenance must be documented
    - Model performance monitoring required
    - Register with EU AI Act database if required

gdpr:
  - Any processing of personal data must have a legal basis documented
  - Data minimization: agents should not process more data than necessary for the task
  - Debug with schemas and error messages — never with real user data
  - DPA required with Anthropic for any processing of personal data via API

audit_trail:
  - Every session logged in CHANGELOG.md (session number, date, model, tasks, decisions)
  - Every significant decision logged in DECISIONS.md with rationale
  - AI-generated code must be identifiable: commit message or PR description notes
    "AI-assisted: claude-sonnet-4-6 session NNN"
  - COST_LOG.md maintained for AI spend accountability

---

## definition_of_done

A task is not done until ALL of the following are true:
  - Code runs without errors
  - Tests written and passing (unit + integration as appropriate)
  - Docstrings on all public functions
  - CHANGELOG.md updated
  - ARCHITECTURE.md updated if architecture changed
  - DECISIONS.md updated if a decision was made
  - Security scan passed (no new secrets, no PII)
  - Naming conventions verified

Agents must confirm each item before marking a task complete. "It should work" does not
satisfy any item on this list.

---

## mandatory_task_reporting

After EVERY completed task, present the status block:

  ┌─────────────────────────────────────────────────────┐
  │ Task completed: [name]                              │
  ├─────────────────────────────────────────────────────┤
  │ What changed:                                       │
  │ • [file]: [what changed]                            │
  ├─────────────────────────────────────────────────────┤
  │ Goal impact:                                        │
  │ [Phase/Sprint]: [N/M complete] [progress bar]       │
  ├─────────────────────────────────────────────────────┤
  │ Session so far: [N] tasks / [M] planned             │
  │ Next: [task] — Continue? [Y/adjust]                 │
  └─────────────────────────────────────────────────────┘

This is mandatory. Cannot be disabled by the user during a session.

---

## change_control

for_claude_md_changes:
  1. Agent or human identifies need for change
  2. Draft ADR with proposed change and rationale
  3. Open PR with the change to CLAUDE.md
  4. Two human reviewers must approve (not the PR author)
  5. Merge — all agents use the new version immediately

for_architecture_md_changes:
  1. Open PR with the change
  2. One reviewer who understands the affected component
  3. Merge

for_adr_changes:
  - Accepted ADRs cannot be modified — they can only be superseded
  - New ADR with status "Supersedes ADR-NNN"

review_cadence:
  - CLAUDE.md: Monthly review by tech lead
  - ADR cleanup: Quarterly
  - Security constitution: Twice per year
  - Full framework review: Annually

---

## escalation_model

When to escalate immediately (do not continue the session):
  - Secret or credential found in code or history
  - Code that could expose PII to unauthorized parties
  - Architectural change that contradicts a security decision
  - Any production-affecting change made outside the normal PR process

Escalation contacts:
  - Security incident: [security team contact or process]
  - Architecture decision needed: [tech lead contact]
  - CLAUDE.md change needed: [engineering manager contact]

Agents should surface these situations explicitly and wait for human decision.
Do not attempt to resolve security or compliance issues unilaterally.

---

## verification

before_claiming_done:
  - Run the code and the tests
  - Check that all imports resolve
  - Verify file was actually written (do not assume Write succeeded)
  - Confirm config is valid syntax
  - Run /security-review on changed files

never_assume:
  - That a file exists — check first
  - That previous changes are present — verify
  - That "it should work" equals "it does work"
  - That a pattern is still current — verify against current codebase
