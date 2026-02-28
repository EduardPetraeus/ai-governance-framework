# Documentation

This directory contains the full specification and guidance for the AI Governance Framework. Files are organized by topic: foundational concepts come first, followed by operational guidance, risk management, and reference material. Start with Getting Started if you are new to the framework; return to specific sections as your governance maturity grows.

## Getting Started

- [getting-started.md](getting-started.md) — Full installation walkthrough: initialize a repo, configure layers, run the first governance check
- [maturity-model.md](maturity-model.md) — Six-level maturity model from Ad-hoc (level 0) to Self-optimizing (level 5); use this to assess and plan your governance journey
- [architecture.md](architecture.md) — Framework architecture and the 7-layer model; how layers compose from repo-level constitution to enterprise orchestration

## Session Protocol

- [session-protocol.md](session-protocol.md) — Mandatory three-phase protocol (Start, During, End) that every AI agent session must follow
- [session-replay.md](session-replay.md) — How to reconstruct what an agent did in a session; audit trail format and tooling
- [rollback-recovery.md](rollback-recovery.md) — Recovery procedures when a session produces bad output or violates governance rules

## Agents and Commands

- [agent-orchestration.md](agent-orchestration.md) — How a master agent coordinates specialist agents; delegation patterns and result aggregation
- [quality-control-patterns.md](quality-control-patterns.md) — Guide to 8 output verification patterns; how agents validate their own work before committing
- [model-routing.md](model-routing.md) — Decision guide for choosing between Opus, Sonnet, and Haiku based on task complexity and cost

## Governance Design

- [constitutional-inheritance.md](constitutional-inheritance.md) — How governance cascades from org-level CLAUDE.org.md down through team and repo CLAUDE.md files
- [prompt-engineering.md](prompt-engineering.md) — Prompt design principles specific to governance contexts; structuring agent instructions for consistency
- [ai-code-quality.md](ai-code-quality.md) — Code quality standards that apply to AI-generated code; what reviewers must verify that linters cannot

## Security and Compliance

- [security-guide.md](security-guide.md) — Security requirements, secret scanning configuration, PII handling rules, and the security reviewer agent
- [compliance-guide.md](compliance-guide.md) — Audit trail requirements for regulated industries; how to configure the framework for compliance contexts
- [adversarial-audit.md](adversarial-audit.md) — Red-team methodology for AI governance; how to test whether agents respect their constraints under adversarial prompts

## Self-Improvement

- [self-updating-framework.md](self-updating-framework.md) — How the framework keeps its own documentation and rules current as practices evolve
- [research-pipeline.md](research-pipeline.md) — The research agent and `/research` command; how new information is evaluated and incorporated
- [knowledge-lifecycle.md](knowledge-lifecycle.md) — Managing knowledge decay, freshness scoring, and scheduled review of framework content

## Measurement

- [metrics-guide.md](metrics-guide.md) — Governance metrics, KPIs, and the scoring system behind the health score calculator
- [productivity-measurement.md](productivity-measurement.md) — Methodology for tracking AI-assisted productivity; baselines, measurement points, and reporting cadence

## Enterprise

- [enterprise-playbook.md](enterprise-playbook.md) — Adoption playbook for enterprise teams: rollout phases, stakeholder alignment, and scaling governance across many repos
- [multi-ide-support.md](multi-ide-support.md) — Configuration guide for Cursor, GitHub Copilot, Windsurf, and Aider alongside Claude Code; feature comparison matrix and migration notes

## Risk and Recovery

- [automation-bias.md](automation-bias.md) — Automation bias risks in AI-assisted development; detection signals and mitigation practices for teams
- [governance-fatigue.md](governance-fatigue.md) — Recognizing and preventing governance burnout; how to keep rules lightweight and respected over time
- [kill-switch.md](kill-switch.md) — Emergency halt procedures; how to stop all agent activity immediately and preserve state for investigation

## Architecture Decisions

- [adr/ADR-000-template.md](adr/ADR-000-template.md) — Template for Architecture Decision Records used in this framework

ADRs are numbered sequentially starting from ADR-001. ADR-000 is the template only and is never a real decision record. Each ADR documents a significant design choice, the alternatives considered, and the rationale for the decision taken. File names follow the pattern `ADR-NNN-short-title.md`.

## Case Studies

- [case-studies/health-reporting.md](case-studies/health-reporting.md) — End-to-end case study of the project that motivated and shaped this framework; covers the governance problems encountered and how each layer was designed in response

---

These docs are updated as the framework evolves. If documentation is missing for a feature you are using, open an issue in the repository so it can be prioritized.
