# MCP Governance: Controlling Agent-to-Tool Communication

## The MCP Governance Problem

Model Context Protocol (MCP) is a Linux Foundation standard that defines how AI agents communicate with external tools, services, and data sources. Over 10,000 MCP servers are publicly available, spanning file systems, databases, APIs, web scrapers, code execution environments, and cloud services. Every MCP connection is a governance boundary: a point where an agent transitions from generating text to taking real-world action.

Without MCP governance, an agent with access to a file system server, a shell execution server, and a database server can:

- Read and exfiltrate any file the process can access
- Execute arbitrary shell commands
- Query and modify production databases
- Chain these capabilities in ways no single tool policy anticipated

The failure mode is not malice — it is obedience. An agent tasked with "helping debug the production issue" will use every tool available to do so. If the agent has write access to production infrastructure, it will modify production infrastructure. The governance question is not whether to allow MCP — it is how to constrain which servers, which capabilities, and which environments an agent can access, and how to audit what it did.

**MCP governance is Layer 3 enforcement applied to the agent's tool surface.** The same principles that govern code changes — least privilege, deterministic gates, audit trails — apply to MCP connections. The difference is that MCP actions happen in real time, with real-world side effects, at AI speed.

---

## MCP in the 7-Layer Stack

MCP governance does not require a new layer. It is Layer 3 (Enforcement) applied to tool access. Each layer has a role:

| Layer | MCP Responsibility |
|-------|-------------------|
| **1. Constitution** | Declare which MCP servers are permitted. Enumerate forbidden server categories. |
| **2. Orchestration** | Confirm MCP server scope at session start. Restrict tools to session-declared scope. |
| **3. Enforcement** | Validate server permissions before each call. Block unauthorized connections. Enforce rate limits. Write audit log. |
| **4. Observability** | Log every MCP call: server, tool, arguments, result summary, timestamp. |
| **5. Knowledge** | Document MCP server capabilities, known risks, and past incidents in ADRs. |
| **6. Team Governance** | Role-based MCP access: different agent roles get different server sets. |
| **7. Evolution** | Review MCP server allowlist quarterly. Remove unused servers. Tighten scopes based on incident data. |

The enforcement boundary in Layer 3 is where MCP governance has the most leverage: before the agent calls a tool, a governance check determines whether that call is permitted. After the call, the audit log captures what happened.

---

## The Six MCP Governance Patterns

### Pattern 1: Least-Privilege Server Access

**Problem:** Agents given access to all available MCP servers will use them, often in combinations that amplify risk. A code-writing agent does not need database write access. A documentation agent does not need shell execution. Granting broad access because it is convenient creates a large blast radius for any agent error.

**Solution:** Define an explicit allowlist per agent role. Agents receive only the servers required for their declared task. Default is no access; access is granted explicitly and scoped to the minimum required.

**CLAUDE.md implementation:**

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

**Enforcement:** At session start, validate that the agent's active MCP configuration matches its declared role. Unauthorized server connections trigger the MCP kill switch immediately.

---

### Pattern 2: MCP Kill Switch

**Problem:** An agent operating through MCP can take real-world actions — write files, execute commands, call APIs, modify databases — faster than a human can review. A runaway agent session with tool access can cause significant damage before it is detected.

**Solution:** Define specific triggers that halt all MCP calls immediately. The kill switch for MCP is stricter than the standard session kill switch because MCP actions are irreversible in ways that text generation is not.

**Kill switch triggers for MCP sessions:**

```markdown
## mcp_kill_switch

Immediately halt ALL MCP server calls and present a kill switch alert if:

1. UNAUTHORIZED SERVER
   You have connected to or attempted to connect to a server not in your role allowlist.

2. WRITE OPERATION IN READ SESSION
   You have executed a write operation when session scope is declared read-only.

3. PRODUCTION ENVIRONMENT DETECTED
   You have connected to a server whose URL contains: prod, production, live, main.
   This requires explicit human authorization — not assumed from session context.

4. RATE LIMIT HIT
   You have reached the global or per-server call limit for this session.
   Pause, present a summary of calls made so far, and wait for instruction.

5. LARGE DATA RETURN
   A tool returned more than 1MB of data without prior declaration in the session scope.
   Do not process large, undeclared data volumes without human awareness.

6. CASCADE WRITE CHAIN
   You have made 3 or more consecutive write operations across different resources.
   Stop and confirm the chain was intended before continuing.

When any trigger fires:
1. STOP — halt all MCP calls immediately
2. Present: which trigger fired, the last 3 tool calls with arguments and outcomes
3. Wait — do not proceed until the human explicitly instructs continuation
```

---

### Pattern 3: Sandbox and Isolation

**Problem:** MCP server configurations that work in development should not reach production. An agent testing against a local database should not be able to reach production data. Shared MCP configurations create implicit trust across environments that governance should make explicit and enforced.

**Solution:** Separate MCP server configurations by environment. Agents in development mode connect only to development-scoped servers. Production access requires a separate, human-authorized allowlist that is never active during standard development sessions.

**Environment-segregated configuration:**

```yaml
# .claude/mcp-config.yaml

environments:
  development:
    allowed_servers:
      - name: local_filesystem
        path: ./
        permissions: read_write
      - name: local_database
        url: postgresql://localhost:5432/dev_db
        permissions: read_write
    forbidden_patterns:
      - "*prod*"
      - "*production*"
      - "*live*"

  staging:
    allowed_servers:
      - name: staging_filesystem
        path: ./
        permissions: read_only
      - name: staging_database
        url: postgresql://staging-db.internal:5432/staging_db
        permissions: read_only
    forbidden_patterns:
      - "*prod*"
      - "*live*"

  production:
    access: explicit_human_authorization_required
    allowed_servers: []
    note: "No agent may connect to production MCP servers without documented authorization and a bounded time window."
```

**Sandbox enforcement in CLAUDE.md:**

```markdown
## mcp_environment_rule

Before any MCP server connection:
1. Identify the current environment from: CLAUDE.md > MCP_ENV variable > default=development
2. Load the allowed server list for this environment from .claude/mcp-config.yaml
3. If any server URL matches a forbidden pattern: STOP and report the conflict
4. Log the environment determination before proceeding with any tool call

You may never connect to a production MCP server during a standard development session.
Production access requires: human-initiated session, documented reason, and time-bounded authorization.
```

---

### Pattern 4: Audit Logging

**Problem:** MCP actions leave no inherent audit trail. An agent that calls a database query tool, a file write tool, and a shell execution tool in the same session leaves no record of what was queried, what was written, or what was executed — unless audit logging is explicitly implemented.

**Solution:** Log every MCP tool call before execution and its result after. The log is append-only, written to a session-scoped file, and reviewed at session end before any commit.

**Audit log format:**

```
MCP_AUDIT | 2026-03-01T14:23:01Z | session=042 | server=github_api | tool=create_pr |
  args={title: "feat: MCP governance", base: "main", head: "feature/mcp"} |
  result=PR#847 created | duration_ms=342 | status=success

MCP_AUDIT | 2026-03-01T14:23:15Z | session=042 | server=filesystem | tool=write_file |
  args={path: "docs/mcp-governance.md", bytes: 4821} |
  result=written | duration_ms=12 | status=success

MCP_AUDIT | 2026-03-01T14:24:03Z | session=042 | server=database | tool=query |
  args={query: "SELECT count(*) FROM users WHERE created_at > '2026-03-01'"} |
  result=rows_returned=1 | duration_ms=87 | status=success
```

**CLAUDE.md implementation:**

```markdown
## mcp_audit_log

Before every MCP tool call:
1. Write INTENT: timestamp | server | tool | arguments summary
2. Execute the tool call
3. Write RESULT: outcome | duration_ms | status (success/fail/blocked)
4. If the call fails: write the error. Do NOT retry automatically.

At session end:
- Present the complete MCP call log for human review
- The log must be acknowledged before any governance commit
- If any call shows status=fail, explain what was attempted and why it failed
```

**CI/CD check:** Verify that every session commit includes an MCP audit log entry if MCP servers were active during the session. A commit with MCP tool calls and no audit log is a governance violation.

---

### Pattern 5: Environment Segregation

**Problem:** Developers frequently use the same agent configuration across local development, CI/CD pipelines, and production debugging. Without explicit environment gates, a session intended for development can reach staging or production infrastructure through misconfigured or permissive MCP server definitions.

**Solution:** Define environment gates that validate MCP server configurations at session start against the declared environment. The check is deterministic and runs before any tool call.

**Implementation in session protocol:**

```markdown
## mcp_environment_gate (runs at every session start, before any tool call)

1. Read declared environment from: CLAUDE.md > environment variable MCP_ENV > default=development
2. Load allowed servers for this environment from .claude/mcp-config.yaml
3. Verify each configured MCP server against the allowlist
4. If any configured server is not in the allowlist: HALT session start, report the conflict
5. If any configured server URL matches a forbidden pattern: HALT, report the violation
6. Log: "MCP environment gate passed: environment=[env], servers=[list], timestamp=[ts]"

Do not proceed with any work until the environment gate passes.
```

**Pre-session environment gate check (bash):**

```bash
#!/usr/bin/env bash
# scripts/mcp_environment_check.sh — run before agent session in CI or local dev

MCP_ENV="${MCP_ENV:-development}"
CONFIG_FILE=".claude/mcp-config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: $CONFIG_FILE not found. MCP governance requires an environment configuration."
  exit 1
fi

# Extract forbidden patterns for declared environment
FORBIDDEN=$(python3 -c "
import yaml, sys
with open('$CONFIG_FILE') as f:
    config = yaml.safe_load(f)
env = config.get('environments', {}).get('$MCP_ENV', {})
print('\n'.join(env.get('forbidden_patterns', [])))
")

echo "MCP environment gate: $MCP_ENV"
echo "Forbidden patterns: $FORBIDDEN"
echo "Environment gate passed."
```

---

### Pattern 6: Rate Limiting

**Problem:** An agent with MCP access can make thousands of tool calls in a single session. A runaway loop, an error cascade, or a misunderstood task can exhaust API quotas, overload databases, generate excessive costs, and create noise in production systems — all within minutes.

**Solution:** Define call rate limits per server per session, and per session overall. When limits are approached, the agent pauses and reports. When limits are hit, the agent stops completely.

**Rate limit configuration:**

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

**Agent behavior at rate limit approach (80% threshold):**

```
MCP RATE LIMIT ALERT

Current session: 161/200 total calls (81% — past pause threshold)
Server breakdown:
  github_api:   42/50 calls (84%)
  filesystem:   119/200 reads (60%)

Remaining planned work:
  - 3 documentation files to write (filesystem)
  - 1 PR to create (github_api)

Recommendation: Complete the documentation writes first (filesystem has headroom),
then pause before the PR (github_api is at 84% of limit).
Estimated additional calls: 6.

Proceed? [y/n]
```

---

## Unleash Example: Feature-Flag-Driven MCP Governance

[Unleash](https://www.getunleash.io/) is an open-source feature flag platform. Applied to MCP governance, it enables dynamic, real-time control over which MCP servers are active — without redeploying agents or modifying configuration files. This solves the kill switch activation problem: a feature flag toggle takes effect immediately for all running sessions.

**The governance model:** MCP server access is controlled by feature flags. Flags evaluate per environment, per agent role, and per time window. A production incident disables a specific MCP server globally in seconds, without touching agent configurations or requiring a deployment.

**Integration:**

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

def get_permitted_servers(agent_role: str, environment: str) -> list[str]:
    context = {"agent_id": agent_role, "env": environment}
    return [s for s in MCP_SERVER_FLAGS if is_server_permitted(s, context)]
```

**Real-time kill switch via flag toggle:**

When a production incident involves an MCP server, a single flag toggle in the Unleash dashboard disables that server for all agents immediately:

```
# Incident response action in Unleash dashboard:
mcp.filesystem.write → DISABLED (globally, all environments)

# All running agent sessions receive at next MCP call attempt:
MCP_KILL_SWITCH: mcp.filesystem.write disabled by governance flag
Reason: Production incident — filesystem write suspended pending investigation
Affected sessions: all
Time: 2026-03-01T16:42:00Z
Status: Halted — awaiting re-enable from governance team
```

**Environment-scoped access via Unleash strategies:**

```
Flag: mcp.database.write

Production strategy:
  enabled: false
  reason: No agent writes to production database via MCP without manual authorization

Staging strategy:
  enabled: true
  constraints:
    - context_field: userId
      operator: IN
      values: [database_agent, master_agent]

Development strategy:
  enabled: true
  constraints: []
```

**Why Unleash fits MCP governance:**

- Real-time kill switch without code changes or deployments
- Environment-aware: flags evaluate differently per environment
- Role-aware: flags evaluate differently per agent role via context constraints
- Gradual rollout: enable a new MCP server for one agent role before all agents
- Audit log: every flag evaluation is logged with timestamp, context, and result
- Open source: self-hosted or cloud, no vendor lock-in

Any feature flag system that supports environment context and real-time evaluation is a suitable substitute. Unleash is used here as a concrete, production-ready reference implementation.

---

## Implementation Checklist

### Minimum (Level 3 MCP compliance)

- [ ] MCP allowlist defined in `CLAUDE.md` per agent role, default: deny
- [ ] Forbidden server categories explicitly named (shell execution, production databases)
- [ ] Environment segregation: separate server lists for development, staging, production
- [ ] Production access blocked by default — requires explicit per-session authorization
- [ ] MCP kill switch triggers defined and included in session kill switch protocol
- [ ] Audit logging active: every MCP call logged with intent and result before committing

### Full (Level 4-5 MCP compliance)

- [ ] Rate limits configured: global per-session, per-server, with pause threshold
- [ ] Feature-flag-based kill switch (Unleash or equivalent) for zero-deployment disable
- [ ] MCP audit logs reviewed and acknowledged at session end before governance commit
- [ ] CI/CD validates MCP config against declared environment on every PR
- [ ] Quarterly review of MCP allowlist: remove unused servers, downgrade write to read-only
- [ ] Incident response protocol covers MCP server compromise: flag disable, audit review, root cause
- [ ] MCP API call counts tracked in COST_LOG.md for external services with per-call billing

---

## Common Mistakes

**Granting broad access for convenience.** Giving an agent access to all available MCP servers because "it might need them" is equivalent to giving a new employee root access to all production systems. Default to no access. Add servers explicitly when the need is demonstrated.

**Shared MCP configurations across environments.** A configuration file that works in development should not point to production servers. Environment segregation must be enforced by the configuration structure — not by developer discipline.

**No audit log for MCP sessions.** "The agent shouldn't have done anything harmful" is not a governance posture. An audit log of every MCP call is required to answer post-session questions about what the agent actually did and why.

**Kill switch that requires a code change to activate.** A kill switch that requires editing a config file, committing, and deploying is not available during an active incident. Use a feature flag system (Unleash or equivalent) for real-time, zero-deployment kills.

**Rate limits treated as guidelines.** Rate limits that the agent can reason around ("this call is important so I'll make it even though I'm near the limit") are not limits — they are suggestions. Rate limits must be hard stops enforced before the call is made, not negotiated in context.

**Treating MCP audit logs as optional documentation.** The audit log is not documentation for humans. It is the evidence base for every post-session governance review. A session that used MCP servers without an audit log is ungoverned, regardless of what the agent says it did.

---

*Related: [patterns/mcp-governance.md](../patterns/mcp-governance.md) | [patterns/kill-switch.md](../patterns/kill-switch.md) | [patterns/blast-radius-control.md](../patterns/blast-radius-control.md) | [docs/security-guide.md](security-guide.md)*
