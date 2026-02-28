# Small Team Example

This configuration is for 3-5 developers working on a shared codebase. It adds the
governance mechanisms that matter when multiple people (and multiple AI agents) are
touching the same code.

## What's added vs. solo developer

### Full session protocol with mid-session checkpoints

The solo config has start/end only. The team config adds checkpoints during the session:
after every task, after every third task, and scope confirmation before any code.

**Why this matters for teams:** In a solo setup, you always know what the agent has done
because you were there. On a team, a colleague might review a PR where an agent did 40
things in one session. Without mid-session checkpoints, those 40 things happen without
explicit approval. With them, each task was explicitly approved before the next started.

### Governance sync (drift detection)

At session start, the agent compares intended work against the sprint plan and flags drift:
"We're working outside the current sprint scope. This was planned for Phase 3."

**Why this matters for teams:** Individual developers make good local decisions that create
bad global outcomes. One developer's "small improvement" becomes three hours of unplanned
scope that pushes the sprint. Drift detection makes scope creep visible before it compounds.

### Model routing (5 task types)

Teams spend enough on AI sessions to care about routing. This config defines 5 routing rules:
opus for architecture and security, sonnet for code and docs, haiku for simple edits.

**Why this matters for teams:** If 4 developers each use opus for everything, you're spending
$0.40-$1.00 per session on tasks that cost $0.01 on haiku. At 50 sessions/week, that's $1,000+/month
in unnecessary spend. Model routing pays for itself immediately.

### PR workflow requirements

The solo config has no PR rules. The team config adds:
- No direct commits to main
- Every PR must update CHANGELOG.md (enforced by CI governance check)
- CLAUDE.md changes require a second reviewer

**Why this matters for teams:** Without PR workflow rules in CLAUDE.md, some agents will commit
directly to main (it's faster). The PR requirement in the constitution means every agent knows
the rule, not just the humans.

### Agents reference

The team config does not force agents on you, but it notes which ones the team uses. This
matters because: when a PR comes in for review, the team should be using the code-reviewer
agent before requesting human review. Documenting this in CLAUDE.md means agents know to
suggest it.

## What's still left out

### Full CI/CD

governance-check.yml and ai-pr-review.yml are available in `../../ci-cd/` but not required
at this level. Add them when you want enforcement rather than convention.

**When to add:** When someone has merged a PR without updating CHANGELOG.md and it caused
a problem. (This will happen. Then you'll want the CI gate.)

### Compliance sections

EU AI Act, GDPR audit requirements, audit trails — these are for regulated industries or
large organizations. Add the enterprise CLAUDE.md sections when you have a compliance officer
asking about AI governance.

### Definition of done

The full definition of done (mandatory checklist before marking any task complete) is in
the enterprise config. For small teams, this is usually overkill — you know each other and
can have the "is this actually done?" conversation directly.

## Time to set up: 30 minutes

1. Copy files:
   ```bash
   cp examples/small-team/CLAUDE.md .
   cp templates/PROJECT_PLAN.md .
   cp templates/CHANGELOG.md .
   cp templates/MEMORY.md .
   cp templates/DECISIONS.md .
   cp templates/ARCHITECTURE.md .
   ```

2. Edit `CLAUDE.md` — fill in project details. (5 minutes)

3. Edit `PROJECT_PLAN.md` — add your actual phases and tasks. (10 minutes)

4. Edit `ARCHITECTURE.md` — fill in your actual architecture. Even a rough diagram is better
   than none. (10 minutes)

5. Install the slash commands:
   ```bash
   mkdir -p .claude/commands
   cp ../../commands/plan-session.md .claude/commands/
   cp ../../commands/end-session.md .claude/commands/
   cp ../../commands/status.md .claude/commands/
   ```

6. Set up the pre-commit hooks if you want local enforcement:
   ```bash
   cp ../../ci-cd/pre-commit/.pre-commit-config.yaml .
   pip install pre-commit
   pre-commit install
   ```

That's 30 minutes and you have a governed, team-ready AI development setup.

## How to move to Enterprise

When you hit compliance requirements or scale beyond 5 developers, copy
`examples/enterprise/CLAUDE.md` and update your CLAUDE.md with the additional sections:
compliance, full model routing, definition of done, escalation model, and change control.
Then set up all three CI/CD components.
