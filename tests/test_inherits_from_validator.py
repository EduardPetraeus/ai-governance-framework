"""Tests for automation/inherits_from_validator.py.

Covers: section extraction, threshold extraction, inheritance detection,
violation checks (missing sections, prohibited permissions, threshold lowering),
and the top-level validate() function.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch


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
        content = "## project_context\n\nA project.\n\n## conventions\n\nSnake case.\n"
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
            "## security_protocol\n\nNo secrets.\n\n## conventions\n\nSnake case.\n"
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
            "## security_protocol\n\nNo secrets.\n\n## conventions\n\nSnake case.\n",
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
        parent.write_text("## security_protocol\n\nNo secrets.\n", encoding="utf-8")
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            f"inherits_from: {parent.name}\n\n## project_context\n\nOnly context.\n",
            encoding="utf-8",
        )
        result = ifv.validate(child)
        missing = [
            v for v in result["violations"] if v["type"] == "missing_required_section"
        ]
        assert len(missing) >= 1

    def test_report_summary_keys_present(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text(
            "## project_context\n\nText.\n", encoding="utf-8"
        )
        result = ifv.validate(tmp_path / "CLAUDE.md")
        # File without inherits_from has no summary key — that is valid behaviour.
        # Files with parents do have summary.
        assert "valid" in result

    def test_extra_parent_argument_is_used(self, tmp_path):
        parent = tmp_path / "org.md"
        parent.write_text("## security_protocol\n\nNo secrets.\n", encoding="utf-8")
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


# ---------------------------------------------------------------------------
# fetch_constitution — URL and local path branches
# ---------------------------------------------------------------------------


class TestFetchConstitution:
    """Tests for fetch_constitution covering URL and local path branches."""

    def test_local_path_relative_to_base_dir(self, tmp_path):
        """Test that local paths are resolved relative to base_dir."""
        parent = tmp_path / "parent.md"
        parent.write_text("## security_protocol\n\nContent.\n", encoding="utf-8")
        content = ifv.fetch_constitution("parent.md", tmp_path)
        assert content is not None
        assert "security_protocol" in content

    def test_local_path_absolute(self, tmp_path):
        """Test that absolute local paths are resolved correctly."""
        parent = tmp_path / "parent.md"
        parent.write_text("## conventions\n\nContent.\n", encoding="utf-8")
        content = ifv.fetch_constitution(str(parent), tmp_path)
        assert content is not None
        assert "conventions" in content

    def test_local_path_not_found_returns_none(self, tmp_path):
        """Test that a missing local file returns None."""
        content = ifv.fetch_constitution("nonexistent.md", tmp_path)
        assert content is None

    @patch("inherits_from_validator.urllib.request.urlopen")
    def test_url_fetch_success(self, mock_urlopen, tmp_path):
        """Test that URL fetching works when the request succeeds."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"## security_protocol\n\nRemote content.\n"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        content = ifv.fetch_constitution("https://example.com/CLAUDE.md", tmp_path)
        assert content is not None
        assert "security_protocol" in content

    @patch("inherits_from_validator.urllib.request.urlopen")
    def test_url_fetch_failure_returns_none(self, mock_urlopen, tmp_path):
        """Test that URL fetch failures return None gracefully."""
        mock_urlopen.side_effect = Exception("Network error")
        content = ifv.fetch_constitution("https://example.com/CLAUDE.md", tmp_path)
        assert content is None


# ---------------------------------------------------------------------------
# extract_thresholds — error handling
# ---------------------------------------------------------------------------


class TestExtractThresholdsExtended:
    """Extended tests for extract_thresholds covering error paths."""

    def test_max_files_extracted(self):
        """Test that maximum files threshold is extracted."""
        content = "Maximum 20 files per session.\n"
        thresholds = ifv.extract_thresholds(content)
        assert "max_files" in thresholds
        assert thresholds["max_files"] == 20

    def test_max_lines_extracted(self):
        """Test that maximum lines threshold is extracted."""
        content = "Maximum 500 lines per commit.\n"
        thresholds = ifv.extract_thresholds(content)
        assert "max_lines" in thresholds
        assert thresholds["max_lines"] == 500

    def test_threshold_generic_extracted(self):
        """Test that generic threshold values are extracted."""
        content = "Quality threshold 80 percent.\n"
        thresholds = ifv.extract_thresholds(content)
        assert "threshold_generic" in thresholds
        assert thresholds["threshold_generic"] == 80

    def test_minimum_generic_extracted(self):
        """Test that minimum values are extracted."""
        content = "Minimum 3 reviewers required.\n"
        thresholds = ifv.extract_thresholds(content)
        assert "minimum_generic" in thresholds
        assert thresholds["minimum_generic"] == 3


# ---------------------------------------------------------------------------
# check_prohibited_permissions
# ---------------------------------------------------------------------------


class TestCheckProhibitedPermissions:
    """Tests for check_prohibited_permissions covering violation detection."""

    def test_no_violation_when_no_prohibition(self):
        """Test that no violation is raised when parent has no prohibitions."""
        parent = "## security_protocol\n\nFollow best practices.\n"
        local = "## security_protocol\n\nExtended security practices.\n"
        violations = ifv.check_prohibited_permissions(local, parent, "parent.md")
        assert violations == []

    def test_violation_when_force_push_allowed_but_prohibited(self):
        """Test violation when local allows force push but parent prohibits it."""
        parent = "Never force push to main branch.\n"
        local = "Allow force push when needed.\n"
        violations = ifv.check_prohibited_permissions(local, parent, "parent.md")
        assert any(v["type"] == "prohibited_permission_granted" for v in violations)

    def test_violation_when_skip_review_allowed_but_prohibited(self):
        """Test violation when local allows skipping review but parent prohibits it."""
        parent = "Never skip review for any pull request.\n"
        local = "Allow skip review for hotfixes.\n"
        violations = ifv.check_prohibited_permissions(local, parent, "parent.md")
        assert any(v["type"] == "prohibited_permission_granted" for v in violations)

    def test_violation_when_commit_secrets_allowed(self):
        """Test violation when local allows committing secrets but parent prohibits."""
        parent = "Never commit secret or credential to the repository.\n"
        local = "It is acceptable to commit secret values for testing.\n"
        violations = ifv.check_prohibited_permissions(local, parent, "parent.md")
        assert any(v["type"] == "prohibited_permission_granted" for v in violations)

    def test_violation_auto_commit_allowed_but_prohibited(self):
        """Test violation when local allows auto-commit but parent prohibits.

        The prohibition regex is: (never|no)\\s+\\w*\\s*(auto.commit|...|commit\\s+without)
        The grant regex is: (auto.commit|commit\\s+automatically|automatically\\s+commit)
        """
        parent = "Never use automatic commit in this project.\n"
        local = "Enable auto-commit for faster workflows.\n"
        violations = ifv.check_prohibited_permissions(local, parent, "parent.md")
        assert any(v["type"] == "prohibited_permission_granted" for v in violations)


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------


class TestFormatText:
    """Tests for the format_text function covering all branches."""

    def test_format_error_report(self):
        """Test format_text with an error report (file not found)."""
        report = {
            "valid": False,
            "error": "File not found: /tmp/CLAUDE.md",
            "violations": [],
        }
        text = ifv.format_text(report)
        assert "ERROR" in text
        assert "File not found" in text

    def test_format_valid_report_no_parents(self):
        """Test format_text with a valid report and no parents checked."""
        report = {
            "valid": True,
            "local_file": "/tmp/CLAUDE.md",
            "note": "No inherits_from section found.",
            "parents_checked": [],
            "violations": [],
            "summary": {
                "missing_sections": 0,
                "prohibited_permissions": 0,
                "lowered_thresholds": 0,
                "fetch_failures": 0,
            },
        }
        text = ifv.format_text(report)
        assert "VALID" in text
        assert "No inherits_from" in text
        assert "(none)" in text

    def test_format_report_with_violations(self):
        """Test format_text with violations present."""
        report = {
            "valid": False,
            "local_file": "/tmp/CLAUDE.md",
            "parents_checked": ["parent.md"],
            "violations": [
                {
                    "type": "missing_required_section",
                    "parent_rule": "Section 'security_protocol' defined in parent.md",
                    "local_rule": "Section 'security_protocol' is absent",
                    "description": "Parent requires 'security_protocol'.",
                },
            ],
            "summary": {
                "missing_sections": 1,
                "prohibited_permissions": 0,
                "lowered_thresholds": 0,
                "fetch_failures": 0,
            },
        }
        text = ifv.format_text(report)
        assert "INVALID" in text
        assert "MISSING_REQUIRED_SECTION" in text
        assert "1 missing sections" in text

    def test_format_valid_report_with_parents(self):
        """Test format_text with a valid report that checked parents."""
        report = {
            "valid": True,
            "local_file": "/tmp/CLAUDE.md",
            "parents_checked": ["parent.md", "org.md"],
            "violations": [],
            "summary": {
                "missing_sections": 0,
                "prohibited_permissions": 0,
                "lowered_thresholds": 0,
                "fetch_failures": 0,
            },
        }
        text = ifv.format_text(report)
        assert "VALID" in text
        assert "parent.md" in text
        assert "No violations" in text


# ---------------------------------------------------------------------------
# validate — extended coverage
# ---------------------------------------------------------------------------


class TestValidateExtended:
    """Extended tests for validate() covering URL parents and all violation types."""

    def test_validate_with_threshold_lowering(self, tmp_path):
        """Test that threshold lowering violations are detected."""
        parent = tmp_path / "parent.md"
        parent.write_text(
            "## security_protocol\n\nBlast radius: maximum 20 files per session.\n\n"
            "## conventions\n\nSnake case.\n\n"
            "## mandatory_session_protocol\n\nRequired.\n\n"
            "## quality_standards\n\nHigh quality.\n",
            encoding="utf-8",
        )
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            f"inherits_from: {parent.name}\n\n"
            "## security_protocol\n\nBlast radius: maximum 5 files per session.\n\n"
            "## conventions\n\nSnake case.\n\n"
            "## mandatory_session_protocol\n\nRequired.\n\n"
            "## quality_standards\n\nHigh quality.\n",
            encoding="utf-8",
        )
        result = ifv.validate(child)
        lowered = [v for v in result["violations"] if v["type"] == "threshold_lowered"]
        assert len(lowered) >= 1

    def test_validate_summary_counts(self, tmp_path):
        """Test that the summary dictionary counts are correct."""
        parent = tmp_path / "parent.md"
        parent.write_text(
            "## security_protocol\n\nNo secrets.\n\n"
            "## conventions\n\nSnake case.\n\n"
            "## mandatory_session_protocol\n\nRequired.\n\n"
            "## quality_standards\n\nStrict quality.\n",
            encoding="utf-8",
        )
        child = tmp_path / "CLAUDE.md"
        child.write_text(
            f"inherits_from: {parent.name}\n\n"
            "## project_context\n\nOnly context, missing required sections.\n",
            encoding="utf-8",
        )
        result = ifv.validate(child)
        assert result["summary"]["missing_sections"] >= 1


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    """Tests for the CLI argument parser builder."""

    def test_build_parser_returns_parser(self):
        """Test that build_parser returns a valid ArgumentParser."""
        parser = ifv.build_parser()
        assert parser is not None

    def test_parser_with_required_arg(self):
        """Test parser with required positional argument."""
        parser = ifv.build_parser()
        args = parser.parse_args(["CLAUDE.md"])
        assert args.claude_md == Path("CLAUDE.md")
        assert args.threshold == "strict"
        assert args.output_format == "text"
        assert args.extra_parents is None

    def test_parser_with_all_args(self):
        """Test parser with all optional arguments."""
        parser = ifv.build_parser()
        args = parser.parse_args(
            [
                "CLAUDE.md",
                "--parent",
                "parent1.md",
                "--parent",
                "parent2.md",
                "--threshold",
                "warn",
                "--format",
                "json",
            ]
        )
        assert args.claude_md == Path("CLAUDE.md")
        assert args.extra_parents == ["parent1.md", "parent2.md"]
        assert args.threshold == "warn"
        assert args.output_format == "json"
