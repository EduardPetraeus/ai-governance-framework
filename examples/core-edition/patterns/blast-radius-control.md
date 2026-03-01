# Pattern: Blast Radius Control

## The problem

A session that starts as "add error handling to the connector" ends with modifications to the base class, three other connectors "for consistency," the test framework, and the config system. Each individual change looks defensible. In aggregate, the PR is 1,400 lines and the reviewer skims it.

At AI velocity, a runaway session produces damage 15x faster than a human developer.

## The rule

**One session, one bounded scope.** Define the files before you start. Stop if the task requires going beyond them.

## Defaults to add to CLAUDE.md

```yaml
blast_radius_limits:
  max_files_modified: 15
  max_lines_per_file: 200
  max_new_files: 10
  critical_files_require_explicit_permission:
    - CLAUDE.md
    - .github/workflows/
    - requirements.txt
    - package.json
    - database migration files
    - infrastructure configuration
```

## How it works in practice

**At session start:** The agent states which files it plans to touch. You confirm before it begins.

**During the session:** If the task grows beyond the agreed scope, the agent stops:
```
SCOPE ALERT: Completing this task requires modifying 18 files (limit: 15).
Options:
  1. Complete the first 12 now, create a follow-up task for the remaining 6
  2. Request a limit override for this session
  3. Reassess — can this be decomposed differently?
```

**At session end:** The agent reports final file count against the limit.

## Blast radius classification

| Level | Files changed | Action |
|-------|---------------|--------|
| LOW | 1–5 files, single module | Proceed |
| MEDIUM | 6–10 files, cross-module | Note in session brief |
| HIGH | >10 files, or any critical file | Pause and confirm before proceeding |

## Why this matters

Review quality drops sharply beyond 400 lines. Beyond 1,000 lines, reviewers skim. AI agents routinely produce 500–2,000 line diffs in one session. Explicit limits force task decomposition, which produces better-structured PRs and better reviews.

## Related patterns

- [Output Contracts](output-contracts.md) — contracts define the blast radius for a specific task
- [Human-in-the-Loop](human-in-the-loop.md) — HIGH blast radius triggers a mandatory checkpoint
