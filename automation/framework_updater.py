"""Check for new releases of the AI Governance Framework and show available updates.

This script queries the GitHub API for releases of the ai-governance-framework
repository, compares them against the locally installed version, and presents
a structured summary of available updates. It never applies changes automatically.

Uses only the standard library (urllib) — no third-party dependencies.

Usage:
    python framework-updater.py --repo-path .
    python framework-updater.py --check-only
    python framework-updater.py --format json
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

GITHUB_OWNER = "clauseduardpetraeus"
GITHUB_REPO = "ai-governance-framework"
GITHUB_API_BASE = "https://api.github.com"
VERSION_FILE = ".governance-version"
DEFAULT_VERSION = "v1.0.0"


def parse_version(version_string: str) -> Tuple[int, int, int]:
    """Parse a semantic version string into a (major, minor, patch) tuple.

    Accepts versions with or without a leading 'v', e.g. 'v1.2.3' or '1.2.3'.
    """
    cleaned = version_string.strip().lstrip("v")
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", cleaned)
    if not match:
        raise ValueError(f"Invalid semantic version: {version_string!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _parse_next_link(link_header: str) -> Optional[str]:
    """Extract the 'next' page URL from a GitHub Link response header."""
    if not link_header:
        return None
    match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
    return match.group(1) if match else None


def find_version_file(repo_path: Path) -> Optional[Path]:
    """Search for .governance-version in repo_path and its parents up to root."""
    current = repo_path.resolve()
    while True:
        candidate = current / VERSION_FILE
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def read_local_version(repo_path: Path) -> str:
    """Read the locally installed framework version from .governance-version."""
    version_path = find_version_file(repo_path)
    if version_path is None:
        return DEFAULT_VERSION
    try:
        text = version_path.read_text().strip()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Warning: Could not read {version_path}: {exc}", file=sys.stderr)
        return DEFAULT_VERSION
    if not text:
        return DEFAULT_VERSION
    return text


def fetch_releases(owner: str = GITHUB_OWNER, repo: str = GITHUB_REPO) -> List[Dict]:
    """Fetch all releases from the GitHub API with pagination, sorted by semantic version.

    Pre-releases (e.g. v1.2.3-beta) are logged and skipped.
    Pagination via Link header is followed automatically.
    """
    url: Optional[str] = (
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases?per_page=100"
    )
    headers = {"Accept": "application/vnd.github+json"}
    all_releases: List[Dict] = []

    while url:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            page_data = json.loads(response.read().decode("utf-8"))
            all_releases.extend(page_data)
            link_header = response.headers.get("Link", "")
            url = _parse_next_link(link_header)

    valid: List[Dict] = []
    for release in all_releases:
        tag = release.get("tag_name", "")
        cleaned = tag.lstrip("v")
        # Skip pre-releases (e.g. v1.2.3-beta, v2.0.0-rc1)
        if re.match(r"^\d+\.\d+\.\d+-", cleaned):
            print(f"Warning: Skipping pre-release tag: {tag}", file=sys.stderr)
            continue
        try:
            parse_version(tag)
            valid.append(release)
        except ValueError:
            continue

    valid.sort(key=lambda r: parse_version(r["tag_name"]))
    return valid


def get_available_updates(releases: List[Dict], current_version: str) -> List[Dict]:
    """Return releases that are newer than the current version."""
    current = parse_version(current_version)
    updates: List[Dict] = []
    for release in releases:
        release_version = parse_version(release["tag_name"])
        if release_version > current:
            updates.append(release)
    return updates


def format_text(current_version: str, latest_version: str, updates: List[Dict], check_only: bool) -> str:
    """Format the update summary as human-readable text."""
    lines = [
        "AI Governance Framework Updater",
        "================================",
        f"Current version: {current_version}",
        f"Latest version: {latest_version}",
        f"Updates available: {len(updates)}",
    ]

    if check_only or not updates:
        if not updates:
            lines.append("")
            lines.append("You are up to date.")
        return "\n".join(lines)

    lines.append("")
    for release in updates:
        tag = release["tag_name"]
        published = release.get("published_at", "unknown")[:10]
        body = release.get("body", "No release notes available.") or "No release notes available."
        excerpt = body[:300]
        if len(body) > 300:
            excerpt += "..."
        lines.append(f"{tag} ({published}):")
        lines.append(f"  Release notes: {excerpt}")
        lines.append("")

    lines.append("Run with --apply to see what files would be added or updated.")
    lines.append("Note: CLAUDE.md and security configuration changes always require manual review.")
    return "\n".join(lines)


def format_json(current_version: str, latest_version: str, updates: List[Dict]) -> str:
    """Format the update summary as JSON."""
    result = {
        "current_version": current_version,
        "latest_version": latest_version,
        "updates_available": len(updates),
        "updates": [
            {
                "version": r["tag_name"],
                "published_at": r.get("published_at", ""),
                "release_notes": (r.get("body", "") or "")[:300],
                "html_url": r.get("html_url", ""),
            }
            for r in updates
        ],
    }
    return json.dumps(result, indent=2)


def show_apply_diff(updates: List[Dict]) -> str:
    """Show a summary of what --apply would do (informational only, no changes are made)."""
    lines = [
        "",
        "Apply preview (no changes are made):",
        "-------------------------------------",
    ]
    for release in updates:
        tag = release["tag_name"]
        assets = release.get("assets", [])
        lines.append(f"  {tag}: {len(assets)} asset(s) available for download")
        for asset in assets:
            lines.append(f"    - {asset['name']} ({asset.get('size', 0)} bytes)")
        if not assets:
            lines.append("    - Source archive available via GitHub release page")
        lines.append(f"    Release URL: {release.get('html_url', 'N/A')}")
    lines.append("")
    lines.append("To apply updates, download the release and manually review all changes.")
    lines.append("CLAUDE.md and security configuration changes always require manual review.")
    return "\n".join(lines)


def run(repo_path: Path, check_only: bool = False, output_format: str = "text", apply: bool = False) -> int:
    """Run the framework updater and return an exit code (0 = success)."""
    current_version = read_local_version(repo_path)

    try:
        releases = fetch_releases()
    except urllib.error.HTTPError as exc:
        print(f"Error: GitHub API returned an error: {exc}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError, socket.timeout) as exc:
        reason = str(exc)
        if isinstance(exc, socket.timeout) or "timed out" in reason.lower():
            print("Error: GitHub API request timed out. Try again later.", file=sys.stderr)
        else:
            print("Error: Could not connect to GitHub API. Check your network connection.", file=sys.stderr)
        return 1

    updates = get_available_updates(releases, current_version)
    latest_version = releases[-1]["tag_name"] if releases else current_version

    if output_format == "json":
        print(format_json(current_version, latest_version, updates))
    else:
        print(format_text(current_version, latest_version, updates, check_only))
        if apply and updates:
            print(show_apply_diff(updates))

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Check for updates to the AI Governance Framework.",
        epilog="This script never modifies governance files automatically.",
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path("."),
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only report whether updates are available, without details",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Show what files would be added or updated (does not apply changes)",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    exit_code = run(
        repo_path=args.repo_path,
        check_only=args.check_only,
        output_format=args.output_format,
        apply=args.apply,
    )
    sys.exit(exit_code)
