# Security Guide: Security as Infrastructure

## 1. The AI Security Paradox

AI-assisted development is simultaneously the most productive and the most dangerous way to write software. This is not a tension that can be resolved — it must be governed.

The threat surface:

- AI agents produce code at 10-15x human speed, which means 10-15x more opportunities to accidentally introduce hardcoded credentials, expose PII, or create vulnerable patterns — per hour, per developer
- AI agents have no instinct for "this looks dangerous." They optimize for functionality, not safety. A developer asked to hardcode a password will hesitate. An agent will comply immediately, format the code correctly, add a comment explaining what the credential is for, and move on
- Documentation is written faster, which means more places where PII, hostnames, configuration details, and real credentials can appear without scrutiny
- Agents read files they are pointed at — without `.claudeignore`, they will read `.env`, `secrets.yaml`, and production configuration files, and may reproduce their contents in generated code or documentation
- The review bottleneck inverts: instead of one developer writing code slowly enough to review, one developer approves code faster than they can read it

### The Obedience Problem

This is the critical insight that makes AI security fundamentally different from traditional application security.

Traditional developers have judgment. They have an emotional response to writing `password = "hunter2"` in source code. They feel uneasy. They push back. An AI agent does not have this response. It will write the password, format it correctly, add type hints, write a docstring explaining the parameter, and generate a unit test that uses the hardcoded credential.

**AI agents are obedient, not cautious.** Their obedience is their value — and their obedience is their risk. The same property that makes them execute 50 tasks in a session without complaint makes them execute 50 security violations in a session without complaint. The difference is entirely determined by the instructions they receive.

The **speed x obedience x no-instinct** combination is genuinely dangerous. A governed agent that has been told "never commit secrets" and is backed by automated scanning will not commit secrets. An ungoverned agent will do exactly what it is asked, including things no human developer would do without at least pausing.

Security governance is therefore not an optional layer on top of AI development. It is the foundation that makes AI development safe to practice at all.

### Why Traditional Security Practices Are Not Enough

Traditional code review was designed for human-speed development: a developer writes 50-200 lines of code per day, a reviewer reads them carefully, and the review happens within 24 hours. AI-assisted development breaks every assumption in this model:

- **Volume**: A single AI session can produce 500-2,000 lines of code across 10-20 files. The review backlog created by 50 developers running 2 sessions per day is physically impossible to review at human reading speed with the attention security review requires
- **Speed**: 50 commits in 2 hours creates pressure to approve quickly. "I'll review it later" becomes "it shipped three days ago"
- **Confidence mimicry**: AI-generated code looks professionally written regardless of whether it is secure. The visual quality signals that reviewers rely on (clean formatting, consistent naming, professional comments) are present in both secure and insecure AI code
- **Pattern novelty**: AI may introduce vulnerability patterns that are not in the reviewer's mental checklist — not because the AI is adversarial, but because it synthesizes patterns from training data that may include insecure code

The response is not to slow down AI development to human speed. The response is to build security infrastructure that operates at AI speed: automated, layered, and continuous.

---

## 2. Security Across All 7 Layers

Security is not a phase or a team. It is woven through every layer of the governance framework.

| Layer | Security Responsibility | Key Practice |
|-------|------------------------|-------------|
| **1. Constitution** | Define what cannot happen, ever. The never-commit list. `.gitignore`, `.claudeignore`. Data classification. | Security rules in `CLAUDE.md` are reviewed every 6 months. They are never the only mechanism — defense in depth. |
| **2. Orchestration** | Security checks during session protocol: at start, during, at end. | Agent performs diff-based scan at session start. Checks each created/modified file against pattern list. Full scan before final commit. |
| **3. Enforcement** | Automated gates that run regardless of agent or developer behavior. | Pre-commit hooks (gitleaks, trufflehog). CI/CD security gates block merge on failure. Branch protection prevents direct pushes. |
| **4. Observability** | Security events tracked over time, not just detected point-in-time. | Security incident log in `docs/SECURITY_LOG.md`. False positive rate monitored. Credential rotation tracking. |
| **5. Knowledge** | Security decisions documented and not re-litigated. | Security ADRs explain why restrictions exist. When questioned, point to the ADR: "We decided this on this date for these reasons." |
| **6. Team** | Security responsibility distributed, not siloed. | Dedicated security agent role (Opus-powered, no compromises). Security agent can hard-block a PR merge. |
| **7. Evolution** | Threat model evolves; security constitution evolves with it. | Post-incident: add a deterministic check that would have caught it. Do not rely on "everyone will be more careful." |

**The principle across all layers: deterministic enforcement where possible, probabilistic (AI-based) analysis where necessary, human judgment for novel situations. Never AI alone for security.**

---

## 3. Three Scan Levels

### Level 1: Per-File Scan (Continuous)

Runs during the session, every time the agent writes or modifies a file. This is the fastest, cheapest, and most frequently triggered security check.

**What it checks:**
- Pattern matching: `api_key=`, `password=`, `secret=`, `token=`, `Authorization:`, `Bearer `
- Absolute paths: `/Users/`, `/home/`, `C:\Users\`
- Base64 strings longer than 40 characters in configuration files (potential encoded credentials)
- Email addresses in non-test, non-documentation files
- IP addresses and internal hostnames (`*.internal.*`, `*.local`, `10.*`, `172.16-31.*`, `192.168.*`)
- Connection strings with embedded credentials (`postgresql://user:pass@host`)
- Context check: is this a config file with real values, or a template with placeholders?

**Speed:** Essentially free — runs in milliseconds, no API call required.

**Coverage:** Catches approximately 80% of accidental secret commits before they reach git.

**Implementation in CLAUDE.md:**
```markdown
## file_security_check (run on EVERY file write)

Before saving any file, scan for:
- Strings matching: api_key=, password=, secret=, token=, Authorization:, Bearer
- Connection strings with embedded credentials (user:pass@host pattern)
- Absolute paths starting with /Users/, /home/, C:\Users\
- Base64 strings longer than 40 characters in config/yaml/json/env files
- Email addresses in non-test, non-documentation files
- IP addresses or hostnames matching internal patterns

If ANY match is found:
  1. STOP — do not save the file
  2. Show the developer the specific match and its location
  3. Ask: "Is this a placeholder/example, or a real credential/value?"
  4. If real: replace with environment variable reference before saving
  5. If placeholder: proceed, but add a comment: "# Example value — not a real credential"
```

### Level 2: Per-Session Scan

Runs at session start and session end. Catches issues that span multiple files or accumulate across changes.

**Session start scan:**
- All files modified since last session (diff-based): `git diff --name-only HEAD~[last_session_commits]`
- Cross-file check: if any new config files were created since last session, is `.gitignore` updated?
- Verify `.claudeignore` exists and covers sensitive paths

**Session end scan (before any commit):**
- All files modified in this session
- Cross-file: if new connection strings appear, are they using environment variables?
- Cross-file: if a new integration was added, does it follow the credential pattern established in existing integrations?
- Verify no file that should be in `.gitignore` is staged

**Speed:** 10-30 seconds depending on change volume. Not blocking for the developer — runs while they review the session summary.

**Coverage:** Catches issues that per-file scanning misses: a credential introduced in file A that is referenced in file B, a config file that should be gitignored but is not, patterns that only become visible across multiple file changes.

**Implementation in CLAUDE.md:**
```markdown
## session_security_scan

on_session_start:
  1. Run git diff --name-only to identify files changed since last session
  2. Scan changed files for security patterns
  3. Verify .claudeignore covers all sensitive paths
  4. Report: "Security scan clean" or list findings

on_session_end (BEFORE any commit):
  1. Run security scan on ALL files modified in this session
  2. Check .gitignore includes all new sensitive file types
  3. Confirm no hardcoded values in any config files
  4. Verify all connection strings use environment variables
  5. If scan is clean: proceed to commit
  6. If scan finds issues: RESOLVE BEFORE COMMIT — do not commit with known issues
```

### Level 3: Periodic Full-Repo Scan

Runs every fifth session and on a monthly schedule. Catches accumulated drift that session-level scanning misses.

**What it checks:**
- All files in the repository, not just recently changed ones
- Historical: `git log` scan for secrets that may exist in older commits (committed and then "removed" — still in history)
- Configuration completeness: is `.gitignore` still current? Is `.claudeignore` covering all sensitive paths? Are there new file types that should be excluded?
- Dependency scan: known vulnerabilities in pinned packages (`pip-audit`, `npm audit`, `safety check`)
- Stale credentials: are there references to credentials that should have been rotated?

**Speed:** Minutes. Scheduled task, not blocking for the developer.

**Coverage:** Catches accumulated drift — a file that was safe six months ago may now contain sensitive information after incremental changes. A dependency that was secure when pinned may now have a known CVE.

**Implementation:** GitHub Actions scheduled workflow:

```yaml
# .github/workflows/security-scan-full.yml
name: Full Security Scan
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 06:00 UTC
  workflow_dispatch:       # Manual trigger

jobs:
  full-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for historical scan

      - name: Scan current files
        run: gitleaks detect --source=. --verbose --report-format=json --report-path=gitleaks-current.json

      - name: Scan git history
        run: gitleaks detect --source=. --log-opts="--all" --verbose --report-format=json --report-path=gitleaks-history.json

      - name: Scan recent history with trufflehog
        run: trufflehog git file://. --since-commit HEAD~100 --only-verified --json > trufflehog-results.json

      - name: Dependency audit
        run: pip-audit --format=json --output=pip-audit-results.json || true

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: |
            gitleaks-current.json
            gitleaks-history.json
            trufflehog-results.json
            pip-audit-results.json
```

---

## 4. Documentation as Attack Vector

Most security thinking focuses on source code. Documentation is equally dangerous and far less frequently scrutinized.

### Specific Examples

**CHANGELOG.md leaking credential information:**
```markdown
## 2026-03-01 — Session 012
- Rotated Oura API key after expiry (old key: sk-oura-abc123def456...)
- Updated database connection string for staging environment
```
The old API key is now in version control history forever. The mention of "Oura API key" confirms the service is in use and its credential format.

**Architecture documentation exposing internal topology:**
```markdown
## Production Infrastructure
Primary database: db-prod-01.internal.company.com:5432
Redis cache: redis-cluster.us-east-1.internal:6379
API gateway: api-gw.internal:8080
```
Internal hostnames in documentation (even private repositories) create reconnaissance value. Repository access controls change; documentation remains.

**README with real credentials in setup instructions:**
```markdown
## Quick Start
export OURA_TOKEN=your_token_here
# Team shared token for development: oat_eyJhbGciOiJSUzI1NiIs...
```
"Temporary" real credentials in setup docs get committed. The comment saying "team shared token" makes this worse — it indicates the token provides broad access.

**Test fixtures with real data:**
```python
# tests/fixtures/sample_health_data.py
SAMPLE_USER = {
    "user_id": 12345,          # Real user ID from production
    "name": "John Smith",       # Real person's name
    "heart_rate": 68,
    "blood_pressure": "142/91", # Real health data — HIPAA/GDPR violation
    "medications": ["metformin", "lisinopril"]
}
```
Real health data in test fixtures is a compliance incident. Even "anonymized" real data may be re-identifiable.

**Screenshots in documentation:**
A screenshot of a dashboard showing real health metrics, a URL bar containing a token, or a terminal output showing database connection details. Screenshots are not scanned by deterministic tools — they require manual or AI-based review.

### The Rule

Scan ALL files in the repository — not just `.py`, `.sql`, `.yaml`. Markdown files, README, CHANGELOG entries, test fixtures, Jupyter notebooks, and configuration examples are all in scope for security scanning. If a deterministic scanner cannot parse a file type, flag it for manual review.

---

## 5. The Never-Commit List

The following items must never appear in any committed file, in any form, in any branch:

```
NEVER COMMIT — CREDENTIALS:
  - API keys and API tokens (any service: Anthropic, OpenAI, AWS, GCP, Stripe, etc.)
  - OAuth tokens, access tokens, refresh tokens
  - JWT secrets and signing keys
  - Passwords and password hashes
  - Webhook secrets and signing secrets
  - SSH private keys
  - Private keys (.pem, .key files) and certificates (.p12, .pfx)
  - Database credentials: usernames, passwords, connection strings with embedded auth
  - Service account credentials and key files

NEVER COMMIT — INFRASTRUCTURE:
  - Production connection strings (even without passwords — they reveal topology)
  - Internal hostnames and IP ranges (*.internal.*, 10.*, 172.16-31.*, 192.168.*)
  - Hardcoded paths to production environments (/prod/, /production/, specific prod hostnames)
  - Cloud resource ARNs, project IDs, or subscription IDs that are not public
  - VPN configurations or network topology details

NEVER COMMIT — PERSONAL DATA:
  - Names, email addresses, phone numbers
  - National IDs: SSN, CPR numbers, passport numbers
  - Health data: diagnoses, medications, biometrics, patient IDs, lab results
  - Financial data: account numbers, transaction IDs with amounts, salary data
  - Location data that can identify individuals
  - Any data that, alone or in combination, can identify a natural person

NEVER COMMIT — REAL DATA SAMPLES:
  - Production data exports or samples (even "a few rows for testing")
  - "Anonymized" production data (anonymization is harder than you think)
  - API responses from production endpoints containing user data
  - Screenshots showing real user data, real credentials, or real infrastructure details
  - Log files containing user actions, IP addresses, or session tokens
```

**The principle: if it looks like a secret, treat it as a secret.** The cost of a false positive (adding a non-sensitive string to `.gitignore`) is negligible. The cost of a false negative (committing a real credential) is a security incident that may require credential rotation, access log audit, breach notification, and regulatory reporting.

**Once committed, always compromised.** A credential committed and then reverted in the next commit is still in the git history. Anyone with repository access can find it with `git log -p`. Treat any credential that has touched a remote repository as compromised and rotate it immediately.

---

## 6. Incident Response Protocol

When a security incident is detected — a secret in a commit, PII in documentation, credentials in a log file — follow this protocol. Speed matters. Each step has a time target.

### 1. STOP
Cease all AI-assisted work immediately. Do not continue the session. Do not commit anything else. Do not attempt to "fix it quickly" — a hurried fix often makes the exposure worse.

*Time target: immediate, within seconds of detection.*

### 2. ASSESS
Determine scope: What was exposed? What type of data or credential? When was it committed? How many commits ago? Has it been pushed to remote? Is the repository public or private? Who has access to the repository?

*Time target: within 5 minutes. Write the answers down — you will need them for the log.*

### 3. CONTAIN
- **If credential**: invalidate it immediately at the source. Rotate the API key. Revoke the token. Change the password. Do this before cleaning the repository — containment before cleanup.
- **If PII**: document exactly what was exposed, in which files, in which commits. Determine who may have accessed the repository during the exposure window.
- **If pushed to remote**: assume it has been observed, even if the repository is private. Private repositories can be forked, cloned, or accessed by anyone with repository permissions — including former team members and CI/CD service accounts.

*Time target: within 15 minutes for credential rotation. Within 1 hour for PII documentation.*

### 4. FIX
Remove the secret from the codebase. Replace with an environment variable reference or secrets manager call. If the secret is in git history, clean the history:

```bash
# Using git-filter-repo (preferred over filter-branch)
pip install git-filter-repo
git filter-repo --invert-paths --path path/to/file-with-secret

# Or for specific strings in multiple files:
git filter-repo --replace-text <(echo 'sk-ant-abc123==>REDACTED')
```

*Time target: within 1 hour of initial detection.*

### 5. VERIFY
Run a full repository scan to confirm the secret is completely removed, including from git history:

```bash
gitleaks detect --source=. --log-opts="--all" --verbose
trufflehog git file://. --only-verified
```

Confirm the new credential (if rotated) is working correctly in all environments.

*Time target: within 2 hours of initial detection.*

### 6. LOG
Document the incident in `docs/SECURITY_LOG.md`:

```markdown
## Incident: 2026-03-01
- **Type:** API key exposure
- **Severity:** High
- **Source:** docs/CHANGELOG.md, commit abc1234
- **What was exposed:** Oura API token (personal access token with read scope)
- **Detection method:** Gitleaks pre-commit hook on colleague's machine (was missed on original committer's machine due to outdated hook version)
- **Timeline:**
  - 14:23 — Committed to feature branch
  - 14:25 — Pushed to remote
  - 14:41 — Detected during PR review
  - 14:43 — Token revoked at Oura developer portal
  - 15:10 — Git history cleaned, force push to feature branch
  - 15:22 — Full repo scan confirmed clean
- **Root cause:** Developer pasted full rotation log including old token into CHANGELOG
- **Prevention:** Added CHANGELOG-specific scanning rule to pre-commit hooks. Updated CLAUDE.md to prohibit credential values in CHANGELOG entries.
```

*Time target: within 24 hours.*

### 7. PREVENT
Add a deterministic check that would have caught this incident. Do not rely on training, awareness, or "everyone being more careful." Implement a check:

- Update pre-commit hook patterns if the scanner did not catch this pattern
- Update `.gitignore` and `.claudeignore` if a file type was not covered
- Update `CLAUDE.md` if a rule was absent or insufficiently specific
- Add a CI/CD check if the pre-commit hook was bypassed

*Time target: within 48 hours.*

### 8. REVIEW
Conduct a post-incident review with the team:
- Was the root cause a missing rule, a broken tool, or a human bypass?
- Could this class of incident happen again through a different path?
- Is the security constitution adequate, or does it need structural changes?
- Update the security maturity assessment if this reveals a gap

*Time target: within 1 week.*

---

## 7. Security Maturity Model

| Level | Name | What Exists | What's Missing |
|-------|------|-------------|----------------|
| 0 | No awareness | Nothing. Secrets in code. No `.gitignore`. No scanning. | Everything. |
| 1 | Basic hygiene | `.gitignore` exists. Developers know not to commit secrets. Manual spot checks. | Automation. Agent awareness. Incident response. |
| 2 | Agent-aware | Security rules in `CLAUDE.md`. Agent performs per-file checks. Session scans at start and end. `.claudeignore` configured. | Enforcement. CI/CD gates. Dedicated security review. |
| 3 | Automated enforcement | Pre-commit hooks (gitleaks/trufflehog). CI/CD security gates block merge on failure. Dedicated security agent for PR review (Opus). Incident response protocol documented and tested. | Continuous monitoring. Dependency scanning. Compliance integration. |
| 4 | Continuous monitoring | Automated threat detection. Dependency vulnerability scanning on schedule. Credential rotation tracking and alerts. Security metrics dashboard (issues/session trending, false positive rate, time-to-fix). | Compliance-grade documentation. External validation. |
| 5 | Compliance-grade | Continuous compliance monitoring. Automated audit trails that satisfy EU AI Act and GDPR documentation requirements. Annual penetration testing or red team exercise. Regulatory-ready documentation package. | This is the target state for regulated industries. |

Teams implementing this framework should reach Level 3 within 8-12 weeks of beginning the rollout. Level 4 is appropriate after 6 months of Level 3 operation. Level 5 is required for regulated industries (healthcare, finance, critical infrastructure) and recommended for any organization with more than 50 developers.

---

## 8. Tooling Stack

### Deterministic Tools (Always Run First)

These tools find exact patterns. They have near-zero false negatives for patterns they know. They should run on every commit and every PR, without exception.

**gitleaks** — secret detection in git repositories

```bash
# Install
brew install gitleaks

# Scan current repository state
gitleaks detect --source=. --verbose

# Scan entire git history (catches committed-then-removed secrets)
gitleaks detect --source=. --log-opts="--all" --verbose

# As a pre-commit hook (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.0
    hooks:
      - id: gitleaks
```

**trufflehog** — credential verification

```bash
# Install
brew install trufflehog

# Scan recent git history (verified credentials only — fewer false positives)
trufflehog git file://. --since-commit HEAD~50 --only-verified

# Scan entire history
trufflehog git file://. --only-verified
```

**git-secrets** — AWS and custom pattern prevention

```bash
# Install
brew install git-secrets

# Register AWS credential patterns
git secrets --register-aws

# Add custom patterns for your stack
git secrets --add 'ANTHROPIC_API_KEY=sk-ant-[A-Za-z0-9_-]+'
git secrets --add 'OURA_TOKEN=[A-Za-z0-9_-]{40,}'
git secrets --add 'postgresql://[^:]+:[^@]+@'

# Install as pre-commit hook
git secrets --install
```

**Custom pre-commit checks:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: no-hardcoded-paths
        name: Check for hardcoded absolute paths
        entry: bash -c 'grep -rn "/Users/\|/home/" --include="*.py" --include="*.yaml" --include="*.sql" --include="*.md" . && exit 1 || exit 0'
        language: system
        pass_filenames: false

      - id: no-env-staged
        name: Prevent .env files from being committed
        entry: bash -c 'git diff --cached --name-only | grep -q "^\.env" && echo "ERROR: .env file staged for commit" && exit 1 || exit 0'
        language: system
        pass_filenames: false

      - id: no-connection-strings
        name: Check for connection strings with credentials
        entry: bash -c 'grep -rn "://[^:]*:[^@]*@" --include="*.py" --include="*.yaml" --include="*.json" --include="*.toml" . | grep -v "example\|placeholder\|your_" && exit 1 || exit 0'
        language: system
        pass_filenames: false

      - id: no-real-emails-in-code
        name: Check for email addresses in source code
        entry: bash -c 'grep -rn "[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]*\.[a-zA-Z]" --include="*.py" . | grep -v "test_\|fixture\|example\|noreply@\|#.*@" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

### Probabilistic Tools (AI-Based Review)

These tools understand context. They catch issues that deterministic scanners miss: a variable named `db_config` that contains an embedded password in a dict literal, PII in a comment, a screenshot URL that reveals a token in the query string.

**Security review agent (Opus-powered):**
- Reviews PR diffs for context-aware security issues
- Distinguishes real credentials from examples and placeholders
- Detects PII in documentation that pattern matchers would not flag (e.g., "the patient John Smith had a heart rate of 68")
- Evaluates whether new integrations open attack vectors
- Catches security anti-patterns: hardcoded CORS origins, disabled SSL verification, overly permissive file permissions

**Implementation in CI/CD:**

```yaml
# .github/workflows/ai-security-review.yml
name: AI Security Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  security-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deterministic scan (always first)
        run: |
          gitleaks detect --source=. --verbose
          echo "Deterministic scan complete"

      - name: AI security review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Extract PR diff
          git diff origin/main...HEAD > /tmp/pr-diff.txt

          # Feed diff to security review agent (Opus)
          # Agent returns: PASS / WARN / FAIL with specific findings
          # Post findings as PR review comment
          python scripts/ai_security_review.py \
            --diff /tmp/pr-diff.txt \
            --constitution CLAUDE.md \
            --output-format github-review
```

### The Combination: Why You Need Both

| Capability | Deterministic | AI-Based |
|-----------|--------------|----------|
| Known secret patterns | Catches all | Catches most |
| Novel secret formats | Misses | Catches with context |
| PII in natural language | Misses | Catches |
| Configuration that reveals topology | Misses | Catches |
| Speed | Milliseconds | Seconds to minutes |
| False positive rate | Very low | Moderate |
| Can be bypassed by the AI itself | No | Theoretically yes |
| Cost | Free | Per-API-call |

**The principle: deterministic first, AI second, never AI alone.** An AI security reviewer can be convinced — through prompt injection or through confident-sounding but insecure code — to approve things that a deterministic scanner would catch. The deterministic scanner cannot be convinced. It checks patterns. Period.

---

## 9. The Confidence Problem

The most dangerous characteristic of AI-generated code from a security perspective: **the agent presents secure and insecure code with identical confidence, identical formatting quality, and identical professional tone.**

A developer reviewing AI-generated code sees:
- Clean syntax
- Proper formatting
- Logical structure
- Professional comments
- Type hints and docstrings

None of these visual signals indicate whether the code is secure. A hardcoded credential, an SQL injection vulnerability, a path traversal issue, or a disabled SSL verification check looks exactly as polished as correct code. The glance test fails completely for security.

### How to Compensate

**Never trust AI security claims.** If an agent says "this code is secure" or "I have verified there are no security issues," those statements have no more validity than any other generated text. The agent is reporting what it expects to be true based on patterns, not what it has verified through analysis.

**Run deterministic tools on every AI-generated file.** The agent's confidence is irrelevant. The scanner's result is what matters. This is non-negotiable.

**Apply the adversarial test during review.** For any AI-generated authentication, authorization, or data handling code, ask: "If this code were written to allow unauthorized access, how would it differ from what I am looking at?" If the answer is "not much," the code needs deeper review.

**Test security assumptions explicitly:**
- Send an unauthenticated request. Does it fail correctly?
- Send a request with an expired token. Is it rejected?
- Send a request with valid authentication but wrong authorization. Is it blocked?
- Send input that contains path traversal patterns (`../../../etc/passwd`). Is it sanitized?
- Send input larger than expected. Does it fail safely?

Do not assume the AI implemented edge cases because the happy path looks correct. The happy path always looks correct. The edge cases are where security lives.

**Use a security checklist that cannot be overridden by confidence.** The checklist forces explicit verification of specific security properties, regardless of how the code looks or what the AI claims about it:

```
Security Review Checklist (for every PR touching auth, data handling, or external integrations):

[ ] No hardcoded credentials or configuration values — verified by scanner AND manual review
[ ] All external input is validated before use — checked specific input paths
[ ] Authentication handles: missing credentials, expired tokens, invalid tokens, revoked tokens
[ ] Authorization handles: valid auth but wrong permissions, escalation attempts
[ ] Error messages do not leak internal details (stack traces, file paths, SQL queries)
[ ] Logging does not capture PII, tokens, or credentials
[ ] HTTPS/TLS used for all external communications — no disabled SSL verification
[ ] Rate limiting exists for public-facing endpoints
[ ] All new dependencies checked for known vulnerabilities
[ ] Connection strings, API endpoints use environment variables — no hardcoded hosts
```

---

*Related guides: [Compliance Guide](./compliance-guide.md) | [AI Code Quality](./ai-code-quality.md) | [Model Routing](./model-routing.md) | [Enterprise Playbook](./enterprise-playbook.md)*
