# AI Governance Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

> **Your AI agent is 15x faster. But is it building the right thing?**

## What Makes This Different

Most AI governance approaches are static rule documents. This framework is a **living system**:

- **Self-testing**: A red team agent actively probes for governance gaps ([/audit](commands/audit.md))
- **Self-updating**: Checks for new best practices and framework updates ([/upgrade](commands/upgrade.md))
- **Self-aware**: Agents know their own model and flag when a task needs a different one
- **Anti-fragile**: Production incidents automatically tighten the rules that allowed them
- **Friction-conscious**: Governance overhead is measured and budgeted — if it's too heavy, we fix it
- **Enterprise-native**: Constitutional inheritance (org → team → repo) with enforced compliance
- **Honest about limits**: Explicit automation bias defense — AI validation has a confidence ceiling of 85%

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
| [`templates/`](templates/) | Core governance file templates: `CLAUDE.md`, `CLAUDE.org.md`, `CLAUDE.team.md`, `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `MEMORY.md`, `SPRINT_LOG.md`, `COST_LOG.md`, `DECISIONS.md`, ADR template |
| [`agents/`](agents/) | Specialized agent definitions: security reviewer, code reviewer, documentation writer, test writer, code simplifier, master agent, quality gate, drift detector, red team auditor, research agent, onboarding agent |
| [`commands/`](commands/) | Slash command definitions: `/plan-session`, `/end-session`, `/status`, `/prioritize`, `/security-review`, `/validate`, `/research`, `/upgrade`, `/health-check`, `/audit` |
| [`ci-cd/`](ci-cd/) | GitHub Actions workflows: AI PR review, governance check, release automation, pre-commit hooks |
| [`scripts/`](scripts/) | Utility scripts: productivity tracker, pre-commit guard hook, post-commit session logger |
| [`docs/`](docs/) | Framework documentation: [architecture](docs/architecture.md), [session protocol](docs/session-protocol.md), [maturity model](docs/maturity-model.md), [getting started](docs/getting-started.md) |
| [`patterns/`](patterns/) | Pattern library: dual-model validation, output contracts, progressive trust, semantic verification, blast radius control, context boundaries, human-in-the-loop, automation bias defense, kill switch, session replay, knowledge decay, friction budget, constitutional inheritance |
| [`automation/`](automation/) | Automation scripts: framework updater, best-practice scanner, governance health calculator |
| [`examples/`](examples/) | Complete configurations for three personas: solo developer, small team, enterprise |

## Agent Orchestration

Independent agents are not enough. An agent that "runs security review" and another that "runs code review" produce redundant work, conflicting feedback, and no shared context. The master agent pattern solves this:

- **Master agent** coordinates all other agents: decomposes tasks, routes to specialists, validates outputs, escalates when agents disagree
- **Quality gate agent** runs after every session: checks output contracts, architecture alignment, test coverage, and naming conventions — produces a score (0-100) and recommendation
- **Onboarding agent** handles new user setup: assesses current state, recommends maturity level, generates configured governance files, walks through first session

See [docs/agent-orchestration.md](docs/agent-orchestration.md) for the full architecture.

## Quality Control

AI agents are confident about everything. A wrong answer and a right answer look identical. The burden of verification is 100% on the human — unless you build a system that helps.

Eight patterns for verifying AI output:

| Pattern | What it solves |
|---------|---------------|
| [Dual-model validation](patterns/dual-model-validation.md) | Same model reviewing its own work catches nothing. Use Sonnet to write, Opus to review. |
| [Output contracts](patterns/output-contracts.md) | Define expected output BEFORE the agent works. Review verifies the contract, not the output in isolation. |
| [Progressive trust](patterns/progressive-trust.md) | Start at maximum oversight. Reduce based on evidence. Reset when quality drops. |
| [Semantic verification](patterns/semantic-verification.md) | Tests verify that code runs. Semantic verification checks that it does the RIGHT thing. |
| [Blast radius control](patterns/blast-radius-control.md) | Limit how much damage one session can do. Maximum 15 files, 200 lines per file by default. |
| [Context boundaries](patterns/context-boundaries.md) | Agents given access to everything use everything. Define what they should and shouldn't see. |
| [Human-in-the-loop](patterns/human-in-the-loop.md) | Specify exactly when human judgment is required. Everything else can proceed without approval. |
| [Automation bias defense](patterns/automation-bias-defense.md) | More AI validation layers can reduce human scrutiny. Cap AI confidence at 85% and surface what was NOT verified. |

See [docs/quality-control-patterns.md](docs/quality-control-patterns.md) for the complete guide.

## Self-Updating Framework

AI capabilities change monthly. A governance framework that requires manual maintenance will drift from current best practices within weeks. This framework includes three mechanisms to stay current:

**Version-based updates**: The `/upgrade` command checks the upstream repository for new releases. It shows what changed, explains why, and applies non-breaking updates (new agents, new docs, new commands) with confirmation. Breaking changes (CLAUDE.md restructuring) always require human review.

**Research pipeline**: The `/research [topic]` command activates the research agent, which scans configured sources (Anthropic docs, engineering blogs, GitHub trending, community forums), filters for actionable, evidence-based insights, and proposes specific framework changes.

**Health assessment**: The `/health-check` command runs the drift detector agent, calculates a governance health score (0-100), identifies gaps, and recommends improvements ranked by impact.

See [docs/self-updating-framework.md](docs/self-updating-framework.md) and [docs/research-pipeline.md](docs/research-pipeline.md) for implementation details.

## Real Results

The framework was built and battle-tested on a real health data platform project — not designed in theory and tested later.

It was used from the first line of code. Every pattern, agent definition, and command in this repository was either extracted from that implementation or created to address a gap discovered during it. The session protocol eliminated context loss between sessions. ADRs stopped re-litigation of closed decisions. CI enforcement made CHANGELOG compliance automatic rather than optional. The case study in [docs/case-studies/health-reporting.md](docs/case-studies/health-reporting.md) documents the full progression, including what did not work and why.

Governance does not slow development down. It redirects a small fraction of velocity into structure so the remainder builds the right thing consistently.

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
