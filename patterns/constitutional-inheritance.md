# Pattern: Constitutional Inheritance

## Problem

A single CLAUDE.md cannot serve an entire organization. It is either too generic (useless)
or too specific (wrong for most teams). Teams that need different rules end up with divergent
constitutions that share no common security baseline. The org has no enforcement mechanism.
Security rules depend on each team implementing them correctly and independently.

## Solution

Hierarchical constitutions with hybrid inheritance rules. Three levels: org → team → repo.
Each level inherits from the level above. Resolution depends on rule category:

- **Safety rules** (security, compliance, kill switch, audit trail): higher level always wins.
  No lower level can weaken, narrow, or remove these rules.
- **Configurable rules** (model routing, coding style, workflow, stack declarations):
  more specific (lower-level) rules win. This aligns with Claude Code's runtime behavior.
- **External legal obligations** (GDPR, HIPAA, regulatory mandates): override all internal
  levels regardless of constitution hierarchy.

See [ADR-004](../docs/adr/ADR-004-hybrid-inheritance-model.md) for the full decision record.

## When to Use

- Organizations with 10+ developers using governed AI development
- Teams that need different workflow rules but share security requirements
- Any environment where governance needs to be verifiably consistent across repositories
- Regulated industries where security rules must be documented as non-negotiable

## When NOT to Use

- Solo developers or single-team organizations (one CLAUDE.md level is sufficient)
- Projects with fewer than 10 developers where direct communication replaces hierarchy
- Prototypes and exploratory projects where consistency across repos is not required

## Structure

```
Level 1: CLAUDE.org.md          — Universal rules. Security, compliance, naming baseline.
                                  Safety rules: nobody overrides these. Changes require RFC.
                                  Configurable rules: team/repo may specialize.

Level 2: CLAUDE.team.md         — Team-specific extensions. Workflow, model routing,
                                  domain rules. Cannot weaken Level 1 safety rules.
                                  Configurable rules take precedence over Level 1 defaults.

Level 3: CLAUDE.md (repo)       — Project-specific conventions. Architecture, tech stack,
                                  session protocol. Cannot weaken Level 1 or 2 safety rules.
                                  Configurable rules take precedence over Level 2 defaults.
```

### Precedence Stack (highest to lowest)

```
Legal / Regulatory  →  Org Safety  →  Team Safety  →  Org Config  →  Team Config  →  Repo Config
```

## Implementation

### Declaring Inheritance

In each repo's CLAUDE.md, declare parent constitutions:

```markdown
## inherits_from
- org: https://github.com/company/governance/CLAUDE.org.md
- team: https://github.com/company/platform-team/CLAUDE.team.md
```

### Validation at Session Start

The governance sync step checks:
1. Parent constitutions are reachable (or cached copy is current)
2. Local rules do not contradict inherited rules
3. Required sections from parent constitutions are present locally

If violations are found:
```
⚠️ Inheritance violation: local rule weakens org security requirement.
See docs/constitutional-inheritance.md for resolution options.
```

### Extending a Safety Rule (Valid)

```markdown
# Org safety rule: use snake_case for all identifiers
# Team extension (valid — more specific, not weaker):
# INHERITANCE: safety — higher-wins
naming:
  identifiers: snake_case
  module_constants: snake_case with MODULE_ prefix (e.g., AUTH_MAX_RETRIES)
  api_response_fields: snake_case (not camelCase — must match internal naming)
```

### Overriding a Safety Rule (Invalid)

```markdown
# Org safety rule: Opus required for all security reviews
# Repo "extension" (invalid — weakens the safety requirement):
# INHERITANCE: safety — higher-wins
security_review_model: sonnet   # ❌ Cannot lower model requirement set by org
```

### Overriding a Configurable Rule (Valid)

```markdown
# Org configurable default: code_generation_model: sonnet
# Repo override (valid — repo context is more specific):
# INHERITANCE: configurable — specific-wins
code_generation_model: haiku   # ✅ Repo uses lightweight tasks; lower cost appropriate
```

### Exception Process (for safety rules only)

When a lower level genuinely needs to weaken a safety rule:
1. Document why the exception is needed
2. Submit a PR to the higher-level constitution proposing either an exception mechanism
   or a revised rule that accommodates the use case
3. Do not implement the exception locally until the higher level approves it
4. If the situation is an operational emergency, use the break-glass mechanism
   documented in `patterns/break-glass.md` — with mandatory post-incident review

Configurable rules do not require this process. Lower-level specifications of configurable
rules are the intended behavior, not exceptions requiring approval.

## Example

### CLAUDE.org.md (org level — ~50 lines)

```markdown
## org_security
# REQUIRED: All teams follow these rules without exception.
never_commit:
  - API keys, tokens, credentials of any kind
  - PII: names, emails, health data, financial data
  - Internal hostnames, IP addresses, production paths
  - Real data samples

security_review_model: opus   # REQUIRED: Never downgrade for security review
pre_commit_hooks: required    # REQUIRED: Secret scanning on every commit

## org_compliance
# REQUIRED: Audit trail requirements
session_changelog: required   # Every session produces a CHANGELOG entry
pr_human_review: required     # Every PR requires human approval
```

### CLAUDE.team.md (team level — extends org)

```markdown
## inherits_from
- org: https://github.com/company/governance/CLAUDE.org.md

## team_context
team: Platform Engineering
domain: Internal developer tooling, CI/CD infrastructure
stack: Python, Kubernetes, Terraform, GitHub Actions

## team_rules
# EXTENDS org rules. Cannot weaken them.

model_routing:
  infrastructure_review: opus    # Team adds: Opus for infra changes (org only required security)
  code_generation: sonnet
  config_edits: haiku

agents:
  # Team uses all org-mandated agents plus:
  - infrastructure-reviewer      # Team-specific for Terraform/K8s review
```

### CLAUDE.md (repo level — extends team)

```markdown
## inherits_from
- org: https://github.com/company/governance/CLAUDE.org.md
- team: https://github.com/company/platform-team/CLAUDE.team.md

## project_context
project_name: "CI Orchestrator"
stack: "Python 3.12, FastAPI, PostgreSQL, deployed to internal K8s"

## local_rules
# EXTENDS team rules. Cannot weaken them.

naming:
  api_endpoints: /api/v1/kebab-case
  database_tables: snake_case with ci_ prefix
```

## Outcome

Any agent reading the repo-level CLAUDE.md inherits all three levels of rules simultaneously.
The agent knows:
- Security rules from org (non-negotiable)
- Workflow rules from team (consistent across all team repos)
- Project conventions from repo (specific to this codebase)

A new developer joining the team gets consistent governance across all repos they touch.
A security audit can verify that org-level rules are present in every repo.

## Related Patterns

- [docs/constitutional-inheritance.md](../docs/constitutional-inheritance.md) — full specification
- [docs/adr/ADR-004-hybrid-inheritance-model.md](../docs/adr/ADR-004-hybrid-inheritance-model.md) — decision record for hybrid model
- [patterns/break-glass.md](break-glass.md) — temporary override for governance emergencies
- [templates/CLAUDE.org.md](../templates/CLAUDE.org.md) — org-level template
- [templates/CLAUDE.team.md](../templates/CLAUDE.team.md) — team-level template
- [docs/architecture.md](../docs/architecture.md) — Layer 1 (Constitution) in the 7-layer stack
