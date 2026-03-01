# Mutation Testing Guide for AI-Generated Code

## Why Mutation Testing Matters

AI agents write tests that verify the code they just produced. This creates a structural risk: **tautological testing**. The test validates what was built, not what was specified. If the agent introduces a logic error, the test is likely written to match that error.

Traditional code coverage tells you which lines were executed. It does not tell you whether the tests would catch a bug. A test suite can achieve 100% coverage and still miss critical defects if the assertions are weak or tautological.

Mutation testing answers a harder question: **if the code changed, would the tests notice?**

## How Mutation Testing Works

A mutation testing tool:

1. Parses the source code
2. Applies small, systematic changes (mutations) — e.g., replacing `>` with `>=`, changing `True` to `False`, removing a return statement
3. Runs the test suite against each mutated version
4. Records whether the tests caught the mutation (killed it) or missed it (it survived)

If a mutation survives, it means the tests do not verify that specific behavior. Surviving mutants reveal gaps in test quality that coverage metrics miss entirely.

## Setup

Install mutmut (Python mutation testing):

```bash
pip install mutmut
```

For projects using a virtual environment:

```bash
pip install mutmut pytest
```

### Configuration

Create a `mutmut-config.toml` (or add to `pyproject.toml`):

```toml
[tool.mutmut]
paths_to_mutate = "src/"
tests_dir = "tests/"
runner = "python -m pytest -x --tb=short"
dict_synonyms = "Struct, NamedStruct"
```

Key settings:

| Setting | Purpose |
|---------|---------|
| `paths_to_mutate` | Source directories to mutate (comma-separated) |
| `tests_dir` | Where tests live |
| `runner` | Test command — `-x` stops at first failure for speed |
| `dict_synonyms` | Custom dict-like types that mutmut should treat as dicts |

For monorepo or multi-package setups, scope mutations to the package under test:

```toml
[tool.mutmut]
paths_to_mutate = "packages/core/src/"
tests_dir = "packages/core/tests/"
runner = "python -m pytest packages/core/tests/ -x --tb=short"
```

## Running Mutation Tests

### Full Run

```bash
mutmut run
```

This takes significantly longer than regular tests (minutes to hours depending on codebase size). Each mutation triggers a full test run.

### View Results

```bash
# Summary
mutmut results

# Detailed HTML report
mutmut html
open html/index.html

# Show a specific surviving mutant
mutmut show 42
```

### Run Against Specific Files

```bash
mutmut run --paths-to-mutate "src/auth.py"
```

## Interpreting Results

| Status | Meaning | Action |
|--------|---------|--------|
| **Killed** | Tests caught the mutation | Good. The tests verify this behavior. |
| **Survived** | Tests did not detect the change | Bad. Add or strengthen assertions. |
| **Timeout** | Mutation caused an infinite loop or excessive runtime | Usually harmless — the mutation broke a loop condition. Review if frequent. |
| **Suspicious** | Test result was ambiguous | Investigate manually. May indicate flaky tests. |

### Mutation Score

```
mutation_score = killed / (killed + survived) * 100
```

### Quality Thresholds

| Score | Assessment |
|-------|-----------|
| 90%+ | Excellent — tests are strong |
| 80-89% | Acceptable for production — minimum target |
| 60-79% | Significant gaps — AI-generated tests likely need manual review |
| <60% | Tests provide false confidence — do not trust coverage numbers |

**Minimum target for production code: 80% mutation score.**

For critical paths (authentication, payment processing, data integrity), target 90%+.

## CI/CD Integration

### GitHub Actions

```yaml
name: Mutation Testing
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"

jobs:
  mutation-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install mutmut

      - name: Run mutation tests
        run: |
          mutmut run --no-progress 2>&1 | tee mutmut-output.txt
          SCORE=$(mutmut results 2>&1 | grep -oP 'Mutation score: \K[0-9]+')
          echo "Mutation score: ${SCORE}%"
          if [ "$SCORE" -lt 80 ]; then
            echo "Mutation score ${SCORE}% is below 80% threshold"
            exit 1
          fi

      - name: Upload mutation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: mutation-report
          path: .mutmut-cache/
```

### Pre-Merge Gate

Add mutation testing as a required check in branch protection rules. This prevents AI-generated code with weak tests from merging.

## Workflow for AI-Generated Code

When an AI agent generates both code and tests in a session:

1. **Run standard tests first** — Verify everything passes
2. **Run mutation tests on the new code** — `mutmut run --paths-to-mutate "src/new_module.py"`
3. **Review surviving mutants** — Each survivor is a behavior the tests do not verify
4. **Strengthen tests manually or re-prompt the agent** — Ask the agent to add assertions for the specific behaviors the mutants revealed
5. **Re-run mutation tests** — Confirm the score meets the 80% threshold

This workflow catches the most common AI testing failure: tests that exercise code paths without actually verifying correctness.

## Common Mutation Types and What They Reveal

| Mutation | Example | What Surviving Reveals |
|----------|---------|----------------------|
| Boundary | `>` to `>=` | Off-by-one errors not tested |
| Negation | `True` to `False` | Boolean logic not verified |
| Return value | `return x` to `return None` | Return value not asserted |
| Arithmetic | `+` to `-` | Calculation results not checked |
| Remove statement | Delete a line | Side effects not verified |
| Constant | `0` to `1` | Magic numbers not boundary-tested |

## Limitations

- **Speed**: Mutation testing is slow. Run it on changed files only, not the entire codebase on every PR.
- **Equivalent mutants**: Some mutations produce functionally identical code. These are false negatives that inflate the denominator. Manual review is needed for borderline cases.
- **Test isolation**: Mutations can interact with shared state. Ensure tests are properly isolated.
- **Language support**: mutmut supports Python. For other languages, see [pitest](https://pitest.org/) (Java), [Stryker](https://stryker-mutator.io/) (JavaScript/TypeScript), or [cargo-mutants](https://github.com/sourcefrog/cargo-mutants) (Rust).
