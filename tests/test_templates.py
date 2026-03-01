"""Tests that validate all governance templates in templates/.

Checks existence, required sections, absence of placeholder text,
valid Markdown structure, and that templates work as-is defaults.
"""

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"

PLACEHOLDER_PATTERNS = [
    r"\[YOUR VALUE HERE\]",
    r"\[INSERT",
    r"FIXME",
    r"<placeholder>",
]

REQUIRED_TEMPLATE_FILES = [
    "CLAUDE.md",
    "CLAUDE.org.md",
    "CLAUDE.team.md",
    "PROJECT_PLAN.md",
    "CHANGELOG.md",
    "ARCHITECTURE.md",
    "MEMORY.md",
    "DECISIONS.md",
    "SPRINT_LOG.md",
    "COST_LOG.md",
]


class TestTemplateFilesExist:
    @pytest.mark.parametrize("filename", REQUIRED_TEMPLATE_FILES)
    def test_required_template_exists(self, filename):
        assert (TEMPLATES_DIR / filename).is_file(), (
            f"Required template templates/{filename} is missing"
        )


class TestClaudeMdTemplate:
    @pytest.fixture(autouse=True)
    def content(self):
        self._content = (TEMPLATES_DIR / "CLAUDE.md").read_text(encoding="utf-8")

    def test_has_project_context_section(self):
        assert "project_context" in self._content.lower()

    def test_has_conventions_section(self):
        assert "conventions" in self._content.lower()

    def test_has_mandatory_session_protocol_section(self):
        assert "mandatory_session_protocol" in self._content.lower()

    def test_has_security_protocol_section(self):
        assert "security_protocol" in self._content.lower()

    def test_contains_no_placeholder_text(self):
        for pattern in PLACEHOLDER_PATTERNS:
            assert not re.search(pattern, self._content, re.IGNORECASE), (
                f"Placeholder found in CLAUDE.md: {pattern}"
            )

    def test_starts_with_heading(self):
        assert self._content.startswith("#"), (
            "CLAUDE.md template must start with a Markdown heading"
        )


class TestClaudeOrgMdTemplate:
    @pytest.fixture(autouse=True)
    def content(self):
        self._content = (TEMPLATES_DIR / "CLAUDE.org.md").read_text(encoding="utf-8")

    def test_has_security_section(self):
        # CLAUDE.org.md uses "org_security" rather than "security_protocol"
        assert "security" in self._content.lower()

    def test_has_naming_or_conventions_section(self):
        # CLAUDE.org.md uses "org_naming" for conventions
        assert (
            "naming" in self._content.lower() or "conventions" in self._content.lower()
        )

    def test_contains_no_placeholder_text(self):
        for pattern in PLACEHOLDER_PATTERNS:
            assert not re.search(pattern, self._content, re.IGNORECASE), (
                f"Placeholder found in CLAUDE.org.md: {pattern}"
            )

    def test_has_nonempty_content(self):
        assert len(self._content.strip()) > 100


class TestClaudeTeamMdTemplate:
    @pytest.fixture(autouse=True)
    def content(self):
        self._content = (TEMPLATES_DIR / "CLAUDE.team.md").read_text(encoding="utf-8")

    def test_has_meaningful_content(self):
        assert len(self._content.strip()) > 100

    def test_contains_no_placeholder_text(self):
        for pattern in PLACEHOLDER_PATTERNS:
            assert not re.search(pattern, self._content, re.IGNORECASE)


class TestAllTemplatesHaveContent:
    @pytest.mark.parametrize("filename", REQUIRED_TEMPLATE_FILES)
    def test_template_is_not_empty(self, filename):
        content = (TEMPLATES_DIR / filename).read_text(encoding="utf-8").strip()
        assert len(content) > 50, f"Template {filename} has too little content"

    @pytest.mark.parametrize("filename", REQUIRED_TEMPLATE_FILES)
    def test_template_has_no_placeholder_text(self, filename):
        content = (TEMPLATES_DIR / filename).read_text(encoding="utf-8")
        for pattern in PLACEHOLDER_PATTERNS:
            assert not re.search(pattern, content, re.IGNORECASE), (
                f"Placeholder '{pattern}' found in templates/{filename}"
            )

    @pytest.mark.parametrize("filename", REQUIRED_TEMPLATE_FILES)
    def test_template_starts_with_markdown_heading(self, filename):
        content = (TEMPLATES_DIR / filename).read_text(encoding="utf-8")
        assert content.lstrip().startswith("#"), (
            f"templates/{filename} does not start with a Markdown heading"
        )
