# Agents

This directory contains specialized agent definitions for the AI Governance Framework.
Each agent is a focused system prompt that turns a Claude Code session into a domain expert
for a specific task type.

## What agents are

Agents in this framework are Claude Code sub-agents: markdown files containing a detailed
system prompt that defines a specific role, expertise, and output format. When you invoke
an agent, you are giving the model a specialized context that makes it significantly more
effective for that type of work than a generic session.

An agent definition specifies:
- What the agent is expert at
- What it will and will not do
- What format its output takes
- How to use it correctly

## Agents vs. slash commands

| | Agents | Slash commands |
|-|--------|---------------|
| **What they are** | Specialized expertise | Workflow steps |
| **How to use** | Copy system prompt, start new session | Type /command-name in current session |
| **Best for** | Domain-specific work (security, code review) | Process automation (session start/end, status) |
| **Session** | Usually a dedicated session | Within the current session |
| **Example** | "Review this PR for security issues" | "/end-session" to close and commit |

Use agents when a task requires deep domain knowledge and benefits from focused context.
Use slash commands for workflow automation within a session.

## How to use agents

### Option 1: Paste as system prompt (recommended)

1. Open a new Claude Code session
2. Copy the contents of the agent's `## System Prompt` section
3. Paste it as your first message, or set it as the system prompt if your client supports it
4. Then provide the input described in the agent's `## Input` section

### Option 2: Reference from main session

In an active session, you can say:
"Act as the security reviewer agent defined in agents/security-reviewer.md. Here is the input: [input]"

This works but is less effective than a dedicated session because the agent's context competes
with the existing session context.

### Option 3: Automated via CI/CD

The CI/CD workflows in `../ci-cd/` invoke agents automatically (the AI PR review workflow
uses the code-reviewer system prompt). See `../ci-cd/README.md` for setup.

## How to create new agents

1. Copy any existing agent file as a starting point
2. Define: purpose, when to use, system prompt, input format, output format
3. Write the system prompt to be opinionated and specific — vague agents produce vague results
4. Include an example showing real input and the expected output format
5. Document what teams typically customize

**Key principle:** An agent should refuse to do things outside its scope. A security reviewer
that also writes features is not a security reviewer — it's just another general session.
Tight scope = consistent, trustworthy output.

## Included agents

| Agent | Purpose | When to use |
|-------|---------|-------------|
| [security-reviewer.md](security-reviewer.md) | Scans code for secrets, PII, vulnerabilities | Before every PR merge |
| [code-reviewer.md](code-reviewer.md) | Reviews PRs against conventions and ADRs | Every PR before human review |
| [documentation-writer.md](documentation-writer.md) | Writes and updates docs to match code | After features, architectural decisions |
| [test-writer.md](test-writer.md) | Generates tests for AI-generated code | After new features, before PR merge |
| [code-simplifier.md](code-simplifier.md) | Reduces complexity without changing behavior | After multi-session refactoring |
