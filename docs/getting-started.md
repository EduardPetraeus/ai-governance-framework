# Getting Started

**From zero to your first governed AI session in 15 minutes.**

This guide walks you through implementing Level 1 of the AI Governance Framework — the foundation that every higher level depends on. By the end, you will have a governed project where your agent reads a constitution before it writes a line of code, updates project state after every session, and never loses context between sittings.

---

## Prerequisites

Before you begin:

- **Claude Code installed** — [claude.ai/code](https://claude.ai/code). The session protocol is designed for Claude Code specifically; the governance concepts apply universally.
- **A git repository** — any existing project works. If you are starting fresh, `git init` and an initial commit are sufficient.
- **15 minutes** — that is a realistic estimate for Level 1. Not a sales claim.

You do not need CI/CD, agents, or any existing governance files. Level 1 starts from nothing.

---

## Step 1: Copy the Template Files

Level 1 requires three files. Copy them into your project root now.

```bash
# From your project directory
FRAMEWORK_DIR="/path/to/ai-governance-framework"

cp "$FRAMEWORK_DIR/templates/CLAUDE.md.template"        ./CLAUDE.md
cp "$FRAMEWORK_DIR/templates/PROJECT_PLAN.md.template"  ./PROJECT_PLAN.md
cp "$FRAMEWORK_DIR/templates/CHANGELOG.md.template"     ./CHANGELOG.md
```

If you have cloned this repository, the paths are relative:

```bash
# If ai-governance-framework is a sibling of your project
cp ../ai-governance-framework/templates/CLAUDE.md.template       ./CLAUDE.md
cp ../ai-governance-framework/templates/PROJECT_PLAN.md.template ./PROJECT_PLAN.md
cp ../ai-governance-framework/templates/CHANGELOG.md.template    ./CHANGELOG.md
```

**What these files are:**

| File | Purpose | Updated by |
|------|---------|------------|
| `CLAUDE.md` | The agent's constitution. Read at every session start. Contains rules, conventions, and the session protocol. | Humans only, via PR review |
| `PROJECT_PLAN.md` | Sprint goals, task tracking, phase structure. The agent's tactical orientation file. | Agent at session end; human at sprint planning |
| `CHANGELOG.md` | Append-only log of what happened in each session. The agent's long-term memory. | Agent at session end |

Commit them immediately:

```bash
git add CLAUDE.md PROJECT_PLAN.md CHANGELOG.md
git commit -m "chore: add Level 1 governance files"
```

---

## Step 2: Customize CLAUDE.md

The template ships with a `project_context` section at the top. This is the only section you must customize right now.

Open `CLAUDE.md` and find the section that looks like this:

```markdown
## project_context

project_name: "YOUR_PROJECT_NAME"
project_type: "YOUR_PROJECT_TYPE"  # e.g. web API, data pipeline, CLI tool
primary_language: "Python"          # or TypeScript, Go, etc.
owner: "YOUR_NAME_OR_TEAM"
current_phase: "Phase 1 — Foundation"
sprint_goal: "DESCRIBE YOUR CURRENT SPRINT GOAL"
```

Replace the placeholders with your actual project details. For example:

```markdown
## project_context

project_name: "customer-data-pipeline"
project_type: "data pipeline"
primary_language: "Python"
owner: "data-engineering-team"
current_phase: "Phase 1 — Bronze Layer"
sprint_goal: "Build all source connectors and ingest raw data to bronze tables"
```

**What to keep untouched:**

Everything under `## session_protocol`, `## mandatory_task_reporting`, `## forbidden`, and `## definition_of_done`. These sections define the agent's behavior at runtime. They are the core of what you are implementing. Do not edit them until you have completed at least three governed sessions and understand what each rule does.

**One rule that is critical to understand:**

```markdown
## session_protocol

on_session_start:
  1. Read PROJECT_PLAN.md, CHANGELOG.md (minimum 2 files)
  2. Present sprint status: current phase, last completed, top 3 suggestions
  3. Confirm scope — NO CODE before scope is confirmed
```

This rule means the agent will not write a single line of code until it has read your project files and confirmed what it is about to do. This is not optional behavior — it is specified as law in the constitution.

Commit your customization:

```bash
git add CLAUDE.md
git commit -m "chore: customize CLAUDE.md for project context"
```

---

## Step 3: Run Your First Session

Open your project in Claude Code. The agent reads `CLAUDE.md` automatically from the repository root.

Start the session by running the session start command:

```
/plan-session
```

The agent will execute the session start protocol:

1. Read `PROJECT_PLAN.md` and `CHANGELOG.md`
2. Identify the current sprint phase and goal
3. List the last completed tasks (or note this is session 1)
4. Present its top 3 proposed tasks for this session
5. Ask you to confirm scope before proceeding

**Example output from a first session:**

```
Session start — governance sync complete.

Model: claude-sonnet-4-6
Project: customer-data-pipeline
Phase: Phase 1 — Bronze Layer
Sprint goal: Build all source connectors

Last session: None (session 1)

Proposed scope for this session:
  1. Set up project structure and directory layout
  2. Build the first source connector skeleton
  3. Write smoke test for connector interface

Confirm to proceed, or adjust scope?
```

If you see output like this, Level 1 is working. The agent has read your governance files and is orienting against your project plan rather than waiting for an ad-hoc instruction.

---

## Step 4: Do Some Work

Confirm the proposed scope (or adjust it), and the agent begins working. During the session, after every completed task, you will see a status report pushed automatically:

```
┌─────────────────────────────────────────────────────┐
│ Task completed: Set up project directory structure   │
├─────────────────────────────────────────────────────┤
│ What changed:                                        │
│ • Created src/, tests/, docs/ directory structure   │
│ • Added .gitignore with Python/env exclusions        │
│ • Added pyproject.toml with project metadata        │
├─────────────────────────────────────────────────────┤
│ Goal impact:                                         │
│ Phase 1: ██░░░░░░░░ 10% (was 0%)                   │
│ Sprint goal: "All source connectors" — 0/3 done     │
│ Remaining: connector skeleton, smoke test           │
├─────────────────────────────────────────────────────┤
│ Next: Build connector skeleton (est. ~20 min)        │
│ Continue, or adjust?                                 │
└─────────────────────────────────────────────────────┘
```

This is the `mandatory_task_reporting` pattern from `CLAUDE.md`. Every task maps to a project goal. The agent does not just tell you what it did — it tells you why it matters relative to your sprint target.

You do not need to ask for status. It is pushed automatically after every task.

---

## Step 5: Complete the Session

When you are ready to end the session, run:

```
/end-session
```

The agent executes the session end protocol:

1. Generates a full session summary (all tasks completed, files changed, goal progress)
2. Auto-updates `CHANGELOG.md` with a new session entry
3. Auto-updates `PROJECT_PLAN.md` with completed task checkboxes and updated progress
4. Proposes a commit with the standard governance commit message

**Example CHANGELOG entry generated automatically:**

```markdown
## 2026-02-28 — Session 001: Project Foundation

**Phase:** Phase 1 — Bronze Layer
**Agent:** Claude Code (claude-sonnet-4-6)
**Duration:** ~45 minutes
**Tasks completed:** 3/3

### What was done
- Created project directory structure (src/, tests/, docs/)
- Built source connector base class in src/connectors/base.py
- Added smoke test in tests/test_connector_interface.py

### What was NOT done
- Individual connector implementations (next session)

### Goal progress
Phase 1: 15% complete (was 0%)
```

The agent will propose this commit message:

```
docs: update project state after session 001

- CHANGELOG.md: added session 001 summary
- PROJECT_PLAN.md: marked 3 tasks complete, updated Phase 1 progress to 15%
```

Review it, then commit:

```bash
git add CHANGELOG.md PROJECT_PLAN.md
git commit -m "docs: update project state after session 001"
```

---

## Step 6: Verify

After the commit, verify that the governance files were updated correctly.

**Check CHANGELOG.md:**
```bash
head -40 CHANGELOG.md
```
You should see a new session entry at the top with the correct date, tasks, and goal progress.

**Check PROJECT_PLAN.md:**
```bash
grep -A5 "Phase 1" PROJECT_PLAN.md
```
You should see completed tasks marked with `[x]` and a progress percentage that matches what the agent reported.

**Check git log:**
```bash
git log --oneline -5
```
The most recent commit should be the governance update with the `docs: update project state` prefix.

If all three checks pass, your first governed session is complete. The next session will start by reading these updated files — giving the agent accurate context about where the project stands without you having to explain it.

---

## You Are Now at Level 1

Here is what Level 1 gives you:

- **The agent reads before it codes.** No more sessions that start with "what should we work on?" answered by hallucinated context.
- **Every session has a documented trace.** `CHANGELOG.md` tells you exactly what happened in session 1, session 2, session 47.
- **Project state is always current.** `PROJECT_PLAN.md` reflects reality, not aspirations from two weeks ago.
- **The agent cannot lose context.** Even if you close Claude Code, come back three weeks later, and open a new session — the agent reads the files and knows where it left off.

Level 1 is not a lightweight warmup. The HealthReporting project ran 137 commits at 16x velocity primarily through the discipline installed at Level 1. The higher levels add enforcement and observability on top of a foundation that already works.

---

## What's Next: The Level 2 Path

Level 2 adds structure: Architecture Decision Records, a dedicated memory file, specialized agents, and slash commands that automate your most common workflows.

**Steps to reach Level 2:**

1. **Add MEMORY.md** — a running file where the agent captures decisions, patterns, and lessons learned across sessions. Place it at `docs/MEMORY.md` and reference it in `CLAUDE.md` as a file to read at session start.

2. **Write your first ADR** — the next significant architectural decision you make, document it. Copy the template from [`templates/adr-template.md`](../templates/adr-template.md) and place it in `docs/adr/ADR-001-your-decision.md`. This prevents the agent from re-opening closed discussions in future sessions.

3. **Add ARCHITECTURE.md** — a living document describing what has been built, the major components, and how they fit together. The agent updates it at session end when new components are added.

4. **Install slash commands** — copy the commands from [`commands/`](../commands/) into your project's `.claude/commands/` directory. The most valuable for Level 2 are `/plan-session`, `/end-session`, `/sprint-status`, and `/security-review`.

5. **Define specialized agents** — instead of one generalist agent doing everything, define a code agent and a review agent with different CLAUDE.md scopes. See [`agents/`](../agents/) for examples.

**Time estimate for Level 2:** 2–4 hours, spread across your next sprint.

**Where to read more:**

- [Maturity Model](maturity-model.md) — detailed description of all 6 levels, what's in each, and how to upgrade
- [Session Protocol](session-protocol.md) — the full 4-phase lifecycle explained, including the mandatory_task_reporting spec
- [Architecture](architecture.md) — the 7-layer framework explained in depth, layer by layer
- [`templates/CLAUDE.md.template`](../templates/CLAUDE.md.template) — the full annotated template

The framework scales as far as you need it to. Level 1 is where every successful implementation starts.
