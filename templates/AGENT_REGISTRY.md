# Agent Registry

## Overview

This registry defines every AI agent authorized to operate in this repository. Each agent is a first-class identity with a declared scope, explicit permissions, a tool allowlist, a confidence ceiling, and a named owner.

An agent that operates without an entry in this file is a governance violation. See [docs/agent-registry.md](../docs/agent-registry.md) for the full specification and the unregistered agent protocol.

---

## How to Use This File

1. Copy this file to your repository root as `AGENT_REGISTRY.md`.
2. Remove agents you do not use.
3. Update the `owner` fields with your actual team members.
4. Update `review_date` to 90 days from today.
5. Add entries for any agents not listed here before those agents begin work.

Fields marked `# KEEP:` are governance mechanisms — do not remove them. Fields marked `# CUSTOMIZE:` must be updated for your project.

---

## Registered Agents

```yaml
agents:

  # ---------------------------------------------------------------------------
  # Claude Code — Anthropic
  # Primary development agent for coding, review, and documentation tasks
  # ---------------------------------------------------------------------------
  - identity:
      id: claude-code-primary                         # KEEP: used as audit key
      name: Claude Code
      model: claude-sonnet-4-6                        # CUSTOMIZE: update when model changes
      provider: Anthropic
      purpose: General-purpose coding assistant for feature development, code review, refactoring, and documentation

    scope:
      repos:
        - "*"                                         # CUSTOMIZE: list specific repos to restrict scope
      branches:
        - "feature/*"
        - "fix/*"
        - "docs/*"
        - "refactor/*"
        - "test/*"
      environments:
        - development
        - staging                                     # CUSTOMIZE: remove staging if not applicable
      excluded_paths:
        - ".env"
        - "*.pem"
        - "*.key"
        - "secrets/"
        - ".git/config"

    permissions:
      read:
        - "**/*"                                      # KEEP: read-all is standard for coding agents
      write:
        - "src/**/*"
        - "tests/**/*"
        - "docs/**/*"
        - "templates/**/*"
        - "CHANGELOG.md"
        - "MEMORY.md"
        - "PROJECT_PLAN.md"
      execute:
        bash_commands: user_approved_only             # KEEP: no unrestricted shell execution
        scripts: []                                   # CUSTOMIZE: add trusted scripts if needed
      denied:
        - "*.env"
        - "*.pem"
        - "*.key"
        - ".git/config"
        - "ci-cd/**/*.yml"                            # CI pipelines require explicit authorization

    tools:
      mcp_servers:
        - name: filesystem
          access: read_write
          paths: ["./"]
        - name: github_api
          access: read_write
          scope: [issues, pull_requests, commits, comments]
      native_tools:
        - bash
        - glob
        - grep
        - read
        - edit
        - write
        - web_fetch
        - web_search
      denied_servers:
        - shell_execution_unrestricted
        - cloud_infrastructure
        - database_write
        - production_systems

    ceiling:
      confidence_max: 85                              # KEEP: default per ADR-003
      rationale: Prevents automation bias; humans must judge business logic, performance, and correctness

    owner:
      name: Engineering Team                          # CUSTOMIZE: actual name or team
      contact: engineering@example.com                # CUSTOMIZE: actual contact
      review_date: 2025-06-01                         # CUSTOMIZE: 90 days from today
      approved_by: Lead Engineer                      # CUSTOMIZE: actual approver
      approval_date: 2025-03-01                       # CUSTOMIZE: today's date


  # ---------------------------------------------------------------------------
  # GitHub Copilot — Microsoft / GitHub
  # Inline suggestion agent in VS Code and JetBrains IDEs
  # ---------------------------------------------------------------------------
  - identity:
      id: github-copilot-ide
      name: GitHub Copilot
      model: gpt-4o                                   # CUSTOMIZE: update to reflect current Copilot model
      provider: Microsoft / GitHub
      purpose: Inline code completion and chat assistance within IDE; operates on open files only

    scope:
      repos:
        - "*"
      branches:
        - "*"                                         # Copilot has no branch awareness; restrict via IDE settings
      environments:
        - development
      excluded_paths:
        - ".env"
        - "*.pem"
        - "*.key"
        - "secrets/"

    permissions:
      read:
        - "**/*"                                      # Reads open files and workspace context automatically
      write:
        - "**/*"                                      # Suggestions only; developer must accept each change
      execute:
        bash_commands: none                           # KEEP: Copilot does not execute commands
      denied:
        - "*.env"
        - "*.pem"
        - "*.key"

    tools:
      mcp_servers: []                                 # Copilot does not use MCP in standard configuration
      native_tools:
        - inline_suggestions
        - copilot_chat
        - copilot_code_review
      denied_servers:
        - all_mcp                                     # MCP access not applicable to Copilot

    ceiling:
      confidence_max: 85                              # KEEP: applies to Copilot Chat review outputs
      rationale: Inline completions carry no explicit confidence; ceiling applies to review chat outputs

    owner:
      name: Engineering Team                          # CUSTOMIZE
      contact: engineering@example.com                # CUSTOMIZE
      review_date: 2025-06-01                         # CUSTOMIZE
      approved_by: Lead Engineer                      # CUSTOMIZE
      approval_date: 2025-03-01                       # CUSTOMIZE


  # ---------------------------------------------------------------------------
  # Cursor — Anysphere
  # IDE agent with composer, chat, and terminal integration
  # ---------------------------------------------------------------------------
  - identity:
      id: cursor-composer-primary
      name: Cursor
      model: claude-3-5-sonnet-20241022               # CUSTOMIZE: Cursor allows model selection; update to actual
      provider: Anysphere
      purpose: Composer-based multi-file editing, chat, and terminal assistance within Cursor IDE

    scope:
      repos:
        - "*"
      branches:
        - "feature/*"
        - "fix/*"
        - "docs/*"
      environments:
        - development
      excluded_paths:
        - ".env"
        - "*.pem"
        - "*.key"
        - "secrets/"
        - ".git/config"

    permissions:
      read:
        - "**/*"
      write:
        - "src/**/*"
        - "tests/**/*"
        - "docs/**/*"
        - "CHANGELOG.md"
      execute:
        bash_commands: user_approved_only             # KEEP: terminal access requires explicit approval in Cursor
        scripts: []
      denied:
        - "*.env"
        - "*.pem"
        - "*.key"
        - ".git/config"
        - "ci-cd/**/*.yml"

    tools:
      mcp_servers:
        - name: filesystem
          access: read_write
          paths: ["./"]
      native_tools:
        - cursor_composer
        - cursor_chat
        - terminal
      denied_servers:
        - cloud_infrastructure
        - database_write
        - production_systems

    ceiling:
      confidence_max: 85                              # KEEP: default per ADR-003
      rationale: Prevents automation bias in Cursor chat review outputs

    owner:
      name: Engineering Team                          # CUSTOMIZE
      contact: engineering@example.com                # CUSTOMIZE
      review_date: 2025-06-01                         # CUSTOMIZE
      approved_by: Lead Engineer                      # CUSTOMIZE
      approval_date: 2025-03-01                       # CUSTOMIZE
```

---

## Archived Agents

Move retired agents here instead of deleting them. The archive preserves the audit trail.

```yaml
archived_agents: []
```

---

## Registry Audit Log

Record registry changes here. One line per change.

```
2025-03-01 | Added claude-code-primary, github-copilot-ide, cursor-composer-primary | Initial registry setup
```

---

## Cross-References

- [docs/agent-registry.md](../docs/agent-registry.md) — full specification: schema details, violation protocol, and layer-by-layer integration
- [patterns/agent-identity.md](../patterns/agent-identity.md) — implementation pattern for enforcing identity at Level 1, Level 3, and Level 5
- [patterns/mcp-governance.md](../patterns/mcp-governance.md) — MCP enforcement that reads this file's `tools.mcp_servers` and `tools.denied_servers` lists
- [docs/known-failure-modes.md](../docs/known-failure-modes.md) — failure mode 3 (Shadow Automation) for what happens without this file
