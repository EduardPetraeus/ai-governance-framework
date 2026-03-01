# Agents

Agents are specialized system prompts that transform a Claude Code session into a domain expert. Each file in this directory contains a complete, ready-to-use system prompt for a specific type of work: security review, code review, documentation, testing, or simplification.

## What agents are in Claude Code

An agent is a sub-session with a targeted system prompt. When you invoke an agent, the model stops being a generalist and becomes an expert with:

- A defined role and adversarial or analytical stance
- An explicit scope boundary (what it will and will not do)
- A structured output format (so output is consistent and machine-parseable)
- Domain-specific checklists that prevent gaps in coverage

The result is repeatable, high-quality output for that domain. A security review from the security-reviewer agent is consistently thorough because the system prompt encodes dozens of specific patterns to check. A general session might miss half of them.

## Three ways to use agents

### 1. Copy the system prompt into a new conversation (best results)

Open a new Claude Code session. Copy the complete content of the agent's **System Prompt** section and paste it as your first message. Then provide the input described in the **Input** section.

This is the highest-quality option because the agent's system prompt gets the model's full context window without competing with an existing conversation.

### 2. Reference from CLAUDE.md as a named agent

Add the agent to your CLAUDE.md:

```yaml
agents:
  security_review: agents/security-reviewer.md
  code_review: agents/code-reviewer.md
```

Then in a session, say: "Run the security review agent on the current diff." The model reads the agent file and follows the system prompt within the current session.

This is convenient but slightly less effective than a dedicated session -- the agent's context competes with the session's existing conversation.

### 3. Invoke via slash command

Some agents have corresponding slash commands (e.g., `/security-review` invokes a lightweight version of the security-reviewer agent). Slash commands run inside the current session and are designed for quick checks, not deep analysis.

## Agents vs. slash commands

These are different tools for different purposes:

| | Agents | Slash Commands |
|---|--------|---------------|
| **What they are** | Specialized expertise that replaces the model's persona | Workflow steps the current agent follows |
| **Depth** | Deep, thorough, adversarial | Quick, procedural, surface-level |
| **Session** | Best in a dedicated session | Within the current session |
| **Output** | Domain-specific analysis with structured findings | Structured status or action reports |
| **When to use** | Security review, PR review, test generation | Session start/end, status checks, prioritization |
| **Analogy** | Calling in a specialist | Following a checklist |

**Rule of thumb:** If the task requires expertise and judgment, use an agent. If the task requires reading files and following a procedure, use a command.

## Tier System

Agents are organized into two tiers based on usage frequency and criticality:

- **Core agents** (4): Used every session. These enforce safety, quality, and coordination. Start here.
- **Extended agents** (7): Used on-demand for specific tasks. Add these as your governance maturity grows.

Start with core agents. Add extended agents as your governance maturity grows.

## Included agents

| Agent | Tier | Purpose | When to invoke |
|-------|------|---------|----------------|
| [security-reviewer](security-reviewer.md) | **Core** | Adversarial scan for secrets, PII, injection, insecure defaults | Before every PR merge, after adding integrations |
| [code-reviewer](code-reviewer.md) | **Core** | PR review against CLAUDE.md conventions and ADR compliance | Every PR before human review |
| [master-agent](master-agent.md) | **Core** | Coordinates specialist agents, decomposes tasks, validates outputs, escalates conflicts | Tasks spanning 2+ agents, architecture changes, multi-step features |
| [quality-gate-agent](quality-gate-agent.md) | **Core** | Scores session output (0-100) against output contracts, architecture, coverage, conventions | After every session, before PR merge |
| [documentation-writer](documentation-writer.md) | Extended | Writes and updates documentation to match actual code | After features, after architectural decisions |
| [test-writer](test-writer.md) | Extended | Generates tests targeting AI-specific failure modes | After new features, before merging PRs lacking coverage |
| [code-simplifier](code-simplifier.md) | Extended | Reduces complexity without changing behavior | After multi-file sessions, when code feels over-engineered |
| [drift-detector-agent](drift-detector-agent.md) | Extended | Detects governance drift: convention violations, stale docs, undocumented patterns | Monthly governance review, after maturity level upgrades |
| [red-team-auditor](red-team-auditor.md) | Extended | Adversarial testing of governance mechanisms with simulated violations | Monthly audits, after adding new governance mechanisms |
| [research-agent](research-agent.md) | Extended | Scans external sources for new AI governance insights and best practices | On-demand via `/research`, weekly automated scans |
| [onboarding-agent](onboarding-agent.md) | Extended | Assesses repo state, recommends maturity level, generates configured governance files | First-time framework setup, new repo onboarding |

## How to create a new agent

Follow this structure (every existing agent uses it):

1. **Purpose** -- one paragraph explaining why this agent exists as a specialist rather than relying on the main session's general knowledge.
2. **When to use** -- specific triggers, not vague guidance. "Before every PR merge" is good. "When appropriate" is not.
3. **System prompt** -- the complete, immediately usable prompt. This is the core of the agent. It should be opinionated, specific, and include explicit rules for edge cases.
4. **Input** -- what to provide (diff, file path, directory, context files).
5. **Output** -- the structured format the agent produces.
6. **Example** -- a realistic example showing real input and the complete output. Not a sketch.
7. **Customization** -- what teams typically adjust and how.

### The quality bar

An agent file is not a placeholder. It is a production system prompt. The system prompt section should be detailed enough that copying it into a blank session produces expert-level output on the first try. If the system prompt says "check for security issues" without listing specific patterns, it is not an agent -- it is a wish.

Test your agent by pasting the system prompt into a new session with realistic input. If the output is vague, generic, or misses obvious findings, the system prompt needs more specificity.
