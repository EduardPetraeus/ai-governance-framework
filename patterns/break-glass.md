# Pattern: Break Glass

## Problem

Constitutional inheritance (org → team → repo) and the hybrid inheritance model (ADR-004)
prevent lower levels from weakening safety rules. This protection is correct in the steady
state. It becomes an operational hazard in four specific scenarios:

1. **Framework bug**: a governance rule or validator contains a defect that blocks legitimate
   work — the governance machinery itself is the obstacle, not a safety violation.
2. **Production incident**: an ongoing outage or data loss event requires immediate action
   that a safety rule would delay (e.g., a mandatory PR review requirement during a
   3am incident where the only available responder is on-call alone).
3. **Security emergency**: an active security breach requires actions (rotating credentials,
   disabling access paths, hot-patching without review) that governance workflow would slow
   by hours.
4. **Governance deadlock**: two or more constitutional rules conflict in a way that makes
   any action a violation — the rules themselves are in irresolvable conflict for the
   current situation.

Permanent exceptions are wrong: they erode the safety rules that constitutional inheritance
exists to protect. The solution is a **time-limited, logged, mandatory-review override** —
the break-glass mechanism.

## When to Use

Use break-glass **only** when all of the following are true:

- The situation is one of the four scenarios above (framework bug, production incident,
  security emergency, governance deadlock)
- The safety rule being overridden is the direct cause of the operational problem
- The override will be in effect for at most 24 hours
- The person activating the override has the authority level required (see below)
- Post-incident review will be completed within 5 business days

**Do not use break-glass for:**
- Convenience (a rule is inconvenient, not blocking)
- Disagreement with a rule (use the exception process in `patterns/constitutional-inheritance.md`)
- Recurring situations (if break-glass is needed repeatedly for the same rule, the rule
  needs to change — submit a PR to the owning constitution level)
- Configurable rules (configurable rules resolve via specific-wins — no override needed)

## When NOT to Use

- **Legal obligations** (`override_level: legal` in `org_compliance`) cannot be overridden
  by break-glass. Legal obligations are not constitutional rules — they derive from
  external legal instruments and persist regardless of internal governance state.
- **External regulatory requirements**: same as legal obligations above.
- **Situations with a safe alternative**: if the safety rule can be satisfied without
  break-glass (e.g., getting async review via chat instead of blocking PR review),
  use the alternative.

## Authority Levels

| Scenario | Minimum authority to activate |
|----------|------------------------------|
| Framework bug | Tech Lead or Senior Engineer |
| Production incident | On-call engineer (any level) |
| Security emergency | Security Lead or Tech Lead |
| Governance deadlock | Tech Lead + one additional approver |

Authority is contextual. In a 3am production incident, "minimum authority" means the
most senior available person — not a requirement to page someone out of sleep before
acting. Document who activated and why in the break-glass log entry.

## How to Activate

### Step 1 — Create the break-glass log entry

Create or append to `BREAK-GLASS.md` in the repository root (or in the governance repo
if the override spans multiple repos). The entry must contain:

```markdown
## Break-Glass Entry [YYYY-MM-DD HH:MM UTC]

**Activated by:** [name and role]
**Scenario:** [framework bug | production incident | security emergency | governance deadlock]
**Duration:** [start time] → [end time, max 24 hours from start]
**Rule overridden:** [exact rule name and source file/section]
**Reason:** [one paragraph — why this rule is blocking legitimate action right now]
**Alternative considered:** [what alternative was evaluated and why it was insufficient]
**Actions taken under override:** [list of specific actions taken while override is active]
**Resolution:** [leave blank until override expires]
**Post-incident review scheduled:** [date, owner]
```

### Step 2 — Notify

Immediately notify (before or during, not after):
- The owner of the constitutional level whose rule is being overridden
  (repo → project developers, team → Tech Lead, org → Engineering Leadership)
- The security lead if the override touches any item in the `never_commit` list,
  `security_review_model`, or `org_kill_switch`

Notification method: synchronous (call, page) for production incidents and security
emergencies; async (chat, email) for framework bugs and governance deadlocks.

### Step 3 — Execute the minimum necessary action

The override applies only to the specific rule named in the log entry, for the duration
specified, for the actions listed. Adjacent safety rules remain in effect. The override
is not a general suspension of governance.

### Step 4 — Restore and close

At the end of the override duration (or sooner when the situation is resolved):
1. Restore the overridden rule to normal enforcement
2. Complete the `Resolution` field in the break-glass log entry
3. Verify that any actions taken under the override did not leave residual safety gaps
4. Trigger the post-incident review process

## Post-Incident Review (Required)

Post-incident review is **not optional**. An override without review is a permanent
exception disguised as a temporary one.

The review must be completed within 5 business days and must answer:

| Question | Required output |
|----------|----------------|
| What triggered the override? | Root cause, not symptoms |
| Was the override justified? | Yes / No / Partially — with reasoning |
| Was the override scope correct? | Could a narrower override have worked? |
| Did the override create residual risk? | What, if any, safety gaps remain? |
| What rule change would prevent this? | Proposed change to the owning constitution level, or confirmation that no change is needed |
| Lessons learned | What governance improvement follows from this incident? |

The review output is appended to the break-glass log entry. The completed log entry is
committed to the governance repository (not deleted or archived).

## Audit Record

Every break-glass activation creates a permanent, committed audit record. The record is not
editable after the post-incident review is complete. Fields:

| Field | Description |
|-------|-------------|
| `who` | Name and role of activating person |
| `when` | Activation timestamp (UTC) |
| `why` | Scenario type and one-paragraph justification |
| `what_overridden` | Rule name, source level, source file |
| `duration` | Planned and actual override duration |
| `actions` | Specific actions taken under override |
| `resolution` | How the underlying situation was resolved |
| `lessons` | Governance improvements identified |

The presence of a break-glass log entry is not itself a governance violation. The **absence
of a log entry for a known override** is a governance violation.

## Example

### Framework Bug Scenario

```markdown
## Break-Glass Entry [2026-03-15 14:32 UTC]

**Activated by:** Priya Mehta, Tech Lead
**Scenario:** framework bug
**Duration:** 2026-03-15 14:32 UTC → 2026-03-15 23:59 UTC
**Rule overridden:** `pr_human_review: required` (CLAUDE.org.md, org_compliance)
**Reason:** The GitHub Actions governance workflow has a defect in the reviewer-assignment
step that causes all PRs to fail the "human review required" check even when a human
has approved. The bug is in the CI workflow, not in the PRs themselves. Fixing the CI
workflow itself requires merging a PR, which is blocked by the same defect. Three PRs
with legitimate human approval are blocked from merging.
**Alternative considered:** Rolling back the CI workflow via direct commit to main — rejected
because direct commits to governance files are prohibited by constitutional_changes: pr_only.
**Actions taken under override:** Merged 3 PRs with confirmed human approval (chat
screenshots archived in incident-2026-03-15.md). Merged CI workflow fix PR.
**Resolution:** CI workflow defect fixed. pr_human_review enforcement restored 16:15 UTC.
**Post-incident review scheduled:** 2026-03-18, Priya Mehta
```

## Related Patterns

- [patterns/constitutional-inheritance.md](constitutional-inheritance.md) — inheritance model and exception process
- [docs/constitutional-inheritance.md](../docs/constitutional-inheritance.md) — full specification
- [docs/adr/ADR-004-hybrid-inheritance-model.md](../docs/adr/ADR-004-hybrid-inheritance-model.md) — hybrid model decision record
