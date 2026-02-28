# CLAUDE.md — AI Governance Framework

This file governs all AI agent sessions in this repository.
The framework governs itself. No exceptions.

---

## project_context

- **Repo:** `ai-governance-framework`
- **Purpose:** Open source framework for governing AI agents in software development teams
- **License:** MIT
- **Status:** Active development
- **Maintainers:** See repository contributors
- **Source of truth for framework design:** `README.md` and `docs/`

This repo is the reference implementation of Layer 1 (Constitution) from the framework it describes.

---

## conventions

- All files are Markdown (`.md`) unless they are YAML workflows, Python scripts, or shell scripts
- File names use `snake_case` (e.g., `session_protocol.md`, not `SessionProtocol.md`)
- Directory names use `kebab-case` (e.g., `ci-cd/`, `docs/`)
- All content is in English — no exceptions
- Cross-references between files use relative links: `[CONTRIBUTING.md](CONTRIBUTING.md)` not absolute URLs
- Code examples in templates must be syntactically correct
- No placeholder text of any kind (`[YOUR VALUE HERE]`, `TODO`, `...`)

---

## mandatory_session_protocol

### Start (required before any file changes)

1. Read `README.md` to understand current framework state and structure
2. Check open GitHub issues for context on in-progress work
3. Confirm scope with the user: which layer, which file group, what outcome
4. Do not create or modify files until scope is confirmed

### During session

- Work one file group at a time (e.g., all Layer 3 templates before moving to Layer 4)
- After each file written or modified: confirm the cross-references are valid
- If a change in one file requires an update in another, make both changes in the same session
- Flag any discovered issues that are out of scope as issues to open — do not fix them silently

### End (required before closing session)

- If `CHANGELOG.md` exists in the repo: append a session summary entry
- Verify all new relative links resolve to existing files
- Summarize: files created or modified, cross-references updated, issues to open

---

## security_protocol

Never commit or include in any file:

- API keys, tokens, or credentials of any kind
- Personal data from any real person (names, emails, health data, financial data)
- Internal hostnames, IP addresses, or connection strings from any real system
- Any data, logs, or configuration from the HealthReporting project or any other real project
- Screenshots or outputs that contain real personal health metrics

If a real example is needed: generate synthetic data that structurally matches but contains no real values.

---

## quality_standards

- No empty files — every file must have real, usable content before it is committed
- No placeholder sections — if a section cannot be written yet, do not create it
- All code examples must be copy-pasteable and syntactically correct
- Templates must work as defaults without modification for a reasonable use case
- Agent definitions must specify write access constraints explicitly
- Command definitions must be self-contained and portable

**Test:** Could a new developer (or a new Claude Code session) read the files in this repo and immediately use the framework correctly? If not, the content is incomplete.
