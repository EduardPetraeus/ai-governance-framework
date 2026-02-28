# Self-Updating Framework

A governance framework that cannot keep pace with the tools it governs is a liability. This document describes how the AI Governance Framework stays current automatically, how updates flow from source to project, and what requires human review versus what can be applied safely.

---

## The Problem with Static Frameworks

AI capabilities change monthly. New models ship with new strengths and new failure modes. New tools emerge. New risks surface. Best practices that were current in February 2026 are partially outdated by April 2026.

Static governance frameworks fail in predictable ways:

1. **Stale rules.** A model routing table written for Claude 3.5 Sonnet does not account for Claude Opus 4 capabilities. The framework routes complex tasks to expensive models when a newer, cheaper model handles them better.
2. **Missing patterns.** A new quality control technique gains adoption across the industry. The framework does not include it. Teams discover it independently — or not at all.
3. **Obsolete warnings.** A security concern that applied to an older model version no longer applies. The framework still warns about it, training teams to ignore warnings.
4. **Manual update friction.** If updates require someone to read changelogs, evaluate relevance, and manually apply changes, they will not happen. The person responsible has other priorities. The framework drifts from the state of the art by a little more each month.

The solution is not to make the framework update itself without human oversight. The solution is to build update mechanisms into the framework so that staying current requires minimal effort and maximum awareness.

---

## The Self-Updating Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  YOUR PROJECT REPO                       │
│  CLAUDE.md ← reads from → ai-governance-framework/     │
│                                                          │
│  /upgrade command → checks upstream → proposes changes  │
│  /research command → scans for new patterns → suggests  │
│  /health-check → scores your governance → recommends    │
└─────────────────────────────────────────────────────────┘
         ↑                    ↑                    ↑
    GitHub releases     Community PRs       Research pipeline
    (versioned)         (curated)           (automated)
```

Three sources feed the framework. GitHub releases deliver versioned, tested updates. Community PRs contribute patterns discovered in practice. The research pipeline scans for new knowledge and proposes framework changes. Each source has a different cadence, a different trust level, and a different integration path.

---

## Update Mechanisms

### 1. Version-Based Updates (Upstream Tracking)

The framework repository uses semantic versioning. Each release is a tagged commit with a changelog entry explaining what changed and why.

**How versioning works:**

- **Patch (v1.0.1):** Typo fixes, clarification of existing guidance, documentation improvements. No behavioral change for projects using the framework.
- **Minor (v1.1.0):** New agent templates, new slash commands, new documentation files, updated CI/CD configs that do not break existing setups. Projects can adopt these without modifying existing files.
- **Major (v2.0.0):** Restructured CLAUDE.md sections, changed agent input/output contracts, renamed directories, or removed deprecated patterns. Projects must follow a migration guide.

**The upgrade workflow:**

1. Developer runs the `/upgrade` command (see [commands/upgrade.md](../commands/upgrade.md)).
2. The command checks the framework's latest release against the project's current version (stored in CLAUDE.md or a `.governance-version` file).
3. If a newer version exists, the command displays the changelog: what changed, why it changed, and whether migration steps are needed.
4. The developer decides: upgrade all, upgrade selectively (pick specific files), or skip.
5. Non-breaking updates (new agents, new docs, new patterns) apply cleanly. The developer reviews the diff.
6. Breaking updates present a migration guide. The developer follows the steps and verifies the result.

**What the upgrade command never does:**

- Overwrites CLAUDE.md without human approval.
- Deletes files the project has customized.
- Changes security rules automatically.
- Applies updates to files the project has modified (it flags conflicts instead).

### 2. Community-Driven Updates

Users discover patterns that work in their specific context. Some of those patterns generalize to other teams and projects. The community contribution pipeline turns individual discoveries into framework-wide improvements.

**The contribution flow:**

1. A user encounters a governance challenge and solves it with a new pattern, agent, or workflow.
2. They submit a GitHub PR against the framework repository, following the contribution guidelines in [CONTRIBUTING.md](../CONTRIBUTING.md).
3. Maintainers evaluate: Does this pattern work generally, or only for one team's specific context? Is it evidence-based? Does it contradict existing guidance?
4. Accepted contributions get versioned into the next release.
5. The `/upgrade` command pulls them into projects that opt in.

**Quality bar for community contributions:**

- The pattern must have been used in at least one real project (not designed in theory).
- The submission must include a worked example showing the pattern in action.
- The pattern must not contradict existing security principles.
- The pattern must map to at least one layer of the [7-layer architecture](architecture.md).

### 3. Research-Driven Updates

The research pipeline automates the discovery of new AI governance knowledge. Instead of relying on individuals to track blog posts, papers, and changelogs, a [research agent](../agents/research-agent.md) periodically scans configured sources, filters for relevance, and proposes framework changes.

See [docs/research-pipeline.md](research-pipeline.md) for the full specification.

**The research workflow:**

1. The research agent scans configured sources (Anthropic docs, engineering blogs, academic papers, community forums).
2. It filters findings by actionability, evidence quality, and relevance to the framework.
3. It maps each finding to a specific layer and maturity level.
4. It compares findings against existing framework guidance: does this complement, contradict, or extend what we already say?
5. It presents a structured proposal with a recommended action: adopt, reject, or defer.
6. The human decides. Adopted findings become PRs. Deferred findings go to a backlog. Rejected findings are logged so they are not rediscovered.

---

## What Gets Updated Automatically vs. Manually

Not all framework components carry the same risk when updated. A new agent template is low-risk: if it does not work for your project, you simply do not use it. A change to CLAUDE.md sections is high-risk: it directly affects how every agent in your project behaves.

### Auto-Update (Safe)

These components can be added to a project without modifying existing behavior:

- **New agent templates** — added to `agents/`, available on demand, no impact until invoked.
- **New slash commands** — added to `commands/`, available on demand, no impact until run.
- **Updated CI/CD configs (non-breaking)** — new workflow files or new steps in existing workflows that do not change existing check behavior.
- **New documentation and guides** — added to `docs/`, purely informational.
- **New quality control patterns** — added to `patterns/`, available as reference, no impact until adopted.

### Manual Review Required

These components affect agent behavior or organizational processes directly:

- **CLAUDE.md changes** — the constitution. Any change here alters what agents treat as law. Human review is mandatory.
- **Security rules** — too critical for automatic application. A security rule that is wrong creates either a false sense of safety or unnecessary friction.
- **Model routing table** — depends on current model pricing, availability, and capability. These change with provider updates and project budgets.
- **Maturity model criteria** — organizational impact. Changing what "Level 3" means affects how teams assess and plan their governance adoption.
- **Agent input/output contracts** — changing what agents expect to receive or produce can break existing orchestration workflows.

---

## Versioning Strategy

```
v1.0.0 — Initial release (7 layers, core templates, basic agents)
v1.1.0 — Added: model routing, security scanning, task reporting
v1.2.0 — Added: agent orchestration, quality control patterns
v1.3.0 — Added: self-updating mechanism, research pipeline, drift detection
v2.0.0 — Breaking: restructured CLAUDE.md sections (migration guide provided)
```

### What Every Version Includes

**CHANGELOG entry** — what changed and why, organized by category (Added, Changed, Fixed, Removed, Breaking). The "why" matters more than the "what." "Added research agent" is less useful than "Added research agent because manual tracking of AI governance best practices does not scale."

**Migration guide for breaking changes** — step-by-step instructions for updating a project from the previous version. The guide includes: what files to update, what sections changed, before/after examples, and a verification checklist.

**Compatibility matrix** — which Claude Code version the framework release was tested with, which models it supports, and any known limitations. A framework release that assumes features from Claude Code v2.0 should not be adopted by teams running v1.8.

### Version Tracking in Projects

Projects track their framework version in one of two places:

1. A comment in CLAUDE.md: `# Based on ai-governance-framework v1.2.0`
2. A `.governance-version` file at the project root containing the version string.

The `/upgrade` command reads this version to determine what has changed since the project last updated.

---

## Connecting to Layer 7 (Evolution)

The self-updating architecture is the practical implementation of Layer 7 (Evolution) from the [7-layer governance stack](architecture.md).

Layer 7 asks: "Who updates the rules? How does the system improve itself?" The self-updating framework answers both questions:

**Who updates the rules:**
- Version-based updates come from framework maintainers who curate and test changes.
- Community-driven updates come from practitioners who discover patterns in real projects.
- Research-driven updates come from the [research agent](../agents/research-agent.md) scanning the state of the art.
- The human always makes the final decision on what to adopt.

**How the system improves:**
- The `/upgrade` command provides a low-friction mechanism for pulling upstream improvements.
- The [research pipeline](research-pipeline.md) automates the discovery of new knowledge.
- The [drift detector](../agents/drift-detector-agent.md) identifies when a project has fallen behind framework standards.
- The `/health-check` workflow scores a project's governance implementation and recommends specific improvements.

**The anti-bureaucracy principle from Layer 7 applies here too:** if the update process itself becomes overhead that teams avoid, the framework is failing. The mechanisms described in this document are designed to make staying current easier than falling behind.

---

## Further Reading

- [Architecture](architecture.md) — the 7-layer governance stack, especially Layer 7 (Evolution)
- [Research Pipeline](research-pipeline.md) — how the framework discovers new knowledge automatically
- [Research Agent](../agents/research-agent.md) — the agent that executes the research pipeline
- [Drift Detector Agent](../agents/drift-detector-agent.md) — detects when a project has drifted from framework standards
- [Maturity Model](maturity-model.md) — Level 5 (Self-optimizing) requires a functioning self-updating mechanism
- [Quality Control Patterns](quality-control-patterns.md) — patterns that the research pipeline may discover and propose
