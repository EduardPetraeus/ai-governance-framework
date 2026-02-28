# COST_LOG.md

AI cost tracking at the session level. This file gives you visibility into what you are spending on AI assistance, which models provide the best value per task type, and where you can optimize without sacrificing quality.

**Tracking philosophy:** We track at the session level, not the token level. Token-level tracking requires SDK instrumentation and is overkill for most teams. Session-level estimation (based on model used and tasks completed) is accurate enough to spot trends, catch anomalies, and optimize model routing.

**Update cadence:** One row added per session by the `on_session_end` protocol or manually.

---

## Cost Estimation Reference

Use these ranges when recording sessions. Actual costs vary by 20--40% depending on context window size and output length, but these are reliable for trend analysis and budget decisions.

| Model | Task Type | Estimated Cost per Task |
|-------|-----------|------------------------|
| claude-opus-4-6 | Architecture decision, ADR, security review | $0.08 -- $0.15 |
| claude-opus-4-6 | Complex debugging, multi-file root cause analysis | $0.10 -- $0.20 |
| claude-sonnet-4-6 | Code generation, feature implementation | $0.01 -- $0.03 |
| claude-sonnet-4-6 | PR review, documentation, CHANGELOG update | $0.005 -- $0.01 |
| claude-haiku-3-5 | File reads, config edits, status checks | $0.001 -- $0.003 |

**Rule of thumb:** One Opus architecture session costs as much as 10--20 Sonnet feature sessions. Model routing is the single highest-leverage cost optimization.

---

## Session Cost Log

| Session | Date | Model | Tasks | Task Types | Est. Cost | Notes |
|---------|------|-------|-------|-----------|-----------|-------|
| 005 | 2025-03-22 | claude-opus-4-6 | 2 | 1 security review, 1 ADR | $0.28 | Opus security review caught hardcoded path missed by pre-commit |
| 004 | 2025-03-20 | claude-sonnet-4-6 | 5 | 3 code, 1 test, 1 docs | $0.09 | Notification event system + tests |
| 003 | 2025-03-15 | claude-sonnet-4-6 | 4 | 3 code, 1 docs | $0.08 | Stripe connector + integration tests |
| 002 | 2025-03-10 | claude-sonnet-4-6 | 3 | 2 code, 1 review | $0.05 | Base connector + local environment |
| 001 | 2025-03-01 | claude-sonnet-4-6 | 5 | 4 infrastructure, 1 docs | $0.12 | Setup-heavy: more context loading, larger prompts |

---

## Monthly Summary

| Month | Sessions | Total Tasks | Total Cost | Avg Cost/Session | Avg Cost/Task | Opus Sessions | Sonnet Sessions | Haiku Sessions |
|-------|----------|-------------|-----------|-----------------|---------------|---------------|-----------------|----------------|
| 2025-03 | 5 | 19 | $0.62 | $0.12 | $0.03 | 1 | 4 | 0 |

---

## Cost Optimization Notes

### Tasks Currently Using Sonnet That Should Use Haiku

Review this quarterly. If a task type consistently costs under $0.01 on Sonnet, it is a candidate for Haiku. Haiku is 10--20x cheaper for simple tasks with no quality loss.

| Task Type | Current Model | Recommended | Est. Savings per Month |
|-----------|--------------|-------------|----------------------|
| Reading CHANGELOG.md at session start | Sonnet | Haiku | ~$0.01/month (4 sessions) |
| Simple config edits (YAML, JSON, env vars) | Sonnet | Haiku | ~$0.02/month |
| Status report generation at session end | Sonnet | Haiku | ~$0.01/month |
| File structure validation and quick lookups | Sonnet | Haiku | ~$0.01/month |

### Tasks Currently Using Sonnet That Need Opus

Be honest about this. Using Sonnet for high-stakes tasks is a false economy. One wrong architectural decision from Sonnet costs more in rework than 50 Opus sessions.

| Task Type | Current Model | Should Be | Risk of Current Approach |
|-----------|--------------|-----------|--------------------------|
| Security review before production release | Sonnet | Opus | Missing subtle vulnerabilities, false confidence |
| New architectural patterns (first implementation) | Sonnet | Opus | Shallow pattern matching instead of deep reasoning |
| ADR writing (trade-off analysis) | Sonnet | Opus | Superficial rationale, weak alternatives analysis |
| Cross-system debugging (3+ files involved) | Sonnet | Opus | Missing root cause, fixing symptoms not causes |

---

## Budget Alerts

Set these thresholds and review when triggered. Alerts do not stop work automatically -- they trigger a review of whether model routing can be optimized.

| Alert | Threshold | Action When Triggered |
|-------|-----------|----------------------|
| Session cost spike | Any single session > $0.50 | Review: was Opus used for tasks Sonnet could handle? |
| Monthly budget | Monthly total > $[your budget] | Review routing table. Which sessions used the wrong model? |
| Haiku underuse | 0 Haiku sessions in a calendar month | Are we using Sonnet for trivial tasks? |
| Opus overuse | >30% of sessions used Opus | Are architecture decisions really this frequent, or is Opus being used for feature work? |
| Cost per task rising | Avg cost/task increasing month over month | Are sessions getting less focused? More context loading? |

---

## ROI Notes

Cost tracking without value tracking is incomplete. Record significant outcomes here to put the numbers in context. The question is not "how much did AI cost?" but "what did we get for that cost?"

| Month | AI Cost | Developer Hours Saved (est.) | Hourly Rate | Value Generated | ROI |
|-------|---------|------------------------------|-------------|-----------------|-----|
| 2025-03 | $0.62 | ~12 hours | $[rate]/hr | $[rate x 12] | [value/cost]x |

**How to estimate hours saved:** For each completed task, estimate how long it would have taken without AI assistance. Be conservative -- use 70% of your gut estimate. Sum across all tasks in the month. This gives a defensible (if approximate) value figure.

**Velocity comparison:**
- Pre-AI baseline: [X] tasks per session
- Current with AI: [Y] tasks per session
- Improvement: [Y/X]x

<!-- CUSTOMIZE: Fill in your hourly rate and update monthly.
     This data is what justifies continued AI investment to stakeholders. -->
