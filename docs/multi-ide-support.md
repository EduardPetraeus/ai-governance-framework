# Multi-IDE Support

The AI Governance Framework works with any AI coding tool. The governance layer that runs in the IDE is the softest layer — it guides suggestions but cannot block commits. The CI/CD layer is the enforcement layer — it blocks merges that violate rules regardless of which IDE generated the code.

This document covers: what each IDE can enforce, setup instructions, and the honest gaps.

## Feature comparison matrix

| Feature | Claude Code | Cursor | Windsurf | Copilot | Aider |
|---------|-------------|--------|----------|---------|-------|
| Reads governance file | CLAUDE.md | .cursorrules | .windsurfrules | copilot-instructions.md | CONVENTIONS.md |
| Session protocol (start/during/end) | Automated via slash commands | Manual | Manual | None | Manual per-command |
| Cross-session memory | CHANGELOG.md + MEMORY.md | None | None | None | None |
| Security scanning (per-file) | Yes | Partial | Partial | Partial | Partial |
| Kill switch (automatic stop) | Configurable | None | None | None | None |
| Model routing by task type | Configurable | None | None | None | None |
| Constitutional inheritance | Yes (inherits_from) | None | None | None | None |
| Slash commands | Yes (.claude/commands/) | None | None | None | None |
| Agent orchestration | Yes (agents/) | None | None | None | None |
| Confidence scoring | Yes | None | None | None | None |
| Blocks convention violations | No (IDE-level only) | No | No | No | No |
| Blocks merges without CHANGELOG | Requires CI/CD | Requires CI/CD | Requires CI/CD | Requires CI/CD | Requires CI/CD |
| Requires 2nd reviewer for CLAUDE.md | Requires CI/CD | N/A | N/A | N/A | N/A |
| Multi-model validation | Yes (dual-model pattern) | No | No | No | No |

### Honest assessment

Claude Code gets the full governance stack because the framework was designed for it. Every other IDE gets partial governance — the naming conventions and security guidance apply, but the session protocol, cross-session memory, kill switch, and constitutional inheritance require the full Claude Code integration.

The CI/CD layer is IDE-agnostic. The governance check, AI PR review, and release workflows run the same checks regardless of whether the code was written with Claude Code, Cursor, or a text editor.

**Recommended approach:** use whichever IDE you prefer for day-to-day coding, and rely on CI/CD for enforcement. If you want full governance (session memory, slash commands, multi-agent orchestration), use Claude Code.

---

## Claude Code

**Configuration file:** `CLAUDE.md`

Claude Code is the reference implementation for this framework. It reads CLAUDE.md at session start and enforces all governance rules during the session.

### Setup

```bash
# Option 1: npx wizard
npx ai-governance-init

# Option 2: manual
cp templates/CLAUDE.md CLAUDE.md
# Edit project_context section
```

### What Claude Code enforces

- Full session protocol via `/plan-session` and `/end-session` slash commands
- Cross-session memory via CHANGELOG.md and MEMORY.md
- Security scanning per-file and per-session
- Kill switch: stops automatically when configured thresholds are hit
- Constitutional inheritance: team projects inherit from org-level CLAUDE.md
- Model routing: uses Opus for architecture decisions, Sonnet for code, Haiku for config

### Slash commands available

Copy `commands/` to `.claude/commands/` in your project:

```bash
bash scripts/deploy_commands.sh /path/to/your-project
```

Commands: `/plan-session`, `/end-session`, `/health-check`, `/audit`, `/validate`, `/status`, `/security-review`, `/research`, `/prioritize`, `/upgrade`

---

## Cursor

**Configuration file:** `.cursorrules`

Cursor reads `.cursorrules` from the repository root and applies it as context for all AI suggestions and Composer sessions.

### Setup

```bash
cp templates/cursor-rules.md .cursorrules
# Edit project_context and conventions sections
```

Then add CI/CD for enforcement:

```bash
mkdir -p .github/workflows
cp ci-cd/github-actions/governance-check.yml .github/workflows/
cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/
```

### What Cursor enforces

- Naming convention guidance in AI suggestions
- Security anti-pattern avoidance in generated code
- Architecture guidance through context

### What Cursor cannot enforce

- Session protocol (start/during/end phases)
- Cross-session memory — each Composer session starts without context
- Kill switch — Cursor does not stop automatically
- Blocking commits that violate conventions

### Cursor-specific notes

- Use Cursor's Composer for multi-file changes; reference `PROJECT_PLAN.md` in your prompt
- Manually update `CHANGELOG.md` at the end of each Composer session
- For multi-file architecture changes, describe the architectural decision in `docs/adr/` first

---

## Windsurf (Codeium)

**Configuration file:** `.windsurfrules`

Windsurf reads `.windsurfrules` from the repository root and applies it as context for Cascade (multi-step agentic) flows.

### Setup

```bash
cp templates/windsurf-rules.md .windsurfrules
# Edit project_context and conventions sections
```

Then add CI/CD for enforcement:

```bash
mkdir -p .github/workflows
cp ci-cd/github-actions/governance-check.yml .github/workflows/
```

Or for GitLab:

```bash
cp ci-cd/gitlab/.gitlab-ci.yml .gitlab-ci.yml
```

### What Windsurf enforces

- Naming convention guidance in Cascade suggestions
- Security anti-pattern avoidance
- Architecture guidance through context in Cascade flows

### Windsurf-specific notes

- Cascade is Windsurf's agentic mode — it can modify multiple files in one flow
- Apply the session protocol manually: read `PROJECT_PLAN.md` before starting a Cascade flow
- After a Cascade flow completes, update `CHANGELOG.md` before closing Windsurf
- Use the kill switch conditions from `.windsurfrules` as a checklist before each Cascade run

### What Windsurf cannot enforce

Same gaps as Cursor: no session memory, no automatic kill switch, no constitutional inheritance.

---

## GitHub Copilot

**Configuration file:** `.github/copilot-instructions.md`

GitHub Copilot reads this file as custom instructions that apply to all Copilot suggestions in the repository. This is a newer feature — verify it is enabled in your GitHub organization settings.

### Setup

```bash
mkdir -p .github
cp templates/copilot-instructions.md .github/copilot-instructions.md
# Edit project_context and naming conventions
```

### What Copilot enforces

Copilot applies instructions as suggestion context, not enforcement. It can:

- Suggest code that follows naming conventions
- Avoid common security anti-patterns in generated code
- Generate test file structure that mirrors source structure

### What Copilot cannot enforce

- Session protocol (Copilot has no session concept — it responds to one request at a time)
- Cross-session memory
- Blocking commits or requiring CHANGELOG updates
- Kill switch behaviour

### Copilot-specific notes

- Copilot is best for line-level and function-level suggestions, not multi-file architecture work
- For multi-file features, use Copilot Chat with the repository context and reference `PROJECT_PLAN.md` manually
- Rely entirely on CI/CD for governance enforcement when using Copilot

---

## Aider

**Configuration file:** `CONVENTIONS.md`

Aider reads `CONVENTIONS.md` from the repository root automatically. You can also specify it explicitly with `aider --conventions CONVENTIONS.md`.

### Setup

```bash
cp templates/aider-conventions.md CONVENTIONS.md
# Edit project_context and naming conventions
```

### Usage patterns

```bash
# Standard usage — Aider picks up CONVENTIONS.md automatically
aider src/feature.py tests/test_feature.py

# With additional context files
aider --read PROJECT_PLAN.md --read ARCHITECTURE.md src/feature.py

# Explicit conventions file (if not in root)
aider --conventions CONVENTIONS.md src/feature.py
```

### Session protocol for Aider

Aider has no persistent session state. Apply the session protocol per-command:

1. Before running: check `PROJECT_PLAN.md` for the current task
2. Scope the aider command to one logical unit
3. After aider completes: run tests, review the diff, update `CHANGELOG.md`, commit

### What Aider enforces

- Follows naming conventions in generated code
- Applies security rules from CONVENTIONS.md
- Generates docstrings and tests when requested

### What Aider cannot enforce

- No session memory between aider runs
- No automatic kill switch
- No blocking of conventional violations at the commit level

---

## Setup instructions by IDE

### Minimum setup (any IDE)

1. Create `CHANGELOG.md` from `templates/CHANGELOG.md`
2. Create `PROJECT_PLAN.md` from `templates/PROJECT_PLAN.md`
3. Copy your IDE's configuration file (see table above)
4. Add CI/CD from `ci-cd/` — this is the enforcement layer

### Full setup (Claude Code)

1. Run `npx ai-governance-init` or copy templates manually
2. Copy `commands/` to `.claude/commands/`
3. Add CI/CD from `ci-cd/github-actions/`
4. Read `docs/getting-started.md` for the complete walkthrough

### Adding CI/CD enforcement (any IDE)

GitHub Actions:
```bash
mkdir -p .github/workflows
cp ci-cd/github-actions/governance-check.yml .github/workflows/
cp ci-cd/github-actions/ai-pr-review.yml .github/workflows/  # requires ANTHROPIC_API_KEY secret
cp ci-cd/github-actions/release.yml .github/workflows/
```

GitLab CI:
```bash
cp ci-cd/gitlab/.gitlab-ci.yml .gitlab-ci.yml
```

CircleCI:
```bash
mkdir -p .circleci
cp ci-cd/circleci/.circleci/config.yml .circleci/config.yml
```

Bitbucket Pipelines:
```bash
cp ci-cd/bitbucket/bitbucket-pipelines.yml bitbucket-pipelines.yml
```

Azure DevOps:
```bash
cp ci-cd/azure-devops/azure-pipelines.yml azure-pipelines.yml
```

---

## Migration guide between IDEs

### From Cursor to Claude Code

1. Your `.cursorrules` conventions translate directly to CLAUDE.md — copy the `conventions` section
2. Create a full `CLAUDE.md` from `templates/CLAUDE.md`, importing your conventions
3. Install slash commands: `bash scripts/deploy_commands.sh .`
4. Update `CHANGELOG.md` to document the IDE migration as a session entry
5. Keep `.cursorrules` in the repository — Cursor users who clone the repo can still benefit from it

### From Claude Code to Cursor

1. Copy the `conventions` section from `CLAUDE.md` to `.cursorrules`
2. Keep `CLAUDE.md`, `CHANGELOG.md`, and `PROJECT_PLAN.md` — CI/CD still uses them
3. Accept the governance reduction: session memory and kill switch no longer function
4. Rely entirely on CI/CD for enforcement

### Running multiple IDEs on the same project

All four IDE configuration files can coexist in the same repository:

```
.cursorrules                        # Cursor users
.windsurfrules                      # Windsurf users
.github/copilot-instructions.md    # Copilot users
CONVENTIONS.md                      # Aider users
CLAUDE.md                          # Claude Code users (full governance)
```

Keep conventions consistent across all files. The CI/CD layer enforces the same rules for all IDEs.

---

## IDE governance summary

The framework applies a principle of maximum governance for the IDE in use, with CI/CD as the non-negotiable floor:

- **Claude Code:** full governance — sessions, memory, kill switch, inheritance
- **Cursor / Windsurf:** partial governance — naming, security guidance, architecture context
- **Copilot:** minimal governance — naming and security suggestions only
- **Aider:** partial governance — per-command conventions and security rules
- **CI/CD (all IDEs):** full enforcement — CHANGELOG requirement, AI PR review, release gates

The CI/CD enforcement is the same regardless of which IDE wrote the code. Governance at the IDE level is additive — it catches problems earlier, before CI/CD runs.
