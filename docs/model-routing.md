# Model Routing: Dynamic Model Selection as a Governance Discipline

## 1. The Routing Problem

Using one AI model for everything is the equivalent of dispatching a neurosurgeon for every medical complaint — including a headache. It works, technically. But it wastes resources, introduces unnecessary cost, and does not produce better outcomes for routine cases.

The three-tier model family — fast/cheap, balanced, powerful/expensive — exists because tasks have fundamentally different cognitive requirements. The models are not interchangeable:

- **Haiku-class** (fast and cheap): Excellent at pattern matching, retrieval, mechanical transformation, and rule-based checks. Weak at nuanced reasoning, detecting subtle logic errors, or evaluating trade-offs between competing architectural approaches.
- **Sonnet-class** (balanced): Strong at code generation, structured output, following detailed instructions, and applying known patterns to new contexts. Good reasoning capacity but not deep enough for architectural analysis or security review where misses have critical consequences.
- **Opus-class** (powerful and expensive): Deep reasoning, cross-domain synthesis, detecting subtle errors that pass the glance test, evaluating architectural trade-offs with long-term consequences. 10-100x the cost of Haiku-class models.

Without deliberate routing, developers default to one model for everything. This creates two distinct governance failures:

1. **Over-spend**: Running Opus for every task — including config edits and file reads — creates AI budgets that cannot be justified to leadership and are genuinely wasteful.
2. **Under-quality**: Running Haiku or Sonnet for tasks that require deep reasoning — security reviews, architectural decisions, complex debugging — produces outputs that look authoritative but miss critical issues. This is the more dangerous failure, because the output's surface quality masks the depth deficit.

Model routing is not an optimization. It is a governance discipline: matching the right level of cognitive capability to the right task, ensuring both cost efficiency and output quality. Just as you would not assign a junior developer to review security-critical code, you should not assign a fast-but-shallow model to review your authentication architecture.

---

## 2. The Routing Table

The following table maps eleven task types to optimal models, with cost estimates and the reasoning behind each assignment.

| Task Type | Optimal Model | Approx. Cost/Task | Why This Model |
|-----------|---------------|-------------------|----------------|
| Quick lookups, file reads, retrieval | Haiku | ~$0.001 | No reasoning required. Speed matters. Information extraction, not analysis. |
| Config edits, formatting, naming fixes | Haiku | ~$0.001 | Mechanical transformation. Pattern-matching is sufficient. No judgment needed. |
| Simple tests, lint fixes, boilerplate | Haiku | ~$0.001 | Deterministic patterns. Haiku produces identical quality to Opus for these tasks at 1/100th the cost. |
| Code generation (connectors, features, transforms) | Sonnet | ~$0.01 | Follows complex instructions. Produces consistent structure. Handles multi-file changes with coherent patterns. |
| Refactoring existing code | Sonnet | ~$0.01 | Pattern application across a defined scope. Does not require deep analysis of long-term consequences. |
| Writing and updating documentation | Sonnet | ~$0.01 | Structured writing with consistent tone. 10x cheaper than Opus for equivalent documentation quality. |
| PR review: naming, conventions, style compliance | Haiku | ~$0.001 | Rule-based checking. Does not require nuanced judgment — either the convention is followed or it is not. |
| Code review: logic correctness, edge cases | Opus | ~$0.10 | Requires deep reasoning. Catching plausible-but-wrong logic requires holding the business context, the code path, and the edge cases simultaneously. |
| Architecture decisions and trade-off analysis | Opus | ~$0.10 | Cross-system reasoning. Must evaluate second and third-order consequences, compatibility with existing decisions, and long-term maintainability. |
| Security review: secrets, PII, unsafe patterns | Opus | ~$0.10 | Zero tolerance for misses. Requires context-aware analysis that distinguishes real credentials from examples, real PII from test data. |
| Debugging complex, multi-layer problems | Opus | ~$0.10 | Root cause analysis requires holding many variables simultaneously: call stack, data flow, state, configuration, timing. |

**The 100x cost ratio is the governing fact.** One Opus task costs the same as one hundred Haiku tasks. Routing correctly is not a marginal optimization — it is the difference between a defensible AI budget and an indefensible one.

---

## 3. Cost at Scale

### Per-Model Cost Reference

| Model Class | Input (per 1M tokens) | Output (per 1M tokens) | Typical Task Cost |
|-------------|----------------------|------------------------|-------------------|
| Haiku | ~$0.25 | ~$1.25 | ~$0.001 |
| Sonnet | ~$3.00 | ~$15.00 | ~$0.01 |
| Opus | ~$15.00 | ~$75.00 | ~$0.10 |

### Monthly Projections for a Team of 10

Assumptions: 10 developers, 3 sessions per week, 5 tasks per session, 4-week month.

```
10 developers x 3 sessions/week x 5 tasks/session x 4 weeks = 600 tasks/month
```

**Scenario A: All-Sonnet (no routing)**
600 tasks x $0.01 = **$6.00/month**
Looks cheap. But 20% of these tasks needed Opus-level reasoning and received Sonnet-level analysis. The security review that missed a credential exposure. The architecture decision that introduced a pattern conflict. The cost of these quality failures dwarfs the AI spend.

**Scenario B: All-Opus (no routing, "premium")**
600 tasks x $0.10 = **$60.00/month**
10x the cost. No quality improvement on the 60% of tasks that are mechanical or routine. Budget conversation with leadership becomes difficult to win.

**Scenario C: Correct routing**
- 240 tasks (40%) at Haiku: $0.24
- 240 tasks (40%) at Sonnet: $2.40
- 120 tasks (20%) at Opus: $12.00
- **Total: $14.64/month**

Scenario C costs 2.4x Scenario A but delivers dramatically better quality on the 20% of tasks that carry the most risk. It costs 75% less than Scenario B with no quality degradation on high-stakes tasks.

**At 50-developer scale**, multiply by 5: $73/month for correct routing vs. $300/month for all-Opus. Over a year, that is $2,736 in savings — while maintaining Opus quality where it matters.

The real value of routing is not primarily cost savings. It is **quality assurance on high-stakes tasks without overspending on routine ones**.

### Cost Tracking

Record model usage in `docs/COST_LOG.md`:

```markdown
| Date | Session | Model | Tasks | Input Tokens | Output Tokens | Est. Cost |
|------|---------|-------|-------|--------------|---------------|-----------|
| 2026-03-01 | 012 | sonnet | 4 | 45,000 | 12,000 | $0.31 |
| 2026-03-01 | 012 | opus | 1 | 8,000 | 3,500 | $0.38 |
| 2026-03-02 | 013 | haiku | 6 | 15,000 | 4,000 | $0.01 |
```

Review monthly: which sessions used Opus for tasks that Sonnet could have handled? Which used Sonnet for tasks that needed Opus? The second question is more important — under-routing is more dangerous than over-routing.

---

## 4. Self-Aware Agents

The central innovation in governance-based model routing is teaching the agent to **know its own capability level and flag when it is the wrong model for the current task** — rather than silently attempting work it is not well-suited for.

This requires three things:

1. The routing table is in `CLAUDE.md` — so the agent reads it at session start
2. The agent is told its own model level — explicitly stated in `CLAUDE.md` or the session context
3. The agent has explicit instructions to flag mismatches — not just proceed with a best effort

### What Self-Aware Routing Looks Like in Practice

**Session start announcement:**
```
Running as: Sonnet
Optimal for: code generation, documentation, refactoring, config edits, SQL transforms
NOT optimal for: security review, architecture decisions, complex debugging, ADR writing

If a task in this session falls into my "NOT optimal" category, I will flag it
and recommend switching to Opus before proceeding.
```

**Mid-session mismatch detection:**
```
Task type detected: security review of authentication module
Current model: Sonnet
Routing table recommendation: Opus

This task is in the Opus-optimal category. Sonnet can attempt this review,
but has a higher probability of missing subtle security issues — especially
in edge cases around token validation and session handling.

Options:
  (1) Start a new session with Opus for this specific task
  (2) Continue with Sonnet and flag the output for separate Opus security review
  (3) Proceed with Sonnet if time constraints require it — with the understanding
      that this review should not be considered comprehensive

Recommendation: Option 1 for production code. Option 2 if this is a draft.
```

**Session-end routing recommendation:**
```
Session 012 complete.
Tasks completed: 5 (code generation x3, config edit x1, documentation x1)
All tasks: Sonnet-appropriate. No routing mismatches.

Upcoming tasks (from PROJECT_PLAN.md):
  - ADR-005: Authentication architecture decision
  - Security review: new API endpoints in /api/v2/
  - Architecture review: medallion layer boundary enforcement

Recommended model for next session: Opus
Reason: All three planned tasks are in the Opus-optimal category.
None should be attempted with Sonnet.
```

### The CLAUDE.md Specification for Self-Awareness

Add this to `CLAUDE.md`:

```markdown
## self_awareness

You know your own model level. At session start, announce:
- Your model (Haiku / Sonnet / Opus)
- Your optimal task types (from the routing table)
- Your non-optimal task types

During the session, if you detect a task that is NOT in your optimal list:
- Stop before starting the task
- Announce the mismatch
- Recommend the appropriate model
- Wait for the developer's decision before proceeding

Do NOT silently attempt tasks outside your optimal range.
A Sonnet that flags "this needs Opus" is more valuable than a Sonnet that
attempts a security review and misses a critical issue.
```

---

## 5. Implementation Levels

### Level 1: Manual Routing (Start Here)

The routing table lives in `CLAUDE.md`. The agent flags mismatches. The developer switches models manually using `/model` or by starting a new session with the appropriate model.

**What you need:**
- Routing table section in `CLAUDE.md` (see section 9)
- Agent instruction to announce its model at session start
- Agent instruction to flag Opus-optimal tasks when running as a cheaper model

**What you get:**
- Zero tooling overhead
- Immediate cost and quality awareness
- Developer education on task-model matching
- Foundation for more advanced routing

**Effort:** 15 minutes to add the routing table and self-awareness instructions to `CLAUDE.md`.

### Level 2: Slash Command Routing

Predefined slash commands for each routing tier, each embedding the appropriate system context and behavioral instructions:

```
.claude/commands/
├── use-haiku.md     <- "You are running as Haiku. Optimal for: quick lookups,
│                       config edits, simple tests, naming checks.
│                       Do NOT attempt: security review, architecture decisions,
│                       complex debugging. Flag these immediately."
│
├── use-sonnet.md    <- "You are running as Sonnet. Optimal for: code generation,
│                       documentation, refactoring, SQL transforms.
│                       Do NOT attempt: security review, architecture decisions.
│                       Flag these and recommend Opus."
│
└── use-opus.md      <- "You are running as Opus. Optimal for: architecture decisions,
                        security review, complex debugging, ADR writing, trade-off analysis.
                        Reason step by step. Show your reasoning explicitly.
                        Do not jump to conclusions. Evaluate alternatives before recommending."
```

Each command loads the appropriate context depth: Haiku gets minimal context (saves tokens), Sonnet gets standard context, Opus gets full governance context plus architectural history.

**Effort:** 1-2 hours to write the command files and test them.

### Level 3: Automatic Orchestrator (Advanced)

An orchestrator agent receives the task description, classifies it against the routing table, and routes to the appropriate specialized model-agent. The developer interacts only with the orchestrator.

```
Developer -> Orchestrator (lightweight model, e.g., Haiku)
              |-- Classify task type against routing table
              |-- Select optimal model
              |-- Route to: Haiku-agent | Sonnet-agent | Opus-agent
                               |
                          Response back to developer via orchestrator
```

This requires orchestration infrastructure (Anthropic Agent SDK, LangGraph, or custom routing) and is appropriate at Level 4+ governance maturity. Do not attempt this before Levels 1 and 2 are working smoothly.

**Effort:** Days to weeks, depending on infrastructure. Not recommended until you have at least 3 months of Level 1-2 routing data to validate routing accuracy.

---

## 6. Session-End Routing

At the end of every session, the agent produces a routing recommendation for the next session. This is embedded in the session-end protocol in `CLAUDE.md`:

```markdown
## session_end_routing_recommendation

At session end, after completing all governance file updates:

1. Review PROJECT_PLAN.md for upcoming tasks
2. Classify each upcoming task against the routing table
3. Produce a recommendation in this format:

---
Next session planned tasks:
  [task 1] -> [model recommendation] ([reason])
  [task 2] -> [model recommendation] ([reason])
  [task 3] -> [model recommendation] ([reason])

Recommended model for next session: [Haiku | Sonnet | Opus]
Reason: [one sentence explaining the choice]

If tasks span multiple tiers, recommend the highest tier present.
An Opus session can handle Sonnet tasks efficiently;
a Sonnet session cannot handle Opus tasks safely.
---
```

This means the developer never has to think about model selection at session start. The previous session's agent has already done the analysis.

---

## 7. Auto-Generated Review Prompts

When a Sonnet session produces changes that cross a significance threshold, the agent automatically generates a review prompt for Opus. The developer does not need to write the review prompt — it is produced as part of the session-end protocol.

### Significance Triggers

Generate an Opus review prompt when:
- More than 5 new files created in a single session
- Any architectural change (new layer, new integration pattern, new boundary)
- Governance files modified (`CLAUDE.md`, `ARCHITECTURE.md`)
- Security-sensitive code touched (authentication, authorization, encryption, API keys)
- A complete document or ADR written or significantly expanded
- Any code that handles financial data, health data, or PII

### Auto-Generated Prompt Format

```markdown
## Opus Review: Session [NNN] Output

**Session model:** Sonnet
**Session date:** [date]
**Review trigger:** [which threshold was crossed]

**What changed:**
[List of files created/modified with one-line descriptions]

**What to review:**
1. [Specific concern 1 — e.g., "New authentication flow in auth/oauth.py — verify edge cases for expired tokens"]
2. [Specific concern 2 — e.g., "Architecture change: new middleware layer — verify consistency with ARCHITECTURE.md"]
3. [Specific concern 3]

**Context files to load:**
- ARCHITECTURE.md (current architecture)
- [Relevant ADR if applicable]
- [The specific files to review]

**Review instructions:**
Review the changes listed above for:
- Logical correctness at edge cases
- Architectural consistency with existing patterns
- Security assumptions and failure handling
- Long-term maintainability implications

Produce: PASS / WARN (with specifics) / FAIL (with specifics)
```

The developer copy-pastes this prompt into an Opus session. The review prompt is generated by the agent, not the human — eliminating the "I should probably review this but I don't feel like writing the prompt" friction.

---

## 8. Vendor-Agnostic Principles

The routing framework described here uses Anthropic model names (Haiku, Sonnet, Opus). The underlying principles apply to any multi-tier model family.

### Cross-Vendor Mapping

| Role | Anthropic | OpenAI | Google | Mistral |
|------|-----------|--------|--------|---------|
| Execute (fast/cheap/mechanical) | Haiku | GPT-4o Mini | Gemini Flash | Mistral Small |
| Generate (balanced/production) | Sonnet | GPT-4o | Gemini Pro | Mistral Large |
| Reason (deep/critical/expensive) | Opus | o1 / o3 | Gemini Ultra | -- |

### The Universal Routing Principle

> Route based on task cognitive load, not model brand. Mechanical tasks go to fast models. Reasoning tasks go to capable models. This principle does not change as models evolve or vendors change.

The three tiers — **execute, generate, reason** — exist across all major AI providers. The specific cost ratios and capability boundaries shift as models improve, but the principle of matching cognitive requirement to model capability is permanent.

### Adapting for a Different Vendor

1. Replace model names in `CLAUDE.md`'s routing table
2. Update cost estimates (pricing varies significantly between vendors)
3. Adjust capability assumptions — each model family has unique strengths (e.g., OpenAI o1/o3 excels at mathematical reasoning; Claude Opus excels at long-document analysis and nuanced instruction following)
4. Test the routing on a sample of 10-20 past tasks to validate that the tier assignments produce expected quality
5. Update the self-awareness instructions to match the new model names

### Open Source Considerations

For teams using self-hosted open source models (Llama, Mistral, DeepSeek via Ollama or similar):

- The execute and generate tiers are well-served by open source models as of early 2026
- The reason tier (deep reasoning for security, architecture, complex debugging) remains weakest for open source models
- **Recommendation:** Use local models for daily coding, config edits, documentation, and routine refactoring. Use cloud models for security review, architectural decisions, and ADR writing — even if daily coding uses local models
- This hybrid approach gives you data sovereignty for routine work and maximum quality for critical decisions

---

## 9. The Routing Table in CLAUDE.md

Copy the following block into `CLAUDE.md` for any team using model routing:

```yaml
## model_routing

You are running as: [SONNET | HAIKU | OPUS — set at session start]

## routing_table

# Execute tier (Haiku-optimal)
task_type: [file_lookup, retrieval, quick_summary]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: retrieval, not reasoning — speed over depth

task_type: [config_edit, formatting, naming_fix]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: mechanical tasks; pattern-matching sufficient

task_type: [simple_test, lint_fix, boilerplate]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: deterministic patterns; no judgment required

task_type: [pr_review_conventions, naming_check, style_compliance]
  optimal_model: haiku
  cost_estimate: ~$0.001/task
  notes: rule-based; follows or violates, no nuance

# Generate tier (Sonnet-optimal)
task_type: [code_generation, connector, sql_transform, feature]
  optimal_model: sonnet
  cost_estimate: ~$0.01/task
  notes: good balance of quality and cost for structured code production

task_type: [refactoring]
  optimal_model: sonnet
  cost_estimate: ~$0.01/task
  notes: pattern application across defined scope; not deep analysis

task_type: [documentation, changelog, release_notes]
  optimal_model: sonnet
  cost_estimate: ~$0.01/task
  notes: structured writing; haiku too shallow, opus unnecessary

# Reason tier (Opus-optimal)
task_type: [code_review_logic, edge_case_analysis]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: catching plausible-but-wrong logic requires deep reasoning

task_type: [architecture_decision, trade_off_analysis]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: cross-system reasoning; long-term consequences; must evaluate alternatives

task_type: [security_review, pii_scan, credential_check]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: zero tolerance for misses; context-aware analysis required

task_type: [debugging_complex, root_cause_analysis]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: holding multiple system layers and state simultaneously

task_type: [adr_writing, formal_decision_record]
  optimal_model: opus
  cost_estimate: ~$0.10/task
  notes: must evaluate alternatives, trade-offs, and long-term consequences

## self_awareness_instructions
At session start: announce your model and list your optimal and non-optimal task types.
During session: if a task is NOT in your optimal list, STOP and flag it immediately.
  Do not silently attempt tasks outside your optimal range.
  A model that flags "this needs a more capable model" is more valuable
  than a model that attempts the task and produces subtly wrong output.
At session end: review upcoming tasks in PROJECT_PLAN.md and recommend model for next session.
```

---

*Related guides: [Security Guide](./security-guide.md) | [Metrics Guide](./metrics-guide.md) | [Enterprise Playbook](./enterprise-playbook.md) | [AI Code Quality](./ai-code-quality.md)*
