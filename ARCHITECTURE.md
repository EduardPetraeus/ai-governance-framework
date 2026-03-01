# Architecture

The AI Governance Framework is organized around a 7-layer stack. Each layer has a
single responsibility. The full specification is in [docs/architecture.md](docs/architecture.md).

## The Stack

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
│  CI/CD checks, MCP access control, AI PR review         │
├─────────────────────────────────────────────────────────┤
│  Layer 2: ORCHESTRATION — Session & sprint              │
│  Session protocol, sprint planning, scope management    │
├─────────────────────────────────────────────────────────┤
│  Layer 1: CONSTITUTION — Static rules                   │
│  CLAUDE.md, ADRs, security policies, naming conventions │
└─────────────────────────────────────────────────────────┘
```

Rules flow down. Data flows up. Implement bottom-up.

## Key Decisions

| Decision | Record |
|---|---|
| Markdown as the universal format for governance artifacts | [ADR-001](docs/adr/ADR-001-markdown-as-governance-format.md) |
| No external runtime dependencies in the core framework | [ADR-002](docs/adr/ADR-002-zero-runtime-dependencies.md) |
| Slash commands as the agent interface standard | [ADR-003](docs/adr/ADR-003-slash-commands-interface.md) |
| Constitutional inheritance via `inherits_from:` | [ADR-004](docs/adr/ADR-004-constitutional-inheritance.md) |

## Repository Structure

```
ai-governance-framework/
├── agents/        # 11 specialized agent definitions
├── automation/    # 8 Python governance automation scripts
├── bin/           # CLI installer
├── ci-cd/         # CI/CD workflows: GitHub, GitLab, CircleCI, Bitbucket, Azure
├── commands/      # 10 slash command definitions
├── docs/          # Framework documentation and ADRs
├── examples/      # Production-ready configurations (4 use cases)
├── patterns/      # 15 governance patterns
├── scripts/       # Security review, hooks, productivity tracking
├── templates/     # 16 governance file templates
└── tests/         # 273+ automated tests
```

## Design Principles

- **Zero core dependencies:** CLAUDE.md + any text editor is enough to start
- **Bottom-up implementation:** Each layer is independently useful
- **Self-governing:** This repo is governed by the framework it describes
- **Honest about limits:** Automation bias confidence ceiling defaults to 85%

See [docs/architecture.md](docs/architecture.md) for the full layer specification.
