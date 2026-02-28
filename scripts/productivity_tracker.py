#!/usr/bin/env python3
"""
productivity_tracker.py

Analyzes git log to produce a development productivity report.
Calculates commit frequency, file change rates, active hours, commit message patterns,
and a governance compliance score.

No external dependencies — uses only Python standard library and git CLI.

Usage:
    python productivity_tracker.py --days 30
    python productivity_tracker.py --since 2025-01-01
    python productivity_tracker.py --since 2025-01-01 --until 2025-02-01
    python productivity_tracker.py --days 7 --author "Jane Smith"
"""

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


# ─── Git log parsing ──────────────────────────────────────────────────────────

def run_git_command(args: list[str]) -> str:
    """Run a git command and return stdout as a string.

    Args:
        args: List of arguments to pass to git (e.g., ["log", "--oneline"])

    Returns:
        Command output as a string. Empty string if the command fails.

    Raises:
        SystemExit: If git is not available or the directory is not a git repository.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: git is not installed or not in PATH.")
        sys.exit(1)


def get_commits(since: str, until: str | None = None, author: str | None = None) -> list[dict]:
    """Fetch git commit records for the given date range.

    Args:
        since: ISO date string (YYYY-MM-DD) — fetch commits after this date
        until: ISO date string or None — fetch commits up to this date
        author: Author name/email filter, or None for all authors

    Returns:
        List of commit dicts with keys: hash, timestamp, date, hour, message,
        files_changed, insertions, deletions, author
    """
    log_args = [
        "log",
        f"--since={since}",
        "--format=%H|||%ai|||%ae|||%s",
        "--shortstat",
    ]

    if until:
        log_args.append(f"--until={until}")

    if author:
        log_args.extend(["--author", author])

    output = run_git_command(log_args)
    if not output:
        return []

    commits = []
    lines = output.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Look for a commit header line
        if "|||" in line:
            parts = line.split("|||")
            if len(parts) < 4:
                i += 1
                continue

            commit_hash = parts[0].strip()
            timestamp_str = parts[1].strip()
            author_email = parts[2].strip()
            message = parts[3].strip()

            # Parse timestamp
            try:
                # Git outputs format like: 2025-03-15 14:23:45 +0200
                dt = datetime.fromisoformat(timestamp_str)
                # Normalize to UTC-naive for comparison
                if dt.tzinfo is not None:
                    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            except ValueError:
                dt = datetime.now()

            # Look ahead for the shortstat line
            files_changed = 0
            insertions = 0
            deletions = 0

            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                stat_match = re.search(
                    r"(\d+) file[s]? changed"
                    r"(?:, (\d+) insertion[s]?\(\+\))?"
                    r"(?:, (\d+) deletion[s]?\(-\))?",
                    next_line
                )
                if stat_match:
                    files_changed = int(stat_match.group(1))
                    insertions = int(stat_match.group(2) or 0)
                    deletions = int(stat_match.group(3) or 0)
                    i += 1  # Skip the stat line

            commits.append({
                "hash": commit_hash[:8],
                "timestamp": dt,
                "date": dt.date(),
                "hour": dt.hour,
                "message": message,
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
                "author": author_email,
            })

        i += 1

    return commits


# ─── Governance compliance scoring ────────────────────────────────────────────

COMMIT_TYPE_PATTERN = re.compile(
    r"^(feat|fix|docs|refactor|test|chore|perf|style|ci|build|revert)(\(.+\))?: .{3,}$"
)

GOVERNANCE_COMMIT_PATTERN = re.compile(
    r"^docs: update project state after session"
)


def score_commit_message(message: str) -> tuple[bool, str]:
    """Check if a commit message follows the conventional commits format.

    Args:
        message: The commit message subject line

    Returns:
        Tuple of (passes, reason). passes is True if the message is compliant.
    """
    if COMMIT_TYPE_PATTERN.match(message):
        return True, "follows conventional commits format"

    if not message:
        return False, "empty message"

    # Common violations
    if message.lower().startswith(("wip", "wip:", "work in progress")):
        return False, "WIP commit — should not be merged"

    if re.match(r"^[A-Z]", message) and not re.match(r"^[a-z]+:", message):
        return False, "starts with uppercase without type prefix (use 'feat:', 'fix:', etc.)"

    if len(message.split()) < 2:
        return False, "too short — commit message should describe what changed"

    if message.endswith("."):
        return False, "ends with period — conventional commits messages do not end with periods"

    return False, f"does not match 'type: description' format (got: '{message[:50]}')"


def calculate_governance_score(commits: list[dict]) -> dict:
    """Calculate a governance compliance score from commit history.

    The score measures:
    - Commit message format compliance (50%)
    - Presence of session update commits (30%)
    - Absence of WIP commits (20%)

    Args:
        commits: List of commit dicts from get_commits()

    Returns:
        Dict with score (0-100), breakdown, and details.
    """
    if not commits:
        return {"score": 0, "message_compliance": 0, "session_updates": 0, "details": []}

    # Score 1: Commit message format compliance
    compliant_messages = 0
    message_details = []

    for commit in commits:
        passes, reason = score_commit_message(commit["message"])
        if passes:
            compliant_messages += 1
        else:
            message_details.append(f"  [{commit['hash']}] '{commit['message'][:60]}' — {reason}")

    message_compliance_pct = (compliant_messages / len(commits)) * 100

    # Score 2: Session update commits present (docs: update project state after session NNN)
    governance_commits = [
        c for c in commits if GOVERNANCE_COMMIT_PATTERN.match(c["message"])
    ]
    # Heuristic: expect at least one session update per 10 commits
    expected_governance = max(1, len(commits) // 10)
    governance_ratio = min(1.0, len(governance_commits) / expected_governance)
    governance_pct = governance_ratio * 100

    # Score 3: No WIP commits
    wip_commits = [
        c for c in commits
        if c["message"].lower().startswith(("wip", "wip:", "work in progress"))
    ]
    wip_pct = 100 - (len(wip_commits) / len(commits)) * 100

    # Weighted final score
    final_score = (
        message_compliance_pct * 0.50 +
        governance_pct * 0.30 +
        wip_pct * 0.20
    )

    return {
        "score": round(final_score),
        "message_compliance": round(message_compliance_pct),
        "session_updates": len(governance_commits),
        "wip_commits": len(wip_commits),
        "non_compliant_messages": message_details[:10],  # Top 10 violations
    }


# ─── Reporting ────────────────────────────────────────────────────────────────

def generate_report(commits: list[dict], since: str, until: str | None, author: str | None) -> str:
    """Generate the full productivity report as a formatted string.

    Args:
        commits: List of commit dicts
        since: Start date string for report header
        until: End date string or None
        author: Author filter string or None

    Returns:
        Formatted report string.
    """
    lines = []
    sep = "=" * 60

    date_range = f"{since} to {until or 'now'}"
    author_label = f" | Author: {author}" if author else ""

    lines.append(sep)
    lines.append("  AI-ASSISTED DEVELOPMENT PRODUCTIVITY REPORT")
    lines.append(sep)
    lines.append(f"  Period: {date_range}{author_label}")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(sep)
    lines.append("")

    if not commits:
        lines.append("  No commits found for the specified period and filters.")
        return "\n".join(lines)

    # ── Overview ──
    total_commits = len(commits)
    total_files = sum(c["files_changed"] for c in commits)
    total_insertions = sum(c["insertions"] for c in commits)
    total_deletions = sum(c["deletions"] for c in commits)

    # Unique active days
    active_days = len(set(c["date"] for c in commits))

    # Date range from actual commits
    dates = [c["date"] for c in commits]
    first_commit_date = min(dates)
    last_commit_date = max(dates)
    calendar_days = (last_commit_date - first_commit_date).days + 1

    lines.append("OVERVIEW")
    lines.append("-" * 40)
    lines.append(f"  Total commits:          {total_commits:>6}")
    lines.append(f"  Files changed:          {total_files:>6}")
    lines.append(f"  Lines added:            {total_insertions:>6}")
    lines.append(f"  Lines removed:          {total_deletions:>6}")
    lines.append(f"  Net lines:              {total_insertions - total_deletions:>+6}")
    lines.append(f"  Active days:            {active_days:>6}")
    lines.append(f"  Calendar days:          {calendar_days:>6}")
    lines.append("")

    # ── Velocity ──
    commits_per_active_day = total_commits / active_days if active_days > 0 else 0
    commits_per_calendar_day = total_commits / calendar_days if calendar_days > 0 else 0
    files_per_commit = total_files / total_commits if total_commits > 0 else 0

    lines.append("VELOCITY")
    lines.append("-" * 40)
    lines.append(f"  Commits per active day:     {commits_per_active_day:>5.1f}")
    lines.append(f"  Commits per calendar day:   {commits_per_calendar_day:>5.1f}")
    lines.append(f"  Files changed per commit:   {files_per_commit:>5.1f}")
    lines.append("")

    # ── Activity by day of week ──
    day_counts: Counter = Counter()
    for commit in commits:
        day_name = commit["timestamp"].strftime("%A")
        day_counts[day_name] += 1

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    lines.append("ACTIVITY BY DAY OF WEEK")
    lines.append("-" * 40)
    max_day_count = max(day_counts.values()) if day_counts else 1
    for day in day_order:
        count = day_counts.get(day, 0)
        bar_length = int((count / max_day_count) * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        lines.append(f"  {day:<10} {bar} {count:>3}")
    lines.append("")

    # ── Activity by hour ──
    hour_counts: Counter = Counter()
    for commit in commits:
        hour_counts[commit["hour"]] += 1

    lines.append("ACTIVITY BY HOUR (UTC)")
    lines.append("-" * 40)
    max_hour_count = max(hour_counts.values()) if hour_counts else 1
    peak_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:3]
    peak_label = ", ".join(f"{h:02d}:00" for h in sorted(peak_hours))
    lines.append(f"  Peak hours: {peak_label}")
    lines.append("")
    for hour in range(24):
        count = hour_counts.get(hour, 0)
        if count == 0:
            continue
        bar_length = int((count / max_hour_count) * 20)
        bar = "█" * bar_length
        lines.append(f"  {hour:02d}:00  {bar} {count}")
    lines.append("")

    # ── Commit type breakdown ──
    type_pattern = re.compile(r"^(feat|fix|docs|refactor|test|chore|perf|style|ci|build|revert)")
    type_counts: Counter = Counter()
    for commit in commits:
        match = type_pattern.match(commit["message"])
        if match:
            type_counts[match.group(1)] += 1
        else:
            type_counts["other"] += 1

    lines.append("COMMIT TYPE BREAKDOWN")
    lines.append("-" * 40)
    for commit_type, count in type_counts.most_common():
        pct = (count / total_commits) * 100
        lines.append(f"  {commit_type:<12} {count:>4}  ({pct:>4.0f}%)")
    lines.append("")

    # ── Most active files ──
    # Get per-file change counts from git
    file_counts: Counter = Counter()
    file_log = run_git_command([
        "log",
        f"--since={since}",
        "--format=",
        "--name-only",
    ] + ([f"--until={until}"] if until else [])
      + ([f"--author={author}"] if author else []))

    if file_log:
        for file_line in file_log.split("\n"):
            file_line = file_line.strip()
            if file_line:
                file_counts[file_line] += 1

    if file_counts:
        lines.append("MOST FREQUENTLY CHANGED FILES (top 10)")
        lines.append("-" * 40)
        for filepath, count in file_counts.most_common(10):
            lines.append(f"  {count:>3}x  {filepath}")
        lines.append("")

    # ── Authors (if not filtered) ──
    if not author:
        author_counts: Counter = Counter()
        for commit in commits:
            author_counts[commit["author"]] += 1

        if len(author_counts) > 1:
            lines.append("COMMITS BY AUTHOR")
            lines.append("-" * 40)
            for author_email, count in author_counts.most_common():
                pct = (count / total_commits) * 100
                lines.append(f"  {count:>4}  ({pct:>4.0f}%)  {author_email}")
            lines.append("")

    # ── Governance compliance score ──
    governance = calculate_governance_score(commits)
    score = governance["score"]

    if score >= 80:
        score_label = "GOOD"
    elif score >= 60:
        score_label = "FAIR"
    else:
        score_label = "NEEDS IMPROVEMENT"

    score_bar_filled = int(score / 5)
    score_bar = "█" * score_bar_filled + "░" * (20 - score_bar_filled)

    lines.append("GOVERNANCE COMPLIANCE SCORE")
    lines.append("-" * 40)
    lines.append(f"  Overall score: {score}/100 — {score_label}")
    lines.append(f"  {score_bar}")
    lines.append("")
    lines.append(f"  Commit message format:  {governance['message_compliance']:>3}%")
    lines.append(f"  Session update commits: {governance['session_updates']:>3}")
    lines.append(f"  WIP commits (avoid):    {governance['wip_commits']:>3}")
    lines.append("")

    if governance["non_compliant_messages"]:
        lines.append("  Non-compliant commit messages (fix these patterns):")
        for msg in governance["non_compliant_messages"][:5]:
            lines.append(msg)
        if len(governance["non_compliant_messages"]) > 5:
            remaining = len(governance["non_compliant_messages"]) - 5
            lines.append(f"  ... and {remaining} more (use --days N to narrow the range)")
        lines.append("")

    lines.append(sep)
    lines.append("")

    return "\n".join(lines)


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main() -> None:
    """Parse arguments and generate the productivity report."""
    parser = argparse.ArgumentParser(
        description="Analyze git history and produce an AI development productivity report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python productivity_tracker.py --days 30
  python productivity_tracker.py --since 2025-01-01
  python productivity_tracker.py --since 2025-01-01 --until 2025-02-01
  python productivity_tracker.py --days 7 --author "jane@example.com"
        """
    )

    # Date range options (mutually exclusive)
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Analyze the last N days of commits"
    )
    date_group.add_argument(
        "--since",
        type=str,
        metavar="YYYY-MM-DD",
        help="Analyze commits since this date"
    )

    parser.add_argument(
        "--until",
        type=str,
        metavar="YYYY-MM-DD",
        default=None,
        help="Analyze commits up to this date (default: now)"
    )

    parser.add_argument(
        "--author",
        type=str,
        default=None,
        help="Filter by author name or email"
    )

    args = parser.parse_args()

    # Resolve date range
    if args.days:
        since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    else:
        # Validate the date format
        try:
            datetime.strptime(args.since, "%Y-%m-%d")
            since_date = args.since
        except ValueError:
            print(f"Error: --since date must be in YYYY-MM-DD format (got: {args.since})")
            sys.exit(1)

    if args.until:
        try:
            datetime.strptime(args.until, "%Y-%m-%d")
        except ValueError:
            print(f"Error: --until date must be in YYYY-MM-DD format (got: {args.until})")
            sys.exit(1)

    # Verify we're in a git repository
    repo_root = run_git_command(["rev-parse", "--show-toplevel"])
    if not repo_root:
        print("Error: not a git repository (or no git history found).")
        sys.exit(1)

    print(f"Analyzing git history from {since_date}...")

    commits = get_commits(since=since_date, until=args.until, author=args.author)

    report = generate_report(
        commits=commits,
        since=since_date,
        until=args.until,
        author=args.author
    )

    print(report)


if __name__ == "__main__":
    main()
