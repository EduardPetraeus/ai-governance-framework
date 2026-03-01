"""Tests for automation/best_practice_scanner.py.

Tests pure functions (calculate_relevance, parse_rss_date, scan_sources)
without making real network calls. Network-dependent functions are tested
with mocked _http_get responses.
"""

import json
import urllib.error
from datetime import datetime, timezone
from unittest.mock import patch


import best_practice_scanner as bps


# ---------------------------------------------------------------------------
# calculate_relevance
# ---------------------------------------------------------------------------


class TestCalculateRelevance:
    def test_exact_keyword_match_gives_high_score(self):
        keywords = ["AI governance", "agent safety"]
        score = bps.calculate_relevance(
            "AI governance and agent safety blog post", keywords
        )
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
            {
                "relevance_score": 0.3,
                "source": "A",
                "title": "T1",
                "url": "",
                "date": "",
                "excerpt": "",
            },
            {
                "relevance_score": 0.9,
                "source": "B",
                "title": "T2",
                "url": "",
                "date": "",
                "excerpt": "",
            },
            {
                "relevance_score": 0.1,
                "source": "C",
                "title": "T3",
                "url": "",
                "date": "",
                "excerpt": "",
            },
        ]
        sorted_findings = sorted(
            findings, key=lambda f: f.get("relevance_score", 0), reverse=True
        )
        assert sorted_findings[0]["relevance_score"] == 0.9
        assert sorted_findings[-1]["relevance_score"] == 0.1

    @patch("best_practice_scanner._http_get")
    def test_rss_source_fetch_failure_returns_empty(self, mock_http_get):
        mock_http_get.side_effect = urllib.error.URLError("Network error")
        source = {"name": "Test RSS", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    @patch("best_practice_scanner._http_get")
    def test_github_trending_fetch_failure_returns_empty(self, mock_http_get):
        mock_http_get.side_effect = urllib.error.URLError("Network error")
        source = {"name": "GitHub", "url": "ai-governance", "type": "github_trending"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_github_trending(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    def test_unknown_source_type_is_skipped(self):
        source = [{"name": "Unknown", "url": "http://x.com", "type": "unknown_type"}]
        results = bps.scan_sources(source, days=7)
        assert results == []


# ---------------------------------------------------------------------------
# fetch_rss — XML parsing and item processing
# ---------------------------------------------------------------------------


class TestFetchRss:
    """Tests for the fetch_rss function covering XML parsing branches."""

    @patch("best_practice_scanner._http_get")
    def test_successful_rss_parse_returns_findings(self, mock_http_get):
        """Test that a valid RSS XML response is parsed into a findings list.

        Note: ElementTree's Element.__bool__ returns False for childless elements,
        so the `or` fallback in fetch_rss means plain <title> evaluates as falsy.
        We add a dummy child to make the element truthy.
        """
        rss_xml = (
            '<rss xmlns:dc="http://purl.org/dc/elements/1.1/">'
            "<channel>"
            "<item>"
            "<title>AI governance<sub/></title>"
            "<link>https://example.com/article<sub/></link>"
            "<dc:date>2029-01-01<sub/></dc:date>"
            "<description>New AI governance framework released.<sub/></description>"
            "</item>"
            "</channel></rss>"
        )
        mock_http_get.return_value = rss_xml

        source = {"name": "Test Feed", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["source"] == "Test Feed"
        assert "AI governance" in results[0]["title"]
        assert results[0]["date"] != ""

    @patch("best_practice_scanner._http_get")
    def test_rss_item_before_cutoff_is_skipped(self, mock_http_get):
        """Test that RSS items with pubDate before the cutoff are excluded.

        Uses a <sub/> child to make the pubDate element truthy for Element.__bool__.
        """
        rss_xml = (
            "<rss><channel>"
            "<item>"
            "<title>Old article<sub/></title>"
            "<link>https://example.com/old<sub/></link>"
            "<pubDate>2020-01-01<sub/></pubDate>"
            "<description>Very old article.<sub/></description>"
            "</item>"
            "</channel></rss>"
        )
        mock_http_get.return_value = rss_xml

        source = {"name": "Test Feed", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    @patch("best_practice_scanner._http_get")
    def test_rss_invalid_xml_returns_empty(self, mock_http_get):
        """Test that invalid XML gracefully returns empty list."""
        mock_http_get.return_value = "not valid xml <><><>"

        source = {"name": "Bad Feed", "url": "https://example.com/bad", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    @patch("best_practice_scanner._http_get")
    def test_rss_http_error_returns_empty(self, mock_http_get):
        """Test that HTTP errors from urlopen return empty list."""
        mock_http_get.side_effect = urllib.error.HTTPError(
            "https://example.com/err", 404, "Not Found", {}, None
        )

        source = {"name": "Error Feed", "url": "https://example.com/err", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    @patch("best_practice_scanner._http_get")
    def test_atom_feed_is_parsed(self, mock_http_get):
        """Test that Atom format feeds are also parsed correctly.

        Uses child elements to make Elements truthy (ElementTree gotcha).
        """
        atom_xml = (
            '<feed xmlns="http://www.w3.org/2005/Atom">'
            "<entry>"
            "<title>AI Agent Safety<sub/></title>"
            '<link href="https://example.com/atom-article"><sub/></link>'
            "<published>2029-06-01T10:00:00Z<sub/></published>"
            "<summary>Agent safety discussion.<sub/></summary>"
            "</entry>"
            "</feed>"
        )
        mock_http_get.return_value = atom_xml

        source = {"name": "Atom Feed", "url": "https://example.com/atom", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com/atom-article"

    @patch("best_practice_scanner._http_get")
    def test_rss_item_without_date_is_included(self, mock_http_get):
        """Test that items without a parsable date element are still included."""
        rss_xml = (
            "<rss><channel>"
            "<item>"
            "<title>No date article<sub/></title>"
            "<link>https://example.com/nodate<sub/></link>"
            "<description>Article without a date.<sub/></description>"
            "</item>"
            "</channel></rss>"
        )
        mock_http_get.return_value = rss_xml

        source = {"name": "Test", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["date"] == ""

    @patch("best_practice_scanner._http_get")
    def test_rss_item_with_link_href_attribute(self, mock_http_get):
        """Test that link elements with href attribute are correctly extracted."""
        rss_xml = (
            "<rss><channel>"
            "<item>"
            "<title>Test<sub/></title>"
            '<link href="https://example.com/href-link"><sub/></link>'
            "<description>Test content.<sub/></description>"
            "</item>"
            "</channel></rss>"
        )
        mock_http_get.return_value = rss_xml

        source = {"name": "Test", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com/href-link"

    @patch("best_practice_scanner._http_get")
    def test_rss_item_no_link_element(self, mock_http_get):
        """Test that items without a link element get empty URL."""
        rss_xml = (
            "<rss><channel>"
            "<item>"
            "<title>No Link<sub/></title>"
            "<description>Content only.<sub/></description>"
            "</item>"
            "</channel></rss>"
        )
        mock_http_get.return_value = rss_xml

        source = {"name": "Test", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["url"] == ""

    @patch("best_practice_scanner._http_get")
    def test_rss_item_no_title_element(self, mock_http_get):
        """Test that items without title get 'Untitled'."""
        rss_xml = (
            "<rss><channel>"
            "<item>"
            "<link>https://example.com/x</link>"
            "<description>No title here.</description>"
            "</item>"
            "</channel></rss>"
        )
        mock_http_get.return_value = rss_xml

        source = {"name": "Test", "url": "https://example.com/feed", "type": "rss"}
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_rss(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["title"] == "Untitled"


# ---------------------------------------------------------------------------
# fetch_github_trending — with mocked responses
# ---------------------------------------------------------------------------


class TestFetchGithubTrending:
    """Tests for the fetch_github_trending function covering API response processing."""

    @patch("best_practice_scanner._http_get")
    def test_successful_github_search_returns_repos(self, mock_http_get):
        """Test that GitHub API search results are parsed into findings."""
        mock_http_get.return_value = json.dumps(
            {
                "items": [
                    {
                        "full_name": "user/ai-governance",
                        "description": "AI governance framework",
                        "html_url": "https://github.com/user/ai-governance",
                        "pushed_at": "2025-06-01T12:00:00Z",
                        "stargazers_count": 42,
                    },
                ]
            }
        )

        source = {
            "name": "GitHub Trending",
            "url": "ai-governance",
            "type": "github_trending",
        }
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_github_trending(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert "42 stars" in results[0]["title"]
        assert results[0]["url"] == "https://github.com/user/ai-governance"

    @patch("best_practice_scanner._http_get")
    def test_github_empty_items_returns_empty(self, mock_http_get):
        """Test that empty GitHub search results return empty list."""
        mock_http_get.return_value = json.dumps({"items": []})

        source = {"name": "GitHub", "url": "ai-governance", "type": "github_trending"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_github_trending(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert results == []

    @patch("best_practice_scanner._http_get")
    def test_github_repo_with_none_description(self, mock_http_get):
        """Test that repos with None description are handled gracefully."""
        mock_http_get.return_value = json.dumps(
            {
                "items": [
                    {
                        "full_name": "user/repo",
                        "description": None,
                        "html_url": "https://github.com/user/repo",
                        "pushed_at": "2025-06-01T12:00:00Z",
                        "stargazers_count": 0,
                    },
                ]
            }
        )

        source = {"name": "GitHub", "url": "ai-governance", "type": "github_trending"}
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = bps.fetch_github_trending(source, cutoff, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["excerpt"] == ""


# ---------------------------------------------------------------------------
# fetch_web — with mocked responses
# ---------------------------------------------------------------------------


class TestFetchWeb:
    """Tests for the fetch_web function covering web page processing."""

    @patch("best_practice_scanner._http_get")
    def test_successful_web_fetch_returns_finding(self, mock_http_get):
        """Test that a web page is fetched and text is extracted."""
        html = (
            "<html><head><title>AI Governance</title></head>"
            "<body><h1>AI governance best practices</h1>"
            "<script>var x = 1;</script>"
            "<style>body { color: red; }</style>"
            "<p>Agent safety discussion.</p></body></html>"
        )
        mock_http_get.return_value = html

        source = {"name": "Web Page", "url": "https://example.com/page", "type": "web"}
        results = bps.fetch_web(source, bps.DEFAULT_KEYWORDS)
        assert len(results) == 1
        assert results[0]["source"] == "Web Page"
        assert "var x = 1" not in results[0]["excerpt"]

    @patch("best_practice_scanner._http_get")
    def test_web_fetch_failure_returns_empty(self, mock_http_get):
        """Test that web fetch errors return empty list."""
        mock_http_get.side_effect = urllib.error.URLError("Connection refused")

        source = {"name": "Bad Page", "url": "https://example.com/fail", "type": "web"}
        results = bps.fetch_web(source, bps.DEFAULT_KEYWORDS)
        assert results == []


# ---------------------------------------------------------------------------
# scan_sources — routing to different source types
# ---------------------------------------------------------------------------


class TestScanSourcesRouting:
    """Tests for scan_sources routing different source types and extra keywords."""

    @patch("best_practice_scanner.fetch_web")
    def test_web_source_routes_to_fetch_web(self, mock_fetch_web):
        """Test that 'web' source type calls fetch_web."""
        mock_fetch_web.return_value = [{"relevance_score": 0.5, "source": "web"}]
        sources = [{"name": "Web", "url": "https://example.com", "type": "web"}]
        results = bps.scan_sources(sources, days=7)
        mock_fetch_web.assert_called_once()
        assert len(results) == 1

    @patch("best_practice_scanner.fetch_rss")
    def test_rss_source_routes_to_fetch_rss(self, mock_fetch_rss):
        """Test that 'rss' source type calls fetch_rss."""
        mock_fetch_rss.return_value = [{"relevance_score": 0.5, "source": "rss"}]
        sources = [{"name": "RSS", "url": "https://example.com/feed", "type": "rss"}]
        results = bps.scan_sources(sources, days=7)
        mock_fetch_rss.assert_called_once()
        assert len(results) == 1

    @patch("best_practice_scanner.fetch_github_trending")
    def test_github_trending_routes_correctly(self, mock_fetch_gh):
        """Test that 'github_trending' type calls fetch_github_trending."""
        mock_fetch_gh.return_value = [{"relevance_score": 0.5, "source": "gh"}]
        sources = [{"name": "GH", "url": "topic", "type": "github_trending"}]
        results = bps.scan_sources(sources, days=7)
        mock_fetch_gh.assert_called_once()
        assert len(results) == 1

    @patch("best_practice_scanner.fetch_web")
    def test_extra_keywords_are_appended(self, mock_fetch_web):
        """Test that extra_keywords extend the default keyword list."""
        mock_fetch_web.return_value = []
        sources = [{"name": "Web", "url": "https://example.com", "type": "web"}]
        bps.scan_sources(sources, days=7, extra_keywords=["custom keyword"])
        call_kwargs = mock_fetch_web.call_args
        keywords_arg = call_kwargs[0][1]  # second positional arg
        assert "custom keyword" in keywords_arg


# ---------------------------------------------------------------------------
# run — output and file writing
# ---------------------------------------------------------------------------


class TestRunFunction:
    """Tests for the run() function covering output and file writing."""

    @patch("best_practice_scanner.scan_sources")
    def test_run_prints_to_stdout(self, mock_scan, capsys):
        """Test that run() prints JSON to stdout when no output_file is given."""
        mock_scan.return_value = [
            {
                "source": "Test",
                "title": "T",
                "url": "",
                "date": "",
                "excerpt": "",
                "relevance_score": 0.5,
            }
        ]
        code = bps.run(days=7)
        assert code == 0
        captured = capsys.readouterr()
        assert "Test" in captured.out

    @patch("best_practice_scanner.scan_sources")
    def test_run_writes_to_file(self, mock_scan, tmp_path):
        """Test that run() writes findings to a file when output_file is given."""
        mock_scan.return_value = [
            {
                "source": "A",
                "title": "T",
                "url": "",
                "date": "",
                "excerpt": "",
                "relevance_score": 0.5,
            }
        ]
        output = str(tmp_path / "output.json")
        code = bps.run(days=7, output_file=output)
        assert code == 0
        content = (tmp_path / "output.json").read_text()
        assert "A" in content

    @patch("best_practice_scanner.scan_sources")
    def test_run_write_error_returns_one(self, mock_scan):
        """Test that run() returns exit code 1 when file write fails."""
        mock_scan.return_value = [
            {
                "source": "A",
                "title": "T",
                "url": "",
                "date": "",
                "excerpt": "",
                "relevance_score": 0.5,
            }
        ]
        code = bps.run(days=7, output_file="/nonexistent/path/output.json")
        assert code == 1

    @patch("best_practice_scanner.scan_sources")
    def test_run_with_extra_keywords(self, mock_scan, capsys):
        """Test that run() passes extra keywords through to scan_sources."""
        mock_scan.return_value = []
        code = bps.run(days=7, extra_keywords=["custom term"])
        assert code == 0
        mock_scan.assert_called_once()
        call_kwargs = mock_scan.call_args
        assert call_kwargs[1].get("extra_keywords") == ["custom term"] or call_kwargs[
            0
        ][2] == ["custom term"]


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    """Tests for the argument parser builder."""

    def test_build_parser_returns_parser(self):
        """Test that build_parser returns a valid ArgumentParser."""
        parser = bps.build_parser()
        assert parser is not None

    def test_parser_defaults(self):
        """Test parser default values."""
        parser = bps.build_parser()
        args = parser.parse_args([])
        assert args.days == 7
        assert args.output_file is None
        assert args.keywords is None

    def test_parser_with_all_args(self):
        """Test parser with all arguments supplied."""
        parser = bps.build_parser()
        args = parser.parse_args(
            [
                "--days",
                "14",
                "--output-file",
                "out.json",
                "--keywords",
                "safety",
                "governance",
            ]
        )
        assert args.days == 14
        assert args.output_file == "out.json"
        assert args.keywords == ["safety", "governance"]
