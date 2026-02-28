# Contributing to AI Governance Framework

Contributions that improve the practical usefulness of this framework are welcome. Every file in this repository is meant to be used in production by real engineering teams. Contributions are held to that standard.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be direct, be constructive, assume good intent.

## Development Setup

No build tools required. The framework is Markdown files, YAML workflows, and Python scripts.

```bash
git clone https://github.com/clauseduardpetraeus/ai-governance-framework.git
cd ai-governance-framework
```

**Requirements:** Git, a text editor, and Python 3.10+ (for scripts only — not needed for template or docs contributions).

## Reporting Issues

### Bugs

Open a GitHub issue with:

- **Which file or template** is affected
- **What it currently says** (or does)
- **What it should say** (or do)
- **Context:** solo dev, small team, or enterprise — the correct fix may differ by scale

### Feature Requests

Open an issue with the `enhancement` label. Include:

- The problem you are trying to solve
- Which layer of the framework it belongs to (Layer 1-7)
- Whether you have a concrete implementation or just the problem statement

### Documentation Gaps

Open an issue with the `docs` label. If a cross-reference is broken, a code example does not work, or a concept is explained ambiguously — that is a bug, not a nice-to-have.

### Questions

Use GitHub Discussions, not issues.

## Pull Request Process

### Before You Start

Open an issue before submitting a PR for significant changes (new agents, new layers, structural reorganizations). This avoids wasted effort when a suggestion conflicts with the framework's design principles.

Small improvements — fixing wording, correcting cross-references, improving examples — can go straight to a PR.

### Branch Naming

```
feature/short-description     # New capability
fix/short-description         # Correction to existing content
docs/short-description        # Documentation improvement
agent/agent-name              # New agent definition
command/command-name           # New slash command
example/example-name           # New worked example
```

### PR Title Format

```
[Layer N] Short description of the change
```

Examples:

```
[Layer 1] Add CLAUDE.md template for data engineering projects
[Layer 3] Add GitLab CI equivalent for AI PR review
[Layer 5] Add ADR template for API versioning decisions
[Docs] Fix broken cross-references in session-protocol.md
```

### PR Description

Every PR description must include:

1. **What this changes** — one paragraph, concrete
2. **Why** — what problem does this solve, or what improvement does it make
3. **Which layer** — Layer 1-7, or cross-cutting
4. **How to verify** — what should a reviewer check to confirm the change is correct

### Review Checklist

Every PR is evaluated against these criteria:

| Criterion | Requirement |
|-----------|-------------|
| **No placeholders** | Every field contains real, usable content. `[YOUR VALUE HERE]` is never acceptable. Write a realistic default or a concrete example. |
| **Cross-references resolve** | Every relative link points to a file that exists. Run a check before submitting. |
| **Layer alignment** | The contribution belongs to the layer it claims. A session protocol change is Layer 2, not Layer 3. |
| **Quality bar** | A senior engineer would accept this in a production project without edits. |
| **No secrets** | No real API keys, tokens, passwords, PII, or credentials from any real project. |
| **Code examples run** | Every code block is syntactically correct and copy-paste ready. |

### Merge Criteria

- At least one maintainer approval
- All CI checks pass
- No unresolved review comments
- PR description is complete (not just a title)

## PR Requirements Checklist

Every PR must satisfy all of the following before merge is considered:

- [ ] No placeholder text in any new or modified file
- [ ] All relative links verified to resolve to existing files
- [ ] If adding a file, it is listed in the relevant directory `README.md`
- [ ] If adding a file, it is listed in the root `README.md` file inventory
- [ ] Code examples are syntactically correct and copy-pasteable without modification
- [ ] `python3 -m pytest tests/` passes with no failures
- [ ] No secrets, credentials, or PII in any file
- [ ] `CHANGELOG.md` entry added describing the change

## How to Run Tests

The test suite covers all automation scripts, naming conventions, cross-references, template completeness, and governance compliance.

### Setup

```bash
pip install -r requirements-dev.txt
```

### Run all tests

```bash
python3 -m pytest tests/
```

### Run with coverage (CI-equivalent)

```bash
python3 -m pytest tests/ --cov=automation --cov=scripts --cov-fail-under=80
```

The coverage gate is 80%. PRs that reduce coverage below this threshold will not be merged.

### Adding tests for new automation scripts

Every new file in `automation/` must have a corresponding test file:

```
automation/my_new_script.py  →  tests/test_my_new_script.py
```

Test files follow the naming pattern `test_[script_name].py`. Import the module using the path setup in `tests/conftest.py`, which inserts both `automation/` and `scripts/` into `sys.path`.

## Adding a New Agent

Agents live in `agents/`. Each agent definition is a self-contained Markdown file that specifies what the agent reads, what it produces, and the explicit boundaries of its authority.

### Step-by-step

1. Copy `agents/security-reviewer.md` as your starting template.
2. Rename the file to `agents/[agent-name].md` using kebab-case.
3. Define all required sections:
   - **Purpose** — one sentence stating what the agent does and why it exists
   - **When to Use** — the trigger condition (manual slash command, CI event, or session protocol step)
   - **What It Reads** — every file or context source the agent consults, with a note on what it extracts from each
   - **What It Outputs** — the exact format of the output (PASS/WARN/FAIL verdicts, comment structure, log entries)
   - **CAN list** — specific actions the agent is permitted to take
   - **CANNOT list** — explicit scope boundaries and write-access restrictions
   - **Example Usage** — a real, copy-pasteable invocation prompt
4. Add the agent to `agents/README.md` with a one-line description in the index table.
5. Add the agent file to the file inventory in the root `README.md`.
6. Verify there are no external dependencies — the agent must work in a standard Claude Code session with access to the repository only.
7. Confirm that write access constraints are stated explicitly. An agent with no write access to production branches must say so in the CANNOT list.

### Requirements for agent definitions

- The CANNOT list is mandatory. Omitting it is not acceptable.
- The example prompt must work without modification in a Claude Code session.
- If the agent integrates with a CI step or slash command, name both in the definition.

## How to Add a New Pattern

Patterns live in `patterns/`. Each pattern documents a repeatable governance technique: the problem it addresses, when to apply it, and how to implement it.

### Step-by-step

1. Add a new file at `patterns/[pattern-name].md` using kebab-case.
2. Structure the file with these sections in order:
   - **Problem** — the failure mode or risk this pattern addresses
   - **When to Apply** — the conditions under which this pattern is appropriate
   - **Implementation** — concrete steps for applying the pattern, with code examples where relevant
   - **Example** — a complete worked instance, not a summary
   - **Related Patterns** — relative links to other patterns in `patterns/` that interact with this one
3. Add the pattern to `patterns/README.md` with a one-line description in the index.
4. If the pattern is an output verification technique, add it to `docs/quality-control-patterns.md`.
5. Add the pattern file to the file inventory in the root `README.md`.

## How to Add a New CI Platform

CI platform configurations live in `ci-cd/`. The canonical reference implementation is `ci-cd/github-actions/`. All new platform integrations must provide equivalent governance enforcement.

### Step-by-step

1. Create a directory at `ci-cd/[platform-name]/` using kebab-case.
2. Add a `README.md` inside the directory with:
   - Prerequisites and authentication requirements for the platform
   - Step-by-step setup instructions
   - Explanation of what each workflow file does
3. Implement the governance check equivalent: a pipeline step that enforces `CHANGELOG.md` has been updated and that naming conventions pass. Reference the equivalent step in `ci-cd/github-actions/` to understand what is required.
4. Add an entry for the new platform in the comparison table in `ci-cd/README.md`, listing which governance checks are supported.
5. If the platform has implications for IDE or multi-tool workflows, add a note in `docs/multi-ide-support.md`.
6. Add all new files to the file inventory in the root `README.md`.

**Reference:** `ci-cd/github-actions/` is the canonical implementation. When in doubt, match its structure and enforce the same governance checks.

## How to Add New IDE Support

IDE-specific governance configurations live in `templates/`. Each IDE template translates the framework's Layer 1 constitution into the configuration format that IDE uses to instruct its AI assistant.

### Step-by-step

1. Add a new template at `templates/[ide-name]-[config-name].md` using kebab-case (for example, `templates/cursor-rules.md` or `templates/copilot-instructions.md`).
2. Use `templates/cursor-rules.md` or `templates/copilot-instructions.md` as the structural reference.
3. The template must include governance equivalents for:
   - **Security rules** — what the AI assistant must never write or expose
   - **Naming conventions** — file and directory naming rules from the framework
   - **Session protocol equivalent** — the start/during/end discipline adapted to the IDE's instruction format
4. Add the template to `templates/README.md` with a one-line description.
5. Add an entry for the IDE in the comparison matrix in `docs/multi-ide-support.md`, indicating which governance features are supported.
6. Add the template file to the file inventory in the root `README.md`.

## Adding a New Agent

Agents live in `agents/`. Follow the existing structure exactly:

```markdown
# [Agent Name] Agent

## Purpose
One sentence: what this agent does and why it exists.

## Trigger
When is this agent invoked? (manual slash command / CI event / session protocol step)

## Input
What files or context does this agent read?
- File 1 and what it extracts from it
- File 2 and what it extracts from it

## Mandate
What this agent CAN do:
- Specific action 1
- Specific action 2

What this agent CANNOT do:
- Write access restriction
- Scope boundary

## Output Format
Structured output specification: PASS/WARN/FAIL verdicts, comment format, log entries.

## Integration
Which layer, which CI step, which slash command invokes this agent.

## Example Prompt
A real, copy-pasteable prompt that invokes this agent correctly.
```

**Requirements for agent definitions:**

- Write access constraints must be stated explicitly. An agent with no write access to production branches says so.
- The mandate section must include both CAN and CANNOT lists. Omitting CANNOT is not acceptable.
- The example prompt must work without modification in a Claude Code session.

## Adding a New Slash Command

Commands live in `commands/`. Each command is a self-contained Markdown file:

```markdown
# /command-name

## Purpose
What this command does in one sentence.

## When to Use
Specific trigger conditions or workflow steps where this command applies.

## What the Agent Reads
- File 1: what it extracts
- File 2: what it extracts

## What the Agent Produces
Exact output format with headers, structure, and content specification.

## Example Output
A complete, realistic example of correct output from this command.
```

**Requirements:** A developer must be able to copy the command file into `.claude/commands/` and have it work without additional setup or external dependencies.

## Adding Templates or Examples

**Templates** (`templates/`) are generic starting points. They must:

- Contain real default content, not empty sections
- Include inline comments explaining what to customize and why
- Work without modification for a reasonable default case
- Follow the naming convention: `FILENAME.md` (uppercase for governance files like `CLAUDE.md`, `PROJECT_PLAN.md`)

**Examples** (`examples/`) are complete worked implementations. They must:

- Be drawn from or structurally consistent with real usage patterns
- Use anonymized or synthetic data — no real PII, credentials, or proprietary logic
- Include a brief README explaining what the example demonstrates and how to adapt it

## Quality Standards

| Standard | Requirement |
|----------|-------------|
| Placeholders | None. Write real content or do not create the section. |
| Cross-references | All relative links resolve to existing files. |
| Secrets | Never. No API keys, tokens, passwords, PII, connection strings. |
| Code examples | Syntactically correct and runnable. |
| Tone | Professional and direct. No marketing language inside templates. |
| Length | As long as needed, no longer. If a sentence does not earn its place, remove it. |

If you are unsure whether your contribution meets the quality bar, open a draft PR and ask for early feedback.
