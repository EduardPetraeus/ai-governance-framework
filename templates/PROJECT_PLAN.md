# PROJECT_PLAN.md

<!-- CUSTOMIZE: Replace with your project name and details -->
project_name: "[Your Project Name]"
current_phase: Phase 1 — Foundation
sprint_goal: "Set up core infrastructure so all team members can build against a stable base"
sprint_dates: "YYYY-MM-DD to YYYY-MM-DD"
last_updated: "YYYY-MM-DD (Session NNN)"

---

## Phase Overview

<!-- CUSTOMIZE: Replace phase names and descriptions with your actual phases.
     Keep the status indicators — agents use them to understand project state. -->

| Phase | Name | Status | Goal |
|-------|------|--------|------|
| 1 | Foundation | 🔵 In Progress | Core infrastructure, data models, authentication |
| 2 | Core Features | ⬜ Planned | Primary user-facing features, integrations |
| 3 | Production | ⬜ Planned | Hardening, monitoring, deployment automation |

**Status legend:** ✅ Complete | 🔵 In Progress | ⬜ Planned | ❌ Blocked

---

## Phase 1: Foundation

**Goal:** Core infrastructure ready. Team can build features without fighting the environment.
**Success criteria:** All developers can run the project locally. CI/CD is green. Core data models exist.

<!-- CUSTOMIZE: Replace these tasks with your actual Phase 1 tasks.
     Keep the table structure — agents read it to understand task status. -->

| Task | Area | Estimated | Depends On | Status | Notes |
|------|------|-----------|------------|--------|-------|
| Set up project structure and tooling | Infrastructure | 1 session | Nothing | ✅ Complete | Python 3.11, ruff, mypy configured |
| Define and implement core data models | Data | 1 session | Project structure | 🔵 In Progress | User and Organization entities done, Product pending |
| Configure local development environment | Infrastructure | 30 min | Data models | ⬜ Planned | Docker Compose for Postgres + Redis |
| Implement authentication framework | Security | 1 session | Data models | ⬜ Planned | JWT-based, refresh token rotation |
| Set up CI/CD pipeline | Infrastructure | 1 session | Auth framework | ⬜ Planned | GitHub Actions, run tests on PR |

**Phase 1 progress:** 1/5 tasks complete (20%)

---

## Phase 2: Core Features

**Goal:** Primary user-facing functionality is complete and tested.
**Success criteria:** Users can complete the core workflow end-to-end in staging.

<!-- CUSTOMIZE: Replace with your actual Phase 2 tasks. -->

| Task | Area | Estimated | Depends On | Status | Notes |
|------|------|-----------|------------|--------|-------|
| Build API layer for resource management | API | 2 sessions | Phase 1 complete | ⬜ Planned | REST, OpenAPI spec |
| Implement data ingestion pipeline | Data | 1 session | API layer | ⬜ Planned | Batch + streaming |
| Build user notification system | Features | 1 session | API layer | ⬜ Planned | Email + in-app |
| Integrate third-party payment provider | Integration | 1 session | API layer | ⬜ Planned | ADR required before starting |

**Phase 2 progress:** 0/4 tasks complete (0%)

---

## Phase 3: Production

**Goal:** System is reliable, monitored, and deployable without manual intervention.
**Success criteria:** Zero-downtime deployments. Alerts fire before users notice problems.

<!-- CUSTOMIZE: Replace with your actual Phase 3 tasks. -->

| Task | Area | Estimated | Depends On | Status | Notes |
|------|------|-----------|------------|--------|-------|
| Add observability (logging, tracing, metrics) | Infrastructure | 1 session | Phase 2 complete | ⬜ Planned | OpenTelemetry |
| Performance testing and optimization | Performance | 1 session | Observability | ⬜ Planned | Target: p95 < 200ms |
| Security hardening and penetration test | Security | 1 session | Performance | ⬜ Planned | External review required |
| Production deployment runbook | Documentation | 30 min | All above | ⬜ Planned | Runbook in docs/runbooks/ |
| On-call setup and escalation policies | Operations | 30 min | Observability | ⬜ Planned | PagerDuty integration |

**Phase 3 progress:** 0/5 tasks complete (0%)

---

## Discovered Tasks

<!-- This section is auto-populated by agents during sessions.
     Tasks found during work that weren't in the original plan go here.
     Review this section at sprint planning to decide whether to add them to a phase. -->

Tasks found during sessions that were not originally planned:

| Task | Discovered In | Priority | Added To Sprint? |
|------|--------------|----------|-----------------|
| Validate YAML config on startup to catch misconfiguration early | Session 003 | Medium | ⬜ No |
| Add request ID propagation through all service calls | Session 003 | High | ⬜ No |
| Document database migration strategy before Phase 2 | Session 004 | High | ⬜ No |

<!-- CUSTOMIZE: Clear this table when you start your project and let agents populate it. -->

---

## Blocked Tasks

<!-- Tasks that cannot proceed due to external dependencies or open decisions. -->

| Task | Blocked By | Since | Resolution Path |
|------|-----------|-------|-----------------|
| Payment integration | ADR for payment provider not written | YYYY-MM-DD | Write ADR in next session |

---

## Architecture Decisions Needed

<!-- Decisions that must be made before certain tasks can start.
     Link to DECISIONS.md when resolved. -->

- [ ] Payment provider selection (blocks Phase 2 payment task)
- [ ] Message queue technology for notifications (Kafka vs. SQS vs. Redis Pub/Sub)

---

## Sprint History

| Sprint | Dates | Goal | Tasks Committed | Tasks Completed | Velocity |
|--------|-------|------|-----------------|-----------------|----------|
| 1 | YYYY-MM-DD to YYYY-MM-DD | Foundation setup | 5 | 1 | 0.5/session |

<!-- CUSTOMIZE: This table grows automatically as sprints complete.
     Copy from SPRINT_LOG.md when you implement Level 3 tracking. -->
