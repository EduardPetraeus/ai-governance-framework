# ARCHITECTURE.md

<!-- CUSTOMIZE: Replace all placeholder content with your actual architecture.
     This file is read by agents at session start. Keep it accurate and current.
     An inaccurate ARCHITECTURE.md is worse than none — agents will make wrong assumptions. -->

project_name: "[Your Project Name]"
last_updated: "YYYY-MM-DD (Session NNN)"
status: "Draft | Stable | Under revision"

---

## System Overview

<!-- CUSTOMIZE: Write one paragraph describing what this system does, who uses it,
     and what the key design goals are (performance, reliability, simplicity, etc.). -->

[One paragraph describing the system. Example: "HealthReporting is a personal health data
pipeline that ingests data from wearable devices via their respective APIs, transforms it
into a unified schema, and serves it through a read-only dashboard. The system prioritizes
data freshness (daily ingestion) and local development speed (DuckDB for local runs,
Databricks for production)."]

### Architecture Diagram

<!-- CUSTOMIZE: Replace with an ASCII diagram of your actual architecture.
     Keep it simple enough to read in a terminal. No external tools required. -->

```
┌──────────────────────────────────────────────────────────────────┐
│                        External Systems                          │
│   [Source API 1]    [Source API 2]    [Source API 3]            │
└───────────┬─────────────────┬─────────────────┬─────────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Ingestion Layer                            │
│              src/connectors/  (one file per source)             │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Storage Layer                              │
│   Bronze (raw)    →    Silver (cleaned)    →    Gold (agg)      │
│   data/bronze/         data/silver/             data/gold/       │
└───────────────────────────────┬──────────────────────────────────┘
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
     The "Why" and "ADR" columns are critical — agents use them to avoid
     re-opening settled decisions. -->

| Component | Technology | Why | ADR |
|-----------|-----------|-----|-----|
| Primary language | Python 3.11 | Team expertise, strong data ecosystem | — |
| Local database | DuckDB | Zero-config, fast analytics, SQL-compatible | [ADR-001](docs/adr/ADR-001.md) |
| Cloud database | [Your choice] | [Your reasoning] | [ADR link] |
| Task orchestration | [Airflow / Prefect / cron / GitHub Actions] | [Your reasoning] | [ADR link] |
| Testing | pytest | Standard Python testing, good fixture support | — |
| Linting | ruff | Fast, replaces flake8 + isort + pep8 | — |
| Type checking | mypy | Catches type errors before runtime | — |
| Secrets management | environment variables + .env (local) | Simple, universal, no vendor lock-in | — |
| CI/CD | GitHub Actions | Integrated with repository, free tier sufficient | — |

---

## Layer and Component Structure

<!-- CUSTOMIZE: Describe your actual directory/module structure.
     Agents use this to know where to put new files. -->

```
project-root/
├── src/
│   ├── connectors/          # One file per external data source
│   │   ├── base_connector.py   # Abstract base class all connectors inherit
│   │   └── [source_name].py    # e.g., stripe.py, salesforce.py
│   ├── transforms/          # Data transformation logic
│   │   └── [entity_name].sql   # One file per entity
│   ├── models/              # Data models and schemas
│   └── utils/               # Shared utilities (logging, config, http)
├── tests/
│   ├── unit/                # Pure function tests, no I/O
│   ├── integration/         # Tests that hit real APIs or databases
│   └── fixtures/            # Shared test data factories
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── runbooks/            # Operational procedures
├── scripts/                 # Utility scripts (not application code)
└── data/                    # Local development data (gitignored)
    ├── bronze/
    ├── silver/
    └── gold/
```

---

## Data Flow

<!-- CUSTOMIZE: Describe how data moves through your system.
     Be specific enough that an agent can understand which component
     is responsible for each step. -->

1. **Ingestion:** Connectors in `src/connectors/` fetch data from external APIs on a schedule.
   Each connector is responsible for one source. Connectors write raw data to the bronze layer.

2. **Transformation:** SQL transforms in `src/transforms/` read from bronze and write to silver.
   Transforms are idempotent — running them twice produces the same result.

3. **Aggregation:** Gold layer views aggregate silver data for dashboards and reports.
   Gold is read-only (views, not materialized tables) in local development.

4. **Serving:** [Describe how downstream consumers access the data.]

**Idempotency rule:** All pipeline stages must be safely re-runnable. Use MERGE INTO, not INSERT.

---

## Integration Points

<!-- CUSTOMIZE: List all external systems this project integrates with.
     Agents need to know this to avoid introducing unplanned dependencies. -->

| System | Direction | Protocol | Auth Method | Notes |
|--------|----------|---------|------------|-------|
| [API Name] | Inbound | REST/HTTPS | API key (env var) | Rate limit: 1000 req/day |
| [Database] | Bidirectional | SQL | Service account | Read/write prod, read-only staging |
| [Notification service] | Outbound | Webhook | HMAC signature | Events defined in docs/events.md |

**Rule:** Adding a new integration requires an entry in this table. Do not add external
dependencies without updating this file.

---

## Security Boundaries

<!-- CUSTOMIZE: Describe which components have access to what.
     This is critical for agents to understand what is and isn't allowed. -->

| Component | Can Access | Cannot Access |
|-----------|-----------|--------------|
| Connectors | External APIs (read only), bronze layer (write) | Silver, gold, production databases |
| Transforms | Bronze (read), silver (read/write) | External APIs, gold (write) |
| Dashboard | Gold (read only) | All other layers |
| Tests | All layers (test databases only) | Production systems |

**Data classification:**

- `RESTRICTED`: PII, credentials, health records — never in AI context, never in logs
- `INTERNAL`: Business logic, schema definitions — allowed in AI context
- `PUBLIC`: Open source dependencies, public API specs — unrestricted

---

## Known Constraints and Trade-offs

<!-- CUSTOMIZE: Document the constraints your architecture works within
     and the trade-offs you have consciously made. This prevents agents
     from "fixing" things that were intentional design choices. -->

| Constraint | Impact | Decision |
|-----------|--------|---------|
| DuckDB is not concurrent | Only one writer at a time | Sequential pipeline stages, no parallel writes |
| [Source API] rate limit: 1000/day | Cannot backfill more than 6 months in one run | Backfill runs in 7-day chunks |
| No ORM | SQL must be written by hand | More control, less magic, see transforms/README.md for patterns |

**Intentional simplicity choices:**
- No message queue (would add operational complexity with no clear benefit at current scale)
- No caching layer (data freshness is more important than read performance for this use case)
- No microservices (single repository, single deployment unit until scale demands otherwise)

<!-- CUSTOMIZE: Document your intentional simplicity choices so agents don't
     "improve" things that were deliberately kept simple. -->

---

## ADR Index

<!-- This table is maintained automatically by agents when new ADRs are added. -->

| ADR | Date | Status | Title |
|-----|------|--------|-------|
| [ADR-001](docs/adr/ADR-001.md) | YYYY-MM-DD | Accepted | [Title] |
| [ADR-002](docs/adr/ADR-002.md) | YYYY-MM-DD | Accepted | [Title] |

**Rule:** Agents may not contradict an Accepted ADR without explicit human approval.
To propose changing an accepted decision, create a new ADR that supersedes the old one.
