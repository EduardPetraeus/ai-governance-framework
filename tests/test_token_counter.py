"""Tests for automation/token_counter.py.

Covers: CHANGELOG parsing, token estimation, cost calculation,
cost-log row formatting, and existing-log deduplication.
Git-dependent functions are tested with mocked subprocess output.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

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


# ---------------------------------------------------------------------------
# run_git
# ---------------------------------------------------------------------------

class TestRunGit:
    """Tests for the run_git function wrapping subprocess."""

    @patch("token_counter.subprocess.run")
    def test_run_git_returns_stdout(self, mock_run, tmp_path):
        """Test that run_git returns subprocess stdout on success."""
        mock_run.return_value = MagicMock(returncode=0, stdout="output\n", stderr="")
        result = tc.run_git(["status"], tmp_path)
        assert result == "output\n"

    @patch("token_counter.subprocess.run")
    def test_run_git_raises_on_failure(self, mock_run, tmp_path):
        """Test that run_git raises RuntimeError when git fails."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="fatal: bad revision")
        with pytest.raises(RuntimeError, match="failed"):
            tc.run_git(["log"], tmp_path)


# ---------------------------------------------------------------------------
# get_git_stats_for_date
# ---------------------------------------------------------------------------

class TestGetGitStatsForDate:
    """Tests for get_git_stats_for_date with mocked git output."""

    @patch("token_counter.run_git")
    def test_parses_numstat_output(self, mock_run_git):
        """Test parsing of git log --numstat output into GitStats."""
        mock_run_git.return_value = (
            "COMMIT\n"
            "10\t5\tsrc/main.py\n"
            "20\t3\tsrc/utils.py\n"
            "COMMIT\n"
            "5\t2\ttests/test_main.py\n"
        )
        stats = tc.get_git_stats_for_date("2025-01-01", Path("/tmp"))
        assert stats.lines_added == 35
        assert stats.lines_removed == 10
        assert stats.commits == 2

    @patch("token_counter.run_git")
    def test_binary_files_handled(self, mock_run_git):
        """Test that binary files (shown as - in numstat) are handled."""
        mock_run_git.return_value = (
            "COMMIT\n"
            "-\t-\timage.png\n"
            "5\t2\tsrc/main.py\n"
        )
        stats = tc.get_git_stats_for_date("2025-01-01", Path("/tmp"))
        assert stats.lines_added == 5
        assert stats.lines_removed == 2

    @patch("token_counter.run_git")
    def test_runtime_error_returns_empty_stats(self, mock_run_git):
        """Test that a git error returns empty stats instead of crashing."""
        mock_run_git.side_effect = RuntimeError("git failed")
        stats = tc.get_git_stats_for_date("2025-01-01", Path("/tmp"))
        assert stats.lines_added == 0
        assert stats.lines_removed == 0
        assert stats.commits == 0

    @patch("token_counter.run_git")
    def test_empty_output_returns_zero_stats(self, mock_run_git):
        """Test that empty git output returns zero stats."""
        mock_run_git.return_value = ""
        stats = tc.get_git_stats_for_date("2025-01-01", Path("/tmp"))
        assert stats.lines_added == 0
        assert stats.commits == 0

    @patch("token_counter.run_git")
    def test_invalid_numstat_values_skipped(self, mock_run_git):
        """Test that non-integer numstat values trigger ValueError and are skipped."""
        mock_run_git.return_value = (
            "COMMIT\n"
            "abc\tdef\tsrc/main.py\n"
            "10\t5\tsrc/utils.py\n"
        )
        stats = tc.get_git_stats_for_date("2025-01-01", Path("/tmp"))
        assert stats.lines_added == 10
        assert stats.lines_removed == 5
        assert stats.commits == 1


# ---------------------------------------------------------------------------
# append_to_cost_log
# ---------------------------------------------------------------------------

class TestAppendToCostLog:
    """Tests for the append_to_cost_log function."""

    def test_append_to_existing_table(self, tmp_path):
        """Test that rows are inserted after the table header separator."""
        cost_log = tmp_path / "COST_LOG.md"
        cost_log.write_text(
            "# Cost Log\n\n"
            "| Session | Date | Model | Tasks | Summary | Cost | Notes |\n"
            "| ------- | ---- | ----- | ----- | ------- | ---- | ----- |\n"
            "| 001 | 2025-01-01 | model | 1 | Test | $0.001 | notes |\n",
            encoding="utf-8",
        )
        rows = ["| 002 | 2025-01-08 | model | 2 | More | $0.002 | notes |"]
        tc.append_to_cost_log(cost_log, rows)
        content = cost_log.read_text()
        assert "002" in content
        # New row should appear between header separator and existing row
        lines = content.splitlines()
        idx_002 = next(i for i, l in enumerate(lines) if "002" in l)
        idx_001 = next(i for i, l in enumerate(lines) if "001" in l)
        assert idx_002 < idx_001

    def test_missing_cost_log_warns(self, tmp_path, capsys):
        """Test that missing COST_LOG.md prints a warning."""
        tc.append_to_cost_log(tmp_path / "COST_LOG.md", ["row"])
        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_no_table_header_appends_at_end(self, tmp_path, capsys):
        """Test that rows are appended at end when no table header is found."""
        cost_log = tmp_path / "COST_LOG.md"
        cost_log.write_text("# Cost Log\n\nNo table here.\n", encoding="utf-8")
        rows = ["| 001 | date | model | 1 | test | $0 | notes |"]
        tc.append_to_cost_log(cost_log, rows)
        content = cost_log.read_text()
        assert "001" in content
        captured = capsys.readouterr()
        assert "Could not locate" in captured.err


# ---------------------------------------------------------------------------
# compute_estimates
# ---------------------------------------------------------------------------

class TestComputeEstimates:
    """Tests for compute_estimates combining sessions with git stats."""

    @patch("token_counter.get_git_stats_for_date")
    def test_new_sessions_are_estimated(self, mock_stats):
        """Test that sessions not in existing_ids are estimated."""
        mock_stats.return_value = tc.GitStats(lines_added=100, lines_removed=20, commits=3)
        sessions = [
            tc.SessionInfo(session_id="001", date="2025-01-01", model="claude-sonnet-4-6", summary="Setup"),
            tc.SessionInfo(session_id="002", date="2025-01-08", model="claude-sonnet-4-6", summary="Features"),
        ]
        existing = {"001"}
        estimates = tc.compute_estimates(sessions, existing, Path("/tmp"))
        assert len(estimates) == 1
        assert estimates[0].session_id == "002"

    @patch("token_counter.get_git_stats_for_date")
    def test_all_sessions_already_logged(self, mock_stats):
        """Test that no estimates are returned when all sessions are logged."""
        sessions = [
            tc.SessionInfo(session_id="001", date="2025-01-01", model="claude-sonnet-4-6", summary="Setup"),
        ]
        existing = {"001"}
        estimates = tc.compute_estimates(sessions, existing, Path("/tmp"))
        assert estimates == []

    @patch("token_counter.get_git_stats_for_date")
    def test_estimate_fields_are_populated(self, mock_stats):
        """Test that all TokenEstimate fields are correctly populated."""
        mock_stats.return_value = tc.GitStats(lines_added=50, lines_removed=10, commits=2)
        sessions = [
            tc.SessionInfo(session_id="003", date="2025-02-01", model="claude-opus-4-6", summary="Refactor", tasks_completed=5),
        ]
        estimates = tc.compute_estimates(sessions, set(), Path("/tmp"))
        assert len(estimates) == 1
        est = estimates[0]
        assert est.session_id == "003"
        assert est.model == "claude-opus-4-6"
        assert est.lines_added == 50
        assert est.lines_removed == 10
        assert est.commits == 2
        assert est.tasks_completed == 5
        assert est.estimated_tokens > 0
        assert est.estimated_cost_usd > 0


# ---------------------------------------------------------------------------
# run — main entry point
# ---------------------------------------------------------------------------

class TestRunFunction:
    """Tests for the run() main entry point."""

    def test_run_no_sessions_returns_zero(self, tmp_path, capsys):
        """Test that run() returns 0 when no sessions found in CHANGELOG."""
        code = tc.run(tmp_path)
        assert code == 0
        captured = capsys.readouterr()
        assert "No sessions found" in captured.err

    @patch("token_counter.compute_estimates")
    @patch("token_counter.parse_existing_log_sessions")
    @patch("token_counter.parse_changelog_sessions")
    def test_run_all_logged_text_format(self, mock_parse, mock_existing, mock_compute, tmp_path, capsys):
        """Test run() when all sessions already logged (text format)."""
        mock_parse.return_value = [tc.SessionInfo("001", "2025-01-01", "sonnet", "Test")]
        mock_existing.return_value = {"001"}
        mock_compute.return_value = []
        code = tc.run(tmp_path, output_format="text")
        assert code == 0
        captured = capsys.readouterr()
        assert "already recorded" in captured.out

    @patch("token_counter.compute_estimates")
    @patch("token_counter.parse_existing_log_sessions")
    @patch("token_counter.parse_changelog_sessions")
    def test_run_all_logged_json_format(self, mock_parse, mock_existing, mock_compute, tmp_path, capsys):
        """Test run() when all sessions already logged (JSON format)."""
        mock_parse.return_value = [tc.SessionInfo("001", "2025-01-01", "sonnet", "Test")]
        mock_existing.return_value = {"001"}
        mock_compute.return_value = []
        code = tc.run(tmp_path, output_format="json")
        assert code == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["new_entries"] == 0

    @patch("token_counter.append_to_cost_log")
    @patch("token_counter.compute_estimates")
    @patch("token_counter.parse_existing_log_sessions")
    @patch("token_counter.parse_changelog_sessions")
    def test_run_with_new_estimates_text(self, mock_parse, mock_existing, mock_compute, mock_append, tmp_path, capsys):
        """Test run() with new estimates in text format."""
        mock_parse.return_value = [tc.SessionInfo("001", "2025-01-01", "claude-sonnet-4-6", "Setup")]
        mock_existing.return_value = set()
        mock_compute.return_value = [
            tc.TokenEstimate("001", "2025-01-01", "claude-sonnet-4-6", 100, 20, 3, 860, 0.005, 2, "Setup")
        ]
        code = tc.run(tmp_path, output_format="text")
        assert code == 0
        captured = capsys.readouterr()
        assert "New sessions to log" in captured.out
        assert "001" in captured.out
        mock_append.assert_called_once()

    @patch("token_counter.append_to_cost_log")
    @patch("token_counter.compute_estimates")
    @patch("token_counter.parse_existing_log_sessions")
    @patch("token_counter.parse_changelog_sessions")
    def test_run_with_new_estimates_json(self, mock_parse, mock_existing, mock_compute, mock_append, tmp_path, capsys):
        """Test run() with new estimates in JSON format."""
        mock_parse.return_value = [tc.SessionInfo("001", "2025-01-01", "claude-sonnet-4-6", "Setup")]
        mock_existing.return_value = set()
        mock_compute.return_value = [
            tc.TokenEstimate("001", "2025-01-01", "claude-sonnet-4-6", 100, 20, 3, 860, 0.005, 2, "Setup")
        ]
        code = tc.run(tmp_path, output_format="json")
        assert code == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["new_entries"] == 1
        assert len(parsed["estimates"]) == 1

    @patch("token_counter.compute_estimates")
    @patch("token_counter.parse_existing_log_sessions")
    @patch("token_counter.parse_changelog_sessions")
    def test_run_dry_run_does_not_append(self, mock_parse, mock_existing, mock_compute, tmp_path, capsys):
        """Test that dry_run=True does not modify COST_LOG.md."""
        mock_parse.return_value = [tc.SessionInfo("001", "2025-01-01", "claude-sonnet-4-6", "Setup")]
        mock_existing.return_value = set()
        mock_compute.return_value = [
            tc.TokenEstimate("001", "2025-01-01", "claude-sonnet-4-6", 100, 20, 3, 860, 0.005, 2, "Setup")
        ]
        code = tc.run(tmp_path, dry_run=True, output_format="text")
        assert code == 0
        captured = capsys.readouterr()
        assert "Dry run" in captured.out


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    """Tests for the CLI argument parser builder."""

    def test_build_parser_returns_parser(self):
        """Test that build_parser returns a valid ArgumentParser."""
        parser = tc.build_parser()
        assert parser is not None

    def test_parser_defaults(self):
        """Test parser default values."""
        parser = tc.build_parser()
        args = parser.parse_args([])
        assert args.repo_path == Path(".")
        assert args.dry_run is False
        assert args.output_format == "text"

    def test_parser_with_all_args(self):
        """Test parser with all arguments supplied."""
        parser = tc.build_parser()
        args = parser.parse_args(["--repo-path", "/tmp/repo", "--dry-run", "--format", "json"])
        assert args.repo_path == Path("/tmp/repo")
        assert args.dry_run is True
        assert args.output_format == "json"
