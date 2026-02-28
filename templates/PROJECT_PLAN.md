# PROJECT_PLAN.md

<!-- CUSTOMIZE: Replace the header values with your project details.
     Agents read this file at every session start to understand what to work on.
     An inaccurate project plan causes agents to work on the wrong things. -->

**Project:** [Your Project Name]
**Current phase:** Phase 1 -- Foundation
**Sprint goal:** Set up core infrastructure so all components can build against a stable base
**Sprint dates:** YYYY-MM-DD to YYYY-MM-DD
**Last updated:** YYYY-MM-DD (Session NNN)

---

## Phase Overview

<!-- CUSTOMIZE: Replace phase names and descriptions with your actual phases.
     KEEP: The status indicators and table structure -- agents parse these
     to understand project state and prevent out-of-phase work. -->

| Phase | Name | Status | Goal |
|-------|------|--------|------|
| 1 | Foundation | In Progress | Core infrastructure, data models, base patterns, CI/CD |
| 2 | Core Features | Planned | Primary features, integrations, API layer |
| 3 | Production | Planned | Hardening, monitoring, deployment automation, documentation |

**Status key:** Complete | In Progress | Planned | Blocked

---

## Phase 1: Foundation

**Goal:** Core infrastructure ready. Features can be built without fighting the environment.
**Success criteria:** Project runs locally. CI/CD is green. Base patterns are established and documented.

<!-- CUSTOMIZE: Replace these tasks with your actual Phase 1 work.
     KEEP: The table columns -- agents use them for status tracking and estimation.
     Tasks should be scoped to a single session. If a task takes more than one
     session, decompose it into smaller tasks. -->

| Task | Area | Estimated | Depends On | Status | Notes |
|------|------|-----------|------------|--------|-------|
| Set up project structure and tooling | Infrastructure | 1 session | -- | Complete | Python 3.11, ruff, mypy, pytest configured |
| Define core data models | Data | 1 session | Project structure | In Progress | User and Organization done, Product pending |
| Implement base connector class | Architecture | 1 session | Data models | Planned | Abstract class with auth, retry, rate limiting |
| Configure local development environment | Infrastructure | 30 min | Base connector | Planned | Docker Compose for database + cache |
| Set up CI/CD pipeline | Infrastructure | 1 session | Local environment | Planned | GitHub Actions: lint, test, security scan on PR |

**Phase 1 progress:** 1/5 tasks complete (20%)

---

## Phase 2: Core Features

**Goal:** Primary user-facing functionality is complete and tested.
**Success criteria:** Users can complete the core workflow end-to-end in staging.

<!-- CUSTOMIZE: Replace with your actual Phase 2 tasks.
     These tasks should not be started until Phase 1 success criteria are met. -->

| Task | Area | Estimated | Depends On | Status | Notes |
|------|------|-----------|------------|--------|-------|
| Build REST API layer for resource management | API | 2 sessions | Phase 1 complete | Planned | OpenAPI spec, versioned endpoints |
| Implement data ingestion pipeline | Data | 1 session | API layer | Planned | Batch processing, idempotent writes |
| Build notification system | Features | 1 session | API layer | Planned | Email + in-app, event-driven |
| Integrate payment provider | Integration | 1 session | API layer | Planned | ADR required before starting |

**Phase 2 progress:** 0/4 tasks complete (0%)

---

## Phase 3: Production

**Goal:** System is reliable, monitored, and deployable without manual intervention.
**Success criteria:** Zero-downtime deployments. Alerts fire before users notice problems. Runbook covers all operational scenarios.

<!-- CUSTOMIZE: Replace with your actual Phase 3 tasks. -->

| Task | Area | Estimated | Depends On | Status | Notes |
|------|------|-----------|------------|--------|-------|
| Add observability: logging, tracing, metrics | Infrastructure | 1 session | Phase 2 complete | Planned | OpenTelemetry, structured logging |
| Performance testing and optimization | Performance | 1 session | Observability | Planned | Target: p95 < 200ms for all endpoints |
| Security hardening and review | Security | 1 session | Performance | Planned | Opus session for review, external pen test |
| Production deployment runbook | Documentation | 30 min | All above | Planned | Step-by-step in docs/runbooks/ |

**Phase 3 progress:** 0/4 tasks complete (0%)

---

## Discovered Tasks

<!-- This section is populated by agents during sessions.
     When an agent encounters work that was not in the original plan, it
     adds the task here instead of doing it immediately.
     WHY: This prevents scope creep while preserving the discovery.
     Review this section during sprint planning to decide what to promote. -->

Tasks found during sessions that were not originally planned:

| Task | Discovered In | Priority | Added to Sprint? |
|------|--------------|----------|-----------------|
| Add request ID propagation through all service calls | Session 003 | High | No |
| Validate YAML config on startup to catch misconfiguration early | Session 003 | Medium | No |
| Document database migration strategy before Phase 2 | Session 004 | High | No |

<!-- CUSTOMIZE: Clear this table when starting your project.
     Agents will populate it during sessions. -->

---

## Blocked Tasks

<!-- Tasks that cannot proceed due to external dependencies or open decisions.
     Agents check this section to avoid starting blocked work. -->

| Task | Blocked By | Since | Resolution Path |
|------|-----------|-------|-----------------|
| Payment integration | ADR for payment provider not written | YYYY-MM-DD | Write ADR in next session |

---

## Architecture Decisions Needed

<!-- Decisions that must be made before certain tasks can begin.
     Link to DECISIONS.md when resolved. -->

- [ ] Payment provider selection (blocks Phase 2 payment integration)
- [ ] Message queue technology for notifications (Kafka vs. SQS vs. Redis Pub/Sub)
- [ ] Caching strategy for expensive external API calls

---

## Sprint History

<!-- This table is populated automatically as sprints complete.
     Agents and developers use it for velocity estimation:
     if the last 3 sprints completed 4 tasks/sprint, do not commit 8. -->

| Sprint | Dates | Goal | Committed | Completed | Velocity (tasks/session) |
|--------|-------|------|-----------|-----------|--------------------------|
| 1 | YYYY-MM-DD to YYYY-MM-DD | Foundation setup | 5 | 1 | 0.5 |

<!-- CUSTOMIZE: Clear this table when starting your project.
     Sprint data will accumulate as you complete sprints. -->
