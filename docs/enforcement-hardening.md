# Enforcement Hardening

_From governance by agreement to governance by constraint._

ChatGPT's framing — "governance by agreement, not constraint" — describes how most AI governance
frameworks actually operate: the agent agrees to follow rules because a human told it to, and
compliance persists only as long as context does. Agreement-based governance works until deadline
pressure, long sessions, complex multi-step tasks, or model updates cause drift. By then,
ungoverned changes are already in the codebase.

This document defines three levels of enforcement hardening, how to make each level
non-bypassable, and how to upgrade from one level to the next.

---

## Current State

The Core Edition provides agreement-based enforcement:

- `CLAUDE.md` sets rules. The agent reads them at session start.
- The governance-check CI workflow rejects PRs where source code changed but `CHANGELOG.md` was
  not updated.
- `CLAUDE.md` changes require a second reviewer.
- Pre-commit hooks block secrets and naming violations at commit time.

This is **Level 1** enforcement. It works for teams with consistent habits and short session
cadences. It does not work when agents operate autonomously, when sessions grow long, or when
multiple agents contribute to the same branch without a human in the loop.

---

## Level 1: Core Enforcement

**Target:** Solo developers and teams who want minimum viable enforcement. No additional
infrastructure required beyond GitHub Actions.

### What Is Enforced

| Gate | Mechanism | Blocking |
|------|-----------|---------|
| `CHANGELOG.md` updated with source code changes | `ci-cd/github-actions/governance-check.yml` | Yes |
| `CLAUDE.md` changes require second reviewer | `ci-cd/github-actions/governance-check.yml` | Advisory |
| Session file limit (max 15 files per session) | Pre-commit hook or PR check | Advisory |
| No secrets in commits | gitleaks / trufflehog pre-commit hook | Yes |

### Configuration

```yaml
# governance-check.yml is sufficient for L1
# Pre-commit hooks: ci-cd/pre-commit/.pre-commit-config.yaml
# File limit: checked by quality-gate-agent at session end
```

### What L1 Does Not Catch

- Agent output that violates architectural decisions without touching `ARCHITECTURE.md`
- Structured output metadata missing (confidence, `not_verified`, `architectural_impact`)
- Naming convention violations in file content (only catches file-level secrets)
- Output contract breaches not visible in the diff

---

## Level 2: Standard Enforcement

**Target:** Teams (5–20 developers) who run multiple agents or have established architecture
patterns that must not drift.

### What Is Added Over L1

| Gate | Mechanism | Blocking |
|------|-----------|---------|
| Structured output contract validation | `automation/output_contract_validator.py` in CI | Yes |
| Architecture linting (naming conventions, import boundaries) | Custom rules in CI | Yes |
| Output contract schema enforcement | JSON schema check on agent output files | Yes |
| Confidence ceiling enforcement | Validate `confidence` ≤ configured ceiling (default: 85) | Yes |
| `not_verified` field required | Output contract schema enforces field presence | Yes |

### The Key Addition: Structured Output Validation

Level 1 enforcement is structural — it checks that files were updated. Level 2 adds semantic
enforcement: it checks that agent output includes the metadata required to evaluate it. An agent
that produces code changes without declaring its confidence, what it did not verify, and what
architectural impact its changes have is producing ungoverned output — even if `CHANGELOG.md` was
updated.

See [patterns/structured-output-contracts.md](../patterns/structured-output-contracts.md) for
the standard schema and field definitions.

### CI Integration

```yaml
# Add to governance-check.yml or a dedicated validate-output.yml job
- name: Validate output contract
  if: hashFiles('output_contract.json') != ''
  run: |
    python automation/output_contract_validator.py output_contract.json \
      --confidence-ceiling 85
```

### Architecture Linting

Architecture linting validates that changes conform to structural rules that are too nuanced for
secret scanning but too important to leave to agent discretion:

- No cross-layer imports (e.g., UI code importing directly from data layer)
- File placement matches declared module boundaries in `ARCHITECTURE.md`
- Naming conventions match what is specified in `CLAUDE.md`

Implement as a Python script in `automation/` invoking `ast` or `importlib` to walk the import
graph, or as a `flake8` plugin if the stack supports it.

### What L2 Does Not Catch

- Runtime behavior that violates policies (agents with live tool access via MCP)
- Cross-session accumulation of small violations that individually pass checks
- Policy violations requiring knowledge of external systems (e.g., "this PR changes behavior X
  which is prohibited by policy Y")

---

## Level 3: Enterprise Enforcement

**Target:** Organizations with 50+ developers, compliance requirements, or agents with
real-world tool access (MCP, APIs, databases).

### What Is Added Over L2

| Gate | Mechanism | Blocking |
|------|-----------|---------|
| Policy engine (OPA / Cedar) | Evaluate PRs against formal policy rules | Yes |
| Runtime guardrails (MCP enforcement) | Allowlist, rate limits, audit log, kill switch | Yes |
| Governance health gate | `automation/health_score_calculator.py --threshold 60` | Yes |
| Constitutional inheritance validation | `automation/inherits_from_validator.py` | Yes |
| Compliance audit trail | Append-only session records with timestamps | Required |
| Agent registry enforcement | `docs/agent-registry.md` — no unregistered agents | Yes |

### Policy Engine Integration

At enterprise scale, CI scripts cannot encode all policy rules. Policies become complex
(role-based permissions, jurisdiction-specific requirements, business rules), they change faster
than CI workflows, and they need to apply consistently across dozens of repositories.

A policy engine decouples policy from enforcement mechanism:

```yaml
# Example: Open Policy Agent (OPA) integration
- name: Evaluate governance policy
  run: |
    opa eval \
      --data policies/ \
      --input pr_metadata.json \
      "data.governance.allow" \
      --fail
```

Policies live in `policies/` as `.rego` files. They are versioned, reviewed, and tested
independently from the CI workflow that invokes them. A compliance team can update policies
without touching CI configuration.

### Runtime Guardrails

When agents have tool access (via MCP), enforcement cannot be deferred to CI — changes happen
at the moment of tool execution. Runtime guardrails enforce constraints before the agent acts:

```
Before any MCP tool call:
  1. Is this server on the allowlist for this agent role?
  2. Has the per-session call limit been reached?
  3. Is this call within the declared session scope?
  4. Has a human confirmed high-impact actions?
```

See [patterns/mcp-governance.md](../patterns/mcp-governance.md) for the full specification.

### Governance Health Gate

The health score becomes a CI gate at Level 3. A PR cannot merge if it reduces the
repository's governance health score below the configured threshold:

```bash
python automation/health_score_calculator.py . --threshold 60
```

This prevents gradual governance decay through individually innocuous changes.

### Compliance Audit Trail

For ISO 42001 and EU AI Act compliance, session records must be:

- Append-only (no modification after commit)
- Timestamped with model ID, session identifier, and operator identity
- Retained per the organization's data retention policy
- Queryable: "what did the agent do in this session?" must have a deterministic answer

The `output_contract.json` plus CHANGELOG entry together satisfy this requirement when both are
committed per session and the git history is preserved.

### What L3 Does Not Catch

- Agent actions that comply with all formal rules but violate intent
- Adversarial governance manipulation (agent modifying its own rules through side channels)
- Governance gaps in the policy specification itself (mitigated by red-team audit — see
  [commands/audit.md](../commands/audit.md))

---

## Upgrade Path

```
L1 (Core)        → L2 (Standard):    Add output contract validation to CI.
                                      Add architecture linting rules.
                                      Takes: 1 sprint.

L2 (Standard)    → L3 (Enterprise):  Add policy engine (OPA/Cedar).
                                      Add MCP runtime guardrails.
                                      Add health score gate.
                                      Add agent registry enforcement.
                                      Takes: 1–2 sprints.
```

The single most impactful L1 → L2 upgrade is structured output validation. Requiring agents to
produce machine-readable output contracts — including what they did not verify — changes the
verification workflow from "does this look right?" to "does this satisfy the contract?" That
shift is the difference between governance by agreement and governance by constraint.

---

## Related

- [docs/architecture.md — Layer 3](architecture.md) — enforcement in the 7-layer model
- [patterns/structured-output-contracts.md](../patterns/structured-output-contracts.md) — the
  output contract standard
- [patterns/mcp-governance.md](../patterns/mcp-governance.md) — runtime enforcement for MCP
  tool access
- [automation/output_contract_validator.py](../automation/output_contract_validator.py) — CI
  validator
- [automation/health_score_calculator.py](../automation/health_score_calculator.py) — health
  score gate
- [ci-cd/github-actions/governance-check.yml](../ci-cd/github-actions/governance-check.yml) —
  Core Edition CI gate
- [docs/compliance-mapping.md](compliance-mapping.md) — mapping to NIST AI RMF, ISO 42001,
  EU AI Act
