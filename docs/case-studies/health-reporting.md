# Case Study: HealthReporting -- Level 0 to Level 3 in 2 Weeks

> This case study documents how the framework was applied to a real personal health data platform. No actual health data, measurements, or personal values appear anywhere in this document — only architecture descriptions, governance methodology, and process metrics. It is included to demonstrate the framework in a real production context.

---

## 1. Project Context

HealthReporting is a personal health data platform. Solo developer. Built entirely with Claude Code. The goal: a unified health data warehouse that correlates data across sources -- sleep quality vs. next-day heart rate variability, nutrition patterns vs. training performance, weight trends vs. caloric intake.

**Data sources:**
- Apple Health (steps, heart rate, sleep analysis, activity energy)
- Oura Ring (sleep stages, readiness score, HRV, body temperature)
- Withings (weight, blood pressure, body composition)
- Strava (running, cycling, workout details, GPS data)
- Lifesum (food diary, macronutrient tracking)
- Garmin (activity tracking, stress scores)
- Cronometer (micronutrient tracking)
- Manual entries (custom health events, annotations)

**Architecture:** Medallion pattern.
- **Bronze layer:** Raw data ingestion from each API, stored as received
- **Silver layer:** Cleaned, typed, normalized -- one row per entity per day, consistent schema across all sources
- **Gold layer:** Aggregated views optimized for analysis and visualization

**Infrastructure:**
- DuckDB locally for development and testing (zero-config, fast, SQL-native)
- Databricks in production (scalable processing, scheduled pipelines)
- GitHub for source control and CI/CD
- Claude Code as the sole AI development tool

**Team:** One person. This is relevant because it proves the framework works even without the social pressure of a team. If governance helps a solo developer, it helps anyone.

---

## 2. Starting Point: Level 0

The project started at Level 0: no governance files, no session protocol, no audit trail. Claude Code from minute one. The "vibe coding" phase.

**What Level 0 looked like in practice:**

Every session started by explaining the project to the agent from scratch. There were no `CLAUDE.md`, no `PROJECT_PLAN.md`, no `CHANGELOG.md`. The agent had zero memory of what had been built, what had been decided, or what the architectural conventions were.

Sessions were productive in the immediate sense. Connectors were built. SQL was written. Data flowed. The Apple Health connector went up in one session. The Oura connector followed in the next. Each session felt like progress.

But the agent made every decision in isolation. Without context about existing patterns, it invented new ones each time:

- The Apple Health connector used `requests` with manual retry logic
- The Oura connector used `httpx` with built-in retry
- The Withings connector used `requests` with no retry at all
- Three different connectors, three different patterns for the same problem

Table naming was inconsistent: `apple_health_steps`, `oura_sleep_data`, `withings_weight_measurements`. Three different naming conventions in a 5-table database.

Error handling was implemented three different ways. Date parsing was handled differently in every connector. The config file format changed between sessions because the agent had no memory of the previous format.

None of this was visible at the time. Each individual session produced working code. The technical debt was invisible until it accumulated enough to become painful.

---

## 3. The Governance Gap

Six weeks in, the compound effect of Level 0 became visible.

**Context loss between sessions.** "What was the decision about daily vs. hourly granularity for Oura data?" The answer existed somewhere in a previous Claude Code conversation, but those conversations are ephemeral. The decision had been made, discussed, and justified -- and now it was gone. It had to be re-made, and it was made differently the second time, creating an inconsistency between two data sources.

**Architectural drift.** The bronze layer had three different patterns for API pagination. The silver layer had two different approaches to handling missing data (NULL vs. sentinel value). The gold layer had views that assumed one approach and broke when they encountered the other. Each individual session had made a reasonable choice. The aggregate was incoherent.

**Duplicate work.** The Strava connector was started in session 7 and partially built (auth flow + basic data fetch). In session 9, the agent did not know session 7's work existed. It started the Strava connector from scratch with a different approach. The result: two partial implementations that had to be manually reconciled. Approximately 3 hours wasted.

**No definition of done.** Sessions ended when the developer got tired or when the code looked approximately correct. There was no structured session end, no changelog entry, no documented state. Three weeks later, the question "what did we build in February?" could not be answered without reading through git logs commit by commit.

**No way to answer basic questions.** "Which connectors are complete?" "What is the current schema for the silver layer?" "Have we decided on the aggregation strategy for the gold layer?" These questions required archaeology -- reading old code, old commits, and trying to reconstruct decisions from implementation artifacts. The governance files that would have answered them instantly did not exist.

These are not unique to this project. They are the universal failure modes of ungoverned AI-assisted development. The speed that makes AI valuable is the same speed that makes these problems accumulate faster than they would with traditional development.

---

## 4. Week 1: Level 1 -- CLAUDE.md and Session Protocol

The first governance intervention was a `CLAUDE.md` file. Not a comprehensive architecture document -- a focused set of rules for the agent:

- Project identity and architecture overview (bronze/silver/gold, DuckDB + Databricks)
- Naming conventions: `snake_case` everywhere, `stg_` prefix for bronze tables, `dim_`/`fct_` for silver, `vw_` for gold
- Session protocol: read `CHANGELOG.md` and `PROJECT_PLAN.md` at session start, update them at session end
- Security: the never-commit list (API keys, health data, hardcoded paths)
- The 5-file rule: no session touches more than 5 files

The session protocol was the most impactful single change.

**First session with governance:**

The agent read `CHANGELOG.md` (which had been back-filled with 3 sessions of history). It read `PROJECT_PLAN.md` (which listed the remaining connectors). Without being asked, it reported:

- Current phase: Phase 1 (Bronze Layer)
- Last session: Withings connector completed
- Strava connector: partially built in session 7, not completed
- Recommended tasks: (1) Complete Strava connector, (2) Add Lifesum connector, (3) Standardize error handling across existing connectors

This was the moment the framework proved its value. The duplicate work problem from session 9 (starting Strava from scratch) would not happen again. The agent knew about session 7's partial implementation because the governance file told it.

**First session protocol catch:** The agent started writing code for the Strava connector immediately after reading the project state. The session protocol required scope confirmation first. When reminded, the agent presented three task options and waited for confirmation before writing any code. Without this check, the agent would have proceeded with its own prioritization -- which was reasonable but not what the developer wanted.

**Time invested:** 45 minutes to write `CLAUDE.md`, back-fill `CHANGELOG.md`, and create `PROJECT_PLAN.md`.

**Immediate return:** Eliminated context rebuilding at session start (saved ~20 minutes per session), prevented duplicate work (saved ~3 hours in the first week), enforced consistent naming (no more divergent table names).

---

## 5. Week 2: Level 2 -- ADRs, MEMORY.md, Specialized Agents

With the session protocol working, the second week focused on knowledge persistence and decision documentation.

**Architecture Decision Records (ADRs)** were created for decisions that had previously existed only in expired conversation windows:

- **ADR-001: DuckDB as local runtime.** "Use DuckDB for local development and testing. Databricks is the production target. All SQL must be compatible with both." This decision had been made in week 1, discussed again in week 3, and almost reversed in week 5 when a session agent suggested PostgreSQL. Now it was documented and closed.

- **ADR-002: Daily summary granularity.** "All sources use daily granularity in the silver layer, not hourly or raw." This was the decision that had been made and re-made differently, causing the inconsistency between Oura and Apple Health. The ADR closed the discussion permanently.

- **ADR-003: Connector pattern.** "All connectors inherit from `BaseConnector`. The base class handles auth, retry, rate limiting, and schema validation. Individual connectors implement `fetch_data()` only." This standardized the three different connector patterns into one.

- **ADR-004: MERGE INTO for all writes.** "All pipeline stages use `MERGE INTO`, not `INSERT INTO`. This makes every stage safely re-runnable." Eliminated the "did I already run this?" problem during development.

The ADRs immediately stopped the re-litigation problem. When a new session's agent suggested "we could improve performance by using raw hourly data for Oura," the developer pointed to ADR-002. The agent read it, accepted the decision, and moved on. Previously, this would have been a 15-minute discussion that might have resulted in a conflicting implementation.

**MEMORY.md** was configured with project-specific knowledge: confirmed patterns (the connector pattern, the MERGE INTO pattern), anti-patterns discovered (do not use `SELECT *` in transforms -- schema changes broke downstream silently), and team preferences (show full diffs before committing, sessions limited to 1--2 hours).

**First specialized agents** were created as slash commands:
- `/session-start` -- automated session initialization with governance file reading
- `/session-end` -- automated session close with CHANGELOG and PROJECT_PLAN updates
- `/project:review` -- reviews current code against ARCHITECTURE.md conventions
- `/security-review` -- scans for secrets, PII, and data governance violations

**MEMORY.md's first catch:** In session 14, the agent proposed implementing a caching layer for API responses. MEMORY.md contained an anti-pattern entry: "Caching was considered and rejected in session 8 -- the complexity of cache invalidation for health data (which updates irregularly) exceeded the benefit for a daily-batch pipeline." The agent read this, acknowledged the prior decision, and moved on. Without MEMORY.md, this would have been another 20-minute discussion and possibly a wasted implementation.

---

## 6. Week 3: Level 3 -- CI/CD, AI PR Review, Security Scanning

The third week implemented automated enforcement. The transition from "the agent should follow these rules" to "the agent cannot merge without following these rules."

**GitHub Actions CI pipeline:**
- `ruff` for linting and formatting (Python)
- `sqlfluff` for SQL convention enforcement
- `gitleaks` for secret scanning on every push
- Custom naming convention script (validates `stg_`, `dim_`, `fct_`, `vw_` prefixes)
- Governance file update check: if any `.py` or `.sql` file changed, `CHANGELOG.md` must also be updated

**First governance check failure:** A session that added a new silver transform committed the SQL file but forgot to update `CHANGELOG.md`. The CI check failed with: "Code files changed but CHANGELOG.md not updated. Add a session entry before merging." This was exactly the kind of slip that, without enforcement, would have left a gap in the project record.

**AI PR review agent** set up as a GitHub Action:
- Reads the PR diff plus `CLAUDE.md` plus `ARCHITECTURE.md`
- Posts review comments on convention violations, architecture issues, potential security concerns
- Returns PASS / WARN / FAIL visible in the PR checks

**First AI PR review catch:** A new connector used `snake_case` for the class name (`oura_heart_rate_connector`) instead of `PascalCase` (`OuraHeartRateConnector`). The naming convention in `CLAUDE.md` specified `snake_case` for files and variables but `PascalCase` for classes. The AI reviewer flagged it. Without the review, the inconsistency would have been committed and become a precedent for future connectors.

**Pre-commit hooks:**
- `gitleaks` for secrets (caught 2 near-misses: a test fixture that contained a realistic-looking API key pattern, and a config file with a hardcoded localhost connection string)
- Custom pattern check for health data PII patterns
- File structure validation (new connectors must be in `src/connectors/`)

**Model routing** was added to `CLAUDE.md`. The routing table mapped 11 task types to optimal model tiers: Opus for architecture decisions and security reviews, Sonnet for code generation and documentation, Haiku for config edits and status checks. The first Opus security review caught a hardcoded file path that had slipped through pre-commit hooks -- the additional cost (~$0.35 for the review) paid for itself immediately.

---

## 7. The 4-PR Session

One session demonstrated what governed AI development can accomplish when every piece of the framework is working together.

In a single 3-hour session, four PRs were created, reviewed, and merged. Each addressed a different governance dimension. None of them touched the same files. Each was small, focused, and independently reviewable.

**PR 1: Governance Sync** (8 minutes human review)

The governance sync agent was implemented as a session-start step. It compares the current codebase against `PROJECT_PLAN.md`, `ARCHITECTURE.md`, and `CHANGELOG.md`, then reports drift before the session's actual work begins.

What the agent found: 3 source files existed in the codebase that were not reflected in `ARCHITECTURE.md`. The architecture document still described 5 connectors; the codebase had 8. The agent generated a drift report, updated `ARCHITECTURE.md`, and committed.

**PR 2: Model Routing** (12 minutes human review)

The routing table was added to `CLAUDE.md`, mapping 11 task types to optimal models. Self-awareness instructions were added: the agent announces its model at session start and flags when a task exceeds its tier. The `COST_LOG.md` template was created.

**PR 3: Security Protocol** (15 minutes human review)

Pre-commit hooks for `gitleaks` and custom pattern matching. A `.claudeignore` file covering sensitive file types. Updated `CLAUDE.md` with security scanning triggers: scan per file, per session start, per session end.

**PR 4: Mandatory Task Reporting** (10 minutes human review)

The task reporting format was added to `CLAUDE.md`: the box-drawing progress display, goal mapping, and cumulative session summary. This was the fix for the "yes-man" anti-pattern -- the agent must report what it did and why it matters after every task, even if the user says "just keep going."

**Total session time:** ~3 hours.
**Total human review time:** ~45 minutes.
**Result:** The project went from partial governance to full Level 3 enforcement in one session.

What made this session exceptional was not the speed. It was the structure. Each PR had clear scope defined before coding began. Each PR changed a small number of files. None created dependencies on the others. The session protocol kept the agent focused. The governance framework made the framework itself self-improving.

---

## 8. Results: The Real Numbers

After the 2-week governance implementation, across the full project lifecycle:

| Metric | Value |
|--------|-------|
| Total commits | 137 |
| Velocity improvement | 16x (methodology below) |
| Specialized agents created | 12 |
| Slash commands implemented | 11 |
| Architecture Decision Records | 4 |
| Secrets leaked to any branch | 0 (gitleaks caught 2 near-misses) |
| Governance level achieved | Level 3 (from Level 0 in 2 weeks) |

### The 16x Velocity Measurement -- Methodology

This is the number that demands scrutiny. Here is how it was measured:

**Pre-governance (Level 0):** Across 14 sessions in 6 weeks, approximately 28 meaningful tasks were completed. "Meaningful task" is defined as a unit of work that advances the project plan: a connector built, a transform written, a bug fixed, a decision documented. This excludes duplicate work, abandoned implementations, and rework.

Effective rate: ~2 meaningful tasks per day of active development.

**Post-governance (Level 3):** Across 8 sessions in 2 weeks, approximately 64 meaningful tasks were completed. The session protocol eliminated duplicate work. ADRs eliminated re-litigation. The project plan made task selection immediate rather than a 20-minute discussion at session start. Scope management prevented the agent from doing unrequested work.

Effective rate: ~32 meaningful tasks per day of active development.

**32 / 2 = 16x.**

The 16x is not because the agent types faster. It is because the agent works in the right direction consistently. At Level 0, a significant fraction of completed work was later redone, abandoned, or incompatible with other work. At Level 3, nearly everything the agent builds is usable because the governance system ensures it aligns with the architecture, follows established patterns, and fits the project plan.

### The 12 Specialized Agents

| Agent | Purpose |
|-------|---------|
| session-start | Automated governance file reading and sprint status |
| session-end | CHANGELOG update, PROJECT_PLAN update, summary commit |
| governance-sync | Drift detection at session start |
| code-reviewer | Convention and architecture compliance |
| security-reviewer | Secret scanning, PII detection, data governance |
| architecture-reviewer | Cross-system pattern validation |
| connector-scaffold | Generate new connector from BaseConnector template |
| sql-transform | Generate silver-layer SQL transform from template |
| test-generator | Generate test suite for a new component |
| docs-updater | Update ARCHITECTURE.md and API docs |
| cost-tracker | Record session cost in COST_LOG.md |
| sprint-reporter | Generate sprint velocity summary |

### The 4 ADRs

| ADR | Decision | Impact |
|-----|----------|--------|
| ADR-001 | DuckDB as local runtime | Prevented 3 re-discussions about local database choice |
| ADR-002 | Daily summary granularity | Eliminated the hourly-vs-daily inconsistency permanently |
| ADR-003 | BaseConnector pattern | Standardized 8 connectors under one pattern |
| ADR-004 | MERGE INTO for all writes | Made every pipeline stage safely re-runnable |

Estimated time saved by preventing re-litigation: 8--12 hours across the project lifecycle.

---

## 9. Lessons Learned

### What Worked

**Session protocol -- the highest-impact single addition.** Requiring the agent to read CHANGELOG and PROJECT_PLAN at session start, and update them at session end, eliminated the context loss problem. Every session begins with a 2-minute orientation that saves 20--30 minutes of re-explanation. The agent arrives knowing what was built, what was decided, and what is planned.

**ADRs -- eliminated decision loops.** "Should we use daily or hourly granularity?" was asked and answered three separate times at Level 0. After ADR-002, it was answered once. The agent references the ADR when the topic arises and moves on. The compounding value is significant: each ADR prevents re-discussion not once but every time the topic naturally recurs.

**Model routing -- 20% cost reduction with quality improvement.** Running security reviews with Opus instead of Sonnet caught issues that Sonnet generated with apparent confidence. Running config edits with Haiku instead of Sonnet reduced cost per trivial task by 10x. The routing table paid for itself in the first week.

**Mandatory task reporting -- eliminated the yes-man problem.** Before task reporting, sessions would end with "what did we actually build?" Now the running summary is maintained automatically. The developer knows exactly what changed, why it matters, and what is next -- without asking.

**Governance file update enforcement via CI.** Making CHANGELOG updates a required CI check meant the project state was always current. The friction of writing a CHANGELOG entry is approximately 2 minutes. The value of having complete session history is measured in hours saved per week.

### What Did Not Work Initially

**CLAUDE.md that was too long.** When CLAUDE.md grew beyond 200 lines, the agent began missing rules at the bottom. Critical rules buried at line 180 had weaker enforcement than rules at line 10. The agent's context window is finite. Under pressure from a long system prompt, later sections receive less attention.

**Fix applied:** CLAUDE.md was shortened to under 150 lines. Critical rules (security, session protocol) were moved to the top. Optional sections (model routing, governance sync) were placed at the bottom with clear `# OPTIONAL` markers.

**Sessions that were too broad.** One session attempted to add three new connectors simultaneously. Each connector touched the same configuration file. The agent managed the merge conflicts but introduced subtle inconsistencies in the shared config. The 5-file rule was created specifically because of this experience.

**Fix applied:** Strict single-layer, single-feature scoping. The 5-file rule was added to CLAUDE.md and enforced during scope confirmation.

**Manual session-end compliance.** During crunch periods, the session-end protocol was skipped. CHANGELOG updates were missed. The subsequent session's governance sync caught the drift, but the gap in the record made it harder to reconstruct what had changed.

**Fix applied:** The governance file update check was added to CI. Code changes without CHANGELOG updates cannot be merged. Automation replaced discipline.

---

## 10. Honest Assessment: What Is Still Missing

This section exists because credibility requires honesty. The framework is not complete. Here is what is still missing and why.

**Test coverage: approximately 20%.** The governance framework does not automatically generate tests. The session protocol does not enforce test writing. Integration tests exist for the ingestion engine but not for individual connectors. Each connector should have tests against realistic mock API responses. This is the largest quality gap.

**Why it is still missing:** Testing was deprioritized in favor of getting the governance framework itself in place. The irony is not lost -- governance without test coverage is governance without verification. This is the top priority for the next sprint.

**Live data pipeline.** DuckDB works locally. The Databricks deployment pipeline is not yet automated. Moving from "it works on my machine" to "it runs in production on a schedule" requires infrastructure work that the governance framework does not address.

**Why it is still missing:** The project was focused on data modeling and connector building, not deployment automation. The governance framework helps ensure the code is production-quality, but deploying it is a separate workstream.

**Governance dashboard.** Governance metrics (session count, cost per session, compliance rate, velocity trend) are tracked in flat Markdown files. There is no visual dashboard. Answering "what is our governance compliance rate?" requires manually counting CHANGELOG entries.

**Why it is still missing:** Building a dashboard is a feature, not a governance improvement. The Markdown files are sufficient for a solo developer. A team would need a dashboard.

**Real-time architectural drift detection.** Drift is currently detected at session start by the governance sync agent. This is retrospective -- the drift has already happened. Real-time detection would flag drift as it occurs, within the session, before the commit.

**Why it is still missing:** Real-time drift detection requires the agent to continuously compare its changes against ARCHITECTURE.md during the session, not just at start. This adds latency and cost to every task. The trade-off has not been worth it for a solo developer. It would be worth it for a team.

---

## 11. The Key Insight

**Governance does not slow you down. It redirects 5% of velocity into structure so the remaining 95% builds the right thing.**

The governance overhead is real and measurable:

| Governance Activity | Time per 2-Hour Session |
|---|---|
| Session start: read governance files, confirm scope | 3 minutes |
| Task reporting: cumulative status after each task | 5 minutes total |
| Session end: CHANGELOG update, PROJECT_PLAN update, summary commit | 5 minutes |
| ADR writing (when a decision is made) | 5 minutes (amortized) |
| Security scan at session end | 2 minutes |
| **Total governance overhead** | **~20 minutes per 2-hour session (~17%)** |

In exchange for that 20 minutes:

- **Zero duplicate work.** The governance sync catches drift before it compounds. The CHANGELOG prevents starting work that was already done.
- **Consistent architecture.** ADRs and CLAUDE.md prevent pattern divergence. Eight connectors follow one pattern, not eight.
- **Confidence when merging.** CI gates catch the issues the session protocol misses. No anxiety about "did I break something?"
- **A codebase that explains itself.** A new developer or a new AI agent can understand the project from the governance files alone, without reading the code or asking the developer.

The 16x velocity number includes the governance overhead. The overhead is not subtracted from productivity -- it is the reason for the productivity. Without governance, the raw speed is higher but the useful output is lower because so much of it is rework, duplication, or architecturally incompatible.

The hardest part of adopting governance is the first week: writing CLAUDE.md, establishing the session protocol, accepting that sessions should end with documentation instead of just closing the terminal. After the first week, the overhead disappears into habit, and the benefits compound with every subsequent session.

---

*Related guides: [Getting Started](../getting-started.md) | [Maturity Model](../maturity-model.md) | [Rollback and Recovery](../rollback-recovery.md) | [Productivity Measurement](../productivity-measurement.md)*
