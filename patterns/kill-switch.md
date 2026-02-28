# Pattern: Kill Switch

## Problem

Agents are trained to be helpful. "Helpful" means continuing, not stopping. When an agent
encounters a situation that should cause it to stop — a confidence collapse, a cascade of
errors, a near-violation of a governance rule — its training bias pushes it to try one more
thing, make one more fix, produce one more output.

Without an explicit stop protocol, the agent drifts through bad states, producing output that
looks plausible but is systematically wrong. By the time the human notices, the session has
produced 20 incorrect changes across 15 files. Rollback is expensive. The codebase needs
surgery.

## Solution

Define explicit triggers that force immediate cessation of all work. When any trigger fires,
the agent stops, presents a structured situation report, and waits for explicit human
instruction. It does not attempt to fix the triggering issue. It does not continue with
unrelated work. It waits.

The kill switch makes stopping the default in ambiguous situations, not the exception.

## When to Use

Add to any CLAUDE.md at Level 3 or above. The kill switch is the safety mechanism that
prevents a bad session from becoming a disaster. It is not optional for projects shipping
to production.

## When NOT to Use

- Read-only or exploratory sessions where no code changes are being made
- Prototype or throwaway projects where there is no production codebase to protect
- Level 1-2 projects that have not yet experienced the failure modes this prevents (add the triggers as preparation anyway — they cost nothing to include)

## Triggers

Implement all five triggers. Do not customize them away — they are calibrated for the
failure modes that occur most frequently in practice.

```markdown
## kill_switch

You MUST immediately stop and present a kill switch alert if ANY of these are true:

1. CONSTITUTION VIOLATION
   You are about to take an action that violates any rule in this CLAUDE.md.
   Examples: committing a credential, modifying an out-of-scope file, pushing to main.

2. CONFIDENCE COLLAPSE
   Your confidence has dropped below 30% on 3 consecutive tasks.
   This indicates context confusion, stale knowledge, or scope beyond your reliable range.

3. BLAST RADIUS EXCEEDED
   You have modified more than [CUSTOMIZE: 20] files this session.
   Or: you are about to modify more than 500 lines in a single file.
   Or: you are about to modify a critical file without explicit permission.

4. CASCADE FAILURE
   You have entered an error → fix → new error loop with 3 or more cycles.
   Continuing will make things worse, not better.

5. CONTEXT CONFUSION
   You are referencing files, functions, or architecture that you cannot verify exists.
   Hallucination risk is active. Stale knowledge may be affecting your reasoning.

When any trigger fires:
1. STOP — do not make any further changes
2. Present the kill switch report (see format below)
3. Wait — do not proceed until the human explicitly instructs you to continue
4. Do not attempt to fix the triggering condition yourself
```

## Kill Switch Report Format

```
🛑 KILL SWITCH ACTIVATED

Trigger: [which of the 5 triggers fired — one sentence]

Last 3 actions:
1. [action] → [outcome]
2. [action] → [outcome]
3. [action] → [outcome — what triggered the kill switch]

Files modified this session: [N total]
[list each file with one-line description of change]

Incomplete work:
- [task name]: [what was started but not finished]

Recommended action:
[specific guidance for this trigger type]

I will not make any further changes. Please tell me how to proceed.
```

## Implementation

### In CLAUDE.md

```markdown
## kill_switch

You MUST immediately stop and present a kill switch alert if:
- You are about to violate any rule in this constitution
- Your confidence drops below 30% on 3 consecutive tasks
- You have modified more than 20 files this session
- You have entered an error→fix→error loop (3+ cycles)
- You reference files or architecture that does not exist in the current codebase

When activated:
1. Stop ALL work immediately
2. Present: trigger reason, last 3 actions, files modified, recommended action
3. Wait for explicit human instruction before any further action
4. Do not attempt to resolve the triggering condition independently

Threshold customization:
- Files per session: default 20. Adjust to project scale.
- Confidence threshold: 30%. Do not raise above 40%.
- Error loop cycles: 3. Do not raise above 4.
```

### Recommended Actions by Trigger

Include these in your CLAUDE.md or reference this pattern:

**Constitution violation**: present the specific rule and the specific action that would
violate it. Let the human decide: approve an exception, redesign the approach, or abandon.

**Confidence collapse**: present what you are uncertain about. The human may be able to
provide the missing context in one or two sentences. Alternatively, a fresh session with
explicit orientation may be needed.

**Blast radius exceeded**: present the list of files modified. The human may decide the
scope is acceptable, or may choose to stop and open a PR for what is already done.

**Cascade failure**: present the loop (what you tried, what broke, what you tried next,
what broke next). Ask the human to describe the correct end state without proposing an
approach — a different path is needed.

**Context confusion**: ask the specific question that would resolve the confusion. Usually:
"Does [file/component/pattern] still exist? My context suggests it does but I cannot verify it."

## Anti-Patterns

**Kill switch that can be disabled** — the kill switch must be unconditional. "Just keep
going" is not a valid override for kill switch triggers. The protocol exists precisely for
situations where stopping feels unnecessary.

**Kill switch that triggers too easily** — the thresholds are calibrated to catch serious
situations. A kill switch that fires on every minor uncertainty trains developers to ignore it.
Use confidence scoring and normal uncertainty handling for situations below the trigger level.

**Attempting to fix before triggering** — if the agent detects a kill switch condition,
it should not try to resolve it before presenting the alert. The attempt may make things
worse and delays the human's awareness of the situation.

## Related Patterns

- [docs/kill-switch.md](../docs/kill-switch.md) — full specification with all trigger details
- [docs/session-replay.md](../docs/session-replay.md) — recording kill switch events for review
- [patterns/blast-radius-control.md](blast-radius-control.md) — blast radius thresholds
- [patterns/progressive-trust.md](progressive-trust.md) — confidence scoring that feeds trigger 2
