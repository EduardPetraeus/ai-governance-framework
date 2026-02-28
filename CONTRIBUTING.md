# Contributing to AI Governance Framework

Thank you for your interest in contributing. This framework exists to solve real problems in AI-assisted software development. Contributions that improve its practical usefulness are welcome.

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) Code of Conduct. Be direct, be constructive, and assume good intent.

---

## Development Setup

No build tools required. The framework consists of Markdown files, YAML workflows, and Python scripts.

**Requirements:**
- Git
- A text editor
- Python 3.10+ (for scripts only — no installation needed to contribute templates or docs)

```bash
git clone https://github.com/your-org/ai-governance-framework.git
cd ai-governance-framework
```

That is it.

---

## How to Report Issues

**Bug reports** — use the GitHub issue tracker. Include:
- Which file or template is affected
- What the file currently says
- What it should say (or what behavior is broken)
- The context in which you encountered the problem (solo dev, small team, enterprise)

**Feature requests** — open an issue with the label `enhancement`. Describe:
- The problem you are trying to solve
- Which layer of the framework it belongs to (Layer 1–7)
- Whether you have a concrete implementation idea or just the problem statement

**Questions** — use GitHub Discussions, not issues.

---

## How to Suggest Improvements to Templates, Agents, or Commands

Open an issue before submitting a PR for significant changes. This avoids wasted effort when a suggestion conflicts with the framework's design principles.

For small improvements (fixing wording, correcting cross-references, improving examples), a PR without a prior issue is fine.

---

## Pull Request Process

### Branch Naming

```
feature/short-description     # New capability
fix/short-description         # Correction to existing content
docs/short-description        # Documentation only
agent/agent-name              # New agent definition
command/command-name          # New slash command
example/example-name          # New worked example
```

### PR Title Format

```
[Layer N] Short description of what this changes
```

Examples:
- `[Layer 1] Add CLAUDE.md template for data engineering projects`
- `[Layer 3] Add GitLab CI equivalent of AI PR review workflow`
- `[Layer 5] Add ADR template for API design decisions`

### What Reviewers Check

Every PR is evaluated against these criteria:

1. **No placeholders** — every field in a template must contain real, usable content. `[YOUR VALUE HERE]` is not acceptable. Write a realistic default or a concrete example.
2. **Cross-references work** — if a file references another file, that file must exist and the relative path must be correct.
3. **Layer alignment** — the contribution belongs to the layer it claims to address. A session protocol belongs in Layer 2, not Layer 3.
4. **Quality bar** — the content is at the level a senior engineer would accept in a production project.
5. **No secrets** — no real API keys, tokens, personal data, or credentials from any real project.

---

## How to Add a New Agent

Agents live in `agents/`. Follow the existing structure:

```markdown
# [Agent Name] Agent

## Purpose
One sentence: what this agent does and why it exists.

## Trigger
When is this agent invoked? (manual slash command / CI/CD event / session protocol step)

## Input
- What files or context does this agent read?

## Mandate
- What can this agent do?
- What can this agent NOT do? (write access restrictions, scope limits)

## Output format
Describe the structured output: PASS/WARN/FAIL verdicts, comment format, log entries.

## Integration
How does this agent connect to the rest of the framework? (which layer, which CI step, which slash command)

## Example prompt
A real, copy-pasteable prompt that invokes this agent with correct context.
```

All agent definitions must specify write access constraints explicitly. An agent that has no write access to production branches must say so.

---

## How to Add a New Slash Command

Commands live in `commands/`. Each command is a Markdown file that defines what the agent does when the command is invoked.

```markdown
# /command-name

## Purpose
What does this command do?

## When to use
Specific trigger conditions or workflow steps.

## What the agent reads
List of files the agent should load before executing.

## What the agent produces
Exact output format — headers, structure, what each section contains.

## Example output
A real example of what a correct response looks like.
```

Commands must be self-contained: a developer should be able to copy the command definition into their `.claude/commands/` directory and have it work without additional setup.

---

## How to Add Templates or Examples

**Templates** (`templates/`) are generic starting points. They must:
- Contain real default content, not empty sections
- Include inline comments explaining what to customize and why
- Work without modification for a reasonable default case

**Examples** (`examples/`) are complete worked implementations. They must:
- Be drawn from or consistent with real usage patterns
- Use anonymized or synthetic data — no real personal data, credentials, or proprietary business logic
- Include a brief `README` explaining what the example demonstrates and how to adapt it

---

## Quality Standards Summary

| Standard | Requirement |
|----------|-------------|
| Placeholders | None. Write real content. |
| Cross-references | All relative links must resolve to existing files. |
| Secrets | Never. No API keys, tokens, passwords, PII. |
| Code examples | Must be syntactically correct and runnable. |
| Tone | Professional and direct. No marketing language inside templates. |
| Length | As long as needed, no longer. Remove padding. |

If you are unsure whether your contribution meets the quality bar, open a draft PR and ask.
