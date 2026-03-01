# ADR-004: Hybrid Inheritance Model — Safety Rules Use Higher-Wins, Configurable Rules Use Specific-Wins

## Status

Accepted

## Date

2026-03-01

## Context

The constitutional inheritance model documented in `docs/constitutional-inheritance.md` established a single conflict resolution rule: higher level always wins. If an org-level rule and a repo-level rule conflict, the org wins. This model is correct and sufficient for safety and security rules — it is structurally impossible for a team to permit what the org prohibits.

Claude Code, the primary AI agent runtime governed by this framework, applies the inverse rule: more specific context wins. A `CLAUDE.md` file at the repo root takes precedence over a global `~/.claude/CLAUDE.md`. A section heading in a repo CLAUDE.md overrides the same heading in an inherited parent. This is Claude Code's documented behavior and it is correct for configurable preferences: the project knows its stack better than the org does.

These two rules are in direct conflict when applied universally:

- If the framework's "higher wins" applies to everything, Claude Code's runtime behavior contradicts the framework's intent for configurable settings. A repo's stack declaration is silently ignored in favor of the org's default.
- If Claude Code's "specific wins" applies to everything, a repo CLAUDE.md can silently override org-level security rules by declaring more specific rules that contradict them — the exact failure mode constitutional inheritance was designed to prevent.

Neither rule is wrong in isolation. Both rules are wrong when applied to the other category of rules.

A second conflict emerged from cross-organizational scenarios. An organization's internal hierarchy (org → team → repo) can conflict with external legal or regulatory requirements. GDPR data residency requirements, HIPAA data handling mandates, and financial sector regulatory obligations are not subject to internal governance hierarchy — they override all internal rules regardless of level. No internal constitution can legitimately permit what a binding legal instrument prohibits. The framework must accommodate external legal authority without requiring organizations to replicate every regulation in their org-level constitution.

## Decision

The framework adopts a hybrid inheritance model with two distinct resolution rules, applied based on rule category:

**Safety rules use higher-wins resolution.** A rule is classified as a safety rule if it prevents harm that cannot be corrected after the fact: data exposure, credential compromise, irreversible data loss, compliance violation, or deliberate security bypass. Safety rules at higher levels cannot be narrowed, weakened, or removed by lower levels. This applies regardless of Claude Code's specific-wins runtime behavior — governance documentation takes precedence over runtime defaults for safety categories.

**Configurable rules use specific-wins resolution.** A rule is classified as configurable if its purpose is workflow optimization, consistency, or preference expression — not harm prevention. Configurable rules at lower levels take precedence over higher-level defaults when the lower level specifies a more concrete value. This aligns with Claude Code's runtime behavior and allows teams and repos to express accurate context without fighting governance machinery.

**External legal obligations override all internal hierarchy.** When a binding legal or regulatory instrument (legislation, regulatory ruling, court order, contractual obligation with legal effect) conflicts with any internal constitutional rule at any level, the legal obligation prevails. Organizations document external obligations in their org-level constitution but the obligation's authority derives from the legal instrument, not from the org's documentation of it. Removing the org-level documentation does not remove the obligation.

The precedence stack for conflict resolution, from highest to lowest authority:

```
1. Legal / Regulatory (external, binding — overrides all internal rules)
2. Org Safety      (internal, non-negotiable safety rules)
3. Team Safety     (internal, safety rules added at team level)
4. Org Config      (internal, configurable defaults from org level)
5. Team Config     (internal, configurable rules from team level — overrides org config)
6. Repo Config     (internal, configurable rules from repo level — overrides team config)
```

Safety categories governed by higher-wins:
- The `never_commit` list and all items on it
- `security_review_model` and any model floor requirements
- `org_kill_switch` mandatory stop conditions
- `pre_commit_hooks: required`
- `pr_human_review: required`
- `constitutional_changes: pr_only`
- Compliance and audit trail requirements
- Data classification rules and PII handling
- Credential rotation timelines

Configurable categories governed by specific-wins:
- `model_routing` routing table entries (except security review model)
- Coding style, naming conventions extensions
- Session length and protocol customizations
- Agent selection beyond org-mandated minimum
- Workflow step additions and sequencing
- Test coverage thresholds (minimum floors set by org; teams and repos may raise them)
- Technology stack declarations
- Domain-specific rules

## Rationale

The dual-rule model resolves the Claude Code conflict without creating a governance loophole. Safety rules retain the protection that constitutional inheritance was designed to provide: no team can accidentally or deliberately weaken the org's security baseline. Configurable rules gain the specificity that makes governance useful rather than obstructive: a repo that uses a different tech stack than the org default can declare it accurately without submitting a PR to the org constitution.

The external legal override is not a new rule — legal obligations already override internal governance by operation of law. Documenting it explicitly in the framework serves three purposes: it prevents the framework from being cited as a reason to delay legal compliance ("our governance framework doesn't require this"), it gives organizations a documented process for surfacing new legal obligations (add to org constitution with source citation), and it establishes that the org constitution is not the highest authority in the framework — a common misconception when organizations first adopt constitutional inheritance.

The precedence stack (Legal → Org Safety → Team Safety → Org Config → Team Config → Repo Config) is explicit and deterministic. At any conflict point, the category of each rule and the level it originates from determines the winner. There is no ambiguity, no case-by-case judgment required, and no configuration parameter that adjusts the resolution logic.

## Consequences

### Positive

- The framework aligns with Claude Code's runtime behavior for configurable rules. Teams no longer experience conflicts between what the framework documents and what Claude Code actually does.
- Safety rules retain absolute protection. No configuration change at any lower level can weaken a safety rule defined at org or team level.
- External legal obligations are explicitly accommodated. Organizations operating under GDPR, HIPAA, SOC 2, or sector-specific regulations can reference binding requirements without embedding every regulation into their org constitution.
- The precedence stack is auditable. A compliance audit can determine rule resolution by inspection: classify the rule, identify its level, apply the stack.
- Teams gain the ability to express accurate technical context (stack, model routing, naming extensions) without friction, which increases constitution quality and reduces the temptation to work around governance.

### Negative

- Two resolution rules increase framework complexity. Contributors and teams must learn which category a rule falls into before they can predict resolution behavior.
- Classification disputes will occur. A team may argue that a rule the org classifies as safety is actually configurable. The framework provides the category lists in this ADR and in `docs/constitutional-inheritance.md`, but does not provide an automated classifier. Disputes require human judgment.
- The external legal override has no automated enforcement mechanism. The framework documents the principle, but verifying that a repo's constitution does not contradict applicable law requires a legal review, not a script.

### Neutral

- The `inherits_from_validator.py` script must be updated to apply category-aware conflict detection: safety-rule conflicts produce hard failures; configurable-rule conflicts at lower levels are resolved in favor of the lower level without flagging.
- Existing constitutions written under the single "higher wins" rule remain valid. The hybrid model is backwards compatible: all safety rules continue to behave as before, and configurable rules that were already consistent across levels are unaffected.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Single "higher wins" rule for all categories | Contradicts Claude Code runtime behavior for configurable settings. Creates friction where governance machinery fights accurate project context. |
| Single "specific wins" rule for all categories | Allows repos to silently override safety rules. Eliminates the primary value of constitutional inheritance. |
| Per-rule override flags in the constitution | High configuration surface area. Allows safety rules to be flagged as overridable, defeating the purpose of the category distinction. |
| Require all legal obligations to be in org constitution | Does not reduce the obligation; only creates documentation maintenance burden. A regulatory change requires updating every org constitution before the obligation takes effect — the wrong coupling. |
| Treat the conflict as a Claude Code issue and wait for a fix | Claude Code's specific-wins behavior is correct for its use case. The framework must accommodate runtime behavior, not the reverse. |

## Implementation Notes

The category lists in this ADR are canonical. When a new rule type is added to any framework template, it must be assigned to either the safety or configurable category before the template is merged. Assignment is documented in the template as an inline comment:

```markdown
# INHERITANCE: safety — higher-wins
pre_commit_hooks: required

# INHERITANCE: configurable — specific-wins
code_generation_model: sonnet
```

The `inherits_from_validator.py` script uses these inline comments when present. If no comment is present, the rule is treated as configurable (safe default: more permissive conflict resolution).

For the external legal override: organizations document binding obligations in `org_compliance` with a source field:

```markdown
## org_compliance
data_residency:
  requirement: EU data must not leave EU infrastructure
  source: "GDPR Article 44 — binding, overrides all internal routing config"
  override_level: legal
```

Rules with `override_level: legal` are treated as the highest precedence in the validator, above `override_level: org_safety` (the default for safety rules).

For cross-constitutional conflicts (two organizations' constitutions in conflict, e.g., a vendor's governance framework vs. a client's org constitution): the legal obligation takes precedence if one exists; otherwise, the more restrictive rule applies. This is the same resolution logic as safety rules. The break-glass mechanism documented in `patterns/break-glass.md` provides a time-limited override path for cases where the more restrictive rule creates an operational emergency.

## Related Decisions

- [ADR-001](ADR-001-constitutional-inheritance-url-references.md) — URL and local path resolution for parent constitutions
- [ADR-002](ADR-002-zero-external-dependencies-for-core-governance.md) — Standard library constraint for governance scripts
- [ADR-003](ADR-003-85-percent-confidence-ceiling.md) — Automation-bias defense pattern

## Related Documents

- [docs/constitutional-inheritance.md](../constitutional-inheritance.md) — Inheritance model specification (updated for hybrid model)
- [patterns/constitutional-inheritance.md](../../patterns/constitutional-inheritance.md) — Implementation pattern (updated for hybrid model)
- [patterns/break-glass.md](../../patterns/break-glass.md) — Temporary override mechanism for governance emergencies

## Review Date

2027-03-01
