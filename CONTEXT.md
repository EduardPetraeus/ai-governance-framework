# Project Context — AI Governance Framework

> **Auto-synced:** Claude Code updates this file at session end. Claude.ai fetches it at conversation start.
> **Last updated:** 2026-03-01
> **Updated by:** Workstream 1 — Governance Refinement

---

## Current State

**Version:** v0.3.0 + workstream-1/governance-refinement
**Status:** 864/864 tests passing. Branch: workstream-1/governance-refinement.
**Repo:** https://github.com/EduardPetraeus/ai-governance-framework

## What This Is

Open-source AI governance framework — executable governance for AI agents in software development. Constitutional hierarchy, automated enforcement, measurable maturity levels. Self-governing (uses its own framework).

## Architecture

7-layer model: Constitution → Orchestration → Enforcement → Observability → Knowledge → Team Governance → Evolution

Key files: CLAUDE.md (constitution), agents/ (11 agents), commands/ (11 commands), patterns/ (19 patterns), templates/ (19 templates), docs/ (39 specs), automation/ (9 Python scripts), ci-cd/ (5 CI platforms), tests/ (16 test files, 859 tests)

## Build History

- v0.1.0: Initial build (4 autonomous prompts, 76 min, ~97 files)
- v0.2.0: Expansion build (7 autonomous prompts, 96 min, ~50 commits, 273 tests, 32 review fixes)
- v0.3.0: Integration + hardening (6 autonomous prompts — sessions 008-013): self-validation, operator playbook, enforcement hardening, compliance guide, integration flow, health score v0.3.0
- Total autonomous build time: ~250 minutes, zero errors, zero manual intervention

## Major v0.3.0 Additions

- Self-validation checklist (6-dimension framework audit)
- Enforcement hardening docs + hardened pre-commit hooks
- Compliance guide for GRC teams
- Governance flow end-to-end pipeline doc
- Integration compatibility guide (migration from Fr-e-d, AI Governor, claude-code-config)
- Operator playbook (onboarding, incident response, quarterly audit)
- Health score calculator v0.3.0: max score raised to 110 (+5 AGENTS.md, +5 self-validation)
- Test suite: 859 tests across 16 files (was 273 across 13), coverage 94%

## Workstream 1 — Governance Refinement (post v0.3.0)

- Health score recalibrated: output is now checklist completion percentage (0-100%) with disclaimer; raw points and max_score preserved in report
- Agent tier system: 4 core agents (security-reviewer, code-reviewer, quality-gate-agent, master-agent) and 7 extended agents, with metadata blocks and updated README
- Pattern cross-references: blast-radius-control, context-boundaries, automation-bias-defense now cross-reference each other; Pattern Groups table added to patterns/README.md
- Confidence ceiling: domain guidance table added to automation-bias-defense pattern; cross-references between ADR-003 and pattern file
- CI/CD: non-GitHub platforms (GitLab, CircleCI, Bitbucket, Azure DevOps) marked as community contributed with status column in README
- Editions: Core Edition established as primary starting point; solo-developer, small-team, enterprise marked as community editions
- Test suite: 864 tests (was 859), all passing

## v0.4.0 Preview

Planned additions:
- Multi-agent orchestration governance (agent-to-agent trust, handoff protocols)
- Cost governance: budget alerts, per-agent cost attribution
- Governance-as-code SDK: Python library wrapping the framework for programmatic use
- Community contributed patterns (GitHub Discussions integration)
- Compliance certifications: SOC 2 and ISO 42001 mapping to framework layers

## Pending Actions

- [ ] Push v0.3.0 tag to remote (human reviews and pushes)
- [ ] Multi-AI adversarial review (Gemini, ChatGPT, Grok) → v0.4.0 issues
- [ ] HealthReporting submodule integration
- [ ] Evaluate plugin distribution format (npm / pip / standalone)
- [ ] Address MCP sandboxed execution in governance scope
