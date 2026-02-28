# Case Study: HealthReporting — From Vibe Coding to Level 3 Governance in 2 Weeks

## 1. Project Context

HealthReporting is a personal health data platform built by a solo developer. The architecture follows the medallion pattern:

- **Bronze layer**: raw data ingestion from external APIs, stored as-is
- **Silver layer**: cleaned, typed, and normalized data; one row per entity per day
- **Gold layer**: aggregated views optimized for analysis and visualization

**Infrastructure:**
- DuckDB locally (development and testing)
- Databricks in cloud (production processing and storage)
- GitHub Actions for CI/CD
- Claude Code as the primary AI development tool

**Health data sources integrated:**
- Apple Health (steps, heart rate, sleep, activity)
- Oura Ring (sleep stages, readiness score, heart rate variability)
- Withings (weight, blood pressure, body composition)
- Strava (running, cycling, workout data)
- Lifesum (food diary, nutrition tracking)
- Garmin (additional activity tracking)
- Cronometer (micronutrient tracking)
- Manual entries (custom health events)

The project's ambition: a unified health data warehouse that enables cross-source analysis — correlating sleep quality with next-day heart rate variability, or nutrition patterns with training performance.

---

## 2. Starting Point

The project began with no governance. Claude Code from day one. Fast initial progress. This is the "vibe coding" phase.

**What vibe coding looked like in practice:**

Every session started by explaining context to the agent from scratch. There were no persistent governance files — the agent had no memory of what had been decided, what had been built, or what the architectural conventions were.

Sessions were productive in the immediate sense: connectors were built, SQL was written, data flowed. The bronze layer for Apple Health went up quickly. The Oura connector followed. Each session felt productive.

**The warning signs that went unnoticed initially:**

- The Oura connector used a different API client pattern than the Apple Health connector, because the agent was not aware of the first connector when building the second
- Table naming was inconsistent — `apple_health_steps` and `oura_sleep_data` followed different conventions
- Error handling was implemented three different ways across three connectors
- There was no record of which SQL schema decisions had been made or why

This is normal for vibe coding. The code works. The technical debt is invisible until it accumulates enough to become painful.

---

## 3. The Governance Gap

By the time the project had five connectors and three silver layer transforms, the governance gap became visible:

**Architectural drift**: Each session started fresh, so the agent made reasonable-but-different decisions each time. The bronze layer had three different patterns for handling API pagination. The silver layer had two different approaches to handling missing data.

**Lost context between sessions**: "What was the decision about daily vs. hourly granularity for Oura data?" The answer existed somewhere in a previous conversation, but there was no way to find it. The decision had to be re-made, potentially differently than before.

**Duplicate work**: The Strava connector was started in session 7 and partially built, then started again in session 9 because session 9's agent did not know session 7's work existed. The result was two partial implementations that had to be reconciled.

**No clear definition of done**: Sessions ended when the developer got tired or the code looked approximately correct. There was no structured session end, no CHANGELOG, no documented state of the project.

These are not unique to this project. They are the universal failure modes of ungoverned AI-assisted development. The speed that makes AI valuable is the same speed that makes these problems accumulate faster than they would with traditional development.

---

## 4. Implementation Timeline

### Week 1: CLAUDE.md and Session Protocol (Level 1)

The first governance intervention was a `CLAUDE.md` file. Not a lengthy architecture document — a focused set of rules for the agent:

- Project identity and architecture overview (bronze/silver/gold, DuckDB + Databricks)
- Naming conventions (snake_case everywhere, `stg_` prefix for bronze, `dim_`/`fct_` for silver)
- Session protocol: what to read at start, how to report during, what to update at end
- The never-commit list
- The 5-file rule for sessions

The session protocol was the most impactful change. Requiring the agent to read `CHANGELOG.md` and `PROJECT_PLAN.md` at session start meant that context was no longer rebuilt from scratch each time. The agent arrived at each session knowing what had been done, what was planned, and what the architectural conventions were.

**First session with governance in place:**
- Agent read CHANGELOG (3 sessions of history documented)
- Agent identified that Strava connector was partially built and carried over from session 7
- Agent completed the Strava connector following the same pattern as Oura (instead of inventing a new pattern)
- Session ended with CHANGELOG update and commit

This was the moment the framework demonstrated its value. A problem that would have required 30 minutes of manual investigation was solved automatically by the governance system.

### Week 2: ADRs, MEMORY.md, First Agents (Level 2)

With the session protocol working, the second week focused on knowledge management.

**Architecture Decision Records (ADRs)** were created for three decisions that had previously existed only in expired conversation windows:

- ADR-001: DuckDB as local runtime, Databricks as cloud target
- ADR-002: Daily summary granularity for all sources (not hourly/raw)
- ADR-003: Connector pattern — all connectors inherit from BaseConnector

These ADRs immediately stopped the re-litigation problem. An agent that suggested hourly granularity for a new data source was shown ADR-002 and accepted the decision without requiring re-explanation.

**First specialized agents** were created as slash commands:
- `/project:review` — reviews the current state against ARCHITECTURE.md
- `/security-review` — scans for secrets and data governance violations
- `/session-start` — automated session initialization
- `/session-end` — automated session close, CHANGELOG update, commit

**MEMORY.md** (Claude Code's project memory) was configured to maintain key context across sessions without requiring explicit loading from CHANGELOG each time.

### Week 3: CI/CD, AI PR Review, Security Scanning (Level 3)

The third week implemented automated enforcement.

**GitHub Actions CI pipeline:**
- `ruff` linting and formatting checks
- `sqlfluff` for SQL conventions
- `gitleaks` secret scanning on every commit
- Naming convention validation script
- Governance file update check (CHANGELOG must be updated if code changed)

**AI PR review agent** set up as a GitHub Action:
- Reads PR diff + CLAUDE.md + ARCHITECTURE.md
- Posts review comments on convention violations, architecture issues, potential security concerns
- PASS / WARN / FAIL result visible in PR checks

**Pre-commit hooks:**
- Secret scanning (gitleaks)
- Custom pattern checks (hardcoded paths, PII patterns)
- File structure validation (new files in correct directories)

**Model routing** added to CLAUDE.md, directing different task types to appropriate model tiers.

---

## 5. Results: The Real Numbers

After two weeks of governance implementation, across 137 total commits:

| Metric | Value |
|--------|-------|
| Total commits | 137 |
| Velocity improvement | 16x (measured by tasks/day before vs. after governance) |
| Specialized agents created | 12 |
| Slash commands implemented | 11 |
| ADRs written | 4 |
| Secrets leaked to any branch | 0 |
| Governance level reached | Level 3 (from Level 0 in 2 weeks) |

**The 16x velocity measurement:**
Pre-governance: approximately 0.5 meaningful tasks per session (sessions frequently went off-track, produced duplicate work, or required significant rework).
Post-governance: approximately 8 meaningful tasks per session (clear scope, defined acceptance criteria, session protocol ensuring context continuity).

**The 12 specialized agents** covered:
- Session management (start, end, governance sync)
- Code review (architecture, conventions, security)
- Documentation (CHANGELOG, ARCHITECTURE.md updates)
- Data pipeline (connector scaffolding, SQL transform generation)
- Testing (smoke test generation, data validation)

**The 4 ADRs** documented decisions that had previously been made and remade across multiple sessions, preventing approximately 8–12 hours of accumulated re-litigation across the project lifecycle.

---

## 6. The 4-PR Session

One session stands out as a demonstration of what governed AI development can accomplish.

In a single session, four PRs were created and merged, each addressing a different governance dimension:

**PR 1: Governance Sync**
The governance sync agent was implemented as a session-start step. It compares the current codebase against `PROJECT_PLAN.md`, `ARCHITECTURE.md`, and `CHANGELOG.md`, then reports drift. Any drift is addressed before the session's actual work begins.

*What the agent did*: Scanned the repository, identified 3 files that existed in the codebase but were not reflected in ARCHITECTURE.md, generated a drift report, updated ARCHITECTURE.md, committed as `docs: governance sync`.

*Human review*: 8 minutes to read the diff and confirm the architecture updates were accurate.

**PR 2: Model Routing**
The routing table was added to CLAUDE.md, mapping 11 task types to optimal model tiers. Self-awareness instructions were added so the agent announces its model at session start and flags mismatches.

*What the agent did*: Wrote the routing table based on task type definitions, added self-awareness prompts to the session protocol, created the `COST_LOG.md` template.

*Human review*: 12 minutes to review the routing decisions and validate the cost estimates.

**PR 3: Security Enhancement**
Pre-commit hooks for gitleaks and custom pattern matching, plus a `.claudeignore` file covering all sensitive file types for the project.

*What the agent did*: Generated `.pre-commit-config.yaml`, created the `.claudeignore` file, added a custom pattern script for health data-specific PII patterns, updated `CLAUDE.md` with the security scanning instructions.

*Human review*: 15 minutes to review patterns, confirm coverage, and test the hooks.

**PR 4: Task Reporting**
The mandatory task reporting format was added to CLAUDE.md — the progress bars, goal mapping, and cumulative session summary that make session status visible without requiring the developer to ask for it.

*What the agent did*: Wrote the reporting format spec, added it to CLAUDE.md, created an example in the CHANGELOG to demonstrate the format.

*Human review*: 10 minutes to read and confirm the reporting format was clear and actionable.

**Total session time**: approximately 3 hours.
**Total human review time**: approximately 45 minutes.
**Total value**: a project that went from partial governance to full Level 3 enforcement in one session.

This session was possible because the session protocol, scoped tasks, and model routing all worked together. Each PR had clear scope, clear acceptance criteria, and was reviewed independently. None of them touched the same files. The agent knew what to do because the governance system told it.

---

## 7. Lessons Learned

### What Worked

**Session protocol**: The most impactful single addition. Requiring the agent to read CHANGELOG and PROJECT_PLAN at session start, and update them at session end, eliminated the context loss problem. Every session now begins with a brief orientation that takes 2 minutes and saves 20–30 minutes of re-explanation.

**Model routing**: Running security reviews with Opus instead of Sonnet caught issues that Sonnet was generating with apparent confidence. The first Opus security review caught a hardcoded path in a config file that had slipped through the pre-commit hooks. The additional cost (approximately $0.35 for that review) was worth it.

**ADRs**: The decision loop problem disappeared. "Should we use daily or hourly granularity?" was a question that had been answered three times. After ADR-002, it was answered once. The agent references the ADR when the topic arises and moves on.

**Mandatory CHANGELOG**: Making CHANGELOG updates a required part of session end, enforced by CI, meant that the project state was always accurate. The friction of writing a CHANGELOG entry is low; the value of having a complete session history is high.

### What Did Not Work

**CLAUDE.md that is too long**: When CLAUDE.md grew beyond 200 lines, sections at the bottom were sometimes missed. The agent's context window is finite. Critical rules buried at line 180 had less enforcement than rules at the top. The fix: keep CLAUDE.md under 200 lines, put the most important rules first.

**Sessions that were too broad**: The session that tried to add three new connectors simultaneously ran into cascade problems. Each connector touched the same configuration file, and the agent managed the merge conflicts but introduced subtle inconsistencies. The 5-file rule exists for this reason — the session that respected it had cleaner output than the one that ignored it.

**Manual session end compliance**: During crunch periods, the session end protocol was skipped. CHANGELOG updates were missed. The subsequent session's governance sync caught the drift, but the gap in the record made it harder to understand what had changed. Automation that requires manual compliance is only as reliable as the developer's discipline.

---

## 8. Honest Assessment

**What is working well:**
- 0 secrets leaked across 137 commits with active security scanning
- Clear architectural consistency across all 8 data source connectors
- Every session has a documented start and end state
- 4 ADRs preventing re-litigation of closed decisions
- CI/CD catches convention violations before they reach main

**What is still missing:**

*Comprehensive test suite*: Coverage is at approximately 62%. Integration tests exist for the ingestion engine but not for individual connectors. Each connector should have a test that validates against a realistic mock API response.

*Live data pipeline*: The project has a working batch pipeline. A streaming or near-real-time pipeline for higher-frequency health events (continuous heart rate, activity) has not been built. This is the next major capability gap.

*User dashboard*: The gold layer has aggregated views. There is no visualization layer. The health data exists and is correct; seeing it requires writing SQL queries. A simple dashboard is the highest-value missing piece.

*Automated cost optimization*: The model routing table is defined and the agent follows it. But there is no automated analysis of whether actual model usage matches the routing table recommendations. This would require parsing the COST_LOG and comparing to the routing decisions.

---

## 9. Key Insight

"The framework does not slow you down. It redirects 5% of velocity into governance so the remaining 95% builds the right thing."

Before governance: sessions were fast, output was inconsistent, and a significant fraction of completed work was redone, abandoned, or incompatible with other completed work. The 16x productivity figure is not about the agent working faster — it is about the agent working in the right direction consistently.

The governance overhead is real: session protocol, CHANGELOG updates, ADR writing, security reviews. In practice, it amounts to approximately 15–20 minutes per 2-hour session. The investment returns:

- Zero duplicate work (the governance sync catches drift before it compounds)
- Consistent architecture across all components (ADRs and CLAUDE.md prevent divergence)
- Confidence when merging (CI gates catch the issues the session protocol misses)
- A codebase that a new developer or new AI agent can understand from the governance files alone

The hardest part of adopting governance is the first week — writing CLAUDE.md, establishing the session protocol, accepting that sessions should end with documentation. After the first week, the governance overhead disappears into habit, and the benefits compound with every subsequent session.

---

*Related guides: [Enterprise Playbook](../enterprise-playbook.md) | [Metrics Guide](../metrics-guide.md) | [Model Routing](../model-routing.md) | [Rollback and Recovery](../rollback-recovery.md)*
