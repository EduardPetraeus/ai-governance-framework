# Commands

Slash commands are workflow automation tools for Claude Code. They handle the procedural
parts of AI-assisted development: starting sessions correctly, closing them with proper
governance updates, checking status, and running reviews.

## What slash commands are

Slash commands are markdown files stored in `.claude/commands/` in your project. When you
type `/command-name` in Claude Code, the model reads the command's markdown file and
executes the instructions inside it. The markdown file is the prompt.

Commands differ from agents in that they are workflow steps within a session, not
specialized expertise. A command reads project files, does a specific procedure,
and produces structured output. An agent is a deep domain expert you invoke for
a specific type of analysis.

## How to install

1. Create the `.claude/commands/` directory in your project root:
   ```bash
   mkdir -p .claude/commands
   ```

2. Copy the command files you want:
   ```bash
   cp ai-governance-framework/commands/plan-session.md .claude/commands/
   cp ai-governance-framework/commands/end-session.md .claude/commands/
   cp ai-governance-framework/commands/status.md .claude/commands/
   cp ai-governance-framework/commands/prioritize.md .claude/commands/
   cp ai-governance-framework/commands/security-review.md .claude/commands/
   ```

3. Verify they appear in Claude Code by typing `/` — you should see the command names.

No other configuration is required. The commands read your existing project files
(`PROJECT_PLAN.md`, `CHANGELOG.md`, `ARCHITECTURE.md`) automatically.

## How to invoke

Type the command name in any Claude Code message:

```
/plan-session
/end-session
/status
/prioritize
/security-review
```

Commands can also be invoked with additional context:

```
/end-session session 042
/security-review src/connectors/stripe.py
```

## Agents vs. commands

| | Slash Commands | Agents |
|-|---------------|--------|
| **What they do** | Workflow automation | Domain expertise |
| **Session** | Within current session | Usually a dedicated session |
| **Input** | Reads project files automatically | You provide specific input |
| **Output** | Structured status/action reports | Domain-specific analysis |
| **Examples** | /plan-session, /end-session, /status | security-reviewer, code-reviewer |

Use commands for: starting sessions, ending sessions, checking status, prioritizing work.
Use agents for: security review, PR review, documentation, test generation.

## Included commands

| Command | Usage | Purpose |
|---------|-------|---------|
| [plan-session.md](plan-session.md) | `/plan-session` | Structure session start, confirm scope before code |
| [end-session.md](end-session.md) | `/end-session` | Close session with governance updates and commit |
| [status.md](status.md) | `/status` | Quick project state at any point in a session |
| [prioritize.md](prioritize.md) | `/prioritize` | Rank backlog tasks by sprint commitment and value |
| [security-review.md](security-review.md) | `/security-review` | Run security checklist on current branch changes |

## Customizing commands

Each command file is a markdown prompt. You can edit them to match your project's conventions.
Common customizations:

- **Add project-specific files:** If your project has additional context files (a CONTEXT.md,
  a RUNBOOK.md), add them to the "Read" steps in plan-session.md and end-session.md.

- **Adjust output format:** If you prefer a different status format (table vs. list, different
  emoji conventions), edit the output format section of each command.

- **Add project-specific checks:** If your project has specific gates (e.g., "always check
  that migration files are present if models changed"), add them to end-session.md.
