# Pattern: Knowledge Decay

## Problem

MEMORY.md is append-only in practice. Sessions add entries. Nothing removes them. After
six months, the file contains conflicting information from different project eras, references
to deleted files, workarounds for resolved bugs, and architectural notes from designs that
were later refactored. The agent reads all of it and treats it as equally valid.

Context degradation compounds: each stale entry slightly corrupts the agent's understanding.
Individually imperceptible. Collectively, after 50 sessions, the agent confidently suggests
solutions to problems that are already solved, using patterns that were explicitly abandoned.

## Solution

Category-based knowledge lifespans with automatic decay. Every entry has a category,
a date, and an expiry condition. At session start, the governance sync scans MEMORY.md,
flags entries past their lifespan, and proposes compression, archival, or deletion.
A hard 200-line cap ensures active context stays lean regardless of session count.

## When to Use This Pattern

- Projects past 20 sessions (MEMORY.md accumulation becomes noticeable)
- Any project where architectural decisions have changed (stale context risk is high)
- Teams where multiple developers contribute to MEMORY.md (conflicting entries likely)
- Before implementing a new architectural pattern (old context may interfere)

## Knowledge Categories

| Category | Expiry | Default Action |
|----------|--------|----------------|
| Convention | permanent | Never decay |
| Architecture | until superseded | Archive to ADR |
| Session summary | 30 days | Compress to one line |
| Bug pattern | until fix verified | Archive 2 weeks after fix |
| Workaround | until condition met | Delete when resolved |
| Performance | 60 days | Re-validate or delete |
| API quirk | 90 days | Re-verify or delete |

## Implementation

### Entry Format

Every entry includes category, date, and expiry:

```markdown
## [Category] — [Title]
Date: YYYY-MM-DD
Expires: [date | permanent | when-superseded | until: condition]
Tags: [category tags]

[2-5 lines of content]
```

### Lifecycle Check at Session Start

As part of the governance sync (not blocking — runs alongside other checks):

```markdown
on_session_start knowledge_check:
  1. Read MEMORY.md
  2. For each entry:
     a. Check if current date exceeds Expires date
     b. Check if referenced files/components exist
     c. Check if entry conflicts with ARCHITECTURE.md or accepted ADRs
  3. Collect flagged entries
  4. Present lifecycle report if any flags found
  5. If user confirms: compress/archive/delete flagged entries
  6. If user skips: flag will repeat next session
```

### Compression Rule

Entries older than 30 days (and not marked permanent) compress to:
```
[YYYY-MM-DD] [Original title]: [one-sentence summary of what was decided or learned]
```

Full content moves to MEMORY_ARCHIVE.md before compression.

### Archival Rule

Entries older than 90 days, or confirmed no longer relevant:
1. Append to MEMORY_ARCHIVE.md with archival date and reason
2. Remove from MEMORY.md

### 200-Line Cap

When MEMORY.md reaches 200 lines:
1. Identify all non-permanent entries (session summaries, workarounds, observations)
2. Compress oldest 20% to one-line entries
3. If still over limit: archive oldest compressed entries to MEMORY_ARCHIVE.md
4. Permanent entries (conventions, active architecture) are never compressed or archived

## Example: Decay in Practice

**Session 1 (February)** — add workaround entry:
```markdown
## Workaround — Withings OAuth token refresh
Date: 2026-02-10
Expires: until: ADR-007 implements token rotation service
Tags: workaround

Withings refresh tokens expire after 30 days if unused. Manual rotation required.
Run scripts/rotate_token.sh monthly until automated service is live.
```

**Session 8 (April)** — ADR-007 is accepted, token service is live:
```markdown
## Architecture — Token rotation service
Date: 2026-04-03
Expires: when-superseded
Tags: architecture

Central token rotation service handles all OAuth refresh tokens automatically.
See ADR-007. Manual rotation scripts are deprecated.
```

**Session 9 — lifecycle check:**
```
📚 Knowledge lifecycle check:

FLAGGED FOR REVIEW:
- "Workaround — Withings OAuth token refresh" (Feb 10)
  Expiry condition: "until: ADR-007 implements token rotation service"
  ADR-007 accepted April 3. Condition appears met.
  Suggested action: Delete entry, archive reference.

Clean up? [Y/skip]
```

After confirmation, the workaround is removed. The agent no longer suggests running
rotation scripts manually.

## Anti-Patterns

**Expiry: permanent on everything** — defeats the purpose. Only conventions and accepted
architecture decisions are genuinely permanent. Session summaries, workarounds, and
observations are temporary by nature. Mark them accordingly.

**No dates on entries** — makes automated age checks impossible. Every entry must have a date.
Treat undated entries as 90+ days old (archive-eligible).

**Skipping the check indefinitely** — the check will repeat every session until addressed.
If the user skips it 3+ times, surface a stronger prompt: "MEMORY.md has 15 entries past
their lifespan. Context quality is degrading. Strongly recommend cleanup."

## Related

- [docs/knowledge-lifecycle.md](../docs/knowledge-lifecycle.md) — full specification
- [templates/MEMORY.md](../templates/MEMORY.md) — MEMORY.md template with lifecycle format
- [docs/architecture.md](../docs/architecture.md) — Layer 5 (Knowledge) in the 7-layer stack
- [commands/health-check.md](../commands/health-check.md) — /health-check includes lifecycle assessment
