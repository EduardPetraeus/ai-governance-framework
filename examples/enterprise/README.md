# Enterprise Configuration

The full governance constitution for organizations with 20+ developers, compliance requirements, or both. This configuration adds everything that cannot be left to convention when agents run in dozens of concurrent sessions across multiple teams.

## When Enterprise Governance Is Worth It

Enterprise governance adds real overhead. Before adopting it, confirm that at least two of these criteria apply:

1. **Regulatory compliance.** You are subject to GDPR, EU AI Act, SOC2, HIPAA, or ISO27001, and you need to demonstrate how AI-assisted development is governed. An auditor asking "how do you control AI agent behavior?" requires a documented answer with evidence, not a verbal description.

2. **Scale.** You have 10+ developers running AI sessions. At this scale, verbal conventions break down — not because people are careless, but because information does not propagate reliably across teams. Developer A's "I changed the error handling pattern" message in Slack does not reach Developer C, whose agent is mid-session building on the old pattern.

3. **Incident history.** You have had a security incident, an architectural decision that was not reviewed, or a "done" task that was not actually done — and the root cause was lack of governance, not lack of skill. Enterprise governance is a response to real problems, not theoretical ones.

4. **Onboarding velocity.** You are hiring faster than your culture can absorb. When 10 new developers join in a quarter, they cannot absorb conventions through osmosis. The constitution gives every agent — and every developer — the same starting point from day one.

If none of these apply, use the small team configuration and add enterprise sections individually as you encounter the problems they solve.

## What Is Added vs. Small Team

### Full model routing (14 task types)

The small team configuration routes 6 task types. Enterprise expands to 14, covering every common task type including ADR writing, SQL queries, test generation, cost reports, and status reports. It also adds automatic review triggers: if a session creates 5+ files, changes the architecture, or modifies security-sensitive code, an Opus review prompt is generated automatically.

**Why at enterprise scale:** With 20+ developers each running 2-3 sessions per week, uncontrolled model selection creates significant unnecessary cost. If half the sessions use opus for tasks that only need sonnet, you are spending 5-10x more than necessary. At 100+ sessions per week, model routing is the difference between $200/week and $2,000/week for the same output quality.

### Compliance section (EU AI Act + GDPR)

At enterprise scale, "we use AI in development" is a legal and regulatory statement. The compliance section documents EU AI Act applicability and high-risk category assessment, GDPR requirements for processing personal data via AI APIs, DPA requirements with AI vendors, and audit trail standards.

**Why this matters:** The EU AI Act (enforcement phases from 2025-2027) has specific requirements for AI systems in high-risk categories. GDPR has always required DPAs with data processors. If you are sending code containing user data patterns to an AI API, you may need a DPA with the AI vendor. This section makes requirements explicit and points to the specific documents where compliance evidence is maintained.

### Security maturity Level 3

Solo has Level 1 (never-commit list). Team has Level 2 (scan triggers). Enterprise requires Level 3: formal incident response, data classification into four tiers (RESTRICTED, CONFIDENTIAL, INTERNAL, PUBLIC), and per-session security scanning.

**Why Level 3:** At enterprise scale, a security incident will happen. The question is not "if" but "when." Level 3 means the response protocol exists before the incident occurs. Agents know to stop immediately, revoke before cleaning, document the incident, and notify the security team. Without this, an agent's response to a detected secret is unpredictable — it might try to "fix" it silently, which makes the incident worse.

### Audit trail requirements

Every session is logged with session number, date, model, tasks completed, and decisions made. AI-generated code is labeled in commit messages. Cost tracking is maintained in COST_LOG.md.

**Why this matters:** "Can you show us the decision log for this architectural choice?" is a question that auditors, security reviewers, and new team members all ask. Without structured audit trails, the answer is "check the git log and hope someone wrote a good commit message." With them, every decision has a date, context, rationale, and record of alternatives considered.

### Definition of done (mandatory 8-item checklist)

A task is not done until: code runs, tests pass, docstrings exist, CHANGELOG updated, ARCHITECTURE.md updated if applicable, DECISIONS.md updated if applicable, security scan passed, naming conventions verified. Agents must confirm each item explicitly.

**Why this matters:** AI agents are completion-oriented. They will mark a task "done" when the code runs — not when it is production-ready. Without a formal checklist, "done" means whatever the agent decides it means. The enterprise checklist has consequences: skipped tests mean the task is marked "incomplete — tests pending" and cannot be merged. A skipped security scan is treated as a potential incident.

### Escalation model with concrete actions

The escalation model defines specific situations that require immediate escalation (secret found, PII exposure risk, architectural contradiction, production change outside PR process), the concrete action to take for each, and the specific contact to notify.

**Why this matters:** Agents do not know when something is a big deal. Without explicit escalation triggers, they will try to resolve everything in the current session — including security incidents that should involve the security team. The escalation model tells agents: these situations require a human decision, here is exactly who to contact, and no code should be written while waiting for a response.

### Change control for CLAUDE.md

CLAUDE.md changes require an ADR explaining the change, a PR, and approval from two human reviewers (neither the PR author). The change is announced to all teams after merge.

**Why this matters:** At enterprise scale, CLAUDE.md is organizational infrastructure. A change affects every agent in every session across every team. It deserves the same review rigor as a change to a core API contract or a security policy. Without change control, one developer changes CLAUDE.md, every agent session in the organization immediately behaves differently, and no one else knows until something breaks.

### Review cadence

Scheduled reviews prevent governance from becoming stale:
- **Monthly:** CLAUDE.md accuracy review, cost log review
- **Quarterly:** ADR cleanup, ARCHITECTURE.md accuracy check
- **Twice yearly:** Security constitution review, incident response tabletop exercise
- **Annually:** Full framework review, compliance reassessment

## Governance Overhead Over Time

The initial setup takes about 2 hours. The first month feels heavy — developers are learning the protocol, agents are being corrected, and the overhead is visible.

By month two, the session protocol becomes automatic. Developers stop thinking about it. Agents follow the constitution without correction. The overhead drops to near-zero for routine sessions.

By month three, the governance pays for itself. New developers onboard faster because the constitution is the single source of truth. Incident response is faster because the protocol exists before the incident. Architectural decisions are better because drift detection catches divergence early.

The overhead that remains is structural: CHANGELOG updates, DECISIONS.md entries, security scans. This is not overhead — it is documentation that would need to exist anyway. The governance framework just ensures it happens consistently rather than sporadically.

**The key insight:** governance overhead is front-loaded. The cost of setting it up is high. The cost of maintaining it is low. The cost of not having it is unpredictable and tends to arrive at the worst possible time.

## Setup: 2 Hours

### Step 1: Copy all template files (5 minutes)
```bash
cp examples/enterprise/CLAUDE.md .
cp templates/PROJECT_PLAN.md .
cp templates/CHANGELOG.md .
cp templates/MEMORY.md .
cp templates/DECISIONS.md .
cp templates/ARCHITECTURE.md .
cp templates/SPRINT_LOG.md .
cp templates/COST_LOG.md .
```

### Step 2: Edit CLAUDE.md (15 minutes)
Fill in all `CUSTOMIZE` sections: project_context, compliance_scope, escalation contacts, and any organization-specific adjustments to the routing table.

### Step 3: Edit ARCHITECTURE.md (30 minutes)
Document your actual system architecture. Include component boundaries, data flows, external integrations, and deployment topology. This document is read by agents at every session start — invest in making it accurate.

### Step 4: Set up CI/CD (20 minutes)
```bash
# GitHub Actions workflows
mkdir -p .github/workflows
cp ci-cd/github-actions/governance-check.yml .github/workflows/
cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/

# Pre-commit hooks
cp ci-cd/pre-commit/.pre-commit-config.yaml .
pip install pre-commit && pre-commit install

# Add ANTHROPIC_API_KEY to GitHub repository secrets
# Settings > Secrets and variables > Actions > New repository secret
```

### Step 5: Install slash commands (5 minutes)
```bash
mkdir -p .claude/commands
cp commands/*.md .claude/commands/
```

### Step 6: Configure branch protection (15 minutes)

Go to Settings > Branches > Add branch protection rule for `main`:

- **Require a pull request before merging:** Enabled
  - Required approving reviews: 1 (set to 2 for paths matching `CLAUDE.md`, `ARCHITECTURE.md`, and security policy files using CODEOWNERS)
  - Dismiss stale pull request approvals when new commits are pushed: Enabled
- **Require status checks to pass before merging:** Enabled
  - Required checks: `Governance Check`, `AI PR Review`
- **Require conversation resolution before merging:** Enabled
- **Do not allow bypassing the above settings:** Enabled (even for administrators)

Create a `CODEOWNERS` file in the repository root:
```
# Governance files require two reviewers
CLAUDE.md           @org/tech-leads @org/engineering-managers
ARCHITECTURE.md     @org/tech-leads
docs/adr/           @org/tech-leads
```

### Step 7: Verify the setup (10 minutes)
Create a test branch, make a small change, open a PR, and verify that the governance check runs, the AI PR review runs, and branch protection enforces the review requirements.

That is 2 hours. You now have a fully governed, compliance-ready, auditable AI development setup.
