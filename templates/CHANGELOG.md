# CHANGELOG.md

This is a session-level changelog, not a release changelog. Each entry records what
happened in one working session with an AI agent: what was built, what decisions were made,
what was discovered, and what the agent recommends for next time.

**Purpose for agents:** This file is your memory. Read the last 10 entries at session start
to understand recent history before proposing work.

**Update cadence:** One entry per session, added automatically at session end via /end-session
or the on_session_end protocol in CLAUDE.md.

**Format:** Entries are newest-first. Session number is monotonically increasing.

---

## Session 002 — 2025-03-15 [claude-sonnet-4-6]

### Tasks completed
- Implemented `src/connectors/stripe.py`: Stripe webhook event connector
  - Subscribes to payment.succeeded, payment.failed, subscription.* events
  - Writes raw events to `data/bronze/stripe_events/`
  - Rate limiting handled via exponential backoff
- Updated `src/connectors/base_connector.py`: Added `validate_schema()` method to base class
  - All connectors must now validate response schema before writing
  - Prevents silent schema drift from upstream API changes
- Added `tests/integration/test_stripe_connector.py`: 8 integration tests
  - Tests cover: auth failure, rate limit, schema validation, happy path
  - All 8 tests passing
- Updated `docs/adr/ADR-002.md`: Documented Stripe as the payment provider

### Decisions made
- **Stripe selected as payment provider** (ADR-002): Evaluated Stripe vs. Paddle vs. Braintree.
  Stripe chosen for: best Python SDK, best webhook reliability, team familiarity. Paddle
  would be better for EU VAT handling if we expand internationally — revisit at Phase 3.
- **Schema validation is now mandatory in base class**: Any connector that skips it will raise
  `SchemaValidationRequired` at runtime. Not optional.

### Discovered tasks (added to PROJECT_PLAN.md)
- Add webhook signature verification for Stripe (security, Medium priority)
- Document the bronze layer schema for Stripe events (docs, Low priority)

### Metrics
- Tasks completed: 4
- Files changed: 5 (3 new, 2 modified)
- Tests added: 8
- Cost estimate: ~$0.08 (code generation + review, Sonnet)

### Next session
- **Recommended model:** claude-sonnet-4-6 (standard feature work continues)
- **Top 3 tasks:**
  1. Build notification system for payment events (Phase 2, unblocked now)
  2. Add webhook signature verification (discovered this session, security)
  3. Write user-facing API endpoints for subscription management

---

## Session 001 — 2025-03-01 [claude-sonnet-4-6]

### Tasks completed
- Created project structure: `src/`, `tests/`, `docs/`, `scripts/`, `data/`
- Configured Python tooling: `pyproject.toml` with ruff, mypy, pytest
  - Ruff replacing flake8 + isort (faster, single config)
  - Mypy strict mode enabled
- Implemented `src/connectors/base_connector.py`: Abstract base class
  - `fetch()` method required by all connectors
  - Built-in retry logic with exponential backoff
  - Structured logging with request ID propagation
- Set up local development environment: `docker-compose.yml`
  - PostgreSQL 15 for local development
  - Volume-mounted for persistence between sessions
- Added `CLAUDE.md`, `PROJECT_PLAN.md`, `ARCHITECTURE.md` from framework templates
  - Customized project_context section
  - Added domain-specific naming conventions for API layer

### Decisions made
- **DuckDB for local analytics, PostgreSQL for application data**: Different use cases.
  DuckDB is for the data pipeline (batch, analytical queries). PostgreSQL is for the
  application (transactional, concurrent). See ADR-001.
- **No ORM**: SQLAlchemy Core (not ORM) for database access. Raw SQL for analytics.
  Rationale: more control, easier to reason about queries, no magic.

### Discovered tasks (added to PROJECT_PLAN.md)
- Set up pre-commit hooks (gitleaks, ruff) — blocking for team onboarding
- Write CONTRIBUTING.md before inviting second developer

### Metrics
- Tasks completed: 5
- Files changed: 12 (11 new, 1 modified)
- Tests added: 0 (infrastructure session — tests come with features)
- Cost estimate: ~$0.12 (setup and architecture work, Sonnet)

### Next session
- **Recommended model:** claude-sonnet-4-6 (Phase 1 continues, standard feature work)
- **Top 3 tasks:**
  1. Implement authentication framework (Phase 1, unblocked)
  2. Set up pre-commit hooks (discovered, blocking for team)
  3. Define core data models: User, Organization, Subscription

---

<!-- New sessions are prepended above this line by the /end-session command -->
