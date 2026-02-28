# Example Configurations

Three production-ready configurations for governing AI agents at different scales. Each is a complete, working setup. Pick the one that matches your situation today and customize it.

## The Three Personas

### Solo Developer
One person. Personal project, side project, or early-stage product. No team coordination needed. The governance goal is not process for its own sake — it is preserving context between sessions and preventing the mistakes that happen when no one is reviewing your work.

**Use case:** You are building a SaaS product alone. You work on it three evenings a week. Each session, the AI agent needs to know what you built last time, what decisions you made, and what the plan is — without you re-explaining it every time.

### Small Team (3-5 developers)
A product team or startup where everyone knows each other. You can talk through decisions, but you need consistency because multiple people and multiple AI agents are modifying the same codebase concurrently. The governance goal is preventing agents from stepping on each other and enforcing shared conventions automatically.

**Use case:** Your team of four shares a monorepo. Two developers run AI sessions simultaneously. Without governance, one agent refactors a module while another adds a feature to it. The PR conflicts are the symptom. The root cause is that agents had no shared awareness of what is in progress.

### Enterprise (20+ developers)
Multiple teams, compliance requirements, and managers who need visibility. The governance goal is that any agent in any session across any team follows the same rules, and violations are caught by automation rather than by humans discovering problems after the fact.

**Use case:** Your engineering organization has 30 developers across four teams. You are subject to GDPR and are evaluating EU AI Act implications. When an auditor asks "how do you govern AI-assisted development?", you need a concrete answer with documentation, not a verbal description.

---

## Feature Comparison

| Feature | Solo | Small Team | Enterprise |
|---|---|---|---|
| Session protocol | Start + end only | Start + mid-session checkpoints + end | Full protocol + audit trail logging |
| Model routing | Not included | 6 task types | 14 task types + auto-review triggers |
| Governance sync (drift detection) | Not included | Sprint scope checking | Sprint + architecture + ADR checking |
| Mandatory task reporting | Not included | After every task, non-disableable | Box-drawing status block, non-disableable |
| PR workflow | Not included | Feature branches, 1 reviewer | Feature branches, 2 reviewers for governance files |
| Security maturity level | Level 1 (never-commit list) | Level 2 (+ scan triggers) | Level 3 (+ incident response + data classification) |
| Compliance section | Not included | Not included | EU AI Act + GDPR + audit trail |
| Audit trail | CHANGELOG.md only | CHANGELOG.md + DECISIONS.md | Full session logging + cost tracking |
| Change control | Not included | PR review for CLAUDE.md | ADR + PR + two reviewers for CLAUDE.md |
| Definition of done | Basic verification | Basic verification | Mandatory 8-item checklist with consequences |

---

## Start Here

**Even if you are on a team, start with the solo configuration.** Set it up in 10 minutes, run two or three sessions with it, and confirm that the session protocol feels natural. Then upgrade one section at a time.

The reason: the solo configuration contains the foundation that every other level builds on. If the session start/end protocol does not work for your project, adding governance sync and model routing on top will not fix it — it will amplify the friction.

## The Upgrade Path

Each level is a strict superset of the one below it:

1. **Solo to Small Team:** Add `governance_sync`, `model_routing`, `pr_workflow`, `mandatory_task_reporting`. Add MEMORY.md, DECISIONS.md, and ARCHITECTURE.md template files.
2. **Small Team to Enterprise:** Add `compliance`, `definition_of_done`, `change_control`, `escalation_model`, `review_cadence`. Expand `model_routing` from 6 to 14 task types. Expand `security` to Level 3 with incident response and data classification. Set up all three CI/CD components.

No section is ever removed or replaced. You only add.

## What Is Deliberately Left Out at Each Level

### Solo: what is missing and why

- **Model routing:** You are one person using one model. The cognitive overhead of deciding "should this be opus or sonnet?" is not worth the cost savings until you are spending more than $50/month on AI. Before that threshold, the routing decision costs you more time than it saves you money.
- **Governance sync:** Drift detection compares your work against a sprint plan. Solo projects rarely have formal sprint plans — you work on whatever matters most today. Adding drift detection before you have a stable plan means constant false positives.
- **Mandatory task reporting:** The status block after every task is designed for team visibility. When you are the only person reading it, it is overhead with no audience. Add it when you start losing track of what happened mid-session.
- **PR workflow:** You are committing to your own repo. Branch protection and review requirements add friction that only pays off when a second person needs to verify your work.

### Small Team: what is missing and why

- **Compliance section:** EU AI Act and GDPR documentation is regulatory overhead. If you are not subject to these regulations, maintaining the documentation costs time and adds no protection. Add it when a compliance officer or legal counsel asks about your AI governance.
- **Definition of done:** Small teams can have the "is this actually done?" conversation directly. The formal 8-item checklist is for situations where that conversation cannot happen — because the team is too large, too distributed, or too busy for every task to get a verbal sign-off.
- **Change control:** On a team of four, a CLAUDE.md change can be discussed in a 5-minute standup. The full ADR + PR + two reviewers process is for organizations where the person changing CLAUDE.md and the people affected by the change do not talk daily.
- **Escalation model:** Small teams escalate naturally — you walk over and say "this looks wrong." The formal escalation contacts and procedures are for organizations where the right person to escalate to is not obvious.

---

## One Rule

Never downgrade. Once your agents have cross-session memory through CHANGELOG.md and DECISIONS.md, removing those files means the next session starts blind. If the governance overhead feels too heavy, slim the configuration rather than deleting core files.
