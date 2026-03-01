# Pattern: Friction Budget

## Problem

Governance mechanisms accumulate. A team starts with a session protocol (reasonable), adds
pre-commit hooks (reasonable), adds mandatory reporting (reasonable), adds approval gates
(reasonable), and then wonders why developers are routing around the entire system.

Each mechanism was individually justified. The aggregate is fatal. Nobody measured the total.

Governance without a budget is governance that grows until it collapses.

## Solution

Define an explicit friction budget per session — the maximum total overhead the governance
system can impose before developers begin to bypass it. Track the cost of each mechanism.
When adding a new mechanism, either reduce an existing one or accept that the budget is spent
and no new mechanisms can be added.

The budget is a forcing function: it requires every governance mechanism to justify its
existence in terms of cost vs. value. Mechanisms that cost more than they contribute get removed.

## When to Use

- When designing a governance system from scratch (design to the budget from day one)
- When developers are reporting that governance is slowing them down
- When adoption rates for governed workflows are declining
- When adding a new governance mechanism (first check available budget)
- When conducting the monthly governance health review

## When NOT to Use

- Level 1 projects where fewer than three governance mechanisms exist (not enough to create friction problems)
- Projects where governance has not yet been adopted (establish governance first, then apply a budget)
- Solo developers with no "adoption rate" to measure (use personal judgment to keep it lightweight)

## Budget Definition

### Default Session Budget

```
┌─────────────────────────────────────────────────────────────┐
│ FRICTION BUDGET — Per Developer Session                      │
├──────────────────────────────┬──────────────────────────────┤
│ Mechanism                    │ Max Friction Cost            │
├──────────────────────────────┼──────────────────────────────┤
│ Invisible (automatic)        │ Unlimited — zero developer   │
│                              │ attention required           │
├──────────────────────────────┼──────────────────────────────┤
│ Acceptable (one command)     │ 4 total per session          │
│                              │ (2 start + 2 end at most)   │
├──────────────────────────────┼──────────────────────────────┤
│ Manual input required        │ 1 per session maximum        │
│                              │ (scope confirmation)         │
├──────────────────────────────┼──────────────────────────────┤
│ Waiting for external gate    │ 0 during active work         │
│                              │ (CI runs async)              │
├──────────────────────────────┼──────────────────────────────┤
│ TOTAL visible overhead       │ < 5 minutes per session      │
│ BUDGET EXCEEDED if           │ > 15 minutes per session     │
└─────────────────────────────────────────────────────────────┘
```

### Friction Classification

Classify every governance mechanism into one category:

**Class 0: Invisible** — runs automatically with zero developer involvement.
Examples: CI/CD gates, automatic changelog updates, background security scans.
Budget cost: zero. Add freely.

**Class 1: Passive** — visible to the developer but requires no action.
Examples: governance sync output at session start, automatic task reporting shown after tasks.
Budget cost: 10-20 seconds. Add with care; limits on the total that can be displayed without
becoming noise.

**Class 2: Active** — requires the developer to type or click.
Examples: `/plan-session`, `/end-session`, scope confirmation.
Budget cost: 30-90 seconds each. Maximum 4 per session total.

**Class 3: Blocking** — developer must wait or complete a form before proceeding.
Examples: mandatory fields, approval queues, manual review gates.
Budget cost: 2-10 minutes. Maximum 1 per session. Eliminate if possible.

**Class 4: External** — requires action outside the developer's current tool.
Examples: filing a ticket, notifying a different team, getting written approval.
Budget cost: 5-30 minutes. Eliminate entirely from routine sessions. Reserve for exceptional cases.

## Implementation

### Step 1: Audit Existing Friction

For every current governance mechanism, classify it and measure its cost:

```markdown
| Mechanism                  | Class | Cost (seconds) | Value delivered         |
|----------------------------|-------|---------------|------------------------|
| /plan-session command      | 2     | 30            | Context orientation     |
| Governance sync output     | 1     | 15 read time  | Drift detection         |
| Scope confirmation         | 2     | 45            | Scope alignment         |
| Task reporting (automatic) | 1     | 5 read time   | Visibility              |
| Security scan (CI)         | 0     | 0             | Secret prevention       |
| /end-session command       | 2     | 60            | State persistence       |
| CHANGELOG update (auto)    | 0     | 0             | Audit trail             |
| PR approval gate           | 3     | varies        | Quality gate            |
| TOTAL CLASS 2              | —     | 135 seconds   | Session structure       |
| TOTAL CLASS 3              | —     | varies        | Review quality          |
```

### Step 2: Identify Overbudget Mechanisms

If any of the following are true, the system is overbudget:
- Total Class 2 actions exceed 4 per session
- Any Class 3 mechanism exists without measurable value
- Any Class 4 mechanism is required for routine sessions
- Total visible overhead exceeds 5 minutes in developer surveys

### Step 3: Reduce Before Adding

When proposing a new governance mechanism:
1. Classify it (what class?)
2. Measure its cost (how much friction?)
3. Check the budget (is there capacity in that class?)
4. If no capacity: what existing mechanism does this replace or reduce?
5. Document the budget update in the governance changelog

### Step 4: Measure Outcomes

After any friction change, measure:
- Developer survey: "Does the framework make you faster or slower?"
- Shadow AI indicators: ungoverned tool usage patterns
- Compliance rate: what percentage of sessions follow the full protocol?
- Session overhead: time from start to first productive output

## Escape Hatches

Every governance mechanism at Class 2 or above needs an escape hatch: a way for a developer
to bypass the mechanism when they have a legitimate reason.

The escape hatch must:
1. Be available (not require manager approval to use)
2. Be logged (every use creates a visible audit entry)
3. Have a named reason field (logged, not enforced)

Example in CLAUDE.md:
```markdown
## governance_bypass
If the session protocol cannot be followed in full (emergency fix, time-critical hotfix):
Use --skip-governance flag. This session will be logged as an unstructured session
in CHANGELOG.md. The bypass reason will be recorded. Review at next retrospective.
```

This converts shadow AI (invisible) into a logged exception (visible and governable).

## Example: Adding a New Mechanism

A team wants to add mandatory blast radius reporting before every session (report how many
files the session is expected to touch).

Budget check:
- Classification: Class 2 (developer must acknowledge before proceeding)
- Cost: ~20 seconds
- Current Class 2 budget used: 3 of 4 (start command, scope confirmation, end command)
- Available capacity: 1 Class 2 slot remains. This mechanism fits.

Implementation:
- Add to session start: automatic blast radius estimate (Class 1, not 2) based on PROJECT_PLAN.md
- If estimated >20 files: trigger explicit confirmation (Class 2 only when threshold exceeded)
- Result: zero cost for normal sessions; confirmation only when needed

This is the correct design: default invisible, escalate only on exception.

## Confidence Ceiling Interaction

The confidence ceiling (see [ADR-003](../docs/adr/ADR-003-85-percent-confidence-ceiling.md) and [patterns/automation-bias-defense.md](automation-bias-defense.md)) directly affects how much friction AI validation consumes from the budget.

### Effective Friction Formula

```
effective_friction = base_friction + (1 - ceiling) × review_overhead
```

Where:
- `base_friction` — friction from governance mechanisms excluding validation review
- `ceiling` — the configured confidence ceiling (expressed as a decimal: 0.85, 0.80, etc.)
- `review_overhead` — time in seconds a developer spends on human review per validation output

**Example:** Base friction = 120 seconds. Review overhead = 300 seconds per validation. Ceiling = 0.85.

```
effective_friction = 120 + (1 - 0.85) × 300 = 120 + 45 = 165 seconds
```

If the team lowers the ceiling to 0.80 (more scrutiny required):

```
effective_friction = 120 + (1 - 0.80) × 300 = 120 + 60 = 180 seconds
```

If the team raises the ceiling to 0.90 (less scrutiny required):

```
effective_friction = 120 + (1 - 0.90) × 300 = 120 + 30 = 150 seconds
```

### Calibration Rule

**Teams must calibrate the ceiling and the friction budget together.** The ceiling is not a free variable — every change to it moves effective friction.

Before changing the confidence ceiling:
1. Calculate current effective friction
2. Calculate effective friction at the proposed ceiling
3. Verify the result is within budget (< 5 minutes total visible overhead)
4. If the ceiling change pushes the budget over limit, reduce another mechanism first
5. Document the calibration in `CHANGELOG.md`

**Ceiling and budget trade-offs by domain:**

| Domain | Ceiling | Review overhead | Budget impact |
|--------|---------|----------------|---------------|
| Safety-critical | 80% | High — more scrutiny required | Consume more budget; may require removing other Class 2/3 mechanisms |
| Standard | 85% (default) | Moderate | Balanced default; works within standard budget |
| Low-risk | 90–95% | Low — less scrutiny needed | Frees budget for additional governance mechanisms |

This means a team that lowers the ceiling for safety reasons must acknowledge the corresponding friction cost and either accept a tighter budget or remove an equivalent mechanism elsewhere. A team that raises the ceiling to reduce friction must document the rationale and verify the governance retrospective approves it.

## Related Patterns

- [docs/governance-fatigue.md](../docs/governance-fatigue.md) — the principle behind this pattern
- [patterns/blast-radius-control.md](blast-radius-control.md) — specific blast radius limits
- [patterns/progressive-trust.md](progressive-trust.md) — adapting friction to experience level
- [patterns/automation-bias-defense.md](automation-bias-defense.md) — confidence ceiling configuration
- [docs/maturity-model.md](../docs/maturity-model.md) — friction scales with maturity level
