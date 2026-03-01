"""Tests for automation/governance_dashboard.py.

Covers: ASCII helpers (ascii_bar, sparkline, trend_arrow), CHANGELOG.md
parsing, COST_LOG.md parsing, MEMORY.md parsing, PROJECT_PLAN.md parsing,
ADR counting, all section builders, full dashboard generation, CLI argument
parser, and main() entry point including error paths.
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

import governance_dashboard as gd


# ---------------------------------------------------------------------------
# Fixture content
# ---------------------------------------------------------------------------

SAMPLE_CHANGELOG = """\
# CHANGELOG

## Session 1 -- 2025-01-10 [claude-sonnet-4]
- Tasks completed: 5
- Files modified: 3

## Session 2 -- 2025-01-20 [claude-opus-4]

- Tasks completed: 8
- Some other content

## Session 3 -- 2025-02-01 [claude-haiku-3]

"""

SAMPLE_COST_LOG = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 1 | 2025-01-10 | claude-sonnet-4 | 5 | docs | $0.120 | |
| 2 | 2025-01-20 | claude-opus-4 | 3 | security | $0.450 | |
"""

SAMPLE_PROJECT_PLAN = """\
# Project Plan

**Current phase:** Phase 2
**Sprint goal:** Implement governance layer
**Sprint dates:** 2025-01-01 to 2025-01-31
**Phase 1 progress:** 10/10 tasks complete (100%)
**Phase 2 progress:** 5/10 tasks complete (50%)
"""


# ---------------------------------------------------------------------------
# ascii_bar
# ---------------------------------------------------------------------------


class TestAsciiBar:
    def test_full_bar(self):
        result = gd.ascii_bar(10, 10, width=10)
        assert result == "█" * 10

    def test_empty_bar_zero_value(self):
        result = gd.ascii_bar(0, 10, width=10)
        assert result == "░" * 10

    def test_max_zero_returns_empty(self):
        result = gd.ascii_bar(5, 0, width=10)
        assert result == "░" * 10

    def test_width_respected(self):
        result = gd.ascii_bar(5, 10, width=20)
        assert len(result) == 20

    def test_value_exceeds_max_is_clamped(self):
        result = gd.ascii_bar(20, 10, width=5)
        assert result == "█" * 5

    def test_bar_contains_only_block_chars(self):
        result = gd.ascii_bar(3, 10, width=8)
        assert all(c in ("█", "░") for c in result)


# ---------------------------------------------------------------------------
# sparkline
# ---------------------------------------------------------------------------


class TestSparkline:
    def test_empty_returns_dash(self):
        assert gd.sparkline([]) == "—"

    def test_single_value(self):
        result = gd.sparkline([1.0])
        assert len(result) == 1

    def test_capped_at_width(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        result = gd.sparkline(values, width=4)
        assert len(result) == 4

    def test_all_zeros_handled(self):
        result = gd.sparkline([0, 0, 0])
        assert len(result) == 3

    def test_default_width_is_eight(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        result = gd.sparkline(values)
        assert len(result) == 8


# ---------------------------------------------------------------------------
# trend_arrow
# ---------------------------------------------------------------------------


class TestTrendArrow:
    def test_single_value_returns_neutral(self):
        assert gd.trend_arrow([1.0]) == "→"

    def test_empty_returns_neutral(self):
        assert gd.trend_arrow([]) == "→"

    def test_increasing_returns_up(self):
        assert gd.trend_arrow([1.0, 2.0]) == "↑"

    def test_decreasing_returns_down(self):
        assert gd.trend_arrow([2.0, 1.0]) == "↓"

    def test_equal_returns_neutral(self):
        assert gd.trend_arrow([5.0, 5.0]) == "→"


# ---------------------------------------------------------------------------
# parse_changelog
# ---------------------------------------------------------------------------


class TestParseChangelog:
    def test_missing_file_returns_empty_list(self, tmp_path):
        assert gd.parse_changelog(tmp_path) == []

    def test_parses_correct_session_count(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert len(sessions) == 3

    def test_session_numbers_parsed(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert sessions[0]["session"] == 1
        assert sessions[1]["session"] == 2

    def test_dates_parsed(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert sessions[0]["date"] == "2025-01-10"
        assert sessions[1]["date"] == "2025-01-20"

    def test_models_parsed(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert sessions[0]["model"] == "claude-sonnet-4"
        assert sessions[1]["model"] == "claude-opus-4"

    def test_tasks_counted(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert sessions[0]["tasks"] == 5
        assert sessions[1]["tasks"] == 8

    def test_session_with_no_tasks_gets_zero(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert sessions[2]["tasks"] == 0

    def test_tasks_completed_case_insensitive(self, tmp_path):
        changelog = """\
# CHANGELOG

## Session 1 -- 2025-01-10 [claude-sonnet-4]
- Completed tasks: 7
"""
        (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
        sessions = gd.parse_changelog(tmp_path)
        assert sessions[0]["tasks"] == 7


# ---------------------------------------------------------------------------
# parse_cost_log (governance_dashboard version)
# ---------------------------------------------------------------------------


class TestParseCostLog:
    def test_missing_file_returns_empty(self, tmp_path):
        assert gd.parse_cost_log(tmp_path) == []

    def test_parses_two_rows(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = gd.parse_cost_log(tmp_path)
        assert len(rows) == 2

    def test_cost_is_float(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = gd.parse_cost_log(tmp_path)
        assert rows[0]["cost"] == pytest.approx(0.120)
        assert rows[1]["cost"] == pytest.approx(0.450)

    def test_sorted_by_session_ascending(self, tmp_path):
        log = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 2 | 2025-01-20 | claude-sonnet-4 | 3 | feature | $0.100 | |
| 1 | 2025-01-10 | claude-sonnet-4 | 5 | feature | $0.080 | |
"""
        (tmp_path / "COST_LOG.md").write_text(log, encoding="utf-8")
        rows = gd.parse_cost_log(tmp_path)
        assert rows[0]["session"] == 1
        assert rows[1]["session"] == 2

    def test_model_stripped(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = gd.parse_cost_log(tmp_path)
        assert rows[0]["model"] == "claude-sonnet-4"

    def test_tasks_parsed_as_int(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = gd.parse_cost_log(tmp_path)
        assert rows[0]["tasks"] == 5


# ---------------------------------------------------------------------------
# parse_memory
# ---------------------------------------------------------------------------


class TestParseMemory:
    def test_missing_file_returns_not_exists(self, tmp_path):
        result = gd.parse_memory(tmp_path)
        assert result == {"exists": False}

    def test_basic_memory_file_detected(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "# Memory\n\n## Patterns\n\n- First pattern\n- Second pattern\n",
            encoding="utf-8",
        )
        result = gd.parse_memory(tmp_path)
        assert result["exists"] is True

    def test_sections_counted(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "# Memory\n\n## Section A\n\ntext\n\n## Section B\n\ntext\n",
            encoding="utf-8",
        )
        result = gd.parse_memory(tmp_path)
        assert result["sections"] == 2

    def test_knowledge_entries_counted(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "# Memory\n\n## Section\n\n- Entry one\n- Entry two\n* Entry three\n",
            encoding="utf-8",
        )
        result = gd.parse_memory(tmp_path)
        assert result["knowledge_entries"] == 3

    def test_last_updated_parsed(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "# Memory\n\n**Last updated:** 2025-01-15\n\n- entry\n",
            encoding="utf-8",
        )
        result = gd.parse_memory(tmp_path)
        assert result["last_updated"] == "2025-01-15"

    def test_placeholder_count(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "# Memory\n\n<!-- CUSTOMIZE: add your info -->\n\n<!-- CUSTOMIZE: more -->\n",
            encoding="utf-8",
        )
        result = gd.parse_memory(tmp_path)
        assert result["placeholder_sections"] == 2

    def test_no_last_updated_returns_none(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text("# Memory\n\n- entry\n", encoding="utf-8")
        result = gd.parse_memory(tmp_path)
        assert result["last_updated"] is None

    def test_case_insensitive_last_updated(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "# Memory\n\n**LAST UPDATED:** 2025-06-01\n\n- entry\n",
            encoding="utf-8",
        )
        result = gd.parse_memory(tmp_path)
        assert result["last_updated"] == "2025-06-01"


# ---------------------------------------------------------------------------
# parse_project_plan
# ---------------------------------------------------------------------------


class TestParseProjectPlan:
    def test_missing_file_returns_not_exists(self, tmp_path):
        result = gd.parse_project_plan(tmp_path)
        assert result == {"exists": False}

    def test_exists_is_true(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text(SAMPLE_PROJECT_PLAN, encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["exists"] is True

    def test_current_phase_parsed(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text(SAMPLE_PROJECT_PLAN, encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["current_phase"] == 2

    def test_sprint_goal_parsed(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text(SAMPLE_PROJECT_PLAN, encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["sprint_goal"] == "Implement governance layer"

    def test_sprint_dates_parsed(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text(SAMPLE_PROJECT_PLAN, encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["sprint_dates"] == "2025-01-01 to 2025-01-31"

    def test_phase_1_progress_parsed(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text(SAMPLE_PROJECT_PLAN, encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert 1 in result["phases"]
        assert result["phases"][1]["completed"] == 10
        assert result["phases"][1]["total"] == 10
        assert result["phases"][1]["pct"] == 100

    def test_phase_2_progress_parsed(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text(SAMPLE_PROJECT_PLAN, encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["phases"][2]["completed"] == 5
        assert result["phases"][2]["pct"] == 50

    def test_missing_sprint_goal_defaults_dash(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text("# Project Plan\n", encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["sprint_goal"] == "—"

    def test_missing_sprint_dates_defaults_dash(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text("# Project Plan\n", encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["sprint_dates"] == "—"

    def test_missing_current_phase_returns_none(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text("# Project Plan\n", encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["current_phase"] is None

    def test_no_phases_returns_empty_dict(self, tmp_path):
        (tmp_path / "PROJECT_PLAN.md").write_text("# Project Plan\n", encoding="utf-8")
        result = gd.parse_project_plan(tmp_path)
        assert result["phases"] == {}


# ---------------------------------------------------------------------------
# count_adrs
# ---------------------------------------------------------------------------


class TestCountAdrs:
    def test_no_adr_dir_returns_zero(self, tmp_path):
        result = gd.count_adrs(tmp_path)
        assert result == {"count": 0, "files": []}

    def test_empty_adr_dir_returns_zero(self, tmp_path):
        (tmp_path / "docs" / "adr").mkdir(parents=True)
        result = gd.count_adrs(tmp_path)
        assert result["count"] == 0

    def test_counts_adr_files(self, tmp_path):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-first.md").write_text("# ADR\n", encoding="utf-8")
        (adr_dir / "ADR-002-second.md").write_text("# ADR\n", encoding="utf-8")
        result = gd.count_adrs(tmp_path)
        assert result["count"] == 2

    def test_excludes_adr_000_template(self, tmp_path):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-000-template.md").write_text("# Template\n", encoding="utf-8")
        (adr_dir / "ADR-001-real.md").write_text("# ADR\n", encoding="utf-8")
        result = gd.count_adrs(tmp_path)
        assert result["count"] == 1
        assert "ADR-001-real.md" in result["files"]
        assert "ADR-000-template.md" not in result["files"]

    def test_files_returned_sorted(self, tmp_path):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-003-c.md").write_text("# ADR\n", encoding="utf-8")
        (adr_dir / "ADR-001-a.md").write_text("# ADR\n", encoding="utf-8")
        (adr_dir / "ADR-002-b.md").write_text("# ADR\n", encoding="utf-8")
        result = gd.count_adrs(tmp_path)
        assert result["files"] == sorted(result["files"])

    def test_non_md_files_excluded(self, tmp_path):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-real.md").write_text("# ADR\n", encoding="utf-8")
        (adr_dir / "README.txt").write_text("text\n", encoding="utf-8")
        result = gd.count_adrs(tmp_path)
        assert result["count"] == 1


# ---------------------------------------------------------------------------
# section_divider
# ---------------------------------------------------------------------------


class TestSectionDivider:
    def test_contains_title(self):
        assert "My Title" in gd.section_divider("My Title")

    def test_contains_h2(self):
        assert "## My Title" in gd.section_divider("My Title")

    def test_contains_divider_chars(self):
        assert "─" in gd.section_divider("Test")

    def test_starts_with_newline(self):
        assert gd.section_divider("X").startswith("\n")


# ---------------------------------------------------------------------------
# build_health_score_section
# ---------------------------------------------------------------------------


class TestBuildHealthScoreSection:
    def _make_report(self, score=50, max_score=100, level=2, label="Structured"):
        return {
            "score": score,
            "max_score": max_score,
            "level": level,
            "level_label": label,
            "checks": [
                {"name": "CLAUDE.md exists", "points": 10, "passed": True},
                {"name": "ADR files", "points": 5, "passed": False},
            ],
        }

    def test_score_fraction_appears(self):
        report = self._make_report(score=50, max_score=100)
        result = gd.build_health_score_section(report)
        assert "50/100" in result

    def test_passed_check_has_checkmark(self):
        report = self._make_report()
        result = gd.build_health_score_section(report)
        assert "✅" in result

    def test_failed_check_has_x_mark(self):
        report = self._make_report()
        result = gd.build_health_score_section(report)
        assert "❌" in result

    def test_level_label_appears(self):
        report = self._make_report(level=2, label="Structured")
        result = gd.build_health_score_section(report)
        assert "Structured" in result

    def test_check_names_present(self):
        report = self._make_report()
        result = gd.build_health_score_section(report)
        assert "CLAUDE.md exists" in result
        assert "ADR files" in result


# ---------------------------------------------------------------------------
# build_velocity_section
# ---------------------------------------------------------------------------


class TestBuildVelocitySection:
    def test_empty_sessions_returns_no_data_message(self):
        result = gd.build_velocity_section([])
        assert "No CHANGELOG.md" in result

    def test_session_count_appears(self):
        sessions = [
            {"session": 1, "tasks": 5, "date": "2025-01-01", "model": "sonnet"},
            {"session": 2, "tasks": 3, "date": "2025-01-02", "model": "sonnet"},
        ]
        result = gd.build_velocity_section(sessions)
        assert "2" in result

    def test_code_block_present(self):
        sessions = [{"session": 1, "tasks": 5, "date": "2025-01-01", "model": "sonnet"}]
        result = gd.build_velocity_section(sessions)
        assert "```" in result

    def test_sparkline_present(self):
        sessions = [{"session": 1, "tasks": 5, "date": "2025-01-01", "model": "sonnet"}]
        result = gd.build_velocity_section(sessions)
        assert "Sparkline" in result

    def test_average_tasks_shown(self):
        sessions = [
            {"session": 1, "tasks": 4, "date": "2025-01-01", "model": "sonnet"},
            {"session": 2, "tasks": 6, "date": "2025-01-02", "model": "sonnet"},
        ]
        result = gd.build_velocity_section(sessions)
        assert "5.0" in result

    def test_capped_at_last_ten_sessions(self):
        sessions = [
            {"session": i, "tasks": i, "date": f"2025-01-{i:02d}", "model": "sonnet"}
            for i in range(1, 15)
        ]
        result = gd.build_velocity_section(sessions)
        assert "last 10" in result


# ---------------------------------------------------------------------------
# build_cost_section
# ---------------------------------------------------------------------------


class TestBuildCostSection:
    def test_empty_returns_no_data_message(self):
        result = gd.build_cost_section([])
        assert "No COST_LOG.md" in result

    def test_total_cost_appears(self):
        rows = [
            {"session": 1, "cost": 0.10, "tasks": 3, "model": "claude-sonnet-4"},
            {"session": 2, "cost": 0.20, "tasks": 4, "model": "claude-sonnet-4"},
        ]
        result = gd.build_cost_section(rows)
        assert "$0.30" in result

    def test_model_appears_in_distribution(self):
        rows = [{"session": 1, "cost": 0.1, "tasks": 3, "model": "claude-opus-4"}]
        result = gd.build_cost_section(rows)
        assert "claude-opus-4" in result

    def test_code_block_present(self):
        rows = [{"session": 1, "cost": 0.1, "tasks": 3, "model": "claude-sonnet-4"}]
        result = gd.build_cost_section(rows)
        assert "```" in result

    def test_sparkline_and_trend_shown(self):
        rows = [{"session": 1, "cost": 0.1, "tasks": 3, "model": "claude-sonnet-4"}]
        result = gd.build_cost_section(rows)
        assert "Sparkline" in result
        assert "Trend" in result

    def test_cost_per_task_shown(self):
        rows = [{"session": 1, "cost": 0.10, "tasks": 5, "model": "claude-sonnet-4"}]
        result = gd.build_cost_section(rows)
        assert "Cost/task" in result


# ---------------------------------------------------------------------------
# build_knowledge_section
# ---------------------------------------------------------------------------


class TestBuildKnowledgeSection:
    def test_no_memory_returns_not_found(self):
        result = gd.build_knowledge_section({"exists": False})
        assert "No MEMORY.md" in result

    def test_last_updated_appears(self):
        memory = {
            "exists": True,
            "last_updated": "2025-01-15",
            "sections": 3,
            "knowledge_entries": 10,
            "placeholder_sections": 0,
        }
        result = gd.build_knowledge_section(memory)
        assert "2025-01-15" in result

    def test_sections_count_shown(self):
        memory = {
            "exists": True,
            "last_updated": None,
            "sections": 5,
            "knowledge_entries": 20,
            "placeholder_sections": 0,
        }
        result = gd.build_knowledge_section(memory)
        assert "5" in result

    def test_placeholder_warning_shown(self):
        memory = {
            "exists": True,
            "last_updated": None,
            "sections": 2,
            "knowledge_entries": 5,
            "placeholder_sections": 2,
        }
        result = gd.build_knowledge_section(memory)
        assert "placeholder" in result.lower() or "CUSTOMIZE" in result

    def test_fresh_label_for_today(self):
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        memory = {
            "exists": True,
            "last_updated": today_str,
            "sections": 3,
            "knowledge_entries": 10,
            "placeholder_sections": 0,
        }
        result = gd.build_knowledge_section(memory)
        assert "Fresh" in result

    def test_stale_label_for_old_date(self):
        memory = {
            "exists": True,
            "last_updated": "2020-01-01",
            "sections": 3,
            "knowledge_entries": 10,
            "placeholder_sections": 0,
        }
        result = gd.build_knowledge_section(memory)
        assert "Stale" in result

    def test_unknown_freshness_for_none_last_updated(self):
        memory = {
            "exists": True,
            "last_updated": None,
            "sections": 2,
            "knowledge_entries": 5,
            "placeholder_sections": 0,
        }
        result = gd.build_knowledge_section(memory)
        assert "unknown" in result


# ---------------------------------------------------------------------------
# build_adr_section
# ---------------------------------------------------------------------------


class TestBuildAdrSection:
    def test_no_adrs_returns_not_found_message(self):
        result = gd.build_adr_section({"count": 0, "files": []})
        assert "No ADRs found" in result

    def test_adr_count_appears(self):
        result = gd.build_adr_section(
            {"count": 3, "files": ["ADR-001.md", "ADR-002.md", "ADR-003.md"]}
        )
        assert "3" in result

    def test_file_names_appear(self):
        result = gd.build_adr_section({"count": 1, "files": ["ADR-001-first.md"]})
        assert "ADR-001-first.md" in result

    def test_table_header_present(self):
        result = gd.build_adr_section(
            {"count": 2, "files": ["ADR-001.md", "ADR-002.md"]}
        )
        assert "ADR File" in result


# ---------------------------------------------------------------------------
# build_sprint_section
# ---------------------------------------------------------------------------


class TestBuildSprintSection:
    def test_no_plan_returns_not_active(self):
        result = gd.build_sprint_section({"exists": False})
        assert "No PROJECT_PLAN.md" in result

    def test_sprint_goal_appears(self):
        plan = {
            "exists": True,
            "sprint_goal": "Ship v1.0",
            "sprint_dates": "2025-01-01 to 2025-01-31",
            "current_phase": 1,
            "phases": {},
        }
        result = gd.build_sprint_section(plan)
        assert "Ship v1.0" in result

    def test_sprint_dates_appear(self):
        plan = {
            "exists": True,
            "sprint_goal": "Ship v1.0",
            "sprint_dates": "2025-01-01 to 2025-01-31",
            "current_phase": 1,
            "phases": {},
        }
        result = gd.build_sprint_section(plan)
        assert "2025-01-01 to 2025-01-31" in result

    def test_phase_progress_bar_present(self):
        plan = {
            "exists": True,
            "sprint_goal": "Test",
            "sprint_dates": "—",
            "current_phase": 1,
            "phases": {1: {"completed": 5, "total": 10, "pct": 50}},
        }
        result = gd.build_sprint_section(plan)
        assert "Phase 1" in result
        assert "5/10" in result

    def test_current_phase_marked(self):
        plan = {
            "exists": True,
            "sprint_goal": "Test",
            "sprint_dates": "—",
            "current_phase": 2,
            "phases": {
                1: {"completed": 10, "total": 10, "pct": 100},
                2: {"completed": 3, "total": 10, "pct": 30},
            },
        }
        result = gd.build_sprint_section(plan)
        assert "current" in result

    def test_no_phases_shows_hint(self):
        plan = {
            "exists": True,
            "sprint_goal": "Test",
            "sprint_dates": "—",
            "current_phase": None,
            "phases": {},
        }
        result = gd.build_sprint_section(plan)
        assert "Progress percentages not found" in result

    def test_multiple_phases_all_shown(self):
        plan = {
            "exists": True,
            "sprint_goal": "Test",
            "sprint_dates": "—",
            "current_phase": 3,
            "phases": {
                1: {"completed": 10, "total": 10, "pct": 100},
                2: {"completed": 5, "total": 10, "pct": 50},
                3: {"completed": 2, "total": 10, "pct": 20},
            },
        }
        result = gd.build_sprint_section(plan)
        assert "Phase 1" in result
        assert "Phase 2" in result
        assert "Phase 3" in result


# ---------------------------------------------------------------------------
# build_maturity_section
# ---------------------------------------------------------------------------


class TestBuildMaturitySection:
    def _make_report(self, score=30, level=1, label="Foundation"):
        return {
            "score": score,
            "max_score": 100,
            "level": level,
            "level_label": label,
            "checks": [
                {"name": "CLAUDE.md exists", "points": 10, "passed": True},
                {"name": "ADR files", "points": 5, "passed": False},
            ],
        }

    def test_current_level_appears(self):
        report = self._make_report(level=1, label="Foundation")
        result = gd.build_maturity_section(report)
        assert "Level 1" in result
        assert "Foundation" in result

    def test_missing_checks_listed(self):
        report = self._make_report()
        result = gd.build_maturity_section(report)
        assert "ADR files" in result

    def test_score_percentage_shown(self):
        report = self._make_report(score=30)
        result = gd.build_maturity_section(report)
        assert "30%" in result

    def test_next_level_shown_when_not_at_max(self):
        report = self._make_report(level=1)
        result = gd.build_maturity_section(report)
        assert "Level 2" in result

    def test_level_5_no_next_level_shown(self):
        report = {
            "score": 100,
            "max_score": 100,
            "level": 5,
            "level_label": "Self-optimizing",
            "checks": [{"name": "All checks", "points": 100, "passed": True}],
        }
        result = gd.build_maturity_section(report)
        assert "Level 5" in result
        assert "Level 6" not in result

    def test_level_description_appears(self):
        report = self._make_report(level=1, label="Foundation")
        result = gd.build_maturity_section(report)
        assert "Foundation" in result


# ---------------------------------------------------------------------------
# generate_dashboard (integration)
# ---------------------------------------------------------------------------


class TestGenerateDashboard:
    def test_empty_repo_generates_dashboard(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "# Governance Dashboard" in result

    def test_health_score_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "Health Score" in result

    def test_session_velocity_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "Session Velocity" in result

    def test_cost_trend_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "Cost Trend" in result

    def test_knowledge_health_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "Knowledge Health" in result

    def test_adr_coverage_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "ADR Coverage" in result

    def test_sprint_progress_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "Sprint Progress" in result

    def test_maturity_level_section_present(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert "Governance Maturity Level" in result

    def test_dashboard_with_data_non_empty(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(SAMPLE_CHANGELOG, encoding="utf-8")
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        result = gd.generate_dashboard(tmp_path)
        assert "# Governance Dashboard" in result
        assert len(result) > 200

    def test_repo_name_in_header(self, tmp_path):
        result = gd.generate_dashboard(tmp_path)
        assert tmp_path.name in result


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    def test_repo_path_default_is_dot(self):
        parser = gd.build_parser()
        args = parser.parse_args([])
        assert str(args.repo_path) == "."

    def test_output_default_is_dashboard(self):
        parser = gd.build_parser()
        args = parser.parse_args([])
        assert args.output == "DASHBOARD.md"

    def test_stdout_flag_defaults_false(self):
        parser = gd.build_parser()
        args = parser.parse_args([])
        assert args.stdout is False

    def test_stdout_flag_set_true(self):
        parser = gd.build_parser()
        args = parser.parse_args(["--stdout"])
        assert args.stdout is True

    def test_custom_repo_path(self):
        parser = gd.build_parser()
        args = parser.parse_args(["--repo-path", "/some/path"])
        assert str(args.repo_path) == "/some/path"

    def test_custom_output_name(self):
        parser = gd.build_parser()
        args = parser.parse_args(["--output", "MY_DASH.md"])
        assert args.output == "MY_DASH.md"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain:
    def test_stdout_mode_returns_zero(self, tmp_path):
        with patch(
            "sys.argv",
            ["governance_dashboard.py", "--repo-path", str(tmp_path), "--stdout"],
        ):
            code = gd.main()
        assert code == 0

    def test_writes_file_and_returns_zero(self, tmp_path):
        with patch(
            "sys.argv", ["governance_dashboard.py", "--repo-path", str(tmp_path)]
        ):
            code = gd.main()
        assert code == 0
        assert (tmp_path / "DASHBOARD.md").is_file()

    def test_invalid_repo_path_returns_one(self, tmp_path):
        nonexistent = str(tmp_path / "no_such_dir")
        with patch("sys.argv", ["governance_dashboard.py", "--repo-path", nonexistent]):
            code = gd.main()
        assert code == 1

    def test_custom_output_file_created(self, tmp_path):
        with patch(
            "sys.argv",
            [
                "governance_dashboard.py",
                "--repo-path",
                str(tmp_path),
                "--output",
                "MY_DASH.md",
            ],
        ):
            code = gd.main()
        assert code == 0
        assert (tmp_path / "MY_DASH.md").is_file()

    def test_generate_exception_returns_one(self, tmp_path):
        with patch(
            "governance_dashboard.generate_dashboard", side_effect=RuntimeError("fail")
        ):
            with patch(
                "sys.argv", ["governance_dashboard.py", "--repo-path", str(tmp_path)]
            ):
                code = gd.main()
        assert code == 1

    def test_stdout_mode_prints_dashboard_header(self, tmp_path, capsys):
        with patch(
            "sys.argv",
            ["governance_dashboard.py", "--repo-path", str(tmp_path), "--stdout"],
        ):
            gd.main()
        output = capsys.readouterr().out
        assert "# Governance Dashboard" in output
