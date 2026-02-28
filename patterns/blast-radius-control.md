# Blast Radius Control

## Name

Blast Radius Control — explicitly limit what a single session can change.

## Problem

An AI session that goes wrong can change hundreds of files. The scope of damage from a bad session is unbounded without explicit limits. At 15x human velocity, a runaway agent session produces damage 15x faster than a human developer.

The failure mode is not obvious. The agent does not crash or produce errors. It produces reasonable-looking changes — just too many of them, in too many places, with cascading implications that no single review can fully assess. A session that starts as "add error handling to the Oura connector" ends with modifications to the base class, the test framework, the configuration system, and three other connectors "for consistency."

Each individual change may be defensible. In aggregate, the session has introduced a review burden that exceeds the reviewer's capacity. The reviewer either spends hours understanding the full scope, or — more commonly — pattern-matches through the diff and approves. The latter is how cross-cutting bugs and architectural drift enter the codebase.

## Solution

Explicitly limit what a single session can change. Define hard stops that prevent scope expansion. Review session scope before starting. Enforce limits through CLAUDE.md instructions and CI/CD checks.

### Default Limits

| Limit | Default | Rationale |
|-------|---------|-----------|
| Maximum files modified per session | 15 | Beyond this, review quality drops sharply |
| Maximum lines changed per file | 200 | Large changes to a single file signal refactoring that needs architectural review |
| Maximum new files created | 10 | Many new files signal feature scope that should be split |

### Critical Files

Certain files govern the behavior of the entire project. Changes to these files cascade and must require explicit human permission:

- `CLAUDE.md` — governs the governance; unauthorized changes can weaken all rules
- `.github/workflows/` — CI/CD pipelines; changes affect every future merge
- `package.json` / `requirements.txt` — dependency changes affect the entire dependency tree
- Database migration files — schema changes are irreversible in production
- Infrastructure configuration — Terraform, Docker, deployment manifests
- Security configuration — authentication, authorization, encryption settings

### Forbidden Combinations

Certain types of changes must never happen in the same session:

| Combination | Why It Is Forbidden |
|------------|-------------------|
| Architecture changes + implementation | Decide first, implement second. Mixing them means neither gets adequate review. |
| Schema migration + application code | Migration failures should not be entangled with application logic. |
| Dependency upgrade + feature work | Dependency changes have unpredictable side effects that contaminate feature review. |
| Governance file changes + code changes | Governance changes affect how all future code is reviewed. They deserve isolated attention. |

## When to Use

- Every AI agent session that modifies code or configuration
- Sessions where the task description is broad ("improve error handling," "refactor the connector module")
- Sessions involving junior or recently-onboarded agents (trust Level 1-2 in [Progressive Trust](progressive-trust.md))
- Any session where the agent has write access to critical files

## When NOT to Use

- Read-only analysis sessions where the agent produces recommendations but no file changes
- Sessions with explicit human co-piloting where every change is approved in real time
- Initial project scaffolding sessions where creating many files is the intended outcome (but even here, set a higher explicit limit rather than removing limits entirely)

## Implementation

### Step 1: Define limits in CLAUDE.md

Add blast radius limits to your project's CLAUDE.md:

```yaml
blast_radius_limits:
  max_files_modified: 15
  max_lines_per_file: 200
  max_new_files: 10
  critical_files:
    - CLAUDE.md
    - .github/workflows/
    - requirements.txt
    - alembic/versions/          # database migrations
    - terraform/                  # infrastructure
  forbidden_combinations:
    - ["architecture_change", "implementation"]
    - ["schema_migration", "application_code"]
    - ["dependency_upgrade", "feature_work"]
    - ["governance_change", "code_change"]
```

### Step 2: Scope review at session start

Before the agent begins work, define and review the session scope:

```
Session scope check:
  Task: Add error handling to the Oura connector
  Planned files:
    - src/connectors/oura/sleep.py (modify)
    - tests/connectors/test_oura_sleep.py (modify)
  Estimated changes: 2 files, ~80 lines
  Blast radius: LOW

  Blast radius classification:
    LOW:    1-5 files, single module, no critical files
    MEDIUM: 6-10 files, cross-module, no critical files
    HIGH:   >10 files, or any critical files, or cross-layer changes

  Action for HIGH: pause and get explicit human confirmation before proceeding
```

### Step 3: Monitor scope during the session

The agent should track its changes and alert when approaching limits:

```
Scope tracker (updated during session):
  Files modified: 3 / 15 limit
  Files created: 1 / 10 limit
  Largest change: 65 lines in sleep.py / 200 limit
  Critical files touched: none
  Status: WITHIN LIMITS
```

If the agent realizes mid-session that the task requires exceeding limits, it must stop and request permission:

```
SCOPE ALERT: This task requires modifying 18 files to be complete.
Current limit: 15 files per session.
Options:
  1. Complete the first 12 files now, create a follow-up task for the remaining 6
  2. Request limit override for this session (requires human confirmation)
  3. Reassess the approach — can the task be decomposed differently?
Recommendation: Option 1 — split into two sessions for manageable review
```

### Step 4: Validate scope at session end

At the end of the session, verify compliance:

```bash
# Check files modified count
git diff --stat HEAD~1 | tail -1
# Expected: "N files changed, X insertions(+), Y deletions(-)"
# Verify N <= max_files_modified

# Check for critical file modifications
git diff --name-only HEAD~1 | grep -E "(CLAUDE\.md|\.github/workflows/|requirements\.txt)"
# If any matches: verify explicit permission was granted

# Check largest file change
git diff --stat HEAD~1 | sort -t'|' -k2 -n -r | head -5
# Verify no single file exceeds max_lines_per_file
```

### Step 5: Add CI/CD enforcement

Create a GitHub Actions check that validates blast radius on PRs:

```yaml
name: Blast Radius Check
on:
  pull_request:
    branches: [main]

jobs:
  check-blast-radius:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Check file count
        run: |
          FILE_COUNT=$(git diff --name-only origin/main...HEAD | wc -l)
          echo "Files changed: $FILE_COUNT"
          if [ "$FILE_COUNT" -gt 15 ]; then
            echo "::warning::Blast radius exceeded: $FILE_COUNT files changed (limit: 15)"
            echo "::warning::Consider splitting this PR into smaller changes"
          fi
      - name: Check critical files
        run: |
          CRITICAL=$(git diff --name-only origin/main...HEAD | grep -E "(CLAUDE\.md|\.github/workflows/)" || true)
          if [ -n "$CRITICAL" ]; then
            echo "::warning::Critical files modified — requires explicit reviewer approval:"
            echo "$CRITICAL"
          fi
```

## Example

A developer assigns a task: "Improve error handling across all connectors." Without blast radius control, the agent session modifies 23 files across 5 connector modules, updates the base class, changes the test fixtures, and adds a new error taxonomy to the documentation. The PR is 1,400 lines. The reviewer spends 90 minutes, misses a subtle regression in the Fitbit connector's pagination logic, and approves.

With blast radius control, the session starts with a scope review:

```
Session scope check:
  Task: Improve error handling across all connectors
  Estimated changes: 23 files, ~1400 lines
  Blast radius: HIGH

  SCOPE ALERT: Task exceeds blast radius limits.
  Recommendation: Split into per-connector sessions.
```

The developer agrees to split. Five sessions follow:

1. Oura connector error handling (3 files, 120 lines) — reviewed in 10 minutes
2. Fitbit connector error handling (3 files, 95 lines) — reviewed in 8 minutes. Reviewer catches the pagination regression because the review is focused.
3. Garmin connector error handling (4 files, 140 lines) — reviewed in 12 minutes
4. Base class updates (2 files, 80 lines) — reviewed in 8 minutes
5. Documentation and error taxonomy (3 files, 200 lines) — reviewed in 15 minutes

Total review time: 53 minutes (versus 90 minutes for the monolithic PR). Quality: higher, because each review was focused on a single context. The pagination regression was caught at session 2, not missed in a 23-file diff.

## Evidence

Blast radius control applies the same principle as small batch sizes in lean manufacturing and continuous delivery: smaller changes are easier to review, easier to understand, easier to revert, and less likely to contain hidden interactions.

Research on code review effectiveness consistently shows that review quality degrades as diff size increases. Beyond approximately 400 lines, reviewers begin skimming rather than reading. Beyond 1,000 lines, the review becomes perfunctory. AI agents routinely produce diffs of 500-2,000 lines in a single session, putting every review in the "skimming" zone.

The specific advantage of explicit limits (rather than guidelines) is that they create a forcing function for task decomposition. When the agent knows it cannot modify more than 15 files, it must design its approach to fit within that constraint. This produces better-structured changes as a side effect.

## Related Patterns

- [Output Contracts](output-contracts.md) — contracts specify the blast radius for a specific task
- [Progressive Trust](progressive-trust.md) — higher trust levels can allow larger blast radii for trusted domains
- [Context Boundaries](context-boundaries.md) — limits what the agent reads; blast radius limits what it writes
- [Human-in-the-Loop](human-in-the-loop.md) — high blast radius triggers mandatory human confirmation
- [Quality Control Patterns](../docs/quality-control-patterns.md) — blast radius control enables effective review at Layer 4
