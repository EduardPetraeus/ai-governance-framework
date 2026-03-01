# Pattern: Human-in-the-Loop

## The problem

Human oversight of AI agents becomes a rubber stamp. The agent's output is well-formatted, confident, and passes automated checks. The human clicks "approve" and moves on. By session 15, the human is adding latency, not value.

The inverse is also a failure: reviewing everything at equal intensity burns the reviewer out. Quality drops to zero despite the process still technically existing.

Both failures have the same root cause: the checkpoints are not designed. They happen by default, not by intent.

## The rule

**Define exactly when human judgment is required. Automate everything else.**

## When to stop and get human approval

| Trigger | Why the human must decide |
|---------|--------------------------|
| Architectural decisions | Agents optimize locally; humans must evaluate globally |
| Authentication or authorization code | Requires threat modeling agents cannot reliably do |
| Database schema changes | Irreversible in production |
| CI/CD pipeline changes | Affects every future merge |
| Confidence below 70% | Agent has flagged genuine uncertainty |
| Blast radius HIGH (>10 files) | Change is too large to approve without explicit review |
| First use of a new pattern | No prior evidence it works in this codebase |

## When automation is sufficient (no human required)

- Syntax and formatting checks → linter
- Test pass/fail → CI pipeline
- Dependency vulnerabilities → automated scanner
- Convention compliance → CLAUDE.md rules
- CHANGELOG formatting → template

Remove these from the human loop. Every unnecessary checkpoint trains the human to review less carefully.

## Checkpoint format

When the agent needs a decision, it presents:

```
CHECKPOINT: [type — Approval / Direction / Confirmation]

Context: [what the agent was doing when it hit this checkpoint]
Decision needed: [specific question, one sentence]

Option A: [description] — Pro: [X] / Con: [Y]
Option B: [description] — Pro: [X] / Con: [Y]

Agent recommendation: [Option A/B] because [one sentence reason]
```

The agent never presents raw output and asks "does this look right?" That invites rubber-stamping.

## When the human says no

The agent acknowledges the rejection, asks what specifically was rejected, presents alternatives if available, and documents the rejected approach so it is not re-proposed. The agent never argues with a rejection.

## Related patterns

- [Blast Radius Control](blast-radius-control.md) — HIGH blast radius triggers this pattern automatically
- [Output Contracts](output-contracts.md) — contracts define what the human reviews against
