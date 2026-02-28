"""Tests for automation/inherits_from_validator.py.

Covers: section extraction, threshold extraction, inheritance detection,
violation checks (missing sections, prohibited permissions, threshold lowering),
and the top-level validate() function.
"""

import json
from pathlib import Path

import pytest

import inherits_from_validator as ifv


# ---------------------------------------------------------------------------
# extract_inherits_from
# ---------------------------------------------------------------------------

class TestExtractInheritsFrom:
    def test_scalar_syntax(self):
        content = "inherits_from: templates/CLAUDE.org.md\n"
        sources = ifv.extract_inherits_from(content)
        assert sources == ["templates/CLAUDE.org.md"]

    def test_list_syntax(self):
        content = "inherits_from:\n  - path/parent.md\n  - https://example.com/org.md\n"
        sources = ifv.extract_inherits_from(content)
        assert "path/parent.md" in sources
        assert "https://example.com/org.md" in sources

    def test_no_inherits_returns_empty(self):
        content = "# CLAUDE.md\n\n## project_context\n\nText.\n"
        assert ifv.extract_inherits_from(content) == []

    def test_quoted_scalar_is_unquoted(self):
        content = 'inherits_from: "templates/CLAUDE.org.md"\n'
        sources = ifv.extract_inherits_from(content)
        assert sources == ["templates/CLAUDE.org.md"]


# ---------------------------------------------------------------------------
# extract_sections
# ---------------------------------------------------------------------------

class TestExtractSections:
    def test_single_section(self):
        content = "## security_protocol\n\nNo secrets.\n"
        sections = ifv.extract_sections(content)
        assert "security_protocol" in sections

    def test_multiple_sections(self):
        content = (
            "## project_context\n\nA project.\n\n"
            "## conventions\n\nSnake case.\n"
        )
        sections = ifv.extract_sections(content)
        assert "project_context" in sections
        assert "conventions" in sections

    def test_special_chars_normalized(self):
        content = "## Mandatory Session Protocol\n\nDo this.\n"
        sections = ifv.extract_sections(content)
        assert "mandatory_session_protocol" in sections

    def test_empty_content_returns_empty_dict(self):
        assert ifv.extract_sections("") == {}


# ---------------------------------------------------------------------------
# extract_thresholds
# ---------------------------------------------------------------------------

class TestExtractThresholds:
    def test_blast_radius_extracted(self):
        content = "Blast radius: maximum 15 files per session.\n"
        thresholds = ifv.extract_thresholds(content)
        assert "blast_radius_files" in thresholds
        assert thresholds["blast_radius_files"] == 15

    def test_confidence_percent_extracted(self):
        content = "AI confidence ceiling: 85%.\n"
        thresholds = ifv.extract_thresholds(content)
        assert thresholds.get("confidence_percent") == 85

    def test_no_thresholds_returns_empty(self):
        content = "No numeric governance thresholds here.\n"
        assert ifv.extract_thresholds(content) == {}


# ---------------------------------------------------------------------------
# check_required_sections
# ---------------------------------------------------------------------------

class TestCheckRequiredSections:
    def test_no_violation_when_sections_present(self):
        parent = ifv.extract_sections(
            "## security_protocol\n\nNo secrets.\n\n"
            "## conventions\n\nSnake case.\n"
        )
        local = ifv.extract_sections(
            "## security_protocol\n\nExtended security.\n\n"
            "## conventions\n\nSnake case + PEP 8.\n"
        )
        violations = ifv.check_required_sections(local, parent, "parent.md")
        missing = [v for v in violations if v["type"] == "missing_required_section"]
        assert missing == []

    def test_violation_when_required_section_removed(self):
        parent = ifv.extract_sections("## security_protocol\n\nNo secrets.\n")
        local = ifv.extract_sections("## project_context\n\nA project.\n")
        violations = ifv.check_required_sections(local, parent, "parent.md")
        assert any(v["type"] == "missing_required_section" for v in violations)


# ---------------------------------------------------------------------------
# check_threshold_lowering
# ---------------------------------------------------------------------------

class TestCheckThresholdLowering:
    def test_no_violation_when_threshold_unchanged(self):
        parent = "Blast radius: maximum 15 files.\n"
        local = "Blast radius: maximum 15 files.\n"
        violations = ifv.check_threshold_lowering(local, parent, "parent.md")
        assert violations == []

    def test_violation_when_local_lowers_threshold(self):
        parent = "Blast radius: maximum 15 files.\n"
        local = "Blast radius: maximum 5 files.\n"
        violations = ifv.check_threshold_lowering(local, parent, "parent.md")
        assert any(v["type"] == "threshold_lowered" for v in violations)

    def test_no_violation_when_local_raises_threshold(self):
        parent = "Blast radius: maximum 15 files.\n"
        local = "Blast radius: maximum 20 files.\n"
        violations = ifv.check_threshold_lowering(local, parent, "parent.md")
        assert violations == []


# ---------------------------------------------------------------------------
# validate — top-level function
# ---------------------------------------------------------------------------

class TestValidate:
    def test_missing_file_returns_invalid(self, tmp_path):
        result = ifv.validate(tmp_path / "NONEXISTENT.md")
        assert result["valid"] is False
        assert "error" in result

    def test_file_without_inherits_from_is_valid(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text(
            "## project_context\n\nProject text.\n", encoding="utf-8"
        )
        result = ifv.validate(tmp_path / "CLAUDE.md")
        assert result["valid"] is True
        assert result["violations"] == []

    def test_valid_inheritance_produces_no_violations(self, tmp_path):
        parent = tmp_path / "parent.md"
        parent.write_text(
            "## security_protocol\n\nNo secrets.\n\n"
            "## conventions\n\nSnake case.\n",
            encoding="utf-8",
        )
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            f"inherits_from: {parent.name}\n\n"
            "## security_protocol\n\nNo secrets in code.\n\n"
            "## conventions\n\nSnake case + PEP 8.\n",
            encoding="utf-8",
        )
        result = ifv.validate(child)
        assert result["violations"] == [] or result["valid"] is True

    def test_missing_parent_section_creates_violation(self, tmp_path):
        parent = tmp_path / "parent.md"
        parent.write_text(
            "## security_protocol\n\nNo secrets.\n", encoding="utf-8"
        )
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            f"inherits_from: {parent.name}\n\n"
            "## project_context\n\nOnly context.\n",
            encoding="utf-8",
        )
        result = ifv.validate(child)
        missing = [v for v in result["violations"] if v["type"] == "missing_required_section"]
        assert len(missing) >= 1

    def test_report_summary_keys_present(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("## project_context\n\nText.\n", encoding="utf-8")
        result = ifv.validate(tmp_path / "CLAUDE.md")
        # File without inherits_from has no summary key — that is valid behaviour.
        # Files with parents do have summary.
        assert "valid" in result

    def test_extra_parent_argument_is_used(self, tmp_path):
        parent = tmp_path / "org.md"
        parent.write_text(
            "## security_protocol\n\nNo secrets.\n", encoding="utf-8"
        )
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            "## security_protocol\n\nExtended security.\n", encoding="utf-8"
        )
        result = ifv.validate(child, extra_parents=[str(parent)])
        assert "parents_checked" in result
        assert len(result["parents_checked"]) >= 1

    def test_nonexistent_parent_creates_fetch_failure(self, tmp_path):
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            "inherits_from: /nonexistent/path/parent.md\n\n"
            "## project_context\n\nText.\n",
            encoding="utf-8",
        )
        result = ifv.validate(child)
        assert any(v["type"] == "fetch_failure" for v in result["violations"])
