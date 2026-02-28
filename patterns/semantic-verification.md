# Pattern: Semantic Verification

## Problem

Automated tests verify that code runs. They do not verify that it does the right thing. An agent can write code that passes all tests but implements the wrong business logic. This gap between "tests pass" and "correct behavior" is where the most expensive bugs live.

The problem compounds when the agent writes both the implementation and the tests. The tests validate the implementation the agent built, not the implementation the human intended. If the agent misunderstands the requirement, both the code and the tests will be consistently wrong — and consistently green.

A concrete example: a task requires calculating average sleep duration per week. The agent implements a function that sums daily sleep durations and divides by 7. The tests confirm this calculation. But the requirement meant "average across days with recorded sleep data" — not all 7 days. A user who did not wear their tracker on Sunday gets their weekly average diluted by a zero-value day. Tests pass. Behavior is wrong.

## Solution

Verify meaning before trusting tests. Define expected behaviors in business language, then trace those behaviors through implementation. Use four complementary techniques.

### Technique 1: Assertion-Based Verification

Define assertions about system state BEFORE coding begins. These assertions describe what must be true after the code runs, in terms the business understands.

```python
# Assertions defined before implementation
# These are acceptance criteria, not unit tests

# After processing one week of sleep data for user A:
assert count_rows(user="A", week="2026-W09") == days_with_data  # NOT always 7
assert all(row.timezone == "UTC" for row in get_rows(user="A", week="2026-W09"))
assert weekly_average(user="A", week="2026-W09") == sum(daily_durations) / days_with_data
assert no_duplicate_entries(user="A", week="2026-W09")

# After processing a week where the user had no data:
assert count_rows(user="B", week="2026-W09") == 0  # no phantom rows
assert weekly_average(user="B", week="2026-W09") is None  # not zero
```

The key: these assertions are written by the human based on their understanding of the requirement, not by the agent based on its understanding of the code. The agent's code must satisfy assertions it did not write.

### Technique 2: Example-Based Verification

Provide 3-5 concrete input/output pairs before the agent begins. The agent must produce code that handles ALL examples correctly. Choose examples that exercise edge cases, not just happy paths.

```yaml
verification_examples:
  - name: "normal week with 7 days of data"
    input:
      user: "user_001"
      dates: ["2026-02-22", "2026-02-23", "2026-02-24", "2026-02-25", "2026-02-26", "2026-02-27", "2026-02-28"]
      durations_minutes: [480, 420, 390, 450, 510, 540, 470]
    expected_output:
      weekly_average_minutes: 465.7  # sum / 7
      days_recorded: 7

  - name: "week with missing days"
    input:
      user: "user_001"
      dates: ["2026-02-22", "2026-02-24", "2026-02-26", "2026-02-28"]
      durations_minutes: [480, 390, 510, 470]
    expected_output:
      weekly_average_minutes: 462.5  # sum / 4, NOT sum / 7
      days_recorded: 4

  - name: "week with no data"
    input:
      user: "user_001"
      dates: []
      durations_minutes: []
    expected_output:
      weekly_average_minutes: null  # NOT zero
      days_recorded: 0

  - name: "week with zero-duration entry (tracker malfunction)"
    input:
      user: "user_001"
      dates: ["2026-02-22"]
      durations_minutes: [0]
    expected_output:
      weekly_average_minutes: 0  # zero is valid when explicitly recorded
      days_recorded: 1

  - name: "duplicate entries for same day"
    input:
      user: "user_001"
      dates: ["2026-02-22", "2026-02-22"]
      durations_minutes: [480, 490]
    expected_output:
      error: "duplicate entries for user_001 on 2026-02-22"
```

Example 2 is the one that catches the "divide by 7" bug. Example 3 catches the "return 0 instead of null" bug. Example 5 catches the "silently average duplicates" bug. Easy examples catch nothing.

### Technique 3: Invariant-Based Verification

Define what must ALWAYS be true, regardless of input. Run invariant checks after every batch of agent work.

```python
# Invariants — must hold after every processing run

def verify_invariants(db):
    """Run after every agent session that modifies data processing code."""

    # No duplicate records
    assert db.query("""
        SELECT user_id, date, COUNT(*)
        FROM sleep_data
        GROUP BY user_id, date
        HAVING COUNT(*) > 1
    """).count() == 0, "Duplicate records detected"

    # All timestamps in UTC
    assert db.query("""
        SELECT COUNT(*)
        FROM sleep_data
        WHERE timezone != 'UTC'
    """).scalar() == 0, "Non-UTC timestamps detected"

    # All durations non-negative
    assert db.query("""
        SELECT COUNT(*)
        FROM sleep_data
        WHERE duration_minutes < 0
    """).scalar() == 0, "Negative duration detected"

    # No NULL in required fields
    for column in ["user_id", "date", "duration_minutes", "timezone"]:
        assert db.query(f"""
            SELECT COUNT(*)
            FROM sleep_data
            WHERE {column} IS NULL
        """).scalar() == 0, f"NULL found in required column: {column}"

    # Weekly averages match underlying data
    averages = db.query("""
        SELECT user_id, week, avg_duration, days_recorded
        FROM weekly_averages
    """)
    for row in averages:
        actual_days = db.query(f"""
            SELECT COUNT(*)
            FROM sleep_data
            WHERE user_id = '{row.user_id}'
            AND week = '{row.week}'
        """).scalar()
        assert row.days_recorded == actual_days, \
            f"days_recorded mismatch for {row.user_id} week {row.week}"
```

Invariants are the most maintainable form of semantic verification because they do not change when requirements change. "No duplicates" and "all timestamps in UTC" are true regardless of what features are added.

### Technique 4: Negative Testing

Define what must NEVER happen. Encode these as assertions that fail if the forbidden behavior occurs.

```python
# Negative tests — these must never pass

def test_never_deletes_existing_records(before_snapshot, after_snapshot):
    """Agent work must never reduce the row count of existing tables."""
    for table in before_snapshot:
        assert after_snapshot[table].count >= before_snapshot[table].count, \
            f"Records deleted from {table}: {before_snapshot[table].count} → {after_snapshot[table].count}"

def test_never_modifies_config_outside_section(git_diff):
    """Changes to config files must be limited to the designated section."""
    for change in git_diff.files:
        if change.path.endswith("config.yaml"):
            for hunk in change.hunks:
                assert hunk.section in ALLOWED_CONFIG_SECTIONS, \
                    f"Config modified outside allowed sections: {hunk.section}"

def test_never_reduces_coverage(before_coverage, after_coverage):
    """Test coverage must not decrease after agent work."""
    assert after_coverage >= before_coverage, \
        f"Coverage decreased: {before_coverage}% → {after_coverage}%"

def test_never_introduces_circular_dependencies(module_graph):
    """No circular dependencies between modules."""
    cycles = find_cycles(module_graph)
    assert len(cycles) == 0, f"Circular dependencies found: {cycles}"
```

## When to Use

- Any task where "tests pass" is an insufficient quality signal
- Tasks where the agent writes both implementation and tests
- Data processing pipelines where correctness depends on business rules
- Integrations where the API behavior has edge cases not covered in documentation
- Any task where a subtle logic error would go undetected for weeks

## When NOT to Use

- Pure infrastructure tasks (deploy scripts, CI configuration) where behavior is binary: it works or it does not
- Formatting and documentation tasks where semantic correctness is not applicable
- Exploratory prototypes where correctness is not yet defined

## Implementation

### Step 1: Write semantic checks before the agent session

Before the agent begins, the human defines:
- 3-5 assertion-based checks (business-level postconditions)
- 3-5 example input/output pairs (including edge cases)
- A set of invariants (always-true properties)
- A set of negative tests (never-true properties)

### Step 2: Share checks with the agent

Include the semantic checks in the session prompt. The agent's implementation must satisfy all checks. If a check seems wrong, the agent must flag it rather than silently ignore it.

### Step 3: Run semantic checks after the session

Execute assertion checks, run example pairs through the implementation, verify invariants, and confirm negative tests do not trigger. This is in addition to the agent's own test suite.

### Step 4: Add checks to CI/CD

Invariants and negative tests are stable enough to run in CI/CD. Add them to the pipeline so they run on every PR. Assertion-based and example-based checks may be task-specific and can be added as PR-specific test cases.

### Step 5: Update checks as requirements evolve

When requirements change, update the semantic checks first, then update the code. If the checks are updated after the code, they are not verifying the requirement — they are documenting the implementation.

## Example

A team is building an ETL pipeline that aggregates health data from wearable APIs. The current sprint includes a task to add weekly sleep aggregation.

The developer writes semantic checks before the agent session:

**Assertions:** "Weekly average is sum of daily durations divided by the count of days with data, not by 7. A week with no data returns null, not zero."

**Examples:** Five input/output pairs including normal weeks, weeks with missing days, weeks with no data, zero-duration entries, and duplicate entries.

**Invariants:** No duplicate user-date pairs. All timestamps in UTC. All durations non-negative.

**Negative tests:** Never delete existing records. Never reduce test coverage.

The agent session produces an implementation and test suite. All agent tests pass. Then the developer runs the semantic checks:

- The assertion about "divide by days with data, not by 7" fails. The agent divided by 7.
- Example 2 (week with missing days) fails. Confirms the same bug.
- Example 3 (week with no data) fails. Agent returns 0 instead of null.
- Invariants pass.
- Negative tests pass.

The developer sends the agent back with the failed checks. The agent fixes the implementation. All semantic checks now pass. The fix took 5 minutes. Without semantic verification, this bug would have reached production and silently produced incorrect averages for every user who did not wear their tracker every day.

## Evidence

Semantic verification applies the principles of property-based testing and design-by-contract to AI agent output. Property-based testing (popularized by QuickCheck in Haskell and Hypothesis in Python) has a strong track record of finding edge-case bugs that example-based tests miss.

The specific value for AI agents is that semantic checks are written by a human who understands the requirement, while the implementation is written by an agent that understands the code. This separation of concerns catches the exact class of bugs where the agent's understanding of the requirement differs from the human's intent.

Invariant-based verification is particularly effective because invariants are requirement-independent. "No duplicate records" is true regardless of what features are added. This makes invariants a stable investment that compounds in value over the life of the project.

## Related Patterns

- [Output Contracts](output-contracts.md) — contracts define WHAT to verify; semantic verification defines HOW
- [Dual-Model Validation](dual-model-validation.md) — a complementary check that focuses on code quality rather than business correctness
- [Progressive Trust](progressive-trust.md) — semantic verification requirements can be relaxed at higher trust levels
- [Blast Radius Control](blast-radius-control.md) — invariant checks catch unintended side effects outside the blast radius
- [Quality Control Patterns](../docs/quality-control-patterns.md) — semantic verification is part of Layer 2 (automated) and Layer 3 (AI cross-validation) of the quality stack
