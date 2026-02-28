"""Tests for automation/framework_updater.py.

Tests pure functions without network calls. GitHub API interactions
are tested with mocked responses.
"""

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
        import json
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
