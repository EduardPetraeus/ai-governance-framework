# AI Governance Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

> **Your AI agent is 15x faster. But is it building the right thing?**

## The Problem

AI agents are obedient, not wise. They optimize for the nearest instruction, not your organization's actual goals. Without governance, they produce technical debt at 15x speed: divergent implementations across developers, architectural decisions reopened in every session, scope that expands silently, and a codebase that drifts from every deliberate choice ever made.

The cost is not individual errors. The cost is structural incoherence compounding across hundreds of commits until no one — human or agent — can explain why the system is built the way it is.

**Governance is not about slowing agents down. It is about giving them the right context so their obedience produces the right result.**

## The 7-Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│  Layer 7: EVOLUTION — Meta-governance                   │
│  Who updates the rules? How does the system improve?    │
├─────────────────────────────────────────────────────────┤
│  Layer 6: TEAM GOVERNANCE — Multi-agent, multi-human    │
│  Roles, ownership, conflict resolution, escalation      │
├─────────────────────────────────────────────────────────┤
│  Layer 5: KNOWLEDGE — Continuity & memory               │
│  Memory hierarchy, ADRs, context propagation            │
├─────────────────────────────────────────────────────────┤
│  Layer 4: OBSERVABILITY — What is happening             │
│  Audit trails, decision logs, cost tracking, metrics    │
├─────────────────────────────────────────────────────────┤
│  Layer 3: ENFORCEMENT — Automated gates                 │
│  CI/CD checks, AI PR review, security scanning          │
├─────────────────────────────────────────────────────────┤
│  Layer 2: ORCHESTRATION — Session & sprint              │
│  Session protocol, sprint planning, scope management    │
├─────────────────────────────────────────────────────────┤
│  Layer 1: CONSTITUTION — Static rules                   │
│  CLAUDE.md, ADRs, security policies, naming conventions │
└─────────────────────────────────────────────────────────┘

          ▲ Data flows up          Rules flow down ▼
```

Each layer builds on the one below. You cannot enforce rules you have not written. You cannot observe chaos you have not structured. Implement bottom-up.

## Quick Start

```bash
# 1. Clone the framework
git clone https://github.com/clauseduardpetraeus/ai-governance-framework.git

# 2. Copy Level 1 templates into your project
cp ai-governance-framework/templates/CLAUDE.md       your-project/CLAUDE.md
cp ai-governance-framework/templates/PROJECT_PLAN.md  your-project/PROJECT_PLAN.md
cp ai-governance-framework/templates/CHANGELOG.md     your-project/CHANGELOG.md

# 3. Open your project in Claude Code — it reads CLAUDE.md automatically.
#    The session protocol guides the agent from the first message.
```

Your agent now has a constitution to follow, a session protocol to execute, and a project plan to orient against. Layers 1 and 2 are live. Time investment: under five minutes.

See [docs/getting-started.md](docs/getting-started.md) for the full walkthrough.

## Maturity Model

| Level | Name | What This Looks Like |
|:-----:|------|----------------------|
| **0** | **Ad-hoc** | "Vibe coding." Agent does whatever is asked. No audit trail. You cannot reconstruct what was built or why. Technical debt accumulates at AI speed. |
| **1** | **Foundation** | `CLAUDE.md` exists and the agent reads it. Sessions start with a governance sync and end with a CHANGELOG update. The agent confirms scope before writing code. |
| **2** | **Structured** | Architecture decisions are recorded in ADRs. Memory persists across sessions. Specialized agents handle distinct concerns. Sprint goals exist and are tracked. |
| **3** | **Enforced** | Governance has teeth. CI/CD rejects ungoverned changes. Pre-commit hooks catch secrets. AI reviews every PR against the constitution. No merge without documented state. |
| **4** | **Measured** | You know your AI productivity number. A master agent detects architectural drift. Cost is tracked per session. Quality metrics drive decisions, not intuition. |
| **5** | **Self-optimizing** | The framework improves itself. Retrospectives are automated. Org-level governance cascades to every repo. Compliance audit trails are complete. |

See [docs/maturity-model.md](docs/maturity-model.md) for the full model with upgrade paths and self-assessment.

## What Is Included

| Directory | Contents |
|-----------|----------|
| [`templates/`](templates/) | Core governance file templates: `CLAUDE.md`, `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, ADR template |
| [`agents/`](agents/) | Specialized agent definitions: code, review, security, docs, cost, master agent |
| [`commands/`](commands/) | Slash command definitions: `/plan-session`, `/end-session`, `/sprint-status`, `/review`, `/security-review` |
| [`ci-cd/`](ci-cd/) | GitHub Actions workflows: AI PR review, naming validation, security scanning, governance file check |
| [`scripts/`](scripts/) | Utility scripts: naming convention validator, governance compliance checker, cost log parser |
| [`docs/`](docs/) | Framework documentation: [architecture](docs/architecture.md), [session protocol](docs/session-protocol.md), [maturity model](docs/maturity-model.md), [getting started](docs/getting-started.md) |
| [`examples/`](examples/) | Worked examples from the HealthReporting case study (anonymized) |

## Real Results

The framework was extracted from a real implementation — not designed in theory and tested later.

| Metric | Value |
|--------|-------|
| Total commits | 137 |
| Measured velocity increase | 16x |
| Specialized agents deployed | 12 |
| Slash commands implemented | 11 |
| Architecture Decision Records | 4 |
| Governance maturity progression | Level 0 → Level 3 in 2 weeks |
| Session protocol compliance | 100% (enforced by CLAUDE.md) |
| Secrets committed to git | 0 |

16x velocity is the byproduct, not the goal. The goal is a team that knows what it is building and has automated the discipline to build it correctly. Speed follows from alignment.

## Who Is This For

**Solo developers** — You ship fast but lose track of what you have built. You need continuity across sessions without manually re-explaining your project every time. Start at Level 1. One afternoon. Immediate results.

**Teams (5-20 developers)** — Multiple agents are running, each following the nearest instruction instead of the shared plan. PRs land without architectural consistency checks. You want governed AI development without a complex platform. Start at Layers 1-2, add Layer 3 enforcement within a sprint.

**Enterprise (50+ developers)** — AI adoption is happening whether governance exists or not. You need compliance audit trails, role-based agent access, and cross-repo consistency. You want a framework that integrates with existing processes. Start at Layers 2-3, target Level 5.

## Roadmap

- [ ] CLI installer (`npx ai-governance-init`) — scaffolds templates into an existing project
- [ ] VS Code extension — inline governance compliance hints
- [ ] GitLab CI/CD equivalents for all GitHub Actions workflows
- [ ] CircleCI and Bitbucket Pipelines support
- [ ] Org-level CLAUDE.md inheritance resolver
- [ ] Cost dashboard (Markdown-based, no external dependencies)

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report issues, add agents or commands, and the quality bar required for PRs.

## License

MIT — see [LICENSE](LICENSE).

Built from practice. Designed for reuse. Governed by its own framework.
