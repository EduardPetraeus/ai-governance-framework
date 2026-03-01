# AI Governance Risk Register

Copy this file to your project root or `docs/` directory. Update it quarterly or after any governance incident. Assign an owner to every row. Unowned risks are unmanaged risks.

---

## How to Use This Register

**Likelihood** — probability of this risk materializing in the next quarter:
- **Low** — unlikely given current controls; no prior occurrence
- **Medium** — plausible; has occurred in similar teams or occurred once here
- **High** — recurring pattern or active precondition present

**Impact** — consequence if the risk materializes without mitigation:
- **Low** — recoverable within a session; no production or compliance effect
- **Medium** — requires engineering effort to remediate; minor production or compliance effect
- **High** — data loss, security breach, production outage, or audit finding

**Risk Level** (derived):

| Likelihood ↓ / Impact → | Low | Medium | High |
|---|---|---|---|
| Low | Acceptable | Monitor | Mitigate |
| Medium | Monitor | Mitigate | Mitigate |
| High | Mitigate | Escalate | Escalate |

**Status:**
- **Open** — risk identified, control not yet implemented
- **In Progress** — control being implemented
- **Controlled** — control implemented and verified effective
- **Accepted** — risk accepted by Owner with documented rationale
- **Closed** — risk no longer applicable

---

## Risk Register

### 1. Speculative Code

| Field | Value |
|---|---|
| **Scenario** | Agent writes code for features outside confirmed scope, producing output that is architecturally incompatible with actual requirements and must be discarded. |
| **Likelihood** | High |
| **Impact** | Medium |
| **Risk Level** | Escalate |
| **Control** | Enforce output contracts before any code generation ([patterns/output-contracts.md](../patterns/output-contracts.md)); require scope confirmation in session protocol. |
| **Owner** | AI Steward |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | First occurrence at Level 0. Controllable at Level 2 with output contracts and human-in-the-loop scope confirmation. |

---

### 2. Architectural Drift

| Field | Value |
|---|---|
| **Scenario** | Small per-session architectural deviations accumulate until the codebase diverges from ARCHITECTURE.md. Subsequent agents read the document and produce code that conflicts with the actual system. |
| **Likelihood** | Medium |
| **Impact** | High |
| **Risk Level** | Escalate |
| **Control** | Run drift detector agent at session start; enforce governance sync check; use blast radius control to limit cross-layer changes per session ([patterns/blast-radius-control.md](../patterns/blast-radius-control.md)). |
| **Owner** | AI Steward |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Emerges at Level 1; first controllable at Level 3 with mandatory drift detection. |

---

### 3. Shadow Automation

| Field | Value |
|---|---|
| **Scenario** | Agent invokes MCP tools or external integrations that produce side effects outside the governed session record — credentials stored in unexpected locations, data written to external services, cloud resources created without authorization. |
| **Likelihood** | Medium |
| **Impact** | High |
| **Risk Level** | Escalate |
| **Control** | Enforce MCP tool allowlists and audit logging ([patterns/mcp-governance.md](../patterns/mcp-governance.md)); require all agents to be registered in the agent registry ([docs/agent-registry.md](../docs/agent-registry.md)). |
| **Owner** | AI Owner |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Emerges at Level 3 when MCP integrations are introduced. Controlled at Level 4 with full audit logging. |

---

### 4. Context Window Overflow

| Field | Value |
|---|---|
| **Scenario** | Long sessions fill the context window with intermediate output and failed attempts. Late-session work contradicts early-session decisions that the agent can no longer see. Quality degrades invisibly. |
| **Likelihood** | High |
| **Impact** | Medium |
| **Risk Level** | Escalate |
| **Control** | Enforce session time limits and friction budget ([patterns/friction-budget.md](../patterns/friction-budget.md)); require status checkpoint every 3 tasks; use session replay for post-session verification ([patterns/session-replay.md](../patterns/session-replay.md)). |
| **Owner** | AI Operator |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Emerges at Level 0. Mitigated at Level 1 with session time limits and mandatory checkpoints. |

---

### 5. Governance Fatigue

| Field | Value |
|---|---|
| **Scenario** | Governance overhead grows until developers route around the framework. Shadow AI workflows emerge. Governance coverage drops while the framework remains comprehensive on paper. |
| **Likelihood** | Medium |
| **Impact** | High |
| **Risk Level** | Escalate |
| **Control** | Monitor friction ratio weekly (target ≤15%); enforce friction budget ([patterns/friction-budget.md](../patterns/friction-budget.md)); measure governance coverage; reduce ceremony when friction threshold is exceeded. |
| **Owner** | AI Steward |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Critical risk above Level 3. See [docs/governance-fatigue.md](../docs/governance-fatigue.md) for diagnostic criteria. |

---

### 6. Automation Bias

| Field | Value |
|---|---|
| **Scenario** | Multiple AI validation layers approve a PR. Human reviewer sees green checkmarks and reduces scrutiny. Business logic errors that AI cannot detect ship to production. |
| **Likelihood** | Medium |
| **Impact** | High |
| **Risk Level** | Escalate |
| **Control** | Set confidence ceiling at 85% (configurable) to prevent all-green signals; require AI reviewers to label what they did NOT verify ([patterns/automation-bias-defense.md](../patterns/automation-bias-defense.md)); train team on automation bias. |
| **Owner** | AI Steward |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Emerges at Level 3 when validation layers multiply. Controlled at Level 4. See [docs/automation-bias.md](../docs/automation-bias.md). |

---

### 7. Knowledge Rot

| Field | Value |
|---|---|
| **Scenario** | MEMORY.md accumulates stale entries from reversed decisions. Agent reads both current and outdated entries, applies the wrong pattern with full confidence, and produces code that fails at runtime. |
| **Likelihood** | Medium |
| **Impact** | Medium |
| **Risk Level** | Mitigate |
| **Control** | Assign TTL values to memory entries ([patterns/knowledge-decay.md](../patterns/knowledge-decay.md)); run drift detector against MEMORY.md quarterly; require session-start lifecycle check before work begins. |
| **Owner** | AI Operator |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Detectable at Level 2. Controlled at Level 4 with automated lifecycle tooling. |

---

### 8. Credential Exposure

| Field | Value |
|---|---|
| **Scenario** | Agent includes API keys, tokens, connection strings, or internal hostnames in committed files, documentation, or logs. |
| **Likelihood** | Low |
| **Impact** | High |
| **Risk Level** | Mitigate |
| **Control** | Pre-commit hook blocks secrets before commit ([scripts/hooks/pre_commit_guard.sh](../scripts/hooks/pre_commit_guard.sh)); AI security reviewer scans every diff ([agents/security-reviewer.md](../agents/security-reviewer.md)); CI/CD governance check rejects ungoverned changes. |
| **Owner** | AI Steward |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Controlled at Level 3 with pre-commit enforcement. See [docs/security-guide.md](../docs/security-guide.md). |

---

### 9. Scope Creep

| Field | Value |
|---|---|
| **Scenario** | Agent expands work beyond the session plan — adding unrequested features, touching files outside confirmed scope, or making architectural changes without documentation. |
| **Likelihood** | High |
| **Impact** | Medium |
| **Risk Level** | Escalate |
| **Control** | Enforce blast radius limit (max 15 files, 200 lines per file by default) ([patterns/blast-radius-control.md](../patterns/blast-radius-control.md)); require output contracts before work begins; human-in-the-loop approval for any file not in the confirmed scope. |
| **Owner** | AI Operator |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Most common failure at Level 0–1. Controllable at Level 2. |

---

### 10. Compliance Gap

| Field | Value |
|---|---|
| **Scenario** | AI-generated output creates a regulatory obligation (data processing, AI Act classification, security certification) that the team is unaware of and does not document. |
| **Likelihood** | Low |
| **Impact** | High |
| **Risk Level** | Mitigate |
| **Control** | Map framework elements to applicable regulations ([docs/compliance-mapping.md](../docs/compliance-mapping.md)); include compliance check in quarterly governance review; assign AI Auditor role. |
| **Owner** | AI Owner |
| **Status** | Open |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | Highest risk for teams operating under EU AI Act, ISO 42001, or SOC 2 obligations. |

---

## Adding New Risks

Copy the template below and add it as a new numbered section:

```markdown
### N. [Risk Name]

| Field | Value |
|---|---|
| **Scenario** | [One sentence: what goes wrong and what the consequence is] |
| **Likelihood** | Low / Medium / High |
| **Impact** | Low / Medium / High |
| **Risk Level** | Acceptable / Monitor / Mitigate / Escalate |
| **Control** | [What prevents or detects this risk — link to relevant pattern or doc] |
| **Owner** | [AI Owner / AI Steward / AI Operator / AI Auditor] |
| **Status** | Open / In Progress / Controlled / Accepted / Closed |
| **Last Reviewed** | YYYY-MM-DD |
| **Notes** | [Maturity level context, trigger conditions, or exceptions] |
```

---

## Related

- [Governance for leaders](../docs/governance-for-leaders.md) — roles, metrics, and quarterly checklist
- [Known failure modes](../docs/known-failure-modes.md) — detailed analysis of the seven core failure patterns
- [Compliance mapping](../docs/compliance-mapping.md) — framework controls mapped to NIST AI RMF, ISO 42001, EU AI Act
- [Operator playbook](../patterns/operator-playbook.md) — response procedures for incidents identified in this register
