# Compliance Mapping

> **Disclaimer:** This document is for informational purposes only and does not constitute legal advice.
> Regulatory obligations vary by jurisdiction, sector, and AI system classification. Consult qualified
> legal counsel for compliance requirements specific to your organization and use case.

This page maps framework elements to three AI governance standards. Use it as a starting point
for compliance conversations — not as a substitute for professional regulatory assessment.

---

## NIST AI Risk Management Framework (AI RMF 1.0)

The NIST AI RMF organizes AI risk management into four core functions.

| NIST AI RMF Function | Framework Element | File |
|---|---|---|
| **GOVERN** — policies and accountability | Agent constitution | [templates/CLAUDE.md](../templates/CLAUDE.md) |
| **GOVERN** — org-level rules cascade to repos | Constitutional inheritance | [patterns/constitutional-inheritance.md](../patterns/constitutional-inheritance.md) |
| **GOVERN** — defined roles and responsibilities | Agent definitions | [agents/](../agents/) |
| **GOVERN** — incident escalation policy | Kill-switch procedure | [patterns/kill-switch.md](../patterns/kill-switch.md) |
| **MAP** — AI system categorization | Maturity model self-assessment | [docs/maturity-model.md](maturity-model.md) |
| **MAP** — risk identification | Red-team auditor | [agents/red-team-auditor.md](../agents/red-team-auditor.md) |
| **MAP** — dependency and context mapping | Context boundaries pattern | [patterns/context-boundaries.md](../patterns/context-boundaries.md) |
| **MEASURE** — governance health score | Health score calculator | [automation/health_score_calculator.py](../automation/health_score_calculator.py) |
| **MEASURE** — AI output quality metrics | Quality gate agent | [agents/quality-gate-agent.md](../agents/quality-gate-agent.md) |
| **MEASURE** — confidence ceiling (85%) | Automation bias defense | [patterns/automation-bias-defense.md](../patterns/automation-bias-defense.md) |
| **MANAGE** — session-level control | Session protocol | [docs/session-protocol.md](session-protocol.md) |
| **MANAGE** — emergency stop | Kill switch | [docs/kill-switch.md](kill-switch.md) |
| **MANAGE** — rollback and recovery | Rollback guide | [docs/rollback-recovery.md](rollback-recovery.md) |
| **MANAGE** — continuous improvement | Framework updater | [automation/framework_updater.py](../automation/framework_updater.py) |

---

## ISO/IEC 42001 (AI Management Systems)

ISO 42001 specifies requirements for an AI Management System (AIMS). Key clause groups:
policies, roles, risk, monitoring, and improvement.

| ISO 42001 Clause | Requirement | Framework Element | File |
|---|---|---|---|
| 5.2 — Policy | Documented AI use policy | Agent constitution | [templates/CLAUDE.md](../templates/CLAUDE.md) |
| 5.3 — Roles | Defined accountability per level | Org and team constitutions | [templates/CLAUDE.org.md](../templates/CLAUDE.org.md) |
| 6.1 — Risk | AI risk identification | Security guide | [docs/security-guide.md](security-guide.md) |
| 6.1 — Risk | Adversarial risk probing | Red-team audit | [agents/red-team-auditor.md](../agents/red-team-auditor.md) |
| 6.2 — Objectives | Measurable AI governance goals | Metrics guide | [docs/metrics-guide.md](metrics-guide.md) |
| 8.4 — Impact | Impact assessment before deployment | Human-in-the-loop pattern | [patterns/human-in-the-loop.md](../patterns/human-in-the-loop.md) |
| 9.1 — Monitoring | Ongoing governance monitoring | Governance dashboard | [automation/governance_dashboard.py](../automation/governance_dashboard.py) |
| 9.2 — Internal audit | Self-audit of AI processes | Audit command | [commands/audit.md](../commands/audit.md) |
| 10.1 — Nonconformity | Incident handling and correction | Rollback and recovery | [docs/rollback-recovery.md](rollback-recovery.md) |
| 10.2 — Improvement | Continual improvement process | Upgrade command | [commands/upgrade.md](../commands/upgrade.md) |

---

## EU AI Act

The EU AI Act creates obligations based on risk class. For software teams using AI coding
assistants, the most relevant obligations are in the **GPAI provisions** (Title VIII, Articles
51-56) and **high-risk system requirements** (Title III, Chapter 2).

| EU AI Act Obligation | Applies When | Framework Element | File |
|---|---|---|---|
| GPAI — model transparency | Using GPAI models (Claude, GPT-4) as coding agents | Model routing documentation | [docs/model-routing.md](model-routing.md) |
| GPAI — usage policy | GPAI integrated into internal tools or workflows | Agent constitution | [templates/CLAUDE.md](../templates/CLAUDE.md) |
| Technical documentation (Art. 11, Annex IV) | High-risk AI systems | Architecture records and ADRs | [templates/ARCHITECTURE.md](../templates/ARCHITECTURE.md) |
| Human oversight (Art. 14) | All high-risk systems | Human-in-the-loop pattern | [patterns/human-in-the-loop.md](../patterns/human-in-the-loop.md) |
| Post-market monitoring (Art. 72) | Deployed high-risk systems | Best-practice scanner + CHANGELOG | [automation/best_practice_scanner.py](../automation/best_practice_scanner.py) |
| Serious incident reporting (Art. 73) | Incidents in high-risk systems | Kill switch + rollback | [patterns/kill-switch.md](../patterns/kill-switch.md) |
| Logging and audit trail | All high-risk systems | Session logs + CI governance check | [commands/end-session.md](../commands/end-session.md) |
| Conformity assessment | Before deploying high-risk AI | Audit command | [commands/audit.md](../commands/audit.md) |

### Annex IV — Technical Documentation Example

Article 11 and Annex IV specify minimum technical documentation for high-risk AI systems.
The table below shows how this framework's files satisfy each item.

| Annex IV Item | Required Content | Framework File |
|---|---|---|
| 1. General description | Purpose, intended use, version | `CLAUDE.md` → `project_context` section |
| 2. Detailed description of elements | Architecture, model, data flows | `ARCHITECTURE.md` + ADRs in `docs/adr/` |
| 3. Design specifications | Constraints, boundaries, write access | `CLAUDE.md` → `security_protocol` section |
| 4. Monitoring and control measures | Oversight triggers, escalation paths | `patterns/human-in-the-loop.md` |
| 5. Changes and versions | Change log with rationale per session | `CHANGELOG.md` |
| 6. Standards applied | Governance standards followed | This document |
| 7. EU declaration of conformity | (External: legal certification) | Provided by qualified assessor |

---

## Related Documentation

- [docs/compliance-guide.md](compliance-guide.md) — Regulatory landscape for AI-assisted development (EU AI Act, GDPR, SOX, HIPAA, NIS2)
- [docs/security-guide.md](security-guide.md) — Security controls and threat model
- [docs/enterprise-playbook.md](enterprise-playbook.md) — Enterprise adoption guide including audit trail requirements
- [docs/maturity-model.md](maturity-model.md) — Maturity levels and self-assessment checklists
