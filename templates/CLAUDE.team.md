# CLAUDE.team.md — Team-Level AI Agent Constitution
#
# This file extends the organization constitution for a specific team.
# All repos in this team inherit these rules in addition to org rules.
#
# OWNERSHIP: Tech Lead
# CHANGE PROCESS: PR with team review (at least one other team member)
# REVIEW CADENCE: Monthly, as part of team retrospective.
#
# This file EXTENDS org rules. It cannot WEAKEN them.
# If you need an exception to an org rule, submit a PR to CLAUDE.org.md.

---

## inherits_from
# REQUIRED: Reference the org-level constitution.
# CUSTOMIZE: Replace with your organization's actual constitution URL or path.
- org: https://github.com/company/ai-governance/CLAUDE.org.md
# For local setups:
# - org: ~/.claude/CLAUDE.org.md

---

## team_context
# CUSTOMIZE: Describe your team's domain, stack, and workflow.
# WHY: Agents use this to understand what domain-specific rules mean.
# Without it, domain rules read as arbitrary constraints.

team: "[team name]"
domain: "[what the team works on — one sentence]"
stack: "[primary languages, frameworks, platforms]"
owner: "[Tech Lead name or role]"
repos: "[list of repos or link to team's GitHub org]"

---

## team_rules
# These rules EXTEND org rules.
# They cannot weaken, remove, or create exceptions to org rules.
# They add team-specific requirements that all team repos share.

### model_routing
# CUSTOMIZE: Team-specific model routing preferences.
# EXTEND: Org requires Opus for security. You can require Opus for additional task types.
# DO NOT: Lower model requirements below what org specifies.

routing_table:
  # Inherited from org (cannot change):
  security_review: opus

  # CUSTOMIZE: Team-specific additions
  architecture_decisions: opus
  code_review: sonnet
  code_generation: sonnet
  documentation: sonnet
  config_edits: haiku

### agents
# CUSTOMIZE: Which specialized agents this team uses beyond any org-mandated ones.
# List agents from the agents/ directory that all team repos should activate.

always_active:
  - security-reviewer   # Inherited org requirement
  # CUSTOMIZE: Add team-specific always-active agents

on_pr:
  - code-reviewer
  - quality-gate-agent
  # CUSTOMIZE: Add team-specific PR review agents

### workflow
# CUSTOMIZE: Team-specific session protocol adjustments.
# EXTEND: You can add steps. You cannot remove required org steps.

session_protocol_extensions:
  on_session_start:
    - Check PROJECT_PLAN.md for the current sprint goal before starting work
    - Verify that the session scope is consistent with sprint priorities
    # CUSTOMIZE: Add team-specific checks
    # Example: - Confirm no team-shared config files changed without notification

  on_session_end:
    - Update PROJECT_PLAN.md sprint status if goal completion percentage changed
    - Flag any architectural decisions made this session in CHANGELOG.md
    # CUSTOMIZE: Add team-specific end-of-session steps
    # Example: - Post session summary to team Slack channel

### naming
# CUSTOMIZE: Team-specific naming extensions.
# EXTEND: Add more specific rules. Do not contradict org naming rules.

extensions:
  test_files: "test_[module].py — all test files use test_ prefix"
  # CUSTOMIZE: Add domain-specific naming rules, for example:
  # api_endpoints: /api/v1/kebab-case
  # database_tables: snake_case with domain prefix
  # terraform_resources: snake_case with service_env_ prefix

---

## team_security
# EXTEND: Add team-specific security rules beyond org requirements.
# Do not repeat or modify org security rules — they are inherited automatically.

data_handling:
  - Never include production data samples in test fixtures
  - All new tables or data models must be reviewed for PII fields before merge
  # CUSTOMIZE: Add domain-specific data handling rules

credential_handling:
  - Rotate any accidentally committed credentials within 1 hour (not 24 hours)
  # CUSTOMIZE: Add team-specific credential rotation or access rules

---

## team_knowledge
# CUSTOMIZE: Team-specific knowledge files that agents should read at session start.

required_files:
  - CLAUDE.md         # Repo constitution (always)
  - PROJECT_PLAN.md   # Sprint status (always)
  - CHANGELOG.md      # Session history (always)
  # CUSTOMIZE: Add team-specific files
  # - ARCHITECTURE.md   # Add at Level 2+
  # - MEMORY.md         # Add at Level 2+

---

## team_quality
# CUSTOMIZE: Team-specific quality thresholds.
# EXTEND: Set higher thresholds than org minimums. Do not set lower.

test_coverage_minimum: 70     # Adjust upward if org sets a minimum
pr_review_required_from: tech_lead_or_senior
  # CUSTOMIZE: Options: any_team_member | senior | tech_lead_or_senior | tech_lead_only

---

## extension_note
# Repos using this team constitution:
# 1. Inherit all org rules (from inherits_from above)
# 2. Inherit all team rules defined in this file
# 3. Add project-specific rules in their own CLAUDE.md
#
# Repo-level CLAUDE.md structure:
#
# ## inherits_from
# - org: [org URL]
# - team: [team URL or path to this file]
#
# ## local_rules
# [project-specific rules that extend team rules]
