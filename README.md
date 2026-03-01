[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Tests](https://github.com/EduardPetraeus/ai-governance-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/EduardPetraeus/ai-governance-framework/actions/workflows/tests.yml) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md) [![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

# AI Governance Framework

_Make AI a reliable engineer in your repo — not just a fast one._

## Quick Start

**Core Edition — 10 minutes, no infrastructure required:**

```bash
# 1. Copy the constitution to your repo root
cp examples/core-edition/CLAUDE.md ./CLAUDE.md

# 2. Fill in 3 lines (project name, type, stack), then commit
git add CLAUDE.md && git commit -m "chore: add AI governance constitution"

# 3. Install session commands
mkdir -p .claude/commands
cp examples/core-edition/commands/*.md .claude/commands/

# 4. Add CI checks
mkdir -p .github/workflows
cp examples/core-edition/ci-cd/*.yml .github/workflows/
```

Open Claude Code, type `/plan-session`. The agent reads your project state and confirms scope before writing a line of code. When done, `/end-session` commits the state log.

See [examples/core-edition/](examples/core-edition/) for the full 10-minute walkthrough.

**Optional addon — cross-tool governance bridge:**

```bash
# 5. Add AGENTS.md to extend governance to Copilot, Cursor, Windsurf, and Aider
cp templates/AGENTS.md ./AGENTS.md
# Fill in project, stack, and commands sections
git add AGENTS.md && git commit -m "chore: add AGENTS.md portable governance bridge"
```

AGENTS.md is an emerging cross-tool standard (60,000+ projects, Linux Foundation). Pair it
with CLAUDE.md to govern all AI tools on the project with a single rule set.
See [docs/agents-md-integration.md](docs/agents-md-integration.md) for the three coexistence options.

**Full framework — interactive wizard:**

```bash
npx ai-governance-init
```

Asks about your project, team size, CI platform, and IDE — scaffolds the right files. Requires Node.js 14+.

See [docs/getting-started.md](docs/getting-started.md) for both paths with step-by-step instructions.

---

## Why This Exists

AI agents are obedient, not wise. Without governance, they produce technical debt at 15x speed: decisions re-opened every session, scope that expands silently, codebases that drift from every deliberate architectural choice. This framework turns agent obedience into a structural advantage by encoding your goals, constraints, and decisions as durable, machine-readable context.

## What Makes This Different

Most AI governance approaches are static rule documents. This framework is a living system:

- **Self-testing**: A red team agent actively probes for governance gaps ([/audit](commands/audit.md))
- **Self-updating**: Checks for new best practices and framework updates ([/upgrade](commands/upgrade.md))
- **Self-aware**: Agents know their own model and flag when a task needs a different one
- **Anti-fragile**: Production incidents automatically tighten the rules that allowed them
- **Friction-conscious**: Governance overhead is measured and budgeted — if it's too heavy, we fix it
- **Enterprise-native**: Constitutional inheritance (org → team → repo) with enforced compliance
- **Honest about limits**: Explicit automation bias defense — AI validation has a confidence ceiling of 85%

## Quick Start

**Interactive wizard (recommended):**

```bash
npx ai-governance-init
```

Asks about your project, team size, CI platform, and IDE — then scaffolds the right files. Requires Node.js 14+.

**One-liner (macOS / Linux):**

```bash
curl -fsSL https://raw.githubusercontent.com/EduardPetraeus/ai-governance-framework/main/install.sh | bash
```

Clones the framework, runs the wizard, cleans up. Requires git and Node.js 14+.

**Manual:**

```bash
git clone https://github.com/EduardPetraeus/ai-governance-framework.git
cp ai-governance-framework/templates/CLAUDE.md       ./CLAUDE.md
cp ai-governance-framework/templates/PROJECT_PLAN.md ./PROJECT_PLAN.md
cp ai-governance-framework/templates/CHANGELOG.md    ./CHANGELOG.md
```

See [docs/getting-started.md](docs/getting-started.md) for the full walkthrough, including slash command setup and Level 2 upgrade path.

## Architecture — The 7-Layer Stack

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

Each layer builds on the one below. Implement bottom-up.

## vs. Other Approaches

| Feature | This Framework | SuperClaude | Governor | THEOS | GRC Plugin |
|---|---|---|---|---|---|
| Governance layers | 7 structured layers | None | Single-layer | Template-based | Policy-file |
| Self-testing (red team) | Yes | No | No | No | No |
| Self-updating | Yes | No | No | No | No |
| Constitutional inheritance | Yes (org → team → repo) | No | No | No | No |
| CI/CD enforcement | 5 platforms | No | Partial | No | GitHub only |
| Multi-IDE support | 4 IDEs | No | No | No | No |
| Automation bias defense | Yes (85% ceiling) | No | No | No | No |
| Confidence ceiling | 85% (hardcoded) | None | None | None | None |
| Test suite | 273 tests | None | None | None | None |
| Zero core dependencies | Yes | No | No | No | No |
| Maturity model | 6 levels (0-5) | None | None | None | None |
| Agent count | 11 specialized | None | None | None | None |

SuperClaude = productivity enhancement layer; Governor = policy-file governance; THEOS = template orchestration system; GRC Plugin = compliance tooling for specific IDEs.

## Directory Structure

```
ai-governance-framework/
├── agents/            # 11 specialized agent definitions (system prompts for Claude Code)
├── automation/        # 8 Python scripts for governance data collection
├── bin/               # CLI installer (ai-governance-init)
├── ci-cd/             # Workflows for GitHub Actions, GitLab, CircleCI, Bitbucket, Azure DevOps
│   ├── github-actions/
│   ├── gitlab/
│   ├── circleci/
│   ├── bitbucket/
│   ├── azure-devops/
│   └── pre-commit/
├── commands/          # 10 slash command definitions for Claude Code
├── docs/              # Framework documentation organized by topic
│   ├── adr/           # Architecture Decision Records
│   └── case-studies/  # Real-world implementation case studies
├── examples/          # Production-ready configurations for 4 use cases
│   ├── core-edition/  # Minimum viable governance — start here (10 min)
│   ├── solo-developer/
│   ├── small-team/
│   └── enterprise/
├── patterns/          # 13 governance patterns with implementation guides
├── scripts/           # Utility scripts: security review, productivity tracking, git hooks
├── templates/         # All governance file templates (15 files)
├── tests/             # 273 tests across 13 files
├── CLAUDE.md          # This repo's own governance constitution
├── CONTRIBUTING.md    # How to contribute
├── install.sh         # One-liner installer
└── package.json       # CLI wizard package definition
```

## Complete File Inventory

### Agents (11)

| File | Description |
|---|---|
| [agents/security-reviewer.md](agents/security-reviewer.md) | Scans diffs and code for secrets, PII, injection vulnerabilities |
| [agents/code-reviewer.md](agents/code-reviewer.md) | Reviews PRs against naming conventions, ADRs, and architecture decisions |
| [agents/documentation-writer.md](agents/documentation-writer.md) | Writes and maintains technical documentation |
| [agents/test-writer.md](agents/test-writer.md) | Generates comprehensive test suites from requirements and code |
| [agents/code-simplifier.md](agents/code-simplifier.md) | Identifies and eliminates unnecessary complexity |
| [agents/master-agent.md](agents/master-agent.md) | Orchestrates all other agents for multi-step tasks |
| [agents/quality-gate-agent.md](agents/quality-gate-agent.md) | Scores every session output 0-100 against framework standards |
| [agents/drift-detector-agent.md](agents/drift-detector-agent.md) | Detects when the codebase diverges from architectural decisions |
| [agents/red-team-auditor.md](agents/red-team-auditor.md) | Adversarially probes governance gaps and enforcement weaknesses |
| [agents/research-agent.md](agents/research-agent.md) | Scans sources for new AI governance insights and proposes updates |
| [agents/onboarding-agent.md](agents/onboarding-agent.md) | Guides new projects through framework setup and first session |

### Commands (10)

| File | Description |
|---|---|
| [commands/plan-session.md](commands/plan-session.md) | Start a governed session: read state, confirm scope, set goals |
| [commands/end-session.md](commands/end-session.md) | Close a session: update CHANGELOG, MEMORY, PROJECT_PLAN |
| [commands/status.md](commands/status.md) | Report current sprint progress, blockers, and next actions |
| [commands/prioritize.md](commands/prioritize.md) | Rank the task backlog by impact and urgency |
| [commands/security-review.md](commands/security-review.md) | Run the security-reviewer agent on staged changes |
| [commands/audit.md](commands/audit.md) | Run the red-team-auditor against the current governance setup |
| [commands/health-check.md](commands/health-check.md) | Calculate governance health score and identify gaps |
| [commands/research.md](commands/research.md) | Activate the research agent to scan for new best practices |
| [commands/upgrade.md](commands/upgrade.md) | Check for framework updates and apply non-breaking changes |
| [commands/validate.md](commands/validate.md) | Verify that all governance files are complete and cross-references resolve |

### Patterns (13)

| File | Description |
|---|---|
| [patterns/dual-model-validation.md](patterns/dual-model-validation.md) | Use a second model to verify the first model's output |
| [patterns/output-contracts.md](patterns/output-contracts.md) | Define expected output before the agent works |
| [patterns/progressive-trust.md](patterns/progressive-trust.md) | Start at maximum oversight, reduce based on evidence |
| [patterns/semantic-verification.md](patterns/semantic-verification.md) | Verify that code does the right thing, not just that it runs |
| [patterns/blast-radius-control.md](patterns/blast-radius-control.md) | Limit how much damage one session can cause (max 15 files/session) |
| [patterns/context-boundaries.md](patterns/context-boundaries.md) | Define what agents should and should not see |
| [patterns/human-in-the-loop.md](patterns/human-in-the-loop.md) | Specify exactly when human judgment is required |
| [patterns/automation-bias-defense.md](patterns/automation-bias-defense.md) | Cap AI confidence at 85%, surface what was not verified |
| [patterns/kill-switch.md](patterns/kill-switch.md) | Emergency halt procedure for any agent at any maturity level |
| [patterns/session-replay.md](patterns/session-replay.md) | Reconstruct what an agent did and why from session artifacts |
| [patterns/knowledge-decay.md](patterns/knowledge-decay.md) | Detect and refresh stale context before it misleads agents |
| [patterns/friction-budget.md](patterns/friction-budget.md) | Measure and limit governance overhead per session |
| [patterns/constitutional-inheritance.md](patterns/constitutional-inheritance.md) | Cascade org-level rules down to team and repo |

### Templates (16)

| File | Description |
|---|---|
| [templates/CLAUDE.md](templates/CLAUDE.md) | Main agent constitution template (copy to repo root) |
| [templates/AGENTS.md](templates/AGENTS.md) | Portable governance bridge (AGENTS.md standard) for Copilot, Cursor, Windsurf, and Aider |
| [templates/CLAUDE.org.md](templates/CLAUDE.org.md) | Organization-level constitution (inherits to all team/repo constitutions) |
| [templates/CLAUDE.team.md](templates/CLAUDE.team.md) | Team-level constitution (inherits from org, inherited by repos) |
| [templates/PROJECT_PLAN.md](templates/PROJECT_PLAN.md) | Sprint goals, phases, task backlog |
| [templates/ARCHITECTURE.md](templates/ARCHITECTURE.md) | Technology choices, component structure, design decisions |
| [templates/CHANGELOG.md](templates/CHANGELOG.md) | Session-level history of changes |
| [templates/MEMORY.md](templates/MEMORY.md) | Cross-session knowledge: patterns, anti-patterns, confirmed decisions |
| [templates/DECISIONS.md](templates/DECISIONS.md) | Permanent log of architectural decisions |
| [templates/SPRINT_LOG.md](templates/SPRINT_LOG.md) | Sprint velocity, retrospectives, trend data |
| [templates/COST_LOG.md](templates/COST_LOG.md) | AI cost per session, model routing data |
| [templates/DASHBOARD.md](templates/DASHBOARD.md) | Auto-generated governance health dashboard |
| [templates/cursor-rules.md](templates/cursor-rules.md) | Governance rules for Cursor IDE |
| [templates/copilot-instructions.md](templates/copilot-instructions.md) | Governance rules for GitHub Copilot |
| [templates/windsurf-rules.md](templates/windsurf-rules.md) | Governance rules for Windsurf IDE |
| [templates/aider-conventions.md](templates/aider-conventions.md) | Governance conventions for Aider |

### Automation Scripts (8)

| File | Description |
|---|---|
| [automation/health_score_calculator.py](automation/health_score_calculator.py) | Scores governance maturity 0-100 across 15 checks |
| [automation/governance_dashboard.py](automation/governance_dashboard.py) | Generates DASHBOARD.md from project artifacts |
| [automation/best_practice_scanner.py](automation/best_practice_scanner.py) | Scans sources for new AI governance insights |
| [automation/framework_updater.py](automation/framework_updater.py) | Checks upstream for new framework releases |
| [automation/cost_dashboard.py](automation/cost_dashboard.py) | Analyzes AI cost trends from COST_LOG.md |
| [automation/inherits_from_validator.py](automation/inherits_from_validator.py) | Validates constitutional inheritance chain |
| [automation/token_counter.py](automation/token_counter.py) | Estimates session token usage from git history |
| [automation/adr_coverage_checker.py](automation/adr_coverage_checker.py) | Identifies architectural decisions lacking ADRs |

### Scripts (5)

| File | Description |
|---|---|
| [scripts/ai_security_review.py](scripts/ai_security_review.py) | Security scanner for git diffs (CRITICAL/HIGH/MEDIUM/LOW) |
| [scripts/productivity_tracker.py](scripts/productivity_tracker.py) | Git-based productivity metrics calculator |
| [scripts/deploy_commands.sh](scripts/deploy_commands.sh) | Installs slash commands into .claude/commands/ |
| [scripts/hooks/pre_commit_guard.sh](scripts/hooks/pre_commit_guard.sh) | Pre-commit hook blocking governance violations |
| [scripts/hooks/post_commit.sh](scripts/hooks/post_commit.sh) | Post-commit session logging hook |

### CI/CD Workflows (10 files across 5 platforms + pre-commit)

| File | Description |
|---|---|
| [ci-cd/github-actions/ai-pr-review.yml](ci-cd/github-actions/ai-pr-review.yml) | AI-powered PR review on every pull request |
| [ci-cd/github-actions/governance-check.yml](ci-cd/github-actions/governance-check.yml) | Enforces CHANGELOG and governance file updates |
| [ci-cd/github-actions/release.yml](ci-cd/github-actions/release.yml) | Release automation with semantic versioning gates |
| [ci-cd/gitlab/.gitlab-ci.yml](ci-cd/gitlab/.gitlab-ci.yml) | GitLab CI pipeline definition |
| [ci-cd/gitlab/ai-review.yml](ci-cd/gitlab/ai-review.yml) | GitLab AI PR review job |
| [ci-cd/gitlab/tests.yml](ci-cd/gitlab/tests.yml) | GitLab test runner job |
| [ci-cd/circleci/.circleci/config.yml](ci-cd/circleci/.circleci/config.yml) | CircleCI governance pipeline |
| [ci-cd/bitbucket/bitbucket-pipelines.yml](ci-cd/bitbucket/bitbucket-pipelines.yml) | Bitbucket Pipelines governance workflow |
| [ci-cd/azure-devops/azure-pipelines.yml](ci-cd/azure-devops/azure-pipelines.yml) | Azure DevOps governance pipeline |
| [ci-cd/pre-commit/.pre-commit-config.yaml](ci-cd/pre-commit/.pre-commit-config.yaml) | Pre-commit hooks for local enforcement |

## Maturity Model

| Level | Name | What This Looks Like |
|:-----:|------|----------------------|
| **0** | **Ad-hoc** | "Vibe coding." Agent does whatever is asked. No audit trail. You cannot reconstruct what was built or why. Technical debt accumulates at AI speed. |
| **1** | **Foundation** | `CLAUDE.md` exists and the agent reads it. Sessions start with a governance sync and end with a CHANGELOG update. The agent confirms scope before writing code. |
| **2** | **Structured** | Architecture decisions are recorded in ADRs. Memory persists across sessions. Specialized agents handle distinct concerns. Sprint goals exist and are tracked. |
| **3** | **Enforced** | Governance has teeth. CI/CD rejects ungoverned changes. Pre-commit hooks catch secrets. AI reviews every PR against the constitution. No merge without documented state. |
| **4** | **Measured** | You know your AI productivity number. A master agent detects architectural drift. Cost is tracked per session. Quality metrics drive decisions, not intuition. |
| **5** | **Self-optimizing** | The framework improves itself. Retrospectives are automated. Org-level governance cascades to every repo. Compliance audit trails are complete. |

See [docs/maturity-model.md](docs/maturity-model.md) for upgrade paths and self-assessment checklists.

## Agent Orchestration

Independent agents are not enough. An agent that "runs security review" and another that "runs code review" produce redundant work, conflicting feedback, and no shared context. The master agent pattern solves this:

- **Master agent** coordinates all other agents: decomposes tasks, routes to specialists, validates outputs, escalates when agents disagree
- **Quality gate agent** runs after every session: checks output contracts, architecture alignment, test coverage, and naming conventions — produces a score (0-100) and a concrete recommendation
- **Onboarding agent** handles new user setup: assesses current state, recommends maturity level, generates configured governance files, walks through first session

See [docs/agent-orchestration.md](docs/agent-orchestration.md) for the full orchestration architecture.

## Quality Control

AI agents are confident about everything. A wrong answer and a right answer look identical. The burden of verification is 100% on the human — unless you build a system that helps.

Eight patterns for verifying AI output:

| Pattern | What It Solves |
|---|---|
| [Dual-model validation](patterns/dual-model-validation.md) | Same model reviewing its own work catches nothing. Use Sonnet to write, Opus to review. |
| [Output contracts](patterns/output-contracts.md) | Define expected output before the agent works. Review verifies the contract, not the output in isolation. |
| [Progressive trust](patterns/progressive-trust.md) | Start at maximum oversight. Reduce based on evidence. Reset when quality drops. |
| [Semantic verification](patterns/semantic-verification.md) | Tests verify that code runs. Semantic verification checks that it does the right thing. |
| [Blast radius control](patterns/blast-radius-control.md) | Limit how much damage one session can do. Maximum 15 files, 200 lines per file by default. |
| [Context boundaries](patterns/context-boundaries.md) | Agents given access to everything use everything. Define what they should and should not see. |
| [Human-in-the-loop](patterns/human-in-the-loop.md) | Specify exactly when human judgment is required. Everything else proceeds without approval. |
| [Automation bias defense](patterns/automation-bias-defense.md) | More AI validation layers can reduce human scrutiny. Cap AI confidence at 85% and surface what was not verified. |

See [docs/quality-control-patterns.md](docs/quality-control-patterns.md) for the complete guide.

## Who Is This For

**You ship with AI but lose control of what it builds.** The agent forgets context between sessions, expands scope without asking, commits things you did not request, and sometimes introduces bugs that look correct until production. You want that fixed without a week of governance infrastructure.

**Core Edition** (10 minutes) — Solo developers and teams up to 10 who want an agent that reads project state before coding, confirms scope, and leaves a written record. No CI platform required beyond GitHub Actions. See [examples/core-edition/](examples/core-edition/).

**Solo developers** — You need continuity across sessions without manually re-explaining your project every time. Core Edition is your starting point. See [examples/solo-developer/CLAUDE.md](examples/solo-developer/CLAUDE.md) for a project-specific example.

**Teams (5-20 developers)** — Multiple agents running, each following the nearest instruction instead of the shared plan. PRs land without architectural consistency checks. Start at Core Edition, add Layer 3 enforcement within a sprint. See [examples/small-team/CLAUDE.md](examples/small-team/CLAUDE.md).

**Enterprise (50+ developers)** — AI adoption is happening whether governance exists or not. You need compliance audit trails, role-based agent access, and cross-repo consistency. Start at Layers 2-3, target Level 5. See [examples/enterprise/CLAUDE.md](examples/enterprise/CLAUDE.md) and [docs/enterprise-playbook.md](docs/enterprise-playbook.md).

## Built With This Framework

This repository is the reference implementation of Layer 1 (Constitution) of the framework it describes. Every file, every cross-reference, and every governance decision in this repo follows the framework's own standards. The CLAUDE.md at the root of this repository governs how AI agents work on this codebase. Governance does not require a separate system. It requires the discipline to apply the same standards everywhere.

## Roadmap

- [x] CLI installer (`npx ai-governance-init`)
- [x] GitLab CI/CD support
- [x] CircleCI and Bitbucket Pipelines support
- [x] Azure DevOps support
- [x] Multi-IDE support (Cursor, Copilot, Windsurf, Aider)
- [x] 273-test automated test suite
- [ ] VS Code extension — inline governance compliance hints
- [ ] Org-level CLAUDE.md inheritance resolver (UI-driven)
- [ ] OpenAI / Gemini model routing configuration

## Contributing

Contributions are welcome. The framework has a 273-test suite and enforces its own governance standards on every PR — contributions must pass the full test suite and follow the conventions in [CLAUDE.md](CLAUDE.md). See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report issues, add agents or commands, propose new patterns, and the quality bar required for all pull requests.

## License

MIT — see [LICENSE](LICENSE).

Built from practice. Designed for reuse. Governed by its own framework.
