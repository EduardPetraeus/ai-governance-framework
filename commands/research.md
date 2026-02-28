# /research

Find the latest best practices, patterns, and guidance for a specific AI governance topic. This command activates the [research agent](../agents/research-agent.md) with a focused topic and returns structured findings with actionable recommendations.

## Usage

```
/research [topic]
```

The topic can be a phrase, a question, or a specific area of interest. Be specific -- the more precise the topic, the more relevant the findings.

**Examples:**
- `/research "pre-commit hooks for AI-generated code"`
- `/research "output contracts for LLM agents"`
- `/research "blast radius control in multi-agent systems"`
- `/research "how to version CLAUDE.md across a team"`
- `/research "cost tracking patterns for Claude Code sessions"`

## Steps

### Step 1: Parse the topic

Extract the research topic from the command arguments. If no topic is provided, ask: "What topic should I research? Provide a phrase or question."

Validate that the topic is specific enough to produce actionable findings. If the topic is too broad (e.g., "AI governance"), ask the user to narrow it: "That topic is very broad. Can you be more specific? For example: 'session protocol patterns for multi-developer teams' or 'security scanning in CI/CD for AI-generated PRs'."

### Step 2: Activate the research agent

Invoke the [research agent](../agents/research-agent.md) with:
- The specific topic
- The current framework version (from CLAUDE.md or `.governance-version`)
- A pointer to the framework's `docs/`, `agents/`, `commands/`, and `patterns/` directories so the research agent can compare findings against existing content

The research agent handles source selection, filtering, analysis, and recommendation generation. See [agents/research-agent.md](../agents/research-agent.md) for the full source list and filtering criteria.

### Step 3: Filter findings for relevance

The research agent applies four filters to every potential finding:

1. **Actionable** -- does it describe something the framework can do, change, or adopt?
2. **Evidence-based** -- is it backed by real experience, measured data, or official documentation?
3. **Framework-mappable** -- does it map to at least one layer of the 7-layer governance stack?
4. **Security-compatible** -- does it avoid relaxing established security constraints?

Findings that fail any filter are excluded from the report.

### Step 4: Compare with current framework guidance

For each finding that passes filtering, the research agent:
- Identifies the framework's current position on the topic (quoting specific files and sections)
- Classifies the relationship: complements, contradicts, extends, or validates existing guidance
- Lists the specific files that would change if the finding were adopted

### Step 5: Present structured findings

Output the findings using the format below. Each finding includes the source, relevance rating, comparison with current guidance, and a specific recommendation.

## Output Format

```
/research: [topic]
================

Finding 1: [title]
Source: [source name or URL] (published [date or "undated"])
Relevant layer: Layer [N] -- [layer name]
Relevance: HIGH / MEDIUM / LOW
Evidence quality: [1-5 stars]
Current guidance: [what the framework currently says, with file reference]
New insight: [what this finding adds, changes, or confirms]
Affected files: [list of files that would change]
Recommended action: [specific action] or "No change needed -- current guidance is sufficient"

---

Finding 2: [title]
Source: [source name or URL] (published [date or "undated"])
Relevant layer: Layer [N] -- [layer name]
Relevance: HIGH / MEDIUM / LOW
Evidence quality: [1-5 stars]
Current guidance: [current framework position]
New insight: [what the finding adds]
Affected files: [files that would change]
Recommended action: [action or "no change needed"]

---

Summary
-------
Findings reviewed: [N]
Actionable findings: [N]
Already covered by framework: [N]
Proposed framework changes: [list of specific changes, or "None -- current guidance is up to date"]
Highest priority finding: [which finding and why]
```

## Rules

- Results are proposals, not automatic changes. Every framework change goes through a PR with human review. The research agent never modifies files directly.
- Never recommend adopting a finding with evidence quality below 2 stars. Low-evidence findings can be noted for future review but not acted on.
- Never recommend changes to security rules based on a single source. Security changes require official provider documentation or multiple independent engineering team reports.
- Always include the current framework guidance alongside each finding. The comparison is what makes findings actionable -- the human needs to see the delta, not just the new information.
- Always list the specific files that would change. "Update the framework" is not a valid recommendation. "Add patterns/chain-of-thought-validation.md, update docs/quality-control-patterns.md section 4" is.
- If no relevant findings are discovered, say so directly: "No actionable findings for this topic. The framework's current guidance in [file] is consistent with current best practices."
- Keep the output focused. Maximum 5 findings per research request. If more are found, present the top 5 by relevance and note: "[N] additional findings available. Run /research with a narrower topic to see more."

---

## Example Output

```
/research: "pre-commit hooks for AI-generated code"
====================================================

Finding 1: Semantic diff validation for AI-generated PRs
Source: Vercel Engineering Blog (published 2026-01-15)
Relevant layer: Layer 3 -- Enforcement
Relevance: HIGH
Evidence quality: 3/5 (single team's documented experience with measured results)
Current guidance: The framework includes pre-commit hooks for secret scanning and
  naming validation (ci-cd/pre-commit/.pre-commit-config.yaml) but does not address
  semantic validation of AI-generated code at the pre-commit stage.
New insight: Vercel added a pre-commit hook that uses a lightweight model to check
  whether the diff semantically matches the commit message. Mismatches (commit says
  "fix pagination" but diff changes authentication logic) are flagged before the
  commit is created. They report a 15% reduction in "accidental scope creep" commits.
Affected files:
  - ci-cd/pre-commit/.pre-commit-config.yaml (add semantic diff hook)
  - patterns/semantic-verification.md (update with pre-commit application)
  - docs/quality-control-patterns.md (reference new hook)
Recommended action: Add as an optional pre-commit hook in the framework. Mark as
  "experimental" until more teams report results.

---

Finding 2: Token-cost-aware commit splitting
Source: Anthropic documentation update (published 2026-02-01)
Relevant layer: Layer 4 -- Observability
Relevance: MEDIUM
Evidence quality: 4/5 (official provider documentation with technical rationale)
Current guidance: The framework tracks cost per session in COST_LOG.md but does not
  address cost at the commit level.
New insight: Large commits from AI sessions consume disproportionate tokens when
  reviewed by AI PR reviewers (the full diff is in context). Splitting AI-generated
  work into smaller, focused commits reduces AI review cost by up to 40% because
  each review has less context to process.
Affected files:
  - docs/architecture.md (add note on commit sizing in Layer 4 section)
  - patterns/blast-radius-control.md (add commit-level blast radius guidance)
Recommended action: Defer. The insight is sound but the framework does not currently
  prescribe commit size. Add a note to blast-radius-control.md when next updated.

---

Summary
-------
Findings reviewed: 7
Actionable findings: 2
Already covered by framework: 3
Proposed framework changes:
  1. Add optional semantic diff pre-commit hook (Finding 1)
  2. Note on commit-level cost optimization in blast-radius-control.md (Finding 2, deferred)
Highest priority finding: Finding 1 (semantic diff validation) -- directly extends
  the framework's existing pre-commit infrastructure with measurable benefit.
```
