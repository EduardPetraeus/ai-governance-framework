# Governance for Leaders: Engineering Managers and CISOs

This document translates the framework's technical structure into operational language for engineering managers, CISOs, and heads of product. It defines who is accountable for what, which metrics reveal whether AI governance is working, and what a quarterly review must cover.

---

## Why This Matters to Leaders

AI agents generate output at a rate that far exceeds human review capacity. Without governance, the risk is not that agents write bad code — it is that they write large volumes of difficult-to-reverse, hard-to-audit work that nobody owns. The failure mode is organizational: technical debt accumulates at AI speed, incidents cannot be attributed to a root cause, and compliance audit trails do not exist.

This framework addresses that risk by making governance explicit, measurable, and assigned. The sections below define the minimum accountability structure for any team using AI agents in production software development.

---

## Roles and Accountability

Four roles cover the full governance lifecycle. One person may hold multiple roles on small teams. On larger teams, each role should be a named individual with a backup.

### AI Owner

**Who:** Engineering manager, VP of Engineering, or CTO.

**Accountable for:**
- Approving the scope of AI agent access (which repos, which tools, which data)
- Setting the target maturity level and timeline
- Signing off on changes to the governance constitution (CLAUDE.md)
- Receiving and acting on quarterly governance reports

**Decision authority:**
- Can halt AI agent use across a repo or team with immediate effect
- Approves exceptions to governance policy
- Owns escalation decisions when the Operator and Steward disagree

**Review cadence:** Quarterly governance review (see checklist below). Receives incident reports within 24 hours of any Severity 1 event.

---

### AI Steward

**Who:** Lead engineer, staff engineer, or architect. Technical owner of the governance constitution.

**Accountable for:**
- Maintaining CLAUDE.md, the agent registry, and all governance templates
- Running the quarterly audit (`/audit` command) and interpreting results
- Reviewing and approving changes to agent permissions
- Ensuring the governance health score stays above the team's target level threshold
- Onboarding new agents using the agent registry process

**Decision authority:**
- Can restrict or expand individual agent permissions
- Approves new agents before registration
- Signs off on ADRs before they are committed

**Review cadence:** Monthly health check. Attends quarterly governance review. Reviews all incident reports.

---

### AI Operator

**Who:** Developer or team lead who runs AI-assisted sessions day to day.

**Accountable for:**
- Following the session protocol (plan-session → work → end-session)
- Maintaining the CHANGELOG with accurate session records
- Flagging anomalies (unexpected agent behavior, scope expansion, tool use outside the allowlist)
- Running pre-commit governance checks before pushing

**Decision authority:**
- Can halt a session immediately using the kill switch
- Reports to the Steward; cannot unilaterally change governance rules

**Review cadence:** Every session. Weekly sync with Steward on friction and anomalies.

---

### AI Auditor

**Who:** Security engineer, compliance officer, or an external reviewer. Must be independent of the Steward.

**Accountable for:**
- Running the adversarial audit (`/audit`) at least quarterly
- Reviewing session logs for unauthorized tool use and scope violations
- Mapping framework compliance to NIST AI RMF, ISO 42001, or EU AI Act obligations
- Reporting findings to the Owner with severity classifications

**Decision authority:**
- Can recommend halting specific agent workflows pending remediation
- Findings require a written response from the Steward within 14 days

**Review cadence:** Quarterly adversarial audit. Ad-hoc review after any Severity 1 or Severity 2 incident.

---

## Governance Metrics

These metrics tell leaders whether AI governance is working. All can be derived from `CHANGELOG.md`, git history, and the session log without additional tooling. See [docs/metrics-guide.md](metrics-guide.md) for full measurement instructions.

### AI LOC Ratio

**Definition:** Lines of AI-generated code committed per week divided by total lines committed per week.

**Why it matters:** A ratio above 80% with no corresponding increase in review time means human oversight per line is falling. This is the early signal for automation bias.

**Target range:** 40–75%. Below 40%: governance may be creating friction that reduces adoption. Above 75%: review capacity must increase proportionally.

**Warning threshold:** >85% for two consecutive weeks without a corresponding increase in review time. See [patterns/automation-bias-defense.md](../patterns/automation-bias-defense.md).

---

### Agent Rejection Rate

**Definition:** The percentage of AI-generated PRs or sessions that are rejected, reverted, or substantially reworked before merge.

**Why it matters:** A healthy rejection rate (5–20%) indicates governance is catching problems. A rate below 5% may indicate rubber-stamping. A rate above 30% indicates the agents are being given poor context or governance is too restrictive to be productive.

**How to measure:** Count commits with "revert", "fix:", or "redo" within 48 hours of the original commit. Divide by total AI-assisted commits in the period.

**Target range:** 5–20%.

**Warning threshold:** <5% (possible automation bias) or >30% (governance friction or poor agent configuration).

---

### Incident Count and Severity

**Definition:** Number of governance incidents per quarter, classified by severity.

| Severity | Definition | Example |
|:---:|---|---|
| **1** | Agent caused data loss, security breach, or production outage | Credentials committed; production database modified by agent |
| **2** | Agent exceeded authorized scope; unauthorized tool use | Agent created cloud resources not in session plan |
| **3** | Governance protocol not followed; no material harm | Session completed without CHANGELOG update |

**Target:** Zero Severity 1 and 2 incidents per quarter. Severity 3 incidents should trend toward zero as team maturity increases.

**Escalation:** Severity 1 → Owner notified within 1 hour. Severity 2 → Owner notified within 24 hours. Severity 3 → Steward logs and reviews at next weekly sync.

---

### Mean Time to Remediation (MTTR)

**Definition:** Average time from incident detection to documented resolution.

**Why it matters:** A slow MTTR indicates that governance response procedures are unclear or that the kill switch and rollback procedures are not practiced.

**Target:** Severity 1 < 4 hours. Severity 2 < 48 hours. Severity 3 < 2 weeks.

**How to track:** Log detection timestamp and resolution timestamp in each incident record in the risk register.

---

### Friction Ratio

**Definition:** Governance overhead time as a percentage of productive session time.

**How to measure:** Estimate time spent on governance ceremony (reading state files, writing CHANGELOG, running checks) divided by total session time. The session protocol is designed to run in under 5 minutes for plan-session and under 3 minutes for end-session.

**Target:** ≤15% of session time. Above 20% is the threshold where developers route around governance rather than comply.

**Warning threshold:** >20% for two or more developers over two consecutive weeks. See [patterns/friction-budget.md](../patterns/friction-budget.md) and [docs/governance-fatigue.md](governance-fatigue.md).

---

### Governance Coverage

**Definition:** Percentage of AI-assisted sessions that follow the full session protocol (plan-session invoked, CHANGELOG updated, end-session invoked).

**Why it matters:** Coverage below 80% means the governance audit trail is incomplete and compliance claims cannot be substantiated.

**Target:** ≥95% of sessions.

**How to measure:** Count sessions with both a plan-session invocation and a CHANGELOG entry. Divide by total sessions (estimated from git commit frequency and session log files).

---

## Quarterly Governance Checklist

Run this checklist every quarter. The Owner chairs the review. The Steward presents findings. The Auditor presents the adversarial audit results. All findings require a named owner and a resolution date.

### Section 1: Health Score

- [ ] Run `/health-check` and record the current score
- [ ] Compare to the previous quarter — is the score stable or improving?
- [ ] Identify the lowest-scoring checks and assign remediation tasks
- [ ] Verify the target maturity level is still appropriate for the team's size and risk profile

### Section 2: Metrics Review

- [ ] Review AI LOC ratio for the quarter — within target range?
- [ ] Review agent rejection rate — within target range?
- [ ] Count and classify incidents by severity — all Severity 1 and 2 incidents documented?
- [ ] Review MTTR for each incident — met targets?
- [ ] Review friction ratio — any developers reporting governance overhead as a blocker?
- [ ] Review governance coverage — ≥95%?

### Section 3: Risk Register

- [ ] Open [templates/risk-register.md](../templates/risk-register.md) — review all open and in-progress controls
- [ ] Update likelihood and impact scores based on the quarter's incident data
- [ ] Assign ownership for any controls without a named owner
- [ ] Close controls that have been verified as effective
- [ ] Add new risks identified this quarter

### Section 4: Adversarial Audit

- [ ] Auditor presents findings from `/audit` run
- [ ] Each finding classified as Severity 1/2/3
- [ ] Each finding assigned to Steward or Owner with resolution date
- [ ] Previous quarter's findings: verify all are resolved or have documented exceptions

### Section 5: Compliance

- [ ] Review [docs/compliance-mapping.md](compliance-mapping.md) — any new regulatory obligations since last quarter?
- [ ] Confirm audit trail is complete (session logs, CHANGELOG, agent registry)
- [ ] Confirm no credentials, PII, or internal hostnames in any committed file
- [ ] For ISO 42001 or EU AI Act obligations: confirm documented evidence exists for each mapped control

### Section 6: Agent and Permission Review

- [ ] Review [agent registry](agent-registry.md) — all agents still authorized?
- [ ] Any agents added this quarter without going through the registry process?
- [ ] Review tool allowlists for each agent — any unused permissions to remove?
- [ ] Review MCP server access — any connections added without governance review?

### Section 7: Forward Planning

- [ ] Set target health score for next quarter
- [ ] Identify one governance improvement to implement next quarter
- [ ] Assign Owner for the improvement
- [ ] Schedule next quarterly review

---

## Escalation Path

```
Developer (Operator)
    │ anomaly detected
    ▼
AI Steward
    │ Severity 2+ or unresolved after 48h
    ▼
AI Owner
    │ Severity 1 or compliance risk
    ▼
CISO / Legal / Board (as applicable)
```

Any team member can trigger a kill switch. See [patterns/kill-switch.md](../patterns/kill-switch.md) for the full emergency halt procedure.

---

## Related

- [Risk register](../templates/risk-register.md) — structured log of AI governance risks, controls, and ownership
- [Operator playbook](../patterns/operator-playbook.md) — step-by-step procedures for onboarding, incidents, audits, and rollouts
- [Compliance mapping](compliance-mapping.md) — framework elements mapped to NIST AI RMF, ISO 42001, and EU AI Act
- [Metrics guide](metrics-guide.md) — full measurement methodology for all metrics listed above
- [Maturity model](maturity-model.md) — six-level model for assessing and advancing governance maturity
- [Known failure modes](known-failure-modes.md) — seven failure patterns and their controls
