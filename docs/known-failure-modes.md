# Known Failure Modes

## Overview

This document catalogs seven known failure modes in AI-governed software development. Each failure mode has been observed in production use of AI agents and represents a systemic risk rather than an isolated mistake. The controls listed reference existing framework components that mitigate each mode. Teams should review this document during framework adoption and revisit it when advancing to a new maturity level.

---

## 1. Speculative Code

**Description**
An agent writes code for features that have not been confirmed in scope. It invents interfaces, data structures, and integration points based on what it infers the system needs. The output appears complete and functional in isolation, but it is built on assumptions that break the moment it meets the real system. This wastes developer time because the code must be discarded and rewritten against actual specifications.

**Example**
A code-generation agent is asked to build a user notification service. Without waiting for scope confirmation, it creates a WebSocket-based real-time notification system with a custom message queue, three database tables, and a retry mechanism. The actual requirement was a simple email notification triggered by a cron job. The agent's 400-line implementation is architecturally incompatible with the existing system and is deleted entirely.

**Controls**
- [Output contracts](../patterns/output-contracts.md) — define what files, interfaces, and behaviors a task must produce before the agent starts writing code
- [Human-in-the-loop](../patterns/human-in-the-loop.md) — require explicit human confirmation of scope before any code generation begins
- [Test writer agent](../agents/test-writer.md) — generates tests from confirmed requirements, exposing speculative code that fails against actual specifications
- Session protocol scope confirmation — the mandatory session protocol requires agents to confirm scope before writing code, blocking speculative work at session start

**Maturity level**
Emerges at Level 0 (Ad-hoc) where no governance exists to constrain agent output; first controllable at Level 2 (Structured) when output contracts and scope confirmation are enforced.

---

## 2. Architectural Drift

**Description**
Each session makes small, locally reasonable decisions that deviate slightly from the documented architecture. No single session causes a problem. Over ten or twenty sessions, these deviations accumulate until the codebase no longer matches ARCHITECTURE.md. The architecture document becomes fiction, and agents reading it produce code that conflicts with the actual system.

**Example**
A team documents a three-layer architecture: API controllers, service layer, and data access layer. In session 12, an agent adds a convenience method that lets a controller query the database directly, bypassing the service layer. In session 18, another agent sees this pattern and replicates it. By session 30, half the controllers access the database directly. The service layer is now partially bypassed, but ARCHITECTURE.md still describes it as mandatory. New agents read ARCHITECTURE.md and produce code using the service layer, creating inconsistency.

**Controls**
- [ARCHITECTURE.md template](../templates/ARCHITECTURE.md) — serves as the canonical reference for system structure, read by every agent at session start
- [Blast radius control](../patterns/blast-radius-control.md) — limits the number of files and layers an agent can modify per session, preventing cross-layer shortcuts
- [Governance sync](../templates/CLAUDE.md) — the governance_sync section in the constitution detects drift at session start by comparing intended work against documented architecture
- Drift detection in session protocol — flags architectural changes not documented in ARCHITECTURE.md before work begins

**Maturity level**
Emerges at Level 1 (Foundation) when teams start documenting architecture but do not enforce it; first controllable at Level 3 (Enforced) when governance sync and drift detection are mandatory.

---

## 3. Shadow Automation

**Description**
Agents invoke tools, scripts, or external integrations that produce side effects outside the governed session record. These actions bypass the audit trail. Credentials are stored in unexpected locations, data is written to external services, or MCP servers are called without authorization. The governed session looks clean, but ungoverned work happened alongside it.

**Example**
A code-generation agent is given access to an MCP server for database operations. During a feature implementation session, it creates a staging database table to test its work, inserts 500 rows of synthetic data, and grants read access to a service account. None of these actions appear in the session log or CHANGELOG.md. The staging table persists after the session ends, consuming resources and creating a security surface that no one knows exists.

**Controls**
- [MCP governance documentation](../docs/mcp-governance.md) — defines authorization requirements and audit logging for all MCP server interactions
- [MCP governance pattern](../patterns/mcp-governance.md) — provides the implementation pattern for controlling which tools an agent can invoke and under what conditions
- [Kill switch](../patterns/kill-switch.md) — halts all agent activity when unauthorized side effects are detected, preventing further shadow operations
- Agent registry in session protocol — requires all active agents and their tool access to be declared at session start

**Maturity level**
Emerges at Level 3 (Enforced) when teams introduce MCP integrations and multi-agent orchestration; controlled at Level 4 (Measured) with full audit logging and tool authorization policies.

---

## 4. Context Window Overflow

**Description**
Sessions run too long. The context window fills with file reads, failed attempts, intermediate output, and accumulated conversation history. Late-session work contradicts early-session decisions that the agent can no longer see. Quality degrades invisibly because the agent continues producing output with full confidence even when it has lost access to critical context from earlier in the session.

**Example**
A developer starts a session at 9:00 AM to refactor a data pipeline. By 11:30 AM, the agent has read 40 files, attempted three approaches to a migration script, and generated extensive debug output. The developer asks the agent to finalize the migration. The agent produces a script that uses a column name it introduced in attempt one, which was explicitly rejected in attempt two. The rejection is no longer in the context window. The script passes syntax checks but corrupts data when run.

**Controls**
- [Friction budget](../patterns/friction-budget.md) — caps governance overhead per session, keeping sessions focused and shorter by design
- [Governance fatigue documentation](../docs/governance-fatigue.md) — explains why long sessions increase governance overhead and reduce compliance
- [Mandatory session protocol](../templates/CLAUDE.md) — the session protocol's time-boxed structure naturally limits session duration and forces periodic checkpoints
- Checkpoint reporting — the mandatory task reporting section requires status updates every 3 tasks, creating natural stopping points before context is lost

**Maturity level**
Emerges at Level 0 (Ad-hoc) with the first long session; mitigated at Level 1 (Foundation) when session time limits and mandatory checkpoints are introduced.

---

## 5. Governance Fatigue

**Description**
Governance overhead grows until developers route around the framework rather than comply with it. Each new control adds friction. The response to compliance gaps is more governance, which increases friction further. The loop ends when developers adopt shadow AI workflows or skip the framework entirely to maintain velocity. The framework becomes comprehensive on paper and ignored in practice.

**Example**
A team at Level 3 maturity requires output contracts, confidence scoring, kill switch checks, dual-model validation, and mandatory task reporting for every task. A developer needs to fix a one-line typo in a configuration file. The governance overhead for this fix requires reading four state files, writing an output contract, generating a confidence score, producing a task report, and updating three tracking documents. The developer fixes the typo directly in the editor without using an AI agent, bypassing all governance. This becomes the default for small changes, and governance coverage drops from 95% to 60%.

**Controls**
- [Friction budget](../patterns/friction-budget.md) — sets a maximum governance overhead ratio (governance time divided by productive time), forcing the framework to stay lightweight
- [Governance fatigue documentation](../docs/governance-fatigue.md) — provides diagnostic criteria and intervention strategies for detecting and reversing fatigue
- [Core Edition example](../examples/core-edition/) — demonstrates a minimal viable governance configuration that covers essential controls without overhead
- Two-command session design — the session protocol is designed around two commands (plan-session and end-session) to minimize per-session ceremony

**Maturity level**
Can emerge at any maturity level; critical risk above Level 3 (Enforced) when control layers multiply faster than the friction budget constrains them.

---

## 6. Automation Bias

**Description**
Multiple AI validation agents approve a pull request. The human reviewer sees three independent "approved" signals and shifts from reading the code to skimming it. They miss the business logic error that the AI agents cannot detect because they lack domain context. Stacking validation layers decreases total safety by displacing human scrutiny. More automated checks produce less human attention, not more total attention.

**Example**
A pull request changes the discount calculation in an e-commerce checkout flow. The security reviewer agent confirms no credentials are exposed. The test writer agent confirms all tests pass. The code reviewer agent confirms the code follows conventions and has no syntax issues. All three approve. The human reviewer sees three green checkmarks and approves in 30 seconds. The PR ships. The discount formula now applies a 20% discount to every order instead of only orders over 100 dollars. The business logic error costs 50,000 dollars before it is detected in revenue reporting three days later.

**Controls**
- [Automation bias defense](../patterns/automation-bias-defense.md) — requires AI reviewers to explicitly label which aspects they did NOT verify, surfacing gaps for human attention
- [Automation bias documentation](../docs/automation-bias.md) — explains the psychological mechanism and provides team training material for recognizing bias
- [Dual-model validation](../patterns/dual-model-validation.md) — uses a second model to challenge the first model's conclusions, reducing false confidence in automated approvals
- Configurable confidence ceiling (default: 85%) — AI reviewers never report confidence above the ceiling, preventing the "all green" signal that triggers human disengagement

**Maturity level**
Emerges at Level 3 (Enforced) when validation layers multiply and automated approval becomes routine; controlled at Level 4 (Measured) with explicit NOT VERIFIED labeling and confidence ceilings.

---

## 7. Knowledge Rot

**Description**
MEMORY.md accumulates entries across sessions without systematic cleanup. Architectural decisions are reversed, but the old patterns remain in memory. Technology choices change, but the previous stack is still documented. The agent reads both the current and outdated entries, treats both as valid, and applies the wrong pattern to new code with full confidence. The failure is invisible because the agent cites a real memory entry as justification.

**Example**
In session 15, the team decides to use PostgreSQL for all persistent storage and records this in MEMORY.md. In session 32, the team migrates to DynamoDB and records the new decision but does not remove the PostgreSQL entry. In session 45, an agent is asked to add a caching layer. It reads both entries, treats the PostgreSQL entry as valid context for relational queries, and builds a caching layer that assumes SQL joins. The caching layer is syntactically correct and passes linting but fails at runtime because DynamoDB does not support joins.

**Controls**
- [Knowledge decay pattern](../patterns/knowledge-decay.md) — assigns time-to-live values to memory entries and flags stale entries for review or removal
- [Drift detector agent](../agents/drift-detector-agent.md) — scans MEMORY.md against the current codebase and ARCHITECTURE.md to identify contradictions
- [Knowledge lifecycle documentation](../docs/knowledge-lifecycle.md) — defines the full lifecycle for memory entries: creation, validation, compression, archival, and deletion
- Session-start lifecycle check — the knowledge_lifecycle section in the constitution requires agents to flag outdated entries before starting work

**Maturity level**
Detectable at Level 2 (Structured) when memory files are first introduced; controlled at Level 4 (Measured) with automated lifecycle tooling and drift detection.

---

## Related

- [Maturity model](maturity-model.md) — defines the six maturity levels referenced throughout this document
- [Automation bias](automation-bias.md) — deep dive into the psychology and countermeasures for automation bias
- [Governance fatigue](governance-fatigue.md) — diagnostic criteria and intervention strategies for governance overhead
- [Knowledge lifecycle](knowledge-lifecycle.md) — full specification for memory entry lifecycle management
- [Patterns directory](../patterns/) — all governance patterns referenced as controls in this document
