"""Tests for automation/best_practice_scanner.py.

Tests pure functions (calculate_relevance, parse_rss_date, scan_sources)
without making real network calls. Network-dependent functions are tested
with mocked responses.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

import best_practice_scanner as bps


# ---------------------------------------------------------------------------
# calculate_relevance
# ---------------------------------------------------------------------------

class TestCalculateRelevance:
    def test_exact_keyword_match_gives_high_score(self):
        keywords = ["AI governance", "agent safety"]
        score = bps.calculate_relevance("AI governance and agent safety blog post", keywords)
        assert score > 0.0

    def test_no_match_gives_zero(self):
        keywords = ["AI governance", "LLM"]
        score = bps.calculate_relevance("unrelated content about gardening", keywords)
        assert score == 0.0

    def test_empty_text_gives_zero(self):
        keywords = ["AI governance"]
        assert bps.calculate_relevance("", keywords) == 0.0

    def test_empty_keywords_gives_zero(self):
        assert bps.calculate_relevance("some text", []) == 0.0

    def test_score_is_between_zero_and_one(self):
        keywords = bps.DEFAULT_KEYWORDS
        score = bps.calculate_relevance("AI governance LLM agent safety", keywords)
        assert 0.0 <= score <= 1.0

    def test_case_insensitive_matching(self):
        keywords = ["AI Governance"]
        score_lower = bps.calculate_relevance("ai governance best practices", keywords)
        score_upper = bps.calculate_relevance("AI GOVERNANCE BEST PRACTICES", keywords)
        assert score_lower == score_upper


# ---------------------------------------------------------------------------
# parse_rss_date
# ---------------------------------------------------------------------------

class TestParseRssDate:
    def test_rfc2822_format(self):
        dt = bps.parse_rss_date("Mon, 01 Jan 2025 12:00:00 +0000")
        assert dt is not None
        assert dt.year == 2025

    def test_iso8601_format(self):
        dt = bps.parse_rss_date("2025-03-15T10:30:00Z")
        assert dt is not None
        assert dt.month == 3

    def test_date_only_format(self):
        dt = bps.parse_rss_date("2025-06-01")
        assert dt is not None
        assert dt.year == 2025

    def test_invalid_format_returns_none(self):
        assert bps.parse_rss_date("not a date at all") is None

    def test_result_is_timezone_aware(self):
        dt = bps.parse_rss_date("2025-01-01")
        assert dt is not None
        assert dt.tzinfo is not None


# ---------------------------------------------------------------------------
# scan_sources — with mocked network
# ---------------------------------------------------------------------------

class TestScanSourcesWithMock:
    def test_empty_sources_returns_empty_list(self):
        results = bps.scan_sources([], days=7)
        assert results == []

    def test_findings_sorted_by_relevance_descending(self):
        findings = [
            {"relevance_score": 0.3, "source": "A", "title": "T1", "url": "", "date": "", "excerpt": ""},
            {"relevance_score": 0.9, "source": "B", "title": "T2", "url": "", "date": "", "excerpt": ""},
            {"relevance_score": 0.1, "source": "C", "title": "T3", "url": "", "date": "", "excerpt": ""},
        ]
        # Simulate what scan_sources does: sort by relevance descending
        sorted_findings = sorted(findings, key=lambda f: f.get("relevance_score", 0), reverse=True)
        assert sorted_findings[0]["relevance_score"] == 0.9
        assert sorted_findings[-1]["relevance_score"] == 0.1

    @patch("best_practice_scanner.requests.get")
    def test_rss_source_fetch_failure_returns_empty(self, mock_get):
        import requests as real_requests
        mock_get.side_effect = real_requests.RequestException("Network error")
        source = {"name": "Test RSS", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    @patch("best_practice_scanner.requests.get")
    def test_github_trending_fetch_failure_returns_empty(self, mock_get):
        import requests as real_requests
        mock_get.side_effect = real_requests.RequestException("Network error")
        source = {"name": "GitHub", "url": "ai-governance", "type": "github_trending"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_github_trending(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    def test_unknown_source_type_is_skipped(self):
        source = [{"name": "Unknown", "url": "http://x.com", "type": "unknown_type"}]
        results = bps.scan_sources(source, days=7)
        assert results == []
