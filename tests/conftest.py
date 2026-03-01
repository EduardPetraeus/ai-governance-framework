"""Shared fixtures and sys.path setup for the ai-governance-framework test suite."""

import sys
from pathlib import Path

import pytest

# Make automation/ and scripts/ importable without installing the package.
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "automation"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture
def repo_root() -> Path:
    """Return the root of the actual ai-governance-framework repository."""
    return REPO_ROOT


@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    """Return a temp directory with no governance files."""
    return tmp_path


@pytest.fixture
def minimal_repo(tmp_path: Path) -> Path:
    """Return a temp directory with only a minimal CLAUDE.md (score ~10)."""
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\nA minimal project constitution.\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def full_repo(tmp_path: Path) -> Path:
    """Return a temp directory with a comprehensive governance setup (score 80+)."""
    # CLAUDE.md with all five required sections
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\n"
        "## project_context\n\nTest project context.\n\n"
        "## conventions\n\nSnake case for Python files.\n\n"
        "## mandatory_session_protocol\n\nStart each session with a read.\n\n"
        "## security_protocol\n\nNo secrets in code. No PII.\n\n"
        "## mandatory_task_reporting\n\nReport all completed tasks.\n",
        encoding="utf-8",
    )
    (tmp_path / "PROJECT_PLAN.md").write_text(
        "# Project Plan\n\n## Phase 1\n\n- Task A\n",
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# CHANGELOG\n\n"
        "## Session 001 -- 2025-01-01\n\n### Scope confirmed\nSetup.\n\n"
        "## Session 002 -- 2025-01-08\n\n### Scope confirmed\nFeatures.\n\n"
        "## Session 003 -- 2025-01-15\n\n### Scope confirmed\nTests.\n",
        encoding="utf-8",
    )
    (tmp_path / "ARCHITECTURE.md").write_text(
        "# Architecture\n\n## Stack\n\nPython, GitHub Actions.\n",
        encoding="utf-8",
    )
    (tmp_path / "MEMORY.md").write_text(
        "# Memory\n\n## Patterns\n\nKnown working patterns.\n",
        encoding="utf-8",
    )
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "ADR-001-use-markdown.md").write_text(
        "# ADR-001: Use Markdown\n\n## Status\n\nAccepted.\n",
        encoding="utf-8",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ai-pr-review.yml").write_text(
        "name: AI PR Review\non: [pull_request]\njobs:\n  review:\n    steps:\n"
        "      - name: Review\n        run: echo anthropic\n",
        encoding="utf-8",
    )
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "security-reviewer.md").write_text(
        "# Security Reviewer\n\nReviews code for secrets.\n",
        encoding="utf-8",
    )
    commands_dir = tmp_path / "commands"
    commands_dir.mkdir()
    (commands_dir / "status.md").write_text(
        "# /status\n\nPrints current status.\n",
        encoding="utf-8",
    )
    patterns_dir = tmp_path / "patterns"
    patterns_dir.mkdir()
    (patterns_dir / "dual-model-validation.md").write_text(
        "# Dual Model Validation\n\nUse two models.\n",
        encoding="utf-8",
    )
    automation_dir = tmp_path / "automation"
    automation_dir.mkdir()
    (automation_dir / "health_score_calculator.py").write_text(
        "# health score calculator placeholder\n",
        encoding="utf-8",
    )
    (tmp_path / ".gitignore").write_text(
        ".env\n*.pyc\n__pycache__/\n", encoding="utf-8"
    )
    # v0.3.0 additions
    (tmp_path / "AGENTS.md").write_text(
        "# AGENTS\n\nPortable governance bridge.\n",
        encoding="utf-8",
    )
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "self-validation-checklist.md").write_text(
        "# Self-Validation Checklist\n\n## 1. Constitution Health\n\nChecks here.\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def sample_diff_clean() -> str:
    """Return a git diff with no security findings."""
    return (
        "diff --git a/src/utils.py b/src/utils.py\n"
        "--- a/src/utils.py\n"
        "+++ b/src/utils.py\n"
        "@@ -1,3 +1,6 @@\n"
        " def greet(name: str) -> str:\n"
        '+     """Return a greeting."""\n'
        "+     return f'Hello, {name}!'\n"
        "+\n"
        "+ def farewell(name: str) -> str:\n"
        '+     return f"Goodbye, {name}."\n'
    )


@pytest.fixture
def sample_diff_with_api_key() -> str:
    """Return a git diff containing an Anthropic API key."""
    return (
        "diff --git a/config.py b/config.py\n"
        "--- a/config.py\n"
        "+++ b/config.py\n"
        "@@ -1,2 +1,3 @@\n"
        " DEBUG = True\n"
        "+API_KEY = 'sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcd'\n"
        " TIMEOUT = 30\n"
    )
