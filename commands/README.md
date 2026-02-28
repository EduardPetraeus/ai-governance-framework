# Commands

Slash commands are workflow automation for Claude Code sessions. They handle the procedural parts of governed AI development -- starting sessions with full context, closing them with proper governance updates, checking project status, prioritizing work, and running security checks.

## What slash commands are

A slash command is a markdown file stored in `.claude/commands/` in your project. When you type `/command-name` in Claude Code, the model reads the command file's content and follows the instructions inside it. The markdown file IS the prompt -- there is no separate configuration.

Commands are workflow steps, not domain expertise. They read project files, execute a defined procedure, and produce structured output. They run inside your current session and take 30 seconds to 2 minutes.

## Installation

```bash
# Create the commands directory
mkdir -p .claude/commands

# Copy the commands you want
cp ai-governance-framework/commands/plan-session.md .claude/commands/
cp ai-governance-framework/commands/end-session.md .claude/commands/
cp ai-governance-framework/commands/status.md .claude/commands/
cp ai-governance-framework/commands/prioritize.md .claude/commands/
cp ai-governance-framework/commands/security-review.md .claude/commands/
```

Verify installation by typing `/` in Claude Code -- you should see the command names in the autocomplete list. No other configuration is needed. The commands read your existing project files (`PROJECT_PLAN.md`, `CHANGELOG.md`, `ARCHITECTURE.md`) automatically.

## How invocation works

When you type `/plan-session`, Claude Code reads `.claude/commands/plan-session.md` and sends its content as a user message. The model then follows the instructions in that file. The command file is a prompt template -- it tells the model what to read, what to produce, and what format to use.

Commands can be invoked with additional context:

```
/plan-session
/end-session
/status
/security-review src/connectors/stripe.py
/prioritize "we have 2 hours today"
```

## Agents vs. commands

| | Slash Commands | Agents |
|---|---------------|--------|
| **What** | Workflow steps the current agent follows | Specialized expertise that replaces the agent's persona |
| **Depth** | Quick procedure (30 sec - 2 min) | Deep analysis (5-20 min) |
| **Session** | Within current session | Best in a dedicated session |
| **Input** | Reads project files automatically | You provide specific input (diff, files, context) |
| **Output** | Status reports, governance updates, task lists | Domain-specific analysis with findings |
| **Examples** | `/plan-session`, `/end-session`, `/status` | security-reviewer, code-reviewer, test-writer |

Use commands for process: starting, ending, checking, prioritizing.
Use agents for analysis: reviewing, testing, simplifying, documenting.

## Included commands

| Command | Invocation | Purpose |
|---------|-----------|---------|
| [plan-session](plan-session.md) | `/plan-session` | Start a session with full context, sprint status, and confirmed scope |
| [end-session](end-session.md) | `/end-session` | Close a session with governance updates, CHANGELOG commit, and next-session recommendation |
| [status](status.md) | `/status` | Quick project snapshot: phase progress, session work, blockers, next task |
| [prioritize](prioritize.md) | `/prioritize` | Ranked task list with reasoning: sprint commitments, dependencies, value/effort |
| [security-review](security-review.md) | `/security-review` | In-session security scan of current branch changes |

## Creating new commands

1. Create a markdown file in `.claude/commands/` with the command name (e.g., `deploy-checklist.md`)
2. Write clear, step-by-step instructions that any model (including Haiku) can follow
3. Define the output format explicitly -- show the model what the result should look like
4. Include an example of the expected output
5. Keep each command focused on one workflow step

**Key principle:** Commands should be deterministic. Given the same project state, the same command should produce effectively the same output regardless of which model runs it. This means the instructions must be specific enough that interpretation is minimal.
