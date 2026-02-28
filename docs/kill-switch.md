# Kill Switch: When the Agent Must Stop Itself

## The Problem

AI agents do not have self-stopping instincts. An agent that detects it is producing
garbage will continue producing garbage until the session ends or the human notices.
By then, 20 files might be corrupted, a cascade of incorrect changes may have been committed,
or a confidence collapse may have been spreading across outputs for the past 30 minutes.

This is not a flaw in any specific model. It is structural. Agents are designed to be helpful
and responsive. Stopping feels unhelpful. Continuing feels responsive. Without an explicit
protocol that mandates stopping under defined conditions, the agent's training bias pushes it
to keep going.

The kill switch is the mechanism that overrides this bias.

---

## Kill Switch Triggers

The agent must immediately stop all work and present a kill switch alert when ANY of these
conditions are met:

### Trigger 1: Constitution Violation

The agent is about to break a rule in CLAUDE.md.

Examples:
- About to commit a file that contains what appears to be a real credential
- About to modify a file that is explicitly off-limits for this session
- About to push directly to main without a PR
- About to exceed the configured blast radius limit

**Why stop, not fix:** The agent detected a violation before committing it. The right response
is to surface it to the human, not to unilaterally decide how to resolve it. The human's
options include: approve an exception, redesign the approach, or cancel the task entirely.
The agent making that decision alone is itself a governance violation.

### Trigger 2: Confidence Collapse

The agent's confidence drops below 30% on three consecutive tasks.

Confidence collapse is an indicator that the agent has lost accurate context:
- The codebase has changed in ways the agent does not understand
- The scope expanded into unfamiliar territory
- The agent's assumptions about the system are consistently incorrect
- MEMORY.md or ARCHITECTURE.md may be stale

Continuing at low confidence produces output that looks plausible but is systematically
wrong. The cost of the human reviewing and reverting low-confidence work exceeds the cost
of stopping cleanly.

### Trigger 3: Blast Radius Exceeded

The session would affect more than the configured maximum scope.

Default thresholds:
- More than 20 files modified in one session
- More than 500 lines changed in a single file
- Critical governance files (CLAUDE.md, CI configs) modified without explicit permission

A session that has touched 20 files has become unfocused. The human's ability to review
it meaningfully has dropped to near zero. Stopping and scoping down is more valuable than
completing the original task at unacceptable review risk.

### Trigger 4: Cascade Failure

The agent has entered an error→fix→error loop: three or more cycles where fixing an error
causes a new error, which requires a new fix, which causes another error.

Cascade failure indicates one of:
- A fundamental misunderstanding of the system's architecture
- A constraint the agent is not aware of that makes the intended change impossible
- Dependencies between components that prevent simple local fixes
- The approach is wrong and needs to be reconsidered, not continued

Each iteration of the loop moves the codebase further from a recoverable state. The right
intervention is stopping, not attempting a fourth fix.

### Trigger 5: Context Confusion

The agent references files that do not exist or architecture that is not current.

Signs:
- Agent reads a file path from MEMORY.md — file does not exist
- Agent proposes a pattern explicitly rejected in an ADR
- Agent refers to a component that was renamed or removed
- Agent's plan assumes a system state that does not match reality

Context confusion means the knowledge base is stale. Continuing with stale context produces
confident-sounding output that contradicts the actual system. Stop, surface the confusion,
and let the human re-orient the agent.

---

## Kill Switch Behavior

### What to Present When Triggered

```
🛑 KILL SWITCH ACTIVATED
Reason: [specific trigger — one sentence]

What happened (last 3 actions):
1. [action 1 and outcome]
2. [action 2 and outcome]
3. [action 3 and outcome — what triggered the kill switch]

Files modified this session:
- [file path] — [what changed]
- [file path] — [what changed]
[list all files touched since session start]

Current session state:
- Tasks completed: [N]
- Tasks in progress (incomplete): [description]
- Tasks not started: [list]

Recommended action:
[Specific guidance based on the trigger type — see below]

Session is PAUSED. I will not make any further changes until you explicitly tell me to continue.
```

### Recommended Actions by Trigger

**Constitution violation**: "Review the flagged file/action. Decide whether to approve an exception, redesign the approach, or cancel this task. Once decided, tell me how to proceed."

**Confidence collapse**: "Review the last 3 outputs for correctness. If they are wrong: tell me what I misunderstood about the system. If they are right: we may be in unfamiliar territory where more human guidance is needed. Consider running this task in a fresh session with explicit context."

**Blast radius exceeded**: "The session has grown beyond safe review scope. Consider: stop here and open a PR for what's done, or continue with explicit authorization to exceed the limit (understanding review quality drops with scope)."

**Cascade failure**: "The current approach is caught in a loop. Do not ask me to try again with the same approach. Instead: describe what the correct end state looks like, and I will propose a different path to get there."

**Context confusion**: "My understanding of the system does not match its actual state. Please orient me: [specific question about the confused element]. Once I understand the current state correctly, I can continue."

### What the Agent Does NOT Do

- Does NOT try to fix the problem that triggered the kill switch
- Does NOT continue with "just one more thing"
- Does NOT minimize the issue ("it's probably fine if we just...")
- Does NOT make judgment calls about whether the situation warrants stopping
  (the triggers are non-negotiable — if they fire, stop)
- Does NOT remain stopped indefinitely — it waits for explicit instruction to continue

---

## Implementation in CLAUDE.md

Add to the `kill_switch` section of CLAUDE.md (Level 3+):

```markdown
## kill_switch

You MUST immediately stop and present a kill switch alert if:
- You are about to violate any rule in this constitution
- Your confidence drops below 30% on 3 consecutive tasks
- You have modified more than [CUSTOMIZE: 20] files this session
- You have entered an error→fix→error loop (3+ cycles)
- You reference files or architecture that does not exist

When kill switch activates:
1. Stop ALL work immediately — do not attempt to fix the triggering issue
2. Present: reason, last 3 actions, all files modified this session, recommended action
3. Wait for explicit human instruction before ANY further action
4. State clearly: "I will not make further changes until you tell me to continue"
```

---

## Kill Switch vs. Normal Uncertainty

The kill switch is not a substitute for normal uncertainty handling.

**Normal uncertainty**: "I'm not sure about the best approach for this API rate limit logic.
Should I use exponential backoff or fixed intervals?" → Ask. Do not stop.

**Kill switch**: "I am about to commit a file that contains what looks like a real API key."
→ Trigger the kill switch. Do not ask and proceed.

The distinction: normal uncertainty is about quality (which option is better?). Kill switch
triggers are about safety (should I be doing this at all?). Confidence scoring handles quality.
The kill switch handles safety and coherence.

---

## Related

- [patterns/kill-switch.md](../patterns/kill-switch.md) — implementation pattern
- [docs/session-replay.md](session-replay.md) — reconstructing what happened after a kill switch event
- [patterns/blast-radius-control.md](../patterns/blast-radius-control.md) — blast radius configuration
- [docs/security-guide.md](security-guide.md) — constitution violation triggers related to security
