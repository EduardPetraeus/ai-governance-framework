# Pattern: Agent Identity

## Problem

Agents operate without declared identities. A session produces code, commits, and side effects, but there is no record of which agent was running, what scope it was granted, or who authorized it. When something goes wrong — a production write, an unexpected file, a secret in a commit — there is no identity to trace it to and no scope definition to compare it against.

This is not a failure of the agent. It is a failure of the governance layer that allowed an anonymous process to operate with real-world effects.

The problem compounds in multi-agent systems. A master agent orchestrates a code-generation agent, which invokes an MCP server for database access. Three agents have operated. None of them declared an identity. The audit trail shows tool calls without actors.

## Solution

Require every agent to declare an identity before operating. Store identities in a structured registry that specifies scope, permissions, tool allowlist, confidence ceiling, and owner. Enforce the registry at the boundaries where agents interact with the real world: session start, tool invocation, and CI/CD gates.

An agent without a registry entry is not an unregistered configuration — it is a violation. Treat it as one.

## When to Use

Apply this pattern whenever:

- More than one agent type operates on the same codebase (even sequentially, not concurrently)
- Any agent has access to MCP servers, shell execution, or external APIs
- Commits or side effects must be traceable to a specific agent and owner
- The team is at Level 2 maturity or above and has introduced cross-session memory or agent orchestration

## When NOT to Use

- Single-developer, single-agent projects where one person directly supervises every session. A minimal declaration (agent name and model in CLAUDE.md) is still good practice but a full registry adds friction without proportional benefit at Level 1.

At Level 1, use the lightweight CLAUDE.md declaration described below. Introduce the full registry when you have more than one agent type or when unattended sessions begin.

## Implementation

### Level 1 — Foundation

**What you need:** A declaration in `CLAUDE.md` and a session-start check. No infrastructure required.

Add to `CLAUDE.md`:

```yaml
agent_identity:
  id: claude-code-primary
  name: Claude Code
  model: claude-sonnet-4-6
  provider: Anthropic
  ceiling: 85
  owner: Engineering Team

  session_start_check:
    - Confirm this session's agent matches the identity declared above
    - Confirm scope matches: no production access, no CI/CD modification without explicit authorization
    - If identity cannot be confirmed: halt and request human review before proceeding
```

Add to `mandatory_session_protocol`:

```markdown
on_session_start:
  1. Declare agent identity: confirm id, model, and provider match agent_identity above
  2. Confirm scope: verify the task falls within declared scope boundaries
  3. If not registered: halt. Do not proceed. See docs/agent-registry.md for the violation protocol.
```

**Maturity level:** Level 1 and above. The minimum viable identity declaration is one YAML block in `CLAUDE.md`. It costs nothing to implement and creates the habit of declared identity.

---

### Level 3 — MCP-Enforced

**What you need:** `AGENT_REGISTRY.md` in the repository root, MCP governance checking registry entries before each tool call, and a CI/CD gate that rejects sessions without registry-backed identities.

**Step 1: Create AGENT_REGISTRY.md**

Copy `templates/AGENT_REGISTRY.md` to your repository root. Fill in actual owners and review dates. Remove agents you do not use. Do not leave placeholder values.

The registry is a constitutional document. It is read at every session start alongside `CLAUDE.md`.

**Step 2: MCP enforcement**

Extend the MCP governance kill switch to check agent identity before each tool call:

```yaml
## mcp_agent_identity_check

Before every MCP tool call:
1. Confirm the active agent_id is present in AGENT_REGISTRY.md
2. Confirm the requested server is in the agent's tools.mcp_servers allowlist
3. Confirm the requested server is not in the agent's tools.denied_servers list
4. If any check fails: block the call, log the attempt, halt the session

Log format:
  AGENT_IDENTITY_CHECK | <timestamp> | agent_id: <id> | server: <server_name> | result: <allowed/blocked>
```

**Step 3: CI/CD gate**

Add a governance check to your CI/CD pipeline that reads the registry and validates session metadata. A minimal GitHub Actions check:

```yaml
# .github/workflows/agent-registry-check.yml
name: Agent Registry Check

on: [push, pull_request]

jobs:
  check-registry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify AGENT_REGISTRY.md exists
        run: |
          if [ ! -f "AGENT_REGISTRY.md" ]; then
            echo "VIOLATION: AGENT_REGISTRY.md not found. All agents must be registered."
            exit 1
          fi

      - name: Check registry has at least one active agent
        run: |
          if ! grep -q "^  - identity:" AGENT_REGISTRY.md; then
            echo "VIOLATION: AGENT_REGISTRY.md contains no registered agents."
            exit 1
          fi

      - name: Verify required fields are present
        run: |
          for field in "id:" "name:" "model:" "provider:" "ceiling:" "owner:"; do
            if ! grep -q "$field" AGENT_REGISTRY.md; then
              echo "VIOLATION: Required field '$field' not found in AGENT_REGISTRY.md"
              exit 1
            fi
          done
          echo "Agent registry check passed."
```

**Step 4: Session protocol registry check**

Update `CLAUDE.md` session start to reference the registry:

```yaml
on_session_start:
  1. Read AGENT_REGISTRY.md — locate the entry matching this session's agent_id
  2. Confirm the active model and provider match the registry entry
  3. Confirm the task scope is within the registry entry's scope.branches and scope.environments
  4. Confirm all MCP servers requested exist in tools.mcp_servers (not in tools.denied_servers)
  5. If any check fails: halt. Log the mismatch. Do not begin work.
```

**Maturity level:** Level 3 (Enforced) and above. MCP-backed enforcement turns the registry from a governance document into a technical control.

---

### Level 5 — Automated Provisioning

**What you need:** CI/CD automation that provisions new agent identities on registry PR merge, validates scope consistency across registries, and runs quarterly agent inventory checks automatically.

**Step 1: Registry PR workflow**

New agents are never added directly to `AGENT_REGISTRY.md` by hand. Changes are made via PR and validated by the registry provisioning workflow:

```yaml
# .github/workflows/agent-provisioning.yml
name: Agent Provisioning

on:
  pull_request:
    paths:
      - "AGENT_REGISTRY.md"

jobs:
  validate-registry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate registry schema
        run: python3 scripts/validate_agent_registry.py AGENT_REGISTRY.md

      - name: Check for duplicate agent IDs
        run: python3 scripts/validate_agent_registry.py --check-duplicates AGENT_REGISTRY.md

      - name: Verify all owners have valid contacts
        run: python3 scripts/validate_agent_registry.py --check-owners AGENT_REGISTRY.md

      - name: Confirm confidence ceiling within allowed range
        run: python3 scripts/validate_agent_registry.py --check-ceiling --min 80 --max 95 AGENT_REGISTRY.md

      - name: Generate provisioning summary
        run: python3 scripts/validate_agent_registry.py --summary AGENT_REGISTRY.md
```

**Step 2: Quarterly agent inventory**

A scheduled workflow compares the registry against recent session logs and flags gaps:

```yaml
# .github/workflows/agent-inventory.yml
name: Quarterly Agent Inventory

on:
  schedule:
    - cron: "0 9 1 */3 *"   # First day of each quarter at 09:00 UTC
  workflow_dispatch:

jobs:
  inventory:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 90     # Last 90 days of commits

      - name: Run agent inventory
        run: python3 scripts/agent_inventory.py --days 90

      - name: Open issue if gaps found
        if: failure()
        run: |
          gh issue create \
            --title "Agent inventory gap: unregistered agents detected" \
            --body "$(cat inventory_report.txt)" \
            --label "governance,agent-registry"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Step 3: Cross-repository inheritance**

For organizations with multiple repositories, the org-level registry inherits into repo-level registries. Org-registered agents do not need to be re-declared per repo. Only repo-specific overrides (tighter scope, reduced permissions) are declared locally.

In `CLAUDE.org.md`:

```yaml
org_agent_registry:
  location: .github/AGENT_REGISTRY.org.md
  inheritance: all repos inherit org-registered agents
  override_policy: repos may restrict scope or permissions; repos may not expand them
  enforcement: registry-check workflow validates inheritance on every PR
```

**Maturity level:** Level 5 (Self-Optimizing). Automated provisioning removes the manual step of registry maintenance while maintaining full governance coverage.

---

## Anti-Patterns

**Registry as documentation, not enforcement.** A registry that agents can read but cannot be verified against is a record, not a control. At Level 3, the registry must be technically enforced — MCP calls fail if the agent is not registered.

**Shared agent IDs across environments.** Using the same `agent_id` in development and production makes it impossible to distinguish between a development session and a production session in audit logs. Use environment-scoped IDs: `claude-code-dev`, `claude-code-prod`.

**Registry entries created after work is done.** An agent that operates, then gets registered retrospectively, is an unregistered agent that was subsequently covered up. The registry entry must exist before the first session begins.

**Owners who are no longer on the team.** An agent entry with a departed owner is an agent with no accountable identity. Run the quarterly inventory. Update owners before they leave.

**Unlimited scope in all registry fields.** A registry entry that grants `repos: ["*"]`, `branches: ["*"]`, `environments: [development, staging, production]`, and `permissions.write: ["**/*"]` provides the same governance as no registry at all. Scope must be meaningful to be effective.

---

## Related Patterns

- [docs/agent-registry.md](../docs/agent-registry.md) — full registry specification: schema, violation protocol, and seven-layer integration
- [templates/AGENT_REGISTRY.md](../templates/AGENT_REGISTRY.md) — copy-pasteable template with pre-filled entries for Claude Code, Copilot, and Cursor
- [patterns/mcp-governance.md](mcp-governance.md) — MCP tool access enforcement; agent identity extends MCP governance by adding the agent as the authorization principal for every tool call
- [docs/known-failure-modes.md](../docs/known-failure-modes.md) — failure mode 3 (Shadow Automation) describes the class of failure this pattern prevents
- [patterns/blast-radius-control.md](blast-radius-control.md) — scope boundaries in the registry (repos, branches, environments, paths) are blast radius controls applied at the identity level
- [agents/master-agent.md](../agents/master-agent.md) — the master agent consults the registry when assigning tasks to specialist agents; only registered agents are orchestrated
