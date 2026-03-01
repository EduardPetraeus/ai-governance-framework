"""Tests for automation/cost_dashboard.py.

Covers: ASCII helpers (ascii_bar, sparkline, trend_arrow), model tier
classification, COST_LOG.md parsing, routing recommendations, routing
efficiency calculation, all section builders, full dashboard generation,
CLI argument parser, and main() entry point including error paths.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

import cost_dashboard as cd


# ---------------------------------------------------------------------------
# COST_LOG.md fixture content
# ---------------------------------------------------------------------------

SAMPLE_COST_LOG = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 1 | 2025-01-10 | claude-sonnet-4 | 5 | docs, config | $0.120 | |
| 2 | 2025-01-15 | claude-opus-4 | 3 | security, adr | $0.450 | Review |
| 3 | 2025-02-01 | claude-haiku-3 | 8 | test, status | $0.025 | Fast |
"""


# ---------------------------------------------------------------------------
# ascii_bar
# ---------------------------------------------------------------------------

class TestAsciiBar:
    def test_full_bar_when_value_equals_max(self):
        result = cd.ascii_bar(10, 10, width=10)
        assert result == "█" * 10

    def test_empty_bar_when_value_is_zero(self):
        result = cd.ascii_bar(0, 10, width=10)
        assert result == "░" * 10

    def test_half_bar(self):
        result = cd.ascii_bar(5, 10, width=10)
        assert result.count("█") == 5
        assert result.count("░") == 5

    def test_max_value_zero_returns_empty_bar(self):
        result = cd.ascii_bar(5, 0, width=10)
        assert result == "░" * 10

    def test_value_exceeding_max_is_clamped(self):
        result = cd.ascii_bar(20, 10, width=10)
        assert result == "█" * 10

    def test_width_respected(self):
        result = cd.ascii_bar(5, 10, width=20)
        assert len(result) == 20

    def test_bar_contains_only_block_chars(self):
        result = cd.ascii_bar(3, 10, width=8)
        assert all(c in ("█", "░") for c in result)


# ---------------------------------------------------------------------------
# sparkline
# ---------------------------------------------------------------------------

class TestSparkline:
    def test_empty_values_returns_dash(self):
        assert cd.sparkline([]) == "—"

    def test_single_value_returns_one_char(self):
        result = cd.sparkline([1.0])
        assert len(result) == 1

    def test_all_zero_values_handled(self):
        result = cd.sparkline([0, 0, 0])
        assert len(result) == 3

    def test_ascending_values_end_higher(self):
        result = cd.sparkline([1.0, 5.0, 9.0])
        blocks = " ▁▂▃▄▅▆▇█"
        assert blocks.index(result[-1]) > blocks.index(result[0])

    def test_length_equals_input_length(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert len(cd.sparkline(values)) == len(values)

    def test_all_equal_values(self):
        result = cd.sparkline([3.0, 3.0, 3.0])
        assert len(result) == 3


# ---------------------------------------------------------------------------
# trend_arrow
# ---------------------------------------------------------------------------

class TestTrendArrow:
    def test_single_value_returns_neutral(self):
        assert cd.trend_arrow([1.0]) == "→"

    def test_empty_list_returns_neutral(self):
        assert cd.trend_arrow([]) == "→"

    def test_increasing_returns_up(self):
        assert cd.trend_arrow([0.01, 0.05]) == "↑"

    def test_decreasing_returns_down(self):
        assert cd.trend_arrow([0.05, 0.01]) == "↓"

    def test_equal_values_returns_neutral(self):
        assert cd.trend_arrow([0.05, 0.05]) == "→"

    def test_delta_below_threshold_is_neutral(self):
        # delta = 0.0005 which is < 0.001 threshold
        assert cd.trend_arrow([0.1000, 0.1005]) == "→"

    def test_delta_above_threshold_upward(self):
        assert cd.trend_arrow([0.10, 0.20]) == "↑"


# ---------------------------------------------------------------------------
# classify_model_tier
# ---------------------------------------------------------------------------

class TestClassifyModelTier:
    def test_haiku_name(self):
        assert cd.classify_model_tier("claude-haiku-3") == "haiku"

    def test_sonnet_name(self):
        assert cd.classify_model_tier("claude-sonnet-4") == "sonnet"

    def test_opus_name(self):
        assert cd.classify_model_tier("claude-opus-4") == "opus"

    def test_haiku_case_insensitive(self):
        assert cd.classify_model_tier("Claude-Haiku-3") == "haiku"

    def test_opus_case_insensitive(self):
        assert cd.classify_model_tier("Claude-OPUS-4") == "opus"

    def test_unknown_model_defaults_to_sonnet(self):
        assert cd.classify_model_tier("gpt-4o") == "sonnet"

    def test_haiku_takes_priority_over_opus_in_same_name(self):
        # haiku pattern checked before opus
        assert cd.classify_model_tier("haiku-opus-mix") == "haiku"

    def test_sonnet_pattern_matches(self):
        assert cd.classify_model_tier("claude-sonnet-3-5") == "sonnet"


# ---------------------------------------------------------------------------
# parse_cost_log
# ---------------------------------------------------------------------------

class TestParseCostLog:
    def test_missing_file_returns_empty_list(self, tmp_path):
        assert cd.parse_cost_log(tmp_path) == []

    def test_parses_correct_number_of_rows(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert len(rows) == 3

    def test_session_numbers_parsed(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["session"] == 1
        assert rows[1]["session"] == 2
        assert rows[2]["session"] == 3

    def test_costs_parsed_as_float(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["cost"] == pytest.approx(0.120)
        assert rows[1]["cost"] == pytest.approx(0.450)
        assert rows[2]["cost"] == pytest.approx(0.025)

    def test_tiers_classified_correctly(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["tier"] == "sonnet"
        assert rows[1]["tier"] == "opus"
        assert rows[2]["tier"] == "haiku"

    def test_docs_session_type_classified(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["session_type"] == "documentation"

    def test_security_session_type_classified(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[1]["session_type"] == "security"

    def test_testing_session_type_classified(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[2]["session_type"] == "testing"

    def test_month_extracted_correctly(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["month"] == "2025-01"
        assert rows[2]["month"] == "2025-02"

    def test_rows_sorted_by_session(self, tmp_path):
        reversed_log = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 3 | 2025-02-01 | claude-sonnet-4 | 5 | feature | $0.100 | |
| 1 | 2025-01-01 | claude-sonnet-4 | 3 | feature | $0.050 | |
| 2 | 2025-01-15 | claude-sonnet-4 | 4 | feature | $0.075 | |
"""
        (tmp_path / "COST_LOG.md").write_text(reversed_log, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert [r["session"] for r in rows] == [1, 2, 3]

    def test_adr_task_type_classified_as_architecture(self, tmp_path):
        log = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 1 | 2025-01-01 | claude-opus-4 | 2 | adr writing | $0.200 | |
"""
        (tmp_path / "COST_LOG.md").write_text(log, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["session_type"] == "architecture"

    def test_arch_task_type_classified_as_architecture(self, tmp_path):
        log = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 1 | 2025-01-01 | claude-opus-4 | 2 | architecture review | $0.200 | |
"""
        (tmp_path / "COST_LOG.md").write_text(log, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["session_type"] == "architecture"

    def test_feature_is_default_session_type(self, tmp_path):
        log = """\
# COST_LOG.md

| # | Date | Model | Tasks | Task Types | Cost | Notes |
|---|------|-------|-------|------------|------|-------|
| 1 | 2025-01-01 | claude-sonnet-4 | 5 | implementation, refactor | $0.080 | |
"""
        (tmp_path / "COST_LOG.md").write_text(log, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["session_type"] == "feature"

    def test_notes_parsed_when_present(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[1]["notes"] == "Review"

    def test_tasks_parsed_as_int(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        rows = cd.parse_cost_log(tmp_path)
        assert rows[0]["tasks"] == 5
        assert rows[2]["tasks"] == 8


# ---------------------------------------------------------------------------
# routing_recommendation
# ---------------------------------------------------------------------------

class TestRoutingRecommendation:
    def test_security_on_sonnet_recommends_opus(self):
        tier, reason = cd.routing_recommendation("sonnet", "security")
        assert tier == "opus"
        assert "Security" in reason

    def test_security_on_haiku_recommends_opus(self):
        tier, reason = cd.routing_recommendation("haiku", "security")
        assert tier == "opus"

    def test_security_on_opus_is_correct(self):
        tier, reason = cd.routing_recommendation("opus", "security")
        assert tier == "opus"
        assert reason == "Correctly routed"

    def test_architecture_on_haiku_recommends_opus(self):
        tier, reason = cd.routing_recommendation("haiku", "architecture")
        assert tier == "opus"

    def test_architecture_on_opus_is_correct(self):
        tier, reason = cd.routing_recommendation("opus", "architecture")
        assert tier == "opus"
        assert reason == "Correctly routed"

    def test_documentation_on_opus_recommends_sonnet(self):
        tier, reason = cd.routing_recommendation("opus", "documentation")
        assert tier == "sonnet"
        assert "Documentation" in reason

    def test_documentation_on_sonnet_is_correct(self):
        tier, reason = cd.routing_recommendation("sonnet", "documentation")
        assert tier == "sonnet"
        assert reason == "Correctly routed"

    def test_feature_on_haiku_recommends_sonnet(self):
        tier, reason = cd.routing_recommendation("haiku", "feature")
        assert tier == "sonnet"
        assert "Feature" in reason

    def test_feature_on_sonnet_is_correct(self):
        tier, reason = cd.routing_recommendation("sonnet", "feature")
        assert tier == "sonnet"
        assert reason == "Correctly routed"

    def test_testing_on_sonnet_is_correct(self):
        tier, reason = cd.routing_recommendation("sonnet", "testing")
        assert tier == "sonnet"
        assert reason == "Correctly routed"

    def test_documentation_on_haiku_is_correct(self):
        tier, reason = cd.routing_recommendation("haiku", "documentation")
        assert tier == "haiku"
        assert reason == "Correctly routed"


# ---------------------------------------------------------------------------
# compute_routing_efficiency
# ---------------------------------------------------------------------------

class TestComputeRoutingEfficiency:
    def test_empty_rows_returns_zero_actual(self):
        result = cd.compute_routing_efficiency([])
        assert result["actual_total"] == 0.0

    def test_empty_rows_efficiency_ratio_is_one(self):
        result = cd.compute_routing_efficiency([])
        assert result["efficiency_ratio"] == pytest.approx(1.0)

    def test_correctly_routed_sessions_have_no_misrouted(self):
        rows = [
            {"session": 1, "cost": 0.1, "tier": "sonnet", "session_type": "feature"},
            {"session": 2, "cost": 0.2, "tier": "opus", "session_type": "security"},
        ]
        result = cd.compute_routing_efficiency(rows)
        assert result["misrouted"] == []

    def test_correctly_routed_efficiency_ratio_is_one(self):
        rows = [
            {"session": 1, "cost": 0.1, "tier": "sonnet", "session_type": "feature"},
        ]
        result = cd.compute_routing_efficiency(rows)
        assert result["efficiency_ratio"] == pytest.approx(1.0)

    def test_misrouted_session_detected(self):
        rows = [
            {
                "session": 1, "cost": 0.5, "tier": "opus",
                "session_type": "documentation", "model": "claude-opus-4",
            },
        ]
        result = cd.compute_routing_efficiency(rows)
        assert len(result["misrouted"]) == 1
        assert result["misrouted"][0]["session"] == 1

    def test_misrouted_has_recommended_tier(self):
        rows = [
            {
                "session": 5, "cost": 0.5, "tier": "opus",
                "session_type": "documentation", "model": "claude-opus-4",
            },
        ]
        result = cd.compute_routing_efficiency(rows)
        assert result["misrouted"][0]["recommended"] == "sonnet"

    def test_actual_total_is_sum_of_costs(self):
        rows = [
            {"session": 1, "cost": 0.10, "tier": "sonnet", "session_type": "feature"},
            {"session": 2, "cost": 0.20, "tier": "sonnet", "session_type": "feature"},
        ]
        result = cd.compute_routing_efficiency(rows)
        assert result["actual_total"] == pytest.approx(0.30)

    def test_optimal_total_computed(self):
        rows = [
            {"session": 1, "cost": 0.10, "tier": "sonnet", "session_type": "feature"},
        ]
        result = cd.compute_routing_efficiency(rows)
        assert result["optimal_total"] > 0


# ---------------------------------------------------------------------------
# section_divider
# ---------------------------------------------------------------------------

class TestSectionDivider:
    def test_contains_title(self):
        assert "My Section" in cd.section_divider("My Section")

    def test_contains_markdown_h2(self):
        assert "## My Section" in cd.section_divider("My Section")

    def test_contains_divider_line(self):
        assert "─" in cd.section_divider("Test")

    def test_starts_with_newline(self):
        result = cd.section_divider("X")
        assert result.startswith("\n")


# ---------------------------------------------------------------------------
# build_summary_section
# ---------------------------------------------------------------------------

class TestBuildSummarySection:
    def test_empty_rows_returns_no_data_message(self):
        result = cd.build_summary_section([])
        assert "No COST_LOG.md data" in result

    def test_total_cost_appears_in_output(self):
        rows = [
            {"session": 1, "date": "2025-01-01", "cost": 0.10, "tasks": 5},
            {"session": 2, "date": "2025-01-02", "cost": 0.20, "tasks": 3},
        ]
        result = cd.build_summary_section(rows)
        assert "$0.300" in result

    def test_session_count_appears(self):
        rows = [{"session": 1, "date": "2025-01-01", "cost": 0.10, "tasks": 5}]
        result = cd.build_summary_section(rows)
        assert "1" in result

    def test_table_has_metric_column(self):
        rows = [{"session": 1, "date": "2025-01-01", "cost": 0.05, "tasks": 2}]
        result = cd.build_summary_section(rows)
        assert "Metric" in result

    def test_sparkline_present(self):
        rows = [{"session": 1, "date": "2025-01-01", "cost": 0.05, "tasks": 2}]
        result = cd.build_summary_section(rows)
        assert "Cost trend" in result


# ---------------------------------------------------------------------------
# build_model_breakdown_section
# ---------------------------------------------------------------------------

class TestBuildModelBreakdownSection:
    def test_empty_rows_returns_no_data(self):
        assert cd.build_model_breakdown_section([]) == "_No data._"

    def test_model_name_appears_in_table(self):
        rows = [{"model": "claude-sonnet-4", "tier": "sonnet", "cost": 0.1, "tasks": 3}]
        result = cd.build_model_breakdown_section(rows)
        assert "claude-sonnet-4" in result

    def test_tier_summary_header_present(self):
        rows = [{"model": "claude-sonnet-4", "tier": "sonnet", "cost": 0.1, "tasks": 3}]
        result = cd.build_model_breakdown_section(rows)
        assert "Tier summary" in result

    def test_multiple_models_sorted_by_cost_descending(self):
        rows = [
            {"model": "claude-haiku-3", "tier": "haiku", "cost": 0.02, "tasks": 5},
            {"model": "claude-opus-4", "tier": "opus", "cost": 0.50, "tasks": 2},
        ]
        result = cd.build_model_breakdown_section(rows)
        assert result.index("claude-opus-4") < result.index("claude-haiku-3")

    def test_haiku_tier_in_summary(self):
        rows = [{"model": "claude-haiku-3", "tier": "haiku", "cost": 0.02, "tasks": 5}]
        result = cd.build_model_breakdown_section(rows)
        assert "Haiku" in result

    def test_percentage_column_present(self):
        rows = [{"model": "claude-sonnet-4", "tier": "sonnet", "cost": 0.1, "tasks": 3}]
        result = cd.build_model_breakdown_section(rows)
        assert "%" in result


# ---------------------------------------------------------------------------
# build_session_type_section
# ---------------------------------------------------------------------------

class TestBuildSessionTypeSection:
    def test_empty_rows_returns_no_data(self):
        assert cd.build_session_type_section([]) == "_No data._"

    def test_session_types_appear_in_output(self):
        rows = [
            {"session_type": "feature", "cost": 0.1, "tasks": 4},
            {"session_type": "security", "cost": 0.3, "tasks": 2},
        ]
        result = cd.build_session_type_section(rows)
        assert "feature" in result
        assert "security" in result

    def test_table_header_present(self):
        rows = [{"session_type": "feature", "cost": 0.1, "tasks": 4}]
        result = cd.build_session_type_section(rows)
        assert "Session Type" in result

    def test_cost_per_task_shown(self):
        rows = [{"session_type": "feature", "cost": 0.1, "tasks": 5}]
        result = cd.build_session_type_section(rows)
        assert "$0.0200" in result


# ---------------------------------------------------------------------------
# build_monthly_section
# ---------------------------------------------------------------------------

class TestBuildMonthlysection:
    def test_empty_rows_returns_no_data(self):
        assert cd.build_monthly_section([]) == "_No data._"

    def test_months_appear_in_output(self):
        rows = [
            {"month": "2025-01", "cost": 0.10, "tasks": 5, "tier": "sonnet"},
            {"month": "2025-02", "cost": 0.20, "tasks": 8, "tier": "sonnet"},
        ]
        result = cd.build_monthly_section(rows)
        assert "2025-01" in result
        assert "2025-02" in result

    def test_code_block_present(self):
        rows = [{"month": "2025-01", "cost": 0.10, "tasks": 5, "tier": "sonnet"}]
        result = cd.build_monthly_section(rows)
        assert "```" in result

    def test_trend_arrow_appears(self):
        rows = [
            {"month": "2025-01", "cost": 0.10, "tasks": 5, "tier": "sonnet"},
            {"month": "2025-02", "cost": 0.20, "tasks": 8, "tier": "sonnet"},
        ]
        result = cd.build_monthly_section(rows)
        assert "↑" in result or "↓" in result or "→" in result

    def test_monthly_cost_trend_label_present(self):
        rows = [{"month": "2025-01", "cost": 0.10, "tasks": 5, "tier": "sonnet"}]
        result = cd.build_monthly_section(rows)
        assert "Monthly cost trend" in result


# ---------------------------------------------------------------------------
# build_routing_efficiency_section
# ---------------------------------------------------------------------------

class TestBuildRoutingEfficiencySection:
    def test_empty_rows_returns_no_data(self):
        result = cd.build_routing_efficiency_section([], {})
        assert "_No data._" in result

    def test_excellent_status_for_low_ratio(self):
        efficiency = {
            "efficiency_ratio": 1.02,
            "misrouted": [],
            "actual_total": 1.02,
            "optimal_total": 1.00,
        }
        rows = [{"session": 1}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "Excellent" in result

    def test_acceptable_status_for_medium_ratio(self):
        efficiency = {
            "efficiency_ratio": 1.15,
            "misrouted": [],
            "actual_total": 1.15,
            "optimal_total": 1.00,
        }
        rows = [{"session": 1}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "Acceptable" in result

    def test_suboptimal_status_for_high_ratio(self):
        efficiency = {
            "efficiency_ratio": 1.30,
            "misrouted": [],
            "actual_total": 1.30,
            "optimal_total": 1.00,
        }
        rows = [{"session": 1}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "Suboptimal" in result

    def test_poor_status_for_very_high_ratio(self):
        efficiency = {
            "efficiency_ratio": 1.50,
            "misrouted": [],
            "actual_total": 1.50,
            "optimal_total": 1.00,
        }
        rows = [{"session": 1}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "Poor" in result

    def test_misrouted_sessions_listed(self):
        efficiency = {
            "efficiency_ratio": 1.20,
            "misrouted": [
                {
                    "session": 3,
                    "model": "claude-opus-4",
                    "recommended": "sonnet",
                    "session_type": "documentation",
                    "reason": "Documentation does not need Opus",
                }
            ],
            "actual_total": 1.20,
            "optimal_total": 1.00,
        }
        rows = [{"session": 3}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "sonnet" in result
        assert "documentation" in result

    def test_no_misrouted_shows_checkmark_message(self):
        efficiency = {
            "efficiency_ratio": 1.0,
            "misrouted": [],
            "actual_total": 1.0,
            "optimal_total": 1.0,
        }
        rows = [{"session": 1}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "No misrouted" in result

    def test_savings_metric_shown(self):
        efficiency = {
            "efficiency_ratio": 1.10,
            "misrouted": [],
            "actual_total": 1.10,
            "optimal_total": 1.00,
        }
        rows = [{"session": 1}]
        result = cd.build_routing_efficiency_section(rows, efficiency)
        assert "savings" in result.lower() or "optimal" in result.lower()


# ---------------------------------------------------------------------------
# build_recommendations_section
# ---------------------------------------------------------------------------

class TestBuildRecommendationsSection:
    def test_empty_rows_returns_no_data_message(self):
        result = cd.build_recommendations_section([])
        assert "No data" in result

    def test_opus_doc_session_generates_recommendation(self):
        rows = [{"tier": "opus", "session_type": "documentation", "cost": 0.5, "tasks": 2}]
        result = cd.build_recommendations_section(rows)
        assert "Opus → Sonnet" in result

    def test_haiku_feature_session_generates_recommendation(self):
        rows = [{"tier": "haiku", "session_type": "feature", "cost": 0.02, "tasks": 3}]
        result = cd.build_recommendations_section(rows)
        assert "Haiku → Sonnet" in result

    def test_non_opus_security_generates_recommendation(self):
        rows = [{"tier": "sonnet", "session_type": "security", "cost": 0.1, "tasks": 1}]
        result = cd.build_recommendations_section(rows)
        assert "Opus for Security" in result

    def test_general_routing_guidelines_always_present(self):
        rows = [{"tier": "sonnet", "session_type": "feature", "cost": 0.1, "tasks": 3}]
        result = cd.build_recommendations_section(rows)
        assert "General Routing Guidelines" in result

    def test_low_haiku_usage_warning_with_five_sessions(self):
        # 5 sessions, all sonnet → 0% haiku should trigger warning
        rows = [
            {"tier": "sonnet", "session_type": "feature", "cost": 0.1, "tasks": 3}
        ] * 5
        result = cd.build_recommendations_section(rows)
        assert "Haiku" in result

    def test_high_opus_usage_warning(self):
        # 2 opus + 1 sonnet → 66% opus > 40% threshold
        rows = [
            {"tier": "opus", "session_type": "security", "cost": 0.5, "tasks": 1},
            {"tier": "opus", "session_type": "security", "cost": 0.5, "tasks": 1},
            {"tier": "sonnet", "session_type": "feature", "cost": 0.1, "tasks": 3},
        ]
        result = cd.build_recommendations_section(rows)
        assert "Opus" in result

    def test_correctly_routed_sessions_no_specific_recommendations(self):
        rows = [{"tier": "sonnet", "session_type": "feature", "cost": 0.1, "tasks": 3}]
        result = cd.build_recommendations_section(rows)
        # No upgrade/downgrade recommendations but guidelines still shown
        assert "General Routing Guidelines" in result


# ---------------------------------------------------------------------------
# generate_cost_dashboard (integration)
# ---------------------------------------------------------------------------

class TestGenerateCostDashboard:
    def test_empty_repo_generates_dashboard(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "# Cost Dashboard" in result

    def test_dashboard_contains_summary_section(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "Summary" in result

    def test_dashboard_contains_model_section(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "Cost by Model" in result

    def test_dashboard_contains_session_type_section(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "Session Type" in result

    def test_dashboard_contains_time_period_section(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "Time Period" in result

    def test_dashboard_contains_routing_section(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "Routing Efficiency" in result

    def test_dashboard_contains_recommendations_section(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "Recommendations" in result

    def test_dashboard_with_data_includes_dollar_figures(self, tmp_path):
        (tmp_path / "COST_LOG.md").write_text(SAMPLE_COST_LOG, encoding="utf-8")
        result = cd.generate_cost_dashboard(tmp_path)
        assert "$" in result

    def test_generated_string_is_non_empty(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert len(result) > 100

    def test_repo_name_appears_in_header(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert tmp_path.name in result

    def test_generated_header_is_present(self, tmp_path):
        result = cd.generate_cost_dashboard(tmp_path)
        assert "auto-generated" in result.lower() or "Generated" in result


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    def test_parser_has_repo_path_argument(self):
        parser = cd.build_parser()
        args = parser.parse_args(["--repo-path", "/tmp"])
        assert str(args.repo_path) == "/tmp"

    def test_default_output_is_cost_dashboard(self):
        parser = cd.build_parser()
        args = parser.parse_args([])
        assert args.output == "COST_DASHBOARD.md"

    def test_stdout_flag_defaults_false(self):
        parser = cd.build_parser()
        args = parser.parse_args([])
        assert args.stdout is False

    def test_stdout_flag_set_true(self):
        parser = cd.build_parser()
        args = parser.parse_args(["--stdout"])
        assert args.stdout is True

    def test_custom_output_filename(self):
        parser = cd.build_parser()
        args = parser.parse_args(["--output", "MY_COSTS.md"])
        assert args.output == "MY_COSTS.md"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

class TestMain:
    def test_stdout_mode_returns_zero(self, tmp_path):
        with patch("sys.argv", ["cost_dashboard.py", "--repo-path", str(tmp_path), "--stdout"]):
            code = cd.main()
        assert code == 0

    def test_writes_file_and_returns_zero(self, tmp_path):
        with patch("sys.argv", ["cost_dashboard.py", "--repo-path", str(tmp_path)]):
            code = cd.main()
        assert code == 0
        assert (tmp_path / "COST_DASHBOARD.md").is_file()

    def test_invalid_repo_path_returns_one(self, tmp_path):
        nonexistent = str(tmp_path / "no_such_dir")
        with patch("sys.argv", ["cost_dashboard.py", "--repo-path", nonexistent]):
            code = cd.main()
        assert code == 1

    def test_custom_output_filename_used(self, tmp_path):
        with patch("sys.argv", [
            "cost_dashboard.py",
            "--repo-path", str(tmp_path),
            "--output", "MY_COSTS.md",
        ]):
            code = cd.main()
        assert code == 0
        assert (tmp_path / "MY_COSTS.md").is_file()

    def test_generate_exception_returns_one(self, tmp_path):
        with patch("cost_dashboard.generate_cost_dashboard", side_effect=RuntimeError("fail")):
            with patch("sys.argv", ["cost_dashboard.py", "--repo-path", str(tmp_path)]):
                code = cd.main()
        assert code == 1

    def test_stdout_mode_prints_header(self, tmp_path, capsys):
        with patch("sys.argv", ["cost_dashboard.py", "--repo-path", str(tmp_path), "--stdout"]):
            cd.main()
        output = capsys.readouterr().out
        assert "# Cost Dashboard" in output
