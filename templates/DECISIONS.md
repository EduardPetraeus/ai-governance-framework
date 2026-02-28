# DECISIONS.md

A permanent log of significant decisions made during this project. Each entry documents the context, the decision, the reasoning, and the consequences. The purpose is to prevent re-litigating closed questions.

**What belongs here:** Architectural decisions, technology choices, process changes, deliberate trade-offs. Decisions that, if reversed, would require meaningful rework or coordination.

**What does NOT belong here:** Every micro-decision from every session. Not "which variable name to use." Only decisions that shape the project's direction.

**Rule for agents:** Do not propose reversing a decision with status "Decided" without first flagging it to the user: "This would reverse Decision DEC-[N] ([title]). Should I write an updated decision record first?" Then wait for human approval. Never silently contradict a decided question.

**Format:** Each decision uses the template below. Entries are newest-first.

---

## DEC-003 -- Connector Base Class Pattern -- 2025-03-15

**Status:** Decided
**Decided by:** Engineering Lead + AI Agent (Session 005)
**Context:** The project has 8 data source connectors. The first 3 were built independently with different patterns for authentication, retry logic, and error handling. This inconsistency made the codebase harder to understand and maintain. A standardized pattern was needed.
**Decision:** All connectors must inherit from `BaseConnector` in `src/connectors/base_connector.py`. The base class handles auth setup, retry with exponential backoff, rate limiting, and schema validation. Individual connectors implement only `fetch_data()`.
**Rationale:** Centralizing cross-cutting concerns in the base class means bug fixes and improvements apply to all connectors at once. The existing 3 connectors were refactored to use the base class, confirming the pattern works for different API styles (REST, webhook, OAuth). The alternative -- documenting a pattern and hoping each connector follows it -- had already failed.
**Consequences:**
- New connectors are faster to build (~30 minutes vs. ~2 hours) because auth, retry, and validation are handled
- Changes to retry logic require running all connector tests (`pytest tests/integration/`)
- The base class is a critical path component -- changes must be reviewed carefully
- Connectors that need non-standard auth (e.g., OAuth with refresh) extend the base class method rather than bypassing it
**Review date:** 2025-09-15 (reassess if connector count exceeds 15 or a fundamentally different API pattern is encountered)

---

## DEC-002 -- Stripe as Payment Provider -- 2025-03-10

**Status:** Decided
**Decided by:** Engineering Lead + AI Agent (Session 003)
**Context:** Payment integration was required for Phase 2. Three providers were evaluated: Stripe, Paddle, and Braintree. The decision needed to be made before building the payment connector to avoid rework.
**Decision:** Use Stripe as the payment provider for all payment flows: checkout, subscriptions, invoices, refunds.
**Rationale:**
- Best-in-class Python SDK with type stubs (fits the typed Python approach established in DEC-001)
- Webhook reliability is higher than alternatives based on team's prior production experience
- Stripe Dashboard is the best for support team to handle disputes without engineering involvement
- Stripe Radar provides fraud detection without additional configuration or vendor
- Team has existing Stripe experience -- zero onboarding time
**Consequences:**
- All payment flows are built on Stripe APIs exclusively
- `src/connectors/stripe.py` is the integration point, following the BaseConnector pattern (DEC-003)
- The notification system is built around Stripe's webhook event format
- If expanding to markets where Stripe is not available (some Southeast Asian markets), this decision needs revisiting
- Stripe's pricing (2.9% + $0.30 per transaction) is accepted as the cost of reliability and developer experience
**Alternatives considered:**
- **Paddle:** Better EU VAT handling (handles tax compliance entirely). Weaker Python SDK. Less team experience. Would be the better choice if international tax compliance becomes a primary concern.
- **Braintree:** Strong enterprise features and PayPal integration. But adopting Braintree means also managing the PayPal relationship, which adds operational complexity disproportionate to the benefit.
**Review date:** 2025-09-10 (if international expansion is on the roadmap by this date)

---

## DEC-001 -- Dual Database Strategy -- 2025-03-01

**Status:** Decided
**Decided by:** Engineering Lead
**Context:** The project needs a database for two distinct purposes: (1) analytical queries on pipeline data -- read-heavy, batch-oriented, benefits from columnar storage; (2) application state for the web service -- transactional, concurrent, requires ACID guarantees. Using one database for both creates performance and design compromises.
**Decision:** Use DuckDB for the data pipeline (analytical layer) and PostgreSQL for application state (transactional layer). They serve different purposes and are not interchangeable.
**Rationale:**
- **DuckDB for analytics:** Zero-config local setup (no Docker, no server process). Extremely fast for analytical queries on columnar data. SQL-compatible with the cloud target (Databricks/Spark SQL). No concurrent write requirements in the batch pipeline.
- **PostgreSQL for application state:** Battle-tested for transactional workloads. Strong ecosystem: pgAdmin, pg_stat, extensions. Team expertise. Runs locally via Docker Compose with persistence.
- **Separation principle:** Each tool is used where it is strongest. The "one database for everything" approach was explicitly rejected because analytical queries on PostgreSQL would require either denormalization (adding maintenance burden) or poor query performance.
**Consequences:**
- SQL written for the pipeline must be compatible with both DuckDB (local) and the cloud target (production). Test both when writing transforms.
- No ORM for analytics -- DuckDB lacks mature ORM support. Raw SQL only for the pipeline.
- PostgreSQL uses SQLAlchemy Core (not ORM) for application state -- explicit queries, no implicit magic.
- Local development requires Docker Compose for PostgreSQL but not for DuckDB.
- The `data/` directory (DuckDB files) is gitignored.
**Alternatives considered:**
- **Single PostgreSQL:** Simpler operationally, but not designed for the analytical query patterns in the pipeline. Performance would degrade as data volume grows. Would require materialized views or denormalization to compensate.
- **SQLite for local development:** Lightweight, but DuckDB's analytical performance is materially better for pipeline workloads, and DuckDB's SQL dialect is closer to the cloud target than SQLite's.
**Review date:** 2025-09-01 (reassess if data volume exceeds 10M rows or team size exceeds 3)

---

<!-- Template for new decisions:

## DEC-NNN -- [Short Title] -- YYYY-MM-DD

**Status:** Open | Decided | Superseded by DEC-NNN | Deprecated
**Decided by:** [Person or "AI Agent session NNN"]
**Context:** [1-2 sentences: what problem or question prompted this decision?]
**Decision:** [One clear, unambiguous sentence: what was decided?]
**Rationale:** [Why this option? Be specific -- vague rationale is useless 6 months later.]
**Consequences:** [What changes as a result? What constraints does this create? What becomes harder?]
**Alternatives considered:** [What was rejected and why? Be fair to the alternatives.]
**Review date:** [YYYY-MM-DD -- when should this decision be revisited?]

-->
