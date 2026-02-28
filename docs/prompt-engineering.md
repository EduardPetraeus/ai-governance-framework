# Prompt Engineering as a Governance Discipline

## 1. Why This Matters for Governance

`CLAUDE.md` defines the rules. Prompts are the language.

Every AI-assisted development session involves two layers of instruction: the constitution (what the agent may and may not do, permanently encoded in `CLAUDE.md`) and the prompt (what the agent does right now, in this task). Governance covers the constitution thoroughly. Prompt quality is where governance breaks down in practice.

The session protocol, the ADRs, the never-commit list — all of this is wasted if the developer then writes: "fix the auth bug." The agent will attempt to fix something. It will produce output. It will look correct. And it will not fix the actual bug, or it will fix it in a way that introduces a different one, or it will "fix" code that was working correctly while leaving the real problem intact.

Quality of input determines quality of output, regardless of how well the constitution is written.

Prompt engineering is therefore not a developer preference or a nice-to-have skill. It is a governance discipline with measurable consequences for code quality, rework rate, and security. Teams that treat it as optional will have higher rework rates, more scope creep, and worse outcomes from the same AI tools.

---

## 2. The Skill Gap Is Real

The same model. The same rules. The same codebase. Dramatically different results.

An experienced AI developer and a developer new to AI-assisted workflows can work side by side, using the same Claude Code installation with the same `CLAUDE.md`, and produce wildly different quality output. The difference is not intelligence, seniority, or domain expertise. It is prompt crafting.

A well-crafted prompt produces:
- Output within the defined scope (no unexpected file changes)
- Code that satisfies the stated acceptance criteria
- Explicit handling of constraints (what must not change)
- Self-limiting behavior (the agent knows when to stop)

A poorly crafted prompt produces:
- Output that does something adjacent to what was requested
- Code that works in the happy path but fails edge cases
- Changes to files that were not mentioned and should not have been touched
- Scope creep that seems helpful but violates architectural boundaries

This gap is measurable. Teams that invest in prompt library development and prompt quality review see rework rates 40–60% lower than teams that do not. The investment is one to two weeks of champion time to build a shared library, and ongoing review during sessions.

---

## 3. Anti-Patterns

The following patterns appear consistently in poorly performing AI development sessions. Each has a specific failure mode.

| Anti-Pattern | Example | Problem | Consequence |
|---|---|---|---|
| Vague instruction | "make it better" | Agent guesses the definition of "better" based on training patterns, not your project context | Output optimizes for a generic version of quality, not your specific requirements |
| Multiple unrelated tasks | "fix the bug, add the new feature, and clean up the old code" | Agent context is split; changes to one concern contaminate the others | Mixed concerns in one commit; impossible to isolate and revert individual changes; rework cascade |
| No acceptance criteria | "add validation" | Agent decides what "validation" means | Validation that passes the happy path but misses the specific edge cases the task was motivated by |
| No constraints | "rewrite this function" | Agent treats the entire function as fair game | Signature changes, behavior changes, interface changes the agent was not authorized to make |
| No context | "why does this fail?" with no stack trace | Agent fills in missing context from patterns, not facts | Confident-sounding diagnosis of the wrong problem |
| Assuming shared knowledge | "implement it like we discussed" | The agent has no memory of previous sessions | Agent invents an interpretation of "like we discussed" that may be entirely different from what was actually discussed |
| No scope boundaries | "improve the data pipeline" | Agent interprets scope as broadly or narrowly as its training patterns suggest | Multi-file changes across architectural boundaries; blast radius exceeds intent |
| Accepting the first output | Running one prompt without validation | The first output is often good enough to look correct but wrong in subtle ways | Committed bugs with a thin layer of correct-looking code on top |

---

## 4. Patterns That Work

### Task Decomposition

The most universally effective pattern. Break complex tasks into small, well-defined units. Each unit has exactly one concern.

**Full example with all required fields:**

```
Task: Add Oura heart rate connector.

Scope:
  - Modify: source_connectors/oura/heartrate.py (create if not exists)
  - Modify: sources_config.yaml (add Oura heart rate entry)
  - Do NOT modify: ingestion_engine.py, any existing connector files, any SQL transforms

Constraints:
  - Use existing OuraConnector base class from source_connectors/oura/base.py
  - Follow the exact same pattern as source_connectors/oura/sleep.py
  - Bronze table name: bronze.oura_heart_rate_daily
  - Columns: timestamp (datetime), bpm (integer), source_system (string), _ingested_at (datetime)
  - API endpoint: configured in env var OURA_API_BASE_URL, do not hardcode

Acceptance criteria:
  - Script runs without errors against mock API response
  - Bronze table created with specified schema
  - All columns populated correctly from sample API response (fixture in tests/fixtures/oura_heartrate_sample.json)
  - sources_config.yaml includes the new connector with correct entity name

Do NOT:
  - Write validation tests (next task)
  - Add any new dependencies
  - Modify the ingestion engine's connector discovery logic
```

This prompt produces a deterministic outcome. The agent knows exactly what to touch, what not to touch, what done looks like, and where to stop.

### Constraint Specification

Use explicit permission tiers for constraints. `MUST NOT` is a hard stop. `MUST` is required. `SHOULD` is a preference that can be overridden with justification.

```
Refactor run_merge.py to reduce duplication in error handling.

MUST NOT: Change function signatures (other code depends on these)
MUST NOT: Change the names or locations of SQL files referenced
MUST NOT: Remove or modify existing unit tests
MUST: Keep all existing behavior identical from the caller's perspective
MUST: Add a docstring to any function that does not have one
SHOULD: Extract repeated error handling into a shared helper function
SHOULD: Reduce the file to under 200 lines if possible without violating the above
```

This pattern makes the agent's review of its own output systematic: "Did I change any function signature? No. Did I change SQL file references? No." The constraints function as a checklist.

### Example-Driven

The most reliable pattern for tasks that follow a known pattern. Point directly at the pattern to follow.

```
Create a silver transform for Lifesum food diary data.

Reference file: transforms/silver/oura_daily_sleep.sql
Follow this file exactly:
  - Same MERGE INTO structure
  - Same column naming pattern (source column → silver column)
  - Same metadata columns: _source_system, _ingested_at, _processed_at
  - Same grain: one row per user per day
  - Same deduplication logic in the USING clause

Input table: bronze.lifesum_food_diary
Output table: silver.lifesum_daily_nutrition
Columns to transform: (see data/schemas/lifesum_food_diary_schema.yaml)

Do not introduce any patterns not present in the reference file.
```

The "do not introduce patterns not in the reference" instruction is critical. Without it, agents will helpfully add patterns they have seen in training — window functions, CTEs, additional metadata columns — that break the consistency you are trying to maintain.

### Chain-of-Thought for Architecture Decisions

For decisions with significant long-term consequences, ask the agent to reason before concluding. This produces dramatically better quality analysis.

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
  6. Implementation time

After reasoning through both, make a recommendation with explicit trade-offs.
Do not jump to the recommendation before completing the analysis.
```

The last instruction — "do not jump to the recommendation before completing the analysis" — is essential. Without it, the agent often produces the recommendation first and then constructs reasoning that supports it, rather than reasoning that might challenge it.

---

## 5. The Standard Prompt Template

All teams should use this template as the starting point for all tasks. Fields can be omitted only if they are genuinely not applicable — not because they are inconvenient to fill in.

```markdown
## [Task type]: [Short descriptive title]

**Context:**
[What is the current situation? What files are relevant? What is the broader goal this task serves?
Link to relevant ADRs, architecture docs, or recent CHANGELOG entries if helpful.]

**Goal:**
[Precisely what should be achieved. One to three sentences. Specific and verifiable.]

**Scope:**
[Which files may be created or modified. Which files must NOT be touched. Be explicit.]

**Constraints:**
[Technical limitations. Existing patterns that must be followed. Things that must not change.
Format as MUST NOT / MUST / SHOULD when helpful.]

**Acceptance criteria:**
[How will you verify this is done correctly? List specific, checkable conditions.
At least one criterion should be a test or a verifiable output.]

**Do NOT:**
[Explicit list of things that are out of scope. This is not redundant with Scope —
it lists specific tempting additions the agent should resist.]

**Reference files:**
[If the task follows an existing pattern, name the file(s) to follow.]
```

This template belongs in `.claude/prompts/task-template.md` and should be referenced in `CLAUDE.md` as the required format for all task prompts.

---

## 6. Bad Prompt vs. Good Prompt

Concrete side-by-side comparison for a feature request: adding a new health data source connector.

### Bad Prompt

```
add withings connector to the project
```

**What this produces**: The agent will create *something*. It might look at existing connectors for inspiration, or it might create something entirely different. It will definitely touch files it was not asked to touch. It will probably not follow the project's naming conventions. It may create a table with different columns than the rest of the pipeline expects. The agent will complete quickly and confidently. The output will look complete. The bugs will be subtle.

### Good Prompt

```
## Feature: Add Withings health data connector (bronze layer)

**Context:**
We have a standard connector pattern (see source_connectors/oura/sleep.py).
Withings provides: weight, blood pressure, heart rate. We only need weight for now.
API docs: https://developer.withings.com/api-reference (oauth2, already configured in .env)

**Goal:**
Create a Withings weight connector that fetches data from the Withings API
and loads it into a bronze table following the existing connector pattern.

**Scope:**
  Create: source_connectors/withings/weight.py
  Modify: sources_config.yaml (add withings_weight entry)
  Do NOT modify: ingestion_engine.py, any other connector, any SQL file

**Constraints:**
  MUST: Follow exactly the same structure as source_connectors/oura/sleep.py
  MUST: Use WithingsConnector base class (create base.py following OuraConnector pattern)
  MUST: Store API credentials from env vars WITHINGS_CLIENT_ID, WITHINGS_CLIENT_SECRET
  MUST NOT: Hardcode any API endpoints, credentials, or configuration values
  MUST NOT: Add any new Python dependencies (use existing: requests, python-dotenv)

**Acceptance criteria:**
  - source_connectors/withings/weight.py exists and imports without error
  - sources_config.yaml has withings_weight entity with correct schema definition
  - Running the connector against the mock fixture in tests/fixtures/withings_weight_sample.json
    produces a bronze table with columns: date, weight_kg, source_system, _ingested_at
  - No API call is made when running in test mode (WITHINGS_TEST_MODE=true)

**Do NOT:**
  - Implement heart rate or blood pressure (future task)
  - Write silver transforms (future task)
  - Write integration tests against the live API (separate task)

**Reference file:** source_connectors/oura/sleep.py
```

The good prompt is longer. It takes 5 minutes to write. It produces output that is correct, in-scope, and requires no rework. The bad prompt is faster to write and produces output that requires 2–4 hours of debugging and rework. The math is not complicated.

---

## 7. Shared Prompt Library

Prompts should be versioned and shared, exactly like code. A developer who discovers a prompt structure that consistently produces better output should not keep it to themselves.

### Directory Structure

```
.claude/prompts/
├── task-template.md        ← The standard task template (section 5)
├── new-feature.md          ← Standard prompt for new features
├── bug-fix.md              ← Standard prompt for bug fixes
├── refactor.md             ← Standard prompt for refactoring
├── sql-transform.md        ← Standard prompt for SQL bronze/silver/gold transforms
├── new-connector.md        ← Standard prompt for adding data source connectors
├── security-review.md      ← Standard prompt for security review (Opus)
├── adr.md                  ← Standard prompt for writing ADRs
└── code-review.md          ← Standard prompt for reviewing PRs
```

### Versioning Prompts

Treat prompt changes like code changes:

- Prompts live in git; changes go through PR review
- The champion reviews prompt changes before they are merged
- Breaking changes to prompt templates require a CHANGELOG entry
- When a prompt produces notably better results after modification, document why in a comment at the top of the file

### When to Update a Prompt Template

Update a prompt template when:
- The same type of task has been redone more than twice due to prompt quality issues
- A developer discovers a significantly better structure and demonstrates it on a real task
- The project's architecture or conventions change in a way that makes the existing template incorrect

Do not update prompts continuously. Stability in prompt templates means stability in agent output. Constant churn means every session is a new experiment.

---

## 8. Prompt Linting

The concept: before a prompt is sent to the AI, check that it contains the required structural fields. A prompt that is missing `Acceptance criteria` or `Scope` is less likely to produce correct output.

### Minimum Required Fields

A lintable prompt must contain:
- A task title
- Scope (what can and cannot be changed)
- At least one acceptance criterion
- At least one explicit constraint

### Simple Lint Check

A pre-session hook or champion review can check for these fields in any prompt that will be committed to the prompt library:

```python
# scripts/lint_prompt.py
import sys

REQUIRED_FIELDS = ["Scope", "Acceptance criteria", "Constraints", "Do NOT"]

def lint_prompt(prompt_text: str) -> list[str]:
    missing = []
    for field in REQUIRED_FIELDS:
        if field.lower() not in prompt_text.lower():
            missing.append(field)
    return missing

if __name__ == "__main__":
    prompt = open(sys.argv[1]).read()
    missing = lint_prompt(prompt)
    if missing:
        print(f"PROMPT LINT FAILED: Missing required fields: {', '.join(missing)}")
        sys.exit(1)
    print("PROMPT LINT PASSED")
```

This script is not a replacement for good judgment. A prompt can contain all required fields and still be poorly written. Lint checks are a floor, not a ceiling.

### When Prompt Linting Makes Sense

Enforce prompt linting for:
- Prompts being added to the shared library (all must pass)
- Prompts for high-stakes tasks (security reviews, architectural changes, ADR writing)

Do not enforce prompt linting for:
- Quick lookups and exploratory questions
- Conversational debugging sessions
- Tasks where the developer is still formulating the problem

The goal is not to bureaucratize every AI interaction. It is to ensure that consequential prompts are written carefully.

---

*Related guides: [AI Code Quality](./ai-code-quality.md) | [Metrics Guide](./metrics-guide.md) | [Enterprise Playbook](./enterprise-playbook.md)*
