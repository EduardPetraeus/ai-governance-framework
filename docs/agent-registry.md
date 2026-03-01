# Agent Registry

## Overview

An agent registry treats every AI agent as a first-class identity with a defined scope, explicit permissions, a declared tool allowlist, a confidence ceiling, and a named owner. Without a registry, agents are anonymous processes. There is no way to answer: which agent wrote this code, which tools was it allowed to use, who approved its access, or what scope was it operating within.

The registry is a governance document, not a service. It lives in the repository alongside `CLAUDE.md` and is versioned with the codebase. Every agent identity is declared before the agent operates. An agent that operates without a registry entry is a governance violation, not a configuration gap.

This document defines the registry schema, the violation protocol for unregistered agents, and how the registry integrates with the framework's seven-layer stack.

---

## Registry Entry Schema

Each registered agent must have the following fields. No field is optional.

### identity

Uniquely identifies the agent across sessions and environments.

```yaml
identity:
  id: claude-code-primary          # Unique across all registry entries
  name: Claude Code                # Human-readable display name
  model: claude-sonnet-4-6         # Model identifier or version string
  provider: Anthropic              # Vendor responsible for the model
  purpose: General-purpose coding assistant for feature development and review
```

The `id` field is used as the audit key: all agent actions in logs, changelogs, and governance reports reference this identifier.

### scope

Defines where the agent is permitted to operate.

```yaml
scope:
  repos:
    - "*"                          # All repos, or list specific ones
  branches:
    - "feature/*"
    - "fix/*"
    - "docs/*"
  environments:
    - development
    - staging
  excluded_paths:
    - ".env"
    - "secrets/"
    - "*.pem"
```

An agent operating in a repo, branch, or environment not listed in its scope entry is out-of-scope and must halt.

### permissions

Defines what the agent can read, write, and execute within its scope.

```yaml
permissions:
  read:
    - "**/*"                       # All files readable
  write:
    - "src/**/*"
    - "tests/**/*"
    - "docs/**/*"
    - "CHANGELOG.md"
    - "MEMORY.md"
  execute:
    - bash_commands: user_approved_only
    - scripts: ["scripts/*.sh"]
  denied:
    - "*.env"
    - "*.pem"
    - ".git/config"
    - "ci-cd/**/*.yml"             # CI pipelines require explicit authorization
```

Permissions follow a deny-by-default model: anything not explicitly permitted is denied.

### tools

Lists every MCP server and native tool the agent is authorized to invoke.

```yaml
tools:
  mcp_servers:
    - name: filesystem
      access: read_write
      paths: ["./"]
    - name: github_api
      access: read_write
      scope: ["issues", "pull_requests", "commits"]
  native_tools:
    - bash
    - glob
    - grep
    - web_fetch
  denied_servers:
    - shell_execution_unrestricted
    - cloud_infrastructure
    - database_write
```

The `denied_servers` list is enforced by the MCP governance layer. See [patterns/mcp-governance.md](../patterns/mcp-governance.md) for the enforcement implementation.

### ceiling

The maximum confidence score this agent may report. Overrides the framework default when set.

```yaml
ceiling:
  confidence_max: 85               # Default: 85. Range: 80–95.
  rationale: Default ceiling per ADR-003. Prevents automation bias from AI approval chains.
```

See [docs/adr/ADR-003-85-percent-confidence-ceiling.md](adr/ADR-003-85-percent-confidence-ceiling.md) for the rationale for the 85% default.

### owner

Names the human or team accountable for this agent's behavior.

```yaml
owner:
  name: Engineering Team
  contact: engineering@example.com
  review_date: 2025-06-01          # Next scheduled registry review
  approved_by: Lead Engineer
  approval_date: 2025-01-15
```

The owner is responsible for reviewing the agent's scope and permissions at least quarterly and for updating the registry when the agent's access requirements change.

---

## Complete Example Entry

```yaml
agents:
  - identity:
      id: claude-code-primary
      name: Claude Code
      model: claude-sonnet-4-6
      provider: Anthropic
      purpose: General-purpose coding assistant for feature development, review, and documentation
    scope:
      repos: ["*"]
      branches: ["feature/*", "fix/*", "docs/*", "refactor/*", "test/*"]
      environments: [development, staging]
      excluded_paths: [".env", "*.pem", "secrets/"]
    permissions:
      read: ["**/*"]
      write: ["src/**/*", "tests/**/*", "docs/**/*", "CHANGELOG.md", "MEMORY.md"]
      execute:
        bash_commands: user_approved_only
      denied: ["*.env", "*.pem", ".git/config"]
    tools:
      mcp_servers:
        - name: filesystem
          access: read_write
          paths: ["./"]
        - name: github_api
          access: read_write
          scope: [issues, pull_requests, commits]
      native_tools: [bash, glob, grep, web_fetch]
      denied_servers: [shell_execution_unrestricted, cloud_infrastructure, database_write]
    ceiling:
      confidence_max: 85
    owner:
      name: Engineering Team
      contact: engineering@example.com
      review_date: 2025-06-01
```

---

## Unregistered Agent Protocol

If an agent operates, or attempts to operate, without a matching registry entry, the following protocol is mandatory. There are no exceptions.

### What triggers the protocol

- An agent identifies itself with an `id` not present in `AGENT_REGISTRY.md`
- An agent produces output but cannot be matched to any registry entry
- A CI/CD governance check detects an agent invocation with no corresponding registry entry
- A human reviewer notices an unregistered agent identity in session logs

### Response steps

1. **Halt the session immediately.** Do not continue work. Incomplete work from the session is not committed.

2. **Log the violation.** Append to `CHANGELOG.md`:
   ```
   VIOLATION | <timestamp> | Unregistered agent attempted session
   Agent ID:    <id or "unknown">
   Work scope:  <description of what the agent was doing>
   Halted by:   <who or what detected it>
   Resolution:  Pending registry entry
   ```

3. **Create a registry entry.** The agent's owner or the team lead drafts an entry following the schema above. The entry must be reviewed and approved before work resumes.

4. **Resume only after registry entry is committed.** The approved registry entry is committed to the repository. A new session starts with the registered agent.

### Severity

An unregistered agent is a Shadow Automation event. See [docs/known-failure-modes.md](known-failure-modes.md) failure mode 3 for the full context. The unregistered agent protocol is a Level 3 (Enforced) control.

---

## Integration with the Seven-Layer Stack

### Layer 1 — Constitution

`AGENT_REGISTRY.md` is a constitutional document. It is placed in the repository root alongside `CLAUDE.md` and is read at every session start. The session protocol in `CLAUDE.md` must reference the registry:

```markdown
## mandatory_session_protocol

on_session_start:
  1. Read AGENT_REGISTRY.md — confirm this agent is registered
  2. Verify your agent_id, scope, and tool allowlist match this session's context
  3. If not registered: halt and follow the unregistered agent protocol
```

### Layer 2 — Orchestration

The [master agent](../agents/master-agent.md) only orchestrates agents present in the registry. When decomposing a task, it assigns subtasks only to registered agent identities. An unregistered specialist agent cannot be invoked through orchestration.

### Layer 3 — Enforcement

Two enforcement mechanisms apply the registry:

**CI/CD gate:** A governance check runs on every PR that verifies no agent identity appears in session logs or commit metadata without a corresponding registry entry. The check fails the PR if a gap exists.

**MCP access control:** The MCP governance layer reads the registry's `tools.mcp_servers` and `tools.denied_servers` lists for the active agent before each tool call. See [patterns/agent-identity.md](../patterns/agent-identity.md) for the implementation pattern and [patterns/mcp-governance.md](../patterns/mcp-governance.md) for the MCP enforcement mechanism.

### Layer 4 — Observability

All agent actions are tagged with the `agent_id` from the registry entry. Session logs, `CHANGELOG.md` entries, and CI/CD audit records are queryable by agent identity. This enables post-incident investigation: given any commit or side effect, the responsible agent identity is traceable to its registry entry and owner.

### Layer 5 — Knowledge

The registry is versioned with the repository. Every change to an agent's scope, permissions, tools, or ceiling is a commit, with a timestamp and a diff. The commit history is the audit trail for agent access changes.

---

## Registry Maintenance

### When to update

- Any time a new agent is introduced to a project
- When an agent's model or version changes
- When an agent's scope or permissions change
- When the owner changes

### Quarterly review checklist

1. Compare the registry against active agent sessions from the last quarter
2. Identify agents in the registry that were never used — archive them
3. Identify agent identities in session logs without registry entries — create entries or open violations
4. Verify all `review_date` fields are within the past 12 months
5. Confirm all `owner.contact` values are current

### Archiving retired agents

Remove retired agents from the `agents:` list and move them to an `archived_agents:` section at the bottom of the file. Do not delete retired entries. The archive preserves the audit trail for past sessions.

---

## Related

- [templates/AGENT_REGISTRY.md](../templates/AGENT_REGISTRY.md) — copy-pasteable registry template with pre-filled entries for Claude Code, Copilot, and Cursor
- [patterns/agent-identity.md](../patterns/agent-identity.md) — governance pattern for enforcing agent identity at Level 1 (simple list), Level 3 (MCP-enforced), and Level 5 (automated provisioning)
- [patterns/mcp-governance.md](../patterns/mcp-governance.md) — MCP tool access enforcement that consumes the registry's tool allowlists
- [docs/known-failure-modes.md](known-failure-modes.md) — failure mode 3 (Shadow Automation) describes what the registry prevents
- [docs/adr/ADR-003-85-percent-confidence-ceiling.md](adr/ADR-003-85-percent-confidence-ceiling.md) — rationale for the 85% default confidence ceiling applied to all registered agents
