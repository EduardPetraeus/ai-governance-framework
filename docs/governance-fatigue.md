# Governance Fatigue: The Silent Framework Killer

## The Fundamental Law of Developer Governance

**If your governance is more friction than copy-pasting into a browser chat window,
developers will copy-paste into a browser chat window.**

This is not a discipline problem. It's a design problem. You cannot solve it with rules,
enforcement, or management pressure. You can only solve it by making governed AI development
EASIER and FASTER than ungoverned AI development.

Every governance mechanism must earn its place. Each check, each required step, each
mandatory field consumes from the same finite budget. Exceed it and governance collapses —
not through rebellion, but through attrition. Developers stop following the process not because
they disagree with it but because following it is slower than not following it.

---

## The Shadow AI Problem

**Shadow AI** is AI usage outside governed channels, adopted specifically to avoid the friction
of governed channels. It is invisible by design. You cannot detect it. You cannot prevent it.
You can only make it unnecessary.

Shadow AI in practice:
- Pasting code into ChatGPT web interface to bypass pre-commit hooks
- Using personal Copilot accounts instead of team-governed Claude Code
- Running AI suggestions locally without committing to avoid CI checks
- Sharing prompts via Slack DMs instead of governed sessions
- Spinning up a personal Claude project with no CLAUDE.md to "just get this one thing done"

Shadow AI is the governance system's most honest metric. When developers route around the
system, the system has failed. The technical governance remains intact — the humans have left it.

The appropriate response is not enforcement. Enforcing against shadow AI drives it further
underground. The appropriate response is reducing friction below the threshold that drives it.

---

## The Friction Budget

Every governance mechanism has a cost measured in developer seconds and cognitive load.
You have a finite "friction budget" per session. Exceed it and developers route around you.

### Budget Model — Per Session

```
┌─────────────────────────────────────────────────────────────┐
│ FRICTION BUDGET — Per Session                                │
├──────────────────────────────┬──────────────────────────────┤
│ Mechanism                    │ Friction Cost                │
├──────────────────────────────┼──────────────────────────────┤
│ Session start (/plan-session)│ ~30 seconds (acceptable)     │
│ Governance sync (automatic)  │ ~10 seconds (invisible)      │
│ Task reporting (automatic)   │ ~5 sec per task (invisible)  │
│ Security scan (automatic)    │ ~0 seconds (invisible)       │
│ Session end (/end-session)   │ ~45 seconds (acceptable)     │
│ Manual review of AI output   │ ~2-5 min per task (variable) │
├──────────────────────────────┼──────────────────────────────┤
│ TOTAL per session            │ ~5-10 minutes overhead       │
│ Value delivered              │ Traceability, quality, safety│
│ Budget threshold             │ >15 min = developers bypass  │
└──────────────────────────────┴──────────────────────────────┘
```

### Friction Categories

**Invisible friction** (zero perceived cost): governance that runs automatically as a side
effect of normal work. Security scanning that happens during CI. Task reporting embedded in the
session protocol. Changelog updates generated at session end. This friction is free — developers
never feel it.

**Acceptable friction** (under 60 seconds): one-command session start, one-command session end.
The protocol runs, the governance fires, but the developer typed two commands. Most developers
accept this without complaint.

**High friction** (minutes per session): mandatory forms, required justification fields,
waiting for approval gates, manual report generation. Each minute of required process is a
minute of productive time lost. Accumulate enough of these and developers calculate: "the
framework costs me 20 minutes per session. Going around it costs zero."

**Fatal friction** (process that feels like bureaucracy): required sign-offs that serve no
detectable purpose, checks that always pass (and are therefore noise), mandatory fields that
everyone fills in with boilerplate, governance that clearly protects the framework rather than
the developer. Fatal friction destroys trust in the entire system.

---

## Design Principles for Zero-Friction Governance

### 1. Invisible by Default

The best governance is governance the developer never notices. Governance sync, security
scanning, task reporting — all automatic. Zero keystrokes required from the developer for
these mechanisms. The developer benefits without paying the price.

Design test: can a developer complete a full governed session by typing only two commands?
If yes, the governance is well-designed. If no, find what is requiring additional keystrokes
and automate it.

### 2. Two-Command Sessions

Starting work = one command (`/plan-session`). Ending work = one command (`/end-session`).
Everything else is automatic. The governance framework runs; the developer never orchestrates
it manually.

This is not about minimizing commands for its own sake. It is about making the governed path
the path of least resistance. If the governed path requires six commands and the ungoverned
path requires zero, developers will take the ungoverned path under time pressure — which is
precisely when governance matters most.

### 3. Value-Obvious

Every friction point must have an obvious benefit the developer cares about.

"This saves YOU from deploying a secret to production" is effective.
"This satisfies compliance requirements" is not.

Developers make rational tradeoff calculations. A friction point whose benefit they understand
and value gets paid willingly. A friction point whose purpose is unclear gets bypassed.
Document the value, not just the rule.

### 4. Escape Hatches With Logging

If a developer must bypass a governance rule, let them — but log it. A logged bypass is
governable. A shadow AI session is invisible.

Example: a `--skip-governance` flag that creates a visible audit entry. The developer can use
it. Their manager can see it. The team can review whether bypasses are accumulating.
The act of logging converts an invisible governance failure into a visible governance signal.

Do not make bypasses impossible. Make them visible.

### 5. Progressive Friction

New developers get more guidance (more friction, more safety).
Experienced developers get less (faster, more trust). Friction adapts to the user.

A developer in week 1 benefits from detailed prompts, explicit scope confirmation, and thorough
review. A developer in year 2 does not need the same scaffolding. Progressive friction preserves
the safety value for those who need it while reducing overhead for those who have earned trust.

See [patterns/progressive-trust.md](../patterns/progressive-trust.md) for implementation.

### 6. Faster Than Ungoverned

The ultimate goal: governed development is faster than ungoverned development.

This is achievable because ungoverned development has hidden costs that governed development
eliminates:
- Re-explaining project context every session (MEMORY.md eliminates this)
- Reconstructing project state from git log (CHANGELOG.md eliminates this)
- Re-litigating settled architectural decisions (ADRs eliminate this)
- Discovering naming inconsistencies during review (naming conventions eliminate this)

Ungoverned development starts from scratch every time. Governed development builds on
accumulated knowledge. Over time, the governed approach is faster — not despite governance,
but because of it.

---

## Measuring Governance Friction

Track these metrics. Measure them before implementing a new governance mechanism and after.
If the numbers move in the wrong direction, the new mechanism costs more than it contributes.

**Session start overhead**: time from "I want to code" to "I'm writing code." Target: under
90 seconds. Above 5 minutes is a friction problem.

**Governance-only commands per session**: commands typed that serve governance rather than
product development. Target: 2 (`/plan-session` and `/end-session`). Above 5 is excessive.

**Developer friction reports**: "the framework slowed me down today." Track these. One per
month is signal. Three per week is a problem. Frame it as a quality metric, not a complaint.

**Shadow AI indicators**: AI usage detected outside governed tools. Hard to measure directly,
but trackable through: team chat patterns, personal API key usage, sudden productivity
improvements without corresponding governed session activity.

---

## The Acid Test

Ask every developer monthly: "Does the governance framework make you faster or slower?"

If more than 20% say "slower" — you have a friction problem. Fix it before adding more features.
The correct response to a failing governance system is not more governance. It is less friction.

The acid test is honest because it measures outcome, not compliance. A developer who follows
the process but feels it slows them down is a governance risk — they are one bad week away from
routing around the system entirely. Fix their friction before it becomes exit.

---

## Related

- [patterns/friction-budget.md](../patterns/friction-budget.md) — implementation pattern
- [docs/maturity-model.md](maturity-model.md) — friction increases appropriately with maturity level
- [docs/automation-bias.md](automation-bias.md) — adding governance layers creates its own risks
