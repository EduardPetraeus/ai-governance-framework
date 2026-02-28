# Compliance Guide: Regulatory Landscape for AI-Assisted Development

## 1. Scope

This guide covers regulations that apply to **teams using AI coding assistants** — not just teams building AI products. The distinction matters: most compliance guidance for AI focuses on the systems being built. This guide focuses on the development process itself.

The regulations that affect AI-assisted software development teams in 2026:

| Regulation | Jurisdiction | What It Governs | When It Applies to Your Team |
|------------|-------------|-----------------|------------------------------|
| **EU AI Act** | EU/EEA | AI systems by risk level | When you build software that classifies as an AI system, or when AI tools are used in development processes subject to EU regulation |
| **GDPR** | EU/EEA + global reach | Personal data processing | When any personal data enters an AI prompt — including during debugging, log analysis, or code review |
| **SOX** | US (public companies) | Financial reporting controls | When AI-generated code processes financial data or feeds into financial reporting |
| **HIPAA** | US | Protected Health Information | When health data enters prompts or when AI-generated code handles patient data |
| **NIS2** | EU | Critical infrastructure cybersecurity | When AI-assisted development builds or maintains critical infrastructure systems |
| **MiFID II** | EU | Financial services | When AI-generated code is part of trading systems, risk calculations, or client-facing financial tools |

**The central insight:** Most compliance requirements are about **documentation and auditability**, not about restricting AI use. An organization with proper AI governance — session logs, CHANGELOG discipline, git attribution, human review gates — satisfies most regulatory requirements as a natural byproduct of operating correctly. Organizations without governance will fail the same audits regardless of whether they use AI.

---

## 2. EU AI Act

### Is Your AI Coding Tool a High-Risk AI System?

No. The classification test is straightforward:

AI-assisted development tools (Claude Code, GitHub Copilot, Cursor, Windsurf) are classified as **limited-risk or minimal-risk** under the EU AI Act. They are assistive tools that help humans write code. They do not autonomously make decisions that affect individuals' rights, safety, or legal status.

However, the classification of the development tool is not the end of the analysis. The relevant follow-up question is: **what does the software that the AI helps build do?**

| What the AI-Assisted Code Produces | Risk Classification | Implications |
|-------------------------------------|---------------------|--------------|
| Internal tooling, dashboards, data pipelines | Minimal risk | Transparency obligations only (document that AI is used) |
| Recommender systems, content personalization | Limited risk | Transparency to end users that AI is involved |
| Credit scoring, insurance pricing, hiring tools | **High risk** | Certification, conformity assessment, human oversight documentation, audit trail |
| Biometric identification systems | **High risk** | Additional restrictions; some use cases prohibited |
| Medical device software, clinical decision support | **Potentially high risk** | Subject to both EU AI Act and Medical Device Regulation (MDR) |
| Critical infrastructure control systems | **High risk** | NIS2 requirements also apply |

**The practical consequence:** The development tool is not high-risk. The software the tool produces may be. If your team builds high-risk AI systems with AI assistance, the development process itself must provide the documentation, audit trail, and human oversight that the EU AI Act requires for the resulting system.

### Human Oversight Requirements

For high-risk AI systems, the EU AI Act (Article 14) requires **meaningful human oversight**. This means:

1. Humans must be able to **understand the outputs** of the AI system
2. Humans must be able to **intervene and override** the system
3. The oversight must be **documented and evidenced** — not merely claimed

For software development teams, this translates to:

- Code review of AI-generated code must be **genuine** — not rubber-stamped (see section 5)
- The review process must be **documented** in a way that can be audited: PR comments, checklist completion, review timestamps
- Developers must be **capable of understanding** the AI-generated code they approve. "I clicked approve but I do not really understand the authentication logic" does not satisfy the oversight requirement for high-risk systems

### Documentation Requirements (Article 13)

The EU AI Act requires that AI systems be accompanied by documentation enabling competent authorities to assess compliance. For AI-assisted development, this means:

| Requirement | What Satisfies It in This Framework |
|-------------|-------------------------------------|
| Record of AI involvement in development | Git `Co-Authored-By` metadata on every AI-assisted commit |
| Evidence of human review | PR approval records with comments demonstrating engagement |
| Decision rationale | ADRs documenting architectural decisions and trade-offs considered |
| System description including AI components | `ARCHITECTURE.md` with explicit notation of AI-generated components |
| Risk assessment | ADRs for risk-relevant decisions; DECISIONS.md for runtime risk trade-offs |

### How the Governance Framework Satisfies EU AI Act Requirements

| EU AI Act Requirement | Framework Component |
|----------------------|---------------------|
| Transparency: AI involvement disclosed | `Co-Authored-By` in commits + CHANGELOG model attribution |
| Human oversight: meaningful review | Session protocol checkpoints + PR review requirement + anti-rubber-stamping practices |
| Documentation: development process recorded | CHANGELOG.md + DECISIONS.md + ADR archive |
| Risk management: risks identified and mitigated | ADRs for architectural decisions + security constitution + incident response protocol |
| Data governance: training data quality | Not directly applicable (using pre-trained models, not training) — but data classification system prevents inappropriate data exposure |
| Accuracy and robustness: system tested | CI/CD test gates + integration tests + property-based testing strategy |
| Traceability: changes trackable | Git history with timestamps, authorship, and review records |

---

## 3. GDPR

### Personal Data in Prompts: The Copy-Paste Problem

GDPR applies whenever personal data is **processed**. Sending a prompt to an AI API is a form of data processing. If that prompt contains personal data, GDPR applies to that processing event — regardless of whether you intended to include personal data or not.

**What constitutes personal data in AI development context:**

| Data Type | Example | Risk Level | Common Exposure Path |
|-----------|---------|------------|---------------------|
| Names | "John Smith" | Moderate | Test fixtures, debugging data, documentation examples |
| Email addresses | "john@company.com" | Moderate | Configuration files, log entries, test data |
| National IDs | SSN, CPR numbers | Critical | Accidentally pasted from production debugging |
| Health data | Heart rate, medications, diagnoses | Critical | Health-tech development, test fixtures with real data |
| Financial data | Account numbers, salary, transaction amounts | Critical | Finance-tech development, log analysis |
| IP addresses | "192.168.1.42" (internal) | Low-moderate | Log entries, debugging output |
| Location data | GPS coordinates, addresses | Moderate | Mobile app development, geospatial features |

**The copy-paste problem in practice:**

A developer encounters a bug in production. A specific record is failing validation. They need to understand why. The fastest path is to copy the record and paste it into a prompt:

```python
# GDPR VIOLATION — never do this:
prompt = """
This record is failing validation:
{
  "user_id": 12345,
  "name": "John Smith",
  "date_of_birth": "1982-01-01",
  "heart_rate_avg": 68,
  "blood_pressure": "142/91",
  "medications": ["metformin", "lisinopril"]
}
What is wrong with this data?
"""
```

This sends health data, personal identifiers, and medication information to an external API. It is a GDPR data processing event. It requires a legal basis. It creates obligations around data retention and deletion. And it happens accidentally, in seconds, under the pressure of debugging a production issue.

**The compliant approach:**

```python
# GDPR-compliant debugging:
prompt = """
A health record with this schema is failing validation:
{
  "user_id": integer,
  "name": string (max 100 chars),
  "date_of_birth": date (YYYY-MM-DD format),
  "heart_rate_avg": integer (expected range: 40-200),
  "blood_pressure": string (format: "systolic/diastolic"),
  "medications": list[string]
}

The validation error is: ValueError: blood_pressure format invalid
The error occurs at line 47 of validators/health_record.py

What validation logic might cause this error for a record
that has a blood_pressure value in the correct format?
"""
```

Debug with schemas, error messages, and anonymized structure. Never with actual data values from production or real user records.

### Data Minimization

GDPR's data minimization principle (Article 5(1)(c)) requires that personal data processing be limited to what is necessary. For AI-assisted development, this means:

- **Use schemas instead of real data** when debugging or explaining data structures to the AI
- **Use synthetic test data** that resembles real data structurally but contains no actual personal information
- **Configure `.claudeignore`** to prevent the agent from reading files that contain personal data
- **Data classification in `CLAUDE.md`**: RESTRICTED data (PII, health records, credentials) must never enter AI context

### Data Processing Agreement (DPA)

GDPR requires a Data Processing Agreement with any third party that processes personal data on your behalf. If developers send personal data to Anthropic, OpenAI, or any other AI provider — even accidentally — a DPA with that provider is required.

**Practical steps:**

1. **Determine if personal data may enter prompts.** If your codebase processes personal data, the answer is almost certainly yes — developers will paste production data into prompts during debugging unless actively prevented.
2. **Establish a DPA with your AI provider.** Anthropic and OpenAI both provide DPA arrangements for enterprise customers. For API usage, review the provider's terms of service and data retention policy.
3. **Implement prevention.** `.claudeignore` for sensitive files. Training for developers. Data classification rules in `CLAUDE.md`. The most reliable approach: prevent personal data from entering prompts in the first place.
4. **Document the processing.** Log what AI tools are used for, what data categories may be processed, and what safeguards are in place. This documentation is required under GDPR Article 30 (Records of processing activities).

### Right to Erasure

GDPR grants individuals the right to erasure (Article 17). If personal data was sent to an AI provider in a prompt, the organization must be able to respond to an erasure request.

**The practical challenge:** Once personal data is sent to an AI API, there is limited ability to guarantee complete erasure from the provider's systems. API providers have their own data retention policies, and even with prompt deletion, the data may have been processed through caching or logging layers.

**The solution is prevention, not correction:**

1. **Do not send personal data to AI APIs in the first place.** This eliminates the erasure problem entirely.
2. **For organizations that must process personal data with AI assistance:** Use self-hosted models (Ollama, Azure OpenAI with no data retention, private endpoints). Data never leaves your infrastructure.
3. **If personal data was sent:** Document the incident, contact the AI provider about erasure capabilities, and update processes to prevent recurrence. Treat it as a data incident.

---

## 4. Audit Trail

Regulatory requirements across GDPR, EU AI Act, SOX, and HIPAA converge on one practical need: the ability to demonstrate, after the fact, **what happened, who approved it, and why.**

The governance framework produces this documentation as a byproduct of correct operation — not as an additional compliance task.

### Git Attribution: Marking AI-Generated Code

Every AI-assisted commit uses the `Co-Authored-By` trailer to create a searchable record:

```
git commit -m "feat(bronze): add oura sleep connector

Implements the OuraSleepConnector class following the standard connector
pattern. Ingests daily sleep summary data from Oura API.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

This enables:
- `git log --grep="Co-Authored-By: Claude"` returns all AI-assisted commits
- `git log --grep="Co-Authored-By"` returns all AI-assisted commits across any provider
- Auditors can calculate the percentage of codebase that is AI-generated
- Production incidents can be traced to AI-assisted or human-only commits

### Session Logs as Compliance Evidence

The CHANGELOG.md session format, followed consistently, provides auditable evidence:

```markdown
## 2026-03-01 — Session 012
**Agent:** Claude Code (claude-sonnet-4-6)
**Duration:** ~2 hours
**Tasks completed:** 4/4
**Files changed:** 7
**Human reviewer:** Developer A (PR #47)

### What was done
- Built oura_connector.py (new file)
- Added 3 entities to sources_config.yaml
- Ran ingestion engine successfully against test fixtures
- Updated ARCHITECTURE.md with Oura integration

### What was NOT done (carried to next session)
- Validation tests for Oura connector
- Silver transform for Oura sleep data
```

For an auditor, this provides:
- **When:** timestamp of the session
- **What:** specific tasks completed and files changed
- **Who (AI):** model version used
- **Who (human):** reviewer identified
- **Scope:** what was done AND what was deliberately not done

### Decision Logs as Compliance Artifacts

`DECISIONS.md` and ADRs document the rationale behind architectural and design decisions:

```markdown
# ADR-003: Watermark-Based Incremental Loading

## Status: Accepted
## Date: 2026-02-28
## Context: We need to load data from APIs incrementally to respect rate limits
## Decision: Track last_loaded_at per source in a metadata table
## Alternatives considered:
  - Full refresh daily (simpler but violates API rate limits at scale)
  - Change data capture (requires API support we do not have)
## Consequences: All bronze connectors must update the watermark after successful load
## AI involvement: Architecture analysis performed by Claude Opus; decision made by Developer A
```

For compliance purposes, this ADR demonstrates that the decision was analyzed, alternatives were considered, consequences were understood, and a human made the final decision. The AI provided analysis; it did not make the decision.

---

## 5. Human Oversight: The Review Theater Problem

### The Regulatory Requirement

Multiple regulations require "meaningful human oversight" of AI-related processes:

- **EU AI Act (Article 14):** High-risk AI systems must have human oversight measures
- **SOX:** Financial controls require documented human review of system changes
- **HIPAA:** Clinical decision support modifications require qualified human review
- **NIS2:** Critical infrastructure changes require documented security review

### What Rubber-Stamping Looks Like

Review theater is the appearance of human oversight without the substance. Auditors are increasingly trained to detect it:

- A developer approves a 500-line PR in 3 minutes with no comments. The time is recorded in the PR metadata. An auditor will calculate reading speed: 500 lines / 3 minutes = 167 lines per minute. This is not review — it is clicking a button.
- CHANGELOG entries show "reviewed and approved" for 12 consecutive tasks with no questions raised. Zero questions across 12 tasks is statistically improbable for genuine review.
- Automated merge after a time delay, with no human interaction between PR creation and merge. This is time-gated auto-approval, not human oversight.
- PR comments are formulaic: "Looks good" or "LGTM" on every PR, without specific references to what was reviewed.

These patterns fail the meaningful oversight test under EU AI Act and under standard professional responsibility norms.

### What Genuine Human Review Looks Like

Meaningful review has specific, observable, auditable characteristics:

1. **The reviewer can explain the change.** If asked to describe what the PR changes and why, the reviewer provides a clear, specific answer — not "the agent added the connector" but "the PR adds an Oura heart rate connector that fetches daily summaries and stores them in the bronze layer, following the same pattern as the existing sleep connector."

2. **The reviewer occasionally rejects or requests changes.** A reviewer who has never rejected a PR or requested changes is not reviewing — they are rubber-stamping. A non-zero rejection rate is evidence that review is functioning. Track this: PR first-attempt pass rate should be between 70-90%, not 100%.

3. **Review is proportional to risk.** A configuration change takes 5 minutes to review. An authentication system change takes 30-60 minutes. A reviewer who spends the same time on both is not calibrating their review to risk.

4. **Review is documented with specific engagement.** PR comments reference specific code: "Verified that the empty list case returns [] not None — checked line 47." "Confirmed the API endpoint uses the environment variable, not a hardcoded URL." These comments demonstrate that the reviewer read specific parts of the code, not just the diff summary.

### Structuring Reviews for Compliance

For PRs that touch high-risk or regulated code:

1. **Use the [AI Code Quality checklist](./ai-code-quality.md) explicitly** and document that you did: "Completed AI code review checklist — all 10 items verified."

2. **Write PR comments that demonstrate specific engagement:**
   - "Verified empty input handling at line 23 — returns empty dict as expected per the acceptance criteria."
   - "Checked that connection string uses env var DATABASE_URL, not hardcoded. Confirmed in sources_config.yaml."
   - "Tested the token expiry edge case locally — correctly returns 401 after token TTL."

3. **Flag when you reviewed only part of the change:** "Reviewed the connector logic and error handling. The SQL transform (lines 89-120) is outside my domain expertise — @developer_b please review the SQL."

4. **Document conditions on approval:** "Approved conditional on adding the edge case test for zero-length input. Must be added before merge."

The goal is a PR history that, if audited two years later, provides evidence that a human understood and approved the change — not just clicked a button.

---

## 6. Framework-to-Regulation Mapping

| Regulatory Requirement | Which Regulation(s) | Framework Component That Satisfies It |
|------------------------|---------------------|--------------------------------------|
| Audit trail for AI-generated code | EU AI Act, SOX | Git `Co-Authored-By` metadata + CHANGELOG session entries |
| Human review documentation | EU AI Act (Art. 14), SOX, HIPAA | PR review history with comments + approval records |
| Decision rationale documented | EU AI Act, SOX | `DECISIONS.md` + ADRs with alternatives considered |
| Data minimization | GDPR (Art. 5) | `.claudeignore` + data classification rules in `CLAUDE.md` + developer training |
| Personal data not sent to external AI | GDPR (Art. 5, 28) | Security constitution + `.claudeignore` + pre-session data check in protocol |
| Data Processing Agreement in place | GDPR (Art. 28) | Organizational contract with AI provider — requires legal action, not framework change |
| No secrets in version control | SOX, PCI-DSS, general | Pre-commit hooks (gitleaks/trufflehog) + CI/CD security gates |
| Meaningful human oversight | EU AI Act (Art. 14), NIST AI RMF | Session protocol with checkpoints + PR review requirements + anti-rubber-stamping practices |
| Traceability of changes | EU AI Act, SOX, HIPAA | Git timestamps + CHANGELOG dates + session numbers |
| Traceability of approvals | SOX, HIPAA, NIS2 | PR approval records + branch protection rules |
| Risk assessment documented | EU AI Act, NIS2 | ADRs for architectural decisions + risk trade-offs + security ADRs |
| Data retention and erasure capability | GDPR (Art. 17) | Prevention approach (.claudeignore) + self-hosted models for sensitive data |
| Incident response documented | NIS2, HIPAA, SOX | Security incident response protocol (8-step) + SECURITY_LOG.md |
| Compliance audit evidence package | All | Aggregated CHANGELOG + PR history + ADR archive + SECURITY_LOG + COST_LOG |

---

## 7. Compliance Checklist

### Data Handling (Items 1-5)

```
[ ] 1. A data classification policy exists and is documented:
       RESTRICTED / CONFIDENTIAL / INTERNAL / PUBLIC.
       RESTRICTED data (PII, health data, credentials) is explicitly prohibited
       from entering AI prompts. This rule is in CLAUDE.md.

[ ] 2. .claudeignore is configured in ALL repositories to prevent
       automatic reading of sensitive files (.env, secrets/, data/prod/, *.pem, *.key).

[ ] 3. Developers have been trained on what constitutes personal data
       and why it must not appear in prompts. Training is documented
       (date, attendees, materials).

[ ] 4. A Data Processing Agreement (DPA) is in place with every AI API provider
       through which personal data MIGHT flow
       (Anthropic, OpenAI, Google, or others as applicable).

[ ] 5. For sensitive data processing: self-hosted model option is available
       and developers know when to use it
       (RESTRICTED data = self-hosted only, no exceptions).
```

### Human Oversight (Items 6-9)

```
[ ] 6. A human review requirement exists for ALL AI-generated code merging
       to protected branches. This is enforced by branch protection rules,
       not developer discipline.

[ ] 7. PR review process produces documented evidence of engagement:
       comments referencing specific code, questions asked, conditions stated.
       NOT just "LGTM" or "Approved."

[ ] 8. For high-risk systems (EU AI Act classification): the AI Code Quality
       checklist is used for every PR and completion is documented in the
       PR review.

[ ] 9. Review rejection rate is tracked. A rate of 0% across more than 20 PRs
       triggers investigation — it may indicate rubber-stamping rather than
       universal perfection.
```

### Audit Trail (Items 10-13)

```
[ ] 10. Every AI-assisted commit uses Co-Authored-By metadata to identify
        AI involvement. The specific model version is included.

        Format: Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

[ ] 11. CHANGELOG.md is updated every session with: timestamp, model version,
        tasks completed, files changed, human reviewer.

[ ] 12. ADRs document major architectural decisions, the alternatives considered,
        and the rationale for the decision made. AI involvement in the analysis
        is noted.

[ ] 13. PR review history provides evidence of human engagement with AI-generated
        code — specific comments, questions, checklist documentation.
        Not just approval clicks.
```

### Security (Items 14-15)

```
[ ] 14. Pre-commit hooks using gitleaks or trufflehog are active in ALL repositories.
        No commit can reach remote without passing the secret scan.
        Hook versions are tracked and updated quarterly.

[ ] 15. CI/CD pipeline includes a security gate that blocks merge on secret detection.
        The gate is a required check — it cannot be bypassed without admin override,
        and admin overrides are logged.
```

---

## 8. Compliance Roadmap

### Now (Q1 2026)

- [ ] Establish DPA with Anthropic/OpenAI if not already in place
- [ ] Implement `.claudeignore` across all repositories
- [ ] Document AI tool usage in internal IT governance policy
- [ ] Ensure `Co-Authored-By` metadata on all AI-assisted commits
- [ ] Ensure CHANGELOG session logging is consistent
- [ ] Verify branch protection rules require human approval

### Next 6 Months (Q2-Q3 2026)

- [ ] Map which teams process personal data and with which AI tools
- [ ] Classify data processed by AI tools (RESTRICTED / CONFIDENTIAL / INTERNAL / PUBLIC)
- [ ] Prepare GDPR Article 30 documentation for AI processing activities
- [ ] Implement pre-commit hooks and CI/CD security gates across all teams
- [ ] Train all developers on data classification and prompt hygiene — document the training
- [ ] Establish compliance audit sampling process (5-10% of sessions reviewed quarterly)

### Before Full EU AI Act Enforcement (2027)

- [ ] Complete EU AI Act risk classification for all AI-assisted software products
- [ ] For high-risk systems: formalize human oversight documentation requirements
- [ ] Establish internal AI audit capability (or engage external auditor)
- [ ] Create compliance evidence package: CHANGELOG archive + PR history + ADR archive + SECURITY_LOG
- [ ] Document the governance framework itself as a compliance measure
- [ ] Conduct first formal compliance audit and remediate findings

**The organizations that prepare now will have a competitive advantage.** Compliance retrofitting under regulatory pressure is expensive, disruptive, and produces weaker results than compliance built into processes from the start. The governance framework described in this repository is designed to produce compliance documentation as a natural byproduct — not as an afterthought.

---

*Related guides: [Security Guide](./security-guide.md) | [AI Code Quality](./ai-code-quality.md) | [Enterprise Playbook](./enterprise-playbook.md) | [Metrics Guide](./metrics-guide.md)*
