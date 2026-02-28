# ADR-002: Core Governance Scripts Use Only Python Standard Library

## Status

Accepted

## Date

2026-02-28

## Context

The framework ships six automation scripts in `automation/` and two in `scripts/`. These scripts perform governance enforcement: calculating health scores, checking ADR coverage, validating inheritance chains, counting context tokens, and generating compliance dashboards. Several of these scripts run as CI gates — they block merges when governance standards are not met.

A governance gate that fails to execute is not a governance gate. It is an infrastructure failure. When `pip install` fails because of a dependency version conflict, a missing build tool, a PyPI outage, or a restricted network policy, the governance check silently disappears from the CI pipeline. The merge proceeds. The governance violation goes undetected. This failure mode is uniquely dangerous for governance tooling: unlike an application dependency failure (which produces a visible runtime error), a failed CI gate produces a green pipeline — the exact signal that tells developers their code is acceptable.

The framework's own rules compound this concern. The governance scripts are meant to run in the repositories they govern, which may be application repositories with complex existing dependency trees. Introducing `requests==2.31.0` as a required dependency of the governance framework may conflict with `requests==2.28.1` pinned by the application. The governance framework would be introducing dependency conflicts into every repository it governs — an ironic failure mode for tooling that is supposed to reduce risk.

Python 3.10+ (the minimum version required by the framework) provides a standard library that covers all core governance needs: `pathlib` for file operations, `json` for structured output, `re` for pattern matching in CLAUDE.md files, `subprocess` for invoking git, `argparse` for CLI interfaces, `urllib.request` for HTTP fetching in optional URL-mode validation, and `datetime` for timestamp handling. The standard library is sufficient.

The `requests` library is used in exactly two optional features: the URL-fetching mode of `inherits_from_validator.py` (see ADR-001) and the external best-practice scanner in `best_practice_scanner.py`. Both features are optional — the scripts function without `requests` and raise a clear `ImportError` message directing the user to install it.

## Decision

All core governance scripts use only the Python 3.10+ standard library. A script is classified as core governance if it can block a CI pipeline or is required to produce the governance health score. External libraries are permitted only for optional features, and scripts with optional external dependencies must handle `ImportError` gracefully and document the requirement in their module docstring. The `requests` library is listed in `requirements-dev.txt` for test-only use and is not a runtime requirement of any core script.

## Rationale

Governance enforcement must be reliable before it can be useful. Reliability in a CI environment means: the script runs with only what is guaranteed to be present — a Python interpreter. The standard library is guaranteed by the Python version constraint already declared in the framework. Nothing else is.

The constraint also serves a secondary purpose: it limits complexity. A governance script that requires `langchain`, `anthropic`, or `numpy` has accumulated feature scope that belongs in application code, not governance tooling. The standard library constraint acts as an architectural forcing function. If a proposed feature cannot be implemented with the standard library, it is a signal that the feature is too complex for core governance and belongs in an optional extension, a separate tool, or out of scope entirely.

Auditability is a third consideration. A governance script that imports a dozen external packages requires the auditor to review the transitive dependency tree to confirm the script is not exfiltrating data, injecting code, or bypassing security controls. A script with zero external imports is fully auditable by reading the source file. Organizations with security reviews for third-party dependencies can adopt the framework without triggering that review process.

## Consequences

### Positive

- Core governance scripts run with `python3 script.py` immediately in any environment with Python 3.10+. No `pip install` step. No virtual environment setup. No dependency resolution.
- No dependency conflicts with application code. The framework introduces zero packages into the application's dependency tree.
- Scripts are fully auditable by reading the source. Security teams can review governance tooling without resolving a dependency graph.
- CI governance gates cannot fail due to package installation issues. If Python 3.10+ is present and the script file is present, the gate runs.
- The constraint enforces simplicity. Governance scripts remain short, readable, and maintainable.

### Negative

- Standard library limitations require more code for some operations. Fetching a URL with `urllib.request` requires explicit error handling, response decoding, and timeout management that `requests` handles with a single method call. This is approximately 8–12 lines of code per network call instead of 1–2 lines.
- Features that genuinely require external libraries — AI-powered semantic analysis, vector similarity for duplicate detection, integration with external governance platforms — are out of scope for core governance. Teams that want these capabilities must build them as separate tools that call the framework scripts, not as additions to the framework itself.
- Developers contributing to the framework must be disciplined about not adding `import` statements for external libraries to core scripts. This must be caught in code review; there is no automated enforcement beyond the test suite running with no external packages installed.

### Neutral

- A two-tier architecture emerges: core scripts (stdlib only, can block CI) and optional scripts (may require external packages, cannot block CI). This distinction must be documented and maintained as new scripts are added.
- `requirements-dev.txt` exists for test dependencies (`pytest`, `pytest-cov`) and optional feature development. It is explicitly not a runtime requirements file. The naming distinction must be communicated to contributors.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Use `requests` throughout all scripts | Makes `pip install requests` a requirement for any CI pipeline using the framework. Introduces a runtime dependency that can conflict with application code. Breaks the zero-setup guarantee. |
| Use a dependency manager (poetry, pipenv) for the framework scripts | Over-engineering for single-purpose, single-file governance scripts. Adds tooling requirements on top of tooling requirements. A developer who wants to run a health check should not need to install poetry first. |
| Compile scripts to self-contained binaries | Removes the auditability property. A binary cannot be reviewed for security without specialized tooling. Defeats the stated goal of readable, auditable governance code. Also requires platform-specific builds and distribution infrastructure. |
| Require Python 3.12+ to access newer stdlib features | Narrows the addressable environment unnecessarily. Python 3.10 is the LTS baseline for most enterprise Linux distributions active as of this ADR's date. The standard library features available in 3.10 are sufficient for all current governance needs. |

## Implementation Notes

The test suite enforces this constraint by running core script tests in an environment where only the standard library is available. Any import of an external package in a core script will cause a test failure. This check is implemented in `tests/test_no_external_deps.py`, which imports each core script and verifies that no `ImportError` is raised and that no non-stdlib module appears in `sys.modules` after import.

Scripts with optional external dependencies follow this pattern at the top of the file:

```python
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
```

Functions that require `requests` check `REQUESTS_AVAILABLE` and raise a `RuntimeError` with a specific installation message if the library is not present. They do not silently degrade or return empty results.

## Review Date

