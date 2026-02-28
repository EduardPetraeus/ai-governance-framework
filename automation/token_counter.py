"""Estimate session token usage from git history and append entries to COST_LOG.md.

This script reads session markers from CHANGELOG.md, analyzes the git commits
associated with each session (lines added and removed), and estimates token
usage based on an average of 4 tokens per line of code. It then appends new
entries to COST_LOG.md in the correct row format.

The estimation is intentionally approximate. Token-exact counting requires SDK
instrumentation. Line-based estimation is accurate enough for trend analysis
and model routing decisions — which is the point of COST_LOG.md.

Usage:
    python3 automation/token_counter.py
    python3 automation/token_counter.py --repo-path /path/to/repo
    python3 automation/token_counter.py --dry-run
    python3 automation/token_counter.py --format json
    python3 automation/token_counter.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Calibration constants. These are tuned for typical Claude Code sessions.
# Average tokens per line of code (including context, prompts, and output).
TOKENS_PER_LINE_ADDED = 8.0
TOKENS_PER_LINE_REMOVED = 3.0

# Approximate cost per 1M tokens by model (input + output blended).
# Based on Anthropic pricing as of 2026. Update when pricing changes.
COST_PER_MILLION_TOKENS: Dict[str, float] = {
    "claude-opus-4-6": 45.0,
    "claude-sonnet-4-6": 6.0,
    "claude-haiku-4-5": 1.0,
    "claude-haiku-3-5": 1.0,
    "unknown": 6.0,  # Default to Sonnet pricing when model is unspecified.
}

# Default model assumption when the CHANGELOG entry does not specify one.
DEFAULT_MODEL = "claude-sonnet-4-6"


@dataclass
class SessionInfo:
    """Metadata extracted from a CHANGELOG.md session entry."""

    session_id: str
    date: str
    model: str
    summary: str
    tasks_completed: int = 0


@dataclass
class GitStats:
    """Lines added and removed across commits in a date range."""

    lines_added: int = 0
    lines_removed: int = 0
    commits: int = 0


@dataclass
class TokenEstimate:
    """Estimated token usage and cost for a session."""

    session_id: str
    date: str
    model: str
    lines_added: int
    lines_removed: int
    commits: int
    estimated_tokens: int
    estimated_cost_usd: float
    tasks_completed: int
    summary: str


def run_git(args: List[str], repo_path: Path) -> str:
    """Run a git command in the repo directory and return stdout. Raises on error."""
    result = subprocess.run(
        ["git"] + args,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def parse_changelog_sessions(changelog_path: Path) -> List[SessionInfo]:
    """Extract session metadata from a CHANGELOG.md file.

    Expects session headers in the format:
        ## Session NNN -- YYYY-MM-DD [model-name]
    or:
        ## Session NNN — YYYY-MM-DD [model-name]
    """
    if not changelog_path.is_file():
        return []

    content = changelog_path.read_text(encoding="utf-8")
    sessions: List[SessionInfo] = []

    # Split on session headers.
    header_pattern = re.compile(
        r"^##\s+Session\s+(\d+)\s+[-\u2013\u2014]+\s+(\d{4}-\d{2}-\d{2})"
        r"(?:\s+\[([^\]]+)\])?",
        re.MULTILINE,
    )

    matches = list(header_pattern.finditer(content))
    for i, match in enumerate(matches):
        session_id = match.group(1).zfill(3)
        date = match.group(2)
        model = match.group(3) or DEFAULT_MODEL

        # Extract the section body up to the next header.
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]

        # Count tasks from the "Completed tasks" section.
        task_count = len(re.findall(r"^\s*-\s+\*\*", body, re.MULTILINE))

        # Extract scope or first meaningful line as summary.
        scope_match = re.search(
            r"###\s+Scope\s+confirmed\s*\n(.+?)(?:\n|$)", body, re.IGNORECASE
        )
        summary = scope_match.group(1).strip() if scope_match else f"Session {session_id}"

        sessions.append(
            SessionInfo(
                session_id=session_id,
                date=date,
                model=model,
                summary=summary[:100],
                tasks_completed=task_count,
            )
        )

    return sessions


def get_git_stats_for_date(date: str, repo_path: Path) -> GitStats:
    """Return lines added and removed for all commits on a given date (YYYY-MM-DD)."""
    stats = GitStats()
    try:
        log_output = run_git(
            [
                "log",
                f"--after={date} 00:00:00",
                f"--before={date} 23:59:59",
                "--numstat",
                "--no-merges",
                "--format=COMMIT",
            ],
            repo_path,
        )
    except RuntimeError:
        return stats

    for line in log_output.splitlines():
        if line.strip() == "COMMIT":
            stats.commits += 1
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            try:
                added = int(parts[0]) if parts[0] != "-" else 0
                removed = int(parts[1]) if parts[1] != "-" else 0
                stats.lines_added += added
                stats.lines_removed += removed
            except ValueError:
                continue

    return stats


def estimate_tokens(stats: GitStats) -> int:
    """Estimate total tokens used in a session based on git line stats."""
    return int(
        stats.lines_added * TOKENS_PER_LINE_ADDED
        + stats.lines_removed * TOKENS_PER_LINE_REMOVED
    )


def estimate_cost(tokens: int, model: str) -> float:
    """Estimate USD cost for a token count given a model."""
    rate = COST_PER_MILLION_TOKENS.get(model, COST_PER_MILLION_TOKENS["unknown"])
    return round((tokens / 1_000_000) * rate, 4)


def parse_existing_log_sessions(cost_log_path: Path) -> set[str]:
    """Return session IDs already recorded in COST_LOG.md to avoid duplicates."""
    if not cost_log_path.is_file():
        return set()

    content = cost_log_path.read_text(encoding="utf-8")
    # Match session rows in the table: | 003 | ...
    # Normalize to zfill(3) to match parse_changelog_sessions() format.
    return set(m.zfill(3) for m in re.findall(r"^\|\s*(\d+)\s*\|", content, re.MULTILINE))


def format_cost_log_row(estimate: TokenEstimate) -> str:
    """Format a single TokenEstimate as a COST_LOG.md table row."""
    cost_str = f"${estimate.estimated_cost_usd:.3f}"
    notes = (
        f"~{estimate.estimated_tokens:,} tokens est. "
        f"({estimate.lines_added}+ {estimate.lines_removed}- lines, "
        f"{estimate.commits} commits)"
    )
    return (
        f"| {estimate.session_id} "
        f"| {estimate.date} "
        f"| {estimate.model} "
        f"| {estimate.tasks_completed} "
        f"| {estimate.summary[:40]} "
        f"| {cost_str} "
        f"| {notes} |"
    )


def append_to_cost_log(cost_log_path: Path, rows: List[str]) -> None:
    """Insert new rows into the Session Cost Log table in COST_LOG.md."""
    if not cost_log_path.is_file():
        print(
            f"Warning: {cost_log_path} does not exist. "
            "Copy templates/COST_LOG.md to create it.",
            file=sys.stderr,
        )
        return

    content = cost_log_path.read_text(encoding="utf-8")

    # Find the table header row and insert new rows after the header separator.
    # The table header is: | Session | Date | Model | ...
    table_header = re.search(
        r"(\|\s*Session\s*\|[^\n]+\n\|[-| ]+\|[^\n]+\n)", content
    )
    if not table_header:
        print(
            "Warning: Could not locate the Session Cost Log table in COST_LOG.md. "
            "Appending rows at end of file.",
            file=sys.stderr,
        )
        with open(cost_log_path, "a", encoding="utf-8") as fh:
            for row in rows:
                fh.write(row + "\n")
        return

    insert_pos = table_header.end()
    new_rows_text = "\n".join(rows) + "\n"
    updated = content[:insert_pos] + new_rows_text + content[insert_pos:]
    cost_log_path.write_text(updated, encoding="utf-8")


def compute_estimates(
    sessions: List[SessionInfo],
    existing_ids: set[str],
    repo_path: Path,
) -> List[TokenEstimate]:
    """Compute token estimates for sessions not yet in the cost log."""
    estimates: List[TokenEstimate] = []

    for session in sessions:
        if session.session_id in existing_ids:
            continue  # Already logged — skip.

        stats = get_git_stats_for_date(session.date, repo_path)
        tokens = estimate_tokens(stats)
        cost = estimate_cost(tokens, session.model)

        estimates.append(
            TokenEstimate(
                session_id=session.session_id,
                date=session.date,
                model=session.model,
                lines_added=stats.lines_added,
                lines_removed=stats.lines_removed,
                commits=stats.commits,
                estimated_tokens=tokens,
                estimated_cost_usd=cost,
                tasks_completed=session.tasks_completed,
                summary=session.summary,
            )
        )

    return estimates


def run(
    repo_path: Path,
    dry_run: bool = False,
    output_format: str = "text",
) -> int:
    """Main entry point: parse CHANGELOG, compute estimates, update COST_LOG."""
    changelog_path = repo_path / "CHANGELOG.md"
    cost_log_path = repo_path / "COST_LOG.md"

    sessions = parse_changelog_sessions(changelog_path)
    if not sessions:
        print(
            "No sessions found in CHANGELOG.md. "
            "Ensure CHANGELOG.md exists and uses the standard session header format.",
            file=sys.stderr,
        )
        return 0

    existing_ids = parse_existing_log_sessions(cost_log_path)
    estimates = compute_estimates(sessions, existing_ids, repo_path)

    if not estimates:
        if output_format == "json":
            print(json.dumps({"message": "All sessions already logged.", "new_entries": 0}))
        else:
            print("All sessions are already recorded in COST_LOG.md. Nothing to add.")
        return 0

    if output_format == "json":
        output = {
            "new_entries": len(estimates),
            "dry_run": dry_run,
            "estimates": [
                {
                    "session_id": e.session_id,
                    "date": e.date,
                    "model": e.model,
                    "lines_added": e.lines_added,
                    "lines_removed": e.lines_removed,
                    "commits": e.commits,
                    "estimated_tokens": e.estimated_tokens,
                    "estimated_cost_usd": e.estimated_cost_usd,
                    "tasks_completed": e.tasks_completed,
                    "summary": e.summary,
                }
                for e in estimates
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"New sessions to log: {len(estimates)}")
        for est in estimates:
            print(
                f"  Session {est.session_id} ({est.date}): "
                f"~{est.estimated_tokens:,} tokens, "
                f"${est.estimated_cost_usd:.3f} [{est.model}]"
            )

    if dry_run:
        print("\nDry run — COST_LOG.md was not modified.")
        return 0

    rows = [format_cost_log_row(e) for e in estimates]
    append_to_cost_log(cost_log_path, rows)

    if output_format == "text":
        print(f"\n{len(rows)} row(s) appended to COST_LOG.md.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Estimate session token usage from git history and "
            "append entries to COST_LOG.md."
        ),
        epilog=(
            "Run after each session or as a post-commit hook: "
            "python3 automation/token_counter.py --repo-path ."
        ),
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path("."),
        metavar="PATH",
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute estimates but do not modify COST_LOG.md",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    repo_path = args.repo_path.resolve()
    if not repo_path.is_dir():
        print(f"Error: {repo_path} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    sys.exit(run(repo_path, dry_run=args.dry_run, output_format=args.output_format))
