# CHANGELOG

Session-level history for the AI Governance Framework. Newest first.

---

## v0.3.0 — Session 013 — 2026-03-01

**Scope:** Self-validation, dogfooding, health score update

### Completed

- Created `docs/self-validation-checklist.md` — six-dimension checklist (constitution health,
  session hygiene, enforcement active, knowledge freshness, agent accountability, friction check)
- Ran checklist against this repo; documented results in `v030_build_logs/self_validation_results.md`
- Fixed governance gaps: CHANGELOG.md, ARCHITECTURE.md, PROJECT_PLAN.md, `.pre-commit-config.yaml`
- Updated `automation/health_score_calculator.py` v0.3.0: added AGENTS.md check (+5) and
  self-validation checklist check (+5); max score extended to 110
- Updated `tests/test_health_score_calculator.py` with tests for v0.3.0 additions

### Score improvement

Pre-fix: 63/100 (Level 3 — Enforced) → Post-fix: 98/110 (Level 5 — Self-optimizing)

### Decisions

- MEMORY.md at root is an intentional deviation: cross-session memory for this repo lives in
  `.claude/memory/MEMORY.md` as per the agent SDK's memory system
- AGENTS.md at root is optional for this repo (Claude Code is the only AI tool used here);
  `templates/AGENTS.md` provides the artifact for framework users

---

## v0.3.0 — Session 012 — 2026-03-01

**Scope:** Integration flow, governance pipeline end-to-end documentation

### Completed

- `docs/governance-flow.md` — complete pipeline: CLAUDE.md → AGENTS.md → MCP → CI → Prod
- `docs/integration-compatibility.md` — migration paths from Fr-e-d, AI Governor, claude-code-config
- Cross-reference updates for new integration docs

---

## v0.3.0 — Session 011 — 2026-03-01

**Scope:** Operator tooling, GRC pattern

### Completed

- `patterns/operator-playbook.md` — step-by-step procedures: onboarding, incident response,
  quarterly audit, governance rollout
- `docs/compliance-guide.md` — governance for compliance teams
- Agent registry expanded with operator role

---

## v0.3.0 — Session 010 — 2026-03-01

**Scope:** Enforcement hardening

### Completed

- `docs/enforcement-hardening.md` — advanced CI/CD enforcement patterns
- Pre-commit hook updates in `ci-cd/pre-commit/`
- `scripts/hooks/pre_commit_guard.sh` and `scripts/hooks/post_commit.sh` hardened

---

## v0.2.0 — Session 009 — 2026-03-01

**Scope:** Agent identity and registry

### Completed

- `docs/agent-registry.md` — agent identity cards, capability matrix, permission boundaries
- `agents/onboarding-agent.md` — new agent for guided framework setup
- `agents/research-agent.md` — new agent for best-practice scanning

---

## v0.2.0 — Session 008 — 2026-03-01

**Scope:** Confidence ceiling, friction budget alignment

### Completed

- Configurable automation bias confidence ceiling (default: 85%) — replaces hardcoded value
- `patterns/friction-budget.md` aligned with confidence ceiling documentation
- README comparison table updated to reflect configurable ceiling

---

## v0.2.0 — Session 007 — 2026-03-01

**Scope:** Known failure modes documentation

### Completed

- `docs/known-failure-modes.md` — catalogue of AI governance failure modes with mitigations
- `docs/rollback-recovery.md` — rollback procedures for governance failures

---

## v0.2.0 — Session 006 — 2026-03-01

**Scope:** Compliance mapping

### Completed

- `docs/compliance-mapping.md` — mapping to NIST AI RMF, ISO 42001, EU AI Act
- `docs/enterprise-playbook.md` — enterprise deployment guide

---

## v0.2.0 — Session 005 — 2026-03-01

**Scope:** MCP governance

### Completed

- `patterns/mcp-governance.md` — MCP tool access control: least-privilege, kill switch,
  audit logging, rate limits
- `docs/mcp-governance.md` — implementation guide for MCP governance

---

## v0.2.0 — Session 004 — 2026-03-01

**Scope:** AGENTS.md portable governance bridge

### Completed

- `templates/AGENTS.md` — cross-tool governance bridge (Copilot, Cursor, Windsurf, Aider)
- `docs/agents-md-integration.md` — three coexistence options (mirror, extend, delegate)
- README updated with AGENTS.md quick-start section

---

## v0.2.0 — Session 003 — 2026-03-01

**Scope:** Core Edition minimum viable governance

### Completed

- `examples/core-edition/` — 10-minute governance setup (CLAUDE.md, commands, CI)
- `docs/getting-started.md` — both paths (Core Edition and Full framework)
- `bin/ai-governance-init` — interactive CLI wizard

---

## v0.1.0 — Session 002 — 2026-02-28

**Scope:** ADR infrastructure, constitutional inheritance, test suite expansion

### Completed

- `docs/adr/` — ADR-001 through ADR-004 covering core decisions
- `patterns/constitutional-inheritance.md` — org → team → repo inheritance pattern
- `automation/inherits_from_validator.py` — validates inheritance chain
- Test suite: 273 tests across 13 files, CI gate at 80% coverage

---

## v0.1.0 — Session 001 — 2026-02-28

**Scope:** Foundation — 7-layer architecture, core automation, initial documentation

### Completed

- 7-layer governance stack (Constitution → Evolution)
- `automation/health_score_calculator.py` — governance health score 0-100
- `automation/governance_dashboard.py` — auto-generated dashboard
- `agents/` — 9 specialized agent definitions
- `commands/` — 10 slash command definitions
- `patterns/` — 14 governance patterns
- `templates/` — 16 governance file templates
- `ci-cd/` — workflows for GitHub Actions, GitLab, CircleCI, Bitbucket, Azure DevOps
- Initial test suite with 80%+ coverage gate
