# CLAUDE.org.md — Organization-Level AI Agent Constitution
#
# This file defines universal AI governance rules for all teams and repositories.
# ALL repos in this organization inherit these rules automatically.
#
# OWNERSHIP: Engineering Leadership / Platform Team
# CHANGE PROCESS: RFC → team review → designated approver → merge
# REVIEW CADENCE: Quarterly. Emergency changes require security lead + CTO sign-off.
#
# Keep this file SHORT (target ~50 lines).
# More lines = more rigidity = more conflict with team needs.
# Only rules that must apply to ALL teams belong here.
# Domain-specific rules belong in CLAUDE.team.md.

---

## org_identity
# REQUIRED: Update before first use.
# WHY: Agents need org context to understand the scope of what they govern.

org_name: "[Organization Name]"
governance_version: "1.0.0"
effective_date: "[YYYY-MM-DD]"
owner: "[Engineering Leadership / Platform Team]"

---

## org_security
# REQUIRED: All teams follow these rules without exception.
# RATIONALE: Security failures at any repo risk the entire organization.
# These rules are the baseline below which no team may go.

never_commit:
  # REQUIRED: Non-negotiable. No team exceptions.
  - API keys, tokens, secrets of any kind (even test/dummy values that look real)
  - Passwords, credentials, JWT secrets, signing keys
  - PII: names, emails, national IDs, phone numbers, addresses
  - Health data: diagnoses, biometrics, patient records
  - Financial data: account numbers, card numbers, salary data
  - Internal hostnames, IP ranges, production connection strings
  - Real data samples of any kind, even if believed to be anonymized

security_review_model: opus
# REQUIRED: Security review always uses the strongest available model.
# CUSTOMIZE: Replace opus with your organization's designated high-capability model.
# RATIONALE: Security review is where false negatives are most costly.
# Cost of stronger model review is trivially small vs. cost of a missed vulnerability.

pre_commit_hooks: required
# REQUIRED: Secret scanning must run on every commit, on every developer's machine.
# Minimum: gitleaks or equivalent. See docs/security-guide.md for configuration.

---

## org_compliance
# REQUIRED: Audit trail requirements for all teams.
# RATIONALE: AI-assisted development produces changes at 10-15x human speed.
# Without an audit trail, "what changed and why" becomes unanswerable.

session_changelog: required
# REQUIRED: Every session must produce a CHANGELOG entry before committing.
# The entry must include: files modified, decisions made, goal progress.

pr_human_review: required
# REQUIRED: Every pull request requires at least one human approval.
# AI review assists but never replaces human review.
# RATIONALE: Human judgment is the last defense against automation bias.

constitutional_changes: pr_only
# REQUIRED: Changes to any CLAUDE.md file require a pull request.
# No direct commits to governance files, at any level.

---

## org_naming
# CUSTOMIZE: These are defaults. Teams may extend them (be more specific).
# Teams may NOT contradict them (use a different scheme).

identifiers: snake_case
classes: PascalCase
constants: UPPER_SNAKE_CASE
branches: "feature/ | fix/ | docs/ | refactor/ | test/ | hotfix/"
commits: "type(scope): description in present tense"
commit_types: "feat, fix, docs, refactor, test, chore, perf, security"

language: English
# REQUIRED: All code, comments, docstrings, and documentation in English.
# RATIONALE: Cross-team review and AI governance both depend on consistent language.

---

## org_kill_switch
# REQUIRED: Agents must stop immediately when these conditions are met.
# Teams may ADD triggers. Teams may not REMOVE these triggers.
# See docs/kill-switch.md for full specification.

mandatory_stop_conditions:
  - About to commit any item in never_commit list
  - About to merge to main without PR review
  - Confidence below 30% on 3 consecutive tasks (context confusion likely)
  - Detected error→fix→error loop (3+ cycles on the same issue)

---

## inherits_from
# Leave blank at org level — this IS the root.
# Teams inherit FROM this file.

## extension_note
# Teams: copy relevant sections to CLAUDE.team.md and add domain-specific rules.
# Rules here flow down to all repos. Rules in CLAUDE.team.md flow to team repos only.
# Rules in repo CLAUDE.md apply only to that repository.
# At every level: EXTEND parent rules. Never WEAKEN them.
