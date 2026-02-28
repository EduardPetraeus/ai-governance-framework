# Adversarial Audit: Does Your Governance Actually Work?

## The Problem

You have built security scanning, pre-commit hooks, CI gates, and quality control agents.
But have you tested them? Do you know, with evidence, that gitleaks catches secrets in
your specific file types? Do you know that the governance file check blocks the PRs it is
supposed to block? Do you know that the AI reviewer flags the naming violations it is
configured to catch?

Most teams discover governance gaps when something goes wrong in production. An adversarial
audit discovers them before production — deliberately, in a controlled environment, before
the real cost is paid.

---

## What Adversarial Audit Is (and Is Not)

**It IS**: a structured test of governance mechanisms using simulated violations in a safe,
isolated environment. The goal is to find gaps so they can be fixed before something real
slips through.

**It IS NOT**: injecting real vulnerabilities into production code, social engineering team
members, or any activity that could cause actual harm. All tests run in a temporary branch
that is deleted at audit completion.

The red team agent is adversarial in methodology but constructive in purpose: find gaps,
report them precisely, propose fixes.

---

## Audit Categories

### Category 1: Security Audit

Tests whether security scanning catches what it claims to catch.

**Tests:**
- Plant a fake API key in a Python config file → does gitleaks catch it?
- Plant a fake API key in a Markdown file → is Markdown in scope for scanning?
- Add PII (name + email) in a code comment → does AI security review flag it?
- Add a hardcoded IP address to a YAML config → is this pattern in the scanner rules?
- Add a connection string with embedded credentials → does the credential pattern match?
- Add a base64-encoded fake token → does the scanner decode and check base64?
- Place a fake key in a test fixture file → are test files in scope?

**Expected outcome for each**: the governance mechanism catches it and blocks the commit
or flags the PR before merge.

**Gap finding**: any test that reaches a commit or PR merge without being caught is a gap
that needs an updated scanner rule or hook configuration.

### Category 2: Compliance Audit

Tests whether required processes are enforced.

**Tests:**
- Submit a PR that changes Python files but does not update CHANGELOG.md → does CI block it?
- Submit a PR that changes CLAUDE.md directly to main (no PR review) → is branch protection enforced?
- Submit a PR with no human approval → does the branch protection rule block merge?
- Complete a session without running the end-session protocol → does the next session detect the gap?
- Modify a critical architecture file without updating ARCHITECTURE.md → does governance sync flag it?

**Expected outcome for each**: the compliance gate blocks the action or flags the gap.

### Category 3: Quality Audit

Tests whether quality controls catch what they should catch.

**Tests:**
- Introduce an obvious off-by-one error in a loop → does the AI reviewer flag it?
- Write a function with a null pointer risk → does code review catch it?
- Name a file using camelCase instead of snake_case → does naming validation block it?
- Import a module with a wildcard import → does linting catch it?
- Remove a test that was previously passing → does CI fail appropriately?

**Expected outcome for each**: the quality mechanism catches the issue before merge.

### Category 4: Architecture Audit

Tests whether architectural conventions are enforced.

**Tests:**
- Create a file in the wrong directory (wrong layer) → does governance sync detect it?
- Use a database connection pattern not specified in ARCHITECTURE.md → does the master agent flag it?
- Add a new dependency without documenting it → does the governance check flag it?
- Violate a naming prefix convention (e.g., missing layer prefix) → does the convention validator catch it?

**Expected outcome for each**: the architecture check flags the deviation.

### Category 5: Scope Audit

Tests whether blast radius and scope controls work.

**Tests:**
- Modify 25 files in a single session → does the blast radius control flag it?
- Modify a file explicitly marked as out-of-scope for the session → does CLAUDE.md prevent it?
- Make a cross-layer change in one session → does governance require confirmation?
- Attempt to merge a feature that was not in the session scope → does task-to-goal mapping surface the discrepancy?

**Expected outcome for each**: the scope control catches the overreach.

---

## The /audit Command

Running `/audit` or `/audit [category]` executes the adversarial audit:

1. **Create temporary branch**: `audit/governance-test-YYYYMMDD`
2. **Invoke red-team-auditor agent** with the specified category (or all categories if unspecified)
3. **Run test battery**: agent attempts each simulated violation and records the result
4. **Record outcomes**: CAUGHT or MISSED for each test, with specific mechanism that caught it
5. **Produce structured report**: pass rate, specific gaps, prioritized recommendations
6. **Clean up**: delete the `audit/governance-test-YYYYMMDD` branch
7. **Log results**: append to CHANGELOG.md with date and audit summary

---

## Audit Report Format

```
🔴 Adversarial Audit Report — YYYY-MM-DD
Category: [security | compliance | quality | architecture | scope | all]

Tests run: [N]
Caught: [N]
Missed: [N]
Pass rate: [N]%

PASSED:
✅ [mechanism]: [description of what was caught and how]
✅ [mechanism]: [description]
[...list all passing tests]

FAILED:
❌ [mechanism]: [description of what was not caught]
   - Expected behavior: [what should have happened]
   - Actual behavior: [what did happen]
   - Likely cause: [why the gap exists]
❌ [mechanism]: [description]
[...list all failing tests]

RECOMMENDATIONS (prioritized by risk):
1. [Highest risk gap]: [specific fix with implementation detail]
2. [Next gap]: [specific fix]
[...list all recommendations]

Next audit scheduled: [date or trigger condition]
```

---

## Audit Cadence

**Monthly**: for active projects. Security threats change; checking that controls still work is
maintenance, not overhead.

**After every maturity level upgrade**: when you add new governance mechanisms, verify they
work before trusting them. A pre-commit hook that was installed but not tested is worse than
no hook — it creates a false sense of security.

**After adding any new governance mechanism**: the day you add a new scanner rule, test it.

**Before enterprise rollout**: if you are presenting this governance system to leadership or
a compliance team, run a full adversarial audit first. "Our governance catches 13 of 15 test
violations" is a credible claim. "We think our governance works" is not.

**After a production incident**: if something slipped through, add a test for that specific
failure mode to the audit battery. The audit is your evidence that the new control works.

---

## Why Governance Testing Is Not Optional

The analogy is smoke alarms. You would not install a smoke alarm and then assume it works
without testing it. You press the test button. You verify the battery. You know it functions.

Governance mechanisms are the same. The pre-commit hook that "should" catch secrets has
never been verified to catch secrets in your specific setup, with your specific file types,
on your team's machines. Until you test it, you do not know if it works.

Adversarial auditing is pressing the test button — for every governance mechanism you depend on.

---

## Related

- [agents/red-team-auditor.md](../agents/red-team-auditor.md) — the agent that runs the audit
- [commands/audit.md](../commands/audit.md) — /audit command definition
- [patterns/automation-bias-defense.md](../patterns/automation-bias-defense.md) — why AI validation can create false safety
- [docs/security-guide.md](security-guide.md) — security mechanisms being tested by the security audit category
