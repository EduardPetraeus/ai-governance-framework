# SPRINT_LOG.md

Sprint-level tracking for AI-assisted development. Each sprint has a goal, committed tasks, velocity metrics, blockers, and a retrospective.

**Why this matters:** Velocity data from past sprints is the only reliable way to estimate future sprints. Without it, every commitment is a guess. With it, you can see trends: are sessions getting more productive? Are certain task types consistently underestimated? Is governance overhead increasing or decreasing?

**Update cadence:** One entry at the end of each sprint (typically weekly or at a milestone). The `on_session_end` protocol handles session-level tracking in CHANGELOG.md; this file handles the sprint-level view.

**Entries are newest-first.**

---

## Sprint 002 -- 2025-03-08 to 2025-03-15

**Sprint goal:** Build payment integration and notification foundation
**Sessions planned:** 3
**Sessions used:** 2

### Committed Tasks

| Task | Estimated | Actual | Status | Notes |
|------|-----------|--------|--------|-------|
| Implement Stripe connector | 1 session | 1 session | Complete | Matched estimate. Base class made this fast. |
| Write integration tests for Stripe | 30 min | 20 min | Complete | Done in same session as connector |
| Build notification event system | 1 session | 1.5 sessions | Complete | Schema design took longer than expected |
| Add webhook signature verification | 30 min | -- | Carried over | Lower priority, no blocker created |

### Committed vs. Completed

- **Committed:** 4 tasks
- **Completed:** 3 tasks
- **Carried over:** 1 task (webhook verification -- deprioritized, not blocked)
- **Completion rate:** 75%

### Velocity Metrics

| Metric | This Sprint | Sprint 001 | Trend |
|--------|-------------|------------|-------|
| Tasks completed per session | 1.5 | 1.2 | +25% (improving) |
| Files changed per session | 4.5 | 5.2 | -13% (more focused) |
| Tests added per session | 6 | 0 | n/a (infrastructure sprint vs. feature sprint) |
| Estimate accuracy (actual/estimated) | 90% | 75% | +15% (estimates improving) |
| Governance overhead (min per session) | 18 | 25 | -28% (protocol becoming habitual) |

### Blocker Log

| Blocker | Duration | Resolution | Prevention |
|---------|----------|------------|------------|
| ADR-002 (payment provider) not written | 30 min delay | Wrote ADR at session start before coding | Add "ADR needed?" check to task estimation |

### Retrospective

**What worked:**
- Writing tests alongside the connector (not in a separate session) made testing fast and caught issues early. The schema validation test caught a Stripe API response field that was not in the documentation.
- Model routing: Sonnet for connector code, brief Opus session for the ADR. Correct allocation -- ADR trade-off analysis was materially better with Opus.
- Base connector pattern is paying dividends. Stripe connector took half the expected time because auth, retry, and rate limiting were already handled.

**What did not work:**
- Notification system scope was underestimated. Event schema design required more architectural thought than expected. A 10-minute design discussion at session start would have revealed this.
- Carried-over webhook task created end-of-sprint pressure. Better to commit fewer tasks and complete them all.

**Experiment for next sprint:**
- Buffer 20% of sprint capacity for discovered tasks. This sprint had 2 discovered tasks; zero buffer meant they could not be absorbed without dropping committed work.
- Write ADRs for open decisions at sprint start, not at task start. Eliminates mid-session delays.

---

## Sprint 001 -- 2025-03-01 to 2025-03-08

**Sprint goal:** Foundation -- project structure, tooling, base infrastructure
**Sessions planned:** 3
**Sessions used:** 2

### Committed Tasks

| Task | Estimated | Actual | Status | Notes |
|------|-----------|--------|--------|-------|
| Set up project structure | 30 min | 30 min | Complete | Clean match |
| Configure Python tooling (ruff, mypy, pytest) | 30 min | 45 min | Complete | mypy strict mode required extra config |
| Implement base connector class | 1 session | 1 session | Complete | Solid foundation, retry logic well-tested |
| Set up local development environment | 30 min | 1 hour | Complete | Docker volume mount permissions on macOS |
| Add governance files (CLAUDE.md, PROJECT_PLAN.md) | 30 min | 30 min | Complete | Templates made this fast |
| Implement authentication framework | 1 session | -- | Carried over | Deprioritized for base connector work |

### Committed vs. Completed

- **Committed:** 6 tasks
- **Completed:** 5 tasks
- **Carried over:** 1 task (auth framework -- deprioritized, not blocked)
- **Completion rate:** 83%

### Velocity Metrics

| Metric | This Sprint | Baseline | Notes |
|--------|-------------|----------|-------|
| Tasks completed per session | 1.2 | n/a | First sprint, establishing baseline |
| Files changed per session | 5.2 | n/a | Infrastructure-heavy, expected to be high |
| Tests added per session | 0 | n/a | Infrastructure sprint -- no features to test yet |
| Estimate accuracy | 75% | n/a | Infrastructure tasks consistently underestimated |

### Blocker Log

| Blocker | Duration | Resolution | Prevention |
|---------|----------|------------|------------|
| Docker volume mount permissions on macOS | 45 min | Added `:delegated` flag and documented | Add OS-specific notes to setup docs |

### Retrospective

**What worked:**
- Starting with governance files before any code was the right call. Session 002 benefited immediately from CLAUDE.md and PROJECT_PLAN.md being in place. The agent arrived with context and produced consistent output.
- The base connector pattern is solid. Sprint 002's Stripe connector took half the expected time because the base class handled auth, retry, and rate limiting.

**What did not work:**
- Auth framework was carried over. It was estimated at 1 session but was never started because infrastructure took priority. Should have been lower in the committed list (priority order, not dependency order).
- Infrastructure setup estimates were too optimistic. Docker permissions, mypy configuration, and pyproject.toml setup all took longer than estimated. Add 50% buffer for infrastructure tasks.

**Experiment for next sprint:**
- Order committed tasks by priority, not dependency. The most important task should be done first, even if it has dependencies that are "supposed" to come first.
- Record actual time alongside estimates in the task table. Build calibration data for future estimation.

---

## Velocity Trend

<!-- This table summarizes velocity across all sprints for quick reference.
     Update it when adding a new sprint entry. -->

| Sprint | Tasks Committed | Tasks Completed | Completion Rate | Tasks/Session | Estimate Accuracy |
|--------|----------------|-----------------|-----------------|---------------|-------------------|
| 001 | 6 | 5 | 83% | 1.2 | 75% |
| 002 | 4 | 3 | 75% | 1.5 | 90% |

**Trend notes:**
- Tasks per session improving (+25% sprint over sprint)
- Estimate accuracy improving (+15% sprint over sprint)
- Commit fewer tasks: 4 is closer to actual capacity than 6

<!-- Add new sprints above this line -->
