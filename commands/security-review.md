# /security-review

Run a security checklist on the current branch changes. Produce a PASS / WARN / FAIL
report with specific file:line references.

This is a quick in-session check. For a deep security review, use the security-reviewer
agent in a dedicated session. This command is designed to run in under 2 minutes.

## Steps

1. Run: `git diff main...HEAD --name-only` to get the list of changed files.
   If on main or no diff: scan the last 10 commits.

2. Run: `git diff main...HEAD` to get the full diff of changed content.

3. Read CLAUDE.md to understand this project's security policy (never_commit list,
   scan_triggers, incident_response).

4. Apply the security checklist to every file in the diff:

---

## Security Checklist

For each changed file, check:

### Secrets and credentials (FAIL if found)
- [ ] API keys or tokens hardcoded (patterns: `_key =`, `_token =`, `api_key`, `secret`)
- [ ] Passwords hardcoded (patterns: `password =`, `passwd =`, `pwd =`)
- [ ] AWS credentials (`AKIA...` key patterns, `aws_access_key_id`)
- [ ] Stripe keys (`sk_live_`, `pk_live_`, `rk_live_`)
- [ ] Database connection strings with embedded credentials (`user:pass@host`)
- [ ] Private keys or certificates (-----BEGIN RSA PRIVATE KEY-----)
- [ ] JWT secrets or signing keys
- [ ] Credentials in comments ("# using key: abc123")

### PII and sensitive data (FAIL if found in code, WARN if found in comments)
- [ ] Email addresses hardcoded in source (not in test data factories)
- [ ] Phone numbers, national ID numbers, passport numbers
- [ ] Health or medical data in source files
- [ ] Real customer names or identifiers
- [ ] IP addresses that appear to be real user IPs

### Configuration security (WARN)
- [ ] New configuration values that should be environment variables but are hardcoded
- [ ] New `.env` file added to git (should be in .gitignore)
- [ ] New hardcoded path to production or staging systems
- [ ] New external URL hardcoded that should be configurable

### Code security patterns (WARN)
- [ ] SQL queries built with string concatenation (injection risk)
- [ ] `eval()` or `exec()` called with user-provided input
- [ ] `subprocess` called with shell=True and user input
- [ ] Unpickle called on data from external sources
- [ ] HTTP (not HTTPS) used for external API calls

### Documentation security (INFO)
- [ ] CLAUDE.md `never_commit` list still covers new patterns introduced
- [ ] New integrations that handle user data are documented in ARCHITECTURE.md

---

5. Produce the security report:

```
SECURITY REVIEW — [project name]
=================================
Branch: [current branch vs. main]
Files reviewed: [N]
Lines reviewed: [N]
Date: [YYYY-MM-DD]

Verdict: PASS | WARN | FAIL

[FAIL]  file.py:N — [issue description]
[WARN]  config.yaml:N — [issue description]
[INFO]  [informational note]

REQUIRED ACTIONS (FAIL items — fix before merge):
1. [action]

RECOMMENDED ACTIONS (WARN items):
1. [action]

CLEAN FILES (no issues):
[list of files that passed]
```

6. If verdict is FAIL:
   Say: "This PR cannot be merged in its current state. The FAIL items above must be
   remediated. If you need help fixing them, I can assist in this session before you commit."

   If verdict is WARN:
   Say: "No blocking issues found, but the WARN items should be addressed before requesting
   human review. Proceed with caution."

   If verdict is PASS:
   Say: "Security check passed. No issues found in the changed files. This does not replace
   a full security review by the security-reviewer agent for sensitive changes."

---

## Notes for the agent

- If git is not available or you cannot get the diff: say so and ask for the files to review
- Do not skip files because they seem unrelated — scan everything in the diff
- If you find a FAIL item, stop and report it before continuing the scan
  (the user should know immediately, not wait for the full report)
- False positives are acceptable — flag anything that looks like a secret even if it might
  be a test value. The cost of a false positive is a quick explanation; the cost of a miss
  is a security incident.
- This command does not run gitleaks or detect-secrets (those run in pre-commit).
  This is a pattern-matching check on the diff content.

---

## Example output

SECURITY REVIEW — HealthReporting
===================================
Branch: feature/shopify-connector vs. main
Files reviewed: 5
Lines reviewed: 312
Date: 2025-03-15

Verdict: WARN

[WARN]  src/connectors/shopify.py:23 — API version hardcoded as "2024-01"
        This should be a configuration value (SHOPIFY_API_VERSION env var) to allow
        version updates without code changes.

[WARN]  tests/integration/test_shopify_connector.py:8 — Test uses realistic-looking
        token value "test_token_not_real". While clearly labeled, consider using a
        constant like SHOPIFY_TEST_TOKEN to make intent clearer across test files.

REQUIRED ACTIONS (none):
No FAIL items found.

RECOMMENDED ACTIONS:
1. src/connectors/shopify.py:23 — Move API version to environment variable or config file.
   Pattern: os.environ.get("SHOPIFY_API_VERSION", "2024-01")

CLEAN FILES (no issues):
- sources_config.yaml
- tests/fixtures/factories.py
- docs/adr/ADR-003.md

No blocking issues found. The WARN items are minor and do not prevent merge, but the
API version hardcoding is worth fixing before Phase 3 (version pinning becomes a
maintenance issue at production scale).
