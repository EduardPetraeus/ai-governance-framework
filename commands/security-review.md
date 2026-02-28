# /security-review

Run a security scan on the current branch changes. This is a quick in-session check (under 2 minutes), not a deep review. For comprehensive security analysis, use the security-reviewer agent in a dedicated session.

## Steps

### Step 1: Get the diff

Run `git diff main...HEAD --name-only` to get the list of changed files.
Run `git diff main...HEAD` to get the full diff content.

If on main or no diff exists: scan the last commit instead with `git diff HEAD~1`.

If git is not available or you cannot get the diff: say so and ask the user to provide the files to review.

### Step 2: Read security policy

Read CLAUDE.md if it exists. Look for:
- The `never_commit` list (project-specific forbidden patterns)
- The `scan_triggers` section (what to check)
- The `security` section (any project-specific rules)

### Step 3: Scan every file in the diff

For each changed file, check against this checklist:

#### Secrets and credentials — FAIL if found
- [ ] API keys or tokens hardcoded: `_key =`, `_token =`, `api_key`, `secret`, `_SECRET`
- [ ] Passwords: `password =`, `passwd =`, `pwd =`, `DB_PASS`
- [ ] AWS credentials: `AKIA` prefix, `aws_access_key_id`, `aws_secret_access_key`
- [ ] Provider-specific keys: `sk_live_`, `pk_live_`, `sk-ant-`, `ghp_`, `xoxb-`, `glpat-`
- [ ] Connection strings with credentials: `://user:pass@host`
- [ ] Private keys: `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN OPENSSH PRIVATE KEY-----`
- [ ] JWT secrets: `jwt_secret`, `signing_key`, `JWT_SECRET`
- [ ] Secrets in comments: `# key:`, `// password:`, `# TODO: remove`
- [ ] `.env` files in the diff (should be gitignored)

#### PII — FAIL if in source code, WARN if in comments or logs
- [ ] Email addresses hardcoded in source (not in test factories with @test.invalid)
- [ ] Phone numbers, national IDs, passport numbers
- [ ] Health or medical data
- [ ] Real customer names
- [ ] PII in log statements: `logger.info(f"...{user.email}...")`

#### Injection and unsafe patterns — WARN
- [ ] SQL with string concatenation: `f"SELECT ... WHERE id = {user_input}"`
- [ ] `eval()` or `exec()` with any external input
- [ ] `subprocess` with `shell=True` and interpolated strings
- [ ] `pickle.loads()` or `yaml.load()` (without SafeLoader) on external data
- [ ] HTTP instead of HTTPS for external API calls
- [ ] TLS verification disabled: `verify=False`
- [ ] Debug mode: `DEBUG = True` in production code paths

#### Configuration — WARN
- [ ] New values that should be environment variables but are hardcoded
- [ ] New hardcoded paths to production or staging systems
- [ ] New external URLs that should be configurable
- [ ] Overly permissive CORS, file permissions, or access controls

### Step 4: Produce the report

---

```
SECURITY REVIEW — [project name]
=================================
Branch: [branch name] vs. main
Files reviewed: [N]
Lines reviewed: [N]
Date: [YYYY-MM-DD]

Verdict: PASS | WARN | FAIL

[FAIL]  file.py:N — [description of finding]
        Pattern: [the actual code/string found]
        Impact: [why this matters]
        Fix: [one-line fix recommendation]

[WARN]  file.py:N — [description]
        Pattern: [code]
        Impact: [why]
        Fix: [recommendation]

[INFO]  [informational note — not a finding, just a heads-up]

REQUIRED ACTIONS (FAIL items — must fix before merge):
1. [specific action with file:line]

RECOMMENDED ACTIONS (WARN items — should fix):
1. [specific action]

CLEAN FILES (no issues found):
- [list of files that passed all checks]
```

---

### Step 5: Verdict response

- **If FAIL:** "This branch cannot merge in its current state. The FAIL items above must be fixed first. I can help fix them in this session — say 'fix' to proceed."

- **If WARN:** "No blocking issues, but the WARN items above should be addressed before requesting human review."

- **If PASS:** "Security check passed. No issues found in the changed files. Note: this is a quick scan, not a comprehensive review. For sensitive changes, run the full security-reviewer agent."

## Rules

- Do not skip files because they seem unrelated. Scan every file in the diff.
- False positives are acceptable. Flag anything that looks suspicious. A false positive costs 30 seconds of explanation. A miss costs a security incident.
- If you find a FAIL item, report it immediately — do not wait for the full scan to complete.
- This command checks patterns in the diff only. It does not run gitleaks or detect-secrets.
- Do not produce a report longer than 50 lines. This is a quick check. If there are many findings, summarize and recommend the full security-reviewer agent.

---

## Example output

```
SECURITY REVIEW — HealthReporting
=================================
Branch: feature/hubspot-connector vs. main
Files reviewed: 4
Lines reviewed: 285
Date: 2026-02-28

Verdict: WARN

[WARN]  src/connectors/hubspot.py:12 — API version hardcoded
        Pattern: API_VERSION = "2024-01"
        Impact: Requires code change to update API version. Should be configurable.
        Fix: Use os.environ.get("HUBSPOT_API_VERSION", "2024-01")

[WARN]  src/connectors/hubspot.py:45 — HTTP logging of request URL includes API key
        Pattern: logger.debug(f"Requesting {url}?hapikey={self.api_key}")
        Impact: API key appears in debug logs. If debug logging is enabled in
                production, the key is exposed in log aggregation systems.
        Fix: Log the URL without the API key parameter, or mask it:
             logger.debug(f"Requesting {url}?hapikey=***")

REQUIRED ACTIONS: None.

RECOMMENDED ACTIONS:
1. src/connectors/hubspot.py:12 — Move API version to env var
2. src/connectors/hubspot.py:45 — Remove or mask API key from log statement

CLEAN FILES:
- src/pipeline/sync.py
- docs/adr/ADR-007.md

No blocking issues. The API key in logs (line 45) is the more important finding —
address before merge to avoid credential exposure in log systems.
```
