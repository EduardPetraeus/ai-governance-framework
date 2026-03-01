# Pattern Effectiveness Metrics

Governance patterns are only valuable if they produce measurable outcomes. This document defines how to measure whether adopted patterns actually reduce errors, speed up development, and lower rework.

## Core Metrics

| Metric | What It Measures | Collection Method |
|--------|-----------------|-------------------|
| Incidents per sprint | Production issues caused by AI-generated code | Issue tracker, tagged with `ai-generated` |
| Agent error rate | Percentage of AI sessions requiring correction | Session logs, CHANGELOG entries marked as fixes |
| Human intervention rate | How often a human must override or redo agent output | PR review comments, rejected PRs |
| Rework rate | Percentage of AI output that gets rewritten within 2 sprints | Git blame analysis on recently changed files |
| Time to first correct output | How many iterations before the agent produces accepted code | Session replay artifacts |
| Governance friction ratio | Time spent on governance overhead vs. productive output | Friction budget tracking (see [friction-budget.md](../patterns/friction-budget.md)) |

## Baseline Template

Measure these metrics **before** adopting governance patterns. Without a baseline, improvement claims are meaningless.

```yaml
# baseline-metrics.yml
# Record these values before governance adoption
project: ""
date_recorded: "YYYY-MM-DD"
sprint: 0
measurement_period_days: 14

metrics:
  incidents_per_sprint: 0
  agent_error_rate_pct: 0.0
  human_intervention_rate_pct: 0.0
  rework_rate_pct: 0.0
  avg_time_to_first_correct_output_min: 0
  governance_friction_ratio_pct: 0.0

notes: ""
```

## Post-Governance Template

Record the same metrics after governance patterns have been active for at least 2 full sprints. Shorter measurement windows produce noise, not signal.

```yaml
# post-governance-metrics.yml
project: ""
date_recorded: "YYYY-MM-DD"
sprint: 0
governance_active_since: "YYYY-MM-DD"
patterns_adopted:
  - "blast-radius-control"
  - "output-contracts"
  - "progressive-trust"
measurement_period_days: 14

metrics:
  incidents_per_sprint: 0
  agent_error_rate_pct: 0.0
  human_intervention_rate_pct: 0.0
  rework_rate_pct: 0.0
  avg_time_to_first_correct_output_min: 0
  governance_friction_ratio_pct: 0.0

comparison_to_baseline:
  incidents_delta_pct: 0.0
  error_rate_delta_pct: 0.0
  intervention_delta_pct: 0.0
  rework_delta_pct: 0.0

notes: ""
```

## Per-Pattern Effectiveness Tracking

Track each pattern independently so you know which ones deliver value and which add overhead without payoff.

```yaml
# pattern-effectiveness.yml
pattern: "blast-radius-control"
adopted_date: "YYYY-MM-DD"
status: "active"

before_adoption:
  incidents_per_sprint: 3
  rework_rate_pct: 25.0
  avg_files_modified_per_session: 32

after_adoption:
  incidents_per_sprint: 1
  rework_rate_pct: 8.0
  avg_files_modified_per_session: 11
  measurement_sprints: 4

effectiveness:
  incident_reduction_pct: 66.7
  rework_reduction_pct: 68.0
  verdict: "keep"
  # verdict options: keep, adjust, remove
```

## Comparison Methodology

### Before/After (Single Team)

The simplest approach. Requires honest baseline measurement.

1. **Measure baseline** — Record all core metrics for 2-4 sprints before adopting governance patterns.
2. **Adopt patterns** — Implement governance changes. Allow 1 sprint for adjustment (do not measure this sprint).
3. **Measure post-governance** — Record the same metrics for 2-4 sprints.
4. **Compare** — Calculate percentage change for each metric.
5. **Attribute carefully** — Other factors (team changes, project complexity, tooling upgrades) can confound results. Document all concurrent changes.

### Control Group (Multi-Team)

Stronger evidence, but requires organizational coordination.

1. **Select two comparable teams** — Similar project complexity, team size, and AI usage patterns.
2. **Team A adopts governance** — Full pattern implementation.
3. **Team B continues as-is** — No governance changes during the measurement period.
4. **Measure both teams** — Same metrics, same sprints, same collection methods.
5. **Compare deltas** — The difference between Team A's improvement and Team B's natural variation is the governance effect.
6. **Rotate** — After measurement, Team B adopts governance. Repeat to confirm results.

### Interpretation Guidelines

| Result | Interpretation | Action |
|--------|---------------|--------|
| Incidents down >30%, friction <15% | Governance is working efficiently | Maintain current patterns |
| Incidents down >30%, friction >25% | Governance works but costs too much | Simplify or automate governance steps |
| Incidents unchanged, friction >15% | Governance adds overhead without benefit | Re-evaluate pattern selection |
| Incidents up, friction up | Governance is actively harmful | Roll back, diagnose root cause |
| Rework down >20% | AI output quality improved | Document which patterns drove the change |

## Reporting Cadence

- **Weekly**: Agent error rate, human intervention rate (lightweight, from session logs)
- **Per sprint**: Full metrics comparison against baseline
- **Quarterly**: Pattern-level effectiveness review — decide which patterns to keep, adjust, or remove
- **Annually**: Full framework ROI assessment with cost data from [COST_LOG.md](../templates/COST_LOG.md)
