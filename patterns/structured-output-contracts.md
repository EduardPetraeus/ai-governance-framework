# Pattern: Structured Output Contracts

## Problem

The [Output Contracts pattern](output-contracts.md) defines what an agent should produce before
it works. The contract is written and reviewed as YAML or prose — useful for human review, but
not machine-parseable. A CI check cannot evaluate whether an agent's confidence was too high,
whether it declared what it did not verify, or whether it flagged architectural impact.

The result: governance checks can verify that files were updated, but cannot verify the quality
of the update metadata. An agent can write any CHANGELOG entry and pass the governance check. An
agent can claim 95% confidence with an empty `not_verified` list and pass the governance check.
The gap between "governance artifact exists" and "governance artifact is valid" is the gap this
pattern closes.

## Solution

Require agents to produce a structured output contract in machine-readable JSON format at the
end of every session. The format is validated by CI before merge is permitted.

### Standard Format

```json
{
  "status": "PASS",
  "session": "042",
  "date": "2026-03-01",
  "model": "claude-sonnet-4-6",
  "files_changed": [
    {"path": "src/connectors/github/stars.py", "operation": "created"},
    {"path": "tests/connectors/test_github_stars.py", "operation": "created"},
    {"path": "src/connectors/registry.py", "operation": "modified"}
  ],
  "confidence": 78,
  "not_verified": [
    "Rate limit behavior under sustained load",
    "Behavior when GITHUB_TOKEN is expired mid-session"
  ],
  "architectural_impact": "none",
  "requires_review": false,
  "requires_review_reason": null
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | `"PASS"` \| `"WARN"` \| `"FAIL"` | Yes | Overall session outcome. `WARN` = completed with caveats. `FAIL` = incomplete or contract breach. |
| `session` | string | Yes | Session identifier matching the CHANGELOG entry. |
| `date` | string (YYYY-MM-DD) | Yes | Session date. |
| `model` | string | Yes | Model ID used. E.g. `claude-sonnet-4-6`. |
| `files_changed` | array of objects | Yes | Each object: `path` (string) + `operation` (`"created"`, `"modified"`, `"deleted"`). Empty array if no file changes. |
| `confidence` | integer 0–100 | Yes | Agent's overall confidence that output is correct and complete. Must be ≤ configured ceiling (default: 85) per [automation-bias-defense](automation-bias-defense.md). |
| `not_verified` | array of strings | Yes | Items the agent did not verify. Documents the scope of required human review. |
| `architectural_impact` | `"none"` \| `"low"` \| `"medium"` \| `"high"` | Yes | Impact on architecture. `"high"` triggers mandatory human review. |
| `requires_review` | boolean | Yes | True if human review is required before merge. |
| `requires_review_reason` | string \| null | Yes | Required when `requires_review` is true. Must be null when false. |

### Status Semantics

| Status | Meaning | Merge allowed |
|--------|---------|---------------|
| `PASS` | All tasks completed, all contract items met | Yes, after CI passes |
| `WARN` | Completed with known gaps (listed in `not_verified`) | Yes, after CI + human acknowledgment of gaps |
| `FAIL` | Task incomplete or contract breach detected | No — must be resolved before merge |

### Confidence Ceiling

The `confidence` field is bounded by the automation-bias-defense principle. The configured
ceiling (default: 85) is enforced by the validator. Agents reporting confidence above the
ceiling are rejected by CI with a specific error:

```
FAIL: confidence value 92 exceeds configured ceiling 85.
      Agents must not claim higher confidence than the project ceiling.
      See patterns/automation-bias-defense.md for the rationale.
```

This constraint is structural, not stylistic. An agent reporting 95% confidence discourages
human scrutiny. A ceiling of 85% preserves the margin for human judgment on every session.

## JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OutputContract",
  "description": "Machine-readable output contract for an AI agent session.",
  "type": "object",
  "required": [
    "status", "session", "date", "model",
    "files_changed", "confidence", "not_verified",
    "architectural_impact", "requires_review", "requires_review_reason"
  ],
  "additionalProperties": false,
  "properties": {
    "status": {
      "type": "string",
      "enum": ["PASS", "WARN", "FAIL"],
      "description": "Overall session outcome."
    },
    "session": {
      "type": "string",
      "minLength": 1,
      "description": "Session identifier matching the CHANGELOG entry."
    },
    "date": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
      "description": "Session date in YYYY-MM-DD format."
    },
    "model": {
      "type": "string",
      "minLength": 1,
      "description": "Model ID used in this session."
    },
    "files_changed": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "operation"],
        "additionalProperties": false,
        "properties": {
          "path": {"type": "string", "minLength": 1},
          "operation": {
            "type": "string",
            "enum": ["created", "modified", "deleted"]
          }
        }
      }
    },
    "confidence": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "Agent confidence 0–100. Validated against project ceiling (default: 85)."
    },
    "not_verified": {
      "type": "array",
      "items": {"type": "string", "minLength": 1},
      "description": "Items the agent did not verify. Documents scope of human review needed."
    },
    "architectural_impact": {
      "type": "string",
      "enum": ["none", "low", "medium", "high"],
      "description": "Impact on project architecture."
    },
    "requires_review": {
      "type": "boolean",
      "description": "True if human review is required before merge."
    },
    "requires_review_reason": {
      "type": ["string", "null"],
      "description": "Required when requires_review is true. Must be null otherwise."
    }
  }
}
```

## CI Validation Example

```yaml
# .github/workflows/governance-check.yml (add to existing workflow)
validate-output-contract:
  name: Validate output contract if present
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v4

    - name: Check output contract
      if: hashFiles('output_contract.json') != ''
      run: |
        python automation/output_contract_validator.py output_contract.json \
          --confidence-ceiling 85
```

The validator produces a structured report and exits with code 0 (PASS) or 1 (FAIL):

```
Validating output_contract.json
================================
  status               PASS
  session              042
  date                 2026-03-01
  model                claude-sonnet-4-6
  files_changed        3 files
  confidence           78  (ceiling: 85)  OK
  not_verified         2 items declared
  architectural_impact none
  requires_review      false

RESULT: PASS
```

On failure:

```
Validating output_contract.json
================================
  status               PASS
  ...
  confidence           92  (ceiling: 85)  EXCEEDS CEILING
  ...

  FAIL: confidence value 92 exceeds configured ceiling 85.
        Agents must not claim higher confidence than the project ceiling.
        See patterns/automation-bias-defense.md.
  FAIL: requires_review_reason must be a non-empty string when requires_review is true

RESULT: FAIL (2 errors)
```

## Where the Contract File Lives

Place `output_contract.json` in the repository root during the session. The CI check runs on
the PR diff. After merge, the file can be archived to `docs/session-contracts/` or deleted —
the CHANGELOG entry remains as the human-readable record.

```
output_contract.json           # transient — present on PR branch, not on main
docs/session-contracts/        # optional archive for compliance audit trail
```

## Implementation

### Step 1: Agent produces the contract at session end

Add to the `/end-session` command or `CLAUDE.md` session protocol:

```
At session end, write output_contract.json to the repository root.
Include all required fields. Confidence must not exceed 85.
not_verified must list every item not fully confirmed by automated checks.
```

### Step 2: CI validates before merge

```yaml
- name: Validate output contract
  if: hashFiles('output_contract.json') != ''
  run: python automation/output_contract_validator.py output_contract.json
```

### Step 3: Human reviews the not_verified list

The `not_verified` list is the direct input for human review. The human does not re-examine
what the agent verified — they focus on the gaps. This makes review efficient and reproducible:
checking a list is faster and more thorough than reading every changed line and deciding whether
it "looks right."

## Example: WARN Status

A session that completed the main task but could not test one scenario:

```json
{
  "status": "WARN",
  "session": "028",
  "date": "2026-03-01",
  "model": "claude-sonnet-4-6",
  "files_changed": [
    {"path": "src/auth/oauth.py", "operation": "modified"},
    {"path": "tests/test_oauth.py", "operation": "modified"}
  ],
  "confidence": 72,
  "not_verified": [
    "Token refresh when both access and refresh tokens expire simultaneously",
    "Behavior with OAuth providers that return non-standard error codes"
  ],
  "architectural_impact": "low",
  "requires_review": true,
  "requires_review_reason": "Auth changes require security team sign-off per CLAUDE.md security_protocol"
}
```

## Related Patterns

- [Output Contracts](output-contracts.md) — the prose-based contract format this extends with
  machine validation
- [Automation Bias Defense](automation-bias-defense.md) — rationale for the confidence ceiling
- [Dual-Model Validation](dual-model-validation.md) — a reviewing model validates against the
  contract
- [Human-in-the-Loop](human-in-the-loop.md) — `requires_review: true` triggers this pattern
- [Enforcement Hardening](../docs/enforcement-hardening.md) — how contract validation fits the
  3-level enforcement model
