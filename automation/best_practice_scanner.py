"""Scan configured sources for new AI governance insights.

This script fetches RSS feeds, GitHub trending repositories, and web pages,
then filters results by governance-related keywords. Output is a JSON array
of findings suitable for downstream analysis by a research agent.

Uses only the standard library (urllib) — no third-party dependencies.

Usage:
    python best-practice-scanner.py --days 7
    python best-practice-scanner.py --days 14 --output-file insights.json
    python best-practice-scanner.py --keywords "prompt safety" "agent guardrails"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

GITHUB_API_BASE = "https://api.github.com"

SOURCES: List[Dict[str, str]] = [
    {
        "name": "Anthropic Blog",
        "url": "https://www.anthropic.com/news",
        "type": "rss",
    },
    {
        "name": "GitHub — claude-code repos",
        "url": "claude-code",
        "type": "github_trending",
    },
    {
        "name": "GitHub — ai-governance repos",
        "url": "ai-governance",
        "type": "github_trending",
    },
]

DEFAULT_KEYWORDS: List[str] = [
    "AI governance",
    "LLM governance",
    "Claude Code",
    "AI agent",
    "agent framework",
    "AI development",
    "prompt engineering",
    "agent safety",
    "AI quality control",
    "output contract",
    "AI oversight",
]


def _http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
) -> str:
    """Perform an HTTP GET using urllib. Returns response body as text.

    Raises urllib.error.URLError (or its subclass HTTPError) on failure.
    """
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8")


def calculate_relevance(text: str, keywords: List[str]) -> float:
    """Calculate a relevance score (0.0-1.0) based on keyword matches in text."""
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    matches = sum(1 for kw in keywords if kw.lower() in text_lower)
    return round(min(matches / max(len(keywords) * 0.3, 1), 1.0), 2)


def parse_rss_date(date_string: str) -> Optional[datetime]:
    """Parse common RSS/Atom date formats into a timezone-aware datetime."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def fetch_rss(source: Dict[str, str], cutoff: datetime, keywords: List[str]) -> List[Dict[str, Any]]:
    """Fetch and parse an RSS/Atom feed, returning items published after cutoff."""
    findings: List[Dict[str, Any]] = []
    try:
        text = _http_get(source["url"], headers={"User-Agent": "ai-governance-scanner/1.0"})
    except urllib.error.URLError as exc:
        print(f"Warning: Could not fetch RSS source '{source['name']}': {exc}", file=sys.stderr)
        return findings

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        print(f"Warning: Could not parse RSS from '{source['name']}': {exc}", file=sys.stderr)
        return findings

    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "dc": "http://purl.org/dc/elements/1.1/",
    }

    items = root.findall(".//item")
    if not items:
        items = root.findall(".//atom:entry", namespaces)

    for item in items:
        title_el = item.find("title") or item.find("atom:title", namespaces)
        link_el = item.find("link") or item.find("atom:link", namespaces)
        date_el = (
            item.find("pubDate")
            or item.find("dc:date", namespaces)
            or item.find("atom:published", namespaces)
            or item.find("atom:updated", namespaces)
        )
        desc_el = item.find("description") or item.find("atom:summary", namespaces) or item.find("atom:content", namespaces)

        title = (title_el.text or "").strip() if title_el is not None else "Untitled"

        if link_el is not None:
            link = link_el.get("href", "") or (link_el.text or "")
        else:
            link = ""

        pub_date = None
        if date_el is not None and date_el.text:
            pub_date = parse_rss_date(date_el.text)

        if pub_date and pub_date < cutoff:
            continue

        description = ""
        if desc_el is not None and desc_el.text:
            description = re.sub(r"<[^>]+>", "", desc_el.text).strip()

        combined_text = f"{title} {description}"
        relevance = calculate_relevance(combined_text, keywords)

        findings.append({
            "source": source["name"],
            "title": title,
            "url": link.strip(),
            "date": pub_date.isoformat() if pub_date else "",
            "excerpt": description[:500],
            "relevance_score": relevance,
        })

    return findings


def fetch_github_trending(source: Dict[str, str], cutoff: datetime, keywords: List[str]) -> List[Dict[str, Any]]:
    """Search GitHub for repositories matching a topic, created or pushed after cutoff."""
    findings: List[Dict[str, Any]] = []
    topic = source["url"]
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    query = f"topic:{topic} pushed:>={cutoff_str}"
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 20,
    }

    try:
        text = _http_get(url, params=params, headers={"Accept": "application/vnd.github+json"})
    except urllib.error.URLError as exc:
        print(f"Warning: Could not search GitHub for topic '{topic}': {exc}", file=sys.stderr)
        return findings

    data = json.loads(text)
    for repo in data.get("items", []):
        name = repo.get("full_name", "")
        description = repo.get("description", "") or ""
        html_url = repo.get("html_url", "")
        pushed_at = repo.get("pushed_at", "")
        stars = repo.get("stargazers_count", 0)

        combined_text = f"{name} {description}"
        relevance = calculate_relevance(combined_text, keywords)

        findings.append({
            "source": source["name"],
            "title": f"{name} ({stars} stars)",
            "url": html_url,
            "date": pushed_at,
            "excerpt": description[:500],
            "relevance_score": relevance,
        })

    return findings


def fetch_web(source: Dict[str, str], keywords: List[str]) -> List[Dict[str, Any]]:
    """Fetch a web page and extract a simplified text excerpt."""
    findings: List[Dict[str, Any]] = []
    try:
        text = _http_get(
            source["url"],
            headers={"User-Agent": "ai-governance-scanner/1.0"},
        )
    except urllib.error.URLError as exc:
        print(f"Warning: Could not fetch web source '{source['name']}': {exc}", file=sys.stderr)
        return findings

    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    relevance = calculate_relevance(text, keywords)

    findings.append({
        "source": source["name"],
        "title": source["name"],
        "url": source["url"],
        "date": datetime.now(timezone.utc).isoformat(),
        "excerpt": text[:500],
        "relevance_score": relevance,
    })

    return findings


def scan_sources(
    sources: List[Dict[str, str]],
    days: int,
    extra_keywords: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Scan all configured sources and return a combined list of findings."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    keywords = DEFAULT_KEYWORDS.copy()
    if extra_keywords:
        keywords.extend(extra_keywords)

    all_findings: List[Dict[str, Any]] = []

    for source in sources:
        source_type = source.get("type", "web")
        if source_type == "rss":
            all_findings.extend(fetch_rss(source, cutoff, keywords))
        elif source_type == "github_trending":
            all_findings.extend(fetch_github_trending(source, cutoff, keywords))
        elif source_type == "web":
            all_findings.extend(fetch_web(source, keywords))
        else:
            print(f"Warning: Unknown source type '{source_type}' for '{source['name']}'", file=sys.stderr)

    all_findings.sort(key=lambda f: f.get("relevance_score", 0), reverse=True)
    return all_findings


def run(
    days: int = 7,
    output_file: Optional[str] = None,
    extra_keywords: Optional[List[str]] = None,
) -> int:
    """Run the best-practice scanner and return an exit code (0 = success)."""
    findings = scan_sources(SOURCES, days, extra_keywords)
    output = json.dumps(findings, indent=2, ensure_ascii=False)

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)
                f.write("\n")
            print(f"Wrote {len(findings)} finding(s) to {output_file}")
        except OSError as exc:
            print(f"Error: Could not write to {output_file}: {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Scan configured sources for new AI governance insights.",
        epilog="Results are structured for downstream analysis by a research agent.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Look back N days for new content (default: 7)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Save results to a JSON file (default: print to stdout)",
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=None,
        help="Additional keywords to filter for",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    exit_code = run(
        days=args.days,
        output_file=args.output_file,
        extra_keywords=args.keywords,
    )
    sys.exit(exit_code)
