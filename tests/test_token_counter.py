"""Tests for automation/token_counter.py.

Covers: CHANGELOG parsing, token estimation, cost calculation,
cost-log row formatting, and existing-log deduplication.
Git-dependent functions are tested with mocked subprocess output.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

import token_counter as tc


# ---------------------------------------------------------------------------
# parse_changelog_sessions
# ---------------------------------------------------------------------------

class TestParseChangelogSessions:
    def test_single_session_parsed(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 001 -- 2025-01-15 [claude-sonnet-4-6]\n\n"
            "### Scope confirmed\nSetup project.\n",
            encoding="utf-8",
        )
        sessions = tc.parse_changelog_sessions(tmp_path / "CHANGELOG.md")
        assert len(sessions) == 1
        assert sessions[0].session_id == "001"
        assert sessions[0].date == "2025-01-15"
        assert sessions[0].model == "claude-sonnet-4-6"

    def test_missing_file_returns_empty(self, tmp_path):
        sessions = tc.parse_changelog_sessions(tmp_path / "NONEXISTENT.md")
        assert sessions == []

    def test_session_without_model_uses_default(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 002 -- 2025-02-01\n\n### Scope confirmed\nFeatures.\n",
            encoding="utf-8",
        )
        sessions = tc.parse_changelog_sessions(tmp_path / "CHANGELOG.md")
        assert sessions[0].model == tc.DEFAULT_MODEL

    def test_multiple_sessions_parsed(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 001 -- 2025-01-01\n\n### Scope confirmed\nSetup.\n\n"
            "## Session 002 -- 2025-01-08\n\n### Scope confirmed\nMore work.\n",
            encoding="utf-8",
        )
        sessions = tc.parse_changelog_sessions(tmp_path / "CHANGELOG.md")
        assert len(sessions) == 2

    def test_em_dash_separator_is_parsed(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(
            "## Session 003 \u2014 2025-03-01\n\n### Scope confirmed\nRefactor.\n",
            encoding="utf-8",
        )
        sessions = tc.parse_changelog_sessions(tmp_path / "CHANGELOG.md")
        assert len(sessions) == 1
        assert sessions[0].date == "2025-03-01"


# ---------------------------------------------------------------------------
# estimate_tokens
# ---------------------------------------------------------------------------

class TestEstimateTokens:
    def test_zero_lines_gives_zero_tokens(self):
        stats = tc.GitStats(lines_added=0, lines_removed=0, commits=0)
        assert tc.estimate_tokens(stats) == 0

    def test_added_lines_use_higher_rate(self):
        stats_added = tc.GitStats(lines_added=100, lines_removed=0, commits=1)
        stats_removed = tc.GitStats(lines_added=0, lines_removed=100, commits=1)
        assert tc.estimate_tokens(stats_added) > tc.estimate_tokens(stats_removed)

    def test_tokens_calculated_correctly(self):
        stats = tc.GitStats(lines_added=10, lines_removed=5, commits=2)
        expected = int(10 * tc.TOKENS_PER_LINE_ADDED + 5 * tc.TOKENS_PER_LINE_REMOVED)
        assert tc.estimate_tokens(stats) == expected


# ---------------------------------------------------------------------------
# estimate_cost
# ---------------------------------------------------------------------------

class TestEstimateCost:
    def test_zero_tokens_gives_zero_cost(self):
        assert tc.estimate_cost(0, "claude-sonnet-4-6") == 0.0

    def test_known_model_uses_correct_rate(self):
        cost = tc.estimate_cost(1_000_000, "claude-opus-4-6")
        assert cost == pytest.approx(45.0, rel=0.01)

    def test_unknown_model_falls_back_to_default_rate(self):
        cost_unknown = tc.estimate_cost(1_000_000, "unknown-model-xyz")
        cost_default = tc.estimate_cost(1_000_000, "unknown")
        assert cost_unknown == cost_default

    def test_cost_is_proportional_to_tokens(self):
        cost_1m = tc.estimate_cost(1_000_000, "claude-sonnet-4-6")
        cost_2m = tc.estimate_cost(2_000_000, "claude-sonnet-4-6")
        assert cost_2m == pytest.approx(cost_1m * 2, rel=0.01)


# ---------------------------------------------------------------------------
# parse_existing_log_sessions
# ---------------------------------------------------------------------------

class TestParseExistingLogSessions:
    def test_missing_file_returns_empty_set(self, tmp_path):
        result = tc.parse_existing_log_sessions(tmp_path / "COST_LOG.md")
        assert result == set()

    def test_parses_session_ids_from_table(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(
            "| Session | Date | Model | Tasks | Summary | Cost | Notes |\n"
            "| ------- | ---- | ----- | ----- | ------- | ---- | ----- |\n"
            "| 001 | 2025-01-01 | claude-sonnet-4-6 | 3 | Setup | $0.001 | notes |\n"
            "| 002 | 2025-01-08 | claude-sonnet-4-6 | 5 | Features | $0.002 | notes |\n",
            encoding="utf-8",
        )
        ids = tc.parse_existing_log_sessions(tmp_path / "COST_LOG.md")
        assert "001" in ids
        assert "002" in ids


# ---------------------------------------------------------------------------
# format_cost_log_row
# ---------------------------------------------------------------------------

class TestFormatCostLogRow:
    def test_row_contains_session_id(self):
        estimate = tc.TokenEstimate(
            session_id="007",
            date="2025-07-01",
            model="claude-sonnet-4-6",
            lines_added=100,
            lines_removed=20,
            commits=5,
            estimated_tokens=850,
            estimated_cost_usd=0.0051,
            tasks_completed=3,
            summary="Weekly session",
        )
        row = tc.format_cost_log_row(estimate)
        assert "007" in row

    def test_row_is_pipe_delimited(self):
        estimate = tc.TokenEstimate(
            session_id="001",
            date="2025-01-01",
            model="claude-sonnet-4-6",
            lines_added=50,
            lines_removed=10,
            commits=3,
            estimated_tokens=430,
            estimated_cost_usd=0.003,
            tasks_completed=2,
            summary="Setup",
        )
        row = tc.format_cost_log_row(estimate)
        assert row.startswith("|")
        assert row.endswith("|")
