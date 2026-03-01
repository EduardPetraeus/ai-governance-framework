# ADR-003: Automation-Bias Defense Pattern — Configurable Confidence Ceiling

## Status

Amended — 2026-03-01

Original decision (2026-02-28): ceiling hardcoded at 85%, non-configurable.

Amendment: ceiling is a configurable parameter (range: 80–95%, default: 85%). The rationale for non-configurability was based on a slippery-slope assumption that this framework's friction budget mechanism makes explicit and governable. See Amendment Rationale below.

## Date

2026-02-28 (original) / 2026-03-01 (amended)

## Context

Automation bias is a documented cognitive phenomenon: when an automated system produces a confident validation result, human reviewers reduce their own scrutiny in proportion to the stated confidence. A code review agent that reports 97% confidence causes human reviewers to allocate their attention to the remaining 3% — treating the agent's output as a baseline of correctness rather than a draft requiring verification.

This effect is compounded when multiple AI validation layers operate in sequence. Consider a pipeline where a code review agent (95% confident), a security agent (92% confident), and a QA agent (90% confident) all pass a pull request. A human reviewer, seeing three independent AI validations, may reason that the probability of an undetected issue is approximately (1 - 0.95) × (1 - 0.92) × (1 - 0.90) = 0.4% — effectively zero. This reasoning is mathematically incorrect because the agents are not independent. They share training data, exhibit correlated failure modes, may be the same base model with different system prompts, and their confidence scores are not calibrated probabilities. The actual residual risk is much higher than the compounded confidence math implies.

The framework's automation-bias-defense pattern was designed to address this. The pattern requires AI agents to structure their output not as "I found no issues (confidence: X%)" but as "I verified A, B, and C. I did not verify D, E, and F. Confidence capped at [ceiling]." The explicit enumeration of what was not verified forces the agent's report to surface gaps rather than hide them behind a high confidence number.

The ceiling value requires a design decision. The 85% default sits above the range where AI output is dismissed as low-quality (roughly below 75%) and below the range where human reviewers shift from active to passive engagement (roughly above 90%). These thresholds are based on documented patterns in automation bias research and practical observation.

However, 85% is a **design default**, not an empirically derived constant. No controlled study has established that 85% is the unique correct threshold for all domains, all team compositions, and all risk profiles. Different deployment contexts require different ceiling values:

- **Safety-critical systems** (medical devices, financial settlement, security tooling): a lower ceiling (80%) is appropriate. The cost of automation bias in these domains is high enough to warrant the additional review friction a lower ceiling creates.
- **Standard development** (product features, APIs, backend services): the 85-90% range preserves active human engagement without creating excessive review overhead.
- **Low-risk outputs** (documentation, minor UI copy, static configuration): a higher ceiling (90-95%) is appropriate. The risk of automation bias is lower, and the review friction of a low ceiling is disproportionate to the benefit.

The original decision to make the ceiling non-configurable was based on the argument that configurable ceilings drift upward: teams raise the ceiling incrementally until the automation bias protection disappears. This argument is valid in the absence of other governance controls. However, this framework provides a friction budget mechanism that makes ceiling changes explicit, audited, and budget-constrained. The slippery-slope risk is governable. Making the ceiling non-configurable to prevent drift is a one-size-fits-all constraint that contradicts the framework's risk-tier and maturity-level approach.

There is also a friction budget interaction that the original ADR did not account for. The ceiling directly determines review overhead: a lower ceiling produces more human scrutiny on each validation output (more friction consumed), and a higher ceiling reduces it. Teams cannot calibrate their friction budget correctly without also controlling their ceiling. Hardcoding the ceiling removes a variable teams need to balance the budget.

## Decision

The automation-bias-defense pattern uses a configurable confidence ceiling with a default of **85%** and a valid range of **80–95%**.

Configuration is per-project, set explicitly in `CLAUDE.md` or in the project's `governance-config.yaml`. The ceiling is not adjusted silently; every change is logged in `CHANGELOG.md` with a stated rationale.

**Guidance by domain:**

| Domain | Recommended ceiling | Rationale |
|--------|--------------------|------------------------------------|
| Safety-critical (medical, financial, security) | 80% | High automation-bias cost; additional friction justified |
| Standard development | 85–90% | Default range; balances scrutiny and review overhead |
| Low-risk (docs, minor UI, static config) | 90–95% | Lower bias risk; high ceiling avoids disproportionate friction |

The ceiling is enforced the same way regardless of its value: agents cap self-reported confidence at the configured value and must accompany any validation report with an explicit NOT VERIFIED section. The ceiling value does not change the structural requirement for gap enumeration.

Teams that want to raise the ceiling above 85% must document the rationale in `CHANGELOG.md` and review the change in the next governance retrospective. The friction budget document (`patterns/friction-budget.md`) governs whether the resulting reduction in review overhead is acceptable.

## Amendment Rationale

The original non-configurability decision rested on three claims:

1. **"A configurable ceiling will trend toward 100%."** True without constraints. Not true when the change requires a CHANGELOG entry, a retrospective review, and explicit friction-budget accounting. The drift risk is addressed through governance process, not through removing the configuration option.

2. **"The value matters less than the non-negotiability."** This is a governance opinion, not a derived principle. The same logic would justify hardcoding blast radius limits, session lengths, and every other parameter the framework exposes as configurable. The framework explicitly allows these to vary by team and maturity level. The ceiling should be consistent with that approach.

3. **"85% is not arbitrary."** Correct. It is a reasonable design default. It is not an empirical constant. The ADR previously claimed it "sits above the range where AI output is dismissed" and "below the range where reviewers shift to passive" — these thresholds are observed heuristics, not measurement-derived boundaries. Presenting them as facts and then using them to justify non-configurability overstated the evidence.

The amendment preserves the core protection (explicit gap enumeration + ceiling below the automation-bias activation range) while making the ceiling a governed parameter rather than a hardcoded constant.

## Consequences

### Positive

- Teams can align the ceiling to their actual risk profile. Safety-critical teams get more scrutiny; low-risk teams avoid disproportionate friction.
- The ceiling interacts correctly with the friction budget. Teams calibrate both together, producing consistent review overhead within their defined budget.
- The framework's configurable-by-default approach is consistent across all parameters. No special case for this one value.
- Projects with empirical evidence of low defect escape rates can express appropriate trust without forking the framework.

### Negative

- Ceiling drift remains a risk. Teams must discipline their governance retrospective to review ceiling changes. The governance process — not a hardcoded value — is the protection.
- Cross-project consistency is reduced. A team reading a validation report from another project may encounter a different ceiling value. The `confidence capped at [N]%` language in every report makes this explicit.
- Configuration adds a parameter to the governance setup. Teams must consciously choose a ceiling rather than inheriting a universal default. Most teams will leave the default unchanged; the configuration option exists for teams that need to diverge.

### Neutral

- All AI validation output still uses consistent structural language: "Verified: [list]. Not verified: [list]. Confidence capped at [ceiling]% per automation-bias-defense policy." The ceiling value varies; the structure does not.
- The ceiling applies only in validation contexts — when an AI agent is producing a pass/fail or confidence-scored assessment of code, security, or compliance. It does not apply to generative tasks (writing code, drafting documentation) where confidence is not a meaningful output.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Non-configurable ceiling at 85% (original decision) | Contradicts the framework's risk-tier approach; removes a friction budget variable; overstates the empirical basis for 85%; drift risk is governable through process. |
| No confidence ceiling; surface all findings and let humans decide | Does not address the accumulation problem. Multiple AI agents all reporting findings-complete status triggers compounded-probability reasoning even without explicit confidence scores. |
| 70% ceiling | Produces output that human reviewers classify as low-quality AI validation. Teams disable the pattern or route around it. |
| 90% ceiling (universal) | Insufficient separation from "AI probably got this right" in standard development contexts. As a domain-specific option for low-risk outputs, 90-95% is appropriate. |
| Dynamic ceiling based on task type, auto-computed | Adds configuration complexity that removes team visibility. Explicit per-project configuration with governance logging is preferable to automatic computation. |

## Implementation Notes

The ceiling is configured in `CLAUDE.md` under the `confidence_ceiling` key:

```markdown
## confidence_ceiling

ceiling: 85
range: 80-95
domain: standard-development

# To change: update ceiling, add rationale to CHANGELOG.md, review at next retrospective.
```

If `confidence_ceiling` is absent from `CLAUDE.md`, the default of 85 applies.

The agent definition templates in `agents/` include a system prompt instruction that caps self-reported confidence at the configured ceiling. The command definitions in `commands/` include a post-processing instruction that strips any confidence value above the configured ceiling from structured output before it is written to a pull request comment or CI log.

The automation script `automation/governance_dashboard.py` reads the configured ceiling from `CLAUDE.md` (defaulting to 85 if absent) and validates that agent output in CI logs does not exceed it.

## Cross-References

- [patterns/automation-bias-defense.md](../../patterns/automation-bias-defense.md) — implementation pattern for this decision
- [patterns/friction-budget.md](../../patterns/friction-budget.md) — ceiling interacts with friction budget calibration

## Review Date

2027-03-01
