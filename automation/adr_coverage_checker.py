"""Check whether architectural decisions have corresponding ADRs.

Reads CHANGELOG.md and DECISIONS.md to identify decisions that were made,
then compares them against the ADR files in docs/adr/. Reports decisions that
match patterns indicating an architectural choice but have no corresponding ADR.

An ADR is considered to cover a decision when the ADR's filename or content
shares at least two significant keywords with the decision text.

Exits with code 1 if any uncovered decisions are found (default), or always
exits 0 when --threshold warn is passed.

Usage:
    python3 automation/adr_coverage_checker.py
    python3 automation/adr_coverage_checker.py --repo-path /path/to/repo
    python3 automation/adr_coverage_checker.py --format json
    python3 automation/adr_coverage_checker.py --threshold warn
    python3 automation/adr_coverage_checker.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Minimum number of significant keywords two texts must share to be considered
# covering the same decision.
KEYWORD_MATCH_THRESHOLD = 2

# Minimum word length to be considered a significant keyword.
MIN_KEYWORD_LENGTH = 4

# Common stop-words to exclude from keyword matching.
STOP_WORDS: Set[str] = {
    "with", "this", "that", "from", "have", "will", "been", "were", "they",
    "also", "more", "some", "such", "when", "then", "than", "what", "which",
    "each", "into", "over", "used", "uses", "make", "made", "using",
    "because", "before", "after", "session", "agent", "code", "file", "files",
    "project", "team", "approach", "pattern", "option", "current", "change",
}

# Patterns in CHANGELOG.md that indicate an architectural decision was made.
CHANGELOG_DECISION_PATTERNS = [
    # "Decisions made" section entries
    re.compile(
        r"^\s*[-*]\s*\*\*([^*]+)\*\*(?:\s*\(ADR[- ]\d+\))?:\s*(.{20,150})",
        re.MULTILINE,
    ),
    # Session "decisions made" section
    re.compile(
        r"###\s+Decisions\s+made\s*\n((?:.*\n)*?)(?=###|\Z)",
        re.MULTILINE | re.IGNORECASE,
    ),
]

# Patterns in DECISIONS.md for DEC entries.
DECISIONS_MD_PATTERN = re.compile(
    r"^##\s+DEC-(\d+)\s+--\s+(.+?)\s+--\s+\d{4}-\d{2}-\d{2}",
    re.MULTILINE,
)


@dataclass
class Decision:
    """An architectural decision extracted from CHANGELOG.md or DECISIONS.md."""

    source: str  # "CHANGELOG.md" or "DECISIONS.md"
    identifier: str  # e.g. "DEC-001" or "Session 003 - Stripe choice"
    title: str
    body: str


@dataclass
class Adr:
    """An ADR file read from docs/adr/."""

    path: str
    number: str  # e.g. "001"
    title: str
    content: str


@dataclass
class CoverageResult:
    """Coverage result for a single decision."""

    decision: Decision
    covered: bool
    covering_adrs: List[str]  # ADR numbers that cover this decision
    recommendation: str


def extract_keywords(text: str) -> Set[str]:
    """Extract significant lowercase words from a text block."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {
        w for w in words
        if len(w) >= MIN_KEYWORD_LENGTH and w not in STOP_WORDS
    }


def keyword_overlap(text_a: str, text_b: str) -> int:
    """Count how many significant keywords two texts share."""
    return len(extract_keywords(text_a) & extract_keywords(text_b))


def parse_decisions_md(path: Path) -> List[Decision]:
    """Parse DECISIONS.md and return a list of Decision objects."""
    if not path.is_file():
        return []

    content = path.read_text(encoding="utf-8")
    decisions: List[Decision] = []

    matches = list(DECISIONS_MD_PATTERN.finditer(content))
    for i, match in enumerate(matches):
        number = match.group(1).zfill(3)
        title = match.group(2).strip()

        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]

        decisions.append(
            Decision(
                source="DECISIONS.md",
                identifier=f"DEC-{number}",
                title=title,
                body=body,
            )
        )

    return decisions


def parse_changelog_decisions(path: Path) -> List[Decision]:
    """Parse CHANGELOG.md and extract decisions from 'Decisions made' sections."""
    if not path.is_file():
        return []

    content = path.read_text(encoding="utf-8")
    decisions: List[Decision] = []

    # Find each session block.
    session_header = re.compile(
        r"^##\s+Session\s+(\d+)\s+[-\u2013\u2014]+\s+(\d{4}-\d{2}-\d{2})",
        re.MULTILINE,
    )
    session_matches = list(session_header.finditer(content))

    for i, session_match in enumerate(session_matches):
        session_id = session_match.group(1).zfill(3)
        start = session_match.start()
        end = session_matches[i + 1].start() if i + 1 < len(session_matches) else len(content)
        session_body = content[start:end]

        # Find the "Decisions made" subsection.
        dec_section = re.search(
            r"###\s+Decisions\s+made\s*\n((?:(?!###).)*)",
            session_body,
            re.IGNORECASE | re.DOTALL,
        )
        if not dec_section:
            continue

        decisions_text = dec_section.group(1)

        # Each bullet in the decisions section is a separate decision.
        bullets = re.findall(
            r"^\s*[-*]\s*\*\*([^*]+)\*\*(?:\s*\([^)]*\))?:\s*(.{20,300})",
            decisions_text,
            re.MULTILINE,
        )

        for title, body in bullets:
            title_clean = title.strip()
            # Skip if the bullet explicitly references an ADR — it is already covered.
            if re.search(r"\bADR[- ]\d+\b", title + body, re.IGNORECASE):
                continue

            decisions.append(
                Decision(
                    source="CHANGELOG.md",
                    identifier=f"Session {session_id} — {title_clean}",
                    title=title_clean,
                    body=body.strip(),
                )
            )

    return decisions


def load_adrs(adr_dir: Path) -> List[Adr]:
    """Load all ADR files from docs/adr/, excluding the template (ADR-000)."""
    if not adr_dir.is_dir():
        return []

    adrs: List[Adr] = []
    for adr_path in sorted(adr_dir.glob("ADR-[0-9]*.md")):
        # Skip the template.
        if adr_path.stem.startswith("ADR-000"):
            continue

        match = re.match(r"ADR-(\d+)", adr_path.stem)
        number = match.group(1) if match else "???"

        # Extract the title from the first H1 or H2 heading.
        content = adr_path.read_text(encoding="utf-8")
        title_match = re.search(r"^#{1,2}\s+ADR[^:]*:\s*(.+)$", content, re.MULTILINE)
        if not title_match:
            title_match = re.search(r"^#{1,2}\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else adr_path.stem

        adrs.append(
            Adr(
                path=str(adr_path),
                number=number,
                title=title,
                content=content,
            )
        )

    return adrs


def check_coverage(
    decisions: List[Decision],
    adrs: List[Adr],
) -> List[CoverageResult]:
    """For each decision, determine whether an ADR covers it."""
    results: List[CoverageResult] = []

    for decision in decisions:
        # Build the text to match against.
        decision_text = f"{decision.title} {decision.body}"

        covering: List[str] = []
        for adr in adrs:
            adr_text = f"{adr.title} {adr.content}"
            # Also check if the DECISIONS.md entry explicitly references this ADR.
            explicit_ref = bool(
                re.search(
                    rf"\bADR[- ]{adr.number}\b",
                    decision.body,
                    re.IGNORECASE,
                )
            )
            if explicit_ref or keyword_overlap(decision_text, adr_text) >= KEYWORD_MATCH_THRESHOLD:
                covering.append(adr.number)

        covered = len(covering) > 0

        if covered:
            recommendation = f"Covered by ADR-{covering[0]}."
        else:
            # Generate a recommendation based on the decision title.
            slug = re.sub(r"\W+", "-", decision.title.lower()).strip("-")[:40]
            next_num = "NNN"  # Placeholder — the human assigns the real number.
            recommendation = (
                f"Create docs/adr/ADR-{next_num}-{slug}.md using the template in "
                "docs/adr/ADR-000-template.md."
            )

        results.append(
            CoverageResult(
                decision=decision,
                covered=covered,
                covering_adrs=covering,
                recommendation=recommendation,
            )
        )

    return results


def format_text(
    results: List[CoverageResult],
    adrs: List[Adr],
    repo_path: Path,
) -> str:
    """Format the coverage report as human-readable text."""
    uncovered = [r for r in results if not r.covered]
    covered = [r for r in results if r.covered]

    lines = [
        "ADR Coverage Report",
        "===================",
        f"Repository: {repo_path}",
        f"ADRs found:          {len(adrs)}",
        f"Decisions found:     {len(results)}",
        f"Covered decisions:   {len(covered)}",
        f"Uncovered decisions: {len(uncovered)}",
    ]

    if adrs:
        lines.append("\nExisting ADRs:")
        for adr in adrs:
            lines.append(f"  ADR-{adr.number}: {adr.title}")

    if uncovered:
        lines.append(f"\nDecisions lacking ADR coverage ({len(uncovered)}):")
        for r in uncovered:
            lines.append(f"\n  [{r.decision.source}] {r.decision.identifier}")
            lines.append(f"  Title: {r.decision.title}")
            body_preview = r.decision.body[:120].replace("\n", " ")
            lines.append(f"  Body:  {body_preview}...")
            lines.append(f"  Recommendation: {r.recommendation}")
    else:
        lines.append("\nAll decisions have ADR coverage.")

    if covered:
        lines.append(f"\nDecisions with ADR coverage ({len(covered)}):")
        for r in covered:
            adr_list = ", ".join(f"ADR-{n}" for n in r.covering_adrs)
            lines.append(f"  {r.decision.identifier} \u2192 {adr_list}")

    return "\n".join(lines)


def run(
    repo_path: Path,
    threshold: str = "strict",
    output_format: str = "text",
) -> int:
    """Main entry point: check ADR coverage and return exit code."""
    changelog_path = repo_path / "CHANGELOG.md"
    decisions_path = repo_path / "DECISIONS.md"
    adr_dir = repo_path / "docs" / "adr"

    changelog_decisions = parse_changelog_decisions(changelog_path)
    decisions_md_entries = parse_decisions_md(decisions_path)

    # Merge, deduplicating by title (DECISIONS.md is authoritative).
    decisions_md_titles = {d.title.lower() for d in decisions_md_entries}
    changelog_unique = [
        d for d in changelog_decisions
        if d.title.lower() not in decisions_md_titles
    ]
    all_decisions = decisions_md_entries + changelog_unique

    adrs = load_adrs(adr_dir)
    results = check_coverage(all_decisions, adrs)

    uncovered = [r for r in results if not r.covered]

    if output_format == "json":
        output: Dict[str, Any] = {
            "repository": str(repo_path),
            "adrs_found": len(adrs),
            "decisions_found": len(results),
            "covered": len(results) - len(uncovered),
            "uncovered": len(uncovered),
            "gate_passed": len(uncovered) == 0,
            "uncovered_decisions": [
                {
                    "source": r.decision.source,
                    "identifier": r.decision.identifier,
                    "title": r.decision.title,
                    "recommendation": r.recommendation,
                }
                for r in uncovered
            ],
            "covered_decisions": [
                {
                    "identifier": r.decision.identifier,
                    "covering_adrs": [f"ADR-{n}" for n in r.covering_adrs],
                }
                for r in results if r.covered
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text(results, adrs, repo_path))

    if threshold == "strict" and uncovered:
        if output_format == "text":
            print(
                f"\nADR COVERAGE GATE FAILED: {len(uncovered)} decision(s) lack ADR coverage.",
                file=sys.stderr,
            )
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Check whether architectural decisions in CHANGELOG.md and "
            "DECISIONS.md have corresponding ADR files in docs/adr/."
        ),
        epilog=(
            "Use --threshold strict (default) to exit 1 when uncovered decisions exist. "
            "Use --threshold warn to always exit 0 (advisory mode)."
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
        "--threshold",
        choices=["strict", "warn"],
        default="strict",
        help=(
            "strict (default): exit 1 if any uncovered decisions are found. "
            "warn: always exit 0, uncovered decisions are printed but non-blocking."
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

    repo_path = args.repo_path.resolve()
    if not repo_path.is_dir():
        print(f"Error: {repo_path} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    sys.exit(run(repo_path, threshold=args.threshold, output_format=args.output_format))
