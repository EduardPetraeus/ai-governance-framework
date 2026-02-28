# Pattern: Session Replay

## Problem

Something went wrong. The change was AI-generated. You have git history showing what changed
but no record of why the agent made the specific choices it made. What context was it
operating from? What alternatives did it consider? What was its confidence? Were there any
flags that should have triggered closer review?

Without session replay, post-incident investigation is archaeology: reading commits backward,
inferring reasoning from code. With session replay, the reasoning is recorded at the time
it happens.

## Solution

Auto-generate a structured session log at every session end. The log records metadata,
task chain with decision rationale, context used, confidence scores, and governance events.
Store in `.session-logs/` (gitignored). Retain 90 days. Use for post-incident investigation,
compliance auditing, and onboarding demonstration.

## When to Use

- Level 3+: any project shipping to production
- Any project with security, compliance, or audit requirements
- Teams where multiple developers run AI sessions (cross-session traceability needed)
- After any production incident involving AI-generated code

## When NOT to Use

- Solo developers on non-production projects where CHANGELOG.md provides sufficient audit trail
- Exploratory or prototype sessions where session reasoning does not need to be preserved beyond the session
- Projects where the overhead of log maintenance exceeds the probability of needing a post-incident investigation

## Implementation

### Directory Setup

```bash
mkdir .session-logs
echo ".session-logs/" >> .gitignore
```

### Log Generation at Session End

The `/end-session` command generates the log. Add to session end protocol in CLAUDE.md:

```markdown
on_session_end:
  [existing steps...]

  7. Generate session log:
     - Write to .session-logs/session-YYYY-MM-DD-NNN.md
     - Include: metadata, task chain, decisions, context used, governance events
     - NNN = three-digit session number from current CHANGELOG.md count
     - If task reporting ran throughout: log will be complete
     - If task reporting was skipped: log metadata only, mark governance_compliance: partial
```

### Log Template

```markdown
# Session Log — YYYY-MM-DD-NNN

## Metadata
- Session: NNN
- Date: YYYY-MM-DD
- Model: [model name]
- Developer: [username]
- Duration: [N] minutes
- Tasks completed: [N] / [M scoped]
- Governance compliance: [complete | partial | none]

## Scope
[scope confirmed at session start]

## Governance Events
- Governance sync: [result]
- Security scans: [result]
- Kill switch: [not triggered | trigger and outcome]
- Knowledge lifecycle: [flags if any]

## Task Chain
### Task 1: [name]
- Confidence: [N]%
- Files: [created/modified list]
- Context used: [MEMORY entries, ADRs, architecture sections]
- Decision: [key reasoning if non-trivial]

[continue for all tasks]

## Session Summary
[2-4 sentences]
```

### Retention Policy

```markdown
# In CLAUDE.md or project documentation:
session_log_retention:
  local: 90 days
  enterprise: push to audit system, retain per compliance requirements
  cleanup: delete logs older than retention period at session start
```

## Using Session Logs

### Post-Incident

1. Identify approximate date range when the bug was introduced
2. List sessions from that range: `ls .session-logs/ | sort`
3. For each candidate session, check the task chain for tasks touching the affected component
4. Review decision points: was the bug due to wrong reasoning, wrong context, or missed scope?
5. Check governance events: were there confidence flags that should have triggered review?

### Compliance Audit

Provide: session log (who ran it, what model, what scope, governance events), git commits
(what changed), PR review comments (what was reviewed by whom). Together these form the
AI governance audit trail.

### Pattern Extraction

Review sessions with high confidence, clean governance events, and zero kill switch triggers.
Extract: how was scope defined? What context was explicitly loaded? What made decisions clean?
Feed patterns back into MEMORY.md and session protocol improvements.

## Anti-Patterns

**Committing session logs** — session logs contain potentially sensitive decision rationale
and architectural context. Keep them gitignored and manage them locally or via a separate
audit system.

**Relying on session logs instead of CHANGELOG.md** — session logs record reasoning;
CHANGELOG.md records outcomes. Both are needed. Session logs are ephemeral (90 days);
CHANGELOG.md is permanent.

**Generating logs only for incidents** — logs are most useful when they are comprehensive.
A log from a clean session that preceded an incident helps establish the baseline. Generating
logs retroactively is impossible.

## Related Patterns

- [docs/session-replay.md](../docs/session-replay.md) — full specification
- [docs/kill-switch.md](../docs/kill-switch.md) — kill switch events are recorded in session logs
- [commands/end-session.md](../commands/end-session.md) — /end-session generates the log
- [docs/architecture.md](../docs/architecture.md) — Layer 4 (Observability) in the 7-layer stack
