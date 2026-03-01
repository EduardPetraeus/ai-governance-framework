# Governance Flow

The complete governance pipeline from constitution to production: CLAUDE.md, AGENTS.md, MCP, CI, Prod.

Each stage enforces a specific governance boundary. A change that passes one stage is not trusted — it must pass every stage before reaching production. The flow is sequential: earlier stages catch intent-level violations, later stages catch implementation-level violations.

---

## Stage 1: CLAUDE.md — Constitutional Layer

The agent reads CLAUDE.md at session start. This is the first governance boundary: before any code is written, the agent knows what it may and may not do.

| Column | Detail |
|---|---|
| **Enforced** | Project conventions, security rules, session protocol, forbidden patterns, file limits, naming standards, scope confirmation requirement |
| **Artifacts produced** | Session start log (model identification, sprint status, proposed scope), scope confirmation record |
| **Responsible** | The AI agent (reads and internalizes), the human operator (confirms scope) |
| **On-failure action** | If CLAUDE.md is missing: agent operates ungoverned (Level 0). If CLAUDE.md exists but agent ignores a rule: drift detector catches it at next scan, CI catches it at PR time, quality gate agent catches it at session end |

CLAUDE.md is Layer 1 enforcement — governance by instruction. The agent complies because the rules are in its context window. This is necessary but not sufficient: context-only enforcement degrades under long sessions, complex tasks, and model updates.

---

## Stage 2: AGENTS.md — Portable Bridge

AGENTS.md extends governance to non-Claude tools operating on the same repository. When a developer uses Copilot for inline suggestions or Aider for a quick patch on the same branch, AGENTS.md ensures they follow the same conventions and security rules.

| Column | Detail |
|---|---|
| **Enforced** | Cross-tool naming conventions, security rules, build/test/lint commands, forbidden patterns — the portable subset of CLAUDE.md |
| **Artifacts produced** | None directly (AGENTS.md is read-only context for other tools). Indirectly: code that conforms to shared conventions regardless of which tool generated it |
| **Responsible** | Every AI tool that reads AGENTS.md (Copilot, Cursor, Windsurf, Aider). The human operator maintains sync between CLAUDE.md and AGENTS.md |
| **On-failure action** | If AGENTS.md is missing: non-Claude tools operate without governance context. If AGENTS.md diverges from CLAUDE.md: CI catches convention violations at PR time. The generator script (`scripts/generate_agents_md.py`) can automate sync |

AGENTS.md is Layer 1 enforcement extended horizontally. It does not add a new governance layer — it ensures the constitution's reach covers every tool, not just Claude Code.

---

## Stage 3: MCP — Tool Access Control

When agents have tool access via Model Context Protocol, governance must enforce constraints before the agent acts — not after. MCP enforcement is real-time: write operations, API calls, and database queries happen at execution speed with real-world side effects.

| Column | Detail |
|---|---|
| **Enforced** | Server allowlists per agent role, environment segregation (dev/staging/prod), rate limits (per-server and global), cascade write chain limits, production access block |
| **Artifacts produced** | MCP audit log (every tool call with intent, arguments, result, timestamp), rate limit alerts, kill switch activation records |
| **Responsible** | The MCP governance layer (validates before each call), the human operator (reviews audit log at session end, authorizes production access) |
| **On-failure action** | Unauthorized server connection: MCP kill switch fires, session halts. Rate limit exceeded: agent pauses and reports. Production environment detected without authorization: immediate halt. Cascade write chain (3+ consecutive writes): pause for confirmation |

MCP enforcement is Layer 3 applied to the agent's tool surface. See [docs/mcp-governance.md](mcp-governance.md) for the six governance patterns and full configuration reference.

---

## Stage 4: CI — Automated Gates

CI runs on every push and every pull request. It enforces governance rules that cannot be left to agent compliance alone: structural checks, secret scanning, governance file validation, and AI-powered code review.

| Column | Detail |
|---|---|
| **Enforced** | CHANGELOG updated with source changes, no secrets in commits, naming convention compliance, output contract validation (Level 2+), health score threshold (Level 3+), constitutional inheritance validity (Level 3+), agent registry compliance (Level 3+) |
| **Artifacts produced** | CI check results (pass/fail per gate), AI PR review comments, health score report, governance violation annotations on the PR |
| **Responsible** | CI platform (GitHub Actions, GitLab CI, CircleCI, Bitbucket Pipelines, or Azure DevOps). The human reviewer acts on CI results before merging |
| **On-failure action** | Blocking gates: PR cannot merge. Advisory gates: warnings annotated on the PR. Health score below threshold: merge blocked until governance files are updated. Secret detected: commit rejected at pre-commit hook or PR level |

CI is Layer 3 enforcement made deterministic. Unlike CLAUDE.md (which depends on agent compliance) and MCP (which depends on runtime configuration), CI gates are binary: the check passes or the PR does not merge.

---

## Stage 5: Prod — Production Deployment

Production is the final governance boundary. Changes that passed CLAUDE.md, AGENTS.md, MCP, and CI still require additional validation before reaching users.

| Column | Detail |
|---|---|
| **Enforced** | Deployment approval gates, feature flag rollout (gradual exposure), rollback automation, incident-to-rule feedback loop |
| **Artifacts produced** | Deployment record (who approved, when, which changes), feature flag state log, incident reports (if issues arise), governance rule updates (incident triggers rule tightening) |
| **Responsible** | The deployment owner (approves production release), the on-call engineer (monitors post-deployment), the governance steward (updates rules based on incidents) |
| **On-failure action** | Production incident traced to an AI-generated change: automatic rollback, incident report generated, the governance rule that should have caught the issue is identified and added to CLAUDE.md and CI gates. This is the anti-fragile loop — production failures strengthen governance |

Production enforcement is where governance becomes anti-fragile. Every incident that reaches production reveals a gap in the earlier stages. The incident response procedure identifies which stage should have caught the issue and adds enforcement at that stage. Over time, fewer issues reach production because earlier stages accumulate enforcement rules from every incident.

---

## End-to-end example: Agent modifies auth module

An agent is tasked with updating the login flow in `src/auth/login.py`. Here is exactly what happens at each governance stage.

### Stage 1: CLAUDE.md at session start

The agent reads CLAUDE.md and encounters auth-specific constraints:

```markdown
## security_protocol

auth_modules:
  paths: ["src/auth/"]
  constraints:
    - All changes to src/auth/ require human approval before execution
    - No new dependencies in auth modules without security review
    - Password handling must use bcrypt with minimum 12 rounds
    - Session tokens must be generated with secrets.token_urlsafe(32)
    - No plaintext credential storage — not in code, not in config, not in logs
  review: "Changes to auth modules are high-risk. Present the full diff
           and wait for explicit approval before committing."
```

The agent announces the constraint during session start:

```
Session start — governance sync complete.

Sprint goal: "Improve login UX and add rate limiting"
Proposed scope: Update src/auth/login.py to add login rate limiting.

NOTE: src/auth/ is under security_protocol.auth_modules.
All changes require human approval before execution.
I will present the full diff before committing.

Confirm scope?
```

The human confirms. The agent begins work but knows it must pause before any commit to auth files.

### Stage 2: AGENTS.md extends coverage

A team member uses Cursor to make a quick CSS fix on the same branch. Cursor reads AGENTS.md:

```markdown
## security

Forbidden in all files:
- Hardcoded credentials, API keys, tokens
- Plaintext password storage
- Direct database connection strings

Files requiring extra care:
- src/auth/** — security-critical, changes need review
- src/config/** — environment configuration, no secrets
```

Cursor sees the auth warning. If the CSS fix inadvertently touches an auth-adjacent file, the AGENTS.md context flags it. The portable bridge ensures that even tools without the full session protocol know about high-risk paths.

### Stage 3: MCP enforcement during the session

The agent needs to test the rate limiting implementation against the development database. It attempts to connect via MCP:

```
MCP_AUDIT | 2026-03-01T10:15:22Z | session=047 | server=database_dev |
  tool=query | args={query: "SELECT count(*) FROM login_attempts
  WHERE created_at > NOW() - INTERVAL '1 hour'"} |
  result=rows_returned=1 | duration_ms=45 | status=success
```

The agent then attempts to verify against the staging database:

```
MCP_KILL_SWITCH TRIGGERED

Trigger: PRODUCTION ENVIRONMENT DETECTED
Server URL contains: staging-db.internal (matches forbidden pattern "*staging*")
Last 3 tool calls:
  1. database_dev:query — login_attempts count — success
  2. database_dev:query — rate_limit_config select — success
  3. database_staging:query — BLOCKED before execution

The current session environment is "development."
Staging database access requires explicit human authorization.

Present your authorization to continue, or I will proceed using
development data only.
```

The human declines staging access. The agent continues with development data.

### Stage 4: CI gates on the pull request

The agent commits the changes and opens a PR. CI runs five checks:

```
governance-check .......................... PASS
  ✓ CHANGELOG.md updated (new entry for rate limiting feature)
  ✓ No secrets detected in diff (gitleaks: 0 findings)
  ✓ CLAUDE.md not modified (no constitution change)

ai-pr-review .............................. PASS (with comments)
  ✓ Code review: rate limiting implementation follows existing patterns
  ✓ Auth module change flagged: "src/auth/login.py modified —
     verify human approval was obtained per security_protocol"
  ⚠ Advisory: consider adding integration test for rate limit window

security-scan ............................. PASS
  ✓ No hardcoded credentials
  ✓ bcrypt usage confirmed (rounds=12)
  ✓ No new dependencies added

output-contract-validation ................ PASS
  ✓ confidence: 82 (within 85 ceiling)
  ✓ not_verified: ["rate limit behavior under concurrent load"]
  ✓ architectural_impact: "none — follows existing auth module pattern"

health-score .............................. PASS
  ✓ Score: 87 (threshold: 60)
  ✓ No governance degradation from this PR
```

All blocking gates pass. The AI PR review adds an advisory comment about integration testing. The human reviewer sees both the CI results and the advisory, reviews the auth diff, and approves the merge.

### Stage 5: Production deployment

The auth change reaches the deployment pipeline:

```
Deployment checklist — src/auth/login.py modified:
  [x] CI gates passed (all 5 checks)
  [x] Human reviewer approved PR
  [x] Auth module change has documented approval (session 047 log)
  [x] Feature flag: login_rate_limiting = enabled for 5% of users
  [x] Rollback plan: revert to previous login.py (commit abc1234)
  [x] Monitoring: alert on login failure rate > 2% (baseline: 0.3%)
```

The change deploys behind a feature flag at 5% rollout. Monitoring tracks login failure rates. If the rate exceeds 2%, the feature flag disables automatically and the on-call engineer is notified.

After 48 hours at 5% with no anomalies, the rollout increases to 25%, then 100%.

If an incident had occurred — say the rate limiter blocked legitimate users due to a shared IP issue — the incident response would:

1. Disable the feature flag immediately
2. Generate an incident report
3. Identify the governance gap: the `not_verified` field in the output contract already flagged "rate limit behavior under concurrent load" — the gap was that this known uncertainty was not tested before deployment
4. Add a new CI gate rule: auth changes with `not_verified` items related to concurrency must include a load test result before merge
5. Update `## security_protocol` in CLAUDE.md: auth module changes that affect rate limiting require a load test in the session scope

This is the anti-fragile loop. The production incident did not just fix the bug — it strengthened every earlier governance stage to prevent recurrence.

---

## State drift

### Definition

State drift occurs when the agent's working model of the project diverges from actual repository state during an active session. It is an in-session problem: the agent read governance files at session start, but those files (or the code they describe) have changed since the read.

State drift is distinct from two related concepts:

- **Architectural drift** is a cross-session problem: the codebase diverges from recorded architectural decisions over weeks or months of development. The drift detector agent measures this.
- **Governance drift** is a maintenance problem: governance files diverge from framework standards over time — missing CHANGELOG entries, stale MEMORY.md, broken cross-references. The health score calculator measures this.

State drift is narrower and more immediate. It happens mid-session when an external process modifies a file the agent has already read. The agent's decisions are based on stale context.

**Common causes:**

- Another developer pushes changes to the same branch while the agent session is active
- A parallel CI pipeline modifies governance files (auto-formatting, auto-generated docs)
- The human operator edits files in a separate editor while the agent is working
- A second agent session (on a different task) modifies shared configuration files

### Detection

Two mechanisms detect state drift:

**1. Drift detector agent** — periodic structural detection. The [drift detector agent](../agents/drift-detector-agent.md) runs on a schedule (typically at sprint start) or on demand. It compares all governance files against framework templates, checks cross-references, validates CHANGELOG freshness, and produces a health score. This catches governance drift and architectural drift between sessions, not within a session.

**2. Session re-read** — real-time in-session detection. The agent monitors file modification timestamps for every governance file it read at session start. When a file the agent has read is modified by an external process during the session, the agent detects the staleness and alerts:

```
STATE DRIFT DETECTED

File modified externally during this session:
  CLAUDE.md — last read at session start (10:15:22)
             — modified externally at 10:47:03 (31 minutes after read)

Changes detected:
  - Section ## security_protocol: new constraint added for src/payments/
  - Section ## conventions: import ordering rule updated

Impact on current session:
  - Current scope does not touch src/payments/ — no immediate conflict
  - Import ordering rule change MAY affect files modified this session

Options:
  (a) Force refresh — re-read all governance files now and recheck scope
  (b) Continue — current scope is unaffected by the detected changes
  (c) Pause — stop work and review the external changes before continuing

Which do you prefer?
```

### Resolution

**1. Force refresh** — for moderate drift where the session can continue after updating context.

The agent re-reads all governance files mid-session, announces the re-read, and rechecks the current scope against the updated rules. If the updated rules do not conflict with the current scope, work continues. If a conflict is detected, the agent pauses and presents the conflict for human resolution.

```
FORCE REFRESH — re-reading governance files

Files re-read:
  ✓ CLAUDE.md (modified externally — updated constraints loaded)
  ✓ PROJECT_PLAN.md (no changes since session start)
  ✓ CHANGELOG.md (no changes since session start)
  ✓ ARCHITECTURE.md (no changes since session start)

Scope recheck:
  Current scope: "Add login rate limiting to src/auth/login.py"
  New constraints: src/payments/ restrictions added (not in scope — no conflict)
  Import ordering: updated rule loaded — will apply to remaining work

Continuing with refreshed context.
```

**2. Re-onboard** — for severe drift where the session context is fundamentally stale.

When the health score drops below 50, or drift items include critical governance changes (security protocol modified, session protocol changed, architectural decisions revised), a force refresh is insufficient. The agent invokes the [onboarding agent](../agents/onboarding-agent.md) to reconstruct project context from scratch before continuing:

```
SEVERE DRIFT DETECTED — re-onboarding required

Health score: 43 (was 87 at session start)
Critical drift items:
  - CLAUDE.md security_protocol rewritten (12 lines changed)
  - ARCHITECTURE.md component inventory updated (3 components added)
  - PROJECT_PLAN.md sprint goal changed

Current session context is fundamentally stale.
Invoking onboarding agent to reconstruct project context.

[Onboarding agent runs full governance sync]
[Session effectively restarts with fresh context]
[Previous session work is preserved — scope is reconfirmed against new context]
```

### CLAUDE.md configuration for state drift detection

Add this block to your project's CLAUDE.md to enable in-session state drift detection:

```markdown
## state_drift_detection

monitoring:
  enabled: true
  check_interval: "before each task"
  files_monitored:
    - CLAUDE.md
    - PROJECT_PLAN.md
    - CHANGELOG.md
    - ARCHITECTURE.md
    - AGENTS.md

on_drift_detected:
  severity_low:
    # Non-governance files modified, or governance files modified in
    # sections unrelated to current scope
    action: "announce drift, continue working"
  severity_medium:
    # Governance file modified in a section relevant to current scope
    action: "force refresh — re-read all governance files, recheck scope"
  severity_critical:
    # Health score below 50, or security_protocol / session_protocol modified
    action: "halt work, invoke onboarding agent for full re-onboard"

force_refresh_procedure:
  1. Re-read all files listed in files_monitored
  2. Announce which files changed and what sections were affected
  3. Recheck current scope against updated constraints
  4. If no conflict: continue with refreshed context
  5. If conflict detected: pause and present options to the human

re_onboard_threshold:
  health_score_below: 50
  critical_sections_changed:
    - security_protocol
    - session_protocol
    - project_context
```

---

## Further reading

- [docs/session-protocol.md](session-protocol.md) — the full session lifecycle specification
- [docs/mcp-governance.md](mcp-governance.md) — MCP tool access governance patterns
- [docs/enforcement-hardening.md](enforcement-hardening.md) — enforcement levels L1 through L3
- [patterns/blast-radius-control.md](../patterns/blast-radius-control.md) — limiting session damage scope
- [patterns/human-in-the-loop.md](../patterns/human-in-the-loop.md) — when human judgment is required
- [agents/drift-detector-agent.md](../agents/drift-detector-agent.md) — structural drift detection between sessions
