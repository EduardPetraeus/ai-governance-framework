# Examples

Three reference configurations for different team sizes and governance needs. Each is a
complete, working setup — not a skeleton. Pick the one that fits your situation and
customize from there.

## The three personas

### Solo developer
One person. Personal project or side project. Speed matters more than process.
The goal is to not lose context between sessions, not to govern a team.

**What's included:** CLAUDE.md (40 lines), minimal session protocol, essential security rules.
**What's left out:** Model routing, agents, team governance, compliance, CI/CD.
**Time to set up:** 10 minutes.

### Small team (3-5 developers)
A team where everyone knows each other. You can talk through decisions, but you need
consistency because multiple people (and multiple AI agents) are touching the same code.
The goal is consistent agent behavior and clear conventions without bureaucracy.

**What's included:** Everything in solo, plus governance sync, basic model routing, PR workflow,
shared conventions enforcement.
**What's left out:** Full CI/CD, compliance sections, enterprise change control.
**Time to set up:** 30 minutes.

### Enterprise (20+ developers)
Multiple teams. Compliance requirements. Managers who need visibility. The goal is
that any agent in any team session follows the same rules, and violations are caught
automatically — not by humans after the fact.

**What's included:** Everything in small team, plus full model routing, EU AI Act reference,
security maturity requirements, audit trail requirements, change control, definition of done,
escalation model.
**What's left out:** Nothing — this is the full framework.
**Time to set up:** 2 hours (including CI/CD setup).

---

## Quick comparison

| Feature | Solo | Small Team | Enterprise |
|---------|------|-----------|-----------|
| CLAUDE.md | Minimal (40 lines) | Standard (80 lines) | Full (150+ lines) |
| Session protocol | Start/end only | Full with mid-session checks | Full + audit trail |
| Model routing | No | Basic (5 task types) | Full (11 task types) |
| Security rules | Never-commit list | Never-commit + scan triggers | Full security maturity |
| Agents | No | Optional | Required |
| CI/CD enforcement | No | governance-check.yml | All three components |
| Compliance | No | No | EU AI Act reference |
| Change control | No | PR review for CLAUDE.md | Full change control process |
| Definition of done | No | No | Mandatory checklist |
| Cost tracking | No | Optional | Required |
| Audit trail | No | CHANGELOG only | Full session + decision log |

---

## How to pick

Start with what matches your current situation, not what you aspire to. A solo developer
running the enterprise config will spend more time on governance than building. A team of
20 running the solo config will have agents that diverge immediately.

**Upgrade path:** Solo → Small Team → Enterprise is a natural progression. Each level adds
files, not replaces them. When you're ready to move up, copy the additional templates
from `../templates/` and enable the additional CI/CD components from `../ci-cd/`.

**Never downgrade:** Once you have CHANGELOG.md and your agents have cross-session memory,
removing it means the next session starts blind. If governance overhead is too high,
slim the config rather than removing core files.
