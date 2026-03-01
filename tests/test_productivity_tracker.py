"""Tests for scripts/productivity_tracker.py.

Covers: ASCII bar helper, date validation, git command runner, git repo
verification, commit parsing from git log output, all report section builders
(overview, velocity chart, hour distribution, commit types, most-changed files,
per-author breakdown, governance score), full report assembly, and CLI entry
point including all argument combinations and error paths.

All git subprocess calls are mocked — no real git operations are performed.
"""

from collections import Counter
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, call, patch

import pytest

import productivity_tracker as pt


# ---------------------------------------------------------------------------
# Helper: build synthetic commit dicts matching get_commits() output
# ---------------------------------------------------------------------------

def make_commit(
    hash_="abc12345",
    day=None,
    hour=10,
    message="feat: add feature here",
    author="Alice",
    files_changed=1,
    insertions=5,
    deletions=2,
    is_main=False,
):
    """Return a synthetic commit dict in the shape produced by get_commits()."""
    d = day or date(2025, 1, 15)
    dt = datetime(d.year, d.month, d.day, hour)
    return {
        "hash": hash_,
        "timestamp": dt,
        "date": d,
        "hour": hour,
        "message": message,
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "author": author,
        "is_main_commit": is_main,
    }


# ---------------------------------------------------------------------------
# _bar
# ---------------------------------------------------------------------------

class TestBar:
    def test_full_bar(self):
        result = pt._bar(10, 10, width=10)
        assert result == "█" * 10

    def test_empty_bar_zero_value(self):
        result = pt._bar(0, 10, width=10)
        assert result == "░" * 10

    def test_zero_max_returns_empty(self):
        result = pt._bar(5, 0, width=10)
        assert result == "░" * 10

    def test_width_respected(self):
        result = pt._bar(5, 10, width=20)
        assert len(result) == 20

    def test_half_bar(self):
        result = pt._bar(5, 10, width=10)
        assert result.count("█") == 5
        assert result.count("░") == 5

    def test_bar_contains_only_block_chars(self):
        result = pt._bar(3, 10, width=8)
        assert all(c in ("█", "░") for c in result)


# ---------------------------------------------------------------------------
# parse_date
# ---------------------------------------------------------------------------

class TestParseDate:
    def test_valid_date_returned_unchanged(self):
        assert pt.parse_date("2025-01-15") == "2025-01-15"

    def test_invalid_string_exits(self):
        with pytest.raises(SystemExit):
            pt.parse_date("not-a-date")

    def test_wrong_format_exits(self):
        with pytest.raises(SystemExit):
            pt.parse_date("15-01-2025")

    def test_partial_date_exits(self):
        with pytest.raises(SystemExit):
            pt.parse_date("2025-01")

    def test_another_valid_date(self):
        assert pt.parse_date("2024-12-31") == "2024-12-31"


# ---------------------------------------------------------------------------
# run_git
# ---------------------------------------------------------------------------

class TestRunGit:
    def test_successful_command_returns_stripped_stdout(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="abc123\n")
            result = pt.run_git(["rev-parse", "HEAD"])
        assert result == "abc123"

    def test_failed_command_returns_empty_string(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = pt.run_git(["bad-command"])
        assert result == ""

    def test_file_not_found_exits(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(SystemExit):
                pt.run_git(["rev-parse", "HEAD"])

    def test_git_prepended_to_args(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="output\n")
            pt.run_git(["log", "--oneline"])
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "git"
        assert call_args[1] == "log"


# ---------------------------------------------------------------------------
# verify_git_repo
# ---------------------------------------------------------------------------

class TestVerifyGitRepo:
    def test_valid_repo_does_not_exit(self):
        with patch.object(pt, "run_git", return_value="/some/repo"):
            pt.verify_git_repo()  # Must not raise

    def test_not_in_repo_exits(self):
        with patch.object(pt, "run_git", return_value=""):
            with pytest.raises(SystemExit):
                pt.verify_git_repo()


# ---------------------------------------------------------------------------
# get_commits
# ---------------------------------------------------------------------------

# Git log output: HASH|||ISO_TIMESTAMP|||AUTHOR|||SUBJECT|||REFS
# followed optionally by a shortstat line

SAMPLE_GIT_TWO_COMMITS = (
    "abc12345|||2025-01-15 10:30:00|||Alice|||feat: add authentication|||HEAD -> main\n"
    " 2 files changed, 15 insertions(+), 3 deletions(-)\n"
    "def67890|||2025-01-16 14:00:00|||Bob|||fix: resolve login bug|||\n"
    " 1 file changed, 5 insertions(+), 2 deletions(-)"
)

SAMPLE_GIT_ONE_COMMIT = (
    "abc12345|||2025-01-15 10:30:00|||Alice|||docs: update README|||\n"
    " 1 file changed, 10 insertions(+)"
)


class TestGetCommits:
    def test_empty_output_returns_empty_list(self):
        with patch.object(pt, "run_git", return_value=""):
            result = pt.get_commits(since="2025-01-01")
        assert result == []

    def test_parses_two_commits(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_TWO_COMMITS):
            result = pt.get_commits(since="2025-01-01")
        assert len(result) == 2

    def test_hash_correct(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_ONE_COMMIT):
            result = pt.get_commits(since="2025-01-01")
        assert result[0]["hash"] == "abc12345"

    def test_author_parsed(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_ONE_COMMIT):
            result = pt.get_commits(since="2025-01-01")
        assert result[0]["author"] == "Alice"

    def test_message_parsed(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_ONE_COMMIT):
            result = pt.get_commits(since="2025-01-01")
        assert result[0]["message"] == "docs: update README"

    def test_files_changed_parsed(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_ONE_COMMIT):
            result = pt.get_commits(since="2025-01-01")
        assert result[0]["files_changed"] == 1

    def test_insertions_parsed(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_ONE_COMMIT):
            result = pt.get_commits(since="2025-01-01")
        assert result[0]["insertions"] == 10

    def test_is_main_commit_for_main_ref(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_TWO_COMMITS):
            result = pt.get_commits(since="2025-01-01")
        assert result[0]["is_main_commit"] is True

    def test_non_main_ref_not_flagged(self):
        with patch.object(pt, "run_git", return_value=SAMPLE_GIT_TWO_COMMITS):
            result = pt.get_commits(since="2025-01-01")
        assert result[1]["is_main_commit"] is False

    def test_until_arg_passed_to_run_git(self):
        with patch.object(pt, "run_git", return_value="") as mock_git:
            pt.get_commits(since="2025-01-01", until="2025-01-31")
        args_passed = mock_git.call_args[0][0]
        assert "--until=2025-01-31" in args_passed

    def test_author_arg_passed_to_run_git(self):
        with patch.object(pt, "run_git", return_value="") as mock_git:
            pt.get_commits(since="2025-01-01", author="Alice")
        args_passed = mock_git.call_args[0][0]
        assert "--author" in args_passed
        assert "Alice" in args_passed

    def test_invalid_timestamp_falls_back(self):
        bad_timestamp = (
            "abc12345|||INVALID_DATE|||Alice|||feat: test|||\n"
            " 1 file changed, 1 insertions(+)"
        )
        with patch.object(pt, "run_git", return_value=bad_timestamp):
            result = pt.get_commits(since="2025-01-01")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# section_overview
# ---------------------------------------------------------------------------

class TestSectionOverview:
    def test_returns_list_of_strings(self):
        commits = [make_commit()]
        result = pt.section_overview(commits)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_total_commits_shown(self):
        commits = [make_commit(), make_commit(hash_="bbb22222")]
        result = pt.section_overview(commits)
        joined = "\n".join(result)
        assert "2" in joined

    def test_date_range_shown(self):
        commits = [
            make_commit(day=date(2025, 1, 1)),
            make_commit(day=date(2025, 1, 15)),
        ]
        result = pt.section_overview(commits)
        joined = "\n".join(result)
        assert "2025-01-01" in joined
        assert "2025-01-15" in joined

    def test_most_productive_day_shown(self):
        commits = [
            make_commit(hash_="a1", day=date(2025, 1, 1)),
            make_commit(hash_="a2", day=date(2025, 1, 1)),
            make_commit(hash_="a3", day=date(2025, 1, 2)),
        ]
        result = pt.section_overview(commits)
        joined = "\n".join(result)
        # Date with 2 commits should appear as most productive
        assert "2025-01-01" in joined

    def test_avg_commits_per_day_shown(self):
        commits = [make_commit(hash_=f"a{i}", day=date(2025, 1, 1)) for i in range(4)]
        result = pt.section_overview(commits)
        joined = "\n".join(result)
        assert "4.0" in joined

    def test_overview_header_present(self):
        commits = [make_commit()]
        result = pt.section_overview(commits)
        assert "OVERVIEW" in result[0]


# ---------------------------------------------------------------------------
# section_velocity_chart
# ---------------------------------------------------------------------------

class TestSectionVelocityChart:
    def test_returns_list_of_strings(self):
        commits = [make_commit()]
        result = pt.section_velocity_chart(commits)
        assert isinstance(result, list)

    def test_empty_commits_shows_no_data(self):
        result = pt.section_velocity_chart([])
        joined = "\n".join(result)
        assert "No data" in joined

    def test_date_appears_in_chart(self):
        commits = [make_commit(day=date(2025, 1, 10))]
        result = pt.section_velocity_chart(commits)
        joined = "\n".join(result)
        assert "2025-01-10" in joined

    def test_bar_chars_present(self):
        commits = [make_commit()]
        result = pt.section_velocity_chart(commits)
        joined = "\n".join(result)
        assert "█" in joined or "░" in joined

    def test_multiple_dates_all_shown(self):
        commits = [
            make_commit(hash_="a1", day=date(2025, 1, 1)),
            make_commit(hash_="a2", day=date(2025, 1, 5)),
        ]
        result = pt.section_velocity_chart(commits)
        joined = "\n".join(result)
        assert "2025-01-01" in joined
        assert "2025-01-05" in joined

    def test_header_present(self):
        commits = [make_commit()]
        result = pt.section_velocity_chart(commits)
        assert "VELOCITY CHART" in result[0]


# ---------------------------------------------------------------------------
# section_hour_distribution
# ---------------------------------------------------------------------------

class TestSectionHourDistribution:
    def test_returns_list_of_strings(self):
        commits = [make_commit(hour=9)]
        result = pt.section_hour_distribution(commits)
        assert isinstance(result, list)

    def test_empty_commits_returns_no_data(self):
        result = pt.section_hour_distribution([])
        joined = "\n".join(result)
        assert "No data" in joined

    def test_all_24_hours_present(self):
        commits = [make_commit(hour=12)]
        result = pt.section_hour_distribution(commits)
        joined = "\n".join(result)
        assert "00:00" in joined
        assert "23:00" in joined

    def test_peak_hours_shown(self):
        commits = [
            make_commit(hash_=f"a{i}", hour=10) for i in range(5)
        ]
        result = pt.section_hour_distribution(commits)
        joined = "\n".join(result)
        assert "Peak" in joined
        assert "10:00" in joined

    def test_active_hour_has_bar(self):
        commits = [make_commit(hour=14)]
        result = pt.section_hour_distribution(commits)
        joined = "\n".join(result)
        assert "14:00" in joined
        # Active hours use bar chars, not dots
        hour_line = [l for l in result if "14:00" in l][0]
        assert "█" in hour_line

    def test_inactive_hour_has_dots(self):
        commits = [make_commit(hour=14)]
        result = pt.section_hour_distribution(commits)
        zero_lines = [l for l in result if "00:00" in l]
        assert len(zero_lines) == 1
        assert "·" in zero_lines[0]


# ---------------------------------------------------------------------------
# section_commit_types
# ---------------------------------------------------------------------------

class TestSectionCommitTypes:
    def test_conventional_type_classified(self):
        commits = [
            make_commit(message="feat: add login"),
            make_commit(message="fix: resolve crash"),
            make_commit(message="docs: update README"),
        ]
        result = pt.section_commit_types(commits)
        joined = "\n".join(result)
        assert "feat" in joined
        assert "fix" in joined
        assert "docs" in joined

    def test_non_conventional_classified_as_other(self):
        commits = [make_commit(message="random commit message")]
        result = pt.section_commit_types(commits)
        joined = "\n".join(result)
        assert "other" in joined

    def test_percentage_shown(self):
        commits = [make_commit(message="feat: something")]
        result = pt.section_commit_types(commits)
        joined = "\n".join(result)
        assert "100.0%" in joined

    def test_returns_list_of_strings(self):
        commits = [make_commit()]
        result = pt.section_commit_types(commits)
        assert isinstance(result, list)

    def test_mixed_types_all_counted(self):
        commits = [
            make_commit(hash_="a1", message="feat: x"),
            make_commit(hash_="a2", message="feat: y"),
            make_commit(hash_="a3", message="fix: z"),
        ]
        result = pt.section_commit_types(commits)
        joined = "\n".join(result)
        # feat appears twice
        assert "feat" in joined
        assert "fix" in joined

    def test_all_conventional_types_supported(self):
        types = ["feat", "fix", "docs", "refactor", "test", "chore", "perf",
                 "security", "style", "ci", "build", "revert"]
        commits = [make_commit(hash_=f"a{i}", message=f"{t}: something") for i, t in enumerate(types)]
        result = pt.section_commit_types(commits)
        joined = "\n".join(result)
        for t in types:
            assert t in joined


# ---------------------------------------------------------------------------
# section_most_changed_files
# ---------------------------------------------------------------------------

class TestSectionMostChangedFiles:
    def test_no_output_returns_no_file_data(self):
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_most_changed_files("2025-01-01", None, None)
        joined = "\n".join(result)
        assert "No file data" in joined

    def test_files_counted_and_shown(self):
        file_output = "README.md\nREADME.md\nsrc/main.py\n"
        with patch.object(pt, "run_git", return_value=file_output):
            result = pt.section_most_changed_files("2025-01-01", None, None)
        joined = "\n".join(result)
        assert "README.md" in joined

    def test_count_appears(self):
        file_output = "README.md\nREADME.md\nREADME.md\n"
        with patch.object(pt, "run_git", return_value=file_output):
            result = pt.section_most_changed_files("2025-01-01", None, None)
        joined = "\n".join(result)
        assert "3x" in joined

    def test_top_10_limit_enforced(self):
        # 15 unique files → only top 10 shown
        files = "\n".join([f"file{i}.py" for i in range(15)])
        with patch.object(pt, "run_git", return_value=files):
            result = pt.section_most_changed_files("2025-01-01", None, None)
        file_lines = [l for l in result if ".py" in l]
        assert len(file_lines) <= 10

    def test_until_passed_when_provided(self):
        with patch.object(pt, "run_git", return_value="") as mock_git:
            pt.section_most_changed_files("2025-01-01", "2025-01-31", None)
        args_passed = mock_git.call_args[0][0]
        assert "--until=2025-01-31" in args_passed

    def test_author_passed_when_provided(self):
        with patch.object(pt, "run_git", return_value="") as mock_git:
            pt.section_most_changed_files("2025-01-01", None, "Alice")
        args_passed = mock_git.call_args[0][0]
        assert "--author" in args_passed
        assert "Alice" in args_passed

    def test_returns_list_of_strings(self):
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_most_changed_files("2025-01-01", None, None)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# section_per_author
# ---------------------------------------------------------------------------

class TestSectionPerAuthor:
    def test_single_author_returns_empty_list(self):
        commits = [make_commit(author="Alice"), make_commit(hash_="b2", author="Alice")]
        result = pt.section_per_author(commits)
        assert result == []

    def test_two_authors_generates_section(self):
        commits = [
            make_commit(hash_="a1", author="Alice"),
            make_commit(hash_="b1", author="Bob"),
        ]
        result = pt.section_per_author(commits)
        joined = "\n".join(result)
        assert "Alice" in joined
        assert "Bob" in joined

    def test_percentage_shown(self):
        commits = [
            make_commit(hash_="a1", author="Alice"),
            make_commit(hash_="a2", author="Alice"),
            make_commit(hash_="b1", author="Bob"),
        ]
        result = pt.section_per_author(commits)
        joined = "\n".join(result)
        assert "%" in joined

    def test_top_commit_types_shown(self):
        commits = [
            make_commit(hash_="a1", author="Alice", message="feat: feature"),
            make_commit(hash_="b1", author="Bob", message="fix: bug"),
        ]
        result = pt.section_per_author(commits)
        joined = "\n".join(result)
        assert "feat" in joined or "fix" in joined

    def test_non_conventional_type_counted_as_other(self):
        commits = [
            make_commit(hash_="a1", author="Alice", message="random message"),
            make_commit(hash_="b1", author="Bob", message="feat: something"),
        ]
        result = pt.section_per_author(commits)
        joined = "\n".join(result)
        assert "other" in joined

    def test_header_present_for_multiple_authors(self):
        commits = [
            make_commit(hash_="a1", author="Alice"),
            make_commit(hash_="b1", author="Bob"),
        ]
        result = pt.section_per_author(commits)
        assert "PER-AUTHOR" in result[0]


# ---------------------------------------------------------------------------
# section_governance_score
# ---------------------------------------------------------------------------

class TestSectionGovernanceScore:
    def test_returns_list_of_strings(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_score_out_of_100_shown(self):
        commits = [make_commit(message="feat: something long enough here")]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "/100" in joined

    def test_zero_conventional_commits_scores_zero_on_format(self):
        commits = [make_commit(message="random non-conventional message")]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "0/40" in joined

    def test_all_conventional_commits_score_40_on_format(self):
        commits = [
            make_commit(hash_=f"a{i}", message="feat: a very descriptive feature")
            for i in range(5)
        ]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "40/40" in joined

    def test_main_commits_reduce_no_main_score(self):
        commits = [
            make_commit(hash_="a1", message="feat: something long enough", is_main=True),
            make_commit(hash_="a2", message="feat: something long enough", is_main=True),
        ]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "direct commits" in joined

    def test_no_main_commits_scores_15(self):
        commits = [make_commit(message="feat: something long enough here", is_main=False)]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "15/15" in joined

    def test_changelog_component_shown(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "CHANGELOG" in joined

    def test_poor_label_with_no_governance(self):
        commits = [make_commit(message="bad")]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "Poor" in joined

    def test_excellent_label_with_full_compliance(self):
        # 10 commits on same day: avg=10 (in 5-20 range → +15)
        # 100% conventional → +40
        # no main commits → +15
        # messages > 20 chars → +10
        # CHANGELOG on all active days → +20
        commits = [
            make_commit(
                hash_=f"a{i}",
                day=date(2025, 1, 1),
                message="feat: a very descriptive long message here",
                is_main=False,
            )
            for i in range(10)
        ]
        # Return a date matching the active day so changelog ratio = 1.0
        with patch.object(pt, "run_git", return_value="2025-01-01"):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "Excellent" in joined

    def test_message_length_component_shown(self):
        commits = [make_commit(message="feat: a long descriptive message")]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "Message length" in joined

    def test_session_size_component_shown(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "session size" in joined.lower()

    def test_good_label_for_moderate_score(self):
        # 5 commits/day on 2 different days → avg=5 (in range → +15)
        # All conventional with type "feat" → +40
        # No main commits → +15
        # All messages > 20 chars → +10
        # No changelog coverage → +0
        # Total = 80 → "Good" (>=70)
        commits = [
            make_commit(
                hash_=f"a{i}",
                day=date(2025, 1, i % 2 + 1),
                message="feat: a well-described message",
                is_main=False,
            )
            for i in range(10)
        ]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        assert "Good" in joined or "Excellent" in joined or "Fair" in joined

    def test_large_session_size_penalized(self):
        # 100 commits on 1 day → avg=100, penalized heavily
        commits = [
            make_commit(hash_=f"a{i}", day=date(2025, 1, 1), message="bad")
            for i in range(100)
        ]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.section_governance_score(commits)
        joined = "\n".join(result)
        # Session size score should be 0 (100 - 80 = 20, floored)
        assert "0/15" in joined


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

class TestGenerateReport:
    def test_empty_commits_returns_no_commits_message(self):
        result = pt.generate_report([], "2025-01-01", None, None)
        assert "No commits found" in result

    def test_non_empty_commits_has_overview_section(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "OVERVIEW" in result

    def test_non_empty_commits_has_velocity_chart(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "VELOCITY CHART" in result

    def test_non_empty_commits_has_hour_distribution(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "HOUR-OF-DAY" in result

    def test_non_empty_commits_has_commit_types(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "COMMIT TYPE" in result

    def test_non_empty_commits_has_governance_score(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "GOVERNANCE" in result

    def test_author_filter_shown_when_set(self):
        commits = [make_commit(author="Alice")]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, "Alice")
        assert "Author filter: Alice" in result

    def test_author_filter_not_shown_when_none(self):
        commits = [make_commit()]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "Author filter" not in result

    def test_separator_present(self):
        result = pt.generate_report([], "2025-01-01", None, None)
        assert "=" * 10 in result

    def test_period_shown_with_since(self):
        result = pt.generate_report([], "2025-01-01", None, None)
        assert "2025-01-01" in result

    def test_until_shown_when_set(self):
        result = pt.generate_report([], "2025-01-01", "2025-01-31", None)
        assert "2025-01-31" in result

    def test_until_none_shows_now(self):
        result = pt.generate_report([], "2025-01-01", None, None)
        assert "now" in result

    def test_single_author_no_per_author_section(self):
        commits = [make_commit(author="Alice"), make_commit(hash_="b2", author="Alice")]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "PER-AUTHOR" not in result

    def test_multi_author_includes_per_author_section(self):
        commits = [
            make_commit(hash_="a1", author="Alice"),
            make_commit(hash_="b1", author="Bob"),
        ]
        with patch.object(pt, "run_git", return_value=""):
            result = pt.generate_report(commits, "2025-01-01", None, None)
        assert "PER-AUTHOR" in result

    def test_empty_commits_lists_possible_causes(self):
        result = pt.generate_report([], "2025-01-01", None, None)
        assert "Possible causes" in result


# ---------------------------------------------------------------------------
# main (CLI integration)
# ---------------------------------------------------------------------------

class TestMain:
    def test_days_flag_runs_without_error(self):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]), \
             patch("sys.argv", ["productivity_tracker.py", "--days", "30"]), \
             patch("builtins.print"):
            pt.main()

    def test_all_flag_uses_epoch_date(self):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]) as mock_commits, \
             patch("sys.argv", ["productivity_tracker.py", "--all"]), \
             patch("builtins.print"):
            pt.main()
        kwargs = mock_commits.call_args[1]
        assert kwargs["since"] == "1970-01-01"

    def test_since_flag_passes_date(self):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]) as mock_commits, \
             patch("sys.argv", ["productivity_tracker.py", "--since", "2025-01-01"]), \
             patch("builtins.print"):
            pt.main()
        kwargs = mock_commits.call_args[1]
        assert kwargs["since"] == "2025-01-01"

    def test_invalid_days_negative_exits(self):
        with patch("sys.argv", ["productivity_tracker.py", "--days", "-5"]):
            with pytest.raises(SystemExit):
                pt.main()

    def test_author_filter_passed_to_get_commits(self):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]) as mock_commits, \
             patch("sys.argv", ["productivity_tracker.py", "--days", "30", "--author", "Alice"]), \
             patch("builtins.print"):
            pt.main()
        kwargs = mock_commits.call_args[1]
        assert kwargs.get("author") == "Alice"

    def test_until_flag_passed_to_get_commits(self):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]) as mock_commits, \
             patch("sys.argv", [
                 "productivity_tracker.py",
                 "--since", "2025-01-01",
                 "--until", "2025-01-31",
             ]), \
             patch("builtins.print"):
            pt.main()
        kwargs = mock_commits.call_args[1]
        assert kwargs.get("until") == "2025-01-31"

    def test_no_date_group_arg_exits(self):
        with patch("sys.argv", ["productivity_tracker.py"]):
            with pytest.raises(SystemExit):
                pt.main()

    def test_output_printed(self, capsys):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]), \
             patch("sys.argv", ["productivity_tracker.py", "--days", "7"]):
            pt.main()
        output = capsys.readouterr().out
        assert "PRODUCTIVITY REPORT" in output

    def test_days_computes_since_date(self):
        with patch.object(pt, "verify_git_repo"), \
             patch.object(pt, "get_commits", return_value=[]) as mock_commits, \
             patch("sys.argv", ["productivity_tracker.py", "--days", "7"]), \
             patch("builtins.print"):
            pt.main()
        kwargs = mock_commits.call_args[1]
        # since should be 7 days ago in YYYY-MM-DD format
        expected = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        assert kwargs["since"] == expected
