"""Check governance file quality — not just existence, but content depth.

Scans a repository for governance files and evaluates whether they meet
minimum quality standards: line count thresholds, required section headers,
and structural expectations (code blocks, YAML examples).

Usage:
    python content_quality_checker.py /path/to/repo
    python content_quality_checker.py . --format json
    python content_quality_checker.py /path/to/repo --format text
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# Quality rules per file category
QUALITY_RULES: Dict[str, Dict[str, Any]] = {
    "CLAUDE.md": {
        "min_lines": 10,
        "required_sections": ["session_protocol", "conventions"],
        "section_match_mode": "any",
        "description": "Agent constitution",
    },
    "README.md": {
        "min_lines": 20,
        "required_sections": [],
        "section_match_mode": "all",
        "description": "Project documentation",
    },
}

PATTERN_RULES: Dict[str, Any] = {
    "min_lines": 15,
    "required_sections": ["When to use", "Implementation"],
    "section_match_mode": "any",
    "description": "Governance pattern",
}

TEMPLATE_RULES: Dict[str, Any] = {
    "requires_code_block": True,
    "description": "Governance template",
}


def count_lines(file_path: Path) -> int:
    """Return the number of non-empty lines in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0
    return len([line for line in content.splitlines() if line.strip()])


def extract_sections(file_path: Path) -> List[str]:
    """Extract all ## header names from a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    headers = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    return [h.strip().lower() for h in headers]


def has_code_block(file_path: Path) -> bool:
    """Check whether a file contains a fenced code block or YAML example."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return bool(re.search(r"^```", content, re.MULTILINE))


def check_required_sections(
    sections: List[str],
    required: List[str],
    match_mode: str,
) -> Dict[str, bool]:
    """Check which required sections are present in the extracted headers.

    match_mode 'any': at least one required section must appear (OR).
    match_mode 'all': every required section must appear (AND).
    """
    result: Dict[str, bool] = {}
    for req in required:
        found = any(req.lower() in s for s in sections)
        result[req] = found
    return result


def grade_file(
    exists: bool,
    line_count: int,
    min_lines: int,
    section_check: Optional[Dict[str, bool]],
    match_mode: str,
    has_code: Optional[bool],
    requires_code: bool,
) -> str:
    """Assign a quality grade A/B/C/F to a governance file.

    Grading:
        F — file does not exist
        C — file exists but fails line count OR required sections
        B — file meets minimum requirements but not all extras
        A — file meets all quality criteria
    """
    if not exists:
        return "F"

    passes_lines = line_count >= min_lines
    passes_sections = True
    if section_check:
        if match_mode == "any":
            passes_sections = any(section_check.values())
        else:
            passes_sections = all(section_check.values())
    passes_code = True
    if requires_code and has_code is not None:
        passes_code = has_code

    if not passes_lines:
        return "F" if line_count == 0 else "C"
    if not passes_sections:
        return "C"
    if not passes_code:
        return "B"

    # A requires generous content
    if line_count >= min_lines * 2 and passes_sections and passes_code:
        return "A"
    return "B"


def check_governance_file(
    repo: Path,
    relative_path: str,
    rules: Dict[str, Any],
) -> Dict[str, Any]:
    """Check a single governance file against its quality rules."""
    file_path = repo / relative_path
    exists = file_path.is_file()
    line_count = count_lines(file_path) if exists else 0
    sections = extract_sections(file_path) if exists else []

    min_lines = rules.get("min_lines", 1)
    required_sections = rules.get("required_sections", [])
    match_mode = rules.get("section_match_mode", "all")
    requires_code = rules.get("requires_code_block", False)

    section_check = None
    if required_sections:
        section_check = check_required_sections(sections, required_sections, match_mode)

    code_present = has_code_block(file_path) if exists else None

    quality_grade = grade_file(
        exists=exists,
        line_count=line_count,
        min_lines=min_lines,
        section_check=section_check,
        match_mode=match_mode,
        has_code=code_present,
        requires_code=requires_code,
    )

    result: Dict[str, Any] = {
        "file": relative_path,
        "description": rules.get("description", ""),
        "exists": exists,
        "line_count": line_count,
        "min_lines_required": min_lines,
        "quality_grade": quality_grade,
    }

    if section_check is not None:
        result["has_required_sections"] = section_check

    if requires_code:
        result["has_code_block"] = code_present if code_present is not None else False

    return result


def find_pattern_files(repo: Path) -> List[str]:
    """Find all markdown files in the patterns/ directory."""
    patterns_dir = repo / "patterns"
    if not patterns_dir.is_dir():
        return []
    return [
        f"patterns/{f.name}"
        for f in sorted(patterns_dir.iterdir())
        if f.is_file() and f.suffix == ".md" and f.name != "README.md"
    ]


def find_template_files(repo: Path) -> List[str]:
    """Find all files in the templates/ directory."""
    templates_dir = repo / "templates"
    if not templates_dir.is_dir():
        return []
    return [
        f"templates/{f.name}"
        for f in sorted(templates_dir.iterdir())
        if f.is_file() and f.name != "README.md"
    ]


def run_quality_check(repo: Path) -> Dict[str, Any]:
    """Run quality checks on all governance files in the repository."""
    repo = repo.resolve()
    results: List[Dict[str, Any]] = []
    all_pass = True

    # Check core governance files
    for filename, rules in QUALITY_RULES.items():
        result = check_governance_file(repo, filename, rules)
        results.append(result)
        if result["quality_grade"] == "F":
            all_pass = False

    # Check pattern files
    pattern_files = find_pattern_files(repo)
    for pf in pattern_files:
        result = check_governance_file(repo, pf, PATTERN_RULES)
        results.append(result)
        if result["quality_grade"] == "F":
            all_pass = False

    # Check template files
    template_files = find_template_files(repo)
    for tf in template_files:
        result = check_governance_file(repo, tf, TEMPLATE_RULES)
        results.append(result)
        if result["quality_grade"] == "F":
            all_pass = False

    summary = {
        "total_files": len(results),
        "grade_a": sum(1 for r in results if r["quality_grade"] == "A"),
        "grade_b": sum(1 for r in results if r["quality_grade"] == "B"),
        "grade_c": sum(1 for r in results if r["quality_grade"] == "C"),
        "grade_f": sum(1 for r in results if r["quality_grade"] == "F"),
    }

    return {
        "repository": str(repo),
        "all_pass": all_pass,
        "summary": summary,
        "files": results,
    }


def format_text(report: Dict[str, Any]) -> str:
    """Format the quality report as human-readable text."""
    lines = [
        "Content Quality Report",
        "======================",
        f"Repository: {report['repository']}",
        "",
    ]

    for file_result in report["files"]:
        grade = file_result["quality_grade"]
        status = "PASS" if grade != "F" else "FAIL"
        lines.append(
            f"  [{grade}] {file_result['file']}: "
            f"{file_result['line_count']} lines — {status}"
        )

    lines.append("")
    s = report["summary"]
    lines.append(
        f"Summary: {s['grade_a']}A / {s['grade_b']}B / "
        f"{s['grade_c']}C / {s['grade_f']}F "
        f"({s['total_files']} files)"
    )
    lines.append(f"Overall: {'PASS' if report['all_pass'] else 'FAIL'}")

    return "\n".join(lines)


def format_json(report: Dict[str, Any]) -> str:
    """Format the quality report as JSON."""
    return json.dumps(report, indent=2)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Check governance file quality — content depth, not just existence.",
        epilog="Exit code 0 if all files pass, 1 if any file receives grade F.",
    )
    parser.add_argument(
        "repo_path",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    return parser


def main() -> int:
    """Entry point for the content quality checker."""
    parser = build_parser()
    args = parser.parse_args()

    repo = args.repo_path
    if not repo.is_dir():
        print(f"Error: {repo} is not a valid directory.", file=sys.stderr)
        return 1

    report = run_quality_check(repo)

    if args.output_format == "json":
        print(format_json(report))
    else:
        print(format_text(report))

    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
