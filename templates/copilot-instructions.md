# GitHub Copilot Instructions

Copy this file to your project as `.github/copilot-instructions.md`.
GitHub Copilot reads this file and applies it as context for all suggestions in the repository.

---

## Project context

- **Project:** [Your Project Name]
- **Description:** [What this project does — one sentence]
- **Stack:** [Primary languages, frameworks, databases]
- **Owner:** [Team name or individual]
- **Governance:** AI Governance Framework

## Naming conventions

Follow these naming rules in all generated code:

- Python files: `snake_case.py`
- JavaScript/TypeScript files: `kebab-case.ts` or `camelCase.ts` (use whichever is established in this repo)
- Markdown documentation: `kebab-case.md`
- Directories: `kebab-case/`
- Classes and types: `PascalCase`
- Functions and variables: `snake_case` (Python) or `camelCase` (JS/TS)
- Constants: `UPPER_SNAKE_CASE`
- Commit messages: conventional commits format — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

All identifiers, comments, and documentation: English only.

## Code style

- Prefer explicit over implicit
- Avoid abbreviations in public APIs and function names
- New public functions require a docstring or JSDoc comment
- Tests must mirror the source structure: `tests/test_feature.py` for `src/feature.py`
- Do not leave `TODO`, `FIXME`, or placeholder comments in committed code — resolve them or open an issue

## Security rules

Never generate code that:

- Hardcodes API keys, tokens, passwords, or connection strings
- Logs or prints personal data (names, emails, health records, financial data)
- Disables SSL/TLS verification
- Uses `eval()` or equivalent on untrusted input
- Constructs SQL queries via string formatting (use parameterised queries)
- Stores credentials in environment variable names that include the actual value

If a test or example requires a secret-like value, use a clearly fake placeholder such as `sk-test-000000000000` or `example-token`.

## Architecture rules

- Source files belong in `src/` or the established module root — not at the project root
- Configuration files belong at the project root or in a dedicated `config/` directory
- Test files belong in `tests/` and mirror the source structure
- Do not create new top-level directories without an architectural decision record in `docs/adr/`
- Do not add new dependencies without updating `requirements.txt`, `package.json`, or the appropriate dependency file

## What to update when changing code

When suggesting code changes:

1. If source code changes, CHANGELOG.md must also be updated in the same commit/PR
2. If a public function signature changes, update all callers and the docstring
3. If a new pattern is introduced, check `docs/adr/` for a relevant decision record
4. If CLAUDE.md or equivalent governance files change, flag that a second reviewer is required

---

## Limitations of GitHub Copilot governance

GitHub Copilot enforces conventions through suggestion quality, not enforcement. This file guides what Copilot suggests — it does not block merges, require reviews, or maintain cross-session memory.

**Copilot can help with:**
- Suggesting code that follows the naming conventions above
- Avoiding common security anti-patterns in generated code
- Generating test structure that mirrors source structure
- Suggesting docstring formats consistent with the project

**Copilot cannot enforce:**
- Blocking commits that violate conventions (requires CI/CD)
- Requiring CHANGELOG.md updates before merging (requires CI/CD)
- Multi-reviewer requirements for governance file changes (requires branch protection)
- Session protocol (start/during/end phases) — Copilot has no session concept
- Cross-session memory — Copilot has no persistent project state

**To get enforcement:** pair Copilot with the GitHub Actions workflows in `ci-cd/github-actions/`. The workflows block merges that violate governance rules regardless of which IDE generated the code.

For a full comparison of IDE governance capabilities, see `docs/multi-ide-support.md`.

---

## Setup checklist

- [ ] File saved as `.github/copilot-instructions.md`
- [ ] `project_context` section updated with actual project values
- [ ] Naming convention section updated if project uses different conventions than the defaults
- [ ] `ci-cd/github-actions/governance-check.yml` copied to `.github/workflows/` for enforcement
- [ ] `CHANGELOG.md` created from `templates/CHANGELOG.md`
- [ ] `CLAUDE.md` created from `templates/CLAUDE.md` if also using Claude Code
