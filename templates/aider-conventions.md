# CONVENTIONS.md — AI Governance Framework

Aider reads this file automatically when it is present in the repository root.
Copy this file to your project root as `CONVENTIONS.md`.

Reference: `aider --conventions CONVENTIONS.md` or place in repo root for automatic loading.

---

## Project context

- **Project:** [Your Project Name]
- **Description:** [What this project does — one sentence]
- **Stack:** [Primary languages, frameworks, databases]
- **Owner:** [Team name or individual]
- **Governance:** AI Governance Framework

## Naming conventions

Aider must follow these naming rules in all generated and modified code:

### Files and directories

- Python source files: `snake_case.py`
- JavaScript/TypeScript files: `kebab-case.ts` (document your choice if different)
- Markdown documentation: `kebab-case.md`
- Directories: `kebab-case/`
- Test files: `test_module_name.py` or `module_name.test.ts`

### Code identifiers

- Classes and types: `PascalCase`
- Functions, methods, and variables: `snake_case` (Python) or `camelCase` (JS/TS)
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_leading_underscore` (Python convention)

### Git

- Branch names: `type/short-description` (e.g., `feat/add-auth`, `fix/null-check`)
- Commit messages: conventional commits format

```
feat: add user authentication endpoint
fix: correct null pointer in session handler
docs: update API reference for v2 endpoints
chore: upgrade pytest to 8.x
refactor: extract validation logic to separate module
test: add coverage for edge cases in parser
```

All identifiers, comments, and docstrings: English only. No exceptions.

## Code quality rules

- New public functions and classes require a docstring (Python) or JSDoc comment (JS/TS)
- Tests must exist for new public functions before the change is considered complete
- Do not leave `TODO`, `FIXME`, or placeholder comments in committed code
- Avoid abbreviations in public API names — prefer `get_user_by_id` over `getUsrById`
- Maximum function length: 50 lines. Split larger functions into named helpers.
- Do not import unused modules

## Security rules

Never generate code that:

- Hardcodes API keys, tokens, passwords, or database credentials
- Constructs SQL queries via string formatting — use parameterised queries
- Uses `eval()` or `exec()` on untrusted input
- Disables SSL/TLS verification (`verify=False`, `NODE_TLS_REJECT_UNAUTHORIZED=0`)
- Logs or prints personal data, health records, or financial data
- Commits `.env` files or files containing real secrets

For test fixtures requiring credential-like values, use clearly fake values:

```python
API_KEY = "sk-test-000000000000000000000000000000000000000000000000"
DATABASE_URL = "postgresql://testuser:testpass@localhost:5432/testdb"
```

## Architecture rules

- New top-level directories require justification in `docs/adr/` before creation
- Do not add dependencies without updating `requirements.txt` or `package.json`
- Source files belong in the established module root, not at the project root
- Test files belong in `tests/` and mirror the source structure

## Session protocol for Aider

Aider operates in a single-command model — there is no persistent session. Apply this protocol per command:

### Before running aider

1. Check `PROJECT_PLAN.md` to identify the current task
2. Check `CHANGELOG.md` for recent changes that affect what you are building
3. Scope the request to one logical unit: one feature, one bug fix, one refactor
4. Use `--read` to provide context files: `aider --read PROJECT_PLAN.md --read ARCHITECTURE.md`

### Aider command patterns

```bash
# Single-file fix with context
aider src/auth.py --read PROJECT_PLAN.md

# Feature addition with related files
aider src/models.py tests/test_models.py

# Documentation update
aider docs/api.md --read src/api.py

# With conventions file explicit
aider --conventions CONVENTIONS.md src/new_feature.py tests/test_new_feature.py
```

### After running aider

1. Review all changes with `git diff` before committing
2. Update `CHANGELOG.md` with what changed and why
3. Run tests: `pytest` or equivalent
4. Commit with a conventional commit message

## What Aider can and cannot enforce

Aider applies this file as instructions for code generation. It does not block commits or enforce process at the CI level.

**Aider can:**
- Follow naming conventions in generated code
- Add docstrings and tests when asked
- Avoid security anti-patterns in generated code
- Follow the file structure rules above

**Aider cannot:**
- Block a commit that violates conventions
- Require CHANGELOG.md updates (you must do this manually after each aider session)
- Enforce branch protection or second reviewers
- Maintain cross-session memory (Aider has no persistent state between runs)

**For CI enforcement:** add the GitHub Actions or GitLab CI workflows from `ci-cd/` to your repository. These workflows enforce the same governance rules regardless of which tool generated the code.

For a full comparison of IDE governance capabilities, see `docs/multi-ide-support.md`.

---

## Setup checklist

- [ ] File saved as `CONVENTIONS.md` in repository root
- [ ] `project_context` section updated with actual values
- [ ] `CHANGELOG.md` created from `templates/CHANGELOG.md`
- [ ] `PROJECT_PLAN.md` created from `templates/PROJECT_PLAN.md`
- [ ] CI/CD workflow copied from `ci-cd/` for enforcement
- [ ] Test that aider reads the file: `aider --help` (check for `--conventions` flag support)
