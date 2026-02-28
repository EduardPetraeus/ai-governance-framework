# SPRINT_LOG.md

Sprint-level tracking for AI-assisted development. Each sprint has its own entry with
committed tasks, completed tasks, velocity metrics, blockers, and a retrospective.

**Why this matters:** Velocity data from past sprints is the only reliable way to estimate
future sprints. Without it, every sprint is a guess. With it, you can see trends: are
sessions getting more productive? Are certain task types consistently taking longer than
estimated?

**Update cadence:** At the end of each sprint (typically weekly or at a milestone).
The /end-session command handles session-level tracking; this file handles sprint-level.

---

## Sprint 002 — 2025-03-08 to 2025-03-15

**Sprint goal:** Build payment integration and notification foundation
**Sessions this sprint:** 3
**Sessions used:** 2

### Committed tasks

| Task | Estimated | Status | Sessions Used |
|------|-----------|--------|---------------|
| Implement Stripe connector | 1 session | ✅ Complete | 1 |
| Write integration tests for Stripe | 30 min | ✅ Complete | 0.5 (done with connector) |
| Build notification event system | 1 session | ✅ Complete | 1 |
| Add webhook signature verification | 30 min | 🔵 Carried over | 0 |

### Committed vs. completed

- Committed: 4 tasks
- Completed: 3 tasks
- Carried over: 1 task (webhook verification — lower priority, no blocker)

### Velocity metrics

| Metric | This Sprint | Sprint 001 | Trend |
|--------|-------------|------------|-------|
| Tasks per session | 1.5 | 1.2 | +25% ↑ |
| Files changed per session | 4.5 | 5.2 | -13% ↓ |
| Tests added per session | 6 | 0 | (infrastructure sprint vs feature sprint) |
| Estimated vs. actual (avg) | 90% | 75% | +15% ↑ (estimates improving) |

### Blockers encountered

- ADR-002 (payment provider selection) took 30 minutes to write before Stripe work could
  start. This delay was not in the sprint estimate. Add "ADR if needed" to task estimates
  when the decision is not yet made.

### Retrospective

**What worked:**
- Writing tests alongside the connector (not after) made the integration test session fast
- The base connector's `validate_schema()` method caught a Stripe API response change
  immediately — would have been a silent bug otherwise
- Model routing: used Sonnet for connector code, brief Opus session for the ADR. Right calls.

**What didn't work:**
- Underestimated the notification system scope. What looked like one session became 1.5.
  The event schema design required more thought than expected.
- The carried-over webhook verification task created pressure at sprint end. Better to
  commit fewer tasks and finish them all.

**What to try next sprint:**
- Buffer 20% of sprint capacity for discovered tasks (this sprint had 3 discovered tasks)
- Write the ADR for message queue technology before starting Sprint 003 notification work

---

## Sprint 001 — 2025-03-01 to 2025-03-08

**Sprint goal:** Foundation — project structure, tooling, base infrastructure
**Sessions this sprint:** 3
**Sessions used:** 2

### Committed tasks

| Task | Estimated | Status | Sessions Used |
|------|-----------|--------|---------------|
| Set up project structure | 30 min | ✅ Complete | 0.5 |
| Configure Python tooling (ruff, mypy, pytest) | 30 min | ✅ Complete | 0.5 |
| Implement base connector class | 1 session | ✅ Complete | 1 |
| Set up local development environment | 30 min | ✅ Complete | 0.5 |
| Add governance files (CLAUDE.md, PROJECT_PLAN.md) | 30 min | ✅ Complete | 0.5 |
| Implement authentication framework | 1 session | ⬜ Carried over | 0 |

### Committed vs. completed

- Committed: 6 tasks
- Completed: 5 tasks
- Carried over: 1 task (auth framework — deprioritized in favor of getting connector base ready)

### Velocity metrics

| Metric | This Sprint | Baseline | Notes |
|--------|-------------|----------|-------|
| Tasks per session | 1.2 | n/a | First sprint, calibrating |
| Files per session | 5.2 | n/a | Infrastructure-heavy |
| Tests added per session | 0 | n/a | No features yet to test |
| Estimate accuracy | 75% | n/a | Infrastructure always surprises |

### Blockers encountered

- Docker Compose setup took 2x the estimated time due to volume mount permission issues
  on macOS. Add OS-specific notes to setup documentation.

### Retrospective

**What worked:**
- Starting with governance files before any code was the right call. Session 002 benefited
  immediately from having CLAUDE.md and PROJECT_PLAN.md in place.
- The base connector pattern is solid. Stripe connector in Sprint 002 took half the expected
  time because the base class handled so much.

**What didn't work:**
- Auth framework was carried over. It was estimated at 1 session but wasn't started because
  infrastructure took priority. Should have been lower in the committed list.

**What to try next sprint:**
- Put most important tasks first in committed list (priority order, not dependency order)
- Establish the estimate-calibration habit: when a task is done, record actual time in the table

<!-- Add new sprints above this line -->
