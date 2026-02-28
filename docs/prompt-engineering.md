# Prompt Engineering as a Governance Discipline

## 1. Why This Is Governance

`CLAUDE.md` sets the rules. Prompt engineering is the language you speak with the agent.

Every AI-assisted session involves two layers of instruction: the constitution (what the agent may and may not do, permanently encoded in `CLAUDE.md`) and the prompt (what the agent does right now, for this specific task). Governance covers the constitution thoroughly. Prompt quality is where governance breaks down in practice.

Consider: the session protocol is followed. The ADRs are written. The never-commit list is in place. The developer then writes: "fix the auth bug."

The agent will attempt to fix something. It will produce output. The code will compile. It will look correct at a glance. And it will not fix the actual bug — or it will fix it in a way that introduces a different one, or it will "fix" code that was working correctly while leaving the real problem untouched, or it will modify files outside the intended scope because "fix the auth bug" does not specify what should and should not change.

**The same rules + a poor prompt = poor output.** Quality of input determines quality of output, regardless of how well the constitution is written.

Prompt engineering is therefore not a developer preference or a nice-to-have skill. It is a governance discipline with measurable consequences for code quality, rework rate, session efficiency, and security. Teams that treat it as optional will have higher rework rates (40-60% higher, based on comparative session data), more scope creep, and worse outcomes from the same AI tools and the same constitution.

The implication for organizations: prompt engineering is a team skill, not an individual one. It should be standardized, reviewed, and improved — exactly like code.

---

## 2. The Skill Gap

The same model. The same rules. The same codebase. Dramatically different results.

An experienced AI developer and a developer new to AI-assisted workflows can work side by side, using the same Claude Code installation with the same `CLAUDE.md`, and produce wildly different quality output. The difference is not intelligence, seniority, or domain expertise. It is prompt crafting.

**Observable evidence of the skill gap:**

A well-crafted prompt produces:
- Output that stays within the defined scope — no unexpected file changes, no architectural surprises
- Code that satisfies the stated acceptance criteria on the first attempt
- Explicit handling of constraints — the agent demonstrably avoided things it was told not to do
- Self-limiting behavior — the agent knew when to stop and reported what it did not do

A poorly crafted prompt produces:
- Output that does something adjacent to what was requested — close enough to look correct, different enough to need rework
- Code that works for the happy path but fails edge cases that a constrained prompt would have surfaced
- Changes to files that were not mentioned and should not have been touched
- Scope creep that seems helpful ("I also noticed that X could be improved, so I...") but violates architectural boundaries

**This gap is measurable.** Teams that invest in prompt library development, prompt quality review, and prompt training see rework rates 40-60% lower than teams that do not. The investment is one to two weeks of champion time to build a shared library, ongoing review during retrospectives, and prompt quality scoring as a Tier 2 metric.

The skill gap also compounds over time. A developer with good prompt discipline produces consistently predictable sessions. A developer with poor prompt discipline produces sessions with high variance — some excellent, some requiring hours of rework — which makes sprint planning unreliable and team velocity unpredictable.

---

## 3. Anti-Patterns

The following patterns appear consistently in poorly performing AI development sessions. Each has a specific failure mode and a specific fix.

| Anti-Pattern | Example Prompt | What Goes Wrong | Better Version |
|---|---|---|---|
| Vague instruction | "make it better" | Agent guesses the definition of "better" from training patterns, not your project context. Produces generic optimization. | "Reduce the cyclomatic complexity of `run_merge.py` by extracting the error handling into a shared helper. MUST NOT change function signatures." |
| Multiple unrelated tasks | "fix the bug, add the new feature, and clean up the old code" | Agent context is split across three concerns. Changes contaminate each other. Impossible to revert one without reverting all. | Three separate prompts, each with its own scope, constraints, and acceptance criteria. One commit per task. |
| No acceptance criteria | "add validation" | Agent decides what "validation" means. Validates the wrong things, or validates correctly but misses the specific edge case that motivated the task. | "Add input validation to `process_record()`. MUST reject: null user_id, dates before 2020-01-01, heart_rate outside 30-250 bpm. Return specific error messages for each case." |
| No constraints | "rewrite this function" | Agent treats the entire function as fair game. Changes the signature, modifies the return type, renames parameters — breaking callers. | "Refactor `calculate_metrics()` to reduce duplication. MUST NOT change the function signature or return type. MUST preserve all existing unit tests." |
| No context | "why does this fail?" (no stack trace, no file reference) | Agent fills missing context from training patterns, not from your actual codebase. Produces a confident diagnosis of the wrong problem. | "The function `load_data()` in `connectors/oura.py` raises `KeyError: 'heart_rate'` when processing the attached API response. Stack trace: [paste]. What is wrong?" |
| Assuming shared knowledge | "implement it like we discussed" | Agent has no memory of previous sessions. Invents an interpretation of "like we discussed" that may be entirely wrong. | "Implement incremental loading using watermark-based approach (see ADR-003). Track `last_loaded_at` per source in `metadata.load_tracking`." |
| No scope boundaries | "improve the data pipeline" | Agent interprets scope as broadly as its training patterns suggest. Multi-file changes across architectural boundaries. Blast radius exceeds intent. | "Improve error handling in the bronze ingestion step only. Scope: `ingestion/bronze_loader.py`. Do NOT modify silver or gold transforms." |
| Accepting first output | Running one prompt, accepting without verification | First output often passes the glance test but fails at edges. Committed bugs under a thin layer of correct-looking code. | Run the prompt. Review output against acceptance criteria. If criteria are not fully met, provide specific feedback and iterate. |

---

## 4. Patterns That Work

### Task Decomposition

The most universally effective pattern. Break complex tasks into small, well-defined units with exactly one concern each.

**Full example with all required fields:**

```
Task: Add Oura heart rate connector.

Context:
  We have a standard connector pattern (see source_connectors/oura/sleep.py).
  The Oura API returns heart rate data as daily summaries.
  This is the third Oura connector — sleep and activity already exist.

Scope:
  Create: source_connectors/oura/heartrate.py
  Modify: sources_config.yaml (add oura_heart_rate entry)
  Do NOT modify: ingestion_engine.py, any existing connector file, any SQL transform

Constraints:
  MUST: Use existing OuraConnector base class from source_connectors/oura/base.py
  MUST: Follow the exact same pattern as source_connectors/oura/sleep.py
  MUST: Use environment variable OURA_API_BASE_URL for API endpoint — no hardcoded URLs
  MUST NOT: Add any new Python dependencies
  MUST NOT: Modify the ingestion engine's connector discovery logic

Acceptance criteria:
  - source_connectors/oura/heartrate.py exists and imports without error
  - Bronze table name: bronze.oura_heart_rate_daily
  - Columns: timestamp (datetime), bpm (integer), source_system (string), _ingested_at (datetime)
  - Script runs without errors against mock fixture in tests/fixtures/oura_heartrate_sample.json
  - sources_config.yaml includes the new connector with correct entity name and schema

Do NOT:
  - Write validation tests (next task)
  - Write silver transforms (next sprint)
  - Add any new dependencies
  - Modify the ingestion engine's connector discovery logic
  - Add data quality checks (separate task)

Reference file: source_connectors/oura/sleep.py — follow this exactly
```

This prompt produces a deterministic outcome. The agent knows exactly what to create, what to modify, what not to touch, what "done" looks like, and where to stop. The output is verifiable against specific criteria, not against the developer's subjective impression.

### Constraint Specification

Use explicit permission tiers. `MUST NOT` is a hard stop — the agent treats this as a prohibition. `MUST` is required — the agent treats this as an obligation. `SHOULD` is a preference — the agent may override it with justification.

```
Refactor run_merge.py to reduce duplication in error handling.

MUST NOT: Change any function signature (other code depends on these)
MUST NOT: Change the names or locations of SQL files referenced in the module
MUST NOT: Remove or modify any existing unit test
MUST NOT: Add new dependencies

MUST: Keep all existing behavior identical from the caller's perspective
MUST: Add a docstring to any function that does not currently have one
MUST: Run all existing tests after refactoring — they must pass unchanged

SHOULD: Extract repeated error handling into a shared helper function
SHOULD: Reduce the file to under 200 lines if possible without violating the MUST NOTs
SHOULD: Improve variable names where they are ambiguous
```

This pattern makes the agent's self-review systematic: "Did I change any function signature? No. Did I change SQL file references? No. Did any test fail? No." The constraints function as a checklist that the agent can verify against its own output.

### Example-Driven

The most reliable pattern for tasks that follow a known pattern. Point directly at the reference and say "follow this exactly."

```
Create a silver transform for Lifesum food diary data.

Reference file: transforms/silver/oura_daily_sleep.sql
Follow this file EXACTLY:
  - Same MERGE INTO structure
  - Same column naming pattern (source_column -> silver_column)
  - Same metadata columns: _source_system, _ingested_at, _processed_at
  - Same grain: one row per user per day
  - Same deduplication logic in the USING clause
  - Same WHERE clause structure for incremental loading

Input table: bronze.lifesum_food_diary
Output table: silver.lifesum_daily_nutrition
Columns to transform: see data/schemas/lifesum_food_diary_schema.yaml

Do NOT introduce any patterns not present in the reference file.
Do NOT add CTEs, window functions, or additional metadata columns
that are not in the reference. Consistency is more important than cleverness.
```

The instruction "do not introduce patterns not in the reference" is critical. Without it, agents will helpfully add patterns they have seen in training — window functions, additional metadata columns, alternative deduplication strategies — that may be individually reasonable but break the consistency you are trying to maintain.

### Chain-of-Thought for Architecture Decisions

For decisions with significant long-term consequences, ask the agent to reason explicitly before concluding. This produces dramatically better analysis than asking for a direct recommendation.

```
I am deciding how to implement incremental loading for the bronze layer.
Evaluate these two approaches:

Approach A: Watermark-based incremental
  - Track last_loaded_at per source in a metadata table
  - Fetch records where updated_at > last_loaded_at
  - Append to bronze

Approach B: Full refresh daily
  - Drop and reload entire bronze table each run
  - No watermark complexity

For each approach, reason through:
  1. Performance at current data scale (< 100k records/source/day)
  2. Performance at 10x scale
  3. API rate limit implications (Oura allows 100 calls/day)
  4. Complexity for future developers to maintain
  5. Risk of data gaps or duplicates
  6. Implementation time estimate

After reasoning through BOTH approaches completely, make a recommendation
with explicit trade-offs stated. Do not jump to the recommendation before
completing the analysis of both approaches.
```

The last instruction is essential. Without it, the agent often produces the recommendation first, then constructs reasoning that supports it — reasoning biased toward the conclusion, not reasoning that might challenge it. Requiring the analysis before the conclusion produces more honest evaluation.

---

## 5. The Standard Prompt Template

All teams should use this template as the starting point for all tasks. Fields can be omitted only if they are genuinely not applicable — not because they are inconvenient to fill in.

```markdown
## [Task type]: [Short descriptive title]

**Context:**
[What is the current situation? What files are relevant? What is the broader goal
this task serves? Link to relevant ADRs, architecture docs, or recent CHANGELOG
entries if they provide important context.]

**Goal:**
[Precisely what should be achieved. One to three sentences. Specific and verifiable.
Not "improve" or "fix" without specifying what improvement or fix means.]

**Scope:**
[Which files may be created or modified — list them explicitly.
Which files MUST NOT be touched — list them explicitly.
If in doubt, list more files in the "must not touch" category.]

**Constraints:**
[Technical limitations. Existing patterns that must be followed. Dependencies that
must not change. Use MUST NOT / MUST / SHOULD hierarchy when helpful.]

**Acceptance criteria:**
[How will you verify this is done correctly? List specific, checkable conditions.
At least one criterion should be a test or a verifiable runtime output.
"It works" is not an acceptance criterion. "It processes the test fixture
without errors and produces a table with 15 rows" is.]

**Do NOT:**
[Explicit list of things that are out of scope. This is not redundant with Scope —
it lists specific tempting additions the agent should resist. Common entries:
"Do not write tests (next task)", "Do not refactor adjacent code",
"Do not add features not specified above".]

**Reference files:**
[If the task follows an existing pattern, name the file(s) to follow.
The agent should match the reference exactly unless constraints specify otherwise.]
```

This template belongs in `.claude/prompts/task-template.md` and should be referenced in `CLAUDE.md` as the required structure for all task prompts.

---

## 6. Bad Prompt vs. Good Prompt

Side-by-side comparison for a realistic task: adding a new health data source connector.

### Bad Prompt

```
add withings connector to the project
```

**What this produces:** The agent will create *something*. It might examine existing connectors for inspiration, or it might create something structurally different. It will probably touch files outside the intended scope — perhaps modifying the ingestion engine to accommodate the new connector, or adding configuration entries with different field names than existing connectors use. It may create a table with columns that do not match the rest of the pipeline's expectations. It might add a dependency you do not want. It will complete quickly and confidently. The output will look professional. The bugs will be subtle — wrong column types, missing error handling for API rate limits, hardcoded endpoint URLs.

**Cost of the bad prompt:** 5 seconds to write. 2-4 hours to debug and rework.

### Good Prompt

```
## Feature: Add Withings weight connector (bronze layer)

**Context:**
We have a standard connector pattern (see source_connectors/oura/sleep.py).
Withings API provides weight, blood pressure, and heart rate data.
We only need weight for this task — blood pressure and heart rate are future tasks.
API docs: https://developer.withings.com/api-reference
Authentication: OAuth2, already configured in .env as WITHINGS_CLIENT_ID and WITHINGS_CLIENT_SECRET.

**Goal:**
Create a Withings weight connector that fetches daily weight measurements from the
Withings API and loads them into a bronze table following our existing connector pattern.

**Scope:**
  Create: source_connectors/withings/weight.py
  Create: source_connectors/withings/base.py (following oura/base.py pattern)
  Modify: sources_config.yaml (add withings_weight entry)
  Do NOT modify: ingestion_engine.py, any other connector, any SQL file, requirements.txt

**Constraints:**
  MUST: Follow exactly the same class structure as source_connectors/oura/sleep.py
  MUST: Create WithingsConnector base class following OuraConnector pattern
  MUST: Read credentials from env vars: WITHINGS_CLIENT_ID, WITHINGS_CLIENT_SECRET
  MUST: Use existing dependencies only (requests, python-dotenv)
  MUST NOT: Hardcode any API endpoints, credentials, or configuration values
  MUST NOT: Add any new Python dependencies

**Acceptance criteria:**
  - source_connectors/withings/weight.py exists and imports without error
  - source_connectors/withings/base.py exists with WithingsConnector class
  - sources_config.yaml has withings_weight entity with schema definition
  - Running connector against tests/fixtures/withings_weight_sample.json produces
    bronze table with columns: date (date), weight_kg (float), source_system (string),
    _ingested_at (datetime)
  - No API call is made when WITHINGS_TEST_MODE=true in environment

**Do NOT:**
  - Implement blood pressure or heart rate connectors (future tasks)
  - Write silver or gold transforms
  - Write integration tests against the live API (separate task)
  - Add data quality validation (separate task)
  - Modify the ingestion engine's connector discovery mechanism

**Reference file:** source_connectors/oura/sleep.py — follow this exactly
```

**Cost of the good prompt:** 5 minutes to write. Output is correct, in-scope, and requires no rework.

**The math:** The good prompt takes 60x longer to write than the bad prompt. It saves 120-480x more time in debugging and rework. The return on prompt quality investment is not subtle.

---

## 7. Shared Prompt Library

Prompts should be versioned and shared, exactly like code. A developer who discovers a prompt structure that consistently produces better output should not keep it to themselves — just as a developer who discovers a better design pattern shares it with the team.

### Directory Structure

```
.claude/prompts/
├── task-template.md        <- The standard task template (section 5)
├── new-feature.md          <- Standard prompt for new features
├── bug-fix.md              <- Standard prompt for bug fixes with debugging context
├── refactor.md             <- Standard prompt for refactoring with constraint specification
├── sql-transform.md        <- Standard prompt for SQL bronze/silver/gold transforms
├── new-connector.md        <- Standard prompt for adding data source connectors
├── security-review.md      <- Standard prompt for security review (Opus)
├── adr.md                  <- Standard prompt for writing Architecture Decision Records
├── code-review.md          <- Standard prompt for reviewing PRs
└── test-suite.md           <- Standard prompt for writing test suites
```

### Versioning and Change Control

Treat prompt changes like code changes:

- **Prompts live in git.** Changes go through PR review. The champion reviews prompt changes before they are merged.
- **Breaking changes require a CHANGELOG entry.** If a prompt template changes in a way that produces different output for the same input, this is a breaking change and should be documented.
- **Document what works and why.** When a prompt modification produces notably better results, add a comment at the top of the file explaining the change and why it improved output quality.
- **Stability over novelty.** Do not update prompts continuously. Stable prompt templates produce predictable output. Constant churn means every session is a new experiment with unknown results.

### When to Update a Prompt Template

Update when:
- The same task type has been redone more than twice due to prompt quality issues
- A developer discovers a significantly better structure and demonstrates it on a real task (not hypothetically)
- The project's architecture or conventions change in a way that makes the existing template produce incorrect output
- A new constraint needs to be universal (e.g., "all connectors must now include retry logic")

Do not update when:
- One developer prefers different wording (preference is not a reason for change)
- A minor formatting variation would look better (consistency matters more than aesthetics)
- The prompt "could be better" without evidence of a specific failure it would prevent

---

## 8. Prompt Linting

The concept: before a prompt is stored in the shared library or used for a high-stakes task, verify that it contains the structural fields that correlate with high-quality output. A prompt missing `Scope` or `Acceptance criteria` is statistically more likely to produce output that requires rework.

### Minimum Required Fields

A prompt that will be stored in the shared library must contain:
- A task title (what type of task and a short description)
- Scope (what can and cannot be changed)
- At least one acceptance criterion (how to verify the output is correct)
- At least one explicit constraint (what must not change)

### Simple Lint Script

```python
#!/usr/bin/env python3
"""
Lint a prompt file for required structural fields.
Usage: python scripts/lint_prompt.py .claude/prompts/new-feature.md
"""
import sys
from pathlib import Path

REQUIRED_FIELDS = {
    "scope": ["Scope:", "Scope (", "**Scope:**", "**Scope**"],
    "acceptance_criteria": ["Acceptance criteria:", "**Acceptance criteria:**", "Acceptance criteria ("],
    "constraints": ["Constraints:", "**Constraints:**", "MUST NOT", "MUST:"],
    "do_not": ["Do NOT:", "**Do NOT:**", "Do not:", "Out of scope:"],
}

RECOMMENDED_FIELDS = {
    "context": ["Context:", "**Context:**"],
    "reference": ["Reference file:", "**Reference", "Reference:"],
}

def check_field(content: str, markers: list[str]) -> bool:
    content_lower = content.lower()
    return any(marker.lower() in content_lower for marker in markers)

def lint_prompt(filepath: str) -> tuple[list[str], list[str]]:
    content = Path(filepath).read_text()
    missing_required = []
    missing_recommended = []

    for field, markers in REQUIRED_FIELDS.items():
        if not check_field(content, markers):
            missing_required.append(field)

    for field, markers in RECOMMENDED_FIELDS.items():
        if not check_field(content, markers):
            missing_recommended.append(field)

    return missing_required, missing_recommended

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lint_prompt.py <prompt_file>")
        sys.exit(1)

    missing_req, missing_rec = lint_prompt(sys.argv[1])

    if missing_req:
        print(f"FAIL: Missing required fields: {', '.join(missing_req)}")
        sys.exit(1)

    if missing_rec:
        print(f"WARN: Missing recommended fields: {', '.join(missing_rec)}")

    if not missing_req and not missing_rec:
        print("PASS: All fields present")

    sys.exit(0)
```

### When to Enforce Prompt Linting

**Always enforce for:**
- Prompts being added to the shared library (all must pass lint)
- Prompts for high-stakes tasks: security reviews, architectural changes, ADR writing, anything touching authentication or authorization

**Do not enforce for:**
- Quick lookups and exploratory questions ("what does this function do?")
- Conversational debugging sessions ("I see this error, what might cause it?")
- Tasks where the developer is still formulating the problem (early exploration)

The goal is not to bureaucratize every AI interaction. It is to ensure that consequential prompts — the ones that produce code that will be committed, reviewed, and maintained — are written with the structural discipline that produces correct output.

### Integrating Linting into CI

For teams ready to enforce prompt quality in the shared library:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: lint-prompts
        name: Lint prompt templates
        entry: python scripts/lint_prompt.py
        language: python
        files: \.claude/prompts/.*\.md$
        pass_filenames: true
```

This ensures every prompt added to the shared library passes the structural check before it can be merged.

---

*Related guides: [AI Code Quality](./ai-code-quality.md) | [Metrics Guide](./metrics-guide.md) | [Enterprise Playbook](./enterprise-playbook.md) | [Model Routing](./model-routing.md)*
