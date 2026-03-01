"""Generate a focused cost analysis dashboard from COST_LOG.md.

Reads COST_LOG.md and generates COST_DASHBOARD.md with:
  - Cost breakdown by model
  - Cost breakdown by session type
  - Cost breakdown by time period (monthly)
  - Cost per task and cost per file trends
  - Model routing efficiency score
  - Recommendations: where to use cheaper models

No external dependencies — standard library only.

Usage:
    python3 automation/cost_dashboard.py --repo-path .
    python3 automation/cost_dashboard.py --repo-path . --output COST_DASHBOARD.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# ASCII chart helpers (self-contained — no shared module dependency)
# ---------------------------------------------------------------------------

BAR_FULL = "█"
BAR_EMPTY = "░"


def ascii_bar(value: float, max_value: float, width: int = 20) -> str:
    """Return a filled ASCII progress bar string."""
    if max_value <= 0:
        return BAR_EMPTY * width
    ratio = min(value / max_value, 1.0)
    filled = round(ratio * width)
    return BAR_FULL * filled + BAR_EMPTY * (width - filled)


def sparkline(values: List[float]) -> str:
    """Return a compact unicode sparkline for a list of values."""
    if not values:
        return "—"
    blocks = " ▁▂▃▄▅▆▇█"
    max_v = max(values) if max(values) > 0 else 1
    return "".join(blocks[round((v / max_v) * (len(blocks) - 1))] for v in values)


def trend_arrow(values: List[float]) -> str:
    """Return ↑, ↓, or → based on recent trend."""
    if len(values) < 2:
        return "→"
    delta = values[-1] - values[-2]
    if delta > 0.001:
        return "↑"
    if delta < -0.001:
        return "↓"
    return "→"


# ---------------------------------------------------------------------------
# COST_LOG.md parser
# ---------------------------------------------------------------------------

COST_TABLE_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|"
    r"\s*([^|]*?)\s*\|\s*\$([0-9.]+)\s*\|(?:\s*([^|]*?)\s*\|)?",
    re.MULTILINE,
)

# Model tier classification
HAIKU_PATTERN = re.compile(r"haiku", re.IGNORECASE)
SONNET_PATTERN = re.compile(r"sonnet", re.IGNORECASE)
OPUS_PATTERN = re.compile(r"opus", re.IGNORECASE)


def classify_model_tier(model_name: str) -> str:
    """Return 'haiku', 'sonnet', or 'opus' for a model name string."""
    if HAIKU_PATTERN.search(model_name):
        return "haiku"
    if OPUS_PATTERN.search(model_name):
        return "opus"
    return "sonnet"


def parse_cost_log(repo: Path) -> List[Dict[str, Any]]:
    """Parse COST_LOG.md session table rows."""
    path = repo / "COST_LOG.md"
    if not path.is_file():
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Warning: Could not read {path}: {exc}", file=sys.stderr)
        return []

    rows = []
    for m in COST_TABLE_ROW_RE.finditer(content):
        task_types_raw = m.group(5).strip()
        notes = m.group(7).strip() if m.group(7) else ""

        # Classify session type from task types field
        task_types_lower = task_types_raw.lower()
        if "security" in task_types_lower:
            session_type = "security"
        elif "arch" in task_types_lower or "adr" in task_types_lower:
            session_type = "architecture"
        elif "test" in task_types_lower:
            session_type = "testing"
        elif "docs" in task_types_lower or "doc" in task_types_lower:
            session_type = "documentation"
        else:
            session_type = "feature"

        model_raw = m.group(3).strip()
        rows.append(
            {
                "session": int(m.group(1)),
                "date": m.group(2),
                "month": m.group(2)[:7],  # YYYY-MM
                "model": model_raw,
                "tier": classify_model_tier(model_raw),
                "tasks": int(m.group(4)),
                "task_types": task_types_raw,
                "session_type": session_type,
                "cost": float(m.group(6)),
                "notes": notes,
            }
        )
    rows.sort(key=lambda r: r["session"])
    return rows


# ---------------------------------------------------------------------------
# Routing efficiency helpers
# ---------------------------------------------------------------------------

# Cost references (approximate USD per 1M tokens — used for efficiency scoring)
TIER_COST_PER_MILLION_TOKENS = {
    "haiku": 0.005,
    "sonnet": 0.025,
    "opus": 0.15,
}

# Tasks that should always use Opus
OPUS_TASK_KEYWORDS = {"security", "adr", "architecture", "threat", "compliance"}

# Tasks suitable for Haiku
HAIKU_TASK_KEYWORDS = {"status", "read", "config", "changelog", "doc"}


def routing_recommendation(tier: str, session_type: str) -> Tuple[str, str]:
    """Return (recommended_tier, reason) for a given session model and type."""
    if session_type in {"security", "architecture"}:
        if tier != "opus":
            return "opus", "Security and architecture tasks need Opus reasoning depth"
        return tier, "Correctly routed"
    if session_type in {"documentation"} and tier == "opus":
        return "sonnet", "Documentation does not need Opus — use Sonnet to reduce cost"
    if session_type in {"feature"} and tier == "haiku":
        return "sonnet", "Feature work typically requires Sonnet-level capability"
    return tier, "Correctly routed"


def compute_routing_efficiency(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate routing efficiency: actual cost vs. optimal routing cost."""
    actual_total = sum(r["cost"] for r in rows)
    optimal_total = 0.0
    misrouted = []

    for r in rows:
        recommended, reason = routing_recommendation(r["tier"], r["session_type"])
        # Estimate optimal cost using tier reference ratios
        actual_ref = TIER_COST_PER_MILLION_TOKENS.get(r["tier"], 0.025)
        optimal_ref = TIER_COST_PER_MILLION_TOKENS.get(recommended, 0.025)
        ratio = optimal_ref / actual_ref if actual_ref > 0 else 1.0
        estimated_optimal = r["cost"] * ratio
        optimal_total += estimated_optimal

        if recommended != r["tier"]:
            misrouted.append(
                {
                    "session": r["session"],
                    "model": r["model"],
                    "recommended": recommended,
                    "reason": reason,
                    "session_type": r["session_type"],
                }
            )

    efficiency_ratio = actual_total / optimal_total if optimal_total > 0 else 1.0
    return {
        "actual_total": actual_total,
        "optimal_total": optimal_total,
        "efficiency_ratio": efficiency_ratio,
        "misrouted": misrouted,
    }


# ---------------------------------------------------------------------------
# Dashboard section builders
# ---------------------------------------------------------------------------


def section_divider(title: str) -> str:
    line = "─" * 60
    return f"\n{line}\n## {title}\n{line}\n"


def build_summary_section(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "_No COST_LOG.md data found. Add cost tracking to session end protocol._"

    total = sum(r["cost"] for r in rows)
    sessions = len(rows)
    tasks = sum(r["tasks"] for r in rows)
    avg_per_session = total / sessions if sessions > 0 else 0
    cost_per_task = total / tasks if tasks > 0 else 0
    costs = [r["cost"] for r in rows]

    lines = [
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total sessions tracked | {sessions} |",
        f"| Total tasks completed | {tasks} |",
        f"| Total AI cost | ${total:.3f} |",
        f"| Average cost per session | ${avg_per_session:.3f} |",
        f"| Average cost per task | ${cost_per_task:.4f} |",
        f"| Cost trend (recent) | {sparkline(costs[-8:])} {trend_arrow(costs)} |",
    ]
    return "\n".join(lines)


def build_model_breakdown_section(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "_No data._"

    by_model: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"sessions": 0, "tasks": 0, "cost": 0.0}
    )
    for r in rows:
        by_model[r["model"]]["sessions"] += 1
        by_model[r["model"]]["tasks"] += r["tasks"]
        by_model[r["model"]]["cost"] += r["cost"]

    total_cost = sum(r["cost"] for r in rows)
    max_cost = max(d["cost"] for d in by_model.values()) if by_model else 1.0

    lines = [
        "| Model | Sessions | Tasks | Total Cost | Avg/Session | % of Spend | Bar |",
        "|-------|:--------:|:-----:|:----------:|:-----------:|:----------:|-----|",
    ]
    for model, data in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        avg_s = data["cost"] / data["sessions"] if data["sessions"] > 0 else 0
        pct = data["cost"] / total_cost * 100 if total_cost > 0 else 0
        bar = ascii_bar(data["cost"], max_cost, 10)
        lines.append(
            f"| `{model}` | {data['sessions']} | {data['tasks']} "
            f"| ${data['cost']:.3f} | ${avg_s:.3f} | {pct:.0f}% | {bar} |"
        )

    # Tier summary
    by_tier: Dict[str, float] = defaultdict(float)
    by_tier_count: Dict[str, int] = defaultdict(int)
    for r in rows:
        by_tier[r["tier"]] += r["cost"]
        by_tier_count[r["tier"]] += 1

    lines += [
        "",
        "**Tier summary:**",
        "| Tier | Sessions | Total Cost | % of Spend |",
        "|------|:--------:|:----------:|:----------:|",
    ]
    for tier in ["haiku", "sonnet", "opus"]:
        if tier in by_tier:
            pct = by_tier[tier] / total_cost * 100 if total_cost > 0 else 0
            lines.append(
                f"| {tier.capitalize()} | {by_tier_count[tier]} "
                f"| ${by_tier[tier]:.3f} | {pct:.0f}% |"
            )

    return "\n".join(lines)


def build_session_type_section(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "_No data._"

    by_type: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"sessions": 0, "tasks": 0, "cost": 0.0}
    )
    for r in rows:
        by_type[r["session_type"]]["sessions"] += 1
        by_type[r["session_type"]]["tasks"] += r["tasks"]
        by_type[r["session_type"]]["cost"] += r["cost"]

    total_cost = sum(r["cost"] for r in rows)
    max_cost = max(d["cost"] for d in by_type.values()) if by_type else 1.0

    lines = [
        "| Session Type | Sessions | Tasks | Total Cost | Cost/Task | Bar |",
        "|-------------|:--------:|:-----:|:----------:|:---------:|-----|",
    ]
    for stype, data in sorted(by_type.items(), key=lambda x: -x[1]["cost"]):
        cpt = data["cost"] / data["tasks"] if data["tasks"] > 0 else 0
        bar = ascii_bar(data["cost"], max_cost, 10)
        lines.append(
            f"| {stype} | {data['sessions']} | {data['tasks']} "
            f"| ${data['cost']:.3f} | ${cpt:.4f} | {bar} |"
        )

    return "\n".join(lines)


def build_monthly_section(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "_No data._"

    by_month: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"sessions": 0, "tasks": 0, "cost": 0.0, "models": set()}
    )
    for r in rows:
        by_month[r["month"]]["sessions"] += 1
        by_month[r["month"]]["tasks"] += r["tasks"]
        by_month[r["month"]]["cost"] += r["cost"]
        by_month[r["month"]]["models"].add(r["tier"])

    months = sorted(by_month.keys())
    monthly_costs = [by_month[m]["cost"] for m in months]
    max_cost = max(monthly_costs) if monthly_costs else 1.0

    lines = [
        "| Month | Sessions | Tasks | Total Cost | Avg/Session | Avg/Task | Trend |",
        "|-------|:--------:|:-----:|:----------:|:-----------:|:--------:|-------|",
    ]
    for i, month in enumerate(months):
        d = by_month[month]
        avg_s = d["cost"] / d["sessions"] if d["sessions"] > 0 else 0
        avg_t = d["cost"] / d["tasks"] if d["tasks"] > 0 else 0
        arrow = trend_arrow(monthly_costs[: i + 1])
        lines.append(
            f"| {month} | {d['sessions']} | {d['tasks']} "
            f"| ${d['cost']:.3f} | ${avg_s:.3f} | ${avg_t:.4f} | {arrow} |"
        )

    lines += [
        "",
        "```",
        "Monthly cost trend:",
        "",
    ]
    for month in months:
        bar = ascii_bar(by_month[month]["cost"], max_cost, 20)
        lines.append(f"  {month}  {bar}  ${by_month[month]['cost']:.3f}")
    lines.append("```")

    return "\n".join(lines)


def build_routing_efficiency_section(
    rows: List[Dict[str, Any]], efficiency: Dict[str, Any]
) -> str:
    if not rows:
        return "_No data._"

    ratio = efficiency["efficiency_ratio"]
    misrouted = efficiency["misrouted"]
    actual = efficiency["actual_total"]
    optimal = efficiency["optimal_total"]
    savings = actual - optimal

    if ratio <= 1.05:
        status = "✅ Excellent"
        interpretation = "Model routing is near-optimal."
    elif ratio <= 1.20:
        status = "⚠️ Acceptable"
        interpretation = "Minor routing inefficiencies detected. Review misrouted sessions."
    elif ratio <= 1.40:
        status = "❌ Suboptimal"
        interpretation = "Significant cost savings available through better model routing."
    else:
        status = "🔴 Poor"
        interpretation = "Major routing issues. Opus used for tasks suitable for Haiku/Sonnet."

    lines = [
        f"**Routing efficiency:** {status}  ({ratio:.2f}x — 1.0x = perfect)",
        f"_Interpretation: {interpretation}_\n",
        f"| Metric | Value |",
        "|--------|-------|",
        f"| Actual spend | ${actual:.3f} |",
        f"| Estimated optimal spend | ${optimal:.3f} |",
        f"| Estimated savings available | ${savings:.3f} |",
        f"| Efficiency ratio | {ratio:.2f}x |",
    ]

    if misrouted:
        lines += [
            "",
            f"**Misrouted sessions ({len(misrouted)}):**",
            "",
            "| Session | Used | Recommended | Session Type | Reason |",
            "|:-------:|------|-------------|:------------:|--------|",
        ]
        for m in misrouted:
            lines.append(
                f"| {m['session']} | {m['model']} | {m['recommended']} "
                f"| {m['session_type']} | {m['reason']} |"
            )
    else:
        lines.append("\n✅ No misrouted sessions detected.")

    return "\n".join(lines)


def build_recommendations_section(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "_No data available for recommendations._"

    by_type: Dict[str, List[str]] = defaultdict(list)
    for r in rows:
        by_type[r["session_type"]].append(r["tier"])

    lines = ["Based on your session history:\n"]

    # Check for tasks using Opus that could use Sonnet
    opus_doc_sessions = [
        r for r in rows if r["tier"] == "opus" and r["session_type"] == "documentation"
    ]
    if opus_doc_sessions:
        lines += [
            "### Switch: Opus → Sonnet for Documentation",
            "",
            "Documentation sessions do not require Opus-level reasoning. "
            "Switching to Sonnet saves ~80-90% per documentation session.\n",
            f"Affected sessions: {len(opus_doc_sessions)}",
            "",
        ]

    # Check for feature work on Haiku
    haiku_feature = [
        r for r in rows if r["tier"] == "haiku" and r["session_type"] == "feature"
    ]
    if haiku_feature:
        lines += [
            "### Upgrade: Haiku → Sonnet for Feature Work",
            "",
            "Feature implementation sessions require Sonnet-level code generation "
            "quality. Haiku may produce lower-quality output for complex features.\n",
            f"Affected sessions: {len(haiku_feature)}",
            "",
        ]

    # Check for security work on non-Opus
    non_opus_security = [
        r for r in rows if r["tier"] != "opus" and r["session_type"] == "security"
    ]
    if non_opus_security:
        lines += [
            "### Upgrade: → Opus for Security Reviews",
            "",
            "Security reviews require Opus reasoning depth to catch subtle "
            "vulnerabilities. Using Sonnet or Haiku creates false confidence.\n",
            f"Affected sessions: {len(non_opus_security)}",
            "",
        ]

    # General recommendations based on tiers
    tier_counts: Dict[str, int] = defaultdict(int)
    for r in rows:
        tier_counts[r["tier"]] += 1
    total = len(rows)

    haiku_pct = tier_counts["haiku"] / total * 100 if total > 0 else 0
    opus_pct = tier_counts["opus"] / total * 100 if total > 0 else 0

    lines.append("### General Routing Guidelines\n")
    lines += [
        "| Task Type | Recommended Tier | Rationale |",
        "|-----------|:----------------:|-----------|",
        "| Security review, ADR writing, architecture | Opus | "
        "High-stakes decisions need deep reasoning |",
        "| Feature implementation, code review, debugging | Sonnet | "
        "Standard quality at lower cost |",
        "| File reads, config edits, CHANGELOG updates | Haiku | "
        "10-20x cheaper, no quality loss |",
    ]

    if haiku_pct < 10 and total >= 5:
        lines += [
            "",
            f"⚠️ Haiku is currently {haiku_pct:.0f}% of sessions. "
            "Consider using Haiku for simple tasks (reads, config, status).",
        ]
    if opus_pct > 40:
        lines += [
            "",
            f"⚠️ Opus is {opus_pct:.0f}% of sessions — higher than typical. "
            "Verify all Opus sessions require architecture-level reasoning.",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dashboard assembler
# ---------------------------------------------------------------------------


def generate_cost_dashboard(repo: Path) -> str:
    """Generate the full COST_DASHBOARD.md content string."""
    repo = repo.resolve()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows = parse_cost_log(repo)
    efficiency = compute_routing_efficiency(rows) if rows else {}

    lines = [
        "# Cost Dashboard",
        "",
        f"> Generated: {now}  |  Repository: `{repo.name}`",
        "",
        "> This file is auto-generated by `automation/cost_dashboard.py`.",
        "> Do not edit manually — run the script to refresh.",
        "> Source data: `COST_LOG.md`",
        "",
    ]

    lines.append(section_divider("Summary"))
    lines.append(build_summary_section(rows))

    lines.append(section_divider("Cost by Model"))
    lines.append(build_model_breakdown_section(rows))

    lines.append(section_divider("Cost by Session Type"))
    lines.append(build_session_type_section(rows))

    lines.append(section_divider("Cost by Time Period"))
    lines.append(build_monthly_section(rows))

    lines.append(section_divider("Model Routing Efficiency"))
    lines.append(build_routing_efficiency_section(rows, efficiency or {}))

    lines.append(section_divider("Recommendations"))
    lines.append(build_recommendations_section(rows))

    lines += [
        "",
        "---",
        "",
        "*See [docs/metrics-guide.md](docs/metrics-guide.md) for cost metric definitions.*",
        "*See [docs/model-routing.md](docs/model-routing.md) for routing guidelines.*",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate a cost analysis dashboard from COST_LOG.md.",
        epilog="Output defaults to COST_DASHBOARD.md in the repo root.",
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
        default="COST_DASHBOARD.md",
        help="Output filename relative to repo root (default: COST_DASHBOARD.md)",
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
        dashboard = generate_cost_dashboard(repo)
    except Exception as exc:  # noqa: BLE001
        print(f"Error generating cost dashboard: {exc}", file=sys.stderr)
        return 1

    if args.stdout:
        print(dashboard)
        return 0

    output_path = repo / args.output
    output_path.write_text(dashboard, encoding="utf-8")
    print(f"Cost dashboard written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
