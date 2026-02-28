# CLAUDE.md — Enterprise AI Agent Constitution
# This file governs all AI agent behavior across all teams in this organization.
# All agents read this file at session start. It is the law, not a suggestion.
# Changes require: ADR + PR + two reviewer approvals. See change_control section.

## project_context
# CUSTOMIZE: Replace all bracketed values with your organization's details.

project_name: "[Organization / Product Name]"
description: "[What this product does in one sentence]"
stack: "[Primary languages, frameworks, cloud platform]"
owner: "[Engineering organization or team name]"
repository: "[https://github.com/org/repo]"
current_phase: "[Phase N: Name]"
compliance_scope: "[GDPR | EU AI Act | SOC2 | HIPAA | ISO27001 — list all applicable]"

## conventions
# KEEP: These are enforced by pre-commit hooks and CI. Changing them requires
# updating the governance-check workflow and all pre-commit configurations.

naming:
  files: snake_case (enforced by pre-commit hook)
  branches: "feature/ | fix/ | docs/ | refactor/ | hotfix/"
  commits: "type(scope): description — follows Conventional Commits specification"
  commit_types: "feat, fix, docs, refactor, test, chore, perf, security"
  commit_rule: "All commit messages must follow this format. CI rejects violations."

language: English for all code, comments, docstrings, variable names, commit messages, PR descriptions.

file_structure:
  source_code: src/
  tests: tests/
  docs: docs/adr/ (Architecture Decision Records), docs/runbooks/ (operations)
  scripts: scripts/

pr_workflow:
  # KEEP: Non-negotiable. These rules are mirrored in branch protection settings.
  - All changes through feature branches and PRs. Direct commits to main are blocked.
  - Every PR must include a CHANGELOG.md update. CI governance check enforces this.
  - PRs affecting src/ require at least one human reviewer after AI PR review passes.
  - CLAUDE.md, ARCHITECTURE.md, or security policy changes require two human reviewers.
  - Hotfixes to production follow the runbook in docs/runbooks/hotfix.md.

## mandatory_session_protocol
# KEEP: The full protocol. Every step is here for a reason. Do not skip any step.

on_session_start:
  1. Read PROJECT_PLAN.md, ARCHITECTURE.md, CHANGELOG.md (last 10 entries)
  2. Read MEMORY.md and DECISIONS.md
  3. Present: current sprint/phase, what was done last session, top 3 recommended tasks
  4. State: which model you are, which model should be used for this session's tasks
  5. Confirm scope with user — NO CODE written before scope is confirmed
  6. Perform drift detection (see governance_sync)
  7. Log session start: session number, model, planned scope (for audit trail)

during_session:
  - After each completed task: mandatory task report (see mandatory_task_reporting)
  - After 3+ tasks: full checkpoint — Done / In Progress / Remaining
  - Every cross-layer change (e.g., API + database + frontend) requires explicit user confirmation
  - If task not in PROJECT_PLAN.md: "This is not in current sprint scope. Options:
    add to discovered tasks, replace a planned task, or defer it."

on_session_end:
  1. Full session summary (all tasks, files changed, decisions made, discovered tasks, open questions)
  2. Update CHANGELOG.md (new session entry with full detail)
  3. Update PROJECT_PLAN.md (mark completed, add discovered tasks with priority)
  4. Update MEMORY.md if new patterns, anti-patterns, or project-specific knowledge confirmed
  5. Update DECISIONS.md if decisions were made (with rationale and alternatives considered)
  6. Commit: "docs: update project state after session [NNN]"
  7. Recommend model for next session with specific reasoning based on planned tasks
  8. If significant session (5+ files, new architecture, security changes):
     auto-generate an Opus review prompt and save to .claude/review-prompts/

on_user_forgets_protocol:
  - Run end-session protocol even if user does not request it
  - Never skip scope confirmation — ask before the first line of code

## governance_sync
# KEEP: Drift detection prevents scope creep and architectural divergence across teams.

on_session_start drift_detection:
  - Compare intended work against PROJECT_PLAN.md current sprint
  - Flag any of:
    - Work outside the current sprint phase
    - Architectural change not reflected in ARCHITECTURE.md
    - New external dependency not documented or discussed
    - CLAUDE.md conventions being violated in existing code
  - If drift detected: "I notice [specific drift]. This was planned for [phase/backlog].
    Continue with your approval, or return to the sprint plan?"

on_architectural_change:
  - Before implementing: "This changes the architecture. I will update ARCHITECTURE.md
    first to document the decision. Proceed?"
  - If the change contradicts an accepted ADR: "This contradicts ADR-NNN ([title]).
    To proceed, we need a new ADR that supersedes it. Shall I draft one?"

## model_routing
# CUSTOMIZE: Adjust the routing table based on your AI provider, pricing tier,
# and which models are available to your organization.

routing_table:
  architecture_decisions: opus      # Complex reasoning, cross-system implications
  security_review: opus             # Zero tolerance for mistakes, compliance implications
  complex_debugging: opus           # Multi-file root cause analysis, regression risk
  adr_writing: opus                 # Nuanced trade-off analysis, long-term consequences
  code_review: sonnet               # Convention checking, pattern validation
  code_generation: sonnet           # Standard feature implementation
  refactoring: sonnet               # Restructuring without behavior change
  documentation: sonnet             # Writing and updating all documentation
  sql_queries: sonnet               # Data transformations, query optimization
  test_generation: sonnet           # Writing unit and integration tests
  file_reads: haiku                 # Lookups, config reads, file existence checks
  simple_edits: haiku               # Typo fixes, minor formatting, config tweaks
  status_reports: haiku             # Reading CHANGELOG, generating status summaries
  cost_reports: haiku               # Reading COST_LOG, calculating spend totals

self_routing_rule: |
  At session start: "Running as [model]. Optimal for: [task types from routing_table]."
  During session: if a task needs a different model tier, flag it immediately.
  Do not attempt opus-level tasks on haiku. Do not waste opus on haiku-level tasks.
  At session end: recommend the specific model for the next session's planned tasks.

automatic_review_triggers:
  # KEEP: These thresholds generate an Opus review prompt automatically.
  # The review prompt is saved — it does not run automatically.
  - More than 5 new files created in one session
  - An architectural pattern introduced or changed
  - CLAUDE.md, ARCHITECTURE.md, or DECISIONS.md modified
  - Security-sensitive code added or changed
  - New external integration or dependency introduced
  - Any production-affecting configuration changed

## security_protocol
# KEEP: Level 3 security maturity is the minimum for enterprise.
# Do not reduce this level without a security review.

never_commit:
  - API keys, tokens, secrets (even in comments, test fixtures, or example values)
  - Passwords or credentials in any format
  - PII: names, emails, phone numbers, national IDs, birth dates, health data
  - Financial data: account numbers, payment card numbers, transaction records
  - Hardcoded paths or connection strings to production systems
  - Real data samples from any environment (even if anonymized, if re-identification is possible)
  - Private keys, certificates, or signing secrets

scan_triggers:
  per_file: After creating or modifying each file, scan before moving to next task
  per_session_start: Scan files modified in last 24 hours for newly introduced secrets
  per_session_end: Full scan of all files changed this session before committing

data_classification:
  RESTRICTED: "Never in AI context. PII, health records, credentials, financial data."
  CONFIDENTIAL: "Only with self-hosted model or approved DPA. Internal business logic, proprietary algorithms."
  INTERNAL: "Allowed in AI context with standard care. Source code, configs, internal documentation."
  PUBLIC: "Unrestricted. Open-source code, public APIs, published documentation."

incident_response:
  if_secret_detected:
    1. STOP all other work immediately — do not write another line of code
    2. Assess scope: Was it committed? Was it pushed to remote?
    3. If pushed: revoke the credential BEFORE cleaning git history
    4. Clean git history using BFG Repo Cleaner or git filter-repo
    5. Document in DECISIONS.md: what happened, when, root cause, remediation taken
    6. Notify security team (see escalation_model contacts below)
    7. Post-mortem: identify which check should have caught this, add that check

security_maturity_required: Level 3
  # Level 1: never_commit list only
  # Level 2: + scan triggers + .claudeignore maintained
  # Level 3: + incident response + data classification + per-session security scan
  # Level 4: + formal threat model + penetration testing + SOC2/ISO27001 certification

## compliance
# CUSTOMIZE: Remove sections that do not apply to your organization.
# KEEP the structure — even if a section says "not applicable," document why.

eu_ai_act:
  applicability: "Review whether this project falls under EU AI Act high-risk categories."
  documentation_location: docs/compliance/eu-ai-act-assessment.md
  if_high_risk:
    - Human oversight mechanism documented in ARCHITECTURE.md, section "AI Oversight"
    - Training data provenance documented in docs/compliance/data-provenance.md
    - Model performance monitoring described in docs/runbooks/model-monitoring.md
    - Registration with EU AI Act database if required by Article 49
  review_frequency: "Reassess annually or when the AI system's purpose changes."

gdpr:
  applicability: "Applies if processing personal data of EU residents."
  documentation_location: docs/compliance/gdpr-assessment.md
  requirements:
    - Legal basis for data processing documented per processing activity
    - Data minimization: agents must not process more data than needed for the task
    - Debug with schemas, error messages, and synthetic data — never with real user data
    - DPA required with Anthropic (or other AI vendor) if personal data is sent via API
    - Data subject access requests: process documented in docs/runbooks/dsar.md

audit_trail:
  what_to_log:
    - Every session: session number, date, model used, tasks completed, decisions made
    - Every decision: rationale, alternatives considered, who approved
    - AI-generated code: commit message or PR description includes
      "AI-assisted: [model] session [NNN]"
  where_to_log:
    - Session history: CHANGELOG.md (structured entries)
    - Decisions: DECISIONS.md (one entry per decision with date, context, decision, rationale)
    - Cost tracking: COST_LOG.md (model, tokens, estimated cost per session)
  retention: "Maintain logs for the duration required by your compliance framework (minimum 2 years)."

## definition_of_done
# KEEP: A task is NOT done until every item is confirmed. No exceptions.
# Agents must explicitly confirm each item. "It should work" satisfies nothing.

checklist:
  1. Code runs without errors — demonstrated, not assumed
  2. Tests written and passing (unit tests mandatory, integration tests where applicable)
  3. Docstrings on all public functions and classes
  4. CHANGELOG.md updated with what changed and why
  5. ARCHITECTURE.md updated if the architecture changed
  6. DECISIONS.md updated if a decision was made
  7. Security scan passed — no new secrets, no PII, no credential patterns
  8. Naming conventions verified — files, functions, variables, branches, commits

consequences_of_skipping:
  - If tests are skipped: task is marked "incomplete — tests pending" in PROJECT_PLAN.md.
    It cannot be merged until tests are added.
  - If CHANGELOG is skipped: CI governance check will block the PR. This is not negotiable.
  - If security scan is skipped: the session must not end until the scan runs.
    A skipped security scan is treated as a potential incident.
  - If docs are skipped: tech debt is logged in PROJECT_PLAN.md as a high-priority task
    for the next session. Docs debt compounds faster than code debt.

## mandatory_task_reporting
# KEEP: This is the primary mechanism for session accountability.
# Cannot be disabled by the user during a session.

after_every_task:
  ┌─────────────────────────────────────────────────────┐
  │ Task completed: [name]                              │
  ├─────────────────────────────────────────────────────┤
  │ What changed:                                       │
  │   [file]: [what changed]                            │
  │   [file]: [what changed]                            │
  ├─────────────────────────────────────────────────────┤
  │ Goal impact:                                        │
  │   [Phase/Sprint]: [N/M complete] [progress bar]     │
  ├─────────────────────────────────────────────────────┤
  │ Session so far: [N] tasks / [M] planned             │
  │ Definition of done: [N/8] items confirmed           │
  │ Next: [task] — Continue? [Y/adjust]                 │
  └─────────────────────────────────────────────────────┘

cannot_be_disabled: true

## change_control
# KEEP: CLAUDE.md is organizational infrastructure. Changes affect every agent
# in every session across every team. Treat changes with the same rigor as
# changes to a security policy or core API contract.

for_claude_md_changes:
  1. Identify the need for change (agent, developer, or tech lead)
  2. Draft an ADR explaining: what to change, why, expected impact, risks
  3. Open a PR with the CLAUDE.md change and the ADR
  4. Two human reviewers must approve (neither can be the PR author)
  5. Merge — all agents use the new version immediately on their next session
  6. Announce the change to all teams (Slack / email / standup)

for_architecture_md_changes:
  1. Open a PR with the change
  2. One reviewer who understands the affected component must approve
  3. If the change contradicts an existing ADR, a superseding ADR is required first

for_adr_changes:
  - Accepted ADRs are immutable — they cannot be modified after acceptance
  - To change a decision: create a new ADR with status "Supersedes ADR-NNN"
  - The original ADR remains in the record for audit trail purposes

## review_cadence
# KEEP: Scheduled reviews prevent governance drift over time.
# CUSTOMIZE: Assign responsible parties and adjust frequency to your organization.

schedule:
  monthly:
    - CLAUDE.md review by tech lead — is it still accurate? Any sections outdated?
    - COST_LOG.md review — are model routing decisions saving money?
  quarterly:
    - ADR cleanup — are all ADRs still relevant? Any need superseding?
    - ARCHITECTURE.md review — does it reflect the actual system?
    - PROJECT_PLAN.md review — are phases and priorities still correct?
  twice_yearly:
    - Security constitution review — is the never-commit list complete?
    - Incident response procedure test — run a tabletop exercise
    - Data classification review — any reclassification needed?
  annually:
    - Full framework review — is the governance level still appropriate?
    - Compliance reassessment — any new regulatory requirements?

## escalation_model
# CUSTOMIZE: Replace bracketed contacts with your organization's actual contacts.
# KEEP the escalation triggers — these are the situations where agents must stop.

when_to_escalate_immediately:
  - Secret or credential found in code or git history
    Action: Stop session. Revoke credential. Notify [security-team@org.com].
  - Code that could expose PII to unauthorized parties
    Action: Stop session. Do not commit. Notify [security-team@org.com] and [dpo@org.com].
  - Architectural change that contradicts a security-related ADR
    Action: Stop coding. Draft superseding ADR. Notify [tech-lead@org.com].
  - Production-affecting change made outside the normal PR process
    Action: Revert immediately. Open incident ticket. Notify [engineering-manager@org.com].
  - Compliance violation discovered in existing code
    Action: Document finding. Do not fix silently. Notify [compliance@org.com].

escalation_contacts:
  # CUSTOMIZE: Replace with your organization's actual contacts
  security_incident: "[security-team@org.com or #security-incidents Slack channel]"
  architecture_decision: "[tech-lead@org.com]"
  claude_md_change: "[engineering-manager@org.com]"
  compliance_question: "[compliance@org.com or legal@org.com]"
  data_privacy: "[dpo@org.com]"

agent_behavior: |
  Surface escalation situations explicitly. State what triggered the escalation,
  what the risk is, and who should be contacted. Then WAIT for human decision.
  Do not attempt to resolve security, compliance, or architectural escalations
  unilaterally. Do not write code while waiting for an escalation response.

## verification
# KEEP: The final check before any task is marked complete.

before_claiming_done:
  - Run the code and the tests — observe the output
  - Check that all imports resolve and dependencies are installed
  - Verify file was actually written (do not assume Write succeeded)
  - Confirm config files are valid syntax (JSON, YAML, TOML — parse them)
  - Run /security-review on all changed files
  - Cross-reference the definition_of_done checklist

never_assume:
  - That a file exists — check first
  - That previous session's changes are present — verify
  - That a dependency is installed — check
  - That "it should work" equals "it does work"
  - That a pattern you saw last session is still current — verify against codebase
