# Scripts

This directory contains utility scripts and git hooks that support the AI Governance Framework.

| Path | Purpose |
|------|---------|
| `ai_security_review.py` | Scans a git diff for secrets, PII, and hardcoded credentials |
| `productivity_tracker.py` | Calculates AI productivity metrics from git history |
| `hooks/pre_commit_guard.sh` | Pre-commit hook: blocks commits containing governance violations |
| `hooks/post_commit.sh` | Post-commit hook: updates session logs after each commit |

## ai_security_review.py

Scans a unified git diff for security patterns including API keys, secrets, PII, hardcoded passwords, connection strings with credentials, and internal IP addresses. Outputs structured JSON and exits with code 1 if any CRITICAL findings are detected.

Used as a hard CI gate in `.github/workflows/ai-pr-review.yml` — the PR review job fails immediately if CRITICAL findings are present.

**Severity levels:**
- `CRITICAL` — secrets and credentials that enable direct unauthorized access. Blocks CI.
- `HIGH` — sensitive references that are frequently exploitable.
- `MEDIUM` — PII, environment variable assignments, configuration issues.
- `LOW` — debug flags, TODO comments near security-sensitive code.

**Usage:**

```bash
# Scan the current PR diff against main
git diff origin/main...HEAD | python3 scripts/ai_security_review.py

# Scan a saved diff file
python3 scripts/ai_security_review.py --file changes.diff

# Integrate into pre-commit via hooks/pre_commit_guard.sh
```

**Output format:**

```json
{
  "findings": [
    {
      "severity": "CRITICAL",
      "file": "src/config.py",
      "line": 12,
      "pattern": "hardcoded_password",
      "description": "Hardcoded password value detected"
    }
  ],
  "summary": {
    "critical": 1,
    "high": 0,
    "medium": 2,
    "low": 0
  }
}
```

Exit code 0 means no CRITICAL findings. Exit code 1 means at least one CRITICAL finding.

---

## productivity_tracker.py

Calculates AI productivity metrics from git history: commit velocity, hour-of-day distribution, task type breakdown, governance compliance score, and per-author statistics. Uses only the Python standard library.

```bash
python3 scripts/productivity_tracker.py .
python3 scripts/productivity_tracker.py . --days 30 --format json
```

See `--help` for the full option list.

---

## hooks/pre_commit_guard.sh

A git pre-commit hook that blocks commits containing governance violations:

- Staged files containing secrets or PII (via `ai_security_review.py`)
- Missing or empty `CHANGELOG.md` when source code files are staged

**Installation:**

```bash
cp scripts/hooks/pre_commit_guard.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Or use the `.pre-commit-config.yaml` in `ci-cd/pre-commit/` for a managed installation.

---

## hooks/post_commit.sh

A git post-commit hook that appends a lightweight session log entry after each commit. Useful for tracking session progress when CHANGELOG.md is updated at session end rather than per-commit.

**Installation:**

```bash
cp scripts/hooks/post_commit.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

---

## Adding New Scripts

Follow these conventions:

1. **Filename:** `snake_case.py` for Python, `kebab-case.sh` for shell.
2. **Entry point:** All Python scripts use `if __name__ == "__main__":` with a `build_parser()` function and `sys.exit(run(...))` pattern.
3. **Dependencies:** Standard library only wherever possible. If external dependencies are required, document them here and in any CI workflow that uses the script.
4. **Exit codes:** 0 = success or no issues found, 1 = gate failed or critical issues detected.
5. **Help:** `python3 scripts/my_script.py --help` must produce useful output.
6. **Update this README** when adding a new script.
