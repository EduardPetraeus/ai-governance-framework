# Getting Started

**From zero to your first governed AI session in 15 minutes.**

By the end of this guide you will have: a `CLAUDE.md` constitution that your agent reads before it writes a line of code, a `PROJECT_PLAN.md` that gives the agent tactical orientation, a `CHANGELOG.md` that preserves session history, and one completed governed session with documented state. That is Level 1 of the [maturity model](maturity-model.md).

---

## Prerequisites

- **Claude Code installed** — [claude.ai/code](https://claude.ai/code). The session protocol is designed for Claude Code; the governance concepts apply to any AI coding assistant.
- **A git repository** — any existing project. If starting fresh, `git init` and an initial commit are enough.
- **15 minutes** — realistic, not aspirational.

You do not need CI/CD, specialized agents, or any existing governance files. Level 1 starts from nothing.

---

## Step 1: Copy the Level 1 Files

Level 1 requires three files. Copy them into your project root.

```bash
# Set the path to your cloned framework
FRAMEWORK="path/to/ai-governance-framework"

# Copy the three Level 1 files
cp "$FRAMEWORK/templates/CLAUDE.md"        ./CLAUDE.md
cp "$FRAMEWORK/templates/PROJECT_PLAN.md"  ./PROJECT_PLAN.md
cp "$FRAMEWORK/templates/CHANGELOG.md"     ./CHANGELOG.md
```

If the framework repo is a sibling directory:

```bash
cp ../ai-governance-framework/templates/CLAUDE.md       ./CLAUDE.md
cp ../ai-governance-framework/templates/PROJECT_PLAN.md ./PROJECT_PLAN.md
cp ../ai-governance-framework/templates/CHANGELOG.md    ./CHANGELOG.md
```

**What each file does:**

| File | Role | Who updates it |
|------|------|----------------|
| `CLAUDE.md` | The agent's constitution. Read at every session start. Contains rules, conventions, session protocol, and forbidden actions. | Humans only, via reviewed changes |
| `PROJECT_PLAN.md` | Sprint goals, task breakdown, phase structure, progress tracking. The agent's tactical orientation. | Agent at session end; human at sprint planning |
| `CHANGELOG.md` | Append-only record of what happened in each session. The agent's long-term memory. | Agent at session end |

Commit immediately:

```bash
git add CLAUDE.md PROJECT_PLAN.md CHANGELOG.md
git commit -m "chore: add Level 1 governance files"
```

---

## Step 2: Customize CLAUDE.md

Open `CLAUDE.md` and find the `project_context` section at the top:

```markdown
## project_context

project_name: "YOUR_PROJECT_NAME"
project_type: "YOUR_PROJECT_TYPE"  # e.g., web API, data pipeline, CLI tool
primary_language: "Python"          # or TypeScript, Go, Rust, etc.
owner: "YOUR_NAME_OR_TEAM"
current_phase: "Phase 1 — Foundation"
sprint_goal: "DESCRIBE YOUR CURRENT SPRINT GOAL"
```

Replace the placeholders with your actual project details:

```markdown
## project_context

project_name: "customer-data-pipeline"
project_type: "data pipeline"
primary_language: "Python"
owner: "data-engineering-team"
current_phase: "Phase 1 — Bronze Layer"
sprint_goal: "Build all source connectors and ingest raw data to bronze tables"
```

**What to keep untouched at Level 1:**

Everything under `session_protocol`, `mandatory_task_reporting`, `forbidden`, and `definition_of_done`. These sections define the agent's runtime behavior. They are the core mechanism. Do not edit them until you have completed at least three governed sessions and understand what each rule does.

**What to skip at Level 1:**

Model routing, agent specialization, and security scanning configuration. These belong to Level 2 and above. The template includes them as commented-out sections — leave them for later.

**The rule that matters most:**

```markdown
## session_protocol

on_session_start:
  1. Read PROJECT_PLAN.md, CHANGELOG.md (minimum 2 files)
  2. Present sprint status: current phase, last completed, top 3 suggestions
  3. Confirm scope — NO CODE before scope is confirmed
```

This means the agent will not write a single line of code until it has read your project files and you have confirmed what the session will do. This is law, not suggestion.

Commit your customization:

```bash
git add CLAUDE.md
git commit -m "chore: customize CLAUDE.md project context"
```

---

## Step 3: Run /plan-session

Open your project in Claude Code. The agent reads `CLAUDE.md` automatically from the repository root.

Start your first governed session:

```
/plan-session
```

The agent executes the session start protocol:

1. Reads `PROJECT_PLAN.md` and `CHANGELOG.md`
2. Identifies the current sprint phase and goal
3. Notes that this is session 1 (no prior history)
4. Proposes 2-3 tasks for this session
5. Waits for you to confirm scope before proceeding

**What you will see:**

```
Session start — governance sync complete.

Model: claude-sonnet-4-6
Project: customer-data-pipeline
Phase: Phase 1 — Bronze Layer
Sprint goal: Build all source connectors

Last session: None (first session)

Proposed scope for this session:
  1. Set up project directory structure (src/, tests/, docs/)
  2. Build source connector base class
  3. Write smoke test for connector interface

Confirm to proceed, or adjust scope?
```

If you see output like this, Level 1 is working. The agent has read your governance files and is orienting against your project plan instead of waiting for an ad-hoc instruction.

---

## Step 4: Work

Confirm the proposed scope (or adjust it) and the agent begins executing. After every completed task, you will see a mandatory status report:

```
┌─────────────────────────────────────────────────────┐
│ Task completed: Set up project directory structure   │
├─────────────────────────────────────────────────────┤
│ What changed:                                        │
│ • Created src/, tests/, docs/ directories            │
│ • Added .gitignore with Python/env exclusions        │
│ • Added pyproject.toml with project metadata         │
├─────────────────────────────────────────────────────┤
│ Goal impact:                                         │
│ Phase 1: ██░░░░░░░░ 10% (was 0%)                    │
│ Sprint goal: "All source connectors" — 0/3 done      │
│ Remaining: connector base class, smoke test          │
├─────────────────────────────────────────────────────┤
│ Next: Build connector base class (est. ~20 min)      │
│ Continue, or adjust?                                 │
└─────────────────────────────────────────────────────┘
```

This is the `mandatory_task_reporting` pattern from `CLAUDE.md`. Every task maps to a project goal. The agent reports not just what it did, but why it matters relative to your sprint target.

You do not ask for status. It is pushed automatically after every task. This cannot be suppressed.

---

## Step 5: Run /end-session

When the session is done:

```
/end-session
```

The agent executes the session end protocol:

1. Generates a full session summary (tasks completed, files changed, goal progress)
2. Updates `CHANGELOG.md` with a new session entry
3. Updates `PROJECT_PLAN.md` with completed task checkboxes and progress percentages
4. Proposes a governance commit

**CHANGELOG entry generated automatically:**

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

**Commit message the agent proposes:**

```
docs: update project state after session 001

- CHANGELOG.md: added session 001 summary
- PROJECT_PLAN.md: marked 3 tasks complete, updated Phase 1 progress to 15%
```

Review the updates, then commit:

```bash
git add CHANGELOG.md PROJECT_PLAN.md
git commit -m "docs: update project state after session 001"
```

---

## Step 6: Verify

After committing, verify governance files were updated correctly.

**Check CHANGELOG.md:**

```bash
head -30 CHANGELOG.md
```

You should see a session entry at the top with the correct date, task list, and goal progress.

**Check PROJECT_PLAN.md:**

```bash
grep -A5 "Phase 1" PROJECT_PLAN.md
```

Completed tasks should be marked `[x]`. Progress percentage should match what the agent reported.

**Check git log:**

```bash
git log --oneline -5
```

The most recent commit should be the governance update with the `docs: update project state` prefix.

If all three checks pass, your first governed session is complete. The next session starts by reading these updated files. The agent has accurate context without you explaining anything.

---

## You Are Now at Level 1

What Level 1 gives you:

- **The agent reads before it codes.** No more sessions that open with hallucinated context or ad-hoc guessing about project state.
- **Every session has a documented trace.** `CHANGELOG.md` tells you exactly what happened in session 1, session 7, session 47.
- **Project state is always current.** `PROJECT_PLAN.md` reflects reality, updated automatically at every session end.
- **Context survives session boundaries.** Close Claude Code, return three weeks later, open a new session — the agent reads the files and knows where it left off.
- **Scope is explicit.** The agent confirms what it will do before writing code. No silent scope expansion. No unasked-for refactors.

Level 1 is not a lightweight warmup. The HealthReporting project ran 137 commits at 16x velocity primarily through the discipline installed at Level 1. The higher levels add enforcement and observability on top of a foundation that already works.

---

## The Level 2 Upgrade Path

Level 2 adds structure: architecture documentation, decision records, cross-session memory, specialized agents, and slash commands.

**Five steps to Level 2:**

1. **Add ARCHITECTURE.md** — Describe what has been built (not what is planned). Place it at `docs/ARCHITECTURE.md`. Reference it in `CLAUDE.md` as a file to read at session start. The agent updates it when new components are added.

2. **Write your first ADR** — The next significant architectural decision, document it. Copy the template from [`docs/adr/ADR-000-template.md`](adr/ADR-000-template.md) to `docs/adr/ADR-001-your-decision.md`. This prevents the agent from reopening decisions that were already settled.

3. **Add MEMORY.md** — A running file where the agent captures cross-session context: decisions, patterns, lessons learned. Place it at `docs/MEMORY.md` and reference it in `CLAUDE.md`.

4. **Install slash commands** — Copy the commands from [`commands/`](../commands/) into `.claude/commands/`. Start with `/plan-session`, `/end-session`, `/sprint-status`, and `/security-review`.

5. **Define specialized agents** — Instead of one generalist agent, define a code agent and a review agent with different scopes. See [`agents/`](../agents/) for templates.

**Time estimate:** 2-4 hours spread across your next sprint.

**Further reading:**

- [Maturity Model](maturity-model.md) — all 6 levels with upgrade paths and self-assessment
- [Session Protocol](session-protocol.md) — the full 4-phase lifecycle, including the mandatory_task_reporting spec
- [Architecture](architecture.md) — the 7-layer framework, layer by layer
- [`templates/CLAUDE.md`](../templates/CLAUDE.md) — the full annotated template

The framework scales as far as you need it to. Level 1 is where every successful implementation starts.
