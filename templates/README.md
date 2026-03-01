# Templates

Copy these files into your project and customize them. Each file is a governance building block. Your maturity level determines which ones you need.

---

## Maturity-Level Pickup Guide

Start at Level 1. Add files as your project grows. Do not skip levels -- each level depends on the previous one being functional.

| Level | Name | Files to Copy | Setup Time | Who It Is For |
|-------|------|---------------|------------|---------------|
| **1** | Foundation | `CLAUDE.md`, `PROJECT_PLAN.md`, `CHANGELOG.md` | 10 minutes | Solo dev, any new project |
| **2** | Memory | Level 1 + `MEMORY.md`, `DECISIONS.md`, `ARCHITECTURE.md` | 30 minutes | Any project past the prototype phase |
| **3** | Tracking | Level 2 + `SPRINT_LOG.md`, `COST_LOG.md`, `AGENT_REGISTRY.md` | 45 minutes | Teams, or solo devs tracking velocity and cost |
| **4** | Enforced | Level 3 + CI/CD workflows + pre-commit hooks + agents | 2 hours | Teams shipping to production |

---

## Level 1: Foundation (10 Minutes)

**Files to copy:**

```
templates/CLAUDE.md        -> repo root/CLAUDE.md
templates/PROJECT_PLAN.md  -> repo root/PROJECT_PLAN.md
templates/CHANGELOG.md     -> repo root/CHANGELOG.md
```

**What you get immediately:**
- Agents follow consistent naming conventions across sessions
- Session start/end protocol prevents context loss
- Security rules prevent accidental secret commits
- Changelog tracks what changed and why, session by session

**The 10-minute setup:**

```bash
# Copy the three files
cp templates/CLAUDE.md .
cp templates/PROJECT_PLAN.md .
cp templates/CHANGELOG.md .

# Open CLAUDE.md and fill in the project_context section (5 minutes)
# Open PROJECT_PLAN.md and replace Phase 1 tasks with your actual tasks (5 minutes)
# That's it. Start your first governed session.
```

Open `CLAUDE.md` and search for `# CUSTOMIZE:` markers. The `project_context` section is the only part that requires replacement before your first session. Everything else works with default values.

---

## Level 2: Memory (30 Minutes)

**Add these files on top of Level 1:**

```
templates/MEMORY.md        -> repo root/MEMORY.md
templates/DECISIONS.md     -> repo root/DECISIONS.md
templates/ARCHITECTURE.md  -> repo root/ARCHITECTURE.md
```

**What you get:**
- Agents remember confirmed patterns and anti-patterns across sessions
- Decisions are documented so they are not re-litigated
- Architecture is explicit so agents build consistently
- Open questions are tracked, not lost in chat history

**When to move to Level 2:**
- You have had 5+ sessions on the same project
- You notice agents repeating mistakes from previous sessions
- You have made architectural decisions that should not be reversed without discussion
- You need a second developer (human or AI) to understand the project from files alone

---

## Level 3: Tracking (45 Minutes)

**Add these files on top of Level 2:**

```
templates/SPRINT_LOG.md       -> repo root/SPRINT_LOG.md
templates/COST_LOG.md         -> repo root/COST_LOG.md
templates/AGENT_REGISTRY.md   -> repo root/AGENT_REGISTRY.md
```

**What you get:**
- Sprint velocity tracking (tasks per session over time, trend analysis)
- AI cost visibility (cost per session, cost per task, model routing optimization)
- Retrospective data to improve the process each sprint
- Budget alerting before costs surprise you
- First-class agent identities: every agent declared with scope, permissions, tool allowlist, ceiling, and owner before it operates

**When to move to Level 3:**
- You want to measure whether AI is actually making you faster
- AI costs are material (team usage, frequent sessions, expensive models)
- You need to justify AI spending to stakeholders or leadership
- You want data for sprint planning (historical velocity for estimation)

---

## Level 4: Enforced (2 Hours)

**What to add on top of Level 3:**
- CI/CD workflows from `../ci-cd/` (GitHub Actions for linting, testing, AI review, governance checks)
- Pre-commit hooks (gitleaks, naming validation, file structure checks)
- Agent definitions from `../agents/` (specialized review agents)
- Branch protection rules on main (require PR, require CI pass, require approval)

**What you get:**
- Every PR is reviewed by an AI agent before human review
- Governance file updates are enforced (code changes without CHANGELOG update = CI failure)
- Security scanning runs automatically on every commit
- Architecture compliance is checked programmatically, not just by convention

**When to move to Level 4:**
- Multiple contributors work on the repository (human or AI)
- Code ships to production
- Governance must be enforced, not merely encouraged
- You need an audit trail for compliance

---

## IDE-Specific Templates

If you use an IDE other than Claude Code, or use multiple IDEs, copy the appropriate template into your project to extend governance rules to that tool's AI assistant:

```
templates/cursor-rules.md          -> .cursor/rules (Cursor IDE)
templates/copilot-instructions.md  -> .github/copilot-instructions.md (GitHub Copilot)
templates/windsurf-rules.md        -> .windsurf/rules.md (Windsurf IDE)
templates/aider-conventions.md     -> .aider.conf.yml convention section (Aider)
```

Each IDE template translates the core governance rules — security constraints, naming conventions, and session discipline — into the format that IDE's AI assistant reads. They are designed to complement, not replace, the primary `CLAUDE.md`.

See [docs/multi-ide-support.md](../docs/multi-ide-support.md) for a feature comparison across all supported IDEs and migration notes.

---

## Governance Dashboard

The `DASHBOARD.md` template is the output format for `automation/governance_dashboard.py`. Copy it to your repo root if you want a manually managed dashboard; the automation script overwrites it on each run.

```
templates/DASHBOARD.md  -> repo root/DASHBOARD.md
```

---

## What to Customize vs. What to Keep

Every template uses comment markers to indicate what to change:

| Marker | Meaning | Action |
|--------|---------|--------|
| `# CUSTOMIZE:` | Replace with your project-specific values | Must change before use |
| `# KEEP:` | Core governance mechanism -- do not modify | Leave as-is |
| `# OPTIONAL:` | Can be removed at lower maturity levels | Remove if not needed yet |
| `<!-- CUSTOMIZE: -->` | HTML comment with customization instructions | Replace content, keep structure |

### What to always change

**`project_context` in CLAUDE.md** -- Replace every placeholder with your actual project name, stack, owner, and phase.

**Phase tasks in PROJECT_PLAN.md** -- Replace example tasks with your actual tasks. Keep the table structure (agents parse it).

**Technology decisions in ARCHITECTURE.md** -- Replace placeholder technologies with your actual stack. Fill in the "Why" and "ADR" columns.

### What to never change

**`mandatory_session_protocol` in CLAUDE.md** -- This is the core governance mechanism. Modifying the session start/end protocol defeats the purpose of the framework.

**`security_protocol` in CLAUDE.md** -- The never-commit list and scan triggers are non-negotiable. Add to them, but do not remove items.

**`mandatory_task_reporting` in CLAUDE.md** -- This prevents agents from silently doing large amounts of work without accountability. Disabling it loses the primary defense against scope creep.

**`verification` in CLAUDE.md** -- Agents skipping verification is the root cause of most "it worked in my head" bugs.

---

## File Reference

### Governance Files (copy to repo root)

| File | Purpose | Updated When | Read By Agent At |
|------|---------|-------------|-----------------|
| `CLAUDE.md` | Agent constitution — rules agents must follow | Monthly review, or when rules change | Every session start |
| `PROJECT_PLAN.md` | Phases, tasks, sprint goals, discovered tasks | Every session end | Every session start |
| `CHANGELOG.md` | Session-level history of what changed and why | Every session end (append) | Every session start (last 10) |
| `MEMORY.md` | Cross-session knowledge: patterns, anti-patterns, preferences | When agent learns something persistent | Every session start |
| `DECISIONS.md` | Permanent log of architectural and process decisions | When decisions are made | When related topics arise |
| `ARCHITECTURE.md` | System design, technology choices, component structure | When architecture changes | Every session start |
| `SPRINT_LOG.md` | Sprint velocity, retrospectives, trend analysis | At sprint boundaries | At sprint planning |
| `COST_LOG.md` | AI cost per session, model routing optimization | Every session end | Monthly review |
| `AGENT_REGISTRY.md` | First-class agent identities: scope, permissions, tools, ceiling, owner | When a new agent is added or agent scope changes | Every session start |
| `DASHBOARD.md` | Auto-generated governance health dashboard | Generated by automation/governance_dashboard.py | Human review, not agent |

### Constitutional Hierarchy (org and team level)

| File | Purpose | Scope |
|------|---------|-------|
| `CLAUDE.org.md` | Organization-level constitution | Inherited by all team and repo constitutions |
| `CLAUDE.team.md` | Team-level constitution | Inherits from org, inherited by repos |

### IDE Templates (copy to IDE config location)

| File | Copy to | IDE |
|------|---------|-----|
| `cursor-rules.md` | `.cursor/rules` | Cursor |
| `copilot-instructions.md` | `.github/copilot-instructions.md` | GitHub Copilot |
| `windsurf-rules.md` | `.windsurf/rules.md` | Windsurf |
| `aider-conventions.md` | `.aider.conf.yml` convention section | Aider |

---

## Cross-References

- For a detailed explanation of each maturity level: [Maturity Model](../docs/maturity-model.md)
- For a worked example of going from Level 0 to Level 3: [Case Study: HealthReporting](../docs/case-studies/health-reporting.md)
- For the full getting started walkthrough: [Getting Started](../docs/getting-started.md)
- For rollback procedures when things go wrong: [Rollback and Recovery](../docs/rollback-recovery.md)
