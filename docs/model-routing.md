# Model Routing: The Right Model for the Right Task

## 1. The Routing Problem

Using one AI model for everything is the equivalent of using a jackhammer to hang a picture frame. It works, technically. But it wastes resources, introduces risk, and produces worse outcomes than matching the tool to the task.

The three-tier model family — fast/cheap, balanced, powerful/expensive — exists for a reason. The models are not interchangeable. They have fundamentally different capability profiles:

- **Haiku-class** (fast and cheap): Excellent at pattern matching, retrieval, mechanical transformation. Weak at nuanced reasoning, detecting subtle logic errors, or evaluating trade-offs.
- **Sonnet-class** (balanced): Strong at code generation, structured output, following detailed instructions. Good reasoning but not deep architectural analysis.
- **Opus-class** (powerful and expensive): Deep reasoning, cross-domain synthesis, detecting subtle errors, evaluating architectural trade-offs. 10–100x the cost of Haiku.

The routing problem is this: **without deliberate routing, developers default to one model for everything**. This means paying Opus prices for config edits, or worse, using Sonnet for security reviews where Opus-level analysis is needed.

At team scale, this creates two distinct failure modes:

1. **Over-spend**: Running Opus for every task, including mechanical ones, creating AI budgets that cannot be justified to leadership.
2. **Under-quality**: Running Haiku or Sonnet for tasks that require deep reasoning — security reviews, architectural decisions — and getting outputs that look authoritative but miss critical issues.

Model routing solves both.

---

## 2. The Routing Table

The following table maps task types to optimal models, with cost estimates per task and the reasoning behind each choice.

| Task Type | Optimal Model | Approx. Cost/Task | Reasoning |
|-----------|---------------|-------------------|-----------|
| Quick lookups, file reads, retrieval | Haiku | ~$0.001 | No reasoning required; speed matters; cost negligible |
| Config edits, formatting, naming fixes | Haiku | ~$0.001 | Mechanical transformation; pattern-matching sufficient |
| Simple tests, lint fixes | Haiku | ~$0.001 | Deterministic patterns; Haiku matches well |
| Code generation (new connectors, features) | Sonnet | ~$0.01 | Follows complex instructions; produces consistent structure |
| Refactoring existing code | Sonnet | ~$0.01 | Pattern application, not deep analysis |
| Writing and updating documentation | Sonnet | ~$0.01 | Structured writing; 10x cheaper than Opus for same quality |
| PR review: naming, conventions, style | Haiku | ~$0.001 | Rule-based; does not require nuanced judgment |
| Code review: logic correctness, edge cases | Opus | ~$0.10 | Requires deep reasoning; catching plausible-but-wrong logic |
| Architecture decisions and trade-off analysis | Opus | ~$0.10 | Cross-system reasoning; detecting subtle long-term consequences |
| Security review: secrets, PII, unsafe patterns | Opus | ~$0.10 | Zero tolerance for misses; requires context-aware analysis |
| Debugging complex, multi-layer problems | Opus | ~$0.10 | Root cause analysis requires holding many variables simultaneously |
| Writing ADRs | Opus | ~$0.10 | Evaluating alternatives, trade-offs, long-term consequences |

The cost column is approximate and will vary with token volume. The relative ratios are what matter: **Opus tasks cost roughly 100x more than Haiku tasks**. Routing correctly is not a small optimization.

---

## 3. Cost Dimension

### Per-Task Cost Estimates

These estimates assume average-length contexts for each task type. Real costs depend on context window usage.

| Model | Input cost (per 1M tokens) | Output cost (per 1M tokens) | Typical task cost |
|-------|----------------------------|------------------------------|-------------------|
| Haiku | ~$0.25 | ~$1.25 | ~$0.001 |
| Sonnet | ~$3.00 | ~$15.00 | ~$0.01 |
| Opus | ~$15.00 | ~$75.00 | ~$0.10 |

### Monthly Projections at Team Scale

Assuming a team of 10 developers, each running 2 sessions per week, 4 tasks per session, across a 4-week month:

```
10 developers × 2 sessions/week × 4 tasks/session × 4 weeks = 320 tasks/month
```

**All-Sonnet (no routing)**:
320 tasks × $0.01 = **$3.20/month**

This sounds cheap. But add architectural reviews, security reviews, and ADR work (say, 20% of tasks should be Opus):
- 256 tasks × $0.01 Sonnet = $2.56
- 64 tasks × $0.10 Opus = $6.40
- Total with correct routing: **$8.96/month** — but with dramatically better quality on the 20% of tasks that matter most.

The real savings from routing are not primarily cost savings. They are **quality gains on high-stakes tasks without cost increases on routine ones**.

For a 50-developer organization, scale these numbers by 5 and add CI/CD automated reviews, and monthly AI costs become meaningful. Routing is what keeps them predictable and defensible.

### Cost Tracking

Record model usage in `docs/COST_LOG.md`:

```markdown
| Date | Session | Model | Input tokens | Output tokens | Est. cost |
|------|---------|-------|--------------|---------------|-----------|
| 2026-03-01 | 012 | sonnet | 45,000 | 12,000 | $0.31 |
| 2026-03-01 | 012 | opus | 8,000 | 3,500 | $0.38 |
```

Review monthly: which sessions used Opus for tasks that Sonnet could have handled? Which used Sonnet for tasks that needed Opus?

---

## 4. Self-Aware Agents

The central innovation in governance-based model routing is teaching the agent to **flag when it is the wrong model for the current task** rather than silently attempting work it is not well-suited for.

This requires three things:

1. The routing table is in `CLAUDE.md` — so the agent reads it at session start
2. The agent knows its own model level — provided explicitly in CLAUDE.md
3. The agent has explicit instructions to flag mismatches — not just proceed

### What Self-Aware Routing Looks Like in Practice

**Session start announcement:**
```
Running as: Sonnet
Optimal for: code generation, documentation, refactoring, config edits
NOT optimal for: security review, architecture decisions, complex debugging, ADRs
```

**Mid-session mismatch flag:**
```
Task type detected: security review of authentication module
Current model: Sonnet
Recommendation: This task is listed as Opus-optimal in the routing table.
Sonnet can attempt this review, but may miss subtle security issues.
Options:
  (1) Switch to Opus for this task, then return to Sonnet
  (2) Continue with Sonnet and flag for separate Opus security review
  (3) Proceed with Sonnet if time constraints apply
Which do you prefer?
```

**Session-end routing recommendation:**
```
Session 012 complete.
Tasks completed: 4 (code generation × 3, config edit × 1)
All tasks: Sonnet-appropriate

Upcoming tasks (from PROJECT_PLAN.md):
  - ADR-005: Decide on authentication architecture
  - Security review: new API endpoints
  - Architecture review: medallion layer boundaries

Recommended model for next session: Opus
Reason: All planned tasks are in the Opus-optimal category.
```

---

## 5. Implementation Levels

### Level 1: Manual Routing (Start Here)

The routing table lives in `CLAUDE.md`. The agent flags mismatches. The developer switches models manually using `/model` or by starting a new session with the appropriate model.

**What you need:**
- Routing table section in `CLAUDE.md`
- Agent instruction to announce its model at session start
- Agent instruction to flag Opus-optimal tasks when running on a cheaper model

**What you get:**
- Zero tooling overhead
- Immediate cost and quality awareness
- Developer education on task-model matching

### Level 2: Slash Command Routing

Predefined slash commands for each routing tier, each embedding the appropriate system context:

```
/use-haiku    → Switches to Haiku, loads lightweight context
/use-sonnet   → Switches to Sonnet, loads standard context
/use-opus     → Switches to Opus, loads full governance context + "reason deeply"
```

Each command also loads the correct prompt template from `.claude/prompts/`:

```
.claude/commands/
├── use-haiku.md     ← "You are running as Haiku. Tasks: quick lookups, config edits..."
├── use-sonnet.md    ← "You are running as Sonnet. Tasks: code generation, docs..."
└── use-opus.md      ← "You are running as Opus. Tasks: architecture, security, ADRs.
                        Reason step by step. Show trade-offs. Do not jump to conclusions."
```

### Level 3: Automatic Orchestrator (Advanced)

An orchestrator agent receives the task description, classifies it against the routing table, and routes to the appropriate specialized model-agent. The developer interacts only with the orchestrator.

```
Developer → Orchestrator (lightweight model)
              ├── classify task type
              ├── select optimal model
              └── route to: Haiku-agent | Sonnet-agent | Opus-agent
                               ↓
                          response back to developer
```

This pattern is documented in the [Master Agent architecture](../CLAUDE.md). It requires orchestration infrastructure (Anthropic Agent SDK, LangGraph, or custom) and is appropriate at Level 4+ maturity.

---

## 6. Session-End Routing

At the end of every session, the agent produces a routing recommendation for the next session. This is embedded in the session-end protocol in `CLAUDE.md`:

```markdown
## session_end_routing_recommendation

At session end, review PROJECT_PLAN.md for upcoming tasks.
Classify each upcoming task against the routing table.
Produce a recommendation in this format:

---
Next session tasks:
  [task 1] → [model recommendation]
  [task 2] → [model recommendation]

Recommended model for next session: [Haiku | Sonnet | Opus]
Reason: [one sentence]

If tasks span multiple tiers, recommend the highest tier present.
---
```

This means the developer never has to think about model selection at session start. The previous session's agent has already done it.

---

## 7. Model Routing in CLAUDE.md

The following block belongs in `CLAUDE.md` for any team using model routing:

```yaml
## model_routing

You are running as: [SONNET | HAIKU | OPUS — fill in at session start]

## Routing table
task_type: [code_generation, connector, sql_transform, feature]
  optimal_model: sonnet
  cost_estimate: ~$0.01/task
  notes: good balance of quality and cost for structured code production

task_type: [config_edit, formatting, naming_fix, simple_test]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: mechanical tasks; speed over depth

task_type: [documentation, changelog, adr_notes]
  optimal_model: sonnet
  cost_estimate: ~$0.01/task
  notes: structured writing; haiku is too shallow, opus unnecessary

task_type: [code_review_logic, edge_case_analysis]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: catching plausible-but-wrong logic requires deep reasoning

task_type: [architecture_decision, trade_off_analysis]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: cross-system reasoning; long-term consequences

task_type: [security_review, pii_scan, credential_check]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: zero tolerance for misses; context-aware analysis required

task_type: [debugging_complex, root_cause_analysis]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: holding multiple system layers simultaneously

task_type: [adr_writing, formal_decision_record]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: must evaluate alternatives and long-term consequences

task_type: [pr_review_conventions, naming_check]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: rule-based; no judgment required

task_type: [refactoring]
  optimal_model: sonnet
  cost_estimate: ~$0.01/task
  notes: pattern application; does not require deep analysis

task_type: [file_lookup, retrieval, quick_summary]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: retrieval, not reasoning

## Self-awareness instructions
At session start: announce your model and optimal task types.
During session: if task type is NOT in your optimal list, flag it immediately.
At session end: review upcoming tasks in PROJECT_PLAN.md and recommend model for next session.
Do not silently attempt tasks outside your optimal range.
```

---

## 8. Vendor-Agnostic Principles

The routing framework described here uses Anthropic model names (Haiku, Sonnet, Opus). The underlying principles apply to any multi-tier model family:

| Anthropic | OpenAI | Google | Mistral | Role |
|-----------|--------|--------|---------|------|
| Haiku | GPT-4o Mini | Gemini Flash | Mistral Small | Fast / cheap / mechanical |
| Sonnet | GPT-4o | Gemini Pro | Mistral Large | Balanced / production |
| Opus | o1 / o3 | Gemini Ultra | — | Deep reasoning / critical |

The routing table concept is independent of vendor. The three tiers — execute, generate, reason — exist across all major AI providers.

**To adapt for a different vendor:**

1. Replace model names in `CLAUDE.md`'s routing table
2. Update cost estimates (they will differ)
3. Adjust capability assumptions (each model has unique strengths)
4. Test the routing on a sample of past tasks to validate

For teams using OpenAI: GPT-4o mini maps well to Haiku, GPT-4o maps to Sonnet, and o1/o3 maps to Opus for reasoning-heavy tasks.

For teams using self-hosted open source models: Routing still applies, but the Opus tier (deep reasoning) remains weakest for open source models as of early 2026. Use cloud models for security review and architectural decisions even if daily coding uses local models.

**The vendor-agnostic principle:**
> Route based on task cognitive load, not model brand. Mechanical tasks go to fast models. Reasoning tasks go to capable models. This principle does not change as models evolve or vendors change.

---

*Related guides: [Security Guide](./security-guide.md) | [Metrics Guide](./metrics-guide.md) | [Enterprise Playbook](./enterprise-playbook.md)*
