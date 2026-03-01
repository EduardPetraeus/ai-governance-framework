"""Tests that validate the example configurations in examples/.

Checks that each persona example (solo-developer, small-team, enterprise)
has the required files, contains real content, and does not use placeholder text.
"""

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"

PERSONAS = ["solo-developer", "small-team", "enterprise"]

PLACEHOLDER_PATTERNS = [
    r"\[YOUR VALUE HERE\]",
    r"\[INSERT [A-Z]",
    r"<placeholder>",
]

REQUIRED_CLAUDE_SECTIONS = [
    "project_context",
    "conventions",
    "mandatory_session_protocol",
    "security_protocol",
]


class TestExampleDirectoriesExist:
    @pytest.mark.parametrize("persona", PERSONAS)
    def test_persona_directory_exists(self, persona):
        assert (EXAMPLES_DIR / persona).is_dir(), (
            f"examples/{persona}/ directory is missing"
        )

    @pytest.mark.parametrize("persona", PERSONAS)
    def test_persona_has_claude_md(self, persona):
        assert (EXAMPLES_DIR / persona / "CLAUDE.md").is_file(), (
            f"examples/{persona}/CLAUDE.md is missing"
        )

    @pytest.mark.parametrize("persona", PERSONAS)
    def test_persona_has_readme(self, persona):
        assert (EXAMPLES_DIR / persona / "README.md").is_file(), (
            f"examples/{persona}/README.md is missing"
        )


class TestExampleClaudeMdContent:
    @pytest.mark.parametrize("persona", PERSONAS)
    def test_claude_md_has_project_context(self, persona):
        content = (
            (EXAMPLES_DIR / persona / "CLAUDE.md").read_text(encoding="utf-8").lower()
        )
        assert "project_context" in content, (
            f"examples/{persona}/CLAUDE.md missing project_context section"
        )

    @pytest.mark.parametrize("persona", PERSONAS)
    def test_claude_md_has_security_section(self, persona):
        content = (
            (EXAMPLES_DIR / persona / "CLAUDE.md").read_text(encoding="utf-8").lower()
        )
        # Examples may use "security" or "security_protocol" as the heading
        has_security = "security" in content
        assert has_security, (
            f"examples/{persona}/CLAUDE.md missing any security section"
        )

    @pytest.mark.parametrize("persona", PERSONAS)
    def test_claude_md_has_no_placeholder_text(self, persona):
        content = (EXAMPLES_DIR / persona / "CLAUDE.md").read_text(encoding="utf-8")
        for pattern in PLACEHOLDER_PATTERNS:
            assert not re.search(pattern, content, re.IGNORECASE), (
                f"Placeholder '{pattern}' in examples/{persona}/CLAUDE.md"
            )

    @pytest.mark.parametrize("persona", PERSONAS)
    def test_claude_md_is_substantial(self, persona):
        content = (EXAMPLES_DIR / persona / "CLAUDE.md").read_text(encoding="utf-8")
        assert len(content.strip()) > 200, (
            f"examples/{persona}/CLAUDE.md is too short to be a useful example"
        )


class TestExampleReadmeContent:
    @pytest.mark.parametrize("persona", PERSONAS)
    def test_readme_has_meaningful_content(self, persona):
        content = (EXAMPLES_DIR / persona / "README.md").read_text(encoding="utf-8")
        assert len(content.strip()) > 50, f"examples/{persona}/README.md is too short"


class TestExamplesIndexExists:
    def test_examples_readme_exists(self):
        assert (EXAMPLES_DIR / "README.md").is_file()

    def test_examples_readme_references_all_personas(self):
        content = (EXAMPLES_DIR / "README.md").read_text(encoding="utf-8").lower()
        # The README uses prose headings ("Solo Developer") rather than directory names.
        persona_keywords = {
            "solo-developer": "solo",
            "small-team": "small",
            "enterprise": "enterprise",
        }
        for persona, keyword in persona_keywords.items():
            assert keyword in content, (
                f"examples/README.md does not reference '{persona}'"
            )
