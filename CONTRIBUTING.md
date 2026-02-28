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
