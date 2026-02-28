# Quality Control Patterns

## The Core Problem

AI agents are confident about everything. They never say "I'm not sure about this." A wrong answer and a right answer look identical in tone, formatting, and structure. The burden of verification is 100% on the human.

Most humans fail this verification because they pattern-match rather than verify. "Looks right" becomes the quality bar instead of "IS right." A function that handles 9 out of 10 edge cases looks identical to one that handles all 10. A connector that works for happy-path requests looks identical to one that handles rate limits, timeouts, and malformed responses.

The patterns in this document address a single question: **How do you know that what the agent produced is correct?**

Each pattern targets a different failure mode. Used together, they form a quality control stack that catches errors at every level — from the agent's own output to production behavior.

---

## Pattern 1: Dual-Model Validation

One model writes. A different model reviews. Not the same model reviewing its own work — that catches almost nothing because the reviewer shares the writer's blind spots.

```
Task → Sonnet writes code → Opus reviews code → Issues found? → Fix → Merge
                                                → No issues?   → Merge
```

**Why it works:** Different models have different failure modes. Sonnet might miss an edge case in retry logic; Opus catches it because it reasons about the problem from a different angle. The asymmetry in capability means the reviewer catches classes of errors the writer systematically misses.

**Implementation:** Build into CI/CD. Branches created during a Sonnet session get an automatic Opus review pass before merge. The review focuses on logic correctness, edge cases, security implications, and architectural fit — not syntax or formatting (linters handle that).

**When to skip it:** Internal documentation, changelog updates, and other low-risk changes where the cost of dual-model review exceeds the risk of an error.

See the full pattern: [Dual-Model Validation](../patterns/dual-model-validation.md)

---

## Pattern 2: Output Contracts

Define the expected output BEFORE the agent works. The contract is the acceptance criteria. Review verifies the contract, not the output in isolation.

```yaml
output_contract:
  name: "oura-sleep-connector"
  task: "Create Oura ring sleep data connector"

  files_created:
    - source_connectors/oura/sleep.py
    - tests/test_oura_sleep.py
  files_modified:
    - sources_config.yaml (new entries only, no existing entries changed)
  files_not_touched:
    - source_connectors/fitbit/    # unrelated connectors
    - CLAUDE.md                    # governance file

  must_include:
    - error handling for API rate limits
    - incremental fetch (not full history every time)
    - retry logic with exponential backoff
    - structured logging (no print statements)
    - type hints on all public functions
  must_not_include:
    - hardcoded API keys
    - print statements (use logging module)
    - any file outside source_connectors/ and tests/
    - wildcard imports

  automated_checks:
    tests_pass: true
    security_scan: clean
    lint: clean
    coverage_threshold: 80
```

After the agent completes: validate output against the contract. Automated checks run first. Human review focuses on the gap between contract and output, not on reading every line.

**Why it works:** Without a contract, "success" is whatever the agent produces. With a contract, success is measurable. The contract also constrains the agent's scope — it cannot justify touching files outside the contract.

See the full pattern: [Output Contracts](../patterns/output-contracts.md)

---

## Pattern 3: Progressive Trust

Start with maximum oversight. Reduce as confidence builds. Track trust level per domain. If a session produces a bug, reduce trust level immediately.

```
Session 1-5:    Review every file, every line.
Session 5-15:   Review logic and architecture. Trust syntax and formatting.
Session 15-30:  Review architecture decisions. Trust implementation details.
Session 30+:    Review at task level. Trust agent within established patterns.
```

Trust is not binary and it is not global. An agent can be trusted with code generation (Level 4) but not with architecture decisions (Level 2). Track each dimension independently in MEMORY.md:

```yaml
trust_levels:
  code_generation: 3
  architecture: 2
  security: 3
  documentation: 4
  testing: 2
```

**The critical rule:** Trust is earned through evidence and lost immediately through failure. One bad session in a domain resets that domain's trust level. Recovery requires the same progression: maximum oversight, gradually reduced.

See the full pattern: [Progressive Trust](../patterns/progressive-trust.md)

---

## Pattern 4: Semantic Verification

Automated tests verify that code runs. They do not verify that it does the right thing. An agent can write code that passes all tests but implements the wrong business logic — especially if the agent also wrote the tests.

Semantic verification checks meaning, not mechanics. Four techniques:

**Assertion-based:** Define assertions about system state before coding begins. "After processing a day of sleep data, the table has exactly one row per user per day, with all timestamps in UTC."

**Example-based:** Provide 3-5 concrete input/output pairs. The agent must produce code that handles all of them. Choose examples that exercise edge cases, not just happy paths.

**Invariant-based:** Define what must always be true, regardless of input. "No duplicate records. All timestamps in UTC. All durations positive. No NULL in required fields." Run invariant checks after every batch of agent work.

**Negative testing:** Define what must never happen. "Never delete existing records. Never modify config outside the designated section. Never reduce test coverage below the current baseline." Encode these as assertions.

See the full pattern: [Semantic Verification](../patterns/semantic-verification.md)

---

## Pattern 5: Blast Radius Control

An AI session that goes wrong can change hundreds of files. At 15x human velocity, a runaway agent produces damage 15x faster. The solution: explicit limits on what a single session can change.

**Default limits** (configurable in CLAUDE.md):

| Limit | Default | Rationale |
|-------|---------|-----------|
| Maximum files modified per session | 15 | Beyond this, review quality drops sharply |
| Maximum lines changed per file | 200 | Large changes to a single file signal refactoring that needs architectural review |
| Maximum new files created | 10 | Many new files signal feature scope that should be split |
| Critical files requiring explicit permission | CLAUDE.md, CI configs, main branch protections | These files govern the governance — changes cascade |
| Architecture changes + implementation in same session | Forbidden | Decide first, implement second |

**Scope review at session start:**
```
Session scope check:
  Planned files: [list]
  Estimated changes: [count] files, ~[N] lines
  Blast radius: LOW / MEDIUM / HIGH

  HIGH blast radius triggers:
    - More than 10 files
    - Cross-layer changes
    - Schema or data model changes
    - CI/CD modifications

  HIGH requires: explicit human confirmation before proceeding
```

See the full pattern: [Blast Radius Control](../patterns/blast-radius-control.md)

---

## Pattern 6: Confidence Scoring

The agent rates its own confidence on each output. This is not a guarantee of correctness — it is a triage signal. Low confidence routes work to stronger review; high confidence allows lighter review.

```
Task: Create Oura sleep connector
Confidence: 85%
Reason: Standard API integration pattern. Familiar with Oura API structure.
Low confidence areas: Rate limit handling (API docs unclear on exact limits)
Recommended review focus: rate limit section, backoff calculation
```

**Thresholds:**

| Confidence | Action |
|------------|--------|
| 90-100% | Standard review process |
| 70-89% | Review with extra attention to flagged areas |
| 50-69% | Mandatory detailed human review |
| Below 50% | Consider switching to a stronger model or breaking the task down |

**Why self-reported confidence works:** It does not work as an accuracy measure. It works as a routing signal. An agent that says "I'm 50% confident about the retry logic" is telling you where to look. That is valuable even if the 50% number is imprecise.

Confidence scoring integrates with [Progressive Trust](../patterns/progressive-trust.md) — agents at higher trust levels can have higher confidence thresholds before mandatory review triggers.

---

## Pattern 7: Regression Detection

After every change, verify that existing functionality still works. This is the simplest pattern and the most frequently skipped.

**Regression detection checklist:**
1. Run the existing test suite (not just new tests)
2. Compare output before and after for key operations
3. Check that no existing files were unexpectedly modified (`git diff --stat`)
4. Verify governance files are still valid (CLAUDE.md parses correctly, cross-references resolve)
5. Confirm that test coverage did not decrease
6. Run security scan to ensure no new vulnerabilities were introduced

**Automation:** Every item on this checklist can and should be automated in CI/CD. The agent should run `git diff --stat` at the end of every session and flag any files modified that were not in the session scope.

See related: [CI/CD workflows](../ci-cd/) for automated regression detection in pull requests.

---

## The Quality Control Stack

These patterns layer into a defense-in-depth stack. Each layer catches what the layers below miss.

```
Layer 5: Production monitoring    ── Did it actually work in production?
Layer 4: Human verification       ── Progressive trust: human reviews what matters
Layer 3: AI cross-validation      ── Dual-model review: different model reviews output
Layer 2: Automated validation     ── Tests, linters, security scan via CI/CD
Layer 1: Agent self-check         ── Confidence score, output contract, built into CLAUDE.md
```

**Layer 1 — Agent self-check.** The agent validates its own output against the output contract and reports a confidence score. This is the cheapest check and catches the most obvious errors: missing files, forgotten requirements, low-confidence areas. Built into CLAUDE.md instructions.

**Layer 2 — Automated validation.** CI/CD runs tests, linters, and security scans. This catches syntax errors, style violations, known vulnerability patterns, and test failures. Zero human effort after initial setup. See [ci-cd/](../ci-cd/) for workflow definitions.

**Layer 3 — AI cross-validation.** A different model reviews the output. This catches logic errors, edge cases, and architectural misalignment that automated tools miss. See [Dual-Model Validation](../patterns/dual-model-validation.md).

**Layer 4 — Human verification.** The human reviews what matters, guided by [Progressive Trust](../patterns/progressive-trust.md). Early sessions: review everything. Mature sessions: review architecture and security. The human focuses on judgment calls that no automated system can make.

**Layer 5 — Production monitoring.** Runtime checks verify that the change works in production. Monitoring alerts, error rate tracking, and performance regression detection catch issues that no pre-production check can find.

**The stack is not optional.** Skipping layers creates blind spots. Layer 1 without Layer 3 means the agent reviews its own work. Layer 3 without Layer 2 means logic is reviewed but syntax is not checked. Layer 4 without Layer 1 means the human has no contract to review against.

---

## Integrating with the 7-Layer Governance Stack

Quality control patterns map directly to the [governance architecture](architecture.md):

| Quality Control Layer | Governance Layer | Implementation |
|----------------------|-----------------|----------------|
| Agent self-check | Layer 1 (Constitution) | CLAUDE.md instructions, output contracts |
| Automated validation | Layer 3 (Enforcement) | CI/CD workflows, pre-commit hooks |
| AI cross-validation | Layer 3 (Enforcement) | Dual-model review in PR workflow |
| Human verification | Layer 2 (Orchestration) | Session protocol, progressive trust |
| Production monitoring | Layer 4 (Observability) | Metrics, alerts, decision logs |

The quality control patterns are not a separate system. They are the enforcement mechanism for the governance framework. Every governance rule that is not enforced by at least one quality control layer is a suggestion, not a rule.

---

## Further Reading

- [Dual-Model Validation](../patterns/dual-model-validation.md) — full pattern specification
- [Output Contracts](../patterns/output-contracts.md) — full pattern specification
- [Progressive Trust](../patterns/progressive-trust.md) — full pattern specification
- [Semantic Verification](../patterns/semantic-verification.md) — full pattern specification
- [Blast Radius Control](../patterns/blast-radius-control.md) — full pattern specification
- [Context Boundaries](../patterns/context-boundaries.md) — limiting agent scope to reduce errors
- [Human-in-the-Loop](../patterns/human-in-the-loop.md) — making human oversight effective
- [Architecture](architecture.md) — the 7-layer governance stack
- [Session Protocol](session-protocol.md) — how sessions implement quality control
- [AI Code Quality](ai-code-quality.md) — code-specific quality patterns
