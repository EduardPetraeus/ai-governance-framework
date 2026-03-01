# Pattern: Output Contracts

## The problem

Without a defined contract, "success" is whatever the agent produces. The human reviews the output and pattern-matches: "looks right" becomes the quality bar. This is how subtle logic errors and missing requirements reach production.

A second problem: without a contract, scope creeps silently. The agent touches files outside the task boundary, refactors code that was not broken, and adds features that were not requested. Each addition looks individually reasonable. In aggregate, the session has drifted far from the intended change.

## The rule

**Before the agent begins any task, define what the output must and must not contain.**

The contract is the acceptance criteria. Review verifies the contract, not the output in isolation.

## Minimal contract format

```yaml
output_contract:
  task: "Create GitHub stars connector"

  files_created:
    - src/connectors/github/stars.py
    - tests/connectors/test_github_stars.py

  files_modified:
    - src/connectors/registry.py

  files_not_touched:
    - src/connectors/gitlab/
    - src/core/

  must_include:
    - "authentication via environment variable (not hardcoded)"
    - "error handling for rate limits"
    - "type hints on all public functions"

  must_not_include:
    - "hardcoded credentials"
    - "print statements (use logging)"

  checks:
    tests_pass: true
    lint: clean
```

Write the contract before the session starts. Writing it after seeing the output is confirmation bias, not quality control.

## Agent compliance report

At session end, the agent produces:

```yaml
contract_compliance:
  task: "Create GitHub stars connector"
  status: complete

  must_include_status:
    - "authentication via env var": DONE — reads from GITHUB_TOKEN
    - "rate limit handling": DONE — checks X-RateLimit-Remaining header
    - "type hints": DONE — all public functions annotated

  must_not_include_status:
    - "hardcoded credentials": VERIFIED absent
    - "print statements": VERIFIED absent

  checks:
    tests_pass: PASS (14/14)
    lint: PASS

  deviations: none
  confidence: 88%
```

If the agent cannot meet a contract item, it reports the deviation before proceeding — not after.

## Where contracts live

- **Per-task**: In `PROJECT_PLAN.md` alongside the task definition
- **Recurring**: In `CLAUDE.md` as always-on rules (e.g., "never modify governance files without permission")

## Why this works

The contract makes review mechanical: check each item, verify compliance, flag deviations. A 5-minute review replaces a 30-minute read-and-decide. The reviewer checks a list instead of judging whether the output "looks right."

## Related patterns

- [Blast Radius Control](blast-radius-control.md) — the `files_not_touched` section IS blast radius control for a specific task
- [Human-in-the-Loop](human-in-the-loop.md) — contracts define what the human reviews at each checkpoint
