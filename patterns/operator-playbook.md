# Operator Playbook

Step-by-step procedures for the four recurring governance operations. Each procedure is self-contained: an Operator can follow it without reading the full framework documentation. All procedures assume the framework is at Level 2 or above.

---

## Who This Is For

The **AI Operator** is the developer or team lead who runs AI-assisted sessions day to day. This playbook covers what to do in four situations:

1. [Onboarding a new agent](#1-onboarding-a-new-agent)
2. [Responding to a governance incident](#2-incident-response)
3. [Running the quarterly governance audit](#3-quarterly-audit)
4. [Rolling out governance to a new team or project](#4-governance-rollout)

For role definitions and escalation paths, see [docs/governance-for-leaders.md](../docs/governance-for-leaders.md).

---

## 1. Onboarding a New Agent

Use this procedure when adding a new AI agent to an existing governed project. An agent that is not in the registry is not authorized to operate.

### Prerequisites

- Access to the agent registry file: `docs/agent-registry.md` (or `templates/AGENT_REGISTRY.md` if not yet instantiated)
- Steward approval for the agent's scope and permissions
- The agent's system prompt or definition ready for review

### Steps

**Step 1: Define the agent's identity**

Create the agent definition file in `agents/`. Follow the naming convention: `agents/[role]-agent.md` (e.g., `agents/data-pipeline-agent.md`). The file must include:
- Agent name and version
- Purpose — one sentence describing what this agent does
- Write access — specific directories and file types the agent may modify
- Prohibited actions — what this agent must never do (e.g., "must not modify production configuration files")
- Tool allowlist — which MCP tools or external integrations this agent may invoke
- Owner — the named individual accountable for this agent's behavior

**Step 2: Register the agent**

Add an entry to the agent registry with all required fields. The entry must include the agent ID, name, purpose, owner, permission scope, tool allowlist, and creation date. An incomplete registry entry is a governance violation. See [docs/agent-registry.md](../docs/agent-registry.md) for the registry schema.

**Step 3: Verify the agent definition**

Before the agent runs a session, verify:
- [ ] Agent definition file exists and all fields are complete
- [ ] Registry entry matches the definition file
- [ ] Prohibited actions are explicit and unambiguous
- [ ] Tool allowlist is minimal — only what the agent needs, not everything available
- [ ] Owner is a named individual, not a team

**Step 4: Run a supervised test session**

For the first session with any new agent:
- Owner or Steward must be present or available for review
- Use the smallest possible scope (one file or one task)
- Verify the agent reads and follows CLAUDE.md before starting work
- Verify the session produces a CHANGELOG entry
- Confirm no tool use outside the allowlist

**Step 5: Document the onboarding**

Add a CHANGELOG entry with: agent name, date, scope, owner, and test session outcome. If the test session revealed issues, resolve them before the agent operates unsupervised.

---

## 2. Incident Response

Use this procedure when an agent causes or nearly causes a governance violation, security event, or production impact. Speed and documentation are both required.

### Incident Severity

| Severity | Definition | Example |
|:---:|---|---|
| **1** | Data loss, security breach, or production outage | Credentials committed; production data modified without authorization |
| **2** | Agent exceeded authorized scope; unauthorized tool use; unreported side effects | Agent created external resources; accessed files outside its write-access scope |
| **3** | Protocol not followed; no material harm | Session completed without CHANGELOG; agent skipped scope confirmation |

### Severity 1 Response (target: resolved within 4 hours)

**Step 1: Halt the agent immediately**

Invoke the kill switch. See [patterns/kill-switch.md](kill-switch.md) for the full procedure. This takes priority over everything else.

```bash
# Revoke all active agent permissions and terminate running sessions
# Follow the kill-switch procedure exactly
```

**Step 2: Notify the Owner within 1 hour**

Send a written notification with:
- What happened (one sentence)
- Which agent was involved
- What data or systems were affected
- What immediate action was taken

**Step 3: Preserve evidence**

Before any remediation:
- Copy session logs and CHANGELOG entries to a dated incident record
- Capture the agent's last 20 messages if accessible
- Note the agent's tool invocations and file access from the session record

**Step 4: Remediate**

- Revoke credentials, rotate secrets, or restore backups as applicable
- Follow [docs/rollback-recovery.md](../docs/rollback-recovery.md) for code rollback
- Document each remediation action with timestamp

**Step 5: Root cause and control update**

Within 48 hours:
- Identify the specific governance gap that allowed the incident
- Find the corresponding risk in the risk register and update its likelihood and status
- Add or tighten the control that would have prevented the incident
- If the gap does not exist in the risk register, add it

**Step 6: Close the incident record**

The incident record must include: incident ID, date/time, severity, root cause, remediation steps, responsible control update, and Steward sign-off. File it in `docs/incidents/YYYY-MM-DD-[brief-description].md`.

---

### Severity 2 Response (target: resolved within 48 hours)

**Step 1: Halt the specific agent**

Do not halt all agents — only the one involved. Remove its registry entry or mark it suspended pending review.

**Step 2: Notify the Owner within 24 hours**

Same format as Severity 1 notification.

**Step 3: Audit the agent's session history**

Review the last three sessions for the same agent. Were similar actions taken without detection? Use [patterns/session-replay.md](session-replay.md) to reconstruct the session timeline.

**Step 4: Update permissions**

Identify the permission or tool access that enabled the unauthorized action. Remove it from the allowlist.

**Step 5: Reinstate the agent**

After permission update and Steward review, update the registry entry and resume operations. Document the reinstatement.

---

### Severity 3 Response (target: resolved within 2 weeks)

**Step 1: Log the violation**

Add an entry to the Steward's weekly review log. Include: date, agent, violation type, and the developer who flagged it.

**Step 2: Identify root cause**

Is the violation:
- A developer skipping steps intentionally (governance fatigue)?
- A step that is too burdensome (friction problem)?
- Ambiguous instructions (constitution clarity problem)?

**Step 3: Address the root cause**

- Fatigue → review [docs/governance-fatigue.md](../docs/governance-fatigue.md) and reduce friction
- Friction → update the constitution to streamline the step
- Clarity → rewrite the ambiguous instruction with examples

---

## 3. Quarterly Audit

Use this procedure to run the full governance audit each quarter. The Auditor leads this procedure. The Steward provides data. The Owner reviews findings.

### Preparation (1 week before audit)

- [ ] Confirm the audit date with Owner, Steward, and Auditor
- [ ] Collect all incident records from the quarter
- [ ] Export governance health score from the last monthly health check
- [ ] Prepare the risk register for review (update Last Reviewed dates on all rows)

### Audit Execution

**Step 1: Run the automated checks**

```bash
# From the project root
/health-check   # governance health score
/audit          # adversarial red-team audit
/validate       # verify all cross-references and file completeness
```

Record all output. Do not dismiss low-severity findings without documentation.

**Step 2: Manual session log review**

Select five sessions at random from the quarter. For each:
- [ ] Was `/plan-session` invoked?
- [ ] Was the CHANGELOG updated at session end?
- [ ] Were all file modifications within the agent's declared write-access scope?
- [ ] Were all tool invocations within the agent's allowlist?
- [ ] Did the session end with `/end-session`?

Document pass/fail for each check and each session.

**Step 3: Agent registry review**

For each agent in the registry:
- [ ] Is the owner still the correct named individual?
- [ ] Has the agent operated within its declared scope this quarter?
- [ ] Are there any agents operating but not in the registry?
- [ ] Are tool allowlists still minimal?

**Step 4: Risk register review**

For each risk in the risk register:
- [ ] Update likelihood based on this quarter's data (did the failure mode occur or almost occur?)
- [ ] Verify controls are implemented (not just documented)
- [ ] Assign ownership to any unowned controls
- [ ] Close controls verified as effective; open new risks identified this quarter

**Step 5: Compliance check**

- [ ] Review [docs/compliance-mapping.md](../docs/compliance-mapping.md) — any new regulatory changes?
- [ ] Confirm audit trail exists and is complete for this quarter
- [ ] Confirm no credentials, PII, or internal data in any committed file (scan with security reviewer)

### Audit Report

Produce a written report with:
- Health score: this quarter vs. last quarter
- Session compliance rate (from Step 2 sample)
- Incidents: count and severity breakdown
- Risk register: summary of changes
- Top 3 findings with severity, root cause, and recommended action
- Each finding assigned to Owner (Severity 1/2) or Steward (Severity 3) with deadline

Distribute to Owner, Steward, and all Operators within 5 business days of the audit.

---

## 4. Governance Rollout

Use this procedure when introducing the framework to a new team or project that currently has no AI governance. Time budget: 2–4 weeks depending on team size and maturity target.

### Week 1: Assess and Configure

**Step 1: Assess current state**

Run the health score calculator on the existing project:

```bash
python3 automation/health_score_calculator.py /path/to/project
```

Document the current score. This is your baseline. If the project has no AI use yet, the score is 0.

**Step 2: Agree on target maturity level**

With the AI Owner, agree on the target maturity level for the initial rollout. Default: Level 2 (Structured). Do not target Level 3+ in the first rollout — governance fatigue is highest when all controls are introduced at once.

| Level | What Is Required | Time to Reach |
|:---:|---|---|
| 1 (Foundation) | CLAUDE.md committed, session protocol followed | 1–2 days |
| 2 (Structured) | ADRs started, MEMORY.md in use, specialized agents configured | 1–2 weeks |
| 3 (Enforced) | CI/CD governance checks active, pre-commit hooks installed | 2–4 weeks |

**Step 3: Configure the constitution**

Copy and fill in the constitution template:

```bash
cp templates/CLAUDE.md ./CLAUDE.md
# Fill in: project name, stack, team, security policy, session protocol
git add CLAUDE.md && git commit -m "chore: add AI governance constitution"
```

Do not use a template with blank fields. Every field must be filled before the first governed session.

**Step 4: Install session commands**

```bash
mkdir -p .claude/commands
cp examples/core-edition/commands/*.md .claude/commands/
```

Verify: open Claude Code and type `/plan-session`. The command should execute without errors.

### Week 2: First Governed Sessions

**Step 5: Run the first governed session**

The Steward or an experienced Operator runs the first session with the full protocol. Duration: 60–90 minutes. Goal: demonstrate the full workflow to the team. Document the session in CHANGELOG.md.

**Step 6: Train Operators**

For each developer who will use AI agents:
- Walk through one complete session together (plan-session → work → end-session)
- Explain the kill switch location and when to use it
- Explain how to flag an incident (Severity 1/2/3)
- Answer questions about friction — if a step feels unnecessary, log it for Steward review

**Step 7: Set up the risk register**

Copy and configure the risk register:

```bash
cp templates/risk-register.md ./docs/risk-register.md
# Assign Owner names to each risk row
# Update likelihood based on your team's context
git add docs/risk-register.md && git commit -m "docs: add governance risk register"
```

### Week 3–4: Enforcement and Measurement

**Step 8: Activate CI/CD checks**

Add the governance workflow to your CI platform:

```bash
# GitHub Actions
cp ci-cd/github-actions/governance-check.yml .github/workflows/governance-check.yml
```

For GitLab, CircleCI, Bitbucket, or Azure DevOps, see [ci-cd/](../ci-cd/) for platform-specific files.

**Step 9: Install pre-commit hooks**

```bash
cp scripts/hooks/pre_commit_guard.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Test the hook by attempting to commit a file containing a fake secret. It should block the commit.

**Step 10: Establish the metrics baseline**

After 2 weeks of governed sessions:
- Calculate the friction ratio
- Calculate governance coverage
- Record the baseline AI LOC ratio and rejection rate

Document these baselines in the project's DASHBOARD.md. Without a baseline, the quarterly review has no trend to analyze.

**Step 11: Schedule the first quarterly review**

Set the date before the rollout is complete. The first quarterly review should occur 90 days after the rollout date. Assign the Owner, Steward, and Auditor. Share this playbook with all three.

---

## Related

- [Governance for leaders](../docs/governance-for-leaders.md) — roles, metrics, and full quarterly checklist
- [Risk register](../templates/risk-register.md) — structured risk log referenced throughout this playbook
- [Kill switch](kill-switch.md) — full emergency halt procedure for Severity 1 incidents
- [Session replay](session-replay.md) — session reconstruction for incident investigation
- [Known failure modes](../docs/known-failure-modes.md) — failure patterns that map to risks in the register
- [Compliance mapping](../docs/compliance-mapping.md) — regulatory control mapping for compliance audits
- [Agent registry](../docs/agent-registry.md) — agent identity and permission management
- [Governance fatigue](../docs/governance-fatigue.md) — diagnosis and remediation for rollout friction
