# Enterprise Example

This is the full governance configuration for organizations with 20+ developers, compliance
requirements, or both. It adds everything that cannot be left to convention when agents
are running in dozens of concurrent sessions across multiple teams.

## What's added vs. small team

### Full model routing (11 task types)

The small team config has 5 routing rules. The enterprise config has 11, covering every
common task type including ADR writing, cost reports, and audit-trail generation.

**Why at enterprise scale:** With 20+ developers each running 2-3 sessions per week,
uncontrolled model selection adds up. If half the sessions use opus for tasks that only
need sonnet, you're spending 5-10x on AI costs unnecessarily. At 100 sessions/week,
that's the difference between $50 and $500/week. Model routing pays for itself.

### Compliance section (EU AI Act and GDPR)

At enterprise scale, "we use AI" is a legal and regulatory statement, not just a workflow
description. The compliance section documents:
- Whether the project falls under EU AI Act high-risk categories
- GDPR requirements for processing personal data via AI APIs
- Data Processing Agreement requirements with AI vendors
- Audit trail requirements for AI-assisted work

**Why this matters:** The EU AI Act (in force from 2026) has specific requirements for
AI systems in high-risk categories. GDPR has always required DPAs with data processors.
If you're using the Anthropic API and processing user data, you need a DPA with Anthropic.
This section makes that requirement explicit rather than letting it drift.

### Security maturity requirements (Level 3)

The solo and team configs have a never-commit list and scan triggers. The enterprise
config adds: formal incident response, data classification (RESTRICTED / CONFIDENTIAL /
INTERNAL / PUBLIC), and a security maturity level requirement.

**Why Level 3:** Level 1 (never-commit list) prevents naive mistakes. Level 2 (scan triggers)
adds systematic checking. Level 3 (incident response + data classification) handles the
"what do we do when something goes wrong?" question before it comes up. At enterprise scale,
a security incident will happen eventually. Having the response protocol in CLAUDE.md means
agents know the procedure and can surface issues immediately rather than hoping the problem
goes away.

### Audit trail requirements

Every session is logged with: session number, date, model used, tasks completed, decisions
made. AI-generated code is labeled in commit messages. The COST_LOG.md tracks spend.

**Why this matters:** When an enterprise customer asks "what AI systems were involved in
building this feature?", you need to be able to answer. When a security audit asks "can
you show us the decision log for this architectural choice?", DECISIONS.md is your answer.
Without these, the answer is "we don't know" — which is not acceptable at enterprise scale.

### Definition of done (mandatory checklist)

The enterprise config defines exactly what "done" means. A task is not done until tests
are written, docs are updated, security scan passed, and naming conventions verified.

**Why this matters:** AI agents are eager to move on. They will mark something as "complete"
when the code runs — not when it's truly production-ready. The definition of done is a
checklist that agents must confirm before changing a task's status. Without it, "done" is
whatever the agent thinks it means.

### Escalation model

The enterprise config defines when to stop and escalate. Secret found? Stop and escalate.
Architectural change that contradicts a security decision? Stop and escalate.

**Why this matters:** Agents do not know when something is a big deal. They will try to
resolve everything in the current session. The escalation model tells them: some things
require a human decision, and no code should be written until that decision is made.

### Change control for CLAUDE.md

The enterprise config requires an ADR + PR + two human reviewers to change CLAUDE.md.

**Why this matters:** At enterprise scale, CLAUDE.md is organizational infrastructure. A
change to CLAUDE.md affects every agent in every session across every team. It deserves
the same review rigor as a change to the core API or a security policy. Without change
control, one developer can change CLAUDE.md on a whim and every agent session in the
organization immediately behaves differently.

## The governance overhead question

The enterprise config adds real overhead. Running the full session protocol, the definition
of done checklist, the audit trail, and the compliance documentation takes time. For a
team of 5, this overhead may outweigh the benefit.

**When the overhead is worth it:**
- You have a compliance requirement that requires audit trails (GDPR, SOC2, HIPAA)
- You've had a security incident that a stricter process would have caught
- You have agents making architectural decisions that were not reviewed and caused problems
- You're onboarding 10+ new developers and need consistent agent behavior from day one

**When it's probably not worth it:**
- Small team, no compliance requirement, everyone knows the conventions
- Early-stage startup where speed is the primary concern
- Internal tools with no user data or regulatory exposure

If you're on the fence: start with the small team config and add enterprise sections
incrementally as you run into the problems they solve. Do not add governance overhead
speculatively — add it in response to real pain.

## Time to set up: 2 hours

1. Copy all template files and the enterprise CLAUDE.md:
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

2. Edit `CLAUDE.md` — fill in project details, compliance_scope, escalation contacts. (15 min)

3. Edit `ARCHITECTURE.md` — document your actual architecture. (30 min)

4. Set up CI/CD:
   ```bash
   mkdir -p .github/workflows
   cp ci-cd/github-actions/governance-check.yml .github/workflows/
   cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/
   cp ci-cd/pre-commit/.pre-commit-config.yaml .
   pip install pre-commit && pre-commit install
   ```
   Add `ANTHROPIC_API_KEY` to GitHub Secrets. (20 min)

5. Install all slash commands:
   ```bash
   mkdir -p .claude/commands
   cp commands/*.md .claude/commands/
   ```

6. Configure branch protection on main:
   - Require PR reviews (min 2 for CLAUDE.md changes)
   - Require status checks: Governance Check, AI PR Review
   - No direct commits to main

That's 2 hours and you have a fully governed, compliance-ready AI development setup.
