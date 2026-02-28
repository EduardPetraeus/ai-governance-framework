# Research Pipeline

The framework must discover and integrate new knowledge faster than it becomes outdated. This document specifies how the research pipeline works: what it monitors, how it filters, how it analyzes, how it proposes changes, and how those changes are integrated.

---

## Why Manual Research Fails

Nobody has time to read every blog post, paper, and changelog about AI development practices. The volume is staggering: Anthropic ships model updates monthly, OpenAI publishes new best practices quarterly, engineering blogs from hundreds of companies share lessons learned, academic papers propose new techniques, and community forums surface patterns daily.

Best practices evolve faster than any individual can track. A team that relies on one person to stay current will always be behind. That person has other responsibilities. They read what catches their attention, miss what does not, and cannot systematically evaluate everything they find against the framework's existing guidance.

The result is predictable: frameworks become outdated not because better knowledge does not exist, but because nobody has the time to find it, evaluate it, and integrate it. The framework must have a built-in mechanism to discover and integrate new knowledge — or accept that it will fall behind within months.

---

## The Research Pipeline

```
Sources → Collection → Filtering → Analysis → Proposal → Integration
```

Each stage has a defined purpose, defined inputs and outputs, and defined quality criteria. Skipping a stage degrades the pipeline. Skipping filtering produces noise. Skipping analysis produces uncontextualized findings. Skipping the proposal format produces changes without rationale.

---

### Sources (What to Monitor)

The pipeline monitors sources across four categories, ordered by reliability.

**Tier 1 — Official documentation (highest reliability):**
- Anthropic documentation and changelog (model updates, new features, API changes, best practices)
- Claude Code release notes (new capabilities, changed behavior, deprecated features)
- OpenAI documentation (competitor patterns worth evaluating for adoption)

**Tier 2 — Engineering practice (high reliability):**
- GitHub repositories tagged with "ai-governance", "claude-code", "llm-governance", "ai-development"
- Engineering blogs from companies using AI development at scale: Anthropic, Stripe, Vercel, Linear, Shopify, Datadog
- Conference talks: AI Engineer Summit, QCon AI track, NeurIPS application tracks, Strange Loop

**Tier 3 — Community knowledge (medium reliability):**
- r/dataengineering, r/machinelearning, r/ExperiencedDevs (community-validated patterns)
- HackerNews discussions on AI development, agent frameworks, governance
- Discord and Slack communities focused on Claude Code and AI-assisted development

**Tier 4 — Academic research (variable reliability):**
- Academic papers on AI-assisted software development
- Papers on LLM evaluation, safety, and alignment (applicable to agent governance)
- Preprints on arXiv related to code generation quality and AI agent coordination

Tier 1 sources are checked weekly. Tier 2 sources are checked biweekly. Tier 3 and 4 sources are checked monthly or on demand.

---

### Collection (How to Gather)

Three collection mechanisms operate at different cadences:

**On-demand collection** — a developer runs the `/research` command with a specific topic. The [research agent](../agents/research-agent.md) searches configured sources for content related to that topic, filters for relevance, and presents findings within the session.

**Automated periodic scan** — a GitHub Action or cron job triggers a research sweep at a defined interval. The sweep checks Tier 1 and Tier 2 sources for new content since the last scan. Findings are aggregated into a research report and posted as a GitHub Issue for human review.

**Community submissions** — users and contributors submit findings via GitHub Issues with the "research" label. These bypass the automated collection stage and enter the pipeline at the filtering stage.

---

### Filtering (What Is Relevant)

Not everything discovered is worth acting on. The filtering stage applies four criteria. A finding must pass all four to proceed to analysis.

**1. Actionable.** The finding must describe something the framework can do, change, or adopt. "AI is transforming software development" is not actionable. "Teams using structured output contracts for agent tasks report 40% fewer review cycles" is actionable — it validates the framework's existing output contracts pattern or suggests an improvement.

**2. Evidence-based.** The finding must be backed by at least one of: a real team's experience, measured data, a reproducible experiment, or official documentation from a model provider. Theoretical arguments without evidence are deferred, not adopted.

**3. Framework-mappable.** The finding must map to at least one layer of the [7-layer architecture](architecture.md). If a finding does not fit any layer — if it concerns a domain the framework does not address — it is out of scope. This keeps the pipeline focused. The framework governs AI agents in software development. Findings about AI in healthcare, finance, or other domains are relevant only if the governance pattern generalizes.

**4. Security-compatible.** The finding must not contradict established security principles. A pattern that improves velocity by relaxing secret scanning is rejected regardless of its other merits. Security rules are the framework's hardest constraint.

---

### Analysis (What to Do with It)

Findings that pass filtering are analyzed in the context of the existing framework. The [research agent](../agents/research-agent.md) performs this analysis, producing a structured assessment for each finding.

**Framework context comparison:**
- What does the framework currently say about this topic?
- Does the finding complement existing guidance (adds depth or evidence)?
- Does the finding contradict existing guidance (suggests a different approach)?
- Does the finding extend existing guidance (covers a case the framework does not address)?

**Layer mapping:**
- Which governance layer does this finding affect?
- What maturity level is it relevant to? (A pattern useful at Level 1 has different adoption criteria than one useful at Level 4.)
- Which existing files would need to change if the finding is adopted?

**Impact assessment:**
- Is this a new pattern (requires a new file)?
- Is this an update to an existing pattern (requires editing an existing file)?
- Is this a new agent or command definition?
- Does this affect CLAUDE.md structure (breaking change)?
- Does this affect security rules (requires elevated review)?

---

### Proposal (How to Present)

Every finding that passes filtering and analysis is presented in a standard format. The format ensures that the human reviewer has everything needed to make a decision without additional research.

```
Research Finding: [title]
Source: [url or reference]
Date discovered: [date]
Relevant layer: [layer name and number]
Current framework guidance: [what we say now on this topic]
New insight: [what the source suggests, in 2-3 sentences]
Proposed action: [add pattern / update guide / new agent / new command / no action]
Affected files: [list of files that would change]
Evidence quality: [1-5 stars with brief justification]
Recommendation: [adopt / defer / reject]
Rationale: [why this recommendation, in 1-2 sentences]
```

**Evidence quality scale:**

| Stars | Meaning |
|-------|---------|
| 1 | Single anecdote or unverified claim |
| 2 | Multiple anecdotes or one team's documented experience |
| 3 | Multiple teams' experience or official documentation from a model provider |
| 4 | Measured data from controlled comparison or extensive multi-team validation |
| 5 | Peer-reviewed research or official provider recommendation with supporting data |

---

### Integration (How to Apply)

The human reviews the proposal and decides: adopt, defer, or reject.

**If adopted:**
1. The research agent (or a human) creates a PR against the framework repository with the proposed change.
2. The PR includes the research finding as context in the description.
3. Standard review process applies: maintainer review, quality checks, merge.
4. The change is included in the next version release.
5. Projects pick it up via the `/upgrade` command (see [docs/self-updating-framework.md](self-updating-framework.md)).

**If deferred:**
1. The finding is logged in DECISIONS.md with the rationale for deferral.
2. The entry includes a "revisit by" date — a point at which the finding should be re-evaluated.
3. Deferred findings are reviewed during the quarterly framework review.

**If rejected:**
1. The finding is logged in DECISIONS.md with the rationale for rejection.
2. This prevents the same finding from being rediscovered by a future scan and re-evaluated from scratch. The pipeline learns from its own decisions.

---

## Research Cadence

| Cadence | Activity | Scope |
|---------|----------|-------|
| Weekly | Automated scan of Tier 1 sources | Anthropic docs, Claude Code releases, critical updates |
| Biweekly | Automated scan of Tier 2 sources | Engineering blogs, GitHub trending repos |
| Monthly | Focused deep-dive on one topic | Selected by maintainers based on framework roadmap or community requests |
| Quarterly | Full framework review | Compare entire framework against industry state of the art. Evaluate all deferred findings. |
| On-demand | `/research` command | Specific question from a developer, scoped to their topic |

The weekly and biweekly scans are lightweight: check for new content, apply filters, produce a brief report. The monthly deep-dive is substantial: pick a topic (e.g., "agent memory patterns" or "CI/CD for AI-generated code"), research it thoroughly, and produce a detailed analysis with specific framework change proposals.

The quarterly review is the most comprehensive. It evaluates the entire framework against the current state of practice: are our patterns still best practice? Are there gaps? Are there rules that should be retired? The quarterly review produces a prioritized list of framework improvements for the next quarter.

---

## Making Research Actionable

Every research finding must answer four questions. If it cannot answer at least one, it is not actionable and should be filtered out.

**1. What should we START doing?**
A practice, pattern, or technique the framework does not currently include. Example: "Start including model-specific failure mode documentation in agent definitions, since different models fail differently and agents should be configured to handle their specific model's weaknesses."

**2. What should we STOP doing?**
A practice the framework currently recommends that evidence suggests is counterproductive or obsolete. Example: "Stop recommending manual token counting for cost tracking — Claude Code now provides this automatically via session metadata."

**3. What should we CHANGE in how we do it?**
A practice the framework includes but that evidence suggests should be modified. Example: "Change the blast radius default from 15 files per session to 20 files per session — data from 50 teams shows that the current limit causes unnecessary session splits for medium-sized features without meaningfully improving review quality."

**4. What should we KEEP doing (validated by external evidence)?**
A practice the framework already recommends that external evidence confirms is effective. This is valuable because it strengthens confidence in existing guidance. Example: "Keep the dual-model validation pattern — Stripe's engineering blog reports a 35% reduction in production bugs after adopting write-with-Sonnet, review-with-Opus workflows."

---

## Further Reading

- [Self-Updating Framework](self-updating-framework.md) — the broader architecture for keeping the framework current
- [Research Agent](../agents/research-agent.md) — the agent that executes this pipeline
- [Architecture](architecture.md) — the 7-layer governance stack, especially Layer 7 (Evolution)
- [Quality Control Patterns](quality-control-patterns.md) — patterns that the research pipeline may validate or extend
- [Maturity Model](maturity-model.md) — Level 5 (Self-optimizing) depends on an active research pipeline
