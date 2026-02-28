"""Validate constitutional inheritance in a CLAUDE.md file.

Reads a CLAUDE.md, extracts the inherits_from section, fetches each parent
constitution (by local path or URL), then validates three invariants:

  1. The local file does not remove a section that is required by a parent.
  2. The local file does not grant permissions that a parent explicitly prohibits.
  3. The local file does not lower a numeric threshold set by a parent.

Exits with code 1 if any violation is found (default) or always exits 0 when
--threshold warn is passed. Use --format json for machine-readable output.

Usage:
    python3 automation/inherits_from_validator.py CLAUDE.md
    python3 automation/inherits_from_validator.py CLAUDE.md --parent templates/CLAUDE.org.md
    python3 automation/inherits_from_validator.py CLAUDE.md --format json
    python3 automation/inherits_from_validator.py CLAUDE.md --threshold warn
    python3 automation/inherits_from_validator.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Sections in a parent constitution that a child must preserve.
REQUIRED_SECTION_KEYWORDS: List[str] = [
    "security_protocol",
    "mandatory_session_protocol",
    "quality_standards",
    "conventions",
]

# Regex phrases that, if present in a parent, constitute a prohibition.
# If the local file appears to grant the same capability, it is a violation.
PROHIBITION_PATTERNS: List[Tuple[str, str]] = [
    # (prohibition_regex_in_parent, grant_regex_in_local)
    (
        r"(?i)(never|prohibited?|forbidden|disallow)\s+\w*\s*(force.{0,10}push|push.*--force)",
        r"(?i)(allow|enable|permitted)\s+\w*\s*(force.{0,10}push|push.*--force)",
    ),
    (
        r"(?i)(never|prohibited?|forbidden)\s+\w*\s*(skip|bypass)\s+\w*\s*(review|ci|check)",
        r"(?i)(allow|enable)\s+\w*\s*(skip|bypass)\s+\w*\s*(review|ci|check)",
    ),
    (
        r"(?i)(never|prohibited?)\s+\w*\s*commit\s+\w*\s*(secret|credential|key|password)",
        r"(?i)(allow|ok|acceptable)\s+\w*\s*commit\s+\w*\s*(secret|credential|key|password)",
    ),
    (
        r"(?i)(never|no)\s+\w*\s*(auto.commit|automatic.commit|commit\s+without)",
        r"(?i)(auto.commit|commit\s+automatically|automatically\s+commit)",
    ),
]

# Threshold patterns: extract a numeric value from surrounding context.
# If the parent sets a higher value and the local sets a lower one, it is a violation.
THRESHOLD_PATTERNS: List[Tuple[str, str]] = [
    (r"(?i)blast.radius.{0,30}?(\d+)\s*files", "blast_radius_files"),
    (r"(?i)max(?:imum)?.{0,20}?(\d+)\s*files", "max_files"),
    (r"(?i)max(?:imum)?.{0,20}?(\d+)\s*lines", "max_lines"),
    (r"(?i)confidence.{0,20}?(\d+)\s*%", "confidence_percent"),
    (r"(?i)threshold.{0,20}?(\d+)", "threshold_generic"),
    (r"(?i)minimum.{0,20}?(\d+)", "minimum_generic"),
]


def fetch_constitution(source: str, base_dir: Path) -> Optional[str]:
    """Fetch a constitution from a URL or local path. Returns None on failure."""
    if source.startswith(("http://", "https://")):
        try:
            with urllib.request.urlopen(source, timeout=15) as response:
                return response.read().decode("utf-8")
        except Exception as exc:
            print(f"Warning: could not fetch {source}: {exc}", file=sys.stderr)
            return None

    # Local path: try relative to base_dir first, then absolute.
    for candidate in (base_dir / source, Path(source)):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")

    print(f"Warning: local path not found: {source}", file=sys.stderr)
    return None


def extract_inherits_from(content: str) -> List[str]:
    """Extract parent source references from the inherits_from section.

    Supports both scalar and list YAML syntax:

        inherits_from: path/or/url

        inherits_from:
          - path/or/url
          - https://example.com/CLAUDE.org.md
    """
    sources: List[str] = []

    # Scalar: inherits_from: value (not starting with -)
    scalar = re.search(r"^inherits_from\s*:\s*(?!-)(.+)$", content, re.MULTILINE)
    if scalar:
        value = scalar.group(1).strip().strip("\"'")
        if value:
            sources.append(value)

    # List: inherits_from:\n  - item\n  - item
    list_block = re.search(
        r"^inherits_from\s*:\s*\n((?:[ \t]+-[ \t]+.+\n?)+)", content, re.MULTILINE
    )
    if list_block:
        for line in list_block.group(1).splitlines():
            item = line.strip()
            if item.startswith("-"):
                sources.append(item[1:].strip().strip("\"'"))

    return sources


def extract_sections(content: str) -> Dict[str, str]:
    """Extract Markdown sections from a CLAUDE.md as {normalized_name: body}."""
    sections: Dict[str, str] = {}
    current_name: Optional[str] = None
    current_lines: List[str] = []

    for line in content.splitlines():
        heading = re.match(r"^(#{1,3})\s+(.+)", line)
        if heading:
            if current_name is not None:
                sections[current_name] = "\n".join(current_lines)
            raw_name = heading.group(2).strip()
            current_name = re.sub(r"\W+", "_", raw_name).lower().strip("_")
            current_lines = [line]
        else:
            if current_name is not None:
                current_lines.append(line)

    if current_name is not None:
        sections[current_name] = "\n".join(current_lines)

    return sections


def extract_thresholds(content: str) -> Dict[str, int]:
    """Extract named numeric thresholds from a constitution's text."""
    thresholds: Dict[str, int] = {}
    for pattern, name in THRESHOLD_PATTERNS:
        match = re.search(pattern, content)
        if match:
            try:
                thresholds[name] = int(match.group(1))
            except (IndexError, ValueError):
                pass
    return thresholds


def check_required_sections(
    local_sections: Dict[str, str],
    parent_sections: Dict[str, str],
    parent_source: str,
) -> List[Dict[str, str]]:
    """Verify that required parent sections are preserved in the local file."""
    violations: List[Dict[str, str]] = []
    for keyword in REQUIRED_SECTION_KEYWORDS:
        parent_has = any(keyword in key for key in parent_sections)
        local_has = any(keyword in key for key in local_sections)
        if parent_has and not local_has:
            violations.append(
                {
                    "type": "missing_required_section",
                    "parent_rule": f"Section '{keyword}' defined in {parent_source}",
                    "local_rule": f"Section '{keyword}' is absent from the local CLAUDE.md",
                    "description": (
                        f"Parent constitution requires '{keyword}' — "
                        "local constitution must not omit it."
                    ),
                }
            )
    return violations


def check_prohibited_permissions(
    local_content: str,
    parent_content: str,
    parent_source: str,
) -> List[Dict[str, str]]:
    """Check that local does not grant permissions that parent explicitly prohibits."""
    violations: List[Dict[str, str]] = []
    for prohibit_pattern, grant_pattern in PROHIBITION_PATTERNS:
        if re.search(prohibit_pattern, parent_content) and re.search(
            grant_pattern, local_content
        ):
            violations.append(
                {
                    "type": "prohibited_permission_granted",
                    "parent_rule": f"Parent ({parent_source}) prohibition matches: {prohibit_pattern}",
                    "local_rule": f"Local CLAUDE.md appears to grant: {grant_pattern}",
                    "description": (
                        "Local constitution grants a permission that the parent constitution prohibits."
                    ),
                }
            )
    return violations


def check_threshold_lowering(
    local_content: str,
    parent_content: str,
    parent_source: str,
) -> List[Dict[str, str]]:
    """Check that local does not set numeric thresholds lower than the parent."""
    violations: List[Dict[str, str]] = []
    parent_thresholds = extract_thresholds(parent_content)
    local_thresholds = extract_thresholds(local_content)

    for name, parent_value in parent_thresholds.items():
        if name in local_thresholds:
            local_value = local_thresholds[name]
            if local_value < parent_value:
                violations.append(
                    {
                        "type": "threshold_lowered",
                        "parent_rule": f"{name} = {parent_value} (in {parent_source})",
                        "local_rule": f"{name} = {local_value} (in local CLAUDE.md)",
                        "description": (
                            f"Local threshold {local_value} is below parent threshold {parent_value}. "
                            "Child constitutions may not lower governance thresholds."
                        ),
                    }
                )
    return violations


def validate(
    local_path: Path,
    extra_parents: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Run all inheritance validation checks and return a structured report."""
    if not local_path.is_file():
        return {
            "valid": False,
            "error": f"File not found: {local_path}",
            "violations": [],
        }

    local_content = local_path.read_text(encoding="utf-8")
    local_sections = extract_sections(local_content)
    base_dir = local_path.parent

    parent_sources = extract_inherits_from(local_content)
    if extra_parents:
        parent_sources = parent_sources + extra_parents

    if not parent_sources:
        return {
            "valid": True,
            "local_file": str(local_path),
            "note": "No inherits_from section found — nothing to validate.",
            "parents_checked": [],
            "violations": [],
            "summary": {
                "missing_sections": 0,
                "prohibited_permissions": 0,
                "lowered_thresholds": 0,
                "fetch_failures": 0,
            },
        }

    all_violations: List[Dict[str, str]] = []

    for source in parent_sources:
        parent_content = fetch_constitution(source, base_dir)
        if parent_content is None:
            all_violations.append(
                {
                    "type": "fetch_failure",
                    "parent_rule": f"Parent source: {source}",
                    "local_rule": "N/A",
                    "description": f"Could not fetch parent constitution from: {source}",
                }
            )
            continue

        parent_sections = extract_sections(parent_content)
        all_violations.extend(
            check_required_sections(local_sections, parent_sections, source)
        )
        all_violations.extend(
            check_prohibited_permissions(local_content, parent_content, source)
        )
        all_violations.extend(
            check_threshold_lowering(local_content, parent_content, source)
        )

    return {
        "valid": len(all_violations) == 0,
        "local_file": str(local_path),
        "parents_checked": parent_sources,
        "violations": all_violations,
        "summary": {
            "missing_sections": sum(
                1 for v in all_violations if v["type"] == "missing_required_section"
            ),
            "prohibited_permissions": sum(
                1 for v in all_violations if v["type"] == "prohibited_permission_granted"
            ),
            "lowered_thresholds": sum(
                1 for v in all_violations if v["type"] == "threshold_lowered"
            ),
            "fetch_failures": sum(
                1 for v in all_violations if v["type"] == "fetch_failure"
            ),
        },
    }


def format_text(report: Dict[str, Any]) -> str:
    """Format the validation report as human-readable text."""
    lines = [
        "Constitutional Inheritance Validation",
        "=====================================",
    ]

    if "error" in report:
        lines.append(f"ERROR: {report['error']}")
        return "\n".join(lines)

    lines.append(f"Local file:      {report.get('local_file', 'N/A')}")
    parents = report.get("parents_checked", [])
    lines.append(f"Parents checked: {', '.join(parents) if parents else '(none)'}")
    lines.append(f"Result:          {'VALID' if report['valid'] else 'INVALID'}")

    if "note" in report:
        lines.append(f"\nNote: {report['note']}")

    violations = report.get("violations", [])
    if violations:
        lines.append(f"\nViolations found: {len(violations)}")
        for i, v in enumerate(violations, 1):
            lines.append(f"\n  [{i}] {v['type'].upper()}")
            lines.append(f"  Parent rule: {v['parent_rule']}")
            lines.append(f"  Local rule:  {v['local_rule']}")
            lines.append(f"  Description: {v['description']}")
    else:
        lines.append("\nNo violations found.")

    summary = report.get("summary", {})
    if summary:
        lines.append(
            f"\nSummary: {summary.get('missing_sections', 0)} missing sections, "
            f"{summary.get('prohibited_permissions', 0)} prohibited permissions, "
            f"{summary.get('lowered_thresholds', 0)} lowered thresholds, "
            f"{summary.get('fetch_failures', 0)} fetch failures."
        )

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate constitutional inheritance in a CLAUDE.md file. "
            "Checks that local rules do not remove parent requirements, "
            "lower thresholds, or grant prohibited permissions."
        ),
        epilog=(
            "Use --threshold strict (default) to exit 1 on any violation. "
            "Use --threshold warn to always exit 0 (for advisory pipelines)."
        ),
    )
    parser.add_argument(
        "claude_md",
        type=Path,
        help="Path to the CLAUDE.md file to validate",
    )
    parser.add_argument(
        "--parent",
        type=str,
        action="append",
        dest="extra_parents",
        metavar="PATH_OR_URL",
        help=(
            "Additional parent constitution path or URL. "
            "Supplements the inherits_from section. Can be repeated."
        ),
    )
    parser.add_argument(
        "--threshold",
        choices=["strict", "warn"],
        default="strict",
        help=(
            "strict (default): exit 1 on any violation. "
            "warn: always exit 0, violations are printed but non-blocking."
        ),
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

    report = validate(args.claude_md, extra_parents=args.extra_parents)

    if args.output_format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_text(report))

    if args.threshold == "strict" and not report.get("valid", True):
        sys.exit(1)

    sys.exit(0)
