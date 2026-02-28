# .cursorrules — AI Governance Framework

Copy this file to your project root as `.cursorrules`.
Cursor reads this file automatically and applies it as context for all AI suggestions.

---

## project_context

- **Project:** [Your Project Name]
- **Description:** [What this project does — one sentence]
- **Stack:** [Primary languages, frameworks, databases]
- **Owner:** [Team name or individual]
- **Governance:** AI Governance Framework — Layer 1 (Constitution)
- **IDE:** Cursor

## conventions

### naming

- Python files: `snake_case.py`
- JavaScript/TypeScript files: `camelCase.ts` or `kebab-case.ts` (pick one, document here)
- Markdown docs: `kebab-case.md`
- Directories: `kebab-case/`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Branches: `type/short-description` (e.g., `feat/user-auth`, `fix/login-redirect`)
- Commits: conventional commits format (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`)

### language

- All code, comments, docstrings, and variable names: English
- No placeholder text in committed files

### file_structure

- Source code in `src/` or language-appropriate root
- Tests mirror the source structure: `tests/` or `__tests__/`
- Documentation in `docs/`
- Configuration files at the project root

## session_protocol

### before_making_changes

1. Read `PROJECT_PLAN.md` if it exists — understand current phase and active tasks
2. Read `CHANGELOG.md` if it exists — understand what was done last session
3. Read `ARCHITECTURE.md` if it exists — understand structural decisions
4. Confirm scope: which layer, which files, what outcome
5. Do not create or modify files until scope is confirmed

### during_changes

- Work one section at a time — complete a logical unit before starting the next
- After each file change: verify cross-references resolve to existing files
- If a change requires an update in another file, make both changes
- Flag issues outside the current scope rather than fixing them silently
- Do not modify more than 10 files per session without explicit confirmation

### after_changes

- Update `CHANGELOG.md` with a session summary entry
- Verify all new relative links resolve to existing files
- Summarize: files created/modified, decisions made, issues to address next session

## security

Never include in any file:

- API keys, tokens, secrets, connection strings
- Passwords or credentials of any kind
- Personal data: names, emails, health records, financial data
- Internal hostnames, IP addresses, or paths from real production systems
- Data, logs, or configuration from real external systems

If a real example is needed: use synthetic data that matches the structure but contains no real values.

## quality_standards

- No empty files — every file has real, usable content
- No placeholder sections — if it cannot be written yet, do not create it
- Templates must work as defaults without modification
- Could a new developer read this codebase and understand what is happening? If not, it is incomplete.

## kill_switch

Stop and ask for human confirmation if:

- About to commit anything that resembles a secret or credential
- About to merge to main without a pull request
- Confidence in the correct approach is below 30%
- The same error has occurred more than twice with different approaches
- About to delete or overwrite files that may contain work not committed elsewhere

---

## Adopting this framework in Cursor

### Setup steps

1. Copy this file to your project root as `.cursorrules`
2. Edit the `project_context` and `conventions` sections to match your project
3. Copy `templates/CLAUDE.md` as `CLAUDE.md` if you also use Claude Code
4. Copy `templates/PROJECT_PLAN.md` as `PROJECT_PLAN.md`
5. Copy `templates/CHANGELOG.md` as `CHANGELOG.md`

### What Cursor enforces vs what it cannot

Cursor reads `.cursorrules` as soft context — it guides suggestions but does not block actions.

**Cursor can help with:**
- Suggesting code that follows the naming conventions defined above
- Reminding you to update CHANGELOG.md when prompted
- Following the session protocol when you start a conversation
- Avoiding security anti-patterns in generated code

**Cursor cannot enforce:**
- Blocking commits that violate conventions (requires CI/CD)
- Requiring CHANGELOG updates before merging (requires CI/CD)
- Multi-reviewer requirements for constitution changes (requires branch protection)
- Cross-session memory persistence (Cursor's context resets per session)

**To get full enforcement:** pair Cursor with the GitHub Actions workflows in `ci-cd/github-actions/`. The workflows catch what the IDE cannot.

### Governance coverage compared to Claude Code

| Feature | Cursor | Claude Code |
|---------|--------|-------------|
| Convention guidance | Partial (suggestions) | Full (enforced in session) |
| Session protocol | Manual | Automated via slash commands |
| Cross-session memory | None | CHANGELOG.md + MEMORY.md |
| Security scanning | Partial | Full (per-file, per-session) |
| Kill switch | None | Configured in CLAUDE.md |
| Model routing | N/A (Cursor chooses) | Configurable per task type |

Cursor provides the best experience for this framework when combined with CI/CD enforcement. For full governance, see `docs/multi-ide-support.md`.
