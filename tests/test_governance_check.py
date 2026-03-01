"""Integration tests for CI/CD governance logic.

Tests the business logic expressed in .github/workflows/governance-check.yml
and the scripts it invokes — without executing GitHub Actions itself.
"""

from pathlib import Path

import pytest

import health_score_calculator as hsc
import adr_coverage_checker as acc


REPO_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


class TestGovernanceCheckWorkflowExists:
    def test_governance_check_workflow_file_exists(self):
        assert (WORKFLOWS_DIR / "governance-check.yml").is_file()

    def test_ai_pr_review_workflow_exists(self):
        assert (WORKFLOWS_DIR / "ai-pr-review.yml").is_file()

    def test_workflows_dir_has_at_least_two_workflows(self):
        yml_files = list(WORKFLOWS_DIR.glob("*.yml"))
        assert len(yml_files) >= 2


class TestGovernanceCheckWorkflowContent:
    @pytest.fixture(autouse=True)
    def workflow_content(self):
        path = WORKFLOWS_DIR / "governance-check.yml"
        self._content = path.read_text(encoding="utf-8")

    def test_workflow_triggers_on_pull_request(self):
        assert "pull_request" in self._content

    def test_workflow_references_python_script_or_action(self):
        has_script = (
            "health" in self._content.lower() or "check" in self._content.lower()
        )
        assert has_script


class TestHealthGateLogic:
    """Verify that the health score gate behaves correctly for border cases."""

    def test_score_just_below_threshold_fails_gate(self, tmp_path):
        # Build a repo that scores exactly 10 (only CLAUDE.md)
        (tmp_path / "CLAUDE.md").write_text(
            "# CLAUDE.md\n\nProject.\n", encoding="utf-8"
        )
        report = hsc.calculate_score(tmp_path)
        # With threshold=20 this should fail
        fails = report["score"] < 20
        assert fails  # A repo with only CLAUDE.md won't reach Level 1

    def test_full_repo_passes_level_three_threshold(self, full_repo):
        report = hsc.calculate_score(full_repo)
        assert report["score"] >= 60, "Full fixture should reach Level 3"

    def test_threshold_exit_code_zero_when_met(self, full_repo):
        assert hsc.run(full_repo, threshold=40) == 0

    def test_threshold_exit_code_one_when_not_met(self, empty_repo):
        assert hsc.run(empty_repo, threshold=40) == 1


class TestAdrGateLogic:
    def test_empty_repo_passes_adr_gate(self, tmp_path):
        # No DECISIONS.md and no ADRs — gate passes vacuously
        code = acc.run(tmp_path, threshold="strict", output_format="json")
        assert code == 0

    def test_warn_mode_always_exits_zero(self, tmp_path):
        (tmp_path / "DECISIONS.md").write_text(
            "## DEC-001 -- Some choice -- 2025-01-01\n\nWe chose X.\n",
            encoding="utf-8",
        )
        code = acc.run(tmp_path, threshold="warn", output_format="json")
        assert code == 0
