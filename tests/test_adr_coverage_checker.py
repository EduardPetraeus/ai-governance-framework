"""Tests for automation/adr_coverage_checker.py.

Covers: keyword extraction, decision parsing (CHANGELOG and DECISIONS.md),
ADR loading, coverage checking, and the run() entry point.
"""

from pathlib import Path

import pytest

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
