# Pattern: Progressive Trust

## Problem

Human review of AI output does not scale. Reviewing every line of every session is unsustainable — it eliminates the velocity advantage of using an AI agent. But trusting the agent completely and immediately is dangerous. One bad session can introduce architectural drift, security vulnerabilities, or subtle logic errors that compound over time.

Most teams oscillate between two extremes. They start with exhaustive review, burn out after a few sessions, then abruptly switch to near-complete trust after a string of successful outputs. This is the worst of both worlds: the early sessions are slow and tedious, and the trust transition is not based on evidence — it is based on fatigue.

The result: critical changes get rubber-stamped because the reviewer has decided the agent "usually gets it right." The one session where it does not get it right is the one that ships a production bug.

## Solution

Formalize a progressive trust model with explicit levels, per-domain tracking, evidence-based transitions, and immediate reset on quality failure.

### Trust Levels

| Level | Name | Review Depth | When |
|:-----:|------|-------------|------|
| 1 | Full Review | Review every file, every line, every decision | Sessions 1-5 or after a trust reset |
| 2 | Logic Review | Review logic and architecture; trust syntax, formatting, and convention adherence | Sessions 5-15 with zero quality issues |
| 3 | Architecture Review | Review architecture decisions and integration points; trust implementation details | Sessions 15-30 with zero quality issues |
| 4 | Task Review | Review at task level; trust the agent within established patterns | Sessions 30+ with zero quality issues |

Session counts are guidelines. The real criterion is consecutive sessions with zero quality issues in the relevant domain. A team that encounters issues at session 8 stays at Level 1 until they have 5 clean sessions from that point.

### Trust Dimensions

Trust is not global. An agent can be highly trusted for code generation but not trusted for architecture decisions. Track each dimension independently:

- **Code generation** — syntax, patterns, conventions, implementation correctness
- **Architecture decisions** — component boundaries, data models, integration patterns, dependency choices
- **Security** — handling of secrets, PII, authentication, authorization, input validation
- **Documentation** — CHANGELOG accuracy, ADR quality, README updates, inline comments
- **Testing** — coverage quality, assertion meaningfulness, edge case identification, test isolation

### Trust Tracking in MEMORY.md

```yaml
trust_levels:
  code_generation: 3       # Level 3: trust implementation, review architecture
  architecture: 2          # Level 2: recent architectural drift detected, reviewing logic
  security: 3              # Level 3: zero security findings in 20 sessions
  documentation: 4         # Level 4: consistently high quality, review at task level
  testing: 2               # Level 2: mediocre edge case coverage, reviewing logic

  last_assessment_date: "2026-02-28"
  sessions_since_last_issue:
    code_generation: 18
    architecture: 3
    security: 22
    documentation: 41
    testing: 7

  last_reset:
    domain: "architecture"
    previous_level: 3
    reset_to: 2
    reason: "Session 31: agent introduced circular dependency between auth and user modules"
    date: "2026-02-20"
```

## When to Use

- Any project with ongoing AI agent sessions (more than 5 total sessions)
- Multi-session projects where review fatigue is a real risk
- Teams where more than one person reviews agent output (shared trust model prevents inconsistent review depth)
- Projects where different types of changes carry different risk levels

## When NOT to Use

- One-off sessions or short-lived prototypes where review investment is not justified
- When all sessions are inherently high-risk (security tooling, financial systems) and full review is always warranted regardless of track record
- When the team has not established quality baselines — you cannot measure trust without knowing what "good" looks like

## Implementation

### Step 1: Establish baselines during Level 1

During the first 5 sessions, review everything. Use this period to:

1. Identify the agent's strengths and weaknesses per domain
2. Document quality issues with specific examples
3. Establish what "good output" looks like for this project
4. Configure automated checks that catch the issues you find manually

```yaml
# MEMORY.md — after initial assessment period
baseline_assessment:
  date: "2026-02-28"
  sessions_reviewed: 5
  findings:
    code_generation:
      strengths: ["follows project conventions", "consistent naming", "good error handling"]
      weaknesses: ["occasionally misses edge cases in date parsing", "verbose logging"]
      quality_issues_found: 1
      initial_trust_level: 1
    architecture:
      strengths: ["respects module boundaries", "follows existing patterns"]
      weaknesses: ["tendency to add unnecessary abstractions"]
      quality_issues_found: 2
      initial_trust_level: 1
    security:
      strengths: ["never hardcodes credentials", "uses environment variables"]
      weaknesses: ["does not always validate input length"]
      quality_issues_found: 1
      initial_trust_level: 1
```

### Step 2: Define promotion criteria

A domain advances to the next trust level when:

1. The specified number of consecutive sessions have zero quality issues in that domain
2. Automated checks consistently pass without manual intervention
3. The types of errors found in previous reviews are now caught by automated tooling

```yaml
promotion_criteria:
  level_1_to_2:
    consecutive_clean_sessions: 5
    automated_checks_passing: true
    previous_error_types_automated: true
  level_2_to_3:
    consecutive_clean_sessions: 10
    no_logic_errors: true
    architecture_decisions_aligned: true
  level_3_to_4:
    consecutive_clean_sessions: 15
    no_architectural_drift: true
    security_scan_clean: true
    test_coverage_stable: true
```

### Step 3: Define demotion triggers

Trust resets are immediate and specific:

| Trigger | Action |
|---------|--------|
| Logic error shipped to production | Reset that domain to Level 1 |
| Security vulnerability introduced | Reset security to Level 1, reduce all domains by 1 level |
| Architectural drift detected | Reset architecture to Level 1 |
| Test coverage decreased without justification | Reset testing to Level 1 |
| Agent modified governance files without permission | Reset all domains to Level 1 |
| Three minor issues in one session | Reset affected domain by 1 level |

### Step 4: Adjust review depth by level

**Level 1 — Full Review:**
- Read every line of every changed file
- Verify every claim in the agent's summary
- Run all automated checks manually to confirm they work
- Check `git diff --stat` against the session scope

**Level 2 — Logic Review:**
- Read the logic and control flow of changed files
- Trust that syntax, naming, and formatting follow conventions (linters verify this)
- Verify architecture decisions against existing patterns
- Spot-check 2-3 functions for edge case handling

**Level 3 — Architecture Review:**
- Review component boundaries and integration points
- Verify no new dependencies were introduced without justification
- Trust implementation details within established patterns
- Check that the session stayed within its declared scope

**Level 4 — Task Review:**
- Verify the task was completed as specified
- Review the agent's compliance report against the [output contract](output-contracts.md)
- Trust the implementation within established patterns
- Focus human attention on novel or unprecedented decisions

### Step 5: Log trust changes

Every trust level change is logged with context:

```yaml
trust_log:
  - date: "2026-02-10"
    domain: "code_generation"
    change: "1 → 2"
    reason: "5 consecutive clean sessions, all automated checks passing"
  - date: "2026-02-18"
    domain: "documentation"
    change: "2 → 3"
    reason: "10 consecutive sessions with accurate CHANGELOGs and clear ADRs"
  - date: "2026-02-20"
    domain: "architecture"
    change: "3 → 2"
    reason: "Circular dependency introduced between auth and user modules"
  - date: "2026-02-28"
    domain: "code_generation"
    change: "2 → 3"
    reason: "18 consecutive clean sessions since last promotion"
```

## Example

A solo developer starts using Claude Code for a data pipeline project.

**Weeks 1-2 (Level 1 across all domains):** The developer reviews every file in every session. They find that the agent consistently writes correct Python but occasionally misses edge cases in date parsing and tends to add unnecessary abstraction layers. They document these patterns and add a date-parsing test template to their project.

**Week 3 (Code generation: Level 2, Architecture: Level 1):** Code generation is promoted after 5 clean sessions. The developer now reviews logic and architecture but trusts syntax and conventions. Architecture stays at Level 1 because the abstraction tendency requires ongoing review.

**Week 5 (Code: Level 3, Architecture: Level 2, Security: Level 2):** Code generation is promoted again. Architecture is promoted after the developer adds a CLAUDE.md rule forbidding new abstraction layers without explicit permission, which eliminates the issue. Security is promoted after zero findings in 10 sessions.

**Week 6 — Incident:** The agent introduces a circular dependency between two modules. Architecture is immediately reset to Level 1. Other domains are unaffected. The developer adds an automated circular dependency check to CI/CD. Architecture begins its progression again with the new automated safeguard in place.

**Week 8:** Architecture returns to Level 2 after 5 clean sessions with the new automated check. The automated check has caught and prevented two potential circular dependencies during this period, validating the promotion.

## Evidence

Progressive trust mirrors the supervision model used in professional apprenticeships, medical residencies, and aviation training. In each domain, the principle is identical: start with full supervision, reduce oversight as competence is demonstrated, and immediately increase oversight when errors occur.

The specific advantage of applying this to AI agents is that the trust model can be quantified and automated. Unlike human apprentices, agent behavior is deterministic enough that "5 clean sessions" is a meaningful signal. The trust tracking in MEMORY.md creates an auditable record of how oversight evolved, which is valuable for both retrospectives and compliance.

Teams that implement progressive trust report sustained review quality over time. Without it, review quality degrades as the novelty of AI-assisted development wears off. With it, the review depth adjusts to the actual risk level, keeping the human engaged where engagement matters.

## Related Patterns

- [Output Contracts](output-contracts.md) — contracts define what the review checks at each trust level
- [Dual-Model Validation](dual-model-validation.md) — can be relaxed at higher trust levels for non-critical code
- [Blast Radius Control](blast-radius-control.md) — higher trust levels can allow larger blast radii
- [Human-in-the-Loop](human-in-the-loop.md) — progressive trust determines which human checkpoints are active
- [Quality Control Patterns](../docs/quality-control-patterns.md) — progressive trust is Layer 4 of the quality control stack
