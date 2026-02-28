# Security Guide: Security as Infrastructure

## 1. Why AI Development Needs MORE Security, Not Less

The intuition that AI tools make development safer is wrong. AI tools make development faster — and faster development without governance is faster exposure.

Consider the threat surface:

- AI agents produce code at 10–15x human speed, which means 10–15x more opportunities to accidentally introduce hardcoded credentials, expose PII, or create vulnerable patterns
- AI agents have no instinct for "this looks dangerous" — they optimize for functionality, not safety
- Copy-paste from Stack Overflow, the old vector for accidental credential leakage, is now replaced by AI-generated code that can contain the same patterns at the same rate
- Documentation is written faster, which means more places where PII, hostnames, and configuration details can appear
- Agents read files they are pointed at — without `.claudeignore`, they will read and transmit `.env` files

### The Obedience Problem

This is the critical insight that makes AI security different from traditional application security.

Traditional developers have judgment. A developer asked to add a password to source code will hesitate, push back, or at least feel uneasy. An AI agent asked to do the same thing will comply immediately, format the code correctly, and write a comment explaining what the credential is for.

**AI agents are obedient, not cautious.** Their obedience is their value — and their obedience is their risk. A well-governed agent that has been told never to commit secrets will not commit secrets. An ungoverned agent will do exactly what it is asked, no matter what it is asked.

The speed × obedience × no-instinct combination is genuinely dangerous. This is the perfect storm that governance exists to prevent.

Security governance is therefore not an optional layer on top of AI development. It is the foundation that makes AI development safe to practice at all.

---

## 2. Security Across All 7 Layers

Security is not a phase or a team. It is woven through every layer of the framework.

### Layer 1 — Constitution

The security constitution defines what cannot happen, ever:

- The never-commit list (see section 5)
- `.gitignore` rules that prevent accidental staging of sensitive files
- `.claudeignore` rules that prevent sensitive files from entering the agent's context window
- Explicit data classification: RESTRICTED / CONFIDENTIAL / INTERNAL / PUBLIC

**Key practice**: The security constitution is in `CLAUDE.md` and is reviewed every six months. It is never the only security mechanism — defense in depth requires automation.

### Layer 2 — Orchestration

Security is enforced during session protocol, not only at CI gates:

- **Session start**: agent performs a diff-based scan of files changed since last session
- **During session**: agent checks each file it creates or modifies against pattern list
- **Session end**: agent performs a scan of all changed files before the final commit

**Key practice**: Agents are instructed to ask before saving any file that matches a sensitive pattern. "This file contains a string matching `api_key=`. Confirm this is a placeholder value."

### Layer 3 — Enforcement

Automated gates that run regardless of agent behavior:

- Pre-commit hooks: `gitleaks`, `trufflehog`, custom pattern scripts
- CI/CD security gates: run on every PR, block merge on failure
- Agent security review: AI-powered review of diffs for subtle issues that deterministic scanners miss
- Branch protection: no direct pushes to main, ever

**Key practice**: Deterministic tools run first, always. AI review supplements but never replaces deterministic scanning.

### Layer 4 — Observability

Security events are tracked, not just detected:

- Security incident log in `docs/SECURITY_LOG.md`
- Scan results tracked over time (trending issues per session)
- False positive rate monitored (to prevent alert fatigue)
- Credential rotation tracking (how old are each team's credentials?)

**Key practice**: If security issues per session is trending up, the cause must be identified and addressed — it means the constitution or tooling is not working.

### Layer 5 — Knowledge

Security decisions are documented and do not get re-litigated:

- Security ADRs document why specific restrictions exist
- Onboarding security module is part of every new developer's Day 1 checklist
- Security decisions logged in `DECISIONS.md` with rationale

**Key practice**: When a security rule is questioned, point to the ADR. "We made this decision on this date for these reasons. If you believe the reasons no longer apply, open a PR to revise the ADR."

### Layer 6 — Team

Security responsibility is distributed, not siloed:

- Dedicated security agent role with elevated review authority
- Security agent can block a PR merge (hard fail, not advisory)
- Champions are responsible for security compliance within their team
- Any developer can trigger a security review; only the security agent's approval unblocks

**Key practice**: The security agent is Opus-powered. No compromises on security review quality.

### Layer 7 — Evolution

The threat model evolves; the security constitution must evolve with it:

- Security constitution review every six months, mandatory
- Post-incident review within 48 hours of any security event
- New threats (new dependency vulnerabilities, new attack patterns) trigger constitution review
- Annual penetration testing or red team exercise

**Key practice**: After every security incident, add a deterministic check that would have caught it. Do not rely on everyone being more careful next time.

---

## 3. Three Scan Levels

### Level 1: Per-File Scan (Continuous)

Runs during the session, every time the agent writes or modifies a file.

**What it checks:**
- Pattern matching: `api_key=`, `password=`, `secret=`, `token=`, `/Users/`, base64 blobs of unusual length, email patterns in non-test files, IP addresses
- Context check: is this a config file with real values, or a template with placeholders?

**Speed**: Essentially free — runs in milliseconds, no API call required.

**Coverage**: Catches roughly 80% of accidental secret commits before they happen.

**Implementation in CLAUDE.md:**
```markdown
## file_security_check (run on every file write)
Before saving any file, check for:
- Strings matching: api_key=, password=, secret=, token=, Authorization:
- Absolute paths starting with /Users/, /home/
- Base64 strings longer than 40 characters in config files
- Email addresses in non-test, non-documentation files
If found: pause and ask the developer to confirm this is not a real credential.
```

### Level 2: Per-Session Scan

Runs at session start and session end.

**What it checks:**
- All files modified since last session (diff-based)
- Cross-file: if a new config file was created, does `.gitignore` include it?
- Cross-file: if new connection strings appear, are they using environment variables?

**Speed**: 10–30 seconds depending on change volume.

**Coverage**: Catches issues that span multiple files — a credential introduced in session N that only becomes a risk in session N+1 when used in a config file.

**Implementation**: Part of the session protocol in `CLAUDE.md`:
```markdown
on_session_end:
  1. Run security scan on all changed files
  2. Check .gitignore includes all new sensitive file types
  3. Confirm no hardcoded values in any config files
  4. If scan is clean: proceed to commit
  5. If scan finds issues: resolve before commit
```

### Level 3: Periodic Full-Repo Scan

Runs every fifth session and on a monthly schedule.

**What it checks:**
- All files in the repository, not just recently changed ones
- Historical: `git log` scan for secrets that may exist in older commits
- Configuration completeness: is `.gitignore` still current? Is `.claudeignore` covering all sensitive paths?
- Dependency scan: known vulnerabilities in pinned packages

**Speed**: Minutes, scheduled task, not blocking.

**Coverage**: Catches accumulated drift — a file that was safe six months ago may now contain sensitive information after incremental changes.

**Implementation**: GitHub Actions scheduled workflow running `gitleaks --source=. --log-opts="--all"` plus `trufflehog git file://. --since-commit HEAD~50`.

---

## 4. Documentation as Attack Vector

Most security thinking focuses on source code. Documentation is equally dangerous and less frequently scrutinized.

### Specific Examples of Documentation-as-Vector

**CHANGELOG.md leakage:**
```markdown
## 2026-03-01 — Session 012
- Updated Oura API key after rotation (old key: sk-oura-abc123...)
```
This is a real API key that is now in version control history forever.

**Architecture docs exposing topology:**
```markdown
## Production Infrastructure
Database host: db-prod-01.internal.company.com:5432
Redis: redis-cluster.internal:6379
```
Internal hostnames in public documentation create reconnaissance value.

**README setup instructions with real credentials:**
```markdown
## Setup
export OURA_TOKEN=your_token_here
# Note: use the team shared token: oat_eyJhbGc...
```
Even "temporary" real credentials in setup docs get committed.

**Test fixtures with real data:**
```python
# tests/fixtures/sample_health_data.py
SAMPLE_USER = {
    "user_id": 12345,  # Real user ID from production
    "name": "John Smith",
    "heart_rate": 68,
    "blood_pressure": "142/91"
}
```
Real health data in test fixtures is a GDPR incident waiting to happen.

**Screenshots in documentation:**
A screenshot of a dashboard showing real health metrics is PII disclosure, even if the file seems innocuous.

### Rule

Scan ALL files in the repository — not just `.py`, `.sql`, `.yaml`. Markdown files, `README.md`, CHANGELOG entries, and test fixtures are all in scope for security scanning.

---

## 5. The Never-Commit List

The following items must never appear in any committed file, in any form, in any branch:

```
NEVER COMMIT:
  - API keys and API tokens (any service)
  - OAuth tokens, access tokens, refresh tokens
  - Passwords and password hashes
  - Hardcoded paths to production environments
    (/prod/, /production/, specific prod hostnames)
  - PII data: names, emails, phone numbers, SSN, CPR, passport numbers
  - Health data: diagnoses, medications, biometrics, patient IDs
  - Financial data: account numbers, transaction IDs with amounts, salary data
  - Database credentials: connection strings with usernames/passwords
  - Production connection strings (any database, any service)
  - Private keys (.pem, .key files) and certificates
  - JWT secrets or signing keys
  - Webhook secrets
  - SSH private keys
  - Internal hostnames and IP ranges (unless in a `.gitignore`'d file)
  - Third-party service credentials (Stripe, Twilio, SendGrid, etc.)
```

**If it looks like a secret, treat it as a secret.** The cost of a false positive (adding a non-sensitive string to `.gitignore`) is minimal. The cost of a false negative (committing a real credential) is a security incident.

**Once committed, always compromised.** A credential committed and then reverted in the next commit is still in the git history. Treat any credential that has touched a remote repository as compromised and rotate it immediately.

---

## 6. Incident Response Protocol

When a security incident is detected — a secret in a commit, PII in a log, credentials in documentation — follow this protocol immediately:

### STOP
Cease all AI-assisted work immediately. Do not continue the session. Do not commit anything else.

*Time: immediate, within seconds of detection.*

### ASSESS
Determine scope: What was exposed? What type of credential or data? When was it committed? Has it been pushed to remote? Is the repository public or private?

*Time: within 5 minutes.*

### CONTAIN
If credential: invalidate it immediately at the source (rotate the API key, revoke the token). If PII: document what was exposed and who may have accessed it. If committed to remote: assume it has been observed, even if the repository is private.

*Time: within 15 minutes for credential rotation.*

### FIX
Remove the secret from the codebase. Replace with an environment variable or secrets manager reference. Clean the git history using `git filter-branch` or `git filter-repo` if necessary.

*Time: within 1 hour.*

### VERIFY
Run a full repository scan with `gitleaks` and `trufflehog` to confirm the secret is fully removed, including from git history. Confirm the new credential (if rotated) is working correctly.

*Time: within 2 hours of initial detection.*

### LOG
Document the incident in `docs/SECURITY_LOG.md`:

```markdown
## Incident: [date]
- Type: [API key | PII | credential | other]
- Source: [which file, which commit]
- Detected: [how was it found]
- Contained: [what was done and when]
- Verified: [confirmation that clean]
- Root cause: [why it happened]
```

*Time: within 24 hours.*

### PREVENT
Add a deterministic check that would have caught this incident. Update `.gitignore`, `.claudeignore`, and pre-commit hook patterns. Do not rely on everyone being more careful — implement a check.

*Time: within 48 hours.*

### REVIEW
Review the security constitution and the session protocol. Is there a rule that was missing? Is there a check that failed? Update `CLAUDE.md` if a rule was absent or insufficient.

*Time: within 1 week.*

---

## 7. Security Maturity Model

| Level | Description | What Exists |
|-------|-------------|-------------|
| 0 | No security awareness | Secrets in code, no `.gitignore`, no scanning |
| 1 | Basic hygiene | `.gitignore` exists, manual spot checks, developer awareness |
| 2 | Agent-aware security | Security rules in `CLAUDE.md`, agent performs file checks, session scans |
| 3 | Automated enforcement | Pre-commit hooks, CI/CD security gates, dedicated security agent for PRs, incident response protocol exists |
| 4 | Continuous monitoring | Automated threat detection, dependency scanning, credential rotation tracking, security metrics dashboard |
| 5 | Compliance-grade | Continuous compliance monitoring, automated audit trails, penetration testing, regulatory-ready documentation |

Teams implementing this framework should reach Level 3 within 8–12 weeks of beginning the rollout. Level 4 and 5 are appropriate for regulated industries or enterprise deployments.

**The HealthReporting case study** reached Level 3 in two weeks for a solo developer — 0 secrets leaked across 137 commits with security scanning active from week 3.

---

## 8. Tooling Stack

### Deterministic Tools (Always Run First)

These tools find exact patterns. They have near-zero false negatives for patterns they know. They should run on every commit and every PR.

**gitleaks**
```bash
# Install
brew install gitleaks

# Scan current repository
gitleaks detect --source=. --verbose

# Scan git history
gitleaks detect --source=. --log-opts="--all" --verbose

# Run as pre-commit hook (add to .pre-commit-config.yaml)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**trufflehog**
```bash
# Install
brew install trufflehog

# Scan git history (last 50 commits)
trufflehog git file://. --since-commit HEAD~50 --only-verified

# Scan entire history
trufflehog git file://. --only-verified
```

**git-secrets**
```bash
# Install
brew install git-secrets

# Configure for AWS patterns
git secrets --register-aws

# Add custom patterns
git secrets --add 'oura_token=[A-Za-z0-9_-]{40}'
git secrets --add 'ANTHROPIC_API_KEY=sk-ant-[A-Za-z0-9_-]+'

# Install hooks
git secrets --install
```

**Custom pre-commit pattern checks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: no-hardcoded-paths
        name: Check for hardcoded absolute paths
        entry: grep -rn "/Users/" --include="*.py" --include="*.yaml" --include="*.sql"
        language: system
        pass_filenames: false

      - id: no-env-in-commit
        name: Check .env is not staged
        entry: bash -c 'git diff --cached --name-only | grep -q "^\.env" && echo "ERROR: .env file staged" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

### Probabilistic Tools (AI-Based Review)

These tools understand context. They catch secrets that deterministic tools miss (e.g., a variable named `connection_params` that contains an embedded password). They also have false positives that deterministic tools do not.

**Security review agent (Opus-powered)**:
- Reviews PR diffs for context-aware issues
- Understands whether a string is a real credential or an example
- Detects PII in documentation that pattern matchers would not flag
- Evaluates whether new integrations open attack vectors

**Implementation in CI/CD:**
```yaml
# .github/workflows/ai-security-review.yml
name: AI Security Review
on: pull_request
jobs:
  security-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run deterministic scan
        run: gitleaks detect --source=. --verbose
      - name: AI security review
        run: |
          # Feed diff to security review agent
          # Agent returns: PASS / WARN / FAIL with specific findings
          # Post findings as PR review comment
```

**Principle**: Deterministic first. AI second. Never AI alone for security — it can be convinced to approve things that deterministic tools would catch.

---

## 9. The Confidence Problem

The most important characteristic of AI-generated code from a security perspective: **the agent presents secure and insecure code with equal confidence and equal formatting quality**.

A developer reviewing AI-generated code sees:
- Clean syntax
- Proper formatting
- Logical structure
- Professional comments

None of these visual signals indicate whether the code is secure. A hardcoded credential, an SQL injection vulnerability, or a path traversal issue looks exactly as polished as correct code. The glance test fails completely for security.

### How to Compensate

**Never trust AI security claims.** If an agent says "this code is secure," that statement has no more validity than any other generated text. The agent is reporting what it expects to be true based on training patterns, not what it has verified.

**Run deterministic tools on every AI-generated file.** The agent's confidence is irrelevant. The scanner's result is what matters.

**Apply the "what would a malicious version look like?" test during review.** For any AI-generated authentication or authorization code, ask: "If this code were written to allow unauthorized access, how would it be different from what I'm looking at?" If the answer is "not very different," the code needs deeper review.

**Test security assumptions explicitly.** AI-generated code will often have correct-looking authorization checks. Test the specific boundary conditions: unauthenticated requests, requests with invalid tokens, requests with valid tokens but wrong permissions. Do not assume the AI implemented the edge cases because the happy path looks correct.

**Use a security checklist that cannot be overridden by confidence.** The review checklist exists specifically to counteract the confidence problem — it forces explicit verification of specific security properties, regardless of how the code looks.

---

*Related guides: [Compliance Guide](./compliance-guide.md) | [Rollback and Recovery](./rollback-recovery.md) | [AI Code Quality](./ai-code-quality.md) | [Model Routing](./model-routing.md)*
