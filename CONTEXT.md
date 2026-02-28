# Project Context — AI Governance Framework

> **Auto-synced:** Claude Code updates this file at session end. Claude.ai fetches it at conversation start.
> **Last updated:** 2026-02-28
> **Updated by:** Manual (post v0.2.0 build verification)

---

## Current State

**Version:** v0.2.0
**Status:** Complete. 273/273 tests passing. Tagged and pushed (commit 96daff3).
**Repo:** https://github.com/EduardPetraeus/ai-governance-framework

## What This Is

Open-source AI governance framework — executable governance for AI agents in software development. Constitutional hierarchy, automated enforcement, measurable maturity levels. Self-governing (uses its own framework).

## Architecture

7-layer model: Constitution → Orchestration → Enforcement → Observability → Knowledge → Team Governance → Evolution

Key files: CLAUDE.md (constitution), agents/ (11 agents), commands/ (10 commands), patterns/ (13 patterns), templates/ (15 templates), docs/ (26 specs), automation/ (8 Python scripts), ci-cd/ (5 CI platforms), tests/ (13 test files, 273 tests)

## Build History

- v0.1.0: Initial build (4 autonomous prompts, 76 min, ~97 files)
- v0.2.0: Expansion build (7 autonomous prompts, 96 min, ~50 commits, 273 tests, 32 review fixes)
- Total autonomous build time: 172 minutes, zero errors, zero manual intervention

## Recent Changes

- CLI installer (`npx ai-governance-init`), shell installer, command deployer
- 273 pytest tests across 13 files, CI workflow with coverage gate
- Multi-IDE (Cursor, Copilot, Windsurf, Aider) and multi-CI (GitHub, GitLab, CircleCI, Bitbucket, Azure DevOps)
- Governance dashboard + cost dashboard generators
- 4 automation scripts (security review, inheritance validator, token counter, ADR coverage)
- 3 ADRs, README rewrite, all index READMEs, CONTRIBUTING extended
- Opus review: 32 issues found and fixed (4 Python bugs, 5 CI shell injection risks, etc.)
- Business strategy documented (consulting phases, Pandora AI team)
- Research notes: CLAUDE.md hierarchy, AGENTS.md standard, MCP paradigm shift, overflow research

## Pending Actions

- [x] Verify v0.2.0 build completion and tag
- [ ] Commit docs/internal/ files to repo (HANDOVER, BUSINESS_STRATEGY, RESEARCH_NOTES, META_DECISIONS)
- [ ] Commit CONTEXT.md to repo root
- [ ] Multi-AI adversarial review (Gemini, ChatGPT, Grok, DeepSeek, Perplexity)
- [ ] Fix review findings → v0.3.0
- [ ] HealthReporting submodule integration
- [ ] Map CLAUDE.md 4-level hierarchy to constitutional inheritance
- [ ] Evaluate AGENTS.md as complementary standard
- [ ] Add conciseness-reminder to CLAUDE.md template
- [ ] Address MCP sandboxed execution in governance scope
- [ ] Evaluate plugin distribution format

## Deep Context

For full details, see these files in the repo:
- `docs/internal/HANDOVER.md` — complete build history and session context
- `docs/internal/BUSINESS_STRATEGY.md` — commercialization phases
- `docs/internal/RESEARCH_NOTES.md` — actionable research findings
- `docs/internal/META_DECISIONS.md` — naming, structure, memory architecture
- `FRAMEWORK_DESCRIPTION.md` — 725-line Opus reference (stored locally, not in repo)
