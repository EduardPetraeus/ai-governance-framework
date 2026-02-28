# Templates

This directory contains the core governance templates for the AI Governance Framework. Copy these files into your project and customize them according to your maturity level.

## Maturity Levels

Your maturity level determines which files to copy. Start at Level 1 and add files as your project grows. Do not skip levels — each level depends on the previous one being functional.

### Quick-start table

| Level | Name | Files to copy | Time to set up | Who it's for |
|-------|------|---------------|----------------|--------------|
| **1** | Foundation | `CLAUDE.md`, `PROJECT_PLAN.md`, `CHANGELOG.md` | 15 minutes | Solo dev, new project |
| **2** | Memory | Level 1 + `MEMORY.md`, `DECISIONS.md` | 30 minutes | Any project past the prototype phase |
| **3** | Tracking | Level 2 + `SPRINT_LOG.md`, `COST_LOG.md` | 45 minutes | Teams or cost-conscious solo devs |
| **4** | Full | Level 3 + `ARCHITECTURE.md` + CI/CD + agents | 2 hours | Teams shipping to production |

---

## Level 1: Foundation (15 minutes)

**Files to copy:**

```
CLAUDE.md          → repo root (required — agents read this first)
PROJECT_PLAN.md    → repo root (required — session protocol reads this)
CHANGELOG.md       → repo root (required — session protocol writes this)
```

**What you get at Level 1:**
- Agents follow consistent naming conventions
- Session start/end protocol prevents context loss
- Security rules prevent accidental secret commits
- Changelog tracks what changed across sessions

**Minimum viable setup:**

```bash
cp templates/CLAUDE.md .
cp templates/PROJECT_PLAN.md .
cp templates/CHANGELOG.md .
```

Then open `CLAUDE.md` and fill in the `project_context` section (5 minutes). That's it.

---

## Level 2: Memory (30 minutes)

**Files to copy (in addition to Level 1):**

```
MEMORY.md          → repo root (cross-session knowledge persistence)
DECISIONS.md       → repo root (decision log, prevents decision loops)
```

**What you get at Level 2:**
- Agents remember confirmed patterns and anti-patterns
- Decisions are logged so they're not re-litigated
- Open questions are tracked (not lost in chat history)
- Team preferences are documented for consistent agent behavior

**When to move to Level 2:**
- When you've had 5+ sessions on the same project
- When you notice agents repeating mistakes from previous sessions
- When you've made architectural decisions that shouldn't be reversed

---

## Level 3: Tracking (45 minutes)

**Files to copy (in addition to Level 2):**

```
SPRINT_LOG.md      → repo root (sprint velocity and retrospectives)
COST_LOG.md        → repo root (AI cost per session)
```

**What you get at Level 3:**
- Sprint velocity tracking (tasks per session over time)
- AI cost visibility (know what each session costs)
- Retrospective data to improve the process
- Budget alerts before costs get out of control

**When to move to Level 3:**
- When you want to measure velocity improvement
- When AI costs start to matter (team usage, frequent sessions)
- When you need to justify AI spend to stakeholders

---

## Level 4: Full (2 hours)

**Files to copy (in addition to Level 3):**

```
ARCHITECTURE.md    → repo root
```

**Plus:** Set up the CI/CD workflows in `../ci-cd/` and copy agents from `../agents/` and commands from `../commands/`.

**What you get at Level 4:**
- Architecture is documented and enforced
- Every PR is reviewed by an AI agent before human review
- Pre-commit hooks catch secrets and naming violations locally
- Full agent library for specialized tasks

**When to move to Level 4:**
- When you have multiple contributors (human or AI agents on multiple branches)
- When you're shipping to production
- When governance needs to be enforced, not just encouraged

---

## How to customize CLAUDE.md

### What to change

**The `project_context` section** — Replace all placeholder values with your actual project details. This is the only section where everything must be replaced.

```yaml
project_context:
  project_name: "HealthReporting"          # Your actual project name
  description: "Personal health data pipeline from wearables to dashboard"
  stack: "Python, DuckDB, Databricks, dbt"
  owner: "Platform Team"
  repository: "https://github.com/org/health-reporting"
```

**The `conventions` section** — Add your domain-specific naming rules. For example, if you use a data warehouse, add layer prefixes (`stg_`, `dim_`, `fct_`). If you use a specific API naming style, document it here.

**The `model_routing` section** — Adjust the model names if you use a different AI provider (OpenAI, Gemini, local models). The task categories are universal; only the model names need changing.

### What NOT to change

**`mandatory_session_protocol`** — This is the core governance mechanism. Changing the session start/end protocol defeats the purpose of the framework. If you need to adjust verbosity, do it in `MEMORY.md` as a team preference.

**`security_protocol`** — The never-commit list and scan triggers are non-negotiable. You can add to them but not remove items. If a rule is too strict for your use case, file an issue on the framework repository rather than weakening your local copy.

**`mandatory_task_reporting`** — The reason this exists is to prevent agents from silently doing large amounts of work without accountability. If you disable it, you lose the primary protection against scope creep.

**`verification`** — Agents skipping verification is the root cause of most "but it worked in my head" bugs. Keep this section intact.

### What is marked OPTIONAL

The `model_routing` section is marked `# OPTIONAL`. At Level 1, remove it entirely — it adds complexity without value for a single developer using one model. Implement it at Level 2 or 3 once you're paying attention to which tasks need deeper reasoning.

---

## File descriptions

| File | Purpose | Updated |
|------|---------|---------|
| `CLAUDE.md` | Agent constitution — rules agents must follow | Rarely (monthly review) |
| `PROJECT_PLAN.md` | Sprint planning and task tracking | Every session |
| `CHANGELOG.md` | Session-level history of what changed | Every session (auto) |
| `MEMORY.md` | Cross-session knowledge that agents accumulate | Ongoing |
| `DECISIONS.md` | Permanent log of decisions made and why | When decisions are made |
| `SPRINT_LOG.md` | Sprint velocity and retrospectives | Per sprint |
| `COST_LOG.md` | AI cost per session and model | Per session |
| `ARCHITECTURE.md` | System design and technology decisions | When architecture changes |
