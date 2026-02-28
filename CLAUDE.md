# CLAUDE.md — AI Governance Framework

This file governs all AI agent sessions in this repository.
This framework governs itself. No exceptions.

## project_context

- **Repo:** ai-governance-framework
- **Purpose:** Open source framework for governing AI agents in software development
- **License:** MIT
- **Status:** Active development
- **Source of truth:** README.md (overview), docs/ (specifications)
- This repo is the reference implementation of Layer 1 (Constitution) of the framework it describes

## conventions

- File names: `kebab-case.md` for docs, patterns, agents, and commands (e.g., `session-protocol.md`); `snake_case.py` for Python source files
- Directory names: `kebab-case/` (e.g., `ci-cd/`); exception: `.circleci/` follows CircleCI's required dot-prefixed convention
- All content in English — no exceptions
- Cross-references use relative links: `[file](../path/file.md)` — never absolute URLs
- Code examples must be syntactically correct and copy-pasteable
- No placeholder text: no `[YOUR VALUE HERE]`, no `TODO`, no `...`
- Markdown only unless the file is a YAML workflow, Python script, or shell script

## mandatory_session_protocol

### Phase 1 — Start (before any file changes)

1. Read README.md — understand current framework state
2. Check open GitHub issues — identify in-progress work
3. Confirm scope with user: which layer, which files, what outcome
4. Do not create or modify files until scope is confirmed

### Phase 2 — During

- Work one section at a time (e.g., all Layer 3 templates before Layer 4)
- After each file: verify cross-references resolve to existing files
- If a change requires an update in another file, make both in the same session
- Discovered issues outside scope: flag as issues to open, do not fix silently

### Phase 3 — End (before closing session)

- Append session summary to CHANGELOG.md if it exists
- Verify all new relative links resolve
- Summarize: files created/modified, cross-references updated, issues to open

## security_protocol

Never commit or include in any file:

- API keys, tokens, credentials, connection strings
- Personal data from real people (names, emails, health data, financial data)
- Internal hostnames, IP addresses, or paths from real systems
- Data, logs, or configuration from real projects (including HealthReporting)
- If a real example is needed: use synthetic data that matches the structure

## quality_standards

- No empty files — every file has real, usable content before commit
- No placeholder sections — if it cannot be written yet, do not create it
- Templates must work as defaults without modification
- Agent definitions must specify write access constraints
- Command definitions must be self-contained and portable
- **Test:** Could a new Claude Code session read this repo and use the framework correctly? If not, the content is incomplete.
