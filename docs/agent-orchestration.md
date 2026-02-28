# Agent Orchestration

## The Problem with Flat Agent Architecture

Most teams adopt AI agents as independent tools. A developer types "run security review." Another invokes the code reviewer. A third asks a general-purpose agent to write tests. Each agent operates in isolation: no shared context, no coordination, no quality control between them.

This is a hospital with 12 specialists and no chief physician coordinating care. The cardiologist orders a medication. The neurologist orders a conflicting one. The radiologist reads a scan without knowing the surgical plan. Each specialist is competent individually. The patient outcome suffers because nobody is integrating the picture.

In software terms, the flat agent architecture produces:

- **Redundant work.** The code reviewer flags an issue that the security reviewer also flags, phrased differently. The documentation writer updates a section the code reviewer just rewrote. Nobody deduplicates.
- **Context loss.** Each agent starts from scratch. The security reviewer does not know which architectural constraints the code reviewer already validated. The test writer does not know which edge cases the code reviewer identified as high-risk.
- **No sequencing.** Agents run in whatever order the developer remembers. Security review happens after merge instead of before. Documentation updates happen three sessions late. Quality checks happen on stale code.
- **Conflicting outputs.** The code reviewer suggests refactoring a function into two. The test writer writes tests for the original single function. The developer now has to reconcile both, negating the efficiency gain.

The fundamental issue is not that individual agents are weak. It is that without orchestration, agent outputs do not compose into coherent project outcomes.

---

## The Master Agent Pattern

The master agent pattern introduces a coordinating layer between the human and the specialized agents. The master agent reads project context, decomposes requests into sub-tasks, routes each sub-task to the optimal specialist, validates outputs, and assembles a unified result.

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER AGENT                              │
│  Reads: CLAUDE.md, PROJECT_PLAN.md, ARCHITECTURE.md         │
│  Role: Orchestrate, delegate, validate, escalate            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Security │  │   Code   │  │  Quality │  │  Docs    │   │
│  │ Reviewer │  │ Reviewer │  │   Gate   │  │  Writer  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│       └──────────────┴──────┬───────┴──────────────┘         │
│                             │                                │
│                    SHARED CONTEXT                             │
│         (MEMORY.md, session state, quality scores)           │
└─────────────────────────────────────────────────────────────┘
```

The master agent never writes production code. It reads, delegates, validates, and reports. This separation is deliberate: an agent that both orchestrates and implements will prioritize implementation over coordination under context pressure. The orchestrator must remain above the work to maintain perspective on the whole.

---

## How the Master Agent Works

The orchestration loop has seven steps. Each step has a defined input and output. Skipping a step degrades the system — particularly steps 5 (validation) and 7 (reporting), which teams skip first when they feel the process is slowing them down.

### Step 1: Task Intake

The human describes what they want. The master agent reads the request alongside current project state: `CLAUDE.md` for rules, `PROJECT_PLAN.md` for sprint context, `ARCHITECTURE.md` for structural constraints, and `MEMORY.md` for cross-session context.

The master agent confirms its understanding before proceeding: "You want X. This maps to sprint goal Y. It will affect files in Z directory. Proceed?"

### Step 2: Decomposition

The master agent breaks the request into sub-tasks, each scoped to a single specialist. Decomposition follows the project's architectural boundaries — a task that crosses two layers becomes two sub-tasks, one per layer.

Each sub-task specifies:
- What needs to be done (concrete deliverable, not vague direction)
- Which files are in scope (explicit list, not "whatever is relevant")
- What constraints apply (from CLAUDE.md, ARCHITECTURE.md, or ADRs)
- What the output should look like (format, location, naming)

### Step 3: Routing

Each sub-task is assigned to a specialist agent. Routing considers the [model routing table](model-routing.md) — not every sub-task needs the same model class. A boilerplate configuration change routes to a Haiku-class model. A security review of authentication logic routes to Opus-class.

The master agent also determines execution order. Tasks with dependencies execute sequentially. Independent tasks can execute in parallel.

### Step 4: Execution

Sub-agents receive their tasks with full context injection (see [Agent Memory and Context Sharing](#agent-memory-and-context-sharing)). Each sub-agent works within its defined scope. If a sub-agent encounters something outside its scope, it reports back to the master agent rather than expanding its own work.

### Step 5: Validation

The master agent reviews each sub-agent's output against the original task specification. The [quality gate agent](../agents/quality-gate-agent.md) runs its checks. Outputs that fail validation are returned to the sub-agent with specific feedback, or escalated to the human if the issue requires judgment.

### Step 6: Assembly

The master agent combines all validated sub-agent outputs into a coherent whole. This includes:
- Verifying that cross-references between outputs are consistent (e.g., tests reference the correct function names)
- Ensuring documentation matches the code that was written
- Checking that no two sub-agents made conflicting changes to the same file
- Resolving any remaining inconsistencies

### Step 7: Reporting

The master agent presents a unified summary to the human:
- What was requested
- What was delivered (files created or modified, with paths)
- What was validated (quality gate results)
- What was deferred (out-of-scope items discovered during work)
- What needs human attention (escalated decisions, low-confidence outputs)
- How this advances the sprint goal

---

## Sub-Agent Communication Protocol

Without a defined protocol, agent-to-agent communication degrades into the telephone game: information loses fidelity at every handoff. The protocol defines four contracts that every sub-agent interaction must follow.

### Input Contract

What the sub-agent receives from the master agent:

| Field | Required | Description |
|-------|----------|-------------|
| `task` | Yes | Concrete description of what to do, scoped to a single deliverable |
| `context` | Yes | Relevant excerpts from CLAUDE.md, ARCHITECTURE.md, MEMORY.md |
| `constraints` | Yes | Rules that apply to this specific task (naming, patterns, forbidden actions) |
| `output_format` | Yes | Expected structure of the result (file paths, report format, code style) |
| `scope_boundary` | Yes | Explicit list of files the sub-agent may read and write |
| `escalation_triggers` | No | Conditions under which the sub-agent should stop and report back |

### Output Contract

What the sub-agent must return to the master agent:

| Field | Required | Description |
|-------|----------|-------------|
| `result` | Yes | The deliverable: code, report, documentation, or analysis |
| `confidence` | Yes | 0-100 score reflecting the sub-agent's certainty in its output |
| `files_changed` | Yes | List of files created, modified, or deleted with paths |
| `issues_found` | No | Problems discovered during work that are outside the sub-agent's scope |
| `deferred_items` | No | Work identified but intentionally not done (with rationale) |
| `dependencies` | No | Other tasks or decisions this output depends on |

### Escalation Rules

A sub-agent should escalate back to the master agent instead of continuing when:

- **Confidence drops below 70%.** The sub-agent is uncertain whether its output is correct. Continuing produces work that may need to be discarded entirely.
- **Scope boundary would be violated.** The task requires modifying files outside the defined scope. The sub-agent does not expand scope unilaterally.
- **Conflicting constraints.** Two rules in CLAUDE.md or ARCHITECTURE.md appear to contradict each other for this specific case. The sub-agent flags the conflict rather than choosing which rule to follow.
- **Missing context.** The sub-agent needs information that was not provided in the input contract and cannot be inferred from the files in scope.
- **Architectural decision required.** The task requires choosing between approaches that have long-term consequences not covered by existing ADRs.

### Conflict Resolution

When two sub-agents produce conflicting outputs:

1. The master agent identifies the specific conflict (not "they disagree" but "Agent A changed line 42 of `config.py` to X while Agent B changed it to Y").
2. The master agent checks whether CLAUDE.md or an ADR resolves the conflict. If a documented rule applies, the rule wins.
3. If no documented rule applies, the master agent presents both outputs to the human with the trade-offs of each approach.
4. The human decides. The decision is logged in `DECISIONS.md` and, if significant enough, becomes an ADR.

---

## Agent Spawn Rules

Not every task requires every agent. Spawning unnecessary agents wastes tokens, increases latency, and produces noise. The following rules define which agents activate under which conditions.

| Trigger | Agents Spawned | Rationale |
|---------|---------------|-----------|
| Every session | Security reviewer | Security is non-negotiable. Every change is scanned. |
| PR or merge to main | Code reviewer + quality gate | Merge is the last gate before code enters the shared branch. |
| Architecture change detected | Master agent + documentation writer | Architectural changes require coordination and documentation updates. |
| New feature implementation | Test writer + code reviewer | New code needs tests and convention checks before it compounds. |
| Session end | Documentation writer | CHANGELOG, MEMORY.md, and PROJECT_PLAN.md must reflect the session's work. |
| On demand | Research agent, onboarding agent | These serve specific needs and should not run automatically. |

The security reviewer is the only always-active agent because security violations have asymmetric consequences: a missed naming convention costs minutes to fix later; a committed secret costs an incident response.

---

## Agent Memory and Context Sharing

This is the hardest problem in multi-agent orchestration. Sub-agents spawned via Claude Code's Task tool do not automatically inherit the parent session's context. They start with a clean slate. If the master agent has read `MEMORY.md` and understands the project's history, a spawned sub-agent does not — unless that context is explicitly provided.

Three solutions, in order of reliability:

### 1. Explicit Context Injection

The master agent includes relevant excerpts from `MEMORY.md`, `CLAUDE.md`, and session state directly in the sub-agent's prompt. This is the most reliable approach because the sub-agent receives exactly the context it needs, with no dependency on external file reads.

The trade-off is token cost. Injecting full context into every sub-agent prompt multiplies token consumption by the number of sub-agents. The master agent should inject only the sections relevant to each sub-task, not the entire knowledge base.

### 2. Shared State File

A temporary `.agent-session-state.json` file that all agents in the session read and write. The master agent initializes it with session context. Sub-agents append their results. The master agent reads the aggregated state after all sub-agents complete.

```json
{
  "session_id": "2026-02-28-001",
  "sprint_goal": "Complete API connector layer",
  "active_task": "Add payment connector",
  "sub_agent_results": [
    {
      "agent": "code-reviewer",
      "status": "complete",
      "confidence": 88,
      "files_reviewed": ["src/connectors/payment.py"],
      "findings": 2
    }
  ],
  "escalations": [],
  "context_notes": "ADR-003 requires all connectors to implement validate() before fetch()"
}
```

The trade-off is coordination complexity. File-based state requires agents to read before writing and handle the case where two agents write simultaneously. For sequential orchestration this works well. For parallel execution, explicit context injection is safer.

### 3. Result Aggregation

The master agent collects all sub-agent outputs into a unified session summary after all work completes. This is the simplest approach: sub-agents work independently, the master agent synthesizes afterward.

The trade-off is that sub-agents cannot benefit from each other's findings during execution. The code reviewer cannot adjust its review based on the security reviewer's findings because both run independently. This is acceptable for most workflows and problematic only when agent outputs are highly interdependent.

---

## Implementation Levels

Agent orchestration is not all-or-nothing. Teams adopt it incrementally, and each level delivers value independently.

### Level 1: Manual Invocation (Available Now)

Agent definition files live in `agents/` (or `.claude/agents/` in your project). The developer manually invokes each agent: "Run the security review on this diff." "Run the code reviewer." There is no coordination between agents. The developer is the orchestrator.

**Value:** Specialized agents produce better output than a single generalist agent. A security reviewer with an adversarial system prompt catches things a cooperative assistant misses. A code reviewer checking against documented rules is more consistent than ad-hoc review.

**Limitation:** The developer must remember which agents to run, in what order, and how to reconcile their outputs. This works for solo developers. It breaks down at team scale.

### Level 2: Chained Commands (Next Step)

Slash commands chain agents into workflows. `/review` runs the security reviewer, then the code reviewer, then the quality gate — automatically, in sequence. The output of each agent feeds into the next.

**Value:** Consistent multi-agent workflows without manual coordination. Every PR gets the same review sequence. No agent is accidentally skipped.

**Limitation:** The chain is static. The same agents run in the same order regardless of what changed. A documentation-only PR still runs through the full code review pipeline.

### Level 3: Dynamic Orchestration (Future)

The master agent is the entry point. The human describes intent ("add a payment connector"), and the master agent decomposes, routes, validates, and reports. Agent selection is dynamic: the master agent reads the request and determines which specialists are needed.

**Value:** The human operates at the intent level. The orchestration layer handles the mechanics. Agent selection adapts to the task.

**Limitation:** Requires mature agent definitions, reliable context sharing, and well-tested input/output contracts. Premature adoption produces unpredictable orchestration.

### Level 4: Autonomous Orchestration (Vision)

The master agent reads `PROJECT_PLAN.md`, identifies the next task in the sprint backlog, executes it with sub-agents, validates the result, and reports to the human. The human reviews completed work rather than initiating it.

**Value:** The AI agent system operates as an autonomous development partner, constrained by the governance framework.

**Limitation:** This requires high confidence in every other layer of the framework. The constitution must be comprehensive, enforcement must be robust, observability must be complete. Autonomy without governance is reckless. Autonomy with governance is powerful.

---

## Anti-Patterns

### Agent Soup

**Symptom:** 15 agents defined, 8 with overlapping responsibilities, nobody sure which to use for what.

**Cause:** Adding a new agent for every new concern instead of extending existing agents with broader capability.

**Fix:** Each agent should have a single, non-overlapping responsibility. If two agents review code — one for style and one for architecture — merge them into one code reviewer with both checks, or draw a hard boundary between their scopes. The test is: given any task, can you identify exactly one agent responsible for it without ambiguity?

### Telephone Game

**Symptom:** Information degrades as it passes between agents. The master agent tells the code reviewer about a constraint. The code reviewer passes a simplified version to the test writer. The test writer receives a distorted version of the original constraint.

**Cause:** Relying on agent-to-agent paraphrasing instead of passing original source material.

**Fix:** Sub-agents always receive context from the original source (CLAUDE.md excerpt, ADR text, architecture diagram), never from another agent's summary. The master agent acts as a router, not a translator.

### Master Bottleneck

**Symptom:** Everything routes through the master agent. Simple tasks that one agent could handle independently require the full orchestration cycle. Developers complain the process is slower than direct invocation.

**Cause:** Over-centralizing control without providing a direct-invocation escape hatch.

**Fix:** The master agent handles multi-step, multi-agent tasks. Single-agent tasks bypass the master and invoke the specialist directly. The routing rule is simple: if a task requires one agent, invoke it directly. If it requires two or more, use the master.

### Over-Orchestration

**Symptom:** A typo fix routes through the master agent, which spawns the code reviewer, which triggers the quality gate, which produces a 40-line report for a one-character change.

**Cause:** Applying the full orchestration pipeline to every change regardless of scope.

**Fix:** Define a complexity threshold. Changes under the threshold (single-file, under 20 lines, no architectural impact) go directly to the relevant agent. Changes above the threshold go through the master. Document the threshold in CLAUDE.md so the rule is consistent.

---

## Connecting to the 7-Layer Stack

Agent orchestration does not exist in isolation. It is the operational mechanism that makes several layers of the [architecture](architecture.md) work together.

### Layer 2: Orchestration

The master agent is the runtime implementation of Layer 2. Where the [session protocol](session-protocol.md) defines the rules for how work flows — start with governance sync, confirm scope, report after each task, update state at session end — the master agent executes those rules. It reads the session protocol from CLAUDE.md and follows it without the human needing to remember each step.

The session protocol specifies *what* should happen. The master agent ensures it *does* happen.

### Layer 4: Observability

Every step of the orchestration loop generates observable data. Task decomposition records what the master agent planned. Routing records which agents were selected and why. Validation records quality gate results. Reporting produces the session summary that becomes a CHANGELOG entry.

Without orchestration, observability captures disconnected fragments: individual agent outputs with no thread connecting them. With orchestration, observability captures the full story: what was requested, how it was decomposed, what each agent produced, what passed validation, and what the aggregate outcome was.

### Layer 6: Team Governance

In a multi-developer team, agent orchestration is what prevents divergence. Without a master agent, each developer's agents follow different sequences, produce different output formats, and apply different levels of rigor. With a shared master agent definition, every developer's session follows the same orchestration pattern. The agents are not just consistent individually — they are consistent in how they coordinate.

The master agent also provides the mechanism for cross-developer conflict resolution described in Layer 6. When two developers' agents make conflicting changes to the same file, the master agent detects the conflict during validation and escalates it through the defined resolution process rather than silently overwriting one developer's work.

---

## Getting Started

If you are adopting agent orchestration for the first time:

1. **Start at Level 1.** Copy the agent definitions from [`agents/`](../agents/) into your project's `.claude/agents/` directory. Use them manually for a week. Learn which agents you invoke most and in what order.
2. **Identify your most common workflow.** For most teams, it is: write code, review code, review security, check quality. That sequence becomes your first chained command (Level 2).
3. **Define input/output contracts.** Before building Level 3, write down what each agent expects to receive and what it must return. The contracts in this document are a starting point. Adapt them to your project.
4. **Add the master agent.** When your contracts are stable and your agents are reliable individually, introduce the [master agent](../agents/master-agent.md) as the coordinator. Start with one workflow (e.g., "new feature") and expand.
5. **Measure.** Track whether orchestrated workflows produce better outcomes than manual invocation. If they do not, the contracts or agent definitions need tuning — not more orchestration.
