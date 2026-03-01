> **Community Edition** — This is an alternative configuration example. For the
> recommended starting point, see the [Core Edition](../core-edition/README.md).

# Small Team Configuration

For 3-5 developers sharing a codebase. Everything from the solo configuration, plus the governance mechanisms that prevent the specific failure modes that emerge when multiple people and multiple AI agents work on the same code concurrently.

## What Is Added vs. Solo

### Full session protocol with mid-session checkpoints

**Solo has:** Start and end protocol only.
**Team adds:** Checkpoints during the session — after every task, after every third task, and scope confirmation before any code is written.

**Failure mode this prevents:** A colleague reviews a PR where an agent completed 15 tasks in one session. Without mid-session checkpoints, those 15 tasks happened without explicit approval. Task 3 introduced a pattern change. Tasks 4-15 built on that pattern. The reviewer now has to evaluate whether the pattern decision in task 3 was correct — but by the time they see it, 12 more tasks depend on it. With checkpoints, each task was explicitly approved before the next started.

### Governance sync (drift detection)

**Solo has:** Nothing — you are the plan.
**Team adds:** At session start, the agent compares intended work against the sprint plan and flags drift before any code is written.

**Failure mode this prevents:** Developer A starts a session planning to build the payment module (sprint task). The agent suggests "while we are here, let us also refactor the user model." Developer A agrees — it is a good idea locally. But Developer B is working on the user model right now. The refactor creates a merge conflict that wastes both developers' time. Drift detection surfaces this: "Refactoring the user model is not in the current sprint. Developer B's branch touches user_model.py. Proceed, or return to the payment module?"

### Model routing (6 task types)

**Solo has:** Not included.
**Team adds:** Routing table mapping task types to optimal model tiers — opus for architecture and security, sonnet for code and docs, haiku for simple edits.

**Failure mode this prevents:** Four developers each use opus for everything because it is the default. At $0.15-0.60 per session, that is fine individually. At 40 sessions per week across the team, you are spending $200-1,000/month when $50-150 would produce the same results. Model routing makes cost optimization a team default rather than an individual discipline.

### PR workflow requirements

**Solo has:** Not included.
**Team adds:** No direct commits to main. Every PR updates CHANGELOG.md (CI enforces this). CLAUDE.md changes require a second reviewer.

**Failure mode this prevents:** An agent commits directly to main because it is faster and the developer did not object. The commit breaks the build. The team does not know who made the change or why. Another agent, running in a different developer's session, reads the broken code and builds on top of it. The PR requirement in the constitution means every agent knows the rule, not just the humans.

### Mandatory task reporting

**Solo has:** Not included.
**Team adds:** After every completed task, the agent presents a structured status block showing files changed, goal impact, session progress, and next steps. This cannot be disabled during a session.

**Failure mode this prevents:** The yes-man anti-pattern. An agent completes 20 tasks in rapid succession, each one drifting slightly from the original scope. The developer says "keep going" without reviewing intermediate results. By task 20, the session has built an elaborate solution to a problem that was not in the sprint. Task reporting forces a pause point where the developer sees exactly what changed and can course-correct.

## What Is Still Left Out

### Compliance sections (EU AI Act, GDPR)

For regulated industries or large organizations. Maintaining compliance documentation costs real time — reviewing EU AI Act applicability, documenting data processing legal bases, maintaining audit trails to the standard required by regulators. If you are not subject to these regulations today, the documentation overhead is pure cost with no benefit.

**When to add:** When a compliance officer, legal counsel, or customer security questionnaire asks about your AI governance practices. Not before.

### Definition of done (mandatory checklist)

The enterprise configuration defines an 8-item checklist that agents must confirm before marking any task complete: code runs, tests pass, docstrings written, CHANGELOG updated, architecture docs updated, decisions documented, security scan passed, naming conventions verified.

**When to add:** When your team grows beyond 5 people, or when you discover that "done" means different things to different team members. At 3-5 people, you can align on "done" through conversation. Beyond that, you need a checklist.

### Change control for CLAUDE.md

The enterprise configuration requires an ADR + PR + two human reviewers to change CLAUDE.md.

**When to add:** When a CLAUDE.md change has caused a problem — an agent behaved unexpectedly because someone changed the constitution without the team knowing. On a team of four, this can be handled with a Slack message. On a team of twenty, it cannot.

### Escalation model

Formal escalation contacts and procedures for security incidents, architectural disputes, and governance changes.

**When to add:** When the team is large enough that the right person to escalate to is not obvious, or when you operate in an environment where security incidents have formal reporting requirements.

## Setup: 30 Minutes

```bash
# 1. Copy all required files
cp examples/small-team/CLAUDE.md .
cp templates/PROJECT_PLAN.md .
cp templates/CHANGELOG.md .
cp templates/MEMORY.md .
cp templates/DECISIONS.md .
cp templates/ARCHITECTURE.md .

# 2. Edit CLAUDE.md — fill in project details (5 minutes)
#    Replace: project_name, description, stack, owner, repository, current_phase

# 3. Edit PROJECT_PLAN.md — add your actual phases and tasks (10 minutes)

# 4. Edit ARCHITECTURE.md — document your system architecture (10 minutes)
#    Even a rough component diagram is better than nothing

# 5. Install slash commands
mkdir -p .claude/commands
cp commands/*.md .claude/commands/

# 6. (Optional) Set up pre-commit hooks for local enforcement
cp ci-cd/pre-commit/.pre-commit-config.yaml .
pip install pre-commit && pre-commit install

# 7. Configure branch protection on main
#    - Require PR reviews (1 minimum, 2 for CLAUDE.md changes)
#    - Require CI status checks to pass before merge
#    - Block direct pushes to main
```

## Moving to Enterprise (Level 3)

When you hit compliance requirements, scale beyond 5 developers, or experience the failure modes that enterprise governance prevents (security incidents without a response protocol, architectural decisions made without review, "done" meaning different things to different teams), add the enterprise sections:

1. Copy `examples/enterprise/CLAUDE.md` and merge the additional sections
2. Add: `compliance`, `definition_of_done`, `change_control`, `escalation_model`, `review_cadence`
3. Expand `model_routing` from 6 to 14 task types
4. Expand `security` to Level 3 with data classification
5. Set up all three CI/CD components
6. Add COST_LOG.md and SPRINT_LOG.md templates

The transition takes about 2 hours. Everything from Level 2 carries forward unchanged.
