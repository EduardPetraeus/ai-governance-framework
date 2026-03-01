"""Tests for automation/adr_coverage_checker.py.

Covers: keyword extraction, decision parsing (CHANGELOG and DECISIONS.md),
ADR loading, coverage checking, and the run() entry point.
"""

from pathlib import Path


import adr_coverage_checker as acc


# ---------------------------------------------------------------------------
# extract_keywords
# ---------------------------------------------------------------------------


class TestExtractKeywords:
    def test_extracts_meaningful_words(self):
        kws = acc.extract_keywords("Use PostgreSQL database for persistence")
        assert "postgresql" in kws
        assert "database" in kws
        assert "persistence" in kws

    def test_filters_stop_words(self):
        kws = acc.extract_keywords("this and that with from")
        assert "this" not in kws
        assert "with" not in kws

    def test_filters_short_words(self):
        kws = acc.extract_keywords("a to be or not to be")
        assert "a" not in kws
        assert "to" not in kws

    def test_empty_text_returns_empty_set(self):
        assert acc.extract_keywords("") == set()

    def test_case_insensitive(self):
        kws = acc.extract_keywords("PostgreSQL POSTGRESQL postgresql")
        assert len(kws) == 1


# ---------------------------------------------------------------------------
# keyword_overlap
# ---------------------------------------------------------------------------


class TestKeywordOverlap:
    def test_identical_texts_have_high_overlap(self):
        text = "Use PostgreSQL database for persistent storage layer"
        assert acc.keyword_overlap(text, text) >= 3

    def test_disjoint_texts_have_zero_overlap(self):
        a = "apple orange banana fruit salad"
        b = "quantum physics neutron particle wave"
        assert acc.keyword_overlap(a, b) == 0

    def test_partial_overlap_counted(self):
        a = "React frontend component rendering performance"
        b = "Frontend performance optimizations rendering speed"
        overlap = acc.keyword_overlap(a, b)
        assert overlap >= 2


# ---------------------------------------------------------------------------
# parse_decisions_md
# ---------------------------------------------------------------------------


class TestParseDecisionsMd:
    def test_parses_single_dec_entry(self, tmp_path):
        (tmp_path / "DECISIONS.md").write_text(
            "# Decisions\n\n"
            "## DEC-001 -- Use PostgreSQL -- 2025-01-01\n\n"
            "We chose PostgreSQL for relational storage.\n",
            encoding="utf-8",
        )
        decisions = acc.parse_decisions_md(tmp_path / "DECISIONS.md")
        assert len(decisions) == 1
        assert decisions[0].identifier == "DEC-001"
        assert "PostgreSQL" in decisions[0].title

    def test_missing_file_returns_empty(self, tmp_path):
        assert acc.parse_decisions_md(tmp_path / "MISSING.md") == []

    def test_multiple_entries_parsed(self, tmp_path):
        (tmp_path / "DECISIONS.md").write_text(
            "## DEC-001 -- Choice A -- 2025-01-01\n\nWe chose A.\n\n"
            "## DEC-002 -- Choice B -- 2025-02-01\n\nWe chose B.\n",
            encoding="utf-8",
        )
        decisions = acc.parse_decisions_md(tmp_path / "DECISIONS.md")
        assert len(decisions) == 2


# ---------------------------------------------------------------------------
# load_adrs
# ---------------------------------------------------------------------------


class TestLoadAdrs:
    def test_loads_adr_files(self, tmp_path):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-use-postgres.md").write_text(
            "# ADR-001: Use PostgreSQL\n\n## Status\nAccepted.\n",
            encoding="utf-8",
        )
        adrs = acc.load_adrs(adr_dir)
        assert len(adrs) == 1
        assert adrs[0].number == "001"

    def test_skips_template_adr_000(self, tmp_path):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-000-template.md").write_text(
            "# ADR-000: Template\n", encoding="utf-8"
        )
        adrs = acc.load_adrs(adr_dir)
        assert adrs == []

    def test_missing_dir_returns_empty(self, tmp_path):
        assert acc.load_adrs(tmp_path / "nonexistent") == []


# ---------------------------------------------------------------------------
# check_coverage
# ---------------------------------------------------------------------------


class TestCheckCoverage:
    def test_decision_with_matching_adr_is_covered(self):
        decision = acc.Decision(
            source="DECISIONS.md",
            identifier="DEC-001",
            title="Use PostgreSQL for storage",
            body="Chosen for ACID compliance and relational queries.",
        )
        adr = acc.Adr(
            path="ADR-001.md",
            number="001",
            title="Use PostgreSQL database for storage layer",
            content="PostgreSQL chosen for ACID transactions and relational queries.",
        )
        results = acc.check_coverage([decision], [adr])
        assert results[0].covered is True

    def test_decision_without_matching_adr_is_uncovered(self):
        decision = acc.Decision(
            source="CHANGELOG.md",
            identifier="Session 001 — Some Choice",
            title="Switch to microservices",
            body="We split the monolith into independent services.",
        )
        adr = acc.Adr(
            path="ADR-001.md",
            number="001",
            title="Use PostgreSQL",
            content="Database selection for ACID compliance.",
        )
        results = acc.check_coverage([decision], [adr])
        assert results[0].covered is False

    def test_no_decisions_no_results(self):
        assert acc.check_coverage([], []) == []


# ---------------------------------------------------------------------------
# run — exit codes
# ---------------------------------------------------------------------------


class TestRun:
    def test_empty_repo_exits_zero(self, tmp_path):
        exit_code = acc.run(tmp_path, threshold="strict", output_format="json")
        assert exit_code == 0

    def test_warn_threshold_exits_zero_even_with_uncovered(self, tmp_path):
        (tmp_path / "DECISIONS.md").write_text(
            "## DEC-001 -- Deploy microservices -- 2025-01-01\n\n"
            "We deploy each service independently with Docker.\n",
            encoding="utf-8",
        )
        exit_code = acc.run(tmp_path, threshold="warn", output_format="json")
        assert exit_code == 0

    def test_strict_threshold_exits_one_with_uncovered(self, tmp_path, capsys):
        """Test that strict threshold returns exit code 1 when uncovered decisions exist."""
        (tmp_path / "DECISIONS.md").write_text(
            "## DEC-001 -- Deploy microservices architecture -- 2025-01-01\n\n"
            "We deploy each service independently with Docker and Kubernetes.\n",
            encoding="utf-8",
        )
        exit_code = acc.run(tmp_path, threshold="strict", output_format="text")
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "GATE FAILED" in captured.err

    def test_strict_threshold_json_exits_one_with_uncovered(self, tmp_path, capsys):
        """Test strict threshold with JSON output returns 1 when uncovered decisions exist."""
        (tmp_path / "DECISIONS.md").write_text(
            "## DEC-001 -- Deploy microservices architecture -- 2025-01-01\n\n"
            "We deploy each service independently with Docker and Kubernetes.\n",
            encoding="utf-8",
        )
        exit_code = acc.run(tmp_path, threshold="strict", output_format="json")
        assert exit_code == 1

    def test_text_format_output_includes_report(self, tmp_path, capsys):
        """Test that text format output includes the coverage report."""
        (tmp_path / "DECISIONS.md").write_text(
            "## DEC-001 -- Use PostgreSQL for storage -- 2025-01-01\n\n"
            "We chose PostgreSQL for relational queries and ACID compliance.\n",
            encoding="utf-8",
        )
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-use-postgres.md").write_text(
            "# ADR-001: Use PostgreSQL\n\nWe use PostgreSQL for relational storage and ACID.\n",
            encoding="utf-8",
        )
        acc.run(tmp_path, threshold="warn", output_format="text")
        captured = capsys.readouterr()
        assert "ADR Coverage Report" in captured.out


# ---------------------------------------------------------------------------
# parse_changelog_decisions
# ---------------------------------------------------------------------------


class TestParseChangelogDecisions:
    """Tests for extracting decisions from CHANGELOG.md sessions."""

    def test_extracts_decisions_from_session(self, tmp_path):
        """Test that decisions are extracted from CHANGELOG session blocks."""
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 001 -- 2025-01-01\n\n"
            "### Decisions made\n\n"
            "- **Use PostgreSQL**: We chose PostgreSQL for relational storage and ACID compliance throughout the system.\n"
            "- **Deploy on AWS**: AWS was selected for cloud infrastructure hosting and deployment.\n",
            encoding="utf-8",
        )
        decisions = acc.parse_changelog_decisions(tmp_path / "CHANGELOG.md")
        assert len(decisions) == 2
        assert any("PostgreSQL" in d.title for d in decisions)

    def test_missing_changelog_returns_empty(self, tmp_path):
        """Test that missing CHANGELOG.md returns empty list."""
        decisions = acc.parse_changelog_decisions(tmp_path / "CHANGELOG.md")
        assert decisions == []

    def test_session_without_decisions_section(self, tmp_path):
        """Test that sessions without 'Decisions made' are skipped."""
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 001 -- 2025-01-01\n\n### Scope confirmed\nSetup project.\n",
            encoding="utf-8",
        )
        decisions = acc.parse_changelog_decisions(tmp_path / "CHANGELOG.md")
        assert decisions == []

    def test_decision_with_adr_reference_is_skipped(self, tmp_path):
        """Test that decisions whose title or body references an ADR are skipped.

        The regex at line 183 searches for 'ADR-NNN' in title + body.
        The title is captured from **title**, body from the text after colon.
        """
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 001 -- 2025-01-01\n\n"
            "### Decisions made\n\n"
            "- **Use PostgreSQL**: Chosen for ACID compliance, documented in ADR-001 for query performance.\n",
            encoding="utf-8",
        )
        decisions = acc.parse_changelog_decisions(tmp_path / "CHANGELOG.md")
        assert len(decisions) == 0

    def test_multiple_sessions_extracted(self, tmp_path):
        """Test that decisions are extracted from multiple sessions."""
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 001 -- 2025-01-01\n\n"
            "### Decisions made\n\n"
            "- **Choice A from first session**: We decided on approach alpha for the backend service.\n\n"
            "## Session 002 -- 2025-01-08\n\n"
            "### Decisions made\n\n"
            "- **Choice B from second session**: We decided on approach beta for the frontend rendering.\n",
            encoding="utf-8",
        )
        decisions = acc.parse_changelog_decisions(tmp_path / "CHANGELOG.md")
        assert len(decisions) == 2


# ---------------------------------------------------------------------------
# load_adrs — fallback title
# ---------------------------------------------------------------------------


class TestLoadAdrsExtended:
    """Extended tests for load_adrs covering the fallback title path."""

    def test_adr_without_standard_heading_uses_fallback(self, tmp_path):
        """Test that ADR without 'ADR-NNN:' heading falls back to any heading."""
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-custom.md").write_text(
            "# Custom Title Without ADR Prefix\n\nContent here.\n",
            encoding="utf-8",
        )
        adrs = acc.load_adrs(adr_dir)
        assert len(adrs) == 1
        assert adrs[0].title == "Custom Title Without ADR Prefix"

    def test_adr_without_any_heading_uses_stem(self, tmp_path):
        """Test that ADR without any heading uses filename stem as title."""
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-002-no-heading.md").write_text(
            "Just body text without any markdown heading.\n",
            encoding="utf-8",
        )
        adrs = acc.load_adrs(adr_dir)
        assert len(adrs) == 1
        assert adrs[0].title == "ADR-002-no-heading"


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------


class TestFormatText:
    """Tests for the format_text function."""

    def test_format_text_with_no_decisions(self):
        """Test format_text when no decisions or ADRs are found."""
        results = []
        adrs = []
        text = acc.format_text(results, adrs, Path("/tmp/repo"))
        assert "ADR Coverage Report" in text
        assert "All decisions have ADR coverage." in text

    def test_format_text_with_uncovered_decisions(self):
        """Test format_text shows uncovered decisions and recommendations."""
        decision = acc.Decision(
            "DECISIONS.md", "DEC-001", "Use Redis", "Cache layer for performance."
        )
        result = acc.CoverageResult(
            decision=decision,
            covered=False,
            covering_adrs=[],
            recommendation="Create docs/adr/ADR-NNN-use-redis.md",
        )
        text = acc.format_text([result], [], Path("/tmp/repo"))
        assert "Uncovered" in text
        assert "Use Redis" in text
        assert "Recommendation" in text

    def test_format_text_with_covered_decisions(self):
        """Test format_text shows covered decisions with ADR references."""
        decision = acc.Decision(
            "DECISIONS.md", "DEC-001", "Use PostgreSQL", "Storage layer."
        )
        result = acc.CoverageResult(
            decision=decision,
            covered=True,
            covering_adrs=["001"],
            recommendation="Covered by ADR-001.",
        )
        adr = acc.Adr("ADR-001.md", "001", "Use PostgreSQL", "Content.")
        text = acc.format_text([result], [adr], Path("/tmp/repo"))
        assert "ADR-001" in text
        assert "Covered" in text or "coverage" in text.lower()

    def test_format_text_with_adrs_listed(self):
        """Test format_text lists existing ADRs."""
        adr = acc.Adr("ADR-001.md", "001", "Use PostgreSQL", "Content.")
        text = acc.format_text([], [adr], Path("/tmp/repo"))
        assert "Existing ADRs" in text
        assert "ADR-001" in text


# ---------------------------------------------------------------------------
# check_coverage — explicit ADR reference
# ---------------------------------------------------------------------------


class TestCheckCoverageExtended:
    """Extended tests for check_coverage covering explicit ADR references."""

    def test_decision_with_explicit_adr_reference_is_covered(self):
        """Test that a decision body referencing ADR-001 is matched."""
        decision = acc.Decision(
            source="DECISIONS.md",
            identifier="DEC-001",
            title="Unique title xyz",
            body="This was documented in ADR-001 for compliance reasons.",
        )
        adr = acc.Adr(
            path="ADR-001.md",
            number="001",
            title="Completely different title abc",
            content="Different content about something else entirely.",
        )
        results = acc.check_coverage([decision], [adr])
        assert results[0].covered is True
        assert "001" in results[0].covering_adrs


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    """Tests for the CLI argument parser builder."""

    def test_build_parser_returns_parser(self):
        """Test that build_parser returns a valid ArgumentParser."""
        parser = acc.build_parser()
        assert parser is not None

    def test_parser_defaults(self):
        """Test parser default values."""
        parser = acc.build_parser()
        args = parser.parse_args([])
        assert args.repo_path == Path(".")
        assert args.threshold == "strict"
        assert args.output_format == "text"

    def test_parser_with_all_args(self):
        """Test parser with all arguments supplied."""
        parser = acc.build_parser()
        args = parser.parse_args(
            ["--repo-path", "/tmp/repo", "--threshold", "warn", "--format", "json"]
        )
        assert args.repo_path == Path("/tmp/repo")
        assert args.threshold == "warn"
        assert args.output_format == "json"
