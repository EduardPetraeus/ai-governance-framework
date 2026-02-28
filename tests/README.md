# Tests

The test suite verifies that the framework is internally consistent and that its automation scripts behave correctly. It covers naming conventions, cross-reference integrity, template completeness, automation script logic, example file validity, and governance self-compliance. The goal is that a freshly cloned repo can be validated end-to-end without manual inspection.

Total: 273 tests across 13 test files.

## Running Tests

Install test dependencies:

```
pip install -r requirements-dev.txt
```

Run the full suite:

```
python3 -m pytest tests/
```

Run with coverage report:

```
python3 -m pytest tests/ --cov=automation --cov=scripts --cov-report=term-missing
```

Run a single test file with verbose output:

```
python3 -m pytest tests/test_conventions.py -v
```

Run the CI-equivalent check (fails if coverage drops below 80%):

```
python3 -m pytest tests/ --cov=automation --cov=scripts --cov-fail-under=80
```

## Test File Inventory

| File | What it tests |
|---|---|
| `conftest.py` | Shared fixtures; inserts `automation/` and `scripts/` onto `sys.path` so all test files can import modules directly |
| `test_adr_coverage_checker.py` | `automation/adr_coverage_checker.py` — ADR discovery, coverage calculation, and reporting |
| `test_ai_security_review.py` | `scripts/ai_security_review.py` — Secret pattern detection, PII scanning, and output format |
| `test_best_practice_scanner.py` | `automation/best_practice_scanner.py` — Rule loading, file scanning, and violation reporting |
| `test_conventions.py` | All repo files follow naming conventions: `.md` files in kebab-case, `.py` files in snake_case, directories in kebab-case |
| `test_cross_references.py` | Every relative link in every `.md` file resolves to a file that exists on disk |
| `test_examples.py` | Example CLAUDE.md files in `examples/` have all required governance sections |
| `test_framework_updater.py` | `automation/framework_updater.py` — Update detection, diff generation, and apply logic |
| `test_governance_check.py` | The repo itself passes its own governance checks; the framework governs itself |
| `test_health_score_calculator.py` | `automation/health_score_calculator.py` — All 15 scoring checks, level thresholds, and edge cases |
| `test_inherits_from_validator.py` | `automation/inherits_from_validator.py` — Inheritance chain resolution and conflict detection |
| `test_templates.py` | All templates in `templates/` start with a `#` heading and contain real, non-placeholder content |
| `test_token_counter.py` | `automation/token_counter.py` — Token estimation accuracy and per-file breakdown |

## What Is Tested

- Naming conventions for all `.md`, `.py`, and directory names across the entire repository
- Resolution of every relative link in every Markdown file to a real file on disk
- That every template starts with a heading and contains no placeholder text
- Correctness of all six automation scripts in `automation/` and both scripts in `scripts/`
- That example CLAUDE.md files in `examples/` satisfy the required section structure
- That the repository itself passes its own governance health checks
- That the security reviewer correctly identifies secrets, tokens, and PII patterns

## What Is Not Tested

- Agent definitions are not executed; their YAML/Markdown structure is checked but agent behavior is not simulated
- CI workflow files in `.github/workflows/` and `ci-cd/` are validated as syntactically correct YAML but are not executed
- Documentation content is checked for structural requirements (headings, no placeholders) but not for factual accuracy

## Adding Tests

To add tests for a new automation script placed in `automation/`:

1. Create `tests/test_<script_name>.py` following the snake_case naming convention.
2. Import the module directly — `conftest.py` already adds `automation/` to `sys.path`, so `import <script_name>` works without path manipulation.
3. Use the fixtures defined in `conftest.py` (such as `tmp_path` and repo root helpers) rather than hardcoding paths.
4. Aim for coverage of the main entry point, each major function, and at least one error/edge-case path.
5. Run `python3 -m pytest tests/test_<script_name>.py -v` locally before opening a pull request.
