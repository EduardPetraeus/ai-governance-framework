# DECISIONS.md

A permanent log of significant decisions made during this project. The purpose is to
prevent re-litigating closed questions. When an agent or team member asks "why did we
do X?", the answer should be in this file.

**What belongs here:** Architectural decisions, technology choices, process decisions,
tradeoffs consciously accepted. Not tactical decisions (what function name to use).

**What does NOT belong here:** Every micro-decision from every session. Only decisions
that, if reversed, would require meaningful rework.

**Rule for agents:** Do not propose reversing a decision marked "Accepted" without first
flagging it: "This would reverse Decision [N] ([title]). Should I write an updated decision
first?" Then wait for human approval.

---

## DEC-002 — 2025-03-10

**Date:** 2025-03-10
**Decided by:** Engineering Lead + AI Agent (Sonnet session)
**Review date:** 2025-09-10 (if international expansion is on the roadmap)

### Context

Payment integration was needed for Phase 2. Three providers were evaluated: Stripe,
Paddle, and Braintree. The decision needed to be made before building the connector.

### Decision

Use Stripe as the payment provider.

### Rationale

- Best-in-class Python SDK with type stubs (fits our typed Python approach)
- Webhook reliability is higher than alternatives based on team's prior experience
- Stripe's Dashboard is the best for support team to handle customer disputes
- Stripe Radar provides fraud detection with no additional configuration
- Team has existing Stripe experience — no learning curve

### Consequences

- All payment flows use Stripe APIs (checkout, subscriptions, invoices, refunds)
- The `src/connectors/stripe.py` connector is the integration point
- Stripe's webhook format is what the notification system is built around
- If we expand to markets where Stripe is not supported (some SEA markets), this decision
  needs revisiting

### Alternatives considered

- **Paddle:** Better EU VAT handling, but weaker Python SDK and less team experience
- **Braintree:** Good enterprise features, but adding Braintree means also managing PayPal
  relationship, which adds complexity

**Status: Accepted**

---

## DEC-001 — 2025-03-01

**Date:** 2025-03-01
**Decided by:** Engineering Lead
**Review date:** 2025-09-01 (reassess if data volume or team size changes significantly)

### Context

The project needs a database for two purposes: (1) analytical queries on pipeline data,
and (2) application state for the web service. These have very different characteristics:
analytical queries are read-heavy, batch, and benefit from columnar storage; application
queries are transactional, concurrent, and need ACID guarantees.

### Decision

Use DuckDB for the data pipeline (analytical layer) and PostgreSQL for application state.
They serve different purposes and are not interchangeable.

### Rationale

- DuckDB: zero-config setup for local development, extremely fast for analytical queries,
  SQL-compatible (easy to port to cloud when needed), no concurrent write requirements
  in the pipeline
- PostgreSQL: battle-tested for transactional workloads, strong ecosystem (pg extensions,
  monitoring tools), team expertise, runs locally via Docker
- Separating them avoids the "one database to rule them all" trap — each tool is used
  where it's strongest

### Consequences

- SQL written for the pipeline must be DuckDB-compatible locally and [cloud DB]-compatible
  in production. Test both when writing transforms.
- No ORM for analytics (DuckDB doesn't have good ORM support). Raw SQL only.
- PostgreSQL via SQLAlchemy Core (not ORM) for application state.
- Local development uses Docker Compose to run PostgreSQL.
- DuckDB database file is gitignored (`data/` directory).

### Alternatives considered

- **Single PostgreSQL for everything:** Simpler, but PostgreSQL is not designed for the
  analytical query patterns in the pipeline. Performance would be a problem.
- **SQLite for local development:** Would have worked, but DuckDB's analytical performance
  is materially better for the pipeline use case, and it's more similar to the cloud target.

**Status: Accepted**

---

<!-- New decisions are added above this line -->
<!-- Template for new decisions:

## DEC-NNN — YYYY-MM-DD

**Date:** YYYY-MM-DD
**Decided by:** [Person or "AI Agent session NNN"]
**Review date:** YYYY-MM-DD

### Context

[1-2 sentences: what problem or question prompted this decision?]

### Decision

[One clear sentence: what was decided?]

### Rationale

[Why? List the reasons. Be specific — vague rationale is not useful 6 months later.]

### Consequences

[What changes as a result? What constraints does this create?]

### Alternatives considered

[What was rejected and why?]

**Status: Accepted | Superseded by DEC-NNN | Deprecated**

-->
