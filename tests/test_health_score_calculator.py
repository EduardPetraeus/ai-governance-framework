"""Tests for automation/health_score_calculator.py.

Covers: maturity level mapping, individual scoring components,
checklist completion percentage calculation, output formats,
disclaimer inclusion, and exit-code threshold logic.
"""

import json
from pathlib import Path


import health_score_calculator as hsc


# ---------------------------------------------------------------------------
# get_maturity_level
# ---------------------------------------------------------------------------


class TestGetMaturityLevel:
    def test_score_0_is_adhoc(self):
        level, label = hsc.get_maturity_level(0)
        assert level == 0
        assert label == "Ad-hoc"

    def test_score_19_is_still_adhoc(self):
        level, label = hsc.get_maturity_level(19)
        assert level == 0

    def test_score_20_is_foundation(self):
        level, label = hsc.get_maturity_level(20)
        assert level == 1
        assert label == "Foundation"

    def test_score_40_is_structured(self):
        level, label = hsc.get_maturity_level(40)
        assert level == 2
        assert label == "Structured"

    def test_score_60_is_enforced(self):
        level, label = hsc.get_maturity_level(60)
        assert level == 3
        assert label == "Enforced"

    def test_score_80_is_measured(self):
        level, label = hsc.get_maturity_level(80)
        assert level == 4
        assert label == "Measured"

    def test_score_95_is_self_optimizing(self):
        level, label = hsc.get_maturity_level(95)
        assert level == 5
        assert label == "Self-optimizing"

    def test_score_100_is_self_optimizing(self):
        level, label = hsc.get_maturity_level(100)
        assert level == 5

    def test_score_110_is_self_optimizing(self):
        level, label = hsc.get_maturity_level(110)
        assert level == 5
        assert label == "Self-optimizing"


# ---------------------------------------------------------------------------
# check_file_exists
# ---------------------------------------------------------------------------


class TestCheckFileExists:
    def test_existing_file_returns_true(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("content", encoding="utf-8")
        assert hsc.check_file_exists(tmp_path, "CLAUDE.md") is True

    def test_missing_file_returns_false(self, tmp_path):
        assert hsc.check_file_exists(tmp_path, "MISSING.md") is False


# ---------------------------------------------------------------------------
# check_dir_has_files
# ---------------------------------------------------------------------------


class TestCheckDirHasFiles:
    def test_dir_with_file_returns_true(self, tmp_path):
        sub = tmp_path / "agents"
        sub.mkdir()
        (sub / "agent.md").write_text("# Agent\n", encoding="utf-8")
        assert hsc.check_dir_has_files(tmp_path, "agents") is True

    def test_missing_dir_returns_false(self, tmp_path):
        assert hsc.check_dir_has_files(tmp_path, "nonexistent") is False

    def test_empty_dir_returns_false(self, tmp_path):
        (tmp_path / "empty").mkdir()
        assert hsc.check_dir_has_files(tmp_path, "empty") is False


# ---------------------------------------------------------------------------
# check_claude_sections
# ---------------------------------------------------------------------------


class TestCheckClaudeSections:
    def test_all_required_sections_found(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text(
            "## project_context\n\ntext\n\n"
            "## conventions\n\ntext\n\n"
            "## mandatory_session_protocol\n\ntext\n\n"
            "## security_protocol\n\ntext\n\n"
            "## mandatory_task_reporting\n\ntext\n",
            encoding="utf-8",
        )
        found = hsc.check_claude_sections(tmp_path)
        assert len(found) == 5

    def test_no_claude_md_returns_empty(self, tmp_path):
        assert hsc.check_claude_sections(tmp_path) == []

    def test_partial_sections_detected(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text(
            "## project_context\n\ntext\n", encoding="utf-8"
        )
        found = hsc.check_claude_sections(tmp_path)
        assert "project_context" in found
        assert "conventions" not in found


# ---------------------------------------------------------------------------
# count_changelog_entries
# ---------------------------------------------------------------------------


class TestCountChangelogEntries:
    def test_three_h2_entries(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(
            "# CHANGELOG\n\n## Entry 1\n\n## Entry 2\n\n## Entry 3\n",
            encoding="utf-8",
        )
        assert hsc.count_changelog_entries(tmp_path) == 3

    def test_missing_changelog_returns_zero(self, tmp_path):
        assert hsc.count_changelog_entries(tmp_path) == 0

    def test_changelog_with_no_entries_returns_zero(self, tmp_path):
        (tmp_path / "CHANGELOG.md").write_text(
            "# CHANGELOG\n\nNo entries yet.\n", encoding="utf-8"
        )
        assert hsc.count_changelog_entries(tmp_path) == 0


# ---------------------------------------------------------------------------
# check_ai_review_workflow
# ---------------------------------------------------------------------------


class TestCheckAiReviewWorkflow:
    def test_workflow_referencing_anthropic_passes(self, tmp_path):
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "review.yml").write_text(
            "steps:\n  - run: echo anthropic\n", encoding="utf-8"
        )
        assert hsc.check_ai_review_workflow(tmp_path) is True

    def test_workflow_referencing_claude_passes(self, tmp_path):
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "review.yml").write_text("uses: claude-action@v1\n", encoding="utf-8")
        assert hsc.check_ai_review_workflow(tmp_path) is True

    def test_plain_ci_workflow_fails(self, tmp_path):
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("steps:\n  - run: pytest\n", encoding="utf-8")
        assert hsc.check_ai_review_workflow(tmp_path) is False

    def test_no_workflows_dir_fails(self, tmp_path):
        assert hsc.check_ai_review_workflow(tmp_path) is False


# ---------------------------------------------------------------------------
# check_gitignore_has_env
# ---------------------------------------------------------------------------


class TestCheckGitignoreHasEnv:
    def test_gitignore_with_dotenv_passes(self, tmp_path):
        (tmp_path / ".gitignore").write_text(".env\n*.pyc\n", encoding="utf-8")
        assert hsc.check_gitignore_has_env(tmp_path) is True

    def test_gitignore_with_dotenv_star_passes(self, tmp_path):
        (tmp_path / ".gitignore").write_text(".env*\n", encoding="utf-8")
        assert hsc.check_gitignore_has_env(tmp_path) is True

    def test_gitignore_without_env_fails(self, tmp_path):
        (tmp_path / ".gitignore").write_text("*.pyc\n__pycache__/\n", encoding="utf-8")
        assert hsc.check_gitignore_has_env(tmp_path) is False

    def test_missing_gitignore_fails(self, tmp_path):
        assert hsc.check_gitignore_has_env(tmp_path) is False


# ---------------------------------------------------------------------------
# calculate_score (integration)
# ---------------------------------------------------------------------------


class TestCalculateScore:
    def test_empty_repo_score_is_zero_percent(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        assert report["score"] == 0

    def test_full_repo_score_is_100_percent(self, full_repo):
        report = hsc.calculate_score(full_repo)
        assert report["score"] == 100

    def test_report_contains_required_keys(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        for key in (
            "score",
            "raw_score",
            "max_score",
            "level",
            "level_label",
            "checks",
            "date",
            "disclaimer",
        ):
            assert key in report

    def test_max_score_equals_sum_of_check_points(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        expected = sum(c["points"] for c in report["checks"])
        assert report["max_score"] == expected

    def test_minimal_repo_earns_claude_points_as_percentage(self, minimal_repo):
        report = hsc.calculate_score(minimal_repo)
        assert report["score"] == round(10 / 110 * 100)
        assert report["raw_score"] == 10

    def test_checks_list_is_nonempty(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        assert len(report["checks"]) > 0

    def test_score_is_percentage_of_raw_over_max(self, full_repo):
        report = hsc.calculate_score(full_repo)
        expected = round(report["raw_score"] / report["max_score"] * 100)
        assert report["score"] == expected


# ---------------------------------------------------------------------------
# format_json / format_text
# ---------------------------------------------------------------------------


class TestOutputFormats:
    def test_json_output_is_parseable(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        parsed = json.loads(hsc.format_json(report))
        assert "score" in parsed

    def test_json_output_checks_is_list(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        parsed = json.loads(hsc.format_json(report))
        assert isinstance(parsed["checks"], list)

    def test_json_output_contains_disclaimer(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        parsed = json.loads(hsc.format_json(report))
        assert "disclaimer" in parsed
        assert "checklist completion" in parsed["disclaimer"].lower()

    def test_text_output_contains_score_label(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        assert "Score:" in hsc.format_text(report)

    def test_text_output_contains_percentage(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        assert "%" in hsc.format_text(report)

    def test_text_output_contains_level(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        assert "Level" in hsc.format_text(report)

    def test_text_output_contains_disclaimer(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        text = hsc.format_text(report)
        assert hsc.SCORE_DISCLAIMER in text

    def test_text_header_says_checklist_completion(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        text = hsc.format_text(report)
        assert "Governance Checklist Completion" in text


# ---------------------------------------------------------------------------
# v0.3.0 additions: AGENTS.md + self-validation checklist
# ---------------------------------------------------------------------------


class TestV030Additions:
    def test_agents_md_check_passes_when_present(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text(
            "# AGENTS\n\nCross-tool bridge.\n", encoding="utf-8"
        )
        assert hsc.check_agents_md(tmp_path) is True

    def test_agents_md_check_fails_when_absent(self, tmp_path):
        assert hsc.check_agents_md(tmp_path) is False

    def test_self_validation_checklist_passes_when_present(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "self-validation-checklist.md").write_text(
            "# Self-Validation Checklist\n\n## 1. Constitution Health\n",
            encoding="utf-8",
        )
        assert hsc.check_self_validation_checklist(tmp_path) is True

    def test_self_validation_checklist_fails_when_absent(self, tmp_path):
        assert hsc.check_self_validation_checklist(tmp_path) is False

    def test_calculate_score_includes_agents_md_check(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
        report = hsc.calculate_score(tmp_path)
        agents_check = next(c for c in report["checks"] if "AGENTS.md" in c["name"])
        assert agents_check["passed"] is True
        assert agents_check["points"] == 5

    def test_calculate_score_includes_checklist_check(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "self-validation-checklist.md").write_text(
            "# Self-Validation Checklist\n", encoding="utf-8"
        )
        report = hsc.calculate_score(tmp_path)
        checklist_check = next(
            c for c in report["checks"] if "self-validation" in c["name"].lower()
        )
        assert checklist_check["passed"] is True
        assert checklist_check["points"] == 5

    def test_max_score_is_110_raw_points(self, empty_repo):
        report = hsc.calculate_score(empty_repo)
        assert report["max_score"] == 110


# ---------------------------------------------------------------------------
# run (exit codes and file output)
# ---------------------------------------------------------------------------


class TestRun:
    def test_run_returns_zero_by_default(self, empty_repo):
        assert hsc.run(empty_repo) == 0

    def test_run_returns_one_when_threshold_not_met(self, empty_repo):
        assert hsc.run(empty_repo, threshold=50) == 1

    def test_run_returns_zero_when_threshold_met(self, full_repo):
        assert hsc.run(full_repo, threshold=50) == 0

    def test_run_returns_one_for_invalid_path(self, tmp_path):
        assert hsc.run(tmp_path / "nonexistent") == 1

    def test_run_json_format_exits_cleanly(self, empty_repo, capsys):
        exit_code = hsc.run(empty_repo, output_format="json")
        assert exit_code == 0
        output = capsys.readouterr().out
        parsed = json.loads(output)
        assert "score" in parsed

    def test_run_writes_report_to_file(self, empty_repo, tmp_path):
        out = str(tmp_path / "report.json")
        exit_code = hsc.run(empty_repo, output_format="json", output_file=out)
        assert exit_code == 0
        assert Path(out).is_file()
