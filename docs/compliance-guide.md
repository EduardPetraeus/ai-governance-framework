# Compliance Guide: Regulatory Landscape for AI-Assisted Development

## 1. Overview

AI-assisted software development is subject to regulations that were written before this development model existed. Most of these regulations apply not because of how code is written, but because of what data is processed during development and what the resulting software does.

The regulations that matter for AI-assisted development teams in 2026:

- **EU AI Act**: Governs AI systems; classifies AI-assisted development tools and the systems they produce
- **GDPR**: Governs personal data; applies when personal data enters the AI context window
- **SOX / MiFID II**: Audit trail requirements for financial software; apply when AI-generated code processes financial data
- **HIPAA**: PHI restrictions; apply when health data enters prompts or AI-generated code handles patient data
- **NIS2**: Applies to critical infrastructure; heightens requirements for AI in those contexts

The central insight: **most compliance requirements are about documentation and auditability, not about restricting AI use**. An organization with proper AI governance — session logs, CHANGELOG discipline, git attribution, human review gates — satisfies most regulatory requirements as a byproduct of operating correctly.

Organizations without governance will fail the same audits, with or without AI.

---

## 2. EU AI Act

### Background

The EU AI Act applies a risk-based classification to AI systems. It entered into force in 2024 with a phased implementation schedule; full compliance for most provisions is required by 2026–2027.

### Classification of AI-Assisted Development Tools

**AI-assisted development tools (Claude Code, GitHub Copilot, Cursor) are classified as low-risk or minimal-risk** under the EU AI Act. They are assistive tools that help humans write code, not autonomous systems that make decisions affecting individuals.

However, the classification of the tool is not the end of the analysis. The relevant question is: **what does the software that the AI helps build do?**

- AI-assisted code that builds a **recommender system**: limited risk (transparency obligations apply)
- AI-assisted code that builds a **credit scoring system**: high risk (certification, human oversight, audit trail requirements apply)
- AI-assisted code that builds a **biometric identification system**: high risk (additional restrictions apply)
- AI-assisted code that builds a **health monitoring application**: potentially high risk depending on medical device classification

The developer tool is not classified as high-risk. The software the developer tool helps produce may be.

### Human Oversight Requirements

For high-risk AI systems (those the AI-assisted code produces, not the tool itself), the EU AI Act requires meaningful human oversight. This means:

- Humans must be able to understand the outputs of the AI system
- Humans must be able to intervene and override the system
- The oversight must be documented and evidenced — not merely claimed

For software development teams, this means: if your AI-generated code is part of a high-risk AI system, the code review process must provide genuine human review — not rubber-stamping. See section 5 of this guide on meaningful human review.

### Practical Requirements

For teams building software with AI assistance:
1. Document that AI tools are used in development (internal policy is sufficient for low-risk)
2. Maintain audit trail showing human review of AI-generated code
3. If the software produced is high-risk: apply the EU AI Act's high-risk requirements to the software system, not just the development tool

---

## 3. GDPR

### Personal Data in Prompts

GDPR applies whenever personal data is processed. Sending a prompt to an AI API is a form of data processing. If that prompt contains personal data, GDPR applies to that processing.

**What constitutes personal data in this context:**
- Names, email addresses, phone numbers, IP addresses
- Health data (any data relating to physical or mental health)
- Financial data that can identify an individual
- Any data that, alone or in combination, can identify a natural person

**The copy-paste problem in practice:**

```python
# GDPR violation — never do this:
user_prompt = f"""
This record is failing validation:
{{
  "user_id": 12345,
  "name": "John Smith",
  "date_of_birth": "1982-01-01",
  "heart_rate_avg": 68,
  "blood_pressure": "142/91",
  "medications": ["metformin", "lisinopril"]
}}
What is wrong with this data?
"""
```

This sends health data and personal identifiers to an external API. It is a GDPR data processing event. It requires a legal basis, and it creates obligations around data retention and deletion.

**The correct approach:**

```python
# GDPR-compliant debugging:
user_prompt = """
A health record with this schema is failing validation:
{
  "user_id": integer,
  "name": string,
  "date_of_birth": date,
  "heart_rate_avg": integer,
  "blood_pressure": string,
  "medications": list[string]
}
The validation error is: [paste error message here, no data values]
What validation logic might cause this error?
"""
```

Debug with schemas and error messages. Never with actual data values from production or real user records.

### Data Processing Agreements

GDPR requires a Data Processing Agreement (DPA) with any third party that processes personal data on your behalf. If developers send personal data to Anthropic, OpenAI, or any other AI provider, a DPA with that provider is required.

**Anthropic** provides DPA arrangements for enterprise customers. For teams using the API directly, review Anthropic's current terms of service and data retention policy.

**What to do:**
1. Establish a DPA with your AI provider if personal data may enter prompts
2. Configure `.claudeignore` to prevent sensitive files from being automatically read
3. Train developers on the data classification system: RESTRICTED data never enters AI context
4. Log what AI tools are used for, to enable GDPR documentation

### Right to Erasure

GDPR grants individuals the right to erasure of their personal data. If personal data was sent to an AI provider in a prompt, the organization should be able to respond to an erasure request.

**The practical challenge**: once personal data is sent to an AI API, there is limited ability to guarantee complete erasure from the provider's systems. This is a strong argument for the prevention approach: do not send personal data to AI APIs in the first place.

For organizations that must process personal data with AI assistance, self-hosted models (Ollama, Azure OpenAI with no data retention, private endpoints) eliminate this risk entirely.

---

## 4. Audit Trail

Regulatory requirements converge on one practical need: the ability to demonstrate, after the fact, what happened, who approved it, and why.

The governance framework produces this documentation as a byproduct of correct operation.

### How to Prove Which Code Was AI-Generated

**Git attribution with `Co-Authored-By`:**
```
git commit -m "feat(bronze): add oura sleep connector

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

This creates a searchable record in git history. `git log --grep="Co-Authored-By: Claude"` returns all AI-assisted commits.

**CHANGELOG entries:**
Each session entry specifies the model used:
```markdown
## 2026-03-01 — Session 012
**Agent:** Claude Code (claude-sonnet-4-6)
**Tasks completed:** 4
**Files changed:** 7
```

**PR metadata:**
PR descriptions document that AI assistance was used, which agent, and what it did.

### Session Logs as Evidence

The session CHANGELOG format, followed consistently, provides:
- Timestamp of the session
- Model version used
- Tasks completed
- Files modified
- Human decisions made during the session

This is sufficient for most audit requirements: "Was this code AI-generated?" (Yes, see CHANGELOG session 012) "Was it reviewed by a human?" (Yes, see PR #47 with approval from [developer]) "What was the review scope?" (See PR description and code review comments)

---

## 5. Human Oversight

### The Regulatory Requirement

Multiple regulations — EU AI Act for high-risk systems, SOX for financial controls, HIPAA for clinical decision support — require "meaningful human oversight" of AI system outputs. This requirement is the hardest to satisfy in practice, because the most natural behavior in AI-assisted development is to approve AI outputs quickly.

### The Review Theater Problem

Review theater is the appearance of human oversight without the substance:

- A developer approves a 500-line PR in 3 minutes without commenting on any specific change
- Commits are stamped "reviewed" because someone clicked the button, not because someone read the code
- The session protocol shows "human review completed" but the CHANGELOG entry shows "approved all suggestions" for 12 consecutive tasks
- Automated merge after a time delay, without any human actually reading the PR

These patterns fail the meaningful oversight test under EU AI Act's human oversight provisions and under standard professional responsibility norms for engineers working on safety-critical systems.

### What Constitutes Genuine Human Review

Meaningful review has specific, observable characteristics:

1. **The reviewer can explain the change**: if asked to describe what the PR changes and why, the reviewer can provide a clear answer — not just "the agent added the connector"
2. **The reviewer occasionally rejects**: a reviewer who has never rejected or requested changes is not reviewing — they are rubber-stamping
3. **The review is proportional to risk**: a config change takes 5 minutes to review; an authentication system change takes 30 minutes
4. **The review is documented**: PR comments, questions, and decision rationale exist in the PR history

### Structuring Reviews for Compliance

For high-stakes or regulated code:

- Use the [AI Code Quality checklist](./ai-code-quality.md) explicitly and document that you did so
- Write PR comments that demonstrate engagement with the code: "Verified that this handles the empty list case — checked against the acceptance criteria"
- If you approve with conditions, state them: "Approved conditional on adding the edge case test for zero-length input"
- Flag when you reviewed only part of the change: "Reviewed the connector logic; the SQL transform is outside my domain — needs additional review from [developer]"

The goal is a PR history that, if audited two years later, provides evidence that a human understood and approved the change — not just clicked a button.

---

## 6. Framework-to-Regulation Mapping

| Regulatory Requirement | Framework Component That Satisfies It |
|------------------------|--------------------------------------|
| Audit trail for AI-generated code | Git `Co-Authored-By` + CHANGELOG session entries |
| Human review documentation | PR review history + approval records |
| Decision rationale | `docs/DECISIONS.md` + ADRs |
| Data minimization (GDPR) | `.claudeignore` + data classification rules in `CLAUDE.md` |
| Personal data not sent to external AI | Security constitution + training + pre-session data check |
| No secrets in code (SOX, general) | Pre-commit hooks + gitleaks/trufflehog CI gates |
| Meaningful human oversight | Session protocol checkpoints + PR review requirements |
| Traceability of when changes were made | Git timestamps + CHANGELOG dates |
| Traceability of who approved | PR approval records + protected branch policy |
| DPA with AI provider | Organizational contract — not a framework component, requires legal action |
| Data retention and erasure capability | Self-hosted models or provider DPA — requires organizational decision |
| Risk classification documentation | ADRs documenting architectural decisions and risk trade-offs |
| Compliance audit evidence | Aggregated CHANGELOG + PR history + ADR archive |

---

## 7. Compliance Checklist

### EU AI Act + GDPR — 15-Item Checklist

**Documentation and Classification:**

```
[ ] 1. The organization has documented that AI tools are used in software development.
       (Internal policy, IT governance document, or similar)

[ ] 2. The AI tools in use are classified by risk level.
       (Development tools: low-risk. Software they produce: classified separately based on use case)

[ ] 3. For any software that may qualify as high-risk under EU AI Act:
       the human oversight requirements are explicitly satisfied and documented.

[ ] 4. A Data Processing Agreement is in place with every AI API provider
       through which personal data might flow.
       (Anthropic, OpenAI, Google, or others as applicable)
```

**Data Governance:**

```
[ ] 5. A data classification policy exists: RESTRICTED / CONFIDENTIAL / INTERNAL / PUBLIC.

[ ] 6. RESTRICTED data (PII, health data, credentials) is explicitly prohibited
       from entering AI prompts. This rule is in CLAUDE.md and enforced in training.

[ ] 7. .claudeignore is configured in all repositories to prevent
       automatic reading of sensitive files.

[ ] 8. Developers have been trained on what constitutes personal data
       and why it must not appear in prompts.
```

**Audit Trail:**

```
[ ] 9. Every AI-assisted commit uses Co-Authored-By metadata to identify AI involvement.

[ ] 10. CHANGELOG.md is updated every session with: timestamp, model version,
        tasks completed, files changed.

[ ] 11. ADRs document major architectural decisions, the alternatives considered,
        and the rationale for the decision made.

[ ] 12. PR review history provides evidence of human engagement with AI-generated code
        (not just approval clicks — actual comments or checklist documentation).
```

**Security:**

```
[ ] 13. Pre-commit hooks using gitleaks or trufflehog are active in all repositories.
        No commit can reach remote without passing the secret scan.

[ ] 14. CI/CD pipeline includes a security gate that blocks merge on secret detection.
```

**Oversight:**

```
[ ] 15. A human review requirement exists for all AI-generated code merging to protected branches.
        This is enforced by branch protection rules, not developer discipline.
```

---

*Related guides: [Security Guide](./security-guide.md) | [AI Code Quality](./ai-code-quality.md) | [Enterprise Playbook](./enterprise-playbook.md) | [ADR Template](./adr/ADR-000-template.md)*
