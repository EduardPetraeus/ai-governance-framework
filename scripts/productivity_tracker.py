#!/usr/bin/env python3
"""
productivity_tracker.py — Git-based productivity metrics calculator.

Reads git log via subprocess and produces a formatted report covering commit
velocity, hour-of-day distribution, commit type breakdown, most-changed files,
per-author stats, and a governance compliance score.

Pure Python 3 standard library — no external dependencies.

Usage:
    python productivity_tracker.py --days 30
    python productivity_tracker.py --since 2025-01-01
    python productivity_tracker.py --since 2025-01-01 --until 2025-02-01
    python productivity_tracker.py --all
    python productivity_tracker.py --days 7 --author "Jane Smith"
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


# ─── Constants ───────────────────────────────────────────────────────────────

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(feat|fix|docs|refactor|test|chore|perf|security|style|ci|build|revert)"
    r"(\([^)]+\))?: .+"
)

COMMIT_TYPE_RE = re.compile(
    r"^(feat|fix|docs|refactor|test|chore|perf|security|style|ci|build|revert)"
)

BAR_WIDTH = 30
SEPARATOR = "=" * 64


# ─── Git interaction ─────────────────────────────────────────────────────────


def run_git(args: list) -> str:
    """Run a git command and return stdout. Returns empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: git is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)


def verify_git_repo() -> None:
    """Exit with a clear message if we are not inside a git repository."""
    root = run_git(["rev-parse", "--show-toplevel"])
    if not root:
        print("Error: not inside a git repository.", file=sys.stderr)
        sys.exit(1)


# ─── Commit parsing ─────────────────────────────────────────────────────────


def get_commits(
    since: str,
    until: str | None = None,
    author: str | None = None,
) -> list[dict]:
    """Fetch commits from git log for the given date range.

    Returns a list of dicts with keys: hash, timestamp, date, hour, message,
    files_changed, insertions, deletions, author, branch.
    """
    # Use a delimiter that will not appear in commit messages
    delim = "|||"
    fmt = f"%H{delim}%ai{delim}%an{delim}%s{delim}%D"

    log_args = ["log", f"--since={since}", f"--format={fmt}", "--shortstat"]

    if until:
        log_args.append(f"--until={until}")
    if author:
        log_args.extend(["--author", author])

    output = run_git(log_args)
    if not output:
        return []

    commits = []
    lines = output.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line or delim not in line:
            i += 1
            continue

        parts = line.split(delim)
        if len(parts) < 5:
            i += 1
            continue

        commit_hash = parts[0].strip()
        timestamp_str = parts[1].strip()
        author_name = parts[2].strip()
        message = parts[3].strip()
        refs = parts[4].strip()

        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp_str)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            dt = datetime.now()

        # Determine if this was a direct commit to main/master
        is_main = (
            any(
                b in refs
                for b in (
                    "HEAD -> main",
                    "HEAD -> master",
                    "origin/main",
                    "origin/master",
                )
            )
            if refs
            else False
        )

        # Parse shortstat on the next non-empty line
        files_changed = 0
        insertions = 0
        deletions = 0

        if i + 1 < len(lines):
            stat_line = lines[i + 1].strip()
            stat_match = re.search(
                r"(\d+) files? changed"
                r"(?:, (\d+) insertions?\(\+\))?"
                r"(?:, (\d+) deletions?\(-\))?",
                stat_line,
            )
            if stat_match:
                files_changed = int(stat_match.group(1))
                insertions = int(stat_match.group(2) or 0)
                deletions = int(stat_match.group(3) or 0)
                i += 1

        commits.append(
            {
                "hash": commit_hash[:8],
                "timestamp": dt,
                "date": dt.date(),
                "hour": dt.hour,
                "message": message,
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
                "author": author_name,
                "is_main_commit": is_main,
            }
        )

        i += 1

    return commits


# ─── Report sections ─────────────────────────────────────────────────────────


def _bar(value: int, max_value: int, width: int = BAR_WIDTH) -> str:
    """Render a proportional ASCII bar."""
    if max_value == 0:
        return "░" * width
    filled = int((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


def section_overview(commits: list[dict]) -> list[str]:
    """Section 1: Overview statistics."""
    lines = ["OVERVIEW", "-" * 44]

    total = len(commits)
    dates = sorted(set(c["date"] for c in commits))
    active_days = len(dates)
    first_date = min(dates)
    last_date = max(dates)
    avg_per_day = total / active_days if active_days else 0

    # Most productive day
    day_counts = Counter(c["date"] for c in commits)
    best_day, best_count = day_counts.most_common(1)[0]

    lines.append(f"  Date range:            {first_date} to {last_date}")
    lines.append(f"  Total commits:         {total:>6}")
    lines.append(f"  Unique active days:    {active_days:>6}")
    lines.append(f"  Avg commits/active day:{avg_per_day:>6.1f}")
    lines.append(f"  Most productive day:   {best_day} ({best_count} commits)")
    lines.append("")

    return lines


def section_velocity_chart(commits: list[dict]) -> list[str]:
    """Section 2: ASCII bar chart — one row per day with commits."""
    lines = ["VELOCITY CHART", "-" * 44]

    day_counts = Counter(c["date"] for c in commits)
    if not day_counts:
        lines.append("  No data.")
        lines.append("")
        return lines

    max_count = max(day_counts.values())

    for day in sorted(day_counts.keys()):
        count = day_counts[day]
        bar = _bar(count, max_count, 20)
        lines.append(f"  {day} │{bar}│ {count:>3}")

    lines.append("")
    return lines


def section_hour_distribution(commits: list[dict]) -> list[str]:
    """Section 3: 24-slot hour-of-day distribution."""
    lines = ["HOUR-OF-DAY DISTRIBUTION", "-" * 44]

    hour_counts = Counter(c["hour"] for c in commits)
    if not hour_counts:
        lines.append("  No data.")
        lines.append("")
        return lines

    max_count = max(hour_counts.values())

    # Show all 24 hours so the pattern is visible, but mark empty ones lightly
    for hour in range(24):
        count = hour_counts.get(hour, 0)
        if count == 0:
            lines.append(f"  {hour:02d}:00  {'·' * 20}   0")
        else:
            bar = _bar(count, max_count, 20)
            lines.append(f"  {hour:02d}:00  {bar} {count:>3}")

    # Identify peak hours
    peak_hours = sorted(hour_counts, key=hour_counts.get, reverse=True)[:3]
    peak_str = ", ".join(f"{h:02d}:00" for h in sorted(peak_hours))
    lines.append(f"  Peak: {peak_str}")
    lines.append("")

    return lines


def section_commit_types(commits: list[dict]) -> list[str]:
    """Section 4: Breakdown by conventional commit type."""
    lines = ["COMMIT TYPE BREAKDOWN", "-" * 44]

    type_counts = Counter()
    total = len(commits)

    for c in commits:
        match = COMMIT_TYPE_RE.match(c["message"])
        if match:
            type_counts[match.group(1)] += 1
        else:
            type_counts["other"] += 1

    for ctype, count in type_counts.most_common():
        pct = (count / total) * 100
        lines.append(f"  {ctype:<12} {count:>4}  ({pct:>5.1f}%)")

    lines.append("")
    return lines


def section_most_changed_files(
    since: str, until: str | None, author: str | None
) -> list[str]:
    """Section 5: Top 10 files appearing in most commits."""
    lines = ["MOST-CHANGED FILES (top 10)", "-" * 44]

    log_args = ["log", f"--since={since}", "--format=", "--name-only"]
    if until:
        log_args.append(f"--until={until}")
    if author:
        log_args.extend(["--author", author])

    output = run_git(log_args)
    if not output:
        lines.append("  No file data available.")
        lines.append("")
        return lines

    file_counts = Counter()
    for f in output.split("\n"):
        f = f.strip()
        if f:
            file_counts[f] += 1

    for filepath, count in file_counts.most_common(10):
        lines.append(f"  {count:>4}x  {filepath}")

    lines.append("")
    return lines


def section_per_author(commits: list[dict]) -> list[str]:
    """Section 6: Per-author breakdown (only if multiple authors)."""
    author_commits = defaultdict(list)
    for c in commits:
        author_commits[c["author"]].append(c)

    if len(author_commits) <= 1:
        return []

    lines = ["PER-AUTHOR BREAKDOWN", "-" * 44]
    total = len(commits)

    for author, author_coms in sorted(author_commits.items(), key=lambda x: -len(x[1])):
        count = len(author_coms)
        pct = (count / total) * 100

        # Commit type breakdown for this author
        type_counts = Counter()
        for c in author_coms:
            match = COMMIT_TYPE_RE.match(c["message"])
            if match:
                type_counts[match.group(1)] += 1
            else:
                type_counts["other"] += 1

        type_summary = ", ".join(f"{t}:{n}" for t, n in type_counts.most_common(3))

        lines.append(f"  {author}")
        lines.append(
            f"    Commits: {count:>4} ({pct:>5.1f}%)  |  Top types: {type_summary}"
        )

    lines.append("")
    return lines


def section_governance_score(commits: list[dict]) -> list[str]:
    """Section 7: Governance compliance score (0-100) with breakdown.

    Scoring:
      +40  Percentage of commits following conventional commits format (scaled to 40)
      +20  CHANGELOG.md updated in >60% of active days
      +15  No direct main/master branch commits
      +15  Average session size (commits per active day) between 5-20
      +10  Average commit message length >20 characters
    """
    lines = ["GOVERNANCE COMPLIANCE SCORE", "-" * 44]
    total = len(commits)

    # --- Component 1: Conventional commits format (max 40) ---
    conventional_count = sum(
        1 for c in commits if CONVENTIONAL_COMMIT_RE.match(c["message"])
    )
    conventional_pct = (conventional_count / total) * 100
    score_format = round((conventional_count / total) * 40)
    detail_format = f"  Conventional commits:   {conventional_count}/{total} ({conventional_pct:.0f}%) = {score_format}/40"

    # --- Component 2: CHANGELOG.md updates (max 20) ---
    # Check if CHANGELOG.md appears in file changes on >60% of active days
    active_dates = set(c["date"] for c in commits)
    changelog_log = run_git(
        [
            "log",
            f"--since={min(active_dates).isoformat()}",
            "--format=%ai",
            "--diff-filter=M",
            "--",
            "CHANGELOG.md",
        ]
    )

    changelog_days = set()
    if changelog_log:
        for line in changelog_log.strip().split("\n"):
            line = line.strip()
            if line:
                try:
                    dt = datetime.fromisoformat(line)
                    changelog_days.add(dt.date())
                except ValueError:
                    pass

    changelog_ratio = len(changelog_days) / len(active_dates) if active_dates else 0
    score_changelog = 20 if changelog_ratio > 0.6 else round(changelog_ratio / 0.6 * 20)
    detail_changelog = (
        f"  CHANGELOG.md coverage:  {len(changelog_days)}/{len(active_dates)} days "
        f"({changelog_ratio:.0%}) = {score_changelog}/20"
    )

    # --- Component 3: No direct main/master commits (max 15) ---
    main_commits = sum(1 for c in commits if c.get("is_main_commit", False))
    score_no_main = 15 if main_commits == 0 else max(0, 15 - main_commits)
    detail_no_main = (
        f"  No main branch commits: {main_commits} direct commits = {score_no_main}/15"
    )

    # --- Component 4: Session size between 5-20 (max 15) ---
    day_counts = Counter(c["date"] for c in commits)
    avg_session_size = total / len(day_counts) if day_counts else 0
    if 5 <= avg_session_size <= 20:
        score_session = 15
    elif avg_session_size < 5:
        score_session = round((avg_session_size / 5) * 15)
    else:
        # Penalize increasingly above 20, but floor at 0
        score_session = max(0, round(15 - (avg_session_size - 20)))
    detail_session = f"  Avg session size:       {avg_session_size:.1f} commits/day = {score_session}/15"

    # --- Component 5: Descriptive messages >20 chars (max 10) ---
    long_msgs = sum(1 for c in commits if len(c["message"]) > 20)
    long_pct = (long_msgs / total) * 100
    score_msgs = round((long_msgs / total) * 10)
    detail_msgs = f"  Message length >20ch:   {long_msgs}/{total} ({long_pct:.0f}%) = {score_msgs}/10"

    # --- Total ---
    total_score = (
        score_format + score_changelog + score_no_main + score_session + score_msgs
    )
    total_score = min(100, max(0, total_score))

    if total_score >= 85:
        label = "Excellent"
    elif total_score >= 70:
        label = "Good"
    elif total_score >= 50:
        label = "Fair"
    else:
        label = "Poor"

    score_bar = _bar(total_score, 100, 20)

    lines.append(f"  Score: {total_score}/100 — {label}")
    lines.append(f"  {score_bar}")
    lines.append("")
    lines.append(detail_format)
    lines.append(detail_changelog)
    lines.append(detail_no_main)
    lines.append(detail_session)
    lines.append(detail_msgs)
    lines.append("")

    return lines


# ─── Report assembly ─────────────────────────────────────────────────────────


def generate_report(
    commits: list[dict],
    since: str,
    until: str | None,
    author: str | None,
) -> str:
    """Assemble the full productivity report."""
    lines = []

    date_range = f"{since} to {until or 'now'}"
    author_label = f"  Author filter: {author}" if author else ""

    lines.append(SEPARATOR)
    lines.append("  AI-ASSISTED DEVELOPMENT — PRODUCTIVITY REPORT")
    lines.append(SEPARATOR)
    lines.append(f"  Period: {date_range}")
    if author_label:
        lines.append(author_label)
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(SEPARATOR)
    lines.append("")

    if not commits:
        lines.append("  No commits found for the specified period and filters.")
        lines.append("")
        lines.append("  Possible causes:")
        lines.append("    - The date range contains no commits")
        lines.append("    - The author filter does not match any committer")
        lines.append("    - The repository has no history yet")
        lines.append("")
        return "\n".join(lines)

    lines.extend(section_overview(commits))
    lines.extend(section_velocity_chart(commits))
    lines.extend(section_hour_distribution(commits))
    lines.extend(section_commit_types(commits))
    lines.extend(section_most_changed_files(since, until, author))
    lines.extend(section_per_author(commits))
    lines.extend(section_governance_score(commits))

    lines.append(SEPARATOR)
    lines.append("")

    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────


def parse_date(value: str) -> str:
    """Validate and return a YYYY-MM-DD date string."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        print(
            f"Error: invalid date format '{value}'. Expected YYYY-MM-DD.",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    """Parse arguments and generate the productivity report."""
    parser = argparse.ArgumentParser(
        description="Analyze git history and produce a development productivity report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python productivity_tracker.py --days 30\n"
            "  python productivity_tracker.py --since 2025-01-01\n"
            "  python productivity_tracker.py --since 2025-01-01 --until 2025-02-01\n"
            "  python productivity_tracker.py --all\n"
            "  python productivity_tracker.py --days 7 --author 'Jane Smith'\n"
        ),
    )

    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Analyze the last N days of commits",
    )
    date_group.add_argument(
        "--since",
        type=str,
        metavar="YYYY-MM-DD",
        help="Analyze commits from this date forward",
    )
    date_group.add_argument(
        "--all",
        action="store_true",
        help="Analyze entire repository history",
    )

    parser.add_argument(
        "--until",
        type=str,
        metavar="YYYY-MM-DD",
        default=None,
        help="Analyze commits up to this date (default: now)",
    )
    parser.add_argument(
        "--author",
        type=str,
        default=None,
        help="Filter commits by author name or email",
    )

    args = parser.parse_args()

    # Resolve the start date
    if args.all:
        # Use the epoch as a since date to capture everything
        since_date = "1970-01-01"
    elif args.days:
        if args.days <= 0:
            print("Error: --days must be a positive integer.", file=sys.stderr)
            sys.exit(1)
        since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    else:
        since_date = parse_date(args.since)

    # Validate --until if provided
    until_date = None
    if args.until:
        until_date = parse_date(args.until)

    verify_git_repo()

    commits = get_commits(since=since_date, until=until_date, author=args.author)

    report = generate_report(
        commits=commits,
        since=since_date,
        until=until_date,
        author=args.author,
    )

    print(report)


if __name__ == "__main__":
    main()
