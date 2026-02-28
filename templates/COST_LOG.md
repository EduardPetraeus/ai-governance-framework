# COST_LOG.md

AI cost tracking at the session level. This file gives you visibility into what you're
spending on AI assistance, which models are providing the best value, and where you can
optimize without sacrificing quality.

**Tracking philosophy:** We track at the session level, not the token level. Token-level
tracking requires SDK instrumentation and is overkill for most teams. Session-level tracking
(estimating cost based on model used and tasks completed) is accurate enough to spot trends
and make routing decisions.

**Update cadence:** One row added per session by the /end-session command or manually.

---

## Cost Estimation Guide

Use these estimates when recording sessions. Actual costs vary by 20-40%, but these are
reliable for trend analysis and budget planning.

| Model | Task type | Estimated cost per task |
|-------|-----------|------------------------|
| claude-opus-4-6 | Architecture decision, ADR, security review | $0.08 - $0.15 |
| claude-opus-4-6 | Complex debugging, multi-file analysis | $0.10 - $0.20 |
| claude-sonnet-4-6 | Code generation, feature implementation | $0.01 - $0.03 |
| claude-sonnet-4-6 | PR review, documentation | $0.005 - $0.01 |
| claude-haiku-3-5 | File reads, simple edits, status checks | $0.001 - $0.003 |

**Rule of thumb:** One Opus architecture session ≈ 10-20 Sonnet feature sessions.
Model routing is the single highest-leverage cost optimization action.

---

## Session Cost Log

| Session | Date | Model | Tasks Completed | Task Types | Estimated Cost | Notes |
|---------|------|-------|-----------------|-----------|----------------|-------|
| 003 | 2025-03-15 | claude-sonnet-4-6 | 4 | 3 code, 1 docs | $0.08 | Stripe connector + tests |
| 002 | 2025-03-10 | claude-sonnet-4-6 | 3 | 2 code, 1 review | $0.05 | Base connector + environment |
| 001 | 2025-03-01 | claude-sonnet-4-6 | 5 | 4 infra, 1 docs | $0.12 | Setup-heavy, more context needed |

---

## Monthly Summary

| Month | Sessions | Total Tasks | Total Cost | Avg Cost/Session | Avg Cost/Task | Primary Model |
|-------|----------|-------------|-----------|-----------------|---------------|---------------|
| 2025-03 | 3 | 12 | $0.25 | $0.08 | $0.02 | claude-sonnet-4-6 |

---

## Cost Optimization Notes

### Tasks that should use Haiku (currently using Sonnet)

Review this quarterly. If you notice certain task types are consistently cheap on Sonnet,
they're probably candidates for Haiku.

| Task type | Current model | Recommended | Estimated savings |
|-----------|--------------|-------------|------------------|
| Reading CHANGELOG.md at session start | sonnet | haiku | ~$0.002/session |
| Simple config edits (YAML, JSON) | sonnet | haiku | ~$0.003/task |
| Status report generation | sonnet | haiku | ~$0.002/report |

### Tasks that need Opus (currently using Sonnet)

Be honest about this. Using Sonnet for architecture decisions is a false economy —
one wrong architectural call costs far more in rework than the model price difference.

| Task type | Current model | Should be | Risk of current approach |
|-----------|--------------|-----------|--------------------------|
| Security review before production release | sonnet | opus | Missing subtle vulnerabilities |
| New architectural patterns | sonnet | opus | Introducing technical debt |
| ADR writing | sonnet | opus | Shallower trade-off analysis |

---

## Budget Alerts

Set these thresholds and review when they're hit. Alerts don't automatically stop work —
they trigger a review of whether model routing can be optimized.

| Alert | Threshold | Action |
|-------|-----------|--------|
| Session cost spike | Any session > $0.50 | Review: was Opus used appropriately? |
| Monthly overage | Monthly total > $[your budget] | Review model routing decisions |
| Haiku underutilization | 0 Haiku sessions in a month | Are we using Sonnet for everything? |
| Opus overuse | >30% of sessions use Opus | Are architecture decisions this frequent? |

---

## ROI Notes

Cost tracking without value tracking is incomplete. Record significant outcomes here to
give context to the cost numbers.

| Month | AI Cost | Notable outcomes | ROI assessment |
|-------|---------|-----------------|----------------|
| 2025-03 | $0.25 | Stripe connector (est. 6 hours saved), base class design, project setup | High — setup cost, ongoing leverage |

**Velocity baseline (pre-AI):** [Record your baseline if you have it]
**Velocity current:** [Record tasks per session to track improvement over time]
