# Project Plan — AI Governance Framework

## Current Version: v0.3.0

### Active Sprint: v0.3.0 — Self-validation and operator tooling

**Sprint goal:** Close the governance loop — the framework governs itself using its own
standards. Every checklist item the framework recommends should be present in this repo.

**Status:** In progress

| Task | Status |
|---|---|
| Self-validation checklist (`docs/self-validation-checklist.md`) | Done |
| Dogfood self-test against this repo | Done |
| Health score calculator v0.3.0 update | Done |
| Operator playbook (`patterns/operator-playbook.md`) | Done |
| Integration flow documentation | Done |
| Enforcement hardening docs | Done |
| Fix governance gaps found during self-test | Done |

---

## Roadmap

### v0.4.0 — Tooling Extensions

| Feature | Priority |
|---|---|
| VS Code extension — inline governance compliance hints | High |
| Automated knowledge freshness scan (flag ADRs > 365 days) | Medium |
| Dashboard auto-generation from CHANGELOG entries | Medium |
| OpenAI / Gemini model routing configuration templates | Low |

### v0.5.0 — Enterprise Scale

| Feature | Priority |
|---|---|
| Org-level CLAUDE.md inheritance resolver (UI-driven) | High |
| Role-based agent access control examples | Medium |
| Compliance audit trail export (NIST, ISO 42001) | Medium |

---

## Maturity Target

This repo targets **Level 5 (Self-optimizing)** — the framework optimizes its own governance.

Current score: tracked by `automation/health_score_calculator.py .`
