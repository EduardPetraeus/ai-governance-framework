"""Calculate the governance health score for a repository.

This script scans a repository for governance files and configuration,
then produces a score from 0 to 100 based on maturity model criteria.
It can serve as a CI/CD health gate by returning exit code 1 when the
score falls below a configurable threshold.

Usage:
    python health-score-calculator.py .
    python health-score-calculator.py /path/to/repo --threshold 40
    python health-score-calculator.py . --format json --output-file report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REQUIRED_CLAUDE_SECTIONS = [
    "project_context",
    "conventions",
    "mandatory_session_protocol",
    "security_protocol",
    "mandatory_task_reporting",
]

MATURITY_LEVELS = [
    (0, 20, 0, "Ad-hoc"),
    (20, 40, 1, "Foundation"),
    (40, 60, 2, "Structured"),
    (60, 80, 3, "Enforced"),
    (80, 95, 4, "Measured"),
    (95, 101, 5, "Self-optimizing"),
]


def get_maturity_level(score: int) -> Tuple[int, str]:
    """Return the maturity level number and label for a given score."""
    for low, high, level, label in MATURITY_LEVELS:
        if low <= score < high:
            return level, label
    return 0, "Ad-hoc"


def check_file_exists(repo: Path, relative_path: str) -> bool:
    """Check whether a file exists relative to the repo root."""
    return (repo / relative_path).is_file()


def check_dir_has_files(repo: Path, relative_path: str, min_count: int = 1) -> bool:
    """Check whether a directory exists and contains at least min_count files."""
    directory = repo / relative_path
    if not directory.is_dir():
        return False
    files = [f for f in directory.iterdir() if f.is_file()]
    return len(files) >= min_count


def check_claude_sections(repo: Path) -> List[str]:
    """Return the list of required sections found in CLAUDE.md."""
    claude_path = repo / "CLAUDE.md"
    if not claude_path.is_file():
        return []
    try:
        content = claude_path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return []
    found = []
    for section in REQUIRED_CLAUDE_SECTIONS:
        pattern = rf"(^|\n)#+\s*{re.escape(section)}|^\s*{re.escape(section)}\s*$|(##\s+{re.escape(section)})"
        if re.search(pattern, content, re.MULTILINE):
            found.append(section)
    return found


def count_changelog_entries(repo: Path) -> int:
    """Count the number of entries in CHANGELOG.md (lines starting with ## or ###)."""
    changelog_path = repo / "CHANGELOG.md"
    if not changelog_path.is_file():
        return 0
    try:
        content = changelog_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0
    entries = re.findall(r"^#{2,3}\s+.+", content, re.MULTILINE)
    return len(entries)


def check_ai_review_workflow(repo: Path) -> bool:
    """Check if any workflow file references Anthropic or Claude."""
    workflows_dir = repo / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return False
    for workflow_file in workflows_dir.iterdir():
        if not workflow_file.is_file():
            continue
        try:
            content = workflow_file.read_text(encoding="utf-8").lower()
            if "anthropic" in content or "claude" in content:
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def check_gitignore_has_env(repo: Path) -> bool:
    """Check if .gitignore exists and contains a line for .env."""
    gitignore_path = repo / ".gitignore"
    if not gitignore_path.is_file():
        return False
    try:
        content = gitignore_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == ".env" or stripped == ".env*" or stripped == ".env/":
            return True
    return False


def check_agents_dir(repo: Path) -> bool:
    """Check for agent definitions in .claude/agents/ or agents/."""
    return check_dir_has_files(repo, ".claude/agents") or check_dir_has_files(repo, "agents")


def check_commands_dir(repo: Path) -> bool:
    """Check for command definitions in .claude/commands/ or commands/."""
    return check_dir_has_files(repo, ".claude/commands") or check_dir_has_files(repo, "commands")


def calculate_score(repo: Path) -> Dict[str, Any]:
    """Calculate the governance health score and return a detailed report."""
    repo = repo.resolve()
    checks: List[Dict[str, Any]] = []

    # CLAUDE.md exists: +10
    claude_exists = check_file_exists(repo, "CLAUDE.md")
    checks.append({
        "name": "CLAUDE.md exists",
        "passed": claude_exists,
        "points": 10,
    })

    # CLAUDE.md has required sections: +2 each (max 10)
    found_sections = check_claude_sections(repo)
    for section in REQUIRED_CLAUDE_SECTIONS:
        present = section in found_sections
        checks.append({
            "name": f"CLAUDE.md section: {section}",
            "passed": present,
            "points": 2,
        })

    # PROJECT_PLAN.md exists: +5
    checks.append({
        "name": "PROJECT_PLAN.md exists",
        "passed": check_file_exists(repo, "PROJECT_PLAN.md"),
        "points": 5,
    })

    # CHANGELOG.md exists with at least 3 entries: +10
    changelog_count = count_changelog_entries(repo)
    checks.append({
        "name": "CHANGELOG.md with 3+ entries",
        "passed": changelog_count >= 3,
        "points": 10,
    })

    # ARCHITECTURE.md exists: +5
    checks.append({
        "name": "ARCHITECTURE.md exists",
        "passed": check_file_exists(repo, "ARCHITECTURE.md"),
        "points": 5,
    })

    # MEMORY.md exists: +5
    checks.append({
        "name": "MEMORY.md exists",
        "passed": check_file_exists(repo, "MEMORY.md"),
        "points": 5,
    })

    # At least 1 ADR in docs/adr/: +5
    checks.append({
        "name": "At least 1 ADR in docs/adr/",
        "passed": check_dir_has_files(repo, "docs/adr"),
        "points": 5,
    })

    # .pre-commit-config.yaml exists: +10
    checks.append({
        "name": ".pre-commit-config.yaml exists",
        "passed": check_file_exists(repo, ".pre-commit-config.yaml"),
        "points": 10,
    })

    # .github/workflows/ has at least 1 file: +5
    checks.append({
        "name": "GitHub Actions workflow exists",
        "passed": check_dir_has_files(repo, ".github/workflows"),
        "points": 5,
    })

    # AI review workflow: +10
    checks.append({
        "name": "AI review workflow (anthropic/claude)",
        "passed": check_ai_review_workflow(repo),
        "points": 10,
    })

    # At least 1 agent: +5
    checks.append({
        "name": "Agent definition exists",
        "passed": check_agents_dir(repo),
        "points": 5,
    })

    # At least 1 command: +5
    checks.append({
        "name": "Command definition exists",
        "passed": check_commands_dir(repo),
        "points": 5,
    })

    # patterns/ directory with at least 1 file: +5
    checks.append({
        "name": "patterns/ directory with files",
        "passed": check_dir_has_files(repo, "patterns"),
        "points": 5,
    })

    # automation/ directory exists: +5
    checks.append({
        "name": "automation/ directory exists",
        "passed": (repo / "automation").is_dir(),
        "points": 5,
    })

    # .gitignore contains .env: +5
    checks.append({
        "name": ".gitignore includes .env",
        "passed": check_gitignore_has_env(repo),
        "points": 5,
    })

    score = sum(c["points"] for c in checks if c["passed"])
    max_score = sum(c["points"] for c in checks)
    level_num, level_label = get_maturity_level(score)

    return {
        "repository": str(repo),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "score": score,
        "max_score": max_score,
        "level": level_num,
        "level_label": level_label,
        "checks": checks,
    }


def format_text(report: Dict[str, Any]) -> str:
    """Format the health score report as human-readable text."""
    lines = [
        "Governance Health Score",
        "=======================",
        f"Repository: {report['repository']}",
        f"Date: {report['date']}",
        f"Score: {report['score']}/{report['max_score']}",
        "",
        "What's present:",
    ]

    for check in report["checks"]:
        if check["passed"]:
            lines.append(f"  \u2705 {check['name']}: +{check['points']} points")

    lines.append("")
    lines.append("What's missing:")

    for check in report["checks"]:
        if not check["passed"]:
            lines.append(f"  \u274c {check['name']}: +{check['points']} points if implemented")

    lines.append("")
    lines.append(f"Overall level: Level {report['level']} ({report['level_label']})")
    lines.append("")
    lines.append("Level thresholds:")
    lines.append("  0-19:   Level 0 (Ad-hoc)")
    lines.append("  20-39:  Level 1 (Foundation)")
    lines.append("  40-59:  Level 2 (Structured)")
    lines.append("  60-79:  Level 3 (Enforced)")
    lines.append("  80-94:  Level 4 (Measured)")
    lines.append("  95-100: Level 5 (Self-optimizing)")
    lines.append("")
    lines.append("To improve your score, see: docs/maturity-model.md")

    return "\n".join(lines)


def format_json(report: Dict[str, Any]) -> str:
    """Format the health score report as JSON."""
    return json.dumps(report, indent=2)


def run(
    repo_path: Path,
    threshold: int = 0,
    output_format: str = "text",
    output_file: Optional[str] = None,
) -> int:
    """Run the health score calculator and return an exit code."""
    if not repo_path.is_dir():
        print(f"Error: {repo_path} is not a valid directory.", file=sys.stderr)
        return 1

    report = calculate_score(repo_path)

    if output_format == "json":
        output = format_json(report)
    else:
        output = format_text(report)

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)
                f.write("\n")
            print(f"Report written to {output_file}")
        except OSError as exc:
            print(f"Error: Could not write to {output_file}: {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    if threshold > 0 and report["score"] < threshold:
        print(
            f"\nGovernance health gate FAILED: score {report['score']} "
            f"is below threshold {threshold}.",
            file=sys.stderr,
        )
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Calculate the governance health score for a repository.",
        epilog="Use --threshold to enforce a minimum score in CI/CD pipelines.",
    )
    parser.add_argument(
        "repo_path",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=0,
        help="Exit with code 1 if score is below this value (default: 0, no threshold)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Save report to a file (default: print to stdout)",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    exit_code = run(
        repo_path=args.repo_path,
        threshold=args.threshold,
        output_format=args.output_format,
        output_file=args.output_file,
    )
    sys.exit(exit_code)
