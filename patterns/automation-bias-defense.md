# Pattern: Automation Bias Defense

## Problem

AI governance adds validation layers. Each layer was justified. Each layer adds an approval
signal. The human reviewer sees multiple approvals and reduces their own scrutiny. The
developer stops practicing independent verification because "the AI catches it."

The governance system has made the code less safe, not more. Automation bias is the mechanism.
The defense requires intentional design against an incentive that the governance system itself
creates.

## Solution

Enforce explicit uncertainty surfacing from every AI validation agent. Cap overall confidence
at 85%. Maintain developer judgment through periodic unassisted sessions. Track human review
quality as a proxy metric for automation bias. Label categories that AI cannot verify as
requiring mandatory human judgment.

## When to Use

- Level 4+: when multiple AI validation agents are active
- Any project where human review time is measurably declining after AI validation was introduced
- Regulated environments where audit requirements mandate genuine human review
- Teams that have experienced the "LGTM without reading" phenomenon

## When NOT to Use

- Level 1-2 projects where AI validation has not yet been introduced (implement validation first)
- Projects where developers are already actively rejecting AI suggestions and maintaining independent review
- Solo developers who have no team dynamic creating social proof pressure

## Implementation

### Step 1: Explicit Uncertainty in Agent Output

Every quality gate, code review, and security review agent must output both what it verified
and what it did not. Template:

```markdown
## Review Results

### VERIFIED
- Naming conventions: [result]
- Secret patterns: [result]
- Test presence: [result]
- Import structure: [result]

### NOT VERIFIED — requires human judgment
- Business logic correctness
- Performance under load
- Correctness of domain-specific calculations
- Whether requirements were interpreted correctly

### Confidence: [N]% (capped at 85%)
AI review is complete. Items in NOT VERIFIED require human sign-off before merge.
```

Add to agent prompt:
```
Always include an explicit NOT VERIFIED section.
Never claim to have verified business logic, domain correctness, or requirement interpretation.
End every review with the confidence ceiling reminder.
```

### Step 2: Confidence Ceiling in CLAUDE.md

```markdown
## confidence_ceiling

Maximum overall confidence from AI validation: 85%
This ceiling applies regardless of how many agents approved.

When reporting review results:
- State confidence as: [N]% of mechanically verifiable properties
- State explicitly: "AI validation does not cover [specific categories]"
- Never imply that AI approval = no human review needed
```

### Step 3: Mandatory Human Judgment Labels

Define the categories that AI cannot approve. These categories require human sign-off
regardless of AI review results:

```markdown
## human_judgment_categories

These require human sign-off even when all AI checks pass:
- business_logic: Is the algorithm doing the right thing for this domain?
- requirements: Did we build what was actually asked for?
- ux_decisions: Does this interaction design serve the user?
- data_model: Are these the right abstractions for this domain?
- performance_tradeoffs: Is this optimization worth its complexity cost?
```

### Step 4: Periodic Unassisted Sessions

Add to governance cadence (track in project documentation):

```markdown
## unassisted_review_cadence

Monthly: run one complete session without invoking any AI review agents.
Human reviews all code directly.

Purpose:
- Maintain independent verification skill
- Detect skill atrophy from disuse
- Establish baseline for measuring AI review value

Record unassisted review results in CHANGELOG.md.
If unassisted review finds significant issues that AI review missed:
→ review agent configuration needs improvement
→ consider rotating deep review more frequently
```

### Step 5: Review Quality Tracking

Track in COST_LOG.md or CHANGELOG.md:

```markdown
| Date | PR | AI review time | Human review time | Issues found by human |
|------|----|---------------|-------------------|----------------------|
| [date] | [PR] | [N] min | [N] min | [count] |
```

Alert threshold: if human review time drops more than 40% after AI validation introduction,
flag for team discussion. If average human review time drops below 2 minutes for substantial
PRs, automation bias is likely active.

## Anti-Patterns

**Removing the NOT VERIFIED section** — "it makes the output longer." The length is necessary.
The human needs to know what was not checked. Removing the section creates the false impression
of complete verification.

**Raising the confidence ceiling** — "85% seems too conservative, our agent is better than that."
The 85% ceiling is not about this specific agent's accuracy. It is about the categories of
correctness that AI systems structurally cannot verify (business logic, requirement
interpretation). These categories are not covered regardless of model capability.

**Skipping unassisted sessions because the AI is doing well** — the unassisted session is most
valuable when AI governance is working. That is when skill atrophy is silently accumulating.
The session reveals what the human can still catch independently.

## Example

**Without automation bias defense:**
```
✅ All checks passed. Ready to merge.
```

**With automation bias defense:**
```
Review complete.

VERIFIED:
✅ No secrets or PII detected
✅ Naming conventions: compliant
✅ Test coverage: 74% (above threshold)
✅ Architecture: consistent with ADR-003

NOT VERIFIED — requires human judgment:
⚠️ Business logic: monthly calculation in calculate_billing() not verified
⚠️ Data model: new PurchaseEvent entity — correct abstraction for this domain?
⚠️ Performance: no load testing in scope

Confidence: 72% (capped at 85% — AI validation is never complete)

Your review should focus on the NOT VERIFIED items above.
The VERIFIED items have been checked; the NOT VERIFIED items have not.
```

The human now knows exactly where to focus. They cannot assume the AI covered everything.

## Related Patterns

- [docs/automation-bias.md](../docs/automation-bias.md) — full specification and theory
- [docs/adversarial-audit.md](../docs/adversarial-audit.md) — testing governance effectiveness
- [patterns/human-in-the-loop.md](human-in-the-loop.md) — defining human checkpoints
- [docs/quality-control-patterns.md](../docs/quality-control-patterns.md) — quality control stack
