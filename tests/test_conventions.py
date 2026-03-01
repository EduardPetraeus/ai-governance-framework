"""Tests that validate naming conventions and structural rules from CLAUDE.md.

Checks: kebab-case .md files, snake_case .py files, kebab-case directories,
no placeholder text outside templates, Python docstrings, agent/pattern structure.
"""

import ast
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent

PLACEHOLDER_PATTERNS = [
    r"\[YOUR VALUE HERE\]",
    r"\[INSERT [A-Z]",
    r"<placeholder>",
]

# Directories that contain .md files expected to follow kebab-case
KEBAB_MD_DIRS = [
    REPO_ROOT / "docs",
    REPO_ROOT / "patterns",
    REPO_ROOT / "agents",
    REPO_ROOT / "commands",
]

# Directories that contain .py files expected to follow snake_case
SNAKE_PY_DIRS = [
    REPO_ROOT / "automation",
    REPO_ROOT / "scripts",
]

# Directories that should themselves use kebab-case naming
# v030_build_logs is a branch-scoped build-runner artifact, excluded from convention checks
TOP_LEVEL_DIRS = [
    d
    for d in REPO_ROOT.iterdir()
    if d.is_dir()
    and not d.name.startswith(".")
    and d.name not in ("tests", "node_modules", "__pycache__", "v030_build_logs")
]


def is_kebab_case(name: str) -> bool:
    """Return True if name uses kebab-case (lowercase letters, digits, hyphens)."""
    stem = Path(name).stem
    return bool(re.match(r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$|^[a-z0-9]$", stem))


def is_snake_case(name: str) -> bool:
    """Return True if Python filename uses snake_case."""
    stem = Path(name).stem
    return bool(re.match(r"^[a-z][a-z0-9_]*$", stem))


def has_module_docstring(py_file: Path) -> bool:
    """Return True if the Python file has a module-level docstring."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    return (
        (
            isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        )
        if tree.body
        else False
    )


class TestMarkdownNamingKebabCase:
    @pytest.mark.parametrize("directory", KEBAB_MD_DIRS)
    def test_all_md_files_are_kebab_case(self, directory):
        if not directory.is_dir():
            pytest.skip(f"{directory} does not exist")
        violations = [
            f.name
            for f in directory.rglob("*.md")
            # README.md is conventionally uppercase; ADR files follow ADR-NNN-title convention
            if not is_kebab_case(f.name)
            and f.name != "README.md"
            and not f.name.startswith("ADR-")
        ]
        assert violations == [], (
            f"Non-kebab-case .md files in {directory.name}/: {violations}"
        )


class TestPythonNamingSnakeCase:
    @pytest.mark.parametrize("directory", SNAKE_PY_DIRS)
    def test_all_py_files_are_snake_case(self, directory):
        if not directory.is_dir():
            pytest.skip(f"{directory} does not exist")
        violations = [
            f.name for f in directory.glob("*.py") if not is_snake_case(f.name)
        ]
        assert violations == [], (
            f"Non-snake_case .py files in {directory.name}/: {violations}"
        )


class TestDirectoryNamingKebabCase:
    def test_top_level_directories_are_kebab_case(self):
        violations = [
            d.name
            for d in TOP_LEVEL_DIRS
            if not re.match(r"^[a-z][a-z0-9\-]*$", d.name)
        ]
        assert violations == [], f"Non-kebab-case top-level directories: {violations}"


class TestNoPlaceholderTextInNonTemplates:
    def test_docs_has_no_placeholder_text(self):
        docs_dir = REPO_ROOT / "docs"
        found = []
        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for pattern in PLACEHOLDER_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    found.append(f"{md_file.relative_to(REPO_ROOT)}: {pattern}")
        assert found == [], "Placeholder text found in docs/:\n" + "\n".join(found)

    def test_agents_has_no_placeholder_text(self):
        agents_dir = REPO_ROOT / "agents"
        found = []
        for md_file in agents_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for pattern in PLACEHOLDER_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    found.append(f"{md_file.relative_to(REPO_ROOT)}: {pattern}")
        assert found == [], "Placeholder text in agents/:\n" + "\n".join(found)

    def test_patterns_has_no_placeholder_text(self):
        patterns_dir = REPO_ROOT / "patterns"
        found = []
        for md_file in patterns_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for pattern in PLACEHOLDER_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    found.append(f"{md_file.relative_to(REPO_ROOT)}: {pattern}")
        assert found == [], "Placeholder text in patterns/:\n" + "\n".join(found)


class TestPythonFilesHaveDocstrings:
    @pytest.mark.parametrize("directory", SNAKE_PY_DIRS)
    def test_automation_scripts_have_module_docstrings(self, directory):
        if not directory.is_dir():
            pytest.skip(f"{directory} does not exist")
        missing = [
            f.name
            for f in directory.glob("*.py")
            if f.name != "__init__.py" and not has_module_docstring(f)
        ]
        assert missing == [], (
            f"Python files in {directory.name}/ without module docstrings: {missing}"
        )


class TestAgentFilesHaveConsistentStructure:
    def test_all_agent_files_have_heading(self):
        agents_dir = REPO_ROOT / "agents"
        missing_heading = []
        for md_file in agents_dir.glob("*.md"):
            if md_file.name == "README.md":
                continue
            content = md_file.read_text(encoding="utf-8")
            if not content.lstrip().startswith("#"):
                missing_heading.append(md_file.name)
        assert missing_heading == [], (
            f"Agent files without a heading: {missing_heading}"
        )

    def test_all_agent_files_are_nonempty(self):
        agents_dir = REPO_ROOT / "agents"
        empty = [
            f.name
            for f in agents_dir.glob("*.md")
            if len(f.read_text(encoding="utf-8").strip()) < 50
        ]
        assert empty == [], f"Near-empty agent files: {empty}"


class TestPatternFilesHaveConsistentStructure:
    def test_all_pattern_files_have_heading(self):
        patterns_dir = REPO_ROOT / "patterns"
        missing = []
        for md_file in patterns_dir.glob("*.md"):
            if md_file.name == "README.md":
                continue
            content = md_file.read_text(encoding="utf-8")
            if not content.lstrip().startswith("#"):
                missing.append(md_file.name)
        assert missing == [], f"Pattern files without heading: {missing}"

    def test_all_pattern_files_are_nonempty(self):
        patterns_dir = REPO_ROOT / "patterns"
        empty = [
            f.name
            for f in patterns_dir.glob("*.md")
            if len(f.read_text(encoding="utf-8").strip()) < 50
        ]
        assert empty == [], f"Near-empty pattern files: {empty}"
