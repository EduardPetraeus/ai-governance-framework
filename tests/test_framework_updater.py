"""Tests for automation/framework_updater.py.

Tests pure functions without network calls. GitHub API interactions
are tested with mocked urllib responses.
"""

import json
import socket
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import framework_updater as fu


# ---------------------------------------------------------------------------
# parse_version
# ---------------------------------------------------------------------------

class TestParseVersion:
    def test_version_with_v_prefix(self):
        assert fu.parse_version("v1.2.3") == (1, 2, 3)

    def test_version_without_prefix(self):
        assert fu.parse_version("2.0.0") == (2, 0, 0)

    def test_version_patch_zero(self):
        assert fu.parse_version("v1.0.0") == (1, 0, 0)

    def test_invalid_version_raises(self):
        with pytest.raises(ValueError):
            fu.parse_version("not-a-version")

    def test_partial_version_raises(self):
        with pytest.raises(ValueError):
            fu.parse_version("1.0")


# ---------------------------------------------------------------------------
# _parse_next_link
# ---------------------------------------------------------------------------

class TestParseNextLink:
    def test_extracts_next_url(self):
        header = '<https://api.github.com/repos/owner/repo/releases?page=2>; rel="next", <https://api.github.com/repos/owner/repo/releases?page=3>; rel="last"'
        assert fu._parse_next_link(header) == "https://api.github.com/repos/owner/repo/releases?page=2"

    def test_no_next_returns_none(self):
        header = '<https://api.github.com/repos/owner/repo/releases?page=1>; rel="prev"'
        assert fu._parse_next_link(header) is None

    def test_empty_header_returns_none(self):
        assert fu._parse_next_link("") is None


# ---------------------------------------------------------------------------
# find_version_file / read_local_version
# ---------------------------------------------------------------------------

class TestReadLocalVersion:
    def test_missing_version_file_returns_default(self, tmp_path):
        version = fu.read_local_version(tmp_path)
        assert version == fu.DEFAULT_VERSION

    def test_reads_version_from_file(self, tmp_path):
        (tmp_path / fu.VERSION_FILE).write_text("v2.1.0\n", encoding="utf-8")
        assert fu.read_local_version(tmp_path) == "v2.1.0"

    def test_empty_version_file_returns_default(self, tmp_path):
        (tmp_path / fu.VERSION_FILE).write_text("", encoding="utf-8")
        assert fu.read_local_version(tmp_path) == fu.DEFAULT_VERSION


# ---------------------------------------------------------------------------
# get_available_updates
# ---------------------------------------------------------------------------

class TestGetAvailableUpdates:
    def _release(self, tag: str) -> dict:
        return {"tag_name": tag, "body": "Notes.", "published_at": "2025-01-01T00:00:00Z"}

    def test_no_updates_when_already_latest(self):
        releases = [self._release("v1.0.0"), self._release("v1.1.0")]
        updates = fu.get_available_updates(releases, "v1.1.0")
        assert updates == []

    def test_returns_newer_releases(self):
        releases = [self._release("v1.0.0"), self._release("v1.1.0"), self._release("v2.0.0")]
        updates = fu.get_available_updates(releases, "v1.0.0")
        assert len(updates) == 2

    def test_empty_releases_returns_empty(self):
        updates = fu.get_available_updates([], "v1.0.0")
        assert updates == []


# ---------------------------------------------------------------------------
# format_text / format_json
# ---------------------------------------------------------------------------

class TestFormatText:
    def _release(self, tag: str) -> dict:
        return {"tag_name": tag, "body": "New features.", "published_at": "2025-06-01T00:00:00Z", "assets": []}

    def test_up_to_date_message(self):
        text = fu.format_text("v1.0.0", "v1.0.0", [], check_only=False)
        assert "up to date" in text.lower()

    def test_shows_available_updates(self):
        updates = [self._release("v1.1.0")]
        text = fu.format_text("v1.0.0", "v1.1.0", updates, check_only=False)
        assert "v1.1.0" in text

    def test_json_format_is_parseable(self):
        updates = [self._release("v1.1.0")]
        output = fu.format_json("v1.0.0", "v1.1.0", updates)
        parsed = json.loads(output)
        assert "updates_available" in parsed
        assert parsed["updates_available"] == 1


# ---------------------------------------------------------------------------
# run — exit codes with mocked network
# ---------------------------------------------------------------------------

class TestRun:
    @patch("framework_updater.fetch_releases")
    def test_run_returns_zero_when_up_to_date(self, mock_fetch, tmp_path):
        mock_fetch.return_value = [{"tag_name": "v1.0.0", "body": "", "published_at": "2025-01-01"}]
        (tmp_path / fu.VERSION_FILE).write_text("v1.0.0", encoding="utf-8")
        code = fu.run(tmp_path)
        assert code == 0

    @patch("framework_updater.fetch_releases")
    def test_run_returns_zero_when_updates_available(self, mock_fetch, tmp_path):
        mock_fetch.return_value = [
            {"tag_name": "v1.0.0", "body": "", "published_at": "2025-01-01", "assets": []},
            {"tag_name": "v1.1.0", "body": "New stuff.", "published_at": "2025-06-01", "assets": []},
        ]
        (tmp_path / fu.VERSION_FILE).write_text("v1.0.0", encoding="utf-8")
        code = fu.run(tmp_path)
        assert code == 0


# ---------------------------------------------------------------------------
# fetch_releases — mocked API
# ---------------------------------------------------------------------------

def _make_urlopen_mock(data, link_header: str = "") -> MagicMock:
    """Helper: create a mock for urllib.request.urlopen returning data as JSON."""
    mock_response = MagicMock()
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.read.return_value = json.dumps(data).encode("utf-8")
    mock_response.headers.get.return_value = link_header
    return mock_response


class TestFetchReleases:
    """Tests for the fetch_releases function with mocked HTTP requests."""

    @patch("framework_updater.urllib.request.urlopen")
    def test_fetches_and_sorts_valid_releases(self, mock_urlopen):
        """Test that valid releases are sorted by version ascending."""
        mock_urlopen.return_value = _make_urlopen_mock([
            {"tag_name": "v2.0.0", "body": "Major release"},
            {"tag_name": "v1.0.0", "body": "Initial"},
            {"tag_name": "v1.1.0", "body": "Minor update"},
        ])

        releases = fu.fetch_releases()
        assert len(releases) == 3
        assert releases[0]["tag_name"] == "v1.0.0"
        assert releases[-1]["tag_name"] == "v2.0.0"

    @patch("framework_updater.urllib.request.urlopen")
    def test_skips_invalid_version_tags(self, mock_urlopen):
        """Test that releases with invalid version tags are filtered out."""
        mock_urlopen.return_value = _make_urlopen_mock([
            {"tag_name": "v1.0.0", "body": "Valid"},
            {"tag_name": "nightly-2025", "body": "Invalid"},
            {"tag_name": "v2.0.0", "body": "Valid too"},
        ])

        releases = fu.fetch_releases()
        assert len(releases) == 2

    @patch("framework_updater.urllib.request.urlopen")
    def test_skips_pre_release_tags(self, mock_urlopen):
        """Test that pre-release tags (e.g. v1.2.3-beta) are skipped with a warning."""
        mock_urlopen.return_value = _make_urlopen_mock([
            {"tag_name": "v1.0.0", "body": "Stable"},
            {"tag_name": "v1.1.0-beta", "body": "Pre-release"},
            {"tag_name": "v2.0.0-rc1", "body": "Release candidate"},
        ])

        releases = fu.fetch_releases()
        assert len(releases) == 1
        assert releases[0]["tag_name"] == "v1.0.0"

    @patch("framework_updater.urllib.request.urlopen")
    def test_pagination_follows_next_link(self, mock_urlopen):
        """Test that pagination via Link header fetches all pages."""
        page1_link = '<https://api.github.com/repos/x/y/releases?page=2>; rel="next"'
        mock_page1 = _make_urlopen_mock([{"tag_name": "v1.0.0", "body": ""}], link_header=page1_link)
        mock_page2 = _make_urlopen_mock([{"tag_name": "v2.0.0", "body": ""}], link_header="")
        mock_urlopen.side_effect = [mock_page1, mock_page2]

        releases = fu.fetch_releases()
        assert len(releases) == 2
        assert mock_urlopen.call_count == 2


# ---------------------------------------------------------------------------
# show_apply_diff
# ---------------------------------------------------------------------------

class TestShowApplyDiff:
    """Tests for the show_apply_diff function."""

    def test_shows_release_info(self):
        """Test that show_apply_diff includes release tag and URL."""
        updates = [
            {
                "tag_name": "v1.1.0",
                "assets": [{"name": "archive.tar.gz", "size": 1024}],
                "html_url": "https://github.com/owner/repo/releases/v1.1.0",
            },
        ]
        output = fu.show_apply_diff(updates)
        assert "v1.1.0" in output
        assert "archive.tar.gz" in output
        assert "1024 bytes" in output

    def test_no_assets_shows_source_archive_msg(self):
        """Test that releases with no assets show source archive message."""
        updates = [
            {
                "tag_name": "v2.0.0",
                "assets": [],
                "html_url": "https://github.com/owner/repo/releases/v2.0.0",
            },
        ]
        output = fu.show_apply_diff(updates)
        assert "Source archive" in output

    def test_includes_manual_review_note(self):
        """Test that the output includes the manual review reminder."""
        output = fu.show_apply_diff([{
            "tag_name": "v1.0.1", "assets": [], "html_url": ""
        }])
        assert "manual" in output.lower()


# ---------------------------------------------------------------------------
# format_text — additional branches
# ---------------------------------------------------------------------------

class TestFormatTextExtended:
    """Extended tests for format_text covering body truncation and check_only."""

    def _release(self, tag, body="Short notes.", published_at="2025-06-01T00:00:00Z"):
        return {"tag_name": tag, "body": body, "published_at": published_at, "assets": []}

    def test_long_body_is_truncated(self):
        """Test that release notes longer than 300 chars are truncated with '...'."""
        long_body = "A" * 400
        updates = [self._release("v1.1.0", body=long_body)]
        text = fu.format_text("v1.0.0", "v1.1.0", updates, check_only=False)
        assert "..." in text

    def test_check_only_with_updates_does_not_show_details(self):
        """Test that check_only mode does not show detailed release notes."""
        updates = [self._release("v1.1.0")]
        text = fu.format_text("v1.0.0", "v1.1.0", updates, check_only=True)
        assert "Release notes" not in text
        assert "Updates available: 1" in text

    def test_null_body_uses_fallback(self):
        """Test that None body falls back to 'No release notes available.'."""
        updates = [self._release("v1.1.0", body=None)]
        text = fu.format_text("v1.0.0", "v1.1.0", updates, check_only=False)
        assert "No release notes available" in text


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

class TestFormatJson:
    """Tests for the format_json function."""

    def test_output_is_valid_json(self):
        """Test that format_json returns valid JSON."""
        updates = [{"tag_name": "v1.1.0", "published_at": "2025-06-01", "body": "Notes", "html_url": ""}]
        output = fu.format_json("v1.0.0", "v1.1.0", updates)
        parsed = json.loads(output)
        assert parsed["current_version"] == "v1.0.0"
        assert parsed["latest_version"] == "v1.1.0"

    def test_truncates_long_release_notes(self):
        """Test that release notes in JSON are truncated to 300 chars."""
        long_notes = "B" * 500
        updates = [{"tag_name": "v2.0.0", "published_at": "", "body": long_notes, "html_url": ""}]
        output = fu.format_json("v1.0.0", "v2.0.0", updates)
        parsed = json.loads(output)
        assert len(parsed["updates"][0]["release_notes"]) <= 300


# ---------------------------------------------------------------------------
# run — error handling and output format branches
# ---------------------------------------------------------------------------

class TestRunExtended:
    """Extended tests for run() covering error handling and output format branches."""

    @patch("framework_updater.fetch_releases")
    def test_run_connection_error(self, mock_fetch, tmp_path, capsys):
        """Test that URLError returns exit code 1."""
        mock_fetch.side_effect = urllib.error.URLError("Network unreachable")
        code = fu.run(tmp_path)
        assert code == 1
        captured = capsys.readouterr()
        assert "Could not connect" in captured.err

    @patch("framework_updater.fetch_releases")
    def test_run_timeout_error(self, mock_fetch, tmp_path, capsys):
        """Test that socket.timeout returns exit code 1."""
        mock_fetch.side_effect = socket.timeout("Request timed out")
        code = fu.run(tmp_path)
        assert code == 1
        captured = capsys.readouterr()
        assert "timed out" in captured.err

    @patch("framework_updater.fetch_releases")
    def test_run_http_error(self, mock_fetch, tmp_path, capsys):
        """Test that HTTPError returns exit code 1."""
        mock_fetch.side_effect = urllib.error.HTTPError(
            None, 403, "Forbidden", {}, None
        )
        code = fu.run(tmp_path)
        assert code == 1
        captured = capsys.readouterr()
        assert "error" in captured.err.lower()

    @patch("framework_updater.fetch_releases")
    def test_run_json_format_output(self, mock_fetch, tmp_path, capsys):
        """Test run() with output_format='json'."""
        mock_fetch.return_value = [
            {"tag_name": "v1.0.0", "body": "", "published_at": "2025-01-01", "assets": [], "html_url": ""},
            {"tag_name": "v1.1.0", "body": "Update.", "published_at": "2025-06-01", "assets": [], "html_url": ""},
        ]
        (tmp_path / fu.VERSION_FILE).write_text("v1.0.0", encoding="utf-8")
        code = fu.run(tmp_path, output_format="json")
        assert code == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["updates_available"] == 1

    @patch("framework_updater.fetch_releases")
    def test_run_with_apply_flag(self, mock_fetch, tmp_path, capsys):
        """Test run() with apply=True shows apply diff."""
        mock_fetch.return_value = [
            {"tag_name": "v1.0.0", "body": "", "published_at": "2025-01-01", "assets": [], "html_url": ""},
            {"tag_name": "v1.1.0", "body": "New stuff.", "published_at": "2025-06-01", "assets": [], "html_url": "https://github.com/x/y/releases/v1.1.0"},
        ]
        (tmp_path / fu.VERSION_FILE).write_text("v1.0.0", encoding="utf-8")
        code = fu.run(tmp_path, apply=True)
        assert code == 0
        captured = capsys.readouterr()
        assert "Apply preview" in captured.out

    @patch("framework_updater.fetch_releases")
    def test_run_empty_releases(self, mock_fetch, tmp_path, capsys):
        """Test run() when no releases exist on GitHub."""
        mock_fetch.return_value = []
        code = fu.run(tmp_path)
        assert code == 0


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    """Tests for the CLI argument parser builder."""

    def test_build_parser_returns_parser(self):
        """Test that build_parser returns a valid ArgumentParser."""
        parser = fu.build_parser()
        assert parser is not None

    def test_parser_defaults(self):
        """Test parser default values."""
        parser = fu.build_parser()
        args = parser.parse_args([])
        assert args.repo_path == Path(".")
        assert args.check_only is False
        assert args.output_format == "text"
        assert args.apply is False

    def test_parser_with_all_args(self):
        """Test parser with all arguments supplied."""
        parser = fu.build_parser()
        args = parser.parse_args(["--repo-path", "/tmp/repo", "--check-only", "--format", "json", "--apply"])
        assert args.repo_path == Path("/tmp/repo")
        assert args.check_only is True
        assert args.output_format == "json"
        assert args.apply is True
