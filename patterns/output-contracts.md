# Output Contracts

## Name

Output Contracts — define expected output before the agent works.

## Problem

Without a defined contract, "success" is whatever the agent produces. The human reviews the output and pattern-matches: "looks right" becomes the quality bar. This is how subtle logic errors, missing edge cases, and incomplete implementations reach production.

The failure mode is insidious because it feels like quality control is happening. The human reads the code. The human sees familiar patterns. The human approves. But the human was never checking against a specification — they were checking against their own sense of "this seems reasonable." That sense is wrong often enough to matter.

A second problem: without a contract, scope creeps silently. The agent touches files outside the task boundary. It refactors code that was not broken. It adds features that were not requested. Each addition looks individually reasonable. In aggregate, the session has drifted far from the intended change.

## Solution

Before the agent begins any task, define what the output MUST contain, what it MUST NOT contain, and what automated checks must pass. The contract is the acceptance criteria. Review verifies the contract, not the output in isolation.

### Contract structure

```yaml
output_contract:
  name: "[descriptive contract name]"
  task: "[task being contracted]"

  files_created:
    - path/to/new_file.py           # every new file, with path
    - tests/test_new_file.py        # tests are part of the contract

  files_modified:
    - config.yaml                   # constraint: new entries only, no existing entries changed
    - README.md                     # constraint: add entry to feature list section only

  files_not_touched:
    - CLAUDE.md                     # governance files stay unchanged
    - src/unrelated_module/         # other modules are out of scope

  must_include:
    - "error handling for API rate limits"
    - "incremental fetch (not full history every time)"
    - "retry logic with exponential backoff"
    - "type hints on all public functions"
    - "docstrings on all public functions"

  must_not_include:
    - "hardcoded API keys or secrets"
    - "print statements (use logging)"
    - "files outside the designated directories"
    - "modifications to existing test assertions"
    - "wildcard imports"

  automated_checks:
    tests_pass: true
    security_scan: clean
    lint: clean
    coverage_threshold: 70         # percentage

  verification_steps:
    - "Run connector against sandbox API and verify response parsing"
    - "Verify incremental fetch by running twice and checking no duplicate records"
    - "Confirm rate limit handling by sending requests at 2x the documented limit"
```

### Where contracts live

Contracts belong alongside the work they govern:

- **Per-task contracts**: In `PROJECT_PLAN.md` alongside each task definition
- **Sprint contracts**: In a dedicated `SPRINT_CONTRACTS.md` file
- **Recurring contracts**: In CLAUDE.md for patterns that apply to every session (e.g., "never modify governance files without explicit permission")

## When to Use

- Every task that produces code changes (the contract can be simple for simple tasks)
- Tasks where the definition of "done" is ambiguous
- Tasks involving multiple files or cross-cutting changes
- Tasks where an error would be costly to discover in production
- When onboarding a new agent to a project (contracts communicate expectations)

## When NOT to Use

- Exploratory sessions where the goal is to investigate, not to produce
- Single-file documentation updates with obvious scope
- When the overhead of writing the contract exceeds the risk of the task (but this threshold is higher than most people think)

## Implementation

### Step 1: Write the contract before the session starts

The contract is written by the human (or a planning agent) before the implementation agent begins. This is non-negotiable. Writing the contract after seeing the output is confirmation bias, not quality control.

```yaml
# Example: contract for adding a new data source
output_contract:
  name: "github-stars-connector"
  task: "Create connector to fetch GitHub star counts for tracked repositories"

  files_created:
    - src/connectors/github/stars.py
    - tests/connectors/test_github_stars.py

  files_modified:
    - src/connectors/registry.py    # add new connector to registry

  files_not_touched:
    - src/connectors/gitlab/        # unrelated connector
    - src/core/                     # core module not in scope

  must_include:
    - "pagination handling for repos with >100 stars"
    - "authentication via GitHub token (not hardcoded)"
    - "rate limit detection and backoff"
    - "structured logging with connector name in context"

  must_not_include:
    - "GraphQL API usage (use REST API for consistency with existing connectors)"
    - "caching layer (out of scope for this task)"

  automated_checks:
    tests_pass: true
    lint: clean
    coverage_threshold: 80
```

### Step 2: Share the contract with the agent

Include the contract in the session prompt or reference it from CLAUDE.md:

```
Task: Create GitHub stars connector
Contract: See SPRINT_CONTRACTS.md, contract "github-stars-connector"
Instruction: Implement according to the contract. Report any contract items you cannot fulfill before proceeding.
```

### Step 3: Agent reports contract compliance

At the end of the session, the agent produces a compliance report:

```yaml
contract_compliance:
  name: "github-stars-connector"
  status: "complete"

  files_created:
    - src/connectors/github/stars.py        # DONE
    - tests/connectors/test_github_stars.py  # DONE

  files_modified:
    - src/connectors/registry.py            # DONE - added GithubStarsConnector entry

  must_include_status:
    - "pagination handling": DONE            # handles Link header pagination
    - "authentication via token": DONE       # reads from GITHUB_TOKEN env var
    - "rate limit detection": DONE           # checks X-RateLimit-Remaining header
    - "structured logging": DONE             # uses logging module with connector context

  must_not_include_status:
    - "GraphQL API usage": VERIFIED          # uses REST API exclusively
    - "caching layer": VERIFIED              # no caching implemented

  automated_checks:
    tests_pass: PASS (14/14)
    lint: PASS
    coverage: 84% (above 80% threshold)

  deviations: none
  confidence: 88%
```

### Step 4: Validate the compliance report

The human (or reviewing agent) checks:

1. Does the compliance report match the actual output? (Agent compliance reports can be wrong.)
2. Are there files modified that are not in the contract?
3. Do the automated checks actually pass when you run them?
4. Are the "must not include" items genuinely absent?

### Step 5: Handle contract deviations

When the agent cannot fulfill a contract item, it must report the deviation before proceeding:

```yaml
deviation:
  contract_item: "pagination handling for repos with >100 stars"
  status: "partial"
  reason: "GitHub REST API uses cursor-based pagination for the Stargazers endpoint, not page-based. Implemented cursor pagination instead of page-number pagination."
  impact: "Functionally equivalent. Interface matches contract. Implementation detail differs."
  action_needed: "none — cursor pagination is the correct approach for this endpoint"
```

Deviations are acceptable when justified. Undisclosed deviations are not.

## Example

A team is building a data pipeline. The sprint includes a task to add an Oura Ring sleep data connector. Without an output contract, the agent might:

- Create the connector (correct)
- Also refactor the base connector class "while it was in there" (scope creep)
- Add a caching layer "for performance" (not requested)
- Modify the test configuration to support the new connector's test fixtures (unexpected side effect)
- Skip rate limit handling because the Oura API docs do not prominently feature rate limits (missing requirement)

With an output contract specifying files_created, files_modified, files_not_touched, must_include (rate limit handling), and must_not_include (caching layer), every one of these deviations is caught at review time. The contract makes the review mechanical: check each item, verify compliance, flag deviations.

The review takes 5 minutes instead of 30 because the reviewer is checking a list, not reading every line of code and deciding whether it "looks right."

## Evidence

Output contracts apply the principle of design-by-contract (Bertrand Meyer, 1986) to AI agent sessions. The core insight — that specifying preconditions, postconditions, and invariants catches more errors than testing alone — has been validated across decades of software engineering practice.

In the context of AI agents, contracts are especially valuable because they constrain the agent's tendency to expand scope. An agent without constraints will optimize for completeness: adding features, refactoring adjacent code, and improving things that were not broken. A contract channels that energy into the defined scope.

Teams using output contracts report a measurable reduction in scope creep (fewer files modified outside the task boundary) and faster review cycles (reviewers check a list instead of reading everything).

## Related Patterns

- [Dual-Model Validation](dual-model-validation.md) — the reviewing model checks against the contract
- [Blast Radius Control](blast-radius-control.md) — contracts define the blast radius for a specific task
- [Semantic Verification](semantic-verification.md) — contracts define WHAT to verify; semantic verification defines HOW
- [Context Boundaries](context-boundaries.md) — contracts limit output scope; context boundaries limit input scope
- [Quality Control Patterns](../docs/quality-control-patterns.md) — how contracts fit the quality control stack
