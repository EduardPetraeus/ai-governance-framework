# .windsurfrules — AI Governance Framework

Copy this file to your project root as `.windsurfrules`.
Windsurf (Codeium) reads this file automatically and applies it as context for all AI flows.

---

## project_context

- **Project:** [Your Project Name]
- **Description:** [What this project does — one sentence]
- **Stack:** [Primary languages, frameworks, databases]
- **Owner:** [Team name or individual]
- **Governance:** AI Governance Framework — Layer 1 (Constitution)
- **IDE:** Windsurf

## conventions

### naming

- Python files: `snake_case.py`
- JavaScript/TypeScript files: `kebab-case.ts` (or `camelCase.ts` — document your choice here)
- Markdown docs: `kebab-case.md`
- Directories: `kebab-case/`
- Classes and types: `PascalCase`
- Functions and variables: `snake_case` (Python) or `camelCase` (JS/TS)
- Constants: `UPPER_SNAKE_CASE`
- Git branches: `type/short-description` (e.g., `feat/payment-flow`, `fix/null-pointer`)
- Commit messages: conventional commits — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

All identifiers, comments, and docstrings: English only. No placeholder text in committed files.

### file_structure

- Source code in established module root (document specific paths here)
- Tests in `tests/` mirroring source structure
- Documentation in `docs/`
- Configuration at project root

## session_protocol

### session_start

Before making any code changes in a new Cascade session:

1. Read `PROJECT_PLAN.md` — identify active phase and current tasks
2. Read `CHANGELOG.md` — understand what changed in previous sessions
3. Read `ARCHITECTURE.md` if it exists — respect structural decisions
4. Confirm task scope before creating or modifying files

### during_session

- Complete one logical unit before starting the next
- If a change in file A requires a change in file B, make both changes
- Flag issues outside scope as comments or issues rather than fixing them silently
- Do not modify more than 10 files per session without explicit user confirmation

### session_end

Before closing the session:

1. Add a session summary entry to `CHANGELOG.md`
2. Verify all new relative links resolve to existing files
3. Summarize files changed, decisions made, and open items for the next session

## security

Never include in generated or modified files:

- API keys, tokens, secrets, passwords, connection strings
- Personal data: names, emails, health records, financial data
- Internal hostnames, IP addresses, or paths from real production systems
- Real credentials or configuration from external systems

For examples or tests requiring credential-like values, use clearly fake placeholders:
- API key: `sk-test-000000000000000000000000000000000000000000000000`
- Password: `example-password-do-not-use`
- Database URL: `postgresql://user:password@localhost:5432/testdb`

## quality

- No empty files — every file must have real, usable content
- No placeholder sections — if it cannot be written yet, do not create it
- New public functions require docstrings or JSDoc comments
- Test files must exist for new modules before the session ends
- Could a new developer read this codebase and understand what is happening? If not, it is incomplete.

## kill_switch

Stop the current task and ask for explicit human confirmation if:

- About to commit anything resembling a secret or credential
- About to push directly to main without a pull request
- The same error has occurred more than twice with different approaches
- About to delete files that may contain uncommitted work
- Confidence in the correct approach is below 30%

---

## Windsurf-specific notes

### Cascade flows

When using Windsurf's Cascade (multi-step agentic mode), apply this governance:

- Each Cascade action should align with one task from `PROJECT_PLAN.md`
- Do not let Cascade create files outside the established directory structure without confirmation
- If Cascade proposes creating a new top-level directory, pause and confirm before proceeding
- After a Cascade flow completes, update `CHANGELOG.md` with what was changed

### Governance coverage compared to Claude Code

| Feature | Windsurf | Claude Code |
|---------|----------|-------------|
| Convention guidance | Partial (context-based) | Full (enforced in session) |
| Session protocol | Manual | Automated via slash commands |
| Cross-session memory | None | CHANGELOG.md + MEMORY.md |
| Security scanning | Partial (suggestion-level) | Full (per-file, per-session) |
| Kill switch | None | Configured in CLAUDE.md |
| Agentic scope control | Limited | Full via session protocol |

### Enforcing what Windsurf cannot

Windsurf reads `.windsurfrules` as soft context — it guides suggestions and Cascade flows but does not block actions at the CI/CD level.

For enforcement that blocks merges and requires reviews:

```bash
# Copy GitHub Actions workflows to your project
cp ci-cd/github-actions/governance-check.yml .github/workflows/
cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/
```

Or for GitLab:
```bash
cp ci-cd/gitlab/.gitlab-ci.yml .gitlab-ci.yml
```

For a full comparison of IDE governance capabilities, see `docs/multi-ide-support.md`.

---

## Setup checklist

- [ ] File saved as `.windsurfrules`
- [ ] `project_context` section updated with actual values
- [ ] `conventions` section updated to match established project conventions
- [ ] `CHANGELOG.md` created from `templates/CHANGELOG.md`
- [ ] `PROJECT_PLAN.md` created from `templates/PROJECT_PLAN.md`
- [ ] CI/CD workflow copied from `ci-cd/` for enforcement
