# Solo Developer Example

This is the minimal governance setup for a single developer working on a personal or
small project. It takes 10 minutes to set up and adds almost zero overhead to your workflow.

## Who this is for

- One developer (you)
- Personal project, side project, or early-stage startup
- You want to use AI agents without losing track of what's been built
- Speed matters more than process right now

## What's included

### CLAUDE.md (40 lines)

The core constitution. Even at this minimal level, it prevents the most common problem:
agents that have no idea what happened in previous sessions and start re-implementing
things you already built.

**Why even solo developers need this:**
Without CLAUDE.md and CHANGELOG.md, every session starts blank. The agent has no context
from yesterday's work. It may suggest approaches you already tried and rejected. It will
not know which decisions are settled.

With them, each session starts with: "Here's what we built, here's where we left off,
here's what I recommend we do today." That alone is worth the 10 minutes of setup.

### PROJECT_PLAN.md

Where you track what needs to be built. Agents read this at session start and use it
to recommend the next task. Without it, agents ask "what do you want to work on?" and
you lose time reconstructing your own priorities.

### CHANGELOG.md

Session-level history. Every session adds one entry: what was done, what decisions were made,
what was discovered. This is the agent's cross-session memory. Also useful for you: two weeks
from now, you'll want to know why you made a certain decision.

## What's deliberately left out

### Model routing

At this level, you probably use one model for everything. Model routing adds cognitive
overhead (which model for which task?) that is only worth it when you're managing costs
across a team or doing enough sessions per week to notice the price difference.

**When to add it:** When you're running 5+ sessions per week or when a single session
costs more than $0.50.

### Agents

Specialized agents (security reviewer, code reviewer, test writer) are valuable but add
setup and context-switching overhead. For solo work, you can invoke the security reviewer
ad hoc when you're about to merge something sensitive.

**When to add it:** When you're shipping to production or onboarding a second developer.

### CI/CD enforcement

Pre-commit hooks and GitHub Actions add friction to the commit/PR flow. For solo work on
a non-production project, that friction costs more than it saves.

**When to add it:** When you have a second person who needs to follow the same rules,
or when you're building something that touches real user data.

### Compliance sections

EU AI Act, audit trails, change control for CLAUDE.md — these are enterprise concerns.
Skip them until you have a compliance requirement.

## Time to set up: 10 minutes

1. Copy the three files:
   ```bash
   cp examples/solo-developer/CLAUDE.md .
   cp templates/PROJECT_PLAN.md .
   cp templates/CHANGELOG.md .
   ```

2. Edit `CLAUDE.md` — fill in `project_name`, `description`, `stack`, `owner`. (2 minutes)

3. Edit `PROJECT_PLAN.md` — replace the example phases with your actual project phases.
   Even 3 tasks per phase is enough to start. (5 minutes)

4. Leave `CHANGELOG.md` as-is — the first session entry will be added automatically when
   you run /end-session.

5. In your first Claude Code session, type `/plan-session` (if you've installed the commands)
   or just say "read CLAUDE.md and PROJECT_PLAN.md and tell me what we should work on today."

That's it. You now have a governed AI development setup.

## How to move to Level 2 (Small Team)

When you add a second developer, or when the project has been running for a few months and
you're losing track of decisions, copy `templates/MEMORY.md` and `templates/DECISIONS.md`
to your project root. Then update `CLAUDE.md` using `examples/small-team/CLAUDE.md` as
the reference — add the governance sync section and model routing.
