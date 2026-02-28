# CHANGELOG.md

This is a **session-level changelog**, not a release changelog. Each entry records what happened in one working session with an AI agent: what was built, what decisions were made, what was discovered, and what the agent recommends for next time.

**Why this exists:** This file is the agent's memory. Without it, every session starts from scratch. With it, the agent arrives knowing what was built yesterday, what decisions were made last week, and what is planned for today. This is not documentation for humans -- it is an instruction set for agents.

**How to use it:**
- Agents: Read the last 10 entries at session start to understand recent history.
- Agents: Append one entry at session end via the `on_session_end` protocol.
- Humans: Scan this file to answer "what did we build this week?" without reading code.

**Format rules:**
- Entries are newest-first (most recent session at the top).
- Session numbers are monotonically increasing.
- Every entry must include: tasks completed, decisions made, discovered tasks, metrics, and next-session recommendation.

---

## Session 002 -- 2025-03-15 [claude-sonnet-4-6]

### Scope confirmed
Build Stripe payment connector and write integration tests. Update base connector with schema validation.

### Completed tasks
- **Stripe connector** (`src/connectors/stripe.py`): Webhook event connector subscribing to `payment.succeeded`, `payment.failed`, `subscription.*` events. Writes raw events to `data/bronze/stripe_events/`. Rate limiting via exponential backoff. -- Advances Phase 2: payment integration unblocked.
- **Schema validation in base class** (`src/connectors/base_connector.py`): Added `validate_schema()` method. All connectors must validate API response schema before writing to bronze. Prevents silent schema drift from upstream API changes. -- Improves architectural consistency across all connectors.
- **Integration tests** (`tests/integration/test_stripe_connector.py`): 8 tests covering auth failure, rate limit handling, schema validation, webhook signature verification, and happy path. All 8 passing. -- Phase 2 test coverage +8 tests.
- **ADR-002** (`docs/adr/ADR-002.md`): Documented Stripe as payment provider. Evaluated Stripe vs. Paddle vs. Braintree. Stripe chosen for SDK quality, webhook reliability, and team familiarity. -- Closes open decision, blocks removed.

### Decisions made
- **Stripe as payment provider** (ADR-002): Best Python SDK, most reliable webhooks, team has existing experience. Paddle would be better for EU VAT if expanding internationally -- revisit at Phase 3.
- **Schema validation is mandatory in BaseConnector**: Runtime enforcement. Any connector that skips validation raises `SchemaValidationRequired`. Not optional.

### Discovered tasks (added to PROJECT_PLAN.md)
- Add webhook signature verification middleware (Security, Medium priority)
- Document bronze layer schema for Stripe events (Documentation, Low priority)

### Metrics
- Tasks completed: 4
- Files changed: 5 (3 created, 2 modified)
- Tests added: 8
- Estimated cost: ~$0.08 (Sonnet, code generation + review)

### Next session
- **Recommended model:** claude-sonnet-4-6 (standard feature work)
- **Top 3 tasks:**
  1. Build notification event system for payment events (Phase 2, unblocked)
  2. Add webhook signature verification (discovered this session, security)
  3. Write API endpoints for subscription management (Phase 2)

---

## Session 001 -- 2025-03-01 [claude-sonnet-4-6]

### Scope confirmed
Set up project structure, configure tooling, implement base connector class, establish governance files.

### Completed tasks
- **Project structure** (multiple files): Created `src/`, `tests/`, `docs/`, `scripts/`, `data/` directories with `__init__.py` files and `.gitkeep` where needed. -- Foundation for all future work.
- **Python tooling** (`pyproject.toml`): Configured ruff (replacing flake8 + isort), mypy in strict mode, pytest with coverage reporting. -- Enforces code quality from day one.
- **Base connector** (`src/connectors/base_connector.py`): Abstract base class with `fetch_data()` interface, built-in retry with exponential backoff, structured logging with request ID propagation, rate limit handling. -- All future connectors inherit this pattern.
- **Local environment** (`docker-compose.yml`): PostgreSQL 15 with volume mount for persistence between sessions. Health check configured. -- Developers can run the project locally in one command.
- **Governance files** (`CLAUDE.md`, `PROJECT_PLAN.md`, `ARCHITECTURE.md`): Copied from framework templates, customized `project_context`, added domain-specific naming conventions for data layers. -- Governance active from session 1.

### Decisions made
- **DuckDB for analytics, PostgreSQL for application state** (ADR-001): Different tools for different jobs. DuckDB for batch analytical queries in the data pipeline. PostgreSQL for transactional application state. No ORM -- SQLAlchemy Core for PostgreSQL, raw SQL for DuckDB.
- **No ORM for analytics**: Raw SQL gives full control. DuckDB does not have mature ORM support. Team prefers explicit queries over implicit magic.

### Discovered tasks (added to PROJECT_PLAN.md)
- Set up pre-commit hooks for gitleaks and ruff (blocking for team onboarding)
- Write CONTRIBUTING.md before second developer joins

### Metrics
- Tasks completed: 5
- Files changed: 14 (12 created, 2 modified)
- Tests added: 0 (infrastructure session -- tests come with features)
- Estimated cost: ~$0.12 (Sonnet, setup-heavy session with more context reading)

### Next session
- **Recommended model:** claude-sonnet-4-6 (Phase 1 continues, standard feature work)
- **Top 3 tasks:**
  1. Implement authentication framework (Phase 1, unblocked)
  2. Set up pre-commit hooks (discovered, blocking for team)
  3. Define core data models: User, Organization, Subscription

---

<!-- New sessions are prepended above this line by the on_session_end protocol. -->
