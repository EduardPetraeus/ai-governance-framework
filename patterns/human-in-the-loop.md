# Human-in-the-Loop

## Name

Human-in-the-Loop — make human oversight effective, not perfunctory.

## Problem

Human oversight of AI agents becomes perfunctory. Developers approve quickly, trust completely, and stop engaging critically with agent output. The human-in-the-loop becomes a rubber stamp. At that point, the human is adding latency, not value.

This happens for predictable reasons. The agent's output is consistently well-formatted. It uses confident language. It passes automated checks. The first 10 approvals were correct. The human's brain learns the pattern: "agent output = probably fine." By session 15, the human is scanning rather than reading. By session 30, the human clicks "approve" and moves on.

The inverse failure is also common: the human reviews everything with equal intensity regardless of risk. This is exhausting and unsustainable. The human burns out, stops reviewing carefully, and the quality of oversight drops to zero despite the process still technically being in place.

Both failure modes have the same root cause: the checkpoints are not designed. They happen by default (review every PR) rather than by design (review specific decisions where human judgment is irreplaceable).

## Solution

Define specific checkpoints where human judgment is genuinely required. Make those checkpoints meaningful by ensuring the agent presents the right information to support a real decision. Remove checkpoints where the human adds no value. Allow the human to say "no" and have the agent respond appropriately.

### When Human Intervention Is Mandatory

| Trigger | Why Human Judgment Is Required |
|---------|-------------------------------|
| Architectural decisions | Component boundaries, data models, and integration patterns define the system's future. Agents optimize locally; humans must evaluate globally. |
| Security-sensitive code | Authentication, authorization, encryption, and credential handling require threat modeling that agents cannot reliably perform. |
| Production operations | Database migrations, infrastructure changes, and CI/CD modifications have irreversible consequences. |
| Confidence below 70% | The agent has explicitly flagged uncertainty. Ignoring this flag defeats the purpose of [confidence scoring](../docs/quality-control-patterns.md#pattern-6-confidence-scoring). |
| Conflicting agent outputs | Two agents disagree on approach. The human must decide which reasoning is correct. |
| Blast radius exceeded | The proposed change exceeds session limits. See [Blast Radius Control](blast-radius-control.md). |
| ADR contradiction | The proposed approach would reverse an Accepted Architecture Decision Record. |
| First use of a new pattern | The agent proposes a pattern not previously used in the project. |

### When Human Intervention Adds No Value

| Situation | Better Alternative |
|-----------|-------------------|
| Syntax and formatting checks | Linters and formatters |
| Test pass/fail verification | CI/CD pipeline |
| Dependency vulnerability scanning | Automated security scanners |
| Convention compliance | CLAUDE.md rules + automated validation |
| CHANGELOG formatting | Template + agent self-check |

Remove these from the human review loop. Every unnecessary checkpoint trains the human to review less carefully.

## When to Use

- Every project where AI agents make changes that reach production
- Teams where multiple humans review agent output (ensures consistent checkpoint definitions)
- Projects transitioning from full manual review to [progressive trust](progressive-trust.md)
- Compliance-sensitive projects where audit trails must show meaningful human approval

## When NOT to Use

- Fully exploratory sessions where the output is disposable
- Sessions where the human is actively co-piloting and approves each change in real time (the human is already in the loop by definition)
- Automated pipelines where no human should be involved (e.g., automated dependency updates with passing tests)

## Implementation

### Step 1: Define checkpoint types

Categorize checkpoints by what the human is actually deciding:

```yaml
checkpoint_types:
  approval:
    description: "Human approves or rejects a specific change"
    requires: "the change, the alternatives considered, the impact if rejected"
    examples: ["architectural decision", "security-sensitive code", "schema migration"]

  direction:
    description: "Human chooses between multiple valid approaches"
    requires: "each approach with trade-offs, the agent's recommendation and reasoning"
    examples: ["technology choice", "API design", "data model structure"]

  confirmation:
    description: "Human confirms the agent understood the requirement correctly"
    requires: "the agent's interpretation of the requirement, the planned approach"
    examples: ["ambiguous requirements", "implicit business rules", "edge case handling"]

  escalation:
    description: "Agent cannot proceed and needs human input"
    requires: "what the agent tried, why it failed, what information it needs"
    examples: ["missing credentials", "unclear specification", "conflicting constraints"]
```

### Step 2: Design checkpoint presentations

Each checkpoint must present the right information for the human to make a real decision. The agent must not present raw output and ask "does this look right?" — that invites rubber-stamping.

**Approval checkpoint format:**

```
CHECKPOINT: Approval Required — Database Schema Change

Change: Add `last_synced_at` column to `user_devices` table
Type: Non-nullable TIMESTAMP WITH TIME ZONE, default NOW()

Impact:
  - Adds column to table with 12,000 rows (migration runs in <1 second)
  - Existing rows get current timestamp as default (acceptable: indicates "never synced before migration")
  - No index added (column used in WHERE clause only for admin queries, not user-facing)

Alternatives considered:
  1. Nullable column, no default — simpler migration, but application code must handle NULL
  2. Separate sync_status table — cleaner separation, but adds JOIN complexity for a single column
  3. [Selected] Non-nullable with NOW() default — simplest application code, acceptable default semantics

If rejected: device sync tracking requires a different approach. Suggest specifying preferred alternative.

Decision needed: Approve schema change, or specify alternative approach.
```

**Direction checkpoint format:**

```
CHECKPOINT: Direction Needed — Retry Strategy

Context: The Oura API occasionally returns 503 during maintenance windows (typically 2-5 minutes).

Option A: Exponential backoff (1s, 2s, 4s, 8s, 16s, max 60s)
  Pro: Standard pattern, handles transient errors well
  Con: 5 retries take 31 seconds total; may not cover a 5-minute maintenance window

Option B: Exponential backoff with jitter + circuit breaker
  Pro: Handles both transient errors and extended outages
  Con: More complex implementation, circuit breaker state must be managed

Option C: Fixed interval retry with timeout (retry every 30s for up to 10 minutes)
  Pro: Covers maintenance windows, simple implementation
  Con: Non-standard pattern, 30s intervals may be too aggressive

Agent recommendation: Option B — the circuit breaker prevents hammering the API during maintenance while exponential backoff handles transient errors.

Decision needed: Which retry strategy should be implemented?
```

### Step 3: Implement checkpoint logging

Every checkpoint interaction must be logged for audit and retrospective analysis:

```yaml
checkpoint_log:
  - id: "ckpt-2026-02-28-001"
    type: "approval"
    session: "session-042"
    timestamp: "2026-02-28T14:32:00Z"
    trigger: "schema migration"
    summary: "Add last_synced_at column to user_devices"
    decision: "approved"
    reviewer: "developer-a"
    time_to_decision: "3 minutes"
    notes: "Confirmed default value semantics are acceptable"

  - id: "ckpt-2026-02-28-002"
    type: "direction"
    session: "session-042"
    timestamp: "2026-02-28T14:45:00Z"
    trigger: "design decision"
    summary: "Retry strategy for Oura API"
    options_presented: 3
    decision: "option B selected"
    reviewer: "developer-a"
    time_to_decision: "5 minutes"
    notes: "Added requirement: circuit breaker timeout configurable via environment variable"
```

### Step 4: Define rejection handling

When the human says "no," the agent must respond constructively:

```yaml
rejection_protocol:
  on_rejection:
    - acknowledge: "Confirm the rejection and the reason"
    - clarify: "Ask what aspect was rejected (entire approach vs. specific detail)"
    - alternatives: "Present alternative approaches if available"
    - document: "Log the rejection, reason, and any new constraints"
    - proceed: "Implement the approved alternative or wait for further direction"

  on_partial_rejection:
    - identify: "Clarify which parts are approved and which are rejected"
    - adjust: "Modify only the rejected parts"
    - re_present: "Present the modified approach for approval"
```

The agent must never argue with a rejection or re-present the same approach without changes. If the agent believes the rejection is based on a misunderstanding, it should present the clarifying information and let the human re-evaluate.

### Step 5: Integrate with Progressive Trust

Checkpoint requirements decrease as trust increases:

| Trust Level | Required Checkpoints |
|:-----------:|---------------------|
| 1 (Full Review) | All checkpoint types active. Every file change requires approval. |
| 2 (Logic Review) | Approval checkpoints for architecture and security. Direction checkpoints for design decisions. |
| 3 (Architecture Review) | Approval checkpoints for architecture only. Direction checkpoints for novel patterns. |
| 4 (Task Review) | Approval checkpoints for critical files and ADR contradictions only. |

See [Progressive Trust](progressive-trust.md) for how trust levels are determined and adjusted.

## Example

A developer is using Claude Code to build a health data aggregation pipeline. The current sprint task is adding a weekly sleep summary feature.

**Session start — confirmation checkpoint:**

```
CHECKPOINT: Confirmation — Requirement Interpretation

Task: "Add weekly sleep summary"

My interpretation:
  - Aggregate daily sleep records into weekly summaries
  - Weekly average = sum of daily durations / number of days with data (not 7)
  - Weeks with no data produce no summary row (not a row with zero values)
  - Week boundaries: Monday 00:00 UTC to Sunday 23:59 UTC
  - Store in new `weekly_sleep_summary` table

Questions:
  1. Is the week boundary correct? Some systems use Sunday-Saturday.
  2. Should the summary include min/max/median in addition to average?
  3. Should summaries be recomputed when historical data is corrected?

Decision needed: Confirm interpretation or correct.
```

The developer confirms Monday-Sunday boundaries, adds min/max to the requirements, and defers the recomputation question to a future task.

**Mid-session — approval checkpoint:**

```
CHECKPOINT: Approval Required — New Database Table

Table: weekly_sleep_summary
Columns:
  - user_id (FK to users, NOT NULL)
  - week_start (DATE, NOT NULL) — Monday of the week
  - avg_duration_minutes (DECIMAL(6,1), NOT NULL)
  - min_duration_minutes (INTEGER, NOT NULL)
  - max_duration_minutes (INTEGER, NOT NULL)
  - days_recorded (INTEGER, NOT NULL, CHECK > 0)
  - created_at (TIMESTAMP WITH TIME ZONE, DEFAULT NOW())
  - updated_at (TIMESTAMP WITH TIME ZONE, DEFAULT NOW())

Primary key: (user_id, week_start)
Index: user_id (for per-user queries)

Decision needed: Approve schema or modify.
```

The developer approves.

**Session end — no checkpoint needed** for the implementation review because automated checks cover test pass, lint, and coverage. The developer reviews the PR at Logic Review depth (trust Level 2 for code generation) and merges.

Total human time: 8 minutes across 2 meaningful checkpoints. Zero time spent on formatting, test verification, or convention compliance. Every minute of human attention was spent on decisions that required human judgment.

## Evidence

The concept of meaningful checkpoints draws from human factors engineering and safety-critical systems design. In aviation, the principle is "monitor when monitoring adds value, automate when automation is sufficient." Unnecessary human monitoring causes vigilance fatigue, which is more dangerous than no monitoring at all because it creates the illusion of oversight.

In software development, the analogous research comes from code review studies. Microsoft Research (2013) found that the most effective code reviews are those where the reviewer understands what they are looking for, has the right context, and is reviewing a manageable scope. Reviews that lack these properties become rubber-stamp exercises regardless of organizational mandate.

The human-in-the-loop pattern applies these findings to AI agent governance: define what the human is looking for (checkpoint type), provide the right context (checkpoint presentation), and keep the scope manageable (only trigger checkpoints where human judgment is irreplaceable).

Teams implementing structured checkpoints report higher reviewer satisfaction (less fatigue), faster review cycles (less time on irrelevant details), and higher defect detection rates (focused attention on what matters).

## Related Patterns

- [Progressive Trust](progressive-trust.md) — determines which checkpoints are active based on trust level
- [Blast Radius Control](blast-radius-control.md) — exceeded blast radius triggers mandatory human checkpoint
- [Output Contracts](output-contracts.md) — contracts define what the human reviews against
- [Dual-Model Validation](dual-model-validation.md) — AI review is Layer 3; human review is Layer 4
- [Context Boundaries](context-boundaries.md) — boundaries reduce the scope the human must understand at each checkpoint
- [Quality Control Patterns](../docs/quality-control-patterns.md) — human-in-the-loop is Layer 4 of the quality control stack
