# Architecture Decision Records (ADRs)

Architecture Decision Records are short documents that capture a significant architectural decision made during the project — including the context that motivated it, the decision itself, and the consequences of that decision.

ADRs matter especially in AI-assisted development because **agents cannot reopen closed decisions on their own**. Without ADRs, an agent working in a new session has no knowledge of decisions made in previous sessions. It will re-evaluate every architectural question it encounters and may reach different conclusions — or the same conclusions through redundant analysis. An agent that encounters an accepted ADR is explicitly instructed not to contradict it without human approval. The ADR system turns closed decisions into durable constraints on agent behavior, not just historical documentation.

**Numbering**: ADRs are numbered sequentially starting from ADR-001 (ADR-000 is this template). Never reuse a number, even if an ADR is deprecated. Deprecated ADRs remain in the archive.

**Naming**: `ADR-NNN-short-descriptive-title.md`. Use hyphens, lowercase, no special characters. Store in `docs/adr/`.

---

# ADR-NNN: [Decision Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-NNN]

## Date

YYYY-MM-DD

## Context

[What is the situation that requires a decision? What forces are at play? What constraints exist?

Be specific about the problem. "We needed a database" is not context. "We need a database that supports local development without network connectivity, can run on a developer's laptop without Docker, and produces SQL that is compatible with our Databricks production environment" is context.

Include: technical constraints, business constraints, team constraints, timeline constraints, and any relevant external factors (regulatory requirements, vendor limitations, etc.)]

## Decision

[What decision was made? State it clearly and concisely. One to three sentences.

"We will use X for Y" or "We will not use X because of Y" — declarative and specific.

Do not explain the rationale here. That belongs in the Rationale section.]

## Rationale

[Why was this decision made? What alternatives were considered and why were they rejected?

This is the most important section. The decision itself may be obvious from hindsight; the rationale is what prevents the decision from being re-opened unnecessarily.

Include:
- The key factors that made this the right decision given the constraints
- Why alternatives did not satisfy the constraints
- Any trade-offs that were consciously accepted]

## Consequences

### Positive

[What becomes easier or better because of this decision?

Be concrete: "Database queries can be developed and tested locally without network access" is better than "Improved developer experience."]

### Negative

[What becomes harder or worse? What trade-offs are accepted?

Be honest. An ADR that claims no negative consequences is not credible. Every architectural decision closes some doors while opening others.

Include future constraints this decision creates: "All SQL must be written to be DuckDB-compatible, which precludes the use of PostgreSQL-specific extensions."]

### Neutral

[What changes that is neither clearly good nor bad — just different? New conventions required, new processes introduced, new tooling needed.]

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| [Option A]  | [Reason — specific, not vague] |
| [Option B]  | [Reason — specific, not vague] |

## Implementation Notes

[Any specific technical notes for implementing this decision.

This section is optional but valuable for complex decisions. Include:
- Migration path if this changes existing behavior
- Specific configuration required
- Known edge cases to watch for
- Testing approach to verify the decision is correctly implemented]

## Review Date

[When should this decision be revisited? YYYY-MM-DD

Set a review date when:
- The decision was made under time pressure and may not be optimal
- External conditions (vendor pricing, library maturity, regulatory landscape) are expected to change
- The team expected to revisit once more information was available

Leave blank if the decision is considered stable and not subject to scheduled review.]
