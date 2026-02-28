# Knowledge Lifecycle: When to Remember, When to Forget

## The Problem With Infinite Memory

MEMORY.md grows every session. After 50 sessions it contains 2,000 lines of accumulated
context. The agent reads ALL of it at session start. Most of it is irrelevant. Some of it
is wrong — architecture decisions that were later reversed, patterns that were abandoned,
workarounds for bugs that are now fixed.

**Stale knowledge is worse than no knowledge.** It causes the agent to:
- Suggest patterns that were tried and abandoned in session 15
- Reference architecture that was refactored two months ago
- Repeat solutions to problems that have already been solved
- Build false confidence from outdated context ("we've handled this before" — but differently now)

The agent cannot distinguish between fresh knowledge and stale knowledge. Both are text.
Both read with equal confidence. Only the knowledge lifecycle protocol provides this distinction.

---

## Knowledge Categories and Lifespans

Different knowledge types have different valid lifespans. Treating all knowledge as equally
permanent is the root cause of context degradation.

```
┌──────────────────────────┬───────────────────┬──────────────────────┐
│ Category                 │ Lifespan          │ Decay Action         │
├──────────────────────────┼───────────────────┼──────────────────────┤
│ Architecture decisions   │ Until superseded  │ Move to ADR archive  │
│ Session summaries        │ 30 days active    │ Compress to 1 line   │
│ Bug patterns             │ Until fix verified│ Archive after 2 weeks│
│ Convention decisions     │ Permanent         │ Never decay          │
│ Temporary workarounds    │ Until proper fix  │ Delete when resolved │
│ Performance observations │ 60 days           │ Re-validate or delete│
│ External API quirks      │ 90 days           │ Re-verify or delete  │
└──────────────────────────┴───────────────────┴──────────────────────┘
```

### Category Details

**Architecture decisions** — decisions about system structure, technology choices, and
fundamental patterns. Valid until a conscious decision reverses them. When a decision is
reversed, it does not disappear — it becomes an ADR entry with Status: Superseded.
The history is preserved; the current context reflects the new decision.

**Session summaries** — what happened in session N. Relevant for cross-session continuity
but not for long-term context. After 30 days, compress to a single line (date, summary of
outcome). After 90 days, archive to MEMORY_ARCHIVE.md.

**Bug patterns** — recurring failure modes worth remembering. Valid until the underlying
issue is fixed and the fix is verified in production. Once resolved, archive with the date
of resolution and a reference to the commit that fixed it.

**Convention decisions** — naming rules, formatting choices, file structure decisions.
These are permanent unless an explicit convention change is made. Never decay automatically.

**Temporary workarounds** — "until X is fixed, do Y instead." These have explicit expiration
conditions. Monitor for resolution; delete aggressively when resolved. Stale workarounds that
are no longer needed but remain in MEMORY.md cause the agent to apply them unnecessarily.

**Performance observations** — "X is slow because of Y." Valid for 60 days or until the
observed component changes. Profiling data becomes stale fast. Re-validate or delete.

**External API quirks** — "service X behaves differently than documented." Valid for 90 days.
APIs change. A quirk noted in March may be fixed by June. Set an explicit re-verify date.

---

## The Decay Protocol

At every session start, as part of governance sync, scan MEMORY.md for knowledge that has
reached its decay threshold. Present the findings before proceeding with work.

### Decay Checks

**Age check**: flag entries older than their category lifespan based on the entry's date stamp.
Every MEMORY.md entry should have a date. Entries without dates are treated as 90+ days old.

**Relevance check**: flag entries that reference files, functions, or components that no
longer exist. The agent can verify this by checking file system state against referenced paths.

**Conflict check**: flag entries that contradict current ARCHITECTURE.md or accepted ADRs.
If MEMORY.md says "we use pattern X" and ARCHITECTURE.md says "pattern X was replaced by Y
in milestone 3," the MEMORY.md entry is stale and potentially harmful.

**Compression**: entries older than 30 days and not marked permanent get compressed to
one-line summaries. The full detail is archived; the active context stays lean.

**Archival**: entries older than 90 days move to MEMORY_ARCHIVE.md, out of active context.
MEMORY_ARCHIVE.md is not read at session start. It is available for explicit lookup when
investigating historical decisions.

### Decay Report Format

Present at session start (before any work):

```
📚 Knowledge lifecycle check:

FLAGGED FOR REVIEW:
- 3 session summaries older than 30 days → ready to compress
- 1 entry references src/connectors/old-api.py (file deleted) → ready to remove
- 2 entries conflict with ADR-003 (connector pattern changed) → flagged for review

PROPOSED ACTIONS:
- Compress 3 session summaries to one-line entries
- Remove reference to deleted file
- Review conflicting entries: [entry text] vs [ADR-003 decision]

Clean up now? [Y/skip — will be flagged again next session]
```

---

## Active Context Window Management

MEMORY.md has a hard size limit: **200 lines maximum**.

When MEMORY.md approaches or exceeds the limit:

1. **Compress oldest entries first**: oldest session summaries compress to one line.
   Format: `[YYYY-MM-DD] Session N: [one-sentence outcome]`

2. **Archive unreferenced entries**: entries that have not been referenced in the last
   5 sessions move to MEMORY_ARCHIVE.md. Reference tracking: the agent logs which MEMORY.md
   sections it actually used during each session in the session log.

3. **Preserve permanent entries always**: convention decisions and accepted architecture
   decisions are never compressed or archived. They remain in active context indefinitely.
   This is why they must be written concisely — they hold space permanently.

4. **Critical entries before session summaries**: if a choice must be made, keep
   critical architectural context over session summaries. Session history is in CHANGELOG.md.

The 200-line limit is not arbitrary. It is calibrated to the practical context window available
for project state after CLAUDE.md, PROJECT_PLAN.md, and ARCHITECTURE.md are loaded. Exceeding
it degrades the signal-to-noise ratio of every session that follows.

---

## MEMORY.md Entry Format

To enable automated lifecycle management, every MEMORY.md entry uses a structured format:

```markdown
## [Category] — [Title]
Date: YYYY-MM-DD
Expires: [date | when-superseded | permanent | until: condition]
Tags: [architecture | pattern | workaround | session | bug | api-quirk | performance]

[Entry content — 2-5 lines maximum for non-permanent entries]
```

### Examples

```markdown
## Convention — API response envelope format
Date: 2026-01-15
Expires: permanent
Tags: architecture, convention

All API responses use: {data: ..., error: ..., meta: {session_id, timestamp}}
Error responses always include a machine-readable error_code, never a raw exception.

---

## Session — Withings connector implementation
Date: 2026-02-10
Expires: 2026-03-12 (30 days)
Tags: session

Implemented Withings OAuth2 connector. Pattern matches Oura (ADR-003).
Refresh token stored in ~/.env, never in code. 4 entities added to config.

---

## Workaround — Oura API rate limit
Date: 2026-01-28
Expires: until: Oura fixes rate limit on /sleep endpoint
Tags: workaround, api-quirk

/sleep endpoint rate limit is 60 req/hour (not 100 as documented).
Current code uses 55 req/hour to stay safe. Remove limit reduction when Oura fixes docs.
```

---

## MEMORY_ARCHIVE.md

Archived entries live in `MEMORY_ARCHIVE.md`. This file:
- Is NOT read at session start (not in the standard file list)
- IS available for explicit lookup when investigating historical decisions
- Has no size limit — it is a permanent historical record
- Is organized reverse-chronologically by archival date

When an entry is archived, append to MEMORY_ARCHIVE.md:
```markdown
## [Original title] [ARCHIVED: YYYY-MM-DD]
[Original content]
[Archival reason: expired / superseded / resolved]
```

---

## Related

- [patterns/knowledge-decay.md](../patterns/knowledge-decay.md) — implementation pattern
- [docs/architecture.md](architecture.md) — Layer 5 (Knowledge) in the 7-layer stack
- [templates/MEMORY.md](../templates/MEMORY.md) — MEMORY.md template with lifecycle annotations
