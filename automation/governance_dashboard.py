"""Generate a Markdown-based governance dashboard for a repository.

Reads: CHANGELOG.md, COST_LOG.md, MEMORY.md, PROJECT_PLAN.md, docs/adr/
Generates: DASHBOARD.md with:
  - Health Score (from health_score_calculator.py)
  - Session Velocity (tasks per session trend)
  - Cost Trend (tokens per session, cost per task)
  - Knowledge Health (MEMORY.md freshness, stale entries count)
  - ADR Coverage (decisions with/without ADRs)
  - Sprint Progress (current sprint completion %)
  - Governance Maturity Level (current level with evidence)

No external dependencies — standard library only.

Usage:
    python3 automation/governance_dashboard.py --repo-path .
    python3 automation/governance_dashboard.py --repo-path . --output DASHBOARD.md
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Imports from sibling automation script
# ---------------------------------------------------------------------------

_AUTOMATION_DIR = Path(__file__).parent
if str(_AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(_AUTOMATION_DIR))

import health_score_calculator as hsc  # noqa: E402

# ---------------------------------------------------------------------------
# ASCII chart helpers
# ---------------------------------------------------------------------------

BAR_FULL = "█"
BAR_EMPTY = "░"
BAR_WIDTH = 20


def ascii_bar(value: float, max_value: float, width: int = BAR_WIDTH) -> str:
    """Return a filled ASCII progress bar string."""
    if max_value <= 0:
        return BAR_EMPTY * width
    ratio = min(value / max_value, 1.0)
    filled = round(ratio * width)
    return BAR_FULL * filled + BAR_EMPTY * (width - filled)


def sparkline(values: List[float], width: int = 8) -> str:
    """Return a compact unicode sparkline for a list of values."""
    if not values:
        return "—"
    blocks = " ▁▂▃▄▅▆▇█"
    max_v = max(values) if max(values) > 0 else 1
    chars = []
    for v in values[-width:]:
        idx = round((v / max_v) * (len(blocks) - 1))
        chars.append(blocks[idx])
    return "".join(chars)


def trend_arrow(values: List[float]) -> str:
    """Return ↑, ↓, or → based on first-vs-last trend in values list."""
    if len(values) < 2:
        return "→"
    delta = values[-1] - values[-2]
    if delta > 0:
        return "↑"
    if delta < 0:
        return "↓"
    return "→"


# ---------------------------------------------------------------------------
# CHANGELOG.md parsers
# ---------------------------------------------------------------------------

SESSION_HEADER_RE = re.compile(
    r"^## Session\s+(\d+)\s*[-–]+\s*(\d{4}-\d{2}-\d{2})\s*\[([^\]]+)\]",
    re.MULTILINE,
)
TASKS_COMPLETED_RE = re.compile(
    r"[-*]\s*(?:Tasks?\s+completed|Completed\s+tasks?):\s*(\d+)",
    re.IGNORECASE,
)


def parse_changelog(repo: Path) -> List[Dict[str, Any]]:
    """Parse CHANGELOG.md and return list of session dicts, newest first."""
    path = repo / "CHANGELOG.md"
    if not path.is_file():
        return []
    content = path.read_text(encoding="utf-8")

    sessions = []
    headers = list(SESSION_HEADER_RE.finditer(content))
    for i, match in enumerate(headers):
        session_num = int(match.group(1))
        date_str = match.group(2)
        model = match.group(3)

        # Extract the body between this header and the next (or end)
        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        body = content[start:end]

        # Count tasks completed
        task_match = TASKS_COMPLETED_RE.search(body)
        tasks = int(task_match.group(1)) if task_match else 0

        sessions.append(
            {
                "session": session_num,
                "date": date_str,
                "model": model,
                "tasks": tasks,
            }
        )

    return sessions


# ---------------------------------------------------------------------------
# COST_LOG.md parsers
# ---------------------------------------------------------------------------

COST_TABLE_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|"
    r"[^|]*\|\s*\$([0-9.]+)\s*\|",
    re.MULTILINE,
)


def parse_cost_log(repo: Path) -> List[Dict[str, Any]]:
    """Parse COST_LOG.md and return list of session cost dicts."""
    path = repo / "COST_LOG.md"
    if not path.is_file():
        return []
    content = path.read_text(encoding="utf-8")

    rows = []
    for m in COST_TABLE_ROW_RE.finditer(content):
        rows.append(
            {
                "session": int(m.group(1)),
                "date": m.group(2),
                "model": m.group(3).strip(),
                "tasks": int(m.group(4)),
                "cost": float(m.group(5)),
            }
        )
    # Sort oldest first
    rows.sort(key=lambda r: r["session"])
    return rows


# ---------------------------------------------------------------------------
# MEMORY.md parser
# ---------------------------------------------------------------------------

MEMORY_UPDATED_RE = re.compile(
    r"\*\*Last\s+updated:\*\*\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE
)
MEMORY_STALE_COMMENT_RE = re.compile(r"<!--\s*CUSTOMIZE:", re.IGNORECASE)


def parse_memory(repo: Path) -> Dict[str, Any]:
    """Return freshness metadata for MEMORY.md."""
    path = repo / "MEMORY.md"
    if not path.is_file():
        return {"exists": False}

    content = path.read_text(encoding="utf-8")
    last_updated = None
    m = MEMORY_UPDATED_RE.search(content)
    if m:
        last_updated = m.group(1)

    # Heuristic: count sections (lines starting with ## )
    sections = re.findall(r"^## .+", content, re.MULTILINE)
    # Heuristic: count customize comments as "placeholder" staleness
    placeholder_count = len(MEMORY_STALE_COMMENT_RE.findall(content))

    # Count non-empty bullet points as knowledge entries
    bullets = re.findall(r"^[-*]\s+\S", content, re.MULTILINE)

    return {
        "exists": True,
        "last_updated": last_updated,
        "sections": len(sections),
        "knowledge_entries": len(bullets),
        "placeholder_sections": placeholder_count,
    }


# ---------------------------------------------------------------------------
# PROJECT_PLAN.md parser
# ---------------------------------------------------------------------------

PHASE_PROGRESS_RE = re.compile(
    r"\*\*Phase\s+(\d+)\s+progress:\*\*\s*(\d+)/(\d+)\s+tasks?\s+complete\s*\((\d+)%\)",
    re.IGNORECASE,
)
SPRINT_GOAL_RE = re.compile(r"\*\*Sprint\s+goal:\*\*\s*(.+)", re.IGNORECASE)
SPRINT_DATES_RE = re.compile(
    r"\*\*Sprint\s+dates:\*\*\s*(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)
CURRENT_PHASE_RE = re.compile(
    r"\*\*Current\s+phase:\*\*\s*Phase\s+(\d+)", re.IGNORECASE
)


def parse_project_plan(repo: Path) -> Dict[str, Any]:
    """Extract sprint and phase progress from PROJECT_PLAN.md."""
    path = repo / "PROJECT_PLAN.md"
    if not path.is_file():
        return {"exists": False}

    content = path.read_text(encoding="utf-8")

    current_phase_m = CURRENT_PHASE_RE.search(content)
    current_phase = int(current_phase_m.group(1)) if current_phase_m else None

    sprint_goal_m = SPRINT_GOAL_RE.search(content)
    sprint_goal = sprint_goal_m.group(1).strip() if sprint_goal_m else "—"

    sprint_dates_m = SPRINT_DATES_RE.search(content)
    sprint_dates = (
        f"{sprint_dates_m.group(1)} to {sprint_dates_m.group(2)}"
        if sprint_dates_m
        else "—"
    )

    phases = {}
    for m in PHASE_PROGRESS_RE.finditer(content):
        phases[int(m.group(1))] = {
            "completed": int(m.group(2)),
            "total": int(m.group(3)),
            "pct": int(m.group(4)),
        }

    return {
        "exists": True,
        "current_phase": current_phase,
        "sprint_goal": sprint_goal,
        "sprint_dates": sprint_dates,
        "phases": phases,
    }


# ---------------------------------------------------------------------------
# ADR scanner
# ---------------------------------------------------------------------------


def count_adrs(repo: Path) -> Dict[str, Any]:
    """Count ADR files in docs/adr/, excluding the template."""
    adr_dir = repo / "docs" / "adr"
    if not adr_dir.is_dir():
        return {"count": 0, "files": []}
    files = [
        f.name
        for f in adr_dir.iterdir()
        if f.is_file()
        and f.suffix == ".md"
        and not f.name.startswith("ADR-000")
    ]
    return {"count": len(files), "files": sorted(files)}


# ---------------------------------------------------------------------------
# Dashboard section builders
# ---------------------------------------------------------------------------


def section_divider(title: str) -> str:
    line = "─" * 60
    return f"\n{line}\n## {title}\n{line}\n"


def build_health_score_section(report: Dict[str, Any]) -> str:
    score = report["score"]
    max_score = report["max_score"]
    level = report["level"]
    label = report["level_label"]
    bar = ascii_bar(score, max_score, BAR_WIDTH)

    passed = [c for c in report["checks"] if c["passed"]]
    failed = [c for c in report["checks"] if not c["passed"]]

    lines = [
        f"**Score:** {score}/{max_score}  {bar}  **Level {level} — {label}**\n",
        "| Status | Check | Points |",
        "|:------:|-------|-------:|",
    ]
    for c in passed:
        lines.append(f"| ✅ | {c['name']} | +{c['points']} |")
    for c in failed:
        lines.append(f"| ❌ | {c['name']} | +{c['points']} if added |")
    return "\n".join(lines)


def build_velocity_section(sessions: List[Dict[str, Any]]) -> str:
    if not sessions:
        return "_No CHANGELOG.md found — cannot compute session velocity._"

    # Show last 10 sessions, oldest first for the chart
    sorted_sessions = sorted(sessions, key=lambda s: s["session"])
    recent = sorted_sessions[-10:]
    task_counts = [s["tasks"] for s in recent]
    max_tasks = max(task_counts) if task_counts else 1
    avg = sum(task_counts) / len(task_counts) if task_counts else 0

    lines = [
        f"**Sessions tracked:** {len(sessions)}  "
        f"| **Avg tasks/session:** {avg:.1f}  "
        f"| **Trend:** {trend_arrow(task_counts)}\n",
        "```",
        f"Tasks/Session (last {len(recent)} sessions)",
        "",
    ]

    for s in recent:
        bar = ascii_bar(s["tasks"], max_tasks, 16)
        lines.append(f"  Session {s['session']:>3}  {bar}  {s['tasks']}")

    lines += [
        "",
        f"  Sparkline: {sparkline(task_counts)}",
        "```",
    ]
    return "\n".join(lines)


def build_cost_section(cost_rows: List[Dict[str, Any]]) -> str:
    if not cost_rows:
        return "_No COST_LOG.md found — cost tracking not active._"

    recent = cost_rows[-8:]
    costs = [r["cost"] for r in recent]
    max_cost = max(costs) if costs else 1.0
    total = sum(r["cost"] for r in cost_rows)
    avg_cost = total / len(cost_rows) if cost_rows else 0
    tasks_total = sum(r["tasks"] for r in cost_rows)
    cost_per_task = total / tasks_total if tasks_total > 0 else 0

    model_counts: Dict[str, int] = {}
    for r in cost_rows:
        model_counts[r["model"]] = model_counts.get(r["model"], 0) + 1

    lines = [
        f"**Total cost (all sessions):** ${total:.2f}  "
        f"| **Avg/session:** ${avg_cost:.3f}  "
        f"| **Cost/task:** ${cost_per_task:.3f}\n",
        "```",
        f"Cost per Session (last {len(recent)} sessions)",
        "",
    ]

    for r in recent:
        bar = ascii_bar(r["cost"], max_cost, 16)
        lines.append(f"  Session {r['session']:>3}  {bar}  ${r['cost']:.3f}")

    lines += [
        "",
        f"  Sparkline: {sparkline(costs)}  Trend: {trend_arrow(costs)}",
        "```\n",
        "**Model distribution:**",
    ]
    for model, count in sorted(model_counts.items()):
        pct = count / len(cost_rows) * 100
        lines.append(f"- `{model}`: {count} session(s) ({pct:.0f}%)")

    return "\n".join(lines)


def build_knowledge_section(memory: Dict[str, Any]) -> str:
    if not memory.get("exists"):
        return "_No MEMORY.md found — cross-session knowledge not persisted._"

    last = memory.get("last_updated") or "unknown"
    sections = memory.get("sections", 0)
    entries = memory.get("knowledge_entries", 0)
    placeholders = memory.get("placeholder_sections", 0)

    # Freshness rating
    freshness = "unknown"
    if last != "unknown":
        try:
            updated_dt = datetime.fromisoformat(last)
            today = datetime.now(timezone.utc).date()
            delta_days = (today - updated_dt.date()).days
            if delta_days <= 7:
                freshness = f"✅ Fresh ({delta_days}d ago)"
            elif delta_days <= 30:
                freshness = f"⚠️ Aging ({delta_days}d ago)"
            else:
                freshness = f"❌ Stale ({delta_days}d ago — review recommended)"
        except ValueError:
            pass

    lines = [
        f"**Last updated:** {last}  | **Freshness:** {freshness}",
        f"**Sections:** {sections}  | **Knowledge entries:** {entries}  "
        f"| **Placeholder sections remaining:** {placeholders}",
    ]
    if placeholders > 0:
        lines.append(
            f"\n⚠️ {placeholders} section(s) still contain `<!-- CUSTOMIZE -->` "
            "placeholder text. Replace with project-specific knowledge."
        )
    return "\n".join(lines)


def build_adr_section(adr_data: Dict[str, Any]) -> str:
    count = adr_data["count"]
    files = adr_data["files"]

    if count == 0:
        return (
            "❌ **No ADRs found** in `docs/adr/` (excluding template).\n\n"
            "Create your first ADR from "
            "[`docs/adr/ADR-000-template.md`](../docs/adr/ADR-000-template.md) "
            "to reach Level 2."
        )

    lines = [f"**ADRs recorded:** {count}\n", "| ADR File | Status |", "|----------|--------|"]
    for f in files:
        # Try to extract status from filename or content (simplified)
        lines.append(f"| `{f}` | — |")
    return "\n".join(lines)


def build_sprint_section(plan: Dict[str, Any]) -> str:
    if not plan.get("exists"):
        return "_No PROJECT_PLAN.md found — sprint tracking not active._"

    current_phase = plan.get("current_phase")
    sprint_goal = plan.get("sprint_goal", "—")
    sprint_dates = plan.get("sprint_dates", "—")
    phases = plan.get("phases", {})

    lines = [
        f"**Sprint goal:** {sprint_goal}",
        f"**Sprint dates:** {sprint_dates}\n",
    ]

    if phases:
        lines.append("**Phase progress:**\n")
        lines.append("```")
        for phase_num, data in sorted(phases.items()):
            bar = ascii_bar(data["completed"], data["total"], 16)
            marker = " ◀ current" if phase_num == current_phase else ""
            lines.append(
                f"  Phase {phase_num}  {bar}  "
                f"{data['completed']}/{data['total']} ({data['pct']}%){marker}"
            )
        lines.append("```")
    else:
        lines.append(
            "_Progress percentages not found in PROJECT_PLAN.md. "
            "Add `**Phase N progress:** X/Y tasks complete (Z%)` lines._"
        )

    return "\n".join(lines)


def build_maturity_section(report: Dict[str, Any]) -> str:
    level = report["level"]
    label = report["level_label"]
    score = report["score"]
    max_score = report["max_score"]

    level_descriptions = {
        0: "No governance. CLAUDE.md does not exist or contains no required sections.",
        1: "Foundation: CLAUDE.md, PROJECT_PLAN.md, CHANGELOG.md in place. "
           "Sessions are governed.",
        2: "Structured: ADRs, MEMORY.md, ARCHITECTURE.md, CI/CD present. "
           "Decisions are recorded.",
        3: "Enforced: Pre-commit hooks, AI review workflow, governance gate active. "
           "Compliance is automatic.",
        4: "Measured: Quality metrics tracked. Drift detection active. "
           "Model routing optimized.",
        5: "Self-optimizing: Org-level governance, research pipeline, "
           "compliance audit trail complete.",
    }

    next_level = level + 1 if level < 5 else None
    missing = [c for c in report["checks"] if not c["passed"]]
    missing_pts = sum(c["points"] for c in missing)

    lines = [
        f"**Current level:** Level {level} — {label}",
        f"**Evidence:** Score {score}/{max_score} ({score/max_score*100:.0f}%)\n",
        f"_{level_descriptions.get(level, '')}_\n",
    ]

    if next_level is not None:
        next_thresholds = {1: 20, 2: 40, 3: 60, 4: 80, 5: 95}
        needed = next_thresholds.get(next_level, 100) - score
        lines += [
            f"**To reach Level {next_level}:** "
            f"add {needed} more points ({missing_pts} available from missing checks)\n",
            "**Missing checks:**",
        ]
        for c in missing:
            lines.append(f"- ❌ {c['name']} (+{c['points']} pts)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dashboard assembler
# ---------------------------------------------------------------------------


def generate_dashboard(repo: Path) -> str:
    """Generate the full DASHBOARD.md content string."""
    repo = repo.resolve()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    report = hsc.calculate_score(repo)
    sessions = parse_changelog(repo)
    cost_rows = parse_cost_log(repo)
    memory = parse_memory(repo)
    plan = parse_project_plan(repo)
    adr_data = count_adrs(repo)

    lines = [
        "# Governance Dashboard",
        "",
        f"> Generated: {now}  |  Repository: `{repo.name}`",
        "",
        "> This file is auto-generated by `automation/governance_dashboard.py`.",
        "> Do not edit manually — run the script to refresh.",
        "",
    ]

    lines.append(section_divider("Health Score"))
    lines.append(build_health_score_section(report))

    lines.append(section_divider("Session Velocity"))
    lines.append(build_velocity_section(sessions))

    lines.append(section_divider("Cost Trend"))
    lines.append(build_cost_section(cost_rows))

    lines.append(section_divider("Knowledge Health"))
    lines.append(build_knowledge_section(memory))

    lines.append(section_divider("ADR Coverage"))
    lines.append(build_adr_section(adr_data))

    lines.append(section_divider("Sprint Progress"))
    lines.append(build_sprint_section(plan))

    lines.append(section_divider("Governance Maturity Level"))
    lines.append(build_maturity_section(report))

    lines += [
        "",
        "---",
        "",
        "*See [docs/metrics-guide.md](docs/metrics-guide.md) for metric definitions "
        "and collection methods.*",
        "*See [docs/maturity-model.md](docs/maturity-model.md) for upgrade paths "
        "between maturity levels.*",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate a Markdown governance dashboard for a repository.",
        epilog="Output defaults to DASHBOARD.md in the repo root.",
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path("."),
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="DASHBOARD.md",
        help="Output filename relative to repo root (default: DASHBOARD.md)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print dashboard to stdout instead of writing a file",
    )
    return parser


def main() -> int:
    """Entry point — returns exit code."""
    parser = build_parser()
    args = parser.parse_args()

    repo = args.repo_path.resolve()
    if not repo.is_dir():
        print(f"Error: {repo} is not a valid directory.", file=sys.stderr)
        return 1

    try:
        dashboard = generate_dashboard(repo)
    except Exception as exc:  # noqa: BLE001
        print(f"Error generating dashboard: {exc}", file=sys.stderr)
        return 1

    if args.stdout:
        print(dashboard)
        return 0

    output_path = repo / args.output
    output_path.write_text(dashboard, encoding="utf-8")
    print(f"Dashboard written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
