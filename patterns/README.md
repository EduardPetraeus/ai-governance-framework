# Patterns

Reusable solutions to recurring AI governance problems.

## What Is a Pattern

A pattern is a named, structured response to a problem that appears repeatedly when governing AI agents in software development. Each pattern documents the problem it solves, the solution it provides, when to apply it, and when to avoid it.

Patterns are not rules. Rules say "do this." Patterns say "when you encounter this situation, this approach works and here is why." You combine patterns to build a governance approach that fits your project's risk profile and team size.

## How to Use This Directory

Each file in this directory is a self-contained pattern specification. You can:

1. **Read individual patterns** when you encounter a specific governance problem
2. **Combine patterns** to build a quality control stack (see [Quality Control Patterns](../docs/quality-control-patterns.md) for how they layer together)
3. **Reference patterns in CLAUDE.md** to make them part of your agent's operating instructions
4. **Adapt patterns** to your context — the defaults are starting points, not mandates

## How Patterns Map to the 7-Layer Governance Stack

Each pattern primarily serves one or more layers of the [governance architecture](../docs/architecture.md):

| Layer | Name | Patterns |
|:-----:|------|----------|
| 1 | Constitution | [Output Contracts](output-contracts.md), [Confidence Scoring](../docs/quality-control-patterns.md#pattern-6-confidence-scoring) |
| 2 | Orchestration | [Progressive Trust](progressive-trust.md), [Blast Radius Control](blast-radius-control.md), [Human-in-the-Loop](human-in-the-loop.md) |
| 3 | Enforcement | [Dual-Model Validation](dual-model-validation.md), [Semantic Verification](semantic-verification.md), [MCP Governance](mcp-governance.md), [Regression Detection](../docs/quality-control-patterns.md#pattern-7-regression-detection) |
| 4 | Observability | [Confidence Scoring](../docs/quality-control-patterns.md#pattern-6-confidence-scoring), [Regression Detection](../docs/quality-control-patterns.md#pattern-7-regression-detection) |
| 5 | Knowledge | [Context Boundaries](context-boundaries.md) |
| 6 | Team Governance | [Human-in-the-Loop](human-in-the-loop.md), [Context Boundaries](context-boundaries.md) |
| 7 | Evolution | [Progressive Trust](progressive-trust.md) |

## Pattern Index

| Pattern | Summary |
|---------|---------|
| [Dual-Model Validation](dual-model-validation.md) | Route written work to a different model for review to catch errors the writing model systematically misses. |
| [Output Contracts](output-contracts.md) | Define expected output before the agent works so "success" is measurable, not subjective. |
| [Progressive Trust](progressive-trust.md) | Start with maximum oversight and reduce it based on evidence, tracking trust per domain independently. |
| [Semantic Verification](semantic-verification.md) | Verify that code does the right thing, not just that it runs, using assertions, examples, invariants, and negative tests. |
| [Blast Radius Control](blast-radius-control.md) | Explicitly limit what a single session can change to contain the damage from a bad session. |
| [Context Boundaries](context-boundaries.md) | Give agents exactly the context they need for a task — no more — to prevent unintended coupling and scope creep. |
| [Human-in-the-Loop](human-in-the-loop.md) | Define specific checkpoints where human judgment is genuinely required and make those checkpoints meaningful. |
| [Automation Bias Defense](automation-bias-defense.md) | Prevent AI validation layers from reducing human scrutiny. Cap confidence at configurable ceiling (default: 85%) and surface what was NOT verified. |
| [Kill Switch](kill-switch.md) | Define explicit stop triggers so agents halt immediately when confidence collapses or limits are exceeded. |
| [Session Replay](session-replay.md) | Record session decisions and actions to enable post-incident investigation and governance auditing. |
| [Knowledge Decay](knowledge-decay.md) | Manage the lifecycle of cross-session memory so stale knowledge does not degrade agent output quality. |
| [Friction Budget](friction-budget.md) | Measure and cap governance overhead so process friction does not outweigh the protection it provides. |
| [Constitutional Inheritance](constitutional-inheritance.md) | Cascade governance rules from organization to team to repo level with explicit override controls. |
| [MCP Governance](mcp-governance.md) | Govern MCP tool access with least-privilege allowlists, kill switch triggers, audit logging, environment segregation, and rate limits. |

## Pattern Groups

Related patterns that work together as a system:

| Group | Patterns | Purpose |
|-------|----------|---------|
| **Scope Control** | Blast Radius Control, Context Boundaries, Output Contracts | Limit what agents can see, change, and produce |
| **Trust Calibration** | Automation Bias Defense, Progressive Trust, Confidence Scoring | Prevent over-reliance on AI output |
| **Safety Net** | Kill Switch, Human in the Loop | Emergency stops and human override |
| **Verification** | Dual Model Validation, Semantic Verification, Session Replay | Validate correctness through independent checks |
| **Governance Evolution** | Constitutional Inheritance, Knowledge Decay, Friction Budget | Maintain and evolve governance over time |

## Further Reading

- [Quality Control Patterns](../docs/quality-control-patterns.md) — how all patterns layer into a defense-in-depth stack
- [Architecture](../docs/architecture.md) — the 7-layer governance stack these patterns enforce
- [Session Protocol](../docs/session-protocol.md) — how patterns are applied during agent sessions
- [Agents](../agents/) — specialized agent definitions that implement these patterns
