# ARCHITECTURE.md

<!-- CUSTOMIZE: Replace all placeholder content with your actual architecture.
     This file is read by agents at every session start. Keep it accurate.
     An inaccurate ARCHITECTURE.md is worse than none -- agents will make
     wrong assumptions and build code that conflicts with reality.
     Update this file whenever the architecture changes. -->

**Project:** [Your Project Name]
**Last updated:** YYYY-MM-DD (Session NNN)
**Status:** Draft | Stable | Under revision

---

## System Overview

<!-- CUSTOMIZE: Write one paragraph describing what this system does, who uses it,
     and what the primary design goals are. Be specific -- agents use this to
     make decisions about patterns, trade-offs, and scope. -->

[One paragraph. Example: "HealthReporting is a personal health data pipeline that
ingests data from wearable device APIs, transforms it into a unified schema using
the medallion pattern (bronze/silver/gold), and serves it through a read-only
dashboard. Design priorities: data freshness (daily ingestion), local development
speed (DuckDB for local, Databricks for production), and correctness (idempotent
pipelines, schema validation on ingestion)."]

### Architecture Diagram

<!-- CUSTOMIZE: Replace with an ASCII diagram of your actual architecture.
     ASCII diagrams work in terminals, PRs, and AI context windows.
     Keep it simple enough to understand in 10 seconds. -->

```
┌──────────────────────────────────────────────────────────────────┐
│                        External Systems                          │
│   [Source API 1]    [Source API 2]    [Source API 3]              │
└────────┬──────────────────┬──────────────────┬───────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Ingestion Layer                            │
│              src/connectors/ (one file per source)               │
│              All connectors inherit BaseConnector                │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Storage Layer                              │
│   Bronze (raw)    →    Silver (cleaned)    →    Gold (agg)       │
│   data/bronze/         data/silver/             data/gold/       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                           │
│                   Dashboard / API / Reports                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technology Decisions

<!-- CUSTOMIZE: Fill in each component with your actual technology choices.
     The "Why" column is critical -- agents use it to understand the reasoning
     and avoid suggesting alternatives to decided questions.
     The "ADR" column links to the full decision record.
     If no ADR exists for a decision, leave the cell as "—" (not blank). -->

| Component | Technology | Version | Why | ADR |
|-----------|-----------|---------|-----|-----|
| Primary language | Python | 3.11 | Team expertise, strong data ecosystem, pinned for platform compatibility | -- |
| Local database | DuckDB | 1.1+ | Zero-config, fast analytics, SQL-compatible with cloud target | ADR-001 |
| Cloud database | [Your choice] | [Version] | [Your reasoning] | [ADR link] |
| Task orchestration | [Airflow / Prefect / cron / GitHub Actions] | [Version] | [Your reasoning] | [ADR link] |
| Testing | pytest | 8.x | Standard Python testing, good fixture support, rich plugin ecosystem | -- |
| Linting | ruff | 0.8+ | Fast, replaces flake8 + isort + pycodestyle in one tool | -- |
| Type checking | mypy | 1.x | Catches type errors before runtime, strict mode enabled | -- |
| Secrets management | Environment variables + .env (local) | -- | Simple, universal, no vendor lock-in | -- |
| CI/CD | GitHub Actions | -- | Integrated with repository, sufficient free tier | -- |
| Secret scanning | gitleaks | 8.x | Detects secrets in commits before they reach remote | -- |

---

## Component Structure

<!-- CUSTOMIZE: Describe your actual directory and module structure.
     Agents use this to know where to put new files. A new connector goes
     in src/connectors/. A new test goes in tests/unit/. If this is wrong,
     agents create files in the wrong places. -->

```
project-root/
├── src/
│   ├── connectors/            # One file per external data source
│   │   ├── base_connector.py  # Abstract base class: auth, retry, rate limit, schema validation
│   │   ├── stripe.py          # Example: Stripe payment connector
│   │   └── [source_name].py   # New connectors follow this pattern
│   ├── transforms/            # Data transformation logic
│   │   └── [entity_name].sql  # One SQL file per entity, MERGE INTO pattern
│   ├── models/                # Data models, schemas, type definitions
│   ├── services/              # Business logic, orchestration
│   └── utils/                 # Shared utilities: logging, config, http client
├── tests/
│   ├── unit/                  # Pure function tests, no I/O, no network
│   ├── integration/           # Tests that hit real APIs or databases
│   └── fixtures/              # Shared test data factories (not static files)
├── docs/
│   ├── adr/                   # Architecture Decision Records (ADR-001.md, etc.)
│   └── runbooks/              # Operational procedures for production
├── scripts/                   # Utility scripts (not application code)
└── data/                      # Local development data (gitignored)
    ├── bronze/                # Raw ingested data
    ├── silver/                # Cleaned and normalized data
    └── gold/                  # Aggregated views
```

**File placement rules (agents must follow):**
- New data source → `src/connectors/[source_name].py` inheriting `BaseConnector`
- New SQL transform → `src/transforms/[entity_name].sql`
- New test → `tests/unit/test_[module_name].py` or `tests/integration/test_[module_name].py`
- New ADR → `docs/adr/ADR-[NNN].md`
- Utility functions → `src/utils/` (not scattered across modules)

---

## Data Flow

<!-- CUSTOMIZE: Describe how data moves through your system.
     Be specific enough that an agent can understand which component
     handles each step. Number the steps for clarity. -->

1. **Ingestion:** Connectors in `src/connectors/` fetch data from external APIs on a schedule (daily). Each connector handles one source. Connectors write raw API responses to the bronze layer without transformation.

2. **Transformation:** SQL transforms in `src/transforms/` read from bronze and write to silver. Transforms clean, type, normalize, and deduplicate. All transforms use `MERGE INTO` for idempotency -- running twice produces the same result.

3. **Aggregation:** Gold layer views aggregate silver data for dashboards and reports. Gold is read-only views in local development, materialized tables in production.

4. **Serving:** [Describe how downstream consumers access the data: API, dashboard, exports.]

**Idempotency rule:** All pipeline stages must be safely re-runnable. Use `MERGE INTO`, never `INSERT INTO`. This is non-negotiable.

---

## Integration Points

<!-- CUSTOMIZE: List every external system this project connects to.
     Agents need this to avoid introducing unplanned dependencies.
     A new integration requires an entry in this table BEFORE implementation. -->

| System | Direction | Protocol | Auth Method | Rate Limit | Notes |
|--------|----------|---------|-------------|-----------|-------|
| [API Name] | Inbound | REST/HTTPS | API key (env var) | 1000 req/day | Pagination via cursor token |
| [Database] | Bidirectional | SQL | Service account | -- | Read/write prod, read-only staging |
| [Notification service] | Outbound | Webhook | HMAC signature | -- | Events defined in docs/events.md |

**Rule:** Adding a new integration requires an entry in this table and an update to this file. Do not add external dependencies without documenting them here.

---

## Security Boundaries

<!-- CUSTOMIZE: Define which components can access what. This is critical
     for agents -- without these boundaries, an agent writing a connector
     might directly access the gold layer or production database. -->

| Component | Can Access | Cannot Access |
|-----------|-----------|--------------|
| Connectors | External APIs (read), bronze layer (write) | Silver, gold, production databases |
| Transforms | Bronze (read), silver (read/write) | External APIs, gold (direct write) |
| Gold views | Silver (read) | All other layers, external systems |
| Tests | All layers (test databases only) | Production systems, real external APIs |

**Data classification:**
- `RESTRICTED`: PII, credentials, health records, financial data -- never in AI context, never in logs, never in test data
- `INTERNAL`: Business logic, schema definitions, proprietary algorithms -- allowed in AI context with care
- `PUBLIC`: Open source code, public API specs, documentation -- unrestricted

---

## Known Constraints and Trade-offs

<!-- CUSTOMIZE: Document the constraints your architecture works within and
     the trade-offs you have consciously made. This prevents agents from
     "fixing" things that were deliberate design choices. -->

| Constraint | Impact | Deliberate Decision |
|-----------|--------|---------------------|
| DuckDB does not support concurrent writers | Sequential pipeline stages, no parallel writes | Acceptable for batch pipeline, revisit if moving to streaming |
| [Source API] rate limit: 1000 req/day | Cannot backfill more than N days in one run | Backfill in daily chunks, queued by date |
| No ORM | SQL written by hand for all data operations | More control, less magic, see transforms/ for patterns |

**Intentional simplicity choices:**

These are things deliberately kept simple. Agents must not add complexity here without explicit human approval and an ADR.

- No message queue (operational complexity exceeds benefit at current scale)
- No caching layer (data freshness matters more than read performance)
- No microservices (single repository, single deployment unit until scale demands otherwise)
- No ORM (raw SQL gives full control over query behavior)

<!-- CUSTOMIZE: Add your own intentional simplicity choices here.
     The purpose is to prevent agents from "improving" things that
     were deliberately kept simple. -->

---

## ADR Index

<!-- Maintained by agents when new ADRs are added. -->

| ADR | Date | Status | Title |
|-----|------|--------|-------|
| ADR-001 | YYYY-MM-DD | Accepted | [Title of decision] |
| ADR-002 | YYYY-MM-DD | Accepted | [Title of decision] |

**Rule:** Agents may not contradict an Accepted ADR without explicit human approval. To change a decided question, create a new ADR that supersedes the existing one.
