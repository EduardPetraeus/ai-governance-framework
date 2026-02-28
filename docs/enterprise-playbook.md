# Enterprise Playbook: Rolling Out AI Governance at Scale

## 1. The Enterprise Challenge

A solo developer adopting AI governance faces one problem: their own habits. A team of five faces coordination. An enterprise of fifty or more developers faces something fundamentally different: a coordination problem that individual discipline cannot solve.

The failure mode at enterprise scale is not "one developer vibe-codes." It is fifteen teams running fifteen divergent interpretations of AI-assisted development, each producing a codebase that cannot be understood, maintained, or audited by anyone outside that team. Without governance, this state is typically reached within three to six months of widespread AI tool adoption.

**Why this is harder than any previous tooling rollout:**

Traditional tools (IDEs, CI/CD, containerization) have deterministic behavior. A Docker container does the same thing for every developer. An AI agent does not. The same agent, given the same `CLAUDE.md`, will produce different outputs depending on who prompts it and how. This means that governance must control not just the tool configuration, but the interaction patterns — something traditional rollout playbooks never address.

Enterprise rollout must solve for four tensions simultaneously:

- **Consistency without uniformity**: shared standards that do not eliminate team autonomy
- **Enforcement without surveillance**: automated gates that catch problems without creating a culture of fear or performative compliance
- **Velocity without drift**: AI-generated speed that builds the right thing, not just any thing at high speed
- **Compliance at scale**: audit trails and regulatory requirements that cannot be satisfied by individual discipline alone

The core insight: **AI agents are obedient, not strategic.** They optimize for the nearest instruction, not the company's goals. At enterprise scale, the nearest instruction for fifty developers is fifty different things. Governance is the mechanism that aligns all fifty toward the same outcome.

The secondary insight: **governance is not overhead, it is context.** An ungoverned agent is not "free" — it is uninformed. Governance gives the agent the information it needs to produce the right output. The 5-10% of session time spent on governance prevents the 30-50% of time lost to rework, drift, and context loss.

---

## 2. Phase 1: Pilot (Weeks 1-6)

### Team Selection Criteria

Do not pilot with the highest-performing team or the most resistant team. Choose a team that is:

- **Mid-sized (4-8 developers)**: small enough to iterate quickly, large enough to expose real coordination problems (merge conflicts, architectural divergence, session overlap)
- **Willing but skeptical**: at least one champion who believes in the approach, plus team members who will ask hard questions. Avoid a team of pure enthusiasts — they will adopt anything and their success will not be credible to skeptics
- **Representative**: working on a codebase that resembles what the rest of the organization builds — not a greenfield side project or an isolated experiment
- **Visible**: has stakeholders who will notice and care about results — the pilot must produce outcomes that leadership can point to
- **Moderate blast radius**: not running mission-critical production systems that cannot tolerate experimentation, but not a throwaway project either

**Selection anti-patterns to avoid:**
- Choosing the team that "has time" (signals low priority)
- Choosing the newest team (no baseline to compare against)
- Choosing a team that is already disciplined (their success will not be attributable to governance)
- Choosing a team led by the person who proposed the initiative (perceived as self-serving)

### What to Implement

The pilot implements exactly Level 1 and Level 2 of the maturity model — no more:

1. `CLAUDE.md` written collaboratively with the team (critical: they write it, not someone imposed from outside)
2. Session protocol: start / checkpoint / end
3. `CHANGELOG.md` updated every session with timestamp, model, tasks, files changed
4. `PROJECT_PLAN.md` as the shared sprint backlog
5. Basic PR workflow: no direct commits to main, all code through branches
6. One shared prompt library in `.claude/prompts/` with templates for the team's three most common task types

Do not attempt CI/CD automation, master agents, model routing, or cost tracking in the pilot. These add complexity that obscures whether the fundamentals are working.

### What to Measure

Establish baselines in week 1 before the governance protocol is enforced, then measure across weeks 2-6:

| Metric | Method | Why It Matters | Expected Change |
|--------|--------|----------------|-----------------|
| Tasks completed per session | Count from `CHANGELOG.md` | Core productivity proxy | +50-100% by week 6 |
| Rework rate | PRs reopened or reverted within 48 hours | Quality proxy | -30-50% by week 6 |
| Session protocol adherence | % of sessions with proper start/end entries | Governance adoption | 40% -> 90%+ |
| Developer satisfaction | Weekly 3-question survey (1-5 scale) | Resistance early warning | Dip at week 3, recovery by week 5 |
| Time from task start to merge | Git timestamps: branch creation to merge | Flow efficiency | -20-40% by week 6 |

### Week-by-Week Pilot Structure

| Week | Focus | Success Criteria |
|------|-------|-----------------|
| 1 | Write `CLAUDE.md` with team. Establish baseline metrics. Install pre-commit hooks. | All developers have read, understood, and contributed to the constitution. Baseline metrics recorded. |
| 2 | Session protocol enforcement begins. First sprint with governance. | >80% of sessions follow start/end protocol. First `CHANGELOG.md` entries appear. |
| 3 | Prompt library in use. CHANGELOG discipline enforced. First resistance appears. | All sessions update CHANGELOG. At least three prompts in the shared library. Accept that productivity dips here. |
| 4 | Retrospective. Adjust `CLAUDE.md` based on what is not working. Address resistance directly. | Team has made at least one PR to improve `CLAUDE.md`. Every team member has voiced at least one concern. |
| 5 | Steady-state operation. Metric comparison to baseline begins. | Tasks/session visibly trending above baseline. Rework rate visibly trending below baseline. |
| 6 | Final retrospective. Prepare case study for expansion. Document what worked and what failed. | Quantitative evidence of improvement across at least three of five metrics. Written case study for next teams. |

---

## 3. Phase 2: The Champion Model (Weeks 4-12)

### What a Champion Is

An AI governance champion is a developer embedded in a team who:

- **Understands** the framework at a deeper level than their colleagues — not just the rules, but the rationale
- **Enforces** the session protocol during team sessions and code reviews — with authority, not suggestions
- **Evolves** the team's `CLAUDE.md` based on what is working and what is not
- **Escalates** systemic problems to the organization-level governance owner
- **Trains** new developers during their onboarding supervised sessions
- **Reports** team metrics monthly to the governance lead

A champion is not a manager. They are a practitioner who is better at AI-assisted development than their peers and is given time and authority to help others improve.

### Champion Selection Criteria

Select champions who are:

- Respected by their peers (not appointed from above — peer nomination is ideal)
- Curious about how AI agents actually work, not just that they work
- Comfortable giving direct, specific feedback ("your prompt lacked scope definition" not "maybe try being more specific")
- Neither the most zealous adopters nor the most resistant — both extremes make poor champions
- Willing to invest 3-5 hours per week in governance work in addition to their development work

**Avoid selecting the team lead by default.** The champion role works better as a peer role, not a management layer. When the team lead is the champion, feedback becomes hierarchical and developers stop being honest about what is not working.

### Champion Responsibilities

| Responsibility | Time per Week | Cadence |
|----------------|---------------|---------|
| Review proposed changes to team `CLAUDE.md` | 1-2 hours | Per PR |
| Run prompt quality review for complex tasks | 30 min | Weekly |
| Debrief new developers after supervised sessions | 1 hour | Per developer onboarding |
| Report team metrics to org governance owner | 30 min | Monthly |
| Attend cross-team champion sync | 1 hour | Monthly |
| Review team's `CHANGELOG.md` entries for quality | 30 min | Weekly |

Total champion overhead: 4-6 hours per week. This must be acknowledged as part of their role — not squeezed in on top of a full development workload.

### Champion Authority

Champions must have explicit, documented authority to:

- **Block a PR** that violates the team's `CLAUDE.md` (even without a CI gate catching it)
- **Reject a session plan** that lacks proper scope definition
- **Request a re-do** of a session whose output cannot be explained by the developer who ran it
- **Propose changes** to `CLAUDE.md` for team review (with a 24-hour comment period)
- **Escalate to org governance** when a team-level issue has org-level implications

Without this authority, the champion role becomes a suggestion box. Document the authority in the team's operating agreement and ensure management explicitly backs it.

---

## 4. CLAUDE.md Ownership

### The Governance of Governance

`CLAUDE.md` is the most consequential file in the entire framework. Every agent reads it. Every session is shaped by it. An unreviewed change to it can silently alter the behavior of every AI session across the team or organization. This makes its change control process a first-class governance concern.

### Ownership Model

| Level | Owner | Co-Owner | Change Authority |
|-------|-------|----------|-----------------|
| Organization (`~/.claude/CLAUDE.md`) | CTO or designated AI governance lead | Security team (for security rules) | Two reviewers required for any change |
| Repository (`repo/CLAUDE.md`) | Team champion | Tech lead (for architectural conventions) | One reviewer (champion or tech lead) |
| Commands (`repo/.claude/commands/`) | Any developer | Champion reviews | Standard PR process |

**No individual developer can unilaterally modify `CLAUDE.md`.** This is the single most important governance rule.

### PR Process for Changes

All changes to `CLAUDE.md` follow this process:

```
1. Developer or agent identifies need for change
2. GitHub issue created describing: what, why, alternatives considered, expected impact
3. PR opened with change — PR description must include rationale and impact analysis
4. Review from champion (team-level) or governance lead (org-level)
5. 24-hour comment period for the full team (48 hours for org-level changes)
6. Merge — all agents automatically use the new version at next session start
```

**Asymmetric review requirements:**
- Changes that **expand permissions** (allow something previously forbidden): two reviewers, 48-hour comment period
- Changes that **restrict behavior** (add a new prohibition): one reviewer, 24-hour comment period
- Changes that **clarify without changing behavior**: one reviewer, no waiting period

### Versioning Strategy

Add a version header to the file:

```markdown
# CLAUDE.md — AI Agent Constitution
# Version: 1.3
# Last modified: 2026-02-28
# Owner: [Team Champion Name]
# Changes: See git log — tag major versions
```

Tag major versions in git: `v1.0`, `v1.1`, `v2.0`. Major version = architectural change to governance model. Minor version = new rule or modified rule. Clarifications do not bump the version.

### Org-Level vs. Repo-Level Split

```
~/.claude/CLAUDE.md              <- Organization constitution (applies to all repos)
repo/CLAUDE.md                   <- Repository constitution (extends, never overrides)
repo/.claude/commands/           <- Repository-specific slash commands
```

**Org-level defines (non-negotiable across all teams):**
- Security rules and the never-commit list
- Compliance requirements (GDPR, EU AI Act)
- Git workflow (branching strategy, PR requirements)
- Session protocol structure (start/end requirements)
- Data classification system (RESTRICTED / CONFIDENTIAL / INTERNAL / PUBLIC)
- Naming conventions (org-wide standard)

**Repo-level adds (team-specific, cannot contradict org-level):**
- Domain-specific architecture rules
- Source system configurations and integration patterns
- Deployment patterns and environment specifics
- Team-specific prompt templates
- Model routing preferences (within org cost policy)
- Local naming extensions

**Conflict resolution:** If there is ever a conflict between org-level and repo-level rules, org-level wins. Both files must contain an explicit statement of this hierarchy:

```markdown
# This file extends the organization constitution at ~/.claude/CLAUDE.md
# In case of conflict, the organization constitution takes precedence.
```

---

## 5. Standardization vs. Flexibility

### The Core Tension

Too much standardization, and teams cannot adapt governance to their specific technical context — the framework becomes a bureaucratic burden that is worked around rather than followed. Too much flexibility, and you have fifty teams running fifty governance systems with no ability to provide org-level oversight, aggregate metrics, or ensure compliance.

The resolution is a **layered constitution**: a shared base that is genuinely non-negotiable, with well-defined extension points for team-specific additions.

### What Is Sacred (Non-Negotiable)

These rules appear in the org-level `CLAUDE.md` and cannot be overridden by any team:

1. **Security**: never-commit list, data classification, `.claudeignore` requirements, secret scanning
2. **Session protocol structure**: sessions must have a documented start (scope definition) and end (CHANGELOG update, governance file updates)
3. **CHANGELOG discipline**: every session updates `CHANGELOG.md` with timestamp, model, tasks, files changed
4. **PR-based workflow**: no direct commits to protected branches, all code through reviewed PRs
5. **Human review requirement**: no AI-generated code merges without documented human approval
6. **ADR supremacy**: agents cannot contradict an accepted ADR without explicit human approval
7. **Audit trail**: all AI-assisted commits use `Co-Authored-By` metadata

### What Is Flexible (Team Extension Points)

Teams can define in their repo-level `CLAUDE.md`:

- Which specific slash commands and agent configurations are active
- Domain-specific architecture rules and patterns
- Technology-specific conventions (SQL formatting, API patterns, testing frameworks)
- Session frequency and checkpoint cadence
- Prompt library contents and task-specific templates
- Model routing preferences (within the org cost policy)
- Definition of Done criteria specific to their domain

### The Shared Base Template

Every team starts from the org-provided `CLAUDE.md` template. Sections marked `# REQUIRED — DO NOT MODIFY` are locked. Sections marked `# EXTEND HERE` are where teams add their specifics:

```markdown
# CLAUDE.md — [Team Name] Agent Constitution
# Extends: Organization Constitution v1.3

# === REQUIRED — DO NOT MODIFY ===
## security_rules
[Inherited from org-level — do not edit]

## session_protocol
[Inherited from org-level — do not edit]

# === EXTEND HERE ===
## architecture_rules
[Team-specific architecture patterns]

## naming_conventions
[Extensions to org naming standard]

## domain_rules
[Domain-specific constraints and patterns]
```

This structure prevents the gradual erosion of org-level rules through well-intentioned local modifications, while giving teams genuine ownership of the parts that matter to their context.

---

## 6. Onboarding New Developers

### The Day 1 Checklist

Before a new developer runs their first AI-assisted session, they complete:

```
Day 1 — Orientation:
  [ ] Read CLAUDE.md — understand what each rule is and WHY it exists
  [ ] Read two recent CHANGELOG entries — understand what session output looks like
  [ ] Read one ADR — understand how architectural decisions are documented and why they prevent agent re-litigation
  [ ] Read .claude/prompts/ — know what standard prompts are available for common tasks
  [ ] Review the never-commit list and data classification rules — quiz coming at end of week 2
  [ ] Set up .claudeignore in their development environment
  [ ] Confirm pre-commit hooks are active: run `pre-commit run --all-files`
  [ ] Set up local development environment and verify all CI checks pass locally

Days 2-3 — Observation:
  [ ] Observe the champion running a full session (start to end) — take notes on prompt structure, scope management, and review process
  [ ] Review the PR that results from that session — read every comment, every check
  [ ] Attend the post-session debrief with the champion — ask at least three questions

Days 4-10 — Supervised Sessions:
  [ ] Run three supervised sessions with the champion present as observer (not intervener)
  [ ] After each session: 15-minute debrief with champion covering prompt quality, scope discipline, and review thoroughness
  [ ] Week 2: run unsupervised sessions with champion available for questions via Slack/Teams

End of Week 2 — Certification:
  [ ] Can explain the rationale behind each rule in CLAUDE.md (not just recite the rule)
  [ ] Can demonstrate correct session start protocol (scope definition, file review, context loading)
  [ ] Can demonstrate correct scope definition and prompt structure using the team template
  [ ] Can perform a rollback exercise (break something intentionally, recover correctly)
  [ ] Passes data governance quiz (10 questions on data classification, never-commit list, GDPR basics — 90% pass threshold)
  [ ] First unsupervised PR has been reviewed and approved without governance violations
```

### The Supervised Session Model

During supervised sessions, the observer (champion) does not intervene. They watch and take notes on:

- How the developer defines session scope (specific vs. vague, bounded vs. open-ended)
- How they structure their prompts (template usage, constraint specification, acceptance criteria)
- How they respond to agent output (reading carefully vs. rubber-stamping, questioning vs. accepting)
- Whether they follow the session protocol (start, checkpoints, end)
- Whether scope creep is recognized and addressed or silently accepted

The debrief after each session covers four questions:

1. "What was the strongest prompt you wrote today, and why did it work?"
2. "Where did the agent's output surprise you — and how did you verify it was correct?"
3. "Did the session stay within its scope? Where did it drift, and what did you do about it?"
4. "Is there anything you approved without fully understanding?"

The mentor does not answer the last question reassuringly. If the developer approved something they did not understand, the correct response is: "Go back and understand it before your next session. Code you cannot explain is code you cannot maintain."

### The Learning Curve

Set the expectation: **the learning curve is two weeks.** During those two weeks, the developer will be slower than they were without governance. This is normal. Acknowledge the dip, do not pretend it does not exist, and show them the data that demonstrates the recovery.

Typical productivity trajectory:
- Week 1: 60% of ungoverned speed (learning the protocol)
- Week 2: 80% of ungoverned speed (internalizing the protocol)
- Week 3: 100% of ungoverned speed (protocol becomes automatic)
- Week 4+: 120-150% of ungoverned speed (governance prevents rework, provides context, reduces drift)

---

## 7. Metrics at Scale

### Team-Level Dashboard

Each team maintains a lightweight dashboard — a markdown file updated weekly by the champion:

```markdown
# Team AI Governance Dashboard
## Week of 2026-03-01

### Tier 1 Metrics
| Metric | This Week | Last Week | 4-Week Avg | Target | Status |
|--------|-----------|-----------|------------|--------|--------|
| Tasks/session (avg) | 4.2 | 3.8 | 3.9 | >=4 | On track |
| Rework rate | 8% | 11% | 10% | <10% | Improving |
| Session protocol adherence | 94% | 87% | 90% | >95% | Watch |
| Test coverage delta | +1.2% | +0.8% | +0.9% | >=0% | Good |
| Cost/session (avg) | $0.34 | $0.41 | $0.38 | <$0.50 | Good |

### Notable Events
- Session 015: scope creep incident — cross-layer changes in one session. Caught by champion in review. Remediated.
- Developer B onboarding: completed supervised sessions, passed certification quiz.

### Action Items
- Champion to run prompt quality review with Developer A (rework rate above team average for 3 consecutive weeks)
- Update CLAUDE.md section on SQL transforms — current wording is ambiguous per team feedback
```

### Org-Level Dashboard

The org-level dashboard aggregates team dashboards monthly:

| Metric | Aggregation Method | Audience | Action Threshold |
|--------|--------------------|----------|-----------------|
| Rework rate | Average across teams | Engineering VP | Any team >15% for 2 consecutive months |
| Protocol adherence | Average across teams | Governance lead | Any team <80% triggers champion intervention |
| Test coverage delta | Average across teams | Engineering VP | Org average declining for 2 consecutive months |
| Cost/session | Total and per-team | Finance / Engineering VP | Any team >2x org average |
| Security incidents | Total count, by severity | CISO / CTO | Any critical incident triggers post-mortem |
| Champion health | Coverage % (teams with active champion) | Governance lead | <100% requires immediate action |

**What stays at team level (do not aggregate):**

- Individual developer metrics of any kind — aggregating these creates surveillance dynamics
- Prompt quality scores — too context-dependent to compare across teams
- Architecture drift scores — team-specific baselines make comparison meaningless

### What Not to Show Leadership

Do not create org-level metrics for:

- **Tasks per developer** (incentivizes gaming with trivial tasks)
- **Commits per day** (incentivizes micro-commits)
- **Lines of code** (AI inflates this meaninglessly — 10,000 lines of AI-generated code is not better than 2,000)
- **Speed of PR approval** (incentivizes rubber-stamping, the opposite of meaningful review)
- **Number of AI sessions** (incentivizes quantity over quality)

These metrics, if visible at the org level, will be gamed in ways that make the real metrics worse. The moment a VP asks "which team has the most tasks per session," teams will start defining tasks as granularly as possible.

---

## 8. Common Resistance Patterns

### "This Will Slow Us Down"

**The fear**: Session protocols, CHANGELOG updates, ADRs — this is overhead that reduces velocity.

**The evidence it does not**: Unstructured AI development is fast for the first two weeks and slow for the next two months. The rework rate for ungoverned AI sessions is typically 15-25%. Governed sessions run 5-10%. That means ungoverned teams spend 15-25% of their time redoing work that governance would have prevented. The 5-10% governance overhead replaces 15-25% rework — a net gain of 5-15% real velocity.

**How to address it**: Do not argue in the abstract. Offer a time-boxed experiment: "Run governed for four weeks. Measure rework rate before and after. If governed sessions have higher total overhead than the rework they prevent, we will stop." No team has ever stopped after the data comes in.

The framing: "We are not adding overhead. We are redirecting 5% of session time into governance so the remaining 95% builds the right thing instead of the wrong thing at high speed."

### "Our Codebase Is Too Complex"

**The fear**: This framework was designed for greenfield projects. Our legacy codebase with 500,000 lines, four frameworks, and twelve years of history makes it inapplicable.

**The reality**: Complex codebases need governance more, not less. Without `CLAUDE.md`, an agent working on a complex codebase will make assumptions about architecture, naming, boundaries, and patterns that are wrong — and will produce code that looks correct but violates undocumented conventions that only exist in team members' heads.

**How to address it**: "Your codebase is complex. That complexity is currently in your team's heads. When they leave or forget, it is lost. `CLAUDE.md` and `ARCHITECTURE.md` make that complexity explicit and available to both agents and new developers. Governance does not add complexity — it makes existing complexity visible and manageable."

### "Developers Won't Follow It"

**The fear**: We can write all the rules we want; developers will ignore them under deadline pressure.

**The reality**: Governance that relies on developer discipline fails. Governance that relies on enforcement succeeds. Pre-commit hooks, CI/CD gates, and branch protection rules do not depend on anyone remembering to follow them. They run automatically, every time, regardless of deadline pressure.

**How to address it**: "You are right — discipline-based governance fails. That is why this framework uses enforcement-based governance. The pre-commit hook does not care if the developer is under pressure. It runs. The CI gate does not care if it is Friday at 5 PM. It checks. The rules that matter are automated, not aspirational."

### "AI Will Take Our Jobs"

**The fear**: If AI makes me 10x more productive, the company needs 10x fewer developers.

**The reality**: In the short and medium term, AI expands what teams can build, not reduces headcount. The developers who adopt AI governance become more valuable, not less — they become AI supervisors, the humans who direct and verify AI work. The developers who resist become less competitive regardless of governance.

**How to address it**: Do not dismiss the fear. Acknowledge it as legitimate.

"The framework we are building positions developers as AI supervisors — the people who define scope, verify output, make architectural decisions, and ensure quality. Agents do the mechanical work. Developers do the judgment work. Governance is the structure that keeps humans in the decision seat. Organizations that govern AI well will need senior developers who understand governance. Organizations that do not govern AI will need fewer developers of any kind — because their codebases will be unmaintainable."

Show the career path: developers who understand AI governance are the ones organizations will want to hire, keep, and promote. This is a new skill with genuine career value.

---

## 9. 24-Week Rollout Timeline

### Weeks 1-4: Foundation and Pilot

| Week | Action | Owner | Success Criteria |
|------|--------|-------|-----------------|
| 1 | Select pilot team (4-8 developers). Appoint org-level governance lead. Write initial org-level `CLAUDE.md`. | CTO / Engineering VP | Pilot team selected. Governance lead appointed. |
| 2 | Pilot team collaboratively writes their `CLAUDE.md`. Install pre-commit hooks. Establish baseline metrics. | Governance lead + pilot team | `CLAUDE.md` exists and every team member has contributed. |
| 3 | Pilot team implements Level 1: session protocol, CHANGELOG, basic PR workflow, first prompt templates. | Pilot team champion | >80% session protocol adherence. First CHANGELOG entries. |
| 4 | First retrospective. Measure metrics vs. baseline. Identify what to adjust. Begin addressing resistance. | Pilot team + governance lead | Baseline comparison available. At least one `CLAUDE.md` improvement PR merged. |

### Weeks 5-8: Pilot Deepening

| Week | Action | Owner | Success Criteria |
|------|--------|-------|-----------------|
| 5 | Pilot team implements Level 2: `PROJECT_PLAN.md`, `ARCHITECTURE.md`, ADRs. | Pilot team | Governance files exist and are referenced by agents. |
| 6 | First prompt library created in `.claude/prompts/`. Prompt quality review begins. | Pilot team champion | At least 5 task-specific prompt templates. |
| 7 | First champion formally identified, onboarded, and given documented authority. | Pilot team lead + governance lead | Champion responsibilities and authority documented. |
| 8 | Pilot retrospective. Document what worked, what failed, what to change. Prepare expansion case study. | All stakeholders | Written case study with metrics. Go/no-go decision for expansion. |

*Expect a productivity dip at weeks 3-4.* This is the adoption overhead period — developers are learning the protocol while still doing their normal work. Communicate this dip in advance so it is not mistaken for evidence that governance is harmful.

### Weeks 9-12: First Expansion (Teams 2 and 3)

| Week | Action | Owner | Success Criteria |
|------|--------|-------|-----------------|
| 9 | Select two additional teams. Brief their leads on the framework using the pilot case study. | Governance lead | Teams selected. Leads briefed. |
| 10 | Pilot champion co-writes `CLAUDE.md` with each new team. **Do not copy-paste — write it together.** | Champions | Each new team has a `CLAUDE.md` they co-authored. |
| 11 | New teams start Level 1. Pilot champion available for questions. Baseline metrics established. | New team champions | >70% session protocol adherence in first week. |
| 12 | First cross-team champion sync. Identify divergences, common issues, and org-level improvements. | All champions | Meeting held. At least one org-level `CLAUDE.md` improvement proposed. |

### Weeks 13-16: Enforcement Infrastructure

| Week | Action | Owner | Success Criteria |
|------|--------|-------|-----------------|
| 13 | CI/CD infrastructure: linting, naming convention checks, secret scanning deployed for all active teams. | Platform / DevOps team | All active teams have automated checks. |
| 14 | Pre-commit hooks standardized and deployed across all active teams. `.claudeignore` templates distributed. | Platform team | No team can commit without hooks running. |
| 15 | Agent PR review set up as optional CI step (not blocking yet). Teams can see agent review comments. | Platform team | Agent reviews appearing on PRs. Teams providing feedback on review quality. |
| 16 | Cost tracking instrumented. First monthly cost report generated. Model routing table drafted. | Governance lead | Cost per team visible. Routing recommendations available. |

### Weeks 17-20: Second Expansion

| Week | Action | Owner | Success Criteria |
|------|--------|-------|-----------------|
| 17 | Expand to remaining teams (target: all teams, 50+ developers total). Use proven playbook. | All champions | All teams have `CLAUDE.md` and session protocol. |
| 18 | Agent PR review promoted to blocking check for all teams. | Governance lead | No PR merges without passing agent review. |
| 19 | Org-level governance dashboard goes live. Monthly reporting cadence established. | Governance lead | Dashboard shows Tier 1 metrics for all teams. |
| 20 | Security audit: scan all repos for compliance with security constitution. Address findings. | Security team | Zero critical findings. All medium findings have remediation plans. |

### Weeks 21-24: Optimization and Steady State

| Week | Action | Owner | Success Criteria |
|------|--------|-------|-----------------|
| 21 | First quarterly framework review. Champions propose improvements to org-level `CLAUDE.md`. | All champions | Review completed. At least three improvements merged. |
| 22 | Master agent proof-of-concept on highest-value repo. Evaluate feasibility for org-wide deployment. | Platform team | POC running and producing useful feedback. |
| 23 | Onboarding guide finalized and integrated into company onboarding for all new engineering hires. | Governance lead + HR | New hire onboarding includes AI governance certification. |
| 24 | Six-month retrospective. Measure all Tier 1 and Tier 2 metrics vs. pre-rollout baseline. Present to leadership. | CTO + all champions | Quantitative evidence of improvement. Go-forward plan approved. |

---

## 10. Governance ROI

### The Cost of Ungoverned AI Development

Ungoverned AI development incurs costs that are real but often invisible until they compound:

| Cost Category | Manifestation | Typical Impact |
|---------------|---------------|----------------|
| Rework | Tasks redone due to drift, scope creep, or incorrect output | 15-25% of developer time |
| Context loss | New sessions start from scratch; no continuity between sessions | 10-15% of each session spent rebuilding context |
| Architectural drift | Multiple implementations of the same pattern; inconsistent conventions | Technical debt that compounds over months |
| Security incidents | Secrets in commits, PII in logs, credentials in documentation | One incident can cost $10K-$500K+ in rotation, audit, and remediation |
| Compliance gaps | No audit trail, no evidence of human review, no data processing documentation | Regulatory exposure; audit failures |
| Onboarding friction | New developers cannot understand AI-generated code; no documentation of decisions | 2-4 weeks longer onboarding per developer |

### The Cost of Governance

| Investment | Time | Frequency |
|------------|------|-----------|
| Session protocol (start/end) | 10-15 min per session | Every session |
| CHANGELOG update | 5 min per session | Every session |
| Champion activities | 4-6 hours per week | Ongoing |
| Governance lead | 8-10 hours per week | Ongoing |
| Quarterly framework review | 2-4 hours per champion | Quarterly |
| New developer onboarding | 2 weeks (partially supervised) | Per hire |

### The Math

For a team of 10 developers running 2 sessions per week:

**Without governance:**
- 20 sessions/week x 20% rework rate = 4 sessions' worth of rework per week
- 4 rework sessions x 2 hours average = **8 hours/week lost to rework**
- Plus: context rebuilding, drift remediation, security incident risk

**With governance:**
- 20 sessions/week x 15 min overhead = 5 hours/week governance overhead
- 20 sessions/week x 7% rework rate = 1.4 sessions' worth of rework per week
- 1.4 rework sessions x 2 hours = **2.8 hours/week lost to rework**
- Governance overhead: 5 hours + champion time (5 hours) = 10 hours
- Rework savings: 8 - 2.8 = 5.2 hours
- Context savings: ~3 hours/week (sessions start with context instead of rebuilding)
- **Net: approximately break-even in direct time, with dramatically reduced risk and improved code quality**

The ROI case is not primarily about saving time. It is about:
1. **Risk reduction**: zero secrets incidents vs. the statistical certainty of incidents without governance
2. **Quality improvement**: code that can be maintained, extended, and audited
3. **Compliance readiness**: audit trail that exists as a byproduct, not a retrofit
4. **Team scalability**: new developers productive in 2 weeks instead of 4-6

Present this to leadership as: "Governance costs approximately the same time as the rework it prevents, while additionally providing security, compliance, and scalability benefits that ungoverned development cannot provide at any cost."

---

## 11. Success Criteria: How to Know the Rollout Succeeded

### Quantitative (6-Month Benchmark)

| Metric | Success Threshold | Measurement |
|--------|-------------------|-------------|
| Session protocol adherence | >90% across all teams | CHANGELOG audit |
| Rework rate | <10% org-wide average | Git log + CHANGELOG analysis |
| Security incidents (secrets committed) | 0 on protected repos | CI/CD scan logs |
| Champion coverage | 100% of teams have active champion | Governance lead verification |
| Cost per session | Within 20% of org-defined target | COST_LOG aggregation |
| Developer satisfaction with AI workflow | >3.5/5 on quarterly survey | Survey tool |
| New developer onboarding time | <2 weeks to first unsupervised session | HR tracking |

### Qualitative

- A new developer can become productive with AI tooling in under two weeks
- Any developer can explain the rationale behind any rule in their team's `CLAUDE.md`
- Post-incident reviews consistently identify the check that failed, not "we just did not know"
- Champions meet monthly and genuinely improve the framework — it is a living system, not a document
- Governance is discussed as a tool for building better software, not as "the process" or "the overhead"

### What Failure Looks Like

The rollout has failed if, after 24 weeks:

- Teams have `CLAUDE.md` files but agents do not follow them (the protocol is broken)
- CHANGELOG entries are copy-pasted boilerplate without real content (performative compliance)
- Developers approve PRs without reviewing AI-generated code (rubber-stamping)
- The framework is maintained by one person; everyone else treats it as that person's problem
- Champions have stopped meeting or have no improvements to propose (the framework is dead)
- Rework rate has not measurably improved vs. baseline (the framework is not producing value)

---

*Related guides: [Metrics Guide](./metrics-guide.md) | [Compliance Guide](./compliance-guide.md) | [Prompt Engineering](./prompt-engineering.md) | [Security Guide](./security-guide.md) | [Model Routing](./model-routing.md)*
