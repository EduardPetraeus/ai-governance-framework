# AGENTS.md — AI Governance Framework

Copy this file to your repository root as `AGENTS.md`.
This file is read by Claude Code, GitHub Copilot agent mode, Cursor, Windsurf, and Aider.
It provides portable governance instructions that work across all AI coding tools.

Claude Code users: pair this file with `CLAUDE.md` for full governance including session
protocol, slash commands, kill switch, and constitutional inheritance.
See `docs/agents-md-integration.md` for coexistence options.

---

## purpose

- **Project:** [Your Project Name]
- **Description:** [What this project does — one sentence]
- **Stack:** [Primary languages, frameworks, databases]
- **Owner:** [Team name or individual]
- **Governance:** AI Governance Framework — portable bridge layer

This agent assists with software development in this repository. It follows the
commands, guidelines, and security rules defined in this file. It stops and asks for
human confirmation whenever the kill switch conditions below are met.

This file maps to Layer 1 (Constitution) of the AI Governance Framework. It encodes
the portable subset of governance rules that apply regardless of which AI tool is active.
Tool-specific features (session memory, slash commands, agent orchestration) require the
full `CLAUDE.md` integration.

---

## commands

Run these commands to verify changes before committing. The agent must run the relevant
commands after making changes and report results before asking to commit.

### Testing

```bash
# Run the full test suite
[replace with: pytest tests/ OR npm test OR go test ./...]

# Run tests for a specific module
[replace with: pytest tests/test_feature.py -v OR npm test -- feature]

# Check test coverage (minimum 80%)
[replace with: pytest --cov=src --cov-report=term-missing OR npm run test:coverage]
```

### Linting and formatting

```bash
# Check code style
[replace with: ruff check . OR eslint src/ OR golangci-lint run]

# Auto-format code
[replace with: ruff format . OR prettier --write src/ OR gofmt -w .]
```

### Governance checks

```bash
# Verify governance health score
python automation/health_score_calculator.py .

# Check staged changes for secrets or security issues
python scripts/ai_security_review.py

# Validate cross-references in documentation
python automation/health_score_calculator.py . --check-refs
```

---

## guidelines

### Naming conventions

| Item | Convention |
|------|------------|
| Python files | `snake_case.py` |
| JS/TS files | `kebab-case.ts` or `camelCase.ts` (use what is established) |
| Markdown docs | `kebab-case.md` |
| Directories | `kebab-case/` |
| Classes and types | `PascalCase` |
| Functions and variables | `snake_case` (Python) or `camelCase` (JS/TS) |
| Constants | `UPPER_SNAKE_CASE` |
| Branches | `type/short-description` (e.g., `feat/user-auth`, `fix/null-check`) |
| Commits | Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:` |

All identifiers, comments, and documentation: English only.

### Before making changes

1. Read `PROJECT_PLAN.md` — understand current phase and active tasks
2. Read `CHANGELOG.md` — understand what was done last session
3. Confirm scope: which files, what outcome — do not start until scope is agreed
4. Do not modify more than 15 files per session without explicit confirmation

### During changes

- Complete one logical unit before starting the next
- If a change requires an update in another file, make both changes in the same session
- Flag issues outside the current scope — do not fix them silently
- After each file: verify relative links resolve to existing files

### After changes

- Update `CHANGELOG.md`: files modified, decisions made, goal progress
- Run the relevant commands from the `commands` section above
- Summarize what changed before asking to commit

### Architecture rules

- New top-level directories require justification in `docs/adr/` before creation
- New dependencies require an update to the appropriate manifest (`requirements.txt`, `package.json`, etc.)
- Source files belong in the established module root, not the project root
- Test files belong in `tests/` and mirror the source structure

### Code quality

- New public functions require a docstring (Python) or JSDoc comment (JS/TS)
- Tests must exist for new public functions before the change is considered complete
- Do not leave `TODO`, `FIXME`, or placeholder comments in committed code
- Maximum function length: 50 lines — extract named helpers for anything longer
- Do not import unused modules

---

## security

Never include in any file or generate code that contains:

- API keys, tokens, secrets, or connection strings
- Passwords or credentials of any kind (even values that look like test data)
- Personal data: names, emails, national IDs, phone numbers, addresses
- Health data: diagnoses, biometrics, patient records
- Financial data: account numbers, card numbers, salary data
- Internal hostnames, IP addresses, or production paths
- Real data samples of any kind, even if believed to be anonymized

For tests or examples requiring secret-like values, use clearly fake placeholders:

```python
API_KEY = "sk-test-000000000000000000000000000000000000000000000000"
DATABASE_URL = "postgresql://testuser:testpass@localhost:5432/testdb"
```

Never generate code that:

- Constructs SQL queries via string formatting — use parameterised queries
- Uses `eval()` or `exec()` on untrusted input
- Disables SSL/TLS verification (`verify=False`, `NODE_TLS_REJECT_UNAUTHORIZED=0`)
- Logs or prints personal data, health records, or financial data
- Stores credentials in environment variable names that expose the value

---

## kill_switch

Stop immediately and request human confirmation if:

- About to commit anything that resembles a real secret or credential
- About to merge to main without a pull request
- Confidence in the correct approach is below 30%
- The same error has appeared three or more times with different approaches
- About to delete or overwrite files that may contain uncommitted work

---

## Governance coverage by tool

This file provides a portable governance layer. Capabilities vary by tool:

| Feature | Claude Code | Cursor | Windsurf | Copilot | Aider |
|---------|:-----------:|:------:|:--------:|:-------:|:-----:|
| Reads AGENTS.md | Yes | Partial | Partial | Agent mode | Yes |
| Naming convention guidance | Yes | Yes | Yes | Yes | Yes |
| Security rule guidance | Yes | Yes | Yes | Yes | Yes |
| Session protocol | Manual | Manual | Manual | None | Manual |
| Kill switch (auto-stop) | With CLAUDE.md | None | None | None | None |
| Cross-session memory | With CLAUDE.md | None | None | None | None |
| Slash commands | With CLAUDE.md | None | None | None | None |
| CI/CD enforcement | IDE-agnostic | IDE-agnostic | IDE-agnostic | IDE-agnostic | IDE-agnostic |

**Claude Code:** pair this file with `templates/CLAUDE.md` for full governance.
See `docs/agents-md-integration.md` for the three coexistence patterns.

**All tools:** add CI/CD workflows from `ci-cd/github-actions/` for enforcement.
The workflows run the same checks regardless of which tool generated the code.

---

## Setup checklist

- [ ] File saved as `AGENTS.md` in repository root
- [ ] `purpose` section updated with actual project values
- [ ] `commands` section updated with actual test, lint, and build commands
- [ ] Naming conventions section updated if project differs from defaults
- [ ] `CHANGELOG.md` created from `templates/CHANGELOG.md`
- [ ] `PROJECT_PLAN.md` created from `templates/PROJECT_PLAN.md`
- [ ] CI/CD workflow copied from `ci-cd/` for enforcement
- [ ] If using Claude Code: `CLAUDE.md` created from `templates/CLAUDE.md`
