# AI Governance Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

**Your AI agent is 15x faster. But is it building the right thing?**

---

## The Problem

AI agents are obedient, not wise. They optimize for the nearest instruction — not your team's actual goals. Without governance, they produce technical debt at 15x speed, introduce scope creep you did not authorize, and lose architectural context the moment a session closes.

Most teams discover this after the damage is done: divergent implementations across developers, secrets accidentally committed, architecture that no one can explain, and a codebase that has drifted from every decision that was ever made deliberately.

Governance is not about slowing agents down. It is about giving them the right context so their obedience produces the right result.

---

## The Solution

A **7-layer governance framework** for AI-assisted software development. Battle-tested on a real project (137 commits, 16x velocity, 12 specialized agents, 11 slash commands, 4 ADRs, full CI/CD with AI PR review). Extracted into generic, reusable patterns that work at any scale — from solo developer to enterprise.

---

## The 7-Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│  Layer 7: EVOLUTION — Meta-governance                   │
│  Who updates the rules? How does the system improve?    │
├─────────────────────────────────────────────────────────┤
│  Layer 6: TEAM GOVERNANCE — Multi-agent, multi-human    │
│  Roles, responsibilities, conflict resolution           │
├─────────────────────────────────────────────────────────┤
│  Layer 5: KNOWLEDGE — Continuity & memory               │
│  Memory hierarchy, ADRs, context propagation            │
├─────────────────────────────────────────────────────────┤
│  Layer 4: OBSERVABILITY — What is happening             │
│  Audit trails, decision logs, cost tracking, metrics    │
├─────────────────────────────────────────────────────────┤
│  Layer 3: ENFORCEMENT — Automated gates                 │
│  CI/CD checks, agent PR review, security scanning       │
├─────────────────────────────────────────────────────────┤
│  Layer 2: ORCHESTRATION — Session & sprint              │
│  Session protocols, sprint planning, scope management   │
├─────────────────────────────────────────────────────────┤
│  Layer 1: CONSTITUTION — Static rules                   │
│  CLAUDE.md, ADRs, security policies, conventions        │
└─────────────────────────────────────────────────────────┘
```

Each layer builds on the one below it. You cannot have enforcement without a constitution. You cannot have team governance without observability. Implement bottom-up.

---

## Quick Start

```bash
# 1. Clone the framework
git clone https://github.com/your-org/ai-governance-framework.git

# 2. Copy the core templates into your project
cp ai-governance-framework/templates/CLAUDE.md.template your-project/CLAUDE.md
cp ai-governance-framework/templates/PROJECT_PLAN.md.template your-project/PROJECT_PLAN.md
cp ai-governance-framework/templates/ARCHITECTURE.md.template your-project/docs/ARCHITECTURE.md

# 3. Start your first governed session
# Open your project in Claude Code — it will read CLAUDE.md automatically
# The session protocol in CLAUDE.md will guide the agent from the first message
```

Your agent now has a constitution to follow, a session protocol to execute, and a project plan to orient against. That is Layer 1 and Layer 2 implemented in under five minutes.

---

## Maturity Levels

| Level | Name | Description |
|-------|------|-------------|
| **0** | Chaos | No governance files. Agents code freely. No audit trail. Technical debt accumulates at AI speed. |
| **1** | Foundation | `CLAUDE.md` exists and is maintained. Session start/end protocol followed. `CHANGELOG.md` updated per session. Git-based workflow. |
| **2** | Structured | `PROJECT_PLAN.md` with phases and milestones. `ARCHITECTURE.md` with diagrams. ADRs for key decisions. Basic CI/CD (lint, tests). |
| **3** | Enforced | Agent PR review as CI check. Automated security scanning. Governance file update check. Pre-commit hooks. Cost tracking. |
| **4** | Optimized | Master agent with full context. Quality metrics tracked over time. Automatic drift detection. Multi-agent specialization. |
| **5** | Enterprise | Org-level constitution. Cross-repo governance. Compliance audit trail. Role-based agent access. Governance dashboard. Full cost attribution. |

The HealthReporting case study moved from Level 0 to Level 3 in two weeks.

---

## What Is Included

| Directory | Contents |
|-----------|----------|
| `templates/` | Core governance file templates: `CLAUDE.md`, `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, ADR template |
| `agents/` | Specialized agent definitions: code agent, review agent, security agent, docs agent, cost agent |
| `commands/` | Slash command definitions for Claude Code: `/review`, `/security-review`, `/session-start`, `/session-end`, `/sprint-status` and more |
| `ci-cd/` | GitHub Actions workflows: AI PR review, naming convention validation, security scanning, governance file check |
| `scripts/` | Utility scripts: naming convention validator, governance compliance checker, cost log parser |
| `docs/` | Framework documentation, layer-by-layer implementation guide, prompt engineering patterns |
| `examples/` | Complete worked example from the HealthReporting case study (anonymized) |

---

## Real Results

The framework was developed from and validated against a real implementation:

| Metric | Value |
|--------|-------|
| Total commits | 137 |
| Measured velocity increase | 16x |
| Specialized agents deployed | 12 |
| Slash commands implemented | 11 |
| Architecture Decision Records written | 4 |
| CI/CD pipeline | Full, with AI PR review |
| Governance maturity progression | Level 0 to Level 3 in 2 weeks |
| Session protocol compliance | 100% (enforced by CLAUDE.md) |
| Secrets committed to git | 0 |

16x velocity is not the goal — it is the byproduct of a team that knows what it is building and has automated the discipline to build it correctly.

---

## Who Is This For

**Solo developers**
- You are shipping fast but losing track of what you have built
- You want continuity across sessions without manual context-loading
- You need one framework file that makes your agent dramatically more useful
- Start at Layer 1. One afternoon to implement. Immediate results.

**Small teams (5–20 developers)**
- Multiple agents are running, each following the nearest instruction
- PRs land without anyone checking architectural consistency
- You want AI-powered code review without setting up a complex platform
- Start at Layer 1–2. Add Layer 3 enforcement within a sprint.

**Enterprise teams (50+ developers)**
- You need compliance audit trails, role-based agent access, and cross-repo consistency
- AI adoption is happening whether governance exists or not
- You want a framework that integrates with existing processes rather than replacing them
- Start at Layer 2–3 org-wide. Layer 5 is your target state.

---

## Roadmap

- [ ] CLI installer (`npx ai-governance-init`) — scaffolds all templates into an existing project
- [ ] GitLab CI/CD equivalents for all GitHub Actions workflows
- [ ] VS Code extension — inline governance compliance hints
- [ ] CircleCI and Bitbucket Pipelines support
- [ ] Org-level CLAUDE.md inheritance resolver
- [ ] Cost dashboard (Markdown-based, no external dependencies)

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report issues, suggest improvements, add new agents or commands, and the quality bar required for PRs.

---

## License

MIT — see [LICENSE](LICENSE).

Built from real-world practice. Designed for reuse. Governed by its own framework.
