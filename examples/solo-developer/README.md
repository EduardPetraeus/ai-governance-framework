# Solo Developer Configuration

The minimal governance setup for a single developer. 10 minutes to set up. Near-zero ongoing overhead. Solves the three problems that hurt solo developers most.

## The Solo Problem

Working alone with AI agents creates three specific failure modes that governance prevents:

**1. Lost context between sessions.** Without a session protocol and CHANGELOG.md, every session starts from zero. The agent does not know what you built yesterday, which approaches you already tried and rejected, or which decisions are settled. You spend the first 10 minutes of every session re-explaining your project. Over a month, that is hours of wasted time repeating yourself.

**2. Architectural drift with no second pair of eyes.** When you are the only reviewer, bad patterns compound silently. An agent introduces a second way to handle errors. Next session, a different pattern for configuration. Six weeks later, you have three error-handling strategies, two config approaches, and a codebase that fights itself. The session protocol forces the agent to read the project plan and existing patterns before writing new code.

**3. Security accidents with no reviewer.** An agent hardcodes an API key "temporarily." It gets committed. No reviewer catches it. It gets pushed. The key is now in your git history permanently. The never-commit list in CLAUDE.md makes the agent check every file before moving on. It is cheaper than rotating credentials.

## What Each Section Provides

| Section | What it prevents | Concrete benefit |
|---|---|---|
| `project_context` | Agent does not know what you are building | Agent understands the project from the first message |
| `conventions` | Inconsistent naming, commit messages, branch structure | Every file, branch, and commit follows the same pattern |
| `session_protocol` | Blank-slate sessions, forgotten progress | Each session starts with context and ends with documentation |
| `security` | Committed secrets, leaked PII | Agent self-checks every file against the never-commit list |
| `verification` | "It should work" without actually running it | Agent runs the code before claiming a task is complete |

## What Is Left Out and When to Add It

### Model routing
**What it does:** Routes different task types to different AI models (opus for architecture, sonnet for code, haiku for simple reads) to optimize cost and quality.

**When to add it:** When your monthly AI spend exceeds $50. Below that threshold, the mental overhead of choosing models costs more than the money you save. The moment you notice your bill and think "that is a lot," add model routing.

### Governance sync (drift detection)
**What it does:** At session start, compares your planned work against the project plan and flags scope drift before you start coding.

**When to add it:** When you are working on the project more than 3 sessions per week. At that frequency, it becomes easy to lose track of the plan and spend sessions on tangents. Below 3 sessions/week, you naturally remember what you were doing.

### Mandatory task reporting
**What it does:** After every completed task, the agent presents a structured status block showing files changed, goal impact, session progress, and next steps.

**When to add it:** When you have lost track of a session mid-way through. The first time you reach the end of a session and cannot remember what you did in the first half, add task reporting. It forces a checkpoint that prevents the agent from silently drifting.

### CI/CD enforcement
**What it does:** Pre-commit hooks and GitHub Actions that enforce conventions automatically — commit message format, CHANGELOG updates, security scans.

**When to add it:** When you have more than 100 commits, or when you add a collaborator. At 100+ commits, manual convention enforcement starts slipping. With a second person, you need automated enforcement because verbal agreements do not scale.

## Setup: 10 Minutes

```bash
# 1. Copy the three core files to your project root
cp examples/solo-developer/CLAUDE.md .
cp templates/PROJECT_PLAN.md .
cp templates/CHANGELOG.md .

# 2. Edit CLAUDE.md — fill in your project details (2 minutes)
#    Replace: project_name, description, stack, owner

# 3. Edit PROJECT_PLAN.md — replace example phases with your actual tasks (5 minutes)
#    Even 3 tasks per phase is enough to start

# 4. CHANGELOG.md needs no editing — the first session entry is added
#    automatically when you run /end-session

# 5. Add .session_log to .gitignore
echo ".session_log" >> .gitignore

# 6. Start your first governed session
#    Say: "Read CLAUDE.md and PROJECT_PLAN.md and tell me what we should work on."
```

That is it. You now have cross-session memory, consistent conventions, and security guardrails.

## Moving to Small Team (Level 2)

When you add a second developer, or when you are working on the project frequently enough that decisions start getting lost, add the team governance sections:

1. Copy `examples/small-team/CLAUDE.md` and merge the additional sections into yours
2. Add the template files: `MEMORY.md`, `DECISIONS.md`, `ARCHITECTURE.md`
3. Enable the `governance_sync` and `model_routing` sections
4. Set up branch protection on main

The transition takes 30 minutes. Everything you have already set up carries forward unchanged.
