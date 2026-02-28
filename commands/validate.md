# /validate

Run quality control on the last completed task or the entire current session. This command answers: "Is what I just built actually good enough to commit?"

Use `/validate` as a checkpoint during and after work. It catches issues that individual checks miss by evaluating the aggregate: security, contracts, tests, architecture alignment, and naming conventions in one pass.

## Steps

### Step 1: Identify what changed

Run `git diff --stat HEAD` to get the list of changed files and line counts since the last commit.

If there are no uncommitted changes, compare against the previous commit: `git diff --stat HEAD~1`.

If the user specifies a range (e.g., "validate the last 3 commits"), use `git diff --stat HEAD~3..HEAD`.

Count total files changed and approximate lines changed.

### Step 2: Run security scan

Read CLAUDE.md and extract the `never_commit` or `security_protocol` patterns.

Scan every changed file for:
- Hardcoded API keys, tokens, passwords, secrets (patterns: `_key =`, `_token =`, `secret`, `password =`, `sk_live_`, `sk-ant-`, `ghp_`, `AKIA`)
- Connection strings with embedded credentials (`://user:pass@host`)
- Private keys (`-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN OPENSSH PRIVATE KEY-----`)
- .env files or their contents in the diff
- PII: real email addresses, phone numbers, national identifiers in source code
- Any patterns listed in CLAUDE.md's forbidden list

Report: number of issues found, severity (FAIL for secrets/PII, WARN for configuration concerns).

### Step 3: Check output contract

Read PROJECT_PLAN.md. Find the task that was just completed (or is in progress). Check whether an output contract was defined for this task -- either in the task description, in a linked pattern from [patterns/output-contracts.md](../patterns/output-contracts.md), or in the session scope agreement.

If an output contract exists:
- Compare actual deliverables against specified deliverables
- Check that all specified files exist at the specified locations
- Check that output format matches specification
- Report: Met, Partial (with details on what is missing), or Not Met

If no output contract was defined:
- Report: "Not defined" with a recommendation to define one for the next task

### Step 4: Report test status

Check for a test runner configuration:
- `pytest.ini`, `pyproject.toml` with `[tool.pytest]`, `setup.cfg` with `[tool:pytest]` for Python
- `package.json` with a `test` script for JavaScript/TypeScript
- `Makefile` with a `test` target

If a test runner is found, run it and report:
- Total tests, passing, failing, skipped
- Whether any new test files were added in the current changes
- Whether changed source files have corresponding test files

If no test runner is configured:
- Report: "No test runner configured" with a recommendation

### Step 5: Check architecture alignment

Read ARCHITECTURE.md if it exists. For each new or moved file in the diff:
- Does the file live in the correct directory according to the documented structure?
- Does the file follow the project's established patterns (naming, structure, imports)?
- If a new directory was created, is it documented in ARCHITECTURE.md?
- If a new external dependency was added, is there an ADR or a note in ARCHITECTURE.md?

If ARCHITECTURE.md does not exist:
- Report: "No ARCHITECTURE.md found" and skip this check
- Recommend creating one if the project has more than 10 source files

### Step 6: Check naming conventions

Read CLAUDE.md conventions section. For each new or renamed file, function, class, variable, and constant in the diff:
- Does the name follow the documented convention?
- File names: check against specified case convention (snake_case, kebab-case, PascalCase)
- Directory names: check against specified convention
- Function/variable names: check against language conventions plus project-specific rules
- Commit messages: check the most recent commit message against the documented format

Report specific violations with file paths and the rule violated.

### Step 7: Calculate quality score and produce report

Score calculation:
- Start at 100
- Each security FAIL finding: -25
- Each output contract gap: -15
- Each test failure: -10
- Each architecture misalignment: -10
- Each naming violation: -5
- No test runner configured: -5
- No ARCHITECTURE.md: -3

Minimum score: 0.

Determine recommendation:
- 90-100: CONTINUE
- 70-89: REVIEW BEFORE PROCEEDING
- Below 70: STOP AND FIX

## Output Format

```
/validate Report
================
Session: [session number from CHANGELOG.md, or "current"]
Checkpoint: [current timestamp]
Changes since last checkpoint: [N files, ~N lines]

Security: [result]
Output contract: [result]
Tests: [result]
Architecture: [result]
Naming: [result]

Quality Score: [0-100]
Recommendation: [CONTINUE | REVIEW BEFORE PROCEEDING | STOP AND FIX]

Issues requiring action:
1. [issue]: [specific fix]
2. [issue]: [specific fix]

Next recommended action: [what to do now]
```

Use these status indicators:
- Pass: "Clean (0 issues)"
- Partial: specific description of what passed and what did not
- Fail: specific description of failures with file paths and line numbers

## Rules

- Never skip the security scan. Even if the user says "just check naming," run security first. A missed secret is more expensive than any other finding.
- If any security FAIL is found, the recommendation is always STOP AND FIX regardless of the overall score.
- Run this command after every 3+ completed tasks during a session.
- Run this command before any commit that touches more than 5 files.
- Run this command after any change that touches architectural boundaries (new directories, new integrations, new dependencies).
- For deeper analysis beyond this quick check, invoke the [quality-gate-agent](../agents/quality-gate-agent.md) with the full file contents and task description.
- Keep the report under 40 lines for quick scanning. If there are more than 5 issues, summarize and recommend running the quality gate agent for the full assessment.

---

## Example Output

```
/validate Report
================
Session: 014
Checkpoint: 2026-02-28 14:23
Changes since last checkpoint: 4 files, ~185 lines

Security: Clean (0 issues)
Output contract: Met (connector + tests + ARCHITECTURE.md update delivered as specified)
Tests: 12/12 passing (4 new tests added for HubSpot connector)
Architecture: Aligned (new connector follows existing pattern in src/connectors/)
Naming: Conventions followed (all files snake_case, commit message follows type: description)

Quality Score: 100
Recommendation: CONTINUE

Issues requiring action:
(none)

Next recommended action: Commit changes and proceed to the next task (silver transform
for Shopify orders).
```

### Example with issues

```
/validate Report
================
Session: 015
Checkpoint: 2026-02-28 16:45
Changes since last checkpoint: 6 files, ~320 lines

Security: FAIL (1 issue)
  - src/connectors/payment.py:8 -- Stripe API key hardcoded: sk_live_abc123...
    Fix: Move to environment variable. Use os.environ["STRIPE_API_KEY"].
Output contract: Partial -- missing integration test for error handling path
Tests: 8/10 passing (2 failing: test_rate_limit, test_timeout)
Architecture: Aligned
Naming: 1 violation
  - src/connectors/PaymentProcessor.py -- should be payment_processor.py per
    CLAUDE.md snake_case convention

Quality Score: 30
Recommendation: STOP AND FIX

Issues requiring action:
1. SECURITY: Remove hardcoded Stripe key from src/connectors/payment.py:8.
   Move to environment variable immediately.
2. TESTS: Fix test_rate_limit and test_timeout failures before committing.
3. NAMING: Rename PaymentProcessor.py to payment_processor.py. Update all imports.
4. CONTRACT: Add integration test for the error handling path.

Next recommended action: Fix the hardcoded API key first (security), then fix
the failing tests, then rename the file.
```
