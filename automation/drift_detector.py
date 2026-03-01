"""Detect CLAUDE.md drift from the governance framework template.

Compares a project CLAUDE.md against the governance framework template
to find missing required sections and sections that have drifted
significantly in content length. Outputs a structured JSON report
with alignment status, missing sections, drift details, and
actionable recommendations.

Usage:
    python drift_detector.py --template templates/CLAUDE.md --target /path/to/project/CLAUDE.md
    python drift_detector.py --template templates/CLAUDE.md --target ../my-project/CLAUDE.md --format text
    python drift_detector.py --template templates/CLAUDE.md --target . --threshold 0.5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


REQUIRED_SECTIONS = [
    "project_context",
    "conventions",
    "session_protocol",
    "mandatory_session_protocol",
    "security_protocol",
    "quality_standards",
]

# session_protocol and mandatory_session_protocol are aliases — only one is required
ALIAS_GROUPS = [
    {"session_protocol", "mandatory_session_protocol"},
]

DEFAULT_DRIFT_THRESHOLD = 0.5


def read_file_content(file_path: Path) -> Optional[str]:
    """Read a file and return its content, or None if unreadable."""
    try:
        return file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def extract_sections(content: str) -> Dict[str, str]:
    """Extract sections keyed by ## header name (lowercased, stripped).

    Returns a dict mapping section name to section body text.
    """
    sections: Dict[str, str] = {}
    lines = content.splitlines()
    current_header: Optional[str] = None
    current_body: List[str] = []

    for line in lines:
        match = re.match(r"^#{1,3}\s+(.+)$", line)
        if match:
            if current_header is not None:
                sections[current_header] = "\n".join(current_body).strip()
            current_header = match.group(1).strip().lower()
            # Normalize underscores and hyphens
            current_header = re.sub(r"[\s\-]+", "_", current_header)
            current_body = []
        elif current_header is not None:
            current_body.append(line)

    if current_header is not None:
        sections[current_header] = "\n".join(current_body).strip()

    return sections


def normalize_section_name(name: str) -> str:
    """Normalize a section name for comparison."""
    return re.sub(r"[\s\-]+", "_", name.lower().strip())


def resolve_aliases(found_sections: set) -> set:
    """Expand found sections with alias resolution.

    If any member of an alias group is found, all members of that group
    are considered satisfied.
    """
    resolved = set(found_sections)
    for group in ALIAS_GROUPS:
        if group & found_sections:
            resolved |= group
    return resolved


def calculate_drift(
    template_sections: Dict[str, str],
    target_sections: Dict[str, str],
    threshold: float,
) -> List[Dict[str, Any]]:
    """Find sections that exist in both files but differ significantly in length.

    A section is considered drifted when the content length ratio exceeds
    the threshold (e.g., target is <50% or >200% of template length).
    """
    drifted: List[Dict[str, Any]] = []

    for section_name, template_body in template_sections.items():
        if section_name not in target_sections:
            continue

        target_body = target_sections[section_name]
        template_len = len(template_body)
        target_len = len(target_body)

        if template_len == 0:
            continue

        ratio = target_len / template_len
        lower_bound = 1.0 - threshold
        upper_bound = 1.0 + threshold

        if ratio < lower_bound or ratio > upper_bound:
            drifted.append(
                {
                    "section": section_name,
                    "template_length": template_len,
                    "target_length": target_len,
                    "ratio": round(ratio, 2),
                    "direction": "shorter" if ratio < 1.0 else "longer",
                }
            )

    return drifted


def generate_recommendations(
    missing: List[str],
    drifted: List[Dict[str, Any]],
) -> List[str]:
    """Generate actionable recommendations based on drift analysis."""
    recommendations: List[str] = []

    if missing:
        recommendations.append(
            f"Add {len(missing)} missing required section(s): "
            f"{', '.join(missing)}. Copy structure from the governance template."
        )

    for d in drifted:
        section = d["section"]
        if d["direction"] == "shorter":
            recommendations.append(
                f"Section '{section}' is {d['ratio']:.0%} of template length. "
                f"Review whether content was accidentally removed or simplified too aggressively."
            )
        else:
            recommendations.append(
                f"Section '{section}' is {d['ratio']:.0%} of template length. "
                f"Verify that added content aligns with governance standards."
            )

    if not missing and not drifted:
        recommendations.append(
            "No drift detected. CLAUDE.md is aligned with the governance template."
        )

    return recommendations


def detect_drift(
    template_path: Path,
    target_path: Path,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,
) -> Dict[str, Any]:
    """Run drift detection and return a structured report."""
    # Handle target_path being a directory
    if target_path.is_dir():
        target_path = target_path / "CLAUDE.md"

    template_content = read_file_content(template_path)
    if template_content is None:
        return {
            "error": f"Cannot read template file: {template_path}",
            "aligned": False,
            "missing_sections": [],
            "drift_sections": [],
            "recommendations": [f"Template file not found: {template_path}"],
        }

    target_content = read_file_content(target_path)
    if target_content is None:
        return {
            "error": f"Cannot read target file: {target_path}",
            "aligned": False,
            "missing_sections": list(REQUIRED_SECTIONS),
            "drift_sections": [],
            "recommendations": [
                f"Target CLAUDE.md not found at {target_path}. "
                "Copy the governance template and customize it."
            ],
        }

    template_sections = extract_sections(template_content)
    target_sections = extract_sections(target_content)

    # Determine which required sections are missing
    found_normalized = set(target_sections.keys())
    resolved = resolve_aliases(found_normalized)

    missing: List[str] = []
    for req in REQUIRED_SECTIONS:
        normalized = normalize_section_name(req)
        if normalized not in resolved:
            # Skip alias partners if one is already found
            skip = False
            for group in ALIAS_GROUPS:
                if normalized in group and group & resolved:
                    skip = True
                    break
            if not skip:
                missing.append(req)

    # Deduplicate: if both aliases are missing, only report one
    seen_groups: List[set] = []
    deduped_missing: List[str] = []
    for m in missing:
        norm = normalize_section_name(m)
        in_group = False
        for group in ALIAS_GROUPS:
            if norm in group:
                if group not in seen_groups:
                    seen_groups.append(group)
                    deduped_missing.append(" or ".join(sorted(group)))
                in_group = True
                break
        if not in_group:
            deduped_missing.append(m)

    # Detect content drift
    drift_sections = calculate_drift(template_sections, target_sections, threshold)

    aligned = len(deduped_missing) == 0 and len(drift_sections) == 0
    recommendations = generate_recommendations(deduped_missing, drift_sections)

    return {
        "template": str(template_path),
        "target": str(target_path),
        "threshold": threshold,
        "aligned": aligned,
        "missing_sections": deduped_missing,
        "drift_sections": drift_sections,
        "template_section_count": len(template_sections),
        "target_section_count": len(target_sections),
        "recommendations": recommendations,
    }


def format_text(report: Dict[str, Any]) -> str:
    """Format the drift report as human-readable text."""
    lines = [
        "CLAUDE.md Drift Report",
        "======================",
    ]

    if "error" in report:
        lines.append(f"Error: {report['error']}")
        return "\n".join(lines)

    lines.append(f"Template: {report['template']}")
    lines.append(f"Target:   {report['target']}")
    lines.append(f"Drift threshold: {report['threshold']:.0%}")
    lines.append(f"Status: {'ALIGNED' if report['aligned'] else 'DRIFTED'}")
    lines.append("")

    if report["missing_sections"]:
        lines.append("Missing required sections:")
        for section in report["missing_sections"]:
            lines.append(f"  - {section}")
        lines.append("")

    if report["drift_sections"]:
        lines.append("Drifted sections:")
        for d in report["drift_sections"]:
            lines.append(
                f"  - {d['section']}: {d['target_length']} chars "
                f"({d['direction']}, {d['ratio']:.0%} of template)"
            )
        lines.append("")

    if report["recommendations"]:
        lines.append("Recommendations:")
        for rec in report["recommendations"]:
            lines.append(f"  - {rec}")

    return "\n".join(lines)


def format_json(report: Dict[str, Any]) -> str:
    """Format the drift report as JSON."""
    return json.dumps(report, indent=2)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Detect CLAUDE.md drift from the governance framework template.",
        epilog="Exit code 0 if aligned, 1 if drifted or errors found.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        required=True,
        help="Path to the governance framework CLAUDE.md template",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Path to the project CLAUDE.md (or directory containing it)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_DRIFT_THRESHOLD,
        help=(
            "Drift threshold as a decimal fraction (default: 0.5). "
            "A section is flagged when its length differs by more than this ratio."
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


def main() -> int:
    """Entry point for the drift detector."""
    parser = build_parser()
    args = parser.parse_args()

    report = detect_drift(
        template_path=args.template,
        target_path=args.target,
        threshold=args.threshold,
    )

    if args.output_format == "json":
        print(format_json(report))
    else:
        print(format_text(report))

    return 0 if report.get("aligned", False) else 1


if __name__ == "__main__":
    sys.exit(main())
