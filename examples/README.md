# Example Configurations

## Start here: Core Edition

The **[Core Edition](core-edition/)** is the recommended starting point for all users. 10 minutes to set up, no infrastructure required, works for solo developers and teams up to 10.

```bash
cp examples/core-edition/CLAUDE.md ./CLAUDE.md
mkdir -p .claude/commands && cp examples/core-edition/commands/*.md .claude/commands/
mkdir -p .github/workflows && cp examples/core-edition/ci-cd/*.yml .github/workflows/
```

If you only use one thing from this repository, use the Core Edition.

---

## Community editions — alternative configurations

The following are alternative configurations contributed as examples for specific team sizes and compliance contexts. They are not actively maintained as separate editions. Use the Core Edition and extend it to your needs.

### Solo Developer
> **Community Edition** — This is an alternative configuration example. For the
> recommended starting point, see the [Core Edition](core-edition/README.md).

One person. Personal project, side project, or early-stage product. No team coordination needed. The governance goal is preserving context between sessions and preventing the mistakes that happen when no one is reviewing your work.

### Small Team (3-5 developers)
> **Community Edition** — This is an alternative configuration example. For the
> recommended starting point, see the [Core Edition](core-edition/README.md).

A product team or startup where everyone knows each other. You need consistency because multiple people and multiple AI agents are modifying the same codebase concurrently.

### Enterprise (20+ developers)
> **Community Edition** — This is an alternative configuration example. For the
> recommended starting point, see the [Core Edition](core-edition/README.md).

Multiple teams, compliance requirements, and managers who need visibility. The governance goal is that any agent in any session across any team follows the same rules.

---

## Feature Comparison

| Feature | Recommended | | |
|---|---|---|---|
| | **Core Edition** | Solo | Small Team | Enterprise |
| Session protocol | Start + end | Start + end only | + mid-session checkpoints | + audit trail logging |
| Model routing | Not included | Not included | 6 task types | 14 task types |
| CI/CD enforcement | GitHub Actions | Not included | Included | Full pipeline |
| Security | Level 1 | Level 1 | Level 2 | Level 3 |
| Compliance | Not included | Not included | Not included | EU AI Act + GDPR |

---

## Start Here

**Start with Core Edition regardless of team size.** Set it up in 10 minutes, run two or three sessions with it, and confirm that the session protocol feels natural. Then extend one section at a time using the community editions as reference.

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
