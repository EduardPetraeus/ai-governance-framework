# Command: /audit

Run an adversarial governance audit to test whether governance mechanisms actually catch
what they are supposed to catch.

## Usage

```
/audit                     # Full audit across all categories
/audit security            # Security scanning tests only
/audit compliance          # Compliance gate tests only
/audit quality             # Code quality and convention tests only
/audit architecture        # Architectural convention tests only
/audit scope               # Blast radius and scope control tests only
```

## What It Does

1. **Creates a temporary audit branch**: `audit/governance-test-YYYYMMDD`
   All tests run here. No changes to main or any feature branch.

2. **Invokes the red-team-auditor agent**: runs the test battery for the specified
   category (or all categories if unspecified).

3. **Attempts simulated violations**: for each test, the agent creates a minimal synthetic
   example designed to trigger the governance mechanism being tested.

4. **Records outcomes**: CAUGHT or MISSED for each test, with the specific mechanism
   (or absence of mechanism) responsible for the outcome.

5. **Produces structured report**: pass rate, specific gaps, prioritized recommendations.

6. **Cleans up**: deletes the `audit/governance-test-YYYYMMDD` branch.

7. **Logs results**: appends summary to CHANGELOG.md with date, category, pass rate,
   and count of gaps found.

## Output

```
🔴 Adversarial Audit — [category] — [YYYY-MM-DD]

Tests run: [N] | Caught: [N] | Missed: [N] | Pass rate: [N]%

PASSED:
✅ SEC-001: gitleaks caught fake API key in config.py
✅ COM-001: CI blocked PR without CHANGELOG update
[...]

FAILED (gaps):
❌ SEC-002: API key in Markdown file not caught by scanner
   Fix: add --include="*.md" to gitleaks scan configuration
❌ ARC-001: File placement in wrong layer not detected
   Fix: add file structure validation to governance-check.yml workflow

RECOMMENDATIONS (prioritized by risk):
1. [HIGH] Add Markdown to security scan scope
2. [MEDIUM] Implement file structure validation in CI

Audit branch deleted. Results logged to CHANGELOG.md.
```

## Safety Guarantees

- All tests use synthetic data: fake keys, example names, constructed patterns
- No real credentials, real PII, or real sensitive data used at any point
- Audit branch is deleted after the audit — no artifacts remain
- Tests are read-only for governance mechanisms (never modifies pre-commit hooks or CI configs)

## When to Run

- Monthly for active projects
- After every maturity level upgrade
- After adding any new governance mechanism (verify it works)
- Before enterprise rollout (demonstrate governance effectiveness to leadership)
- After any production incident that slipped through governance (add test for the gap)

## Prerequisites

- Git repository with at least Level 2 governance (CLAUDE.md, pre-commit hooks configured)
- GitHub Actions workflows configured (for compliance and quality gate tests)
- The red-team-auditor agent available in `agents/red-team-auditor.md`

## Related

- [agents/red-team-auditor.md](../agents/red-team-auditor.md) — agent that executes the audit
- [docs/adversarial-audit.md](../docs/adversarial-audit.md) — full specification
- [docs/security-guide.md](../docs/security-guide.md) — security mechanisms being tested
- [docs/maturity-model.md](../docs/maturity-model.md) — adversarial audit becomes available at Level 3
