# Pattern: MCP Governance

## Problem

Model Context Protocol (MCP) connects AI agents to real-world tools: file systems, databases, APIs, shell execution environments, and cloud infrastructure. Unlike text generation, MCP calls produce real-world side effects — files are written, commands are executed, API calls are billed, database records are modified — at AI speed and with AI volume.

Without governance, an agent with MCP access operates with an unconstrained blast radius. The agent does not distinguish between "allowed to help" and "allowed to do anything that helps." If a filesystem server is configured, the agent reads any file it can reach. If a shell execution server is available, the agent runs commands. If a database server is connected without write restrictions, the agent may modify records it should only query. Each decision is individually reasonable. The aggregate is uncontrolled.

The failure mode is not adversarial. It is obedient. The agent does exactly what it is instructed, using every tool available, faster than any human can review.

## Solution

Treat MCP access as a governance boundary, not a configuration detail. Apply least-privilege principles to server access, define kill switch triggers specific to tool calls, isolate environments explicitly, log every tool call before and after execution, enforce rate limits per server and per session, and implement a real-time kill switch that does not require a deployment to activate.

The governance model for MCP mirrors the governance model for code:

- **What is permitted:** defined in advance, per role, per environment
- **What is monitored:** every call, with arguments and outcomes logged
- **What stops the session:** specific triggers that fire before damage accumulates
- **What contains the damage:** per-session and per-server call limits
- **What separates environments:** configuration that makes production unreachable by default

## When to Use

Apply MCP governance whenever an agent has access to one or more MCP servers in a session where:

- The server can write to any persistent storage (files, databases, external APIs)
- The server can execute code or shell commands
- The server connects to external services that have costs or rate limits
- The environment includes staging or production servers
- Multiple agents share access to the same servers

## When NOT to Use

- Read-only, local-only MCP servers with no external effects or costs. Apply a minimum allowlist and call logging even here — the pattern overhead is negligible.
- Pure analysis sessions where MCP provides only read-access context. Apply the allowlist and audit log; skip rate limits if volume is bounded by task definition.

## Implementation

### Step 1: Define the allowlist in CLAUDE.md

```yaml
mcp_access:
  default: deny

  roles:
    code_agent:
      allowed_servers: [filesystem_read_only, github_api]
      forbidden_servers: [shell_execution, database_write, cloud_infrastructure]

    documentation_agent:
      allowed_servers: [filesystem_read_only, github_api]
      forbidden_servers: [shell_execution, database_write, cloud_infrastructure]

    database_agent:
      allowed_servers: [database_read_only]
      forbidden_servers: [shell_execution, filesystem_write, cloud_infrastructure]
```

### Step 2: Add MCP kill switch triggers

Add to your CLAUDE.md `kill_switch` section:

```markdown
## mcp_kill_switch

Halt ALL MCP calls and present a kill switch alert if ANY of these trigger:

1. UNAUTHORIZED SERVER — attempted connection to a server not in the role allowlist
2. WRITE IN READ SESSION — write operation attempted when session is declared read-only
3. PRODUCTION DETECTED — server URL contains: prod, production, live (requires explicit authorization)
4. RATE LIMIT HIT — global or per-server call limit for this session has been reached
5. CASCADE WRITE — 3 or more consecutive write operations across different resources
6. LARGE DATA RETURN — tool returned more than 1MB of data without prior declaration in scope

When triggered: stop all tool calls, present the complete audit log to date,
wait for explicit human instruction before resuming.
```

### Step 3: Separate environment configurations

Create `.claude/mcp-config.yaml` with per-environment server lists:

```yaml
environments:
  development:
    allowed_servers:
      - name: local_filesystem
        path: ./
        permissions: read_write
      - name: local_database
        url: postgresql://localhost:5432/dev_db
        permissions: read_write
    forbidden_patterns: ["*prod*", "*production*", "*live*"]

  staging:
    allowed_servers:
      - name: staging_filesystem
        path: ./
        permissions: read_only
      - name: staging_database
        url: postgresql://staging-db.internal:5432/staging_db
        permissions: read_only
    forbidden_patterns: ["*prod*", "*live*"]

  production:
    access: explicit_human_authorization_required
    allowed_servers: []
```

### Step 4: Configure rate limits

```yaml
# .claude/mcp-config.yaml

rate_limits:
  global:
    max_calls_per_session: 200
    max_calls_per_minute: 30
    pause_at_percent: 80

  per_server:
    github_api:
      max_calls_per_session: 50
      max_calls_per_minute: 10
    filesystem:
      max_write_calls_per_session: 30
      max_read_calls_per_session: 200
    database_read_only:
      max_calls_per_session: 100
      max_rows_returned: 10000
    shell_execution:
      max_calls_per_session: 20
      max_execution_time_seconds: 30
```

### Step 5: Enable audit logging

Add to CLAUDE.md:

```markdown
## mcp_audit_log

Before every MCP tool call:
1. Write INTENT entry: timestamp | server | tool | arguments summary
2. Execute the call
3. Write RESULT entry: outcome | duration_ms | status (success/fail/blocked)
4. If the call fails: write the error. Do NOT retry automatically.

At session end: present the complete MCP call log for human review.
The log must be acknowledged before any governance commit.
```

### Step 6: Implement a real-time kill switch

Use a feature flag system so that any MCP server can be disabled instantly across all running sessions without a deployment. Unleash (open source, self-hostable) is a production-ready option:

```python
# scripts/mcp_governance_check.py
from UnleashClient import UnleashClient

client = UnleashClient(
    url="https://unleash.internal.company.com/api",
    app_name="ai-governance-framework",
    environment="development"
)
client.initialize_client()

MCP_SERVER_FLAGS = {
    "filesystem_write":     "mcp.filesystem.write",
    "shell_execution":      "mcp.shell.execute",
    "database_write":       "mcp.database.write",
    "github_api":           "mcp.github.api",
    "cloud_infrastructure": "mcp.cloud.infra",
}

def is_server_permitted(server_name: str, context: dict) -> bool:
    flag_name = MCP_SERVER_FLAGS.get(server_name)
    if not flag_name:
        return False  # Unknown servers denied by default
    return client.is_enabled(
        flag_name,
        context={"userId": context.get("agent_id"), "environment": context.get("env")}
    )
```

A toggle in the feature flag dashboard immediately stops all sessions from accessing the disabled server — no deployment, no config change, no agent restart required. See [docs/mcp-governance.md](../docs/mcp-governance.md) for the complete Unleash integration and environment-scoped flag strategy.

## Anti-Patterns

**MCP allowlist that is never reviewed.** An allowlist that grows over time without pruning becomes a list of everything. Review MCP access quarterly. Remove servers that agents no longer need. Downgrade write to read-only when write access is no longer required.

**Shared configuration across environments.** A single MCP config file that works in development and production is a production access risk. Environment segregation must be structural — enforced by the configuration — not conventional.

**Kill switch that requires a deployment.** A kill switch activated by editing a file, committing, and deploying is unavailable during an active incident. The kill switch must be reachable within seconds, without touching the codebase.

**No audit log during production debugging sessions.** Production access without a complete tool call log is an uncontrolled situation. If logs are not being written, the session should not proceed.

**Rate limits as guidelines.** Rate limits that the agent can reason its way around ("this call is important but I'm near the limit") are not limits. They are suggestions. Rate limits must be hard stops enforced before the call is made.

**Treating MCP audit logs as optional.** The audit log is the evidence base for every post-session governance review. A session that used MCP servers without an audit log is ungoverned, regardless of what the agent reports it did.

## Related Patterns

- [docs/mcp-governance.md](../docs/mcp-governance.md) — complete MCP governance specification with Unleash example and implementation checklist
- [patterns/agent-identity.md](agent-identity.md) — agent identity enforcement that defines which MCP servers each registered agent is authorized to access; MCP governance enforces the per-agent tool allowlist declared in AGENT_REGISTRY.md
- [docs/agent-registry.md](../docs/agent-registry.md) — registry schema for `tools.mcp_servers` and `tools.denied_servers` that MCP governance reads per agent before each tool call
- [patterns/kill-switch.md](kill-switch.md) — session-level kill switch; MCP kill switch extends trigger 3 (blast radius) with tool-specific triggers
- [patterns/blast-radius-control.md](blast-radius-control.md) — MCP rate limits and call limits are blast radius control applied to tool access
- [patterns/context-boundaries.md](context-boundaries.md) — controls what the agent can read; MCP governance controls what it can do
- [docs/security-guide.md](../docs/security-guide.md) — MCP servers as an extended security surface; audit logging and environment segregation connect to Layer 3 enforcement
