# Constitutional Inheritance: Org → Team → Repo

## The Problem With a Single CLAUDE.md

In a 50-person engineering organization, a single global CLAUDE.md is either:
- Too vague to be useful (lowest common denominator rules that mean nothing to any specific team)
- Too specific to one team's workflow (the platform team's rules embedded in a mobile team's repo)
- Constantly contested (whose conventions win when teams have different standards?)

The result is one of three failure modes: the global CLAUDE.md is never written, it is written and ignored, or it is written and creates constant friction. None of these outcomes serves governance.

The same problem appears at smaller scales. A solo developer with three projects needs different project-specific rules, but wants to define security and naming rules once. A team of five needs team-level workflow preferences without touching the security constitution.

The solution is **constitutional inheritance**: a strict hierarchy where rules flow down, and lower levels can extend but never weaken higher levels.

---

## The Inheritance Model

```
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE.org.md (Organization Level)                           │
│ Security rules, compliance, naming standards                 │
│ CANNOT be overridden by lower levels                         │
├─────────────────────────────────────────────────────────────┤
│ CLAUDE.team.md (Team Level)                                  │
│ Workflow preferences, agent selection,                       │
│ model routing, domain-specific rules                         │
│ Can EXTEND org rules, cannot WEAKEN them                     │
├─────────────────────────────────────────────────────────────┤
│ CLAUDE.md (Repo Level)                                       │
│ Project-specific conventions, architecture,                  │
│ tech stack, session protocol customization                   │
│ Can EXTEND team rules, cannot WEAKEN them                    │
└─────────────────────────────────────────────────────────────┘
```

Each level specializes the level above it. Specialization is additive, never subtractive.

---

## Rule Resolution

The framework uses a **hybrid inheritance model** with two distinct resolution rules.
Rule category determines which rule applies — not the level of the rule alone.
See [ADR-004](adr/ADR-004-hybrid-inheritance-model.md) for the full decision record.

---

### Safety Rules — Higher Wins

Safety rules prevent harm that cannot be corrected after the fact. Higher level always wins.

A rule is a safety rule if it governs:
- The `never_commit` list and all items on it
- Security review model requirements
- Kill switch / mandatory stop conditions
- Pre-commit hook requirements
- PR human review requirements
- Constitutional change process (PR-only)
- Compliance, audit trail, and data classification requirements
- PII handling and credential rotation

No lower level can narrow, weaken, or remove a safety rule. If org says "never commit
secrets," no team or repo rule can create an exception — not even for test credentials.

---

### Configurable Rules — Specific Wins

Configurable rules optimize workflow, express preferences, or capture accurate technical
context. More specific (lower-level) rules take precedence over higher-level defaults.

A rule is configurable if it governs:
- Model routing (except security review model floor)
- Coding style and naming convention extensions
- Session length and protocol customizations
- Agent selection beyond org-mandated minimum
- Workflow step additions and sequencing
- Test coverage thresholds (org sets floor; teams/repos may raise)
- Technology stack declarations
- Domain-specific rules

This aligns with Claude Code's runtime behavior: a repo CLAUDE.md that declares a specific
tech stack overrides the org's generic default — that is the intended behavior.

---

### External Legal Override

Binding legal or regulatory obligations override all internal constitutional rules regardless
of level. GDPR, HIPAA, financial sector regulations, and contractual obligations with legal
effect are not subject to internal governance hierarchy. Removing documentation of a legal
obligation from the org constitution does not remove the obligation.

Organizations document binding obligations in `org_compliance` with a source field:

```markdown
data_residency:
  requirement: EU data must not leave EU infrastructure
  source: "GDPR Article 44 — binding"
  override_level: legal
```

---

### Precedence Stack

From highest to lowest authority:

```
1. Legal / Regulatory    — external, binding — overrides all internal rules
2. Org Safety            — non-negotiable safety rules at org level
3. Team Safety           — safety rules added at team level
4. Org Config            — configurable defaults from org level
5. Team Config           — configurable rules from team level (overrides org config)
6. Repo Config           — configurable rules from repo level (overrides team config)
```

---

### Examples

| Rule | Category | Org | Team | Repo | Resolution |
|------|----------|-----|------|------|------------|
| Never commit secrets | Safety | prohibited | no exceptions for tests | no exceptions for stubs | ✅ Higher wins |
| PR human review | Safety | required | also required for hotfixes | also required for payment PRs | ✅ Higher wins |
| Security review model | Safety | opus | — | sonnet ← | ❌ Repo cannot downgrade |
| Code generation model | Configurable | sonnet (default) | — | haiku (repo uses lightweight tasks) | ✅ Repo wins |
| snake_case naming | Safety (baseline) | snake_case | snake_case + module prefix | snake_case + domain prefix | ✅ Extensions valid |
| snake_case naming | Safety (baseline) | snake_case | — | camelCase ← | ❌ Contradicts org rule |
| Test coverage minimum | Configurable (floor) | 60% minimum | 70% minimum | 80% minimum | ✅ All raise floor |
| Test coverage minimum | Configurable (floor) | 60% minimum | 40% ← | — | ❌ Team cannot lower floor |
| Data residency | Legal | GDPR Article 44 | EU-only routing | — | ✅ Legal overrides all |

The test for safety rules: does the lower-level rule reduce the coverage or strength of a
higher-level rule? If yes, the rule is invalid. Return it to the higher level.

The test for configurable rules: does the lower-level rule contradict the higher-level rule,
or does it simply make it more specific to the project's context? Specificity is valid.

---

## Inheritance Syntax

CLAUDE.md files reference their parents using the `inherits_from` section:

```markdown
## inherits_from
- org: https://github.com/company/ai-governance/CLAUDE.org.md
- team: https://github.com/company/platform-team/CLAUDE.team.md

## override_rules
# Rules below EXTEND parent rules. You cannot WEAKEN parent rules.
# If you need an exception, submit a request to the parent level owner.

## local_rules
# Rules specific to this repository only.
```

For local setups (not URL-based), use relative paths:
```markdown
## inherits_from
- org: ~/.claude/CLAUDE.org.md
- team: ~/.claude/teams/platform/CLAUDE.team.md
```

---

## Validation

The governance sync step validates inheritance at session start:

1. Fetch parent CLAUDE.md files (or use cached version with TTL)
2. Parse rules at each level
3. Check that local rules do not contradict parent rules using these tests:
   - Does any local rule remove a requirement from a parent rule?
   - Does any local rule lower a threshold set by a parent rule?
   - Does any local rule grant permissions that parent rules prohibit?
4. Flag violations with specific guidance:

```
⚠️ Constitutional inheritance violation detected:

Your CLAUDE.md contains:
  "Pre-commit checks are optional for hotfix branches"

This weakens org rule:
  "All commits require pre-commit hook validation (CLAUDE.org.md, line 23)"

Options:
  1. Remove the local rule and follow the org standard
  2. Request an exception via the org governance PR process
  3. If the org rule is wrong, propose a change to CLAUDE.org.md

Local rule will not be enforced until conflict is resolved.
```

---

## Ownership Model

**Organization level**: owned by Engineering Leadership or Platform Team. Changes via RFC
process — proposed change, discussion period, vote or designated approver, merge.
Cadence: quarterly review cycle. Emergency changes require security lead and CTO sign-off.

**Team level**: owned by Tech Lead. Changes via team PR review — at least one other team
member reviews. Cadence: monthly review as part of retrospective.

**Repo level**: owned by project developers. Changes via standard PR review.
Cadence: any time a project decision warrants documentation. Monthly cleanup.

No level can change the rules of the level above it. A repo developer cannot modify the team
constitution. A tech lead cannot modify the org constitution. This is structural, not cultural.

---

## Implementation Levels

**Level 1: Manual inheritance** — Copy the org and team templates into each repo's CLAUDE.md.
Manually check for contradictions. Self-discipline only. No automation.
Appropriate for: small teams, early stage governance, trust-based culture.

**Level 2: Automated validation** — The `/health-check` command fetches parent constitutions
and checks for contradictions at session start. Violations are flagged but not blocked.
Appropriate for: teams with >5 developers, projects with security requirements.

**Level 3: CI/CD enforcement** — A GitHub Actions workflow blocks PRs that would violate the
parent constitution. No merge without inheritance compliance.
Appropriate for: enterprise environments, regulated industries, compliance requirements.

---

## File Locations

**Recommended structure for enterprise:**

```
company/ai-governance/              # Org governance repo
├── CLAUDE.org.md                   # Org-level constitution
├── CLAUDE.team.template.md         # Template for team constitutions
└── policies/
    ├── security-constitution.md
    └── compliance-requirements.md

~/.claude/                          # Developer machine (applied to all repos)
├── CLAUDE.md                       # Personal preferences (optional layer)
└── teams/
    └── platform/CLAUDE.team.md    # Team constitution (if not repo-based)

each-project/
├── CLAUDE.md                       # Repo-level constitution
└── .claude/
    └── commands/                   # Project-specific slash commands
```

---

## Related

- [templates/CLAUDE.org.md](../templates/CLAUDE.org.md) — organization-level constitution template
- [templates/CLAUDE.team.md](../templates/CLAUDE.team.md) — team-level constitution template
- [patterns/constitutional-inheritance.md](../patterns/constitutional-inheritance.md) — implementation pattern
- [patterns/break-glass.md](../patterns/break-glass.md) — temporary override for governance emergencies
- [docs/adr/ADR-004-hybrid-inheritance-model.md](adr/ADR-004-hybrid-inheritance-model.md) — decision record for hybrid model
- [docs/architecture.md](architecture.md) — Layer 1 (Constitution) in the 7-layer stack
