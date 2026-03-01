"""Tests for automation/output_contract_validator.py.

Covers: field validation, type checking, confidence ceiling, cross-field
constraints, output formats, and exit-code logic.
"""

import json

import pytest

import output_contract_validator as ocv


VALID_CONTRACT = {
    "status": "PASS",
    "session": "042",
    "date": "2026-03-01",
    "model": "claude-sonnet-4-6",
    "files_changed": [
        {"path": "src/auth/oauth.py", "operation": "modified"},
    ],
    "confidence": 78,
    "not_verified": ["Rate limit behavior under sustained load"],
    "architectural_impact": "none",
    "requires_review": False,
    "requires_review_reason": None,
}


def make_contract(**overrides):
    """Return a valid contract dict with the given fields overridden."""
    contract = dict(VALID_CONTRACT)
    contract.update(overrides)
    return contract


# ---------------------------------------------------------------------------
# validate_contract — valid input
# ---------------------------------------------------------------------------


class TestValidContract:
    def test_valid_pass_contract(self):
        errors = ocv.validate_contract(VALID_CONTRACT)
        assert errors == []

    def test_valid_warn_contract(self):
        contract = make_contract(status="WARN", confidence=60)
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_valid_fail_contract(self):
        contract = make_contract(status="FAIL", confidence=30)
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_empty_files_changed_is_valid(self):
        contract = make_contract(files_changed=[])
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_empty_not_verified_is_valid(self):
        contract = make_contract(not_verified=[])
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_requires_review_true_with_reason(self):
        contract = make_contract(
            requires_review=True, requires_review_reason="Auth changes"
        )
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_high_architectural_impact(self):
        contract = make_contract(
            architectural_impact="high",
            requires_review=True,
            requires_review_reason="Major arch change",
        )
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_confidence_at_ceiling(self):
        contract = make_contract(confidence=85)
        errors = ocv.validate_contract(contract, confidence_ceiling=85)
        assert errors == []

    def test_confidence_below_ceiling(self):
        contract = make_contract(confidence=70)
        errors = ocv.validate_contract(contract, confidence_ceiling=85)
        assert errors == []

    def test_confidence_zero_is_valid(self):
        contract = make_contract(confidence=0)
        errors = ocv.validate_contract(contract)
        assert errors == []

    def test_multiple_files_changed(self):
        contract = make_contract(
            files_changed=[
                {"path": "src/a.py", "operation": "created"},
                {"path": "src/b.py", "operation": "modified"},
                {"path": "src/c.py", "operation": "deleted"},
            ]
        )
        errors = ocv.validate_contract(contract)
        assert errors == []


# ---------------------------------------------------------------------------
# validate_contract — status field
# ---------------------------------------------------------------------------


class TestStatusField:
    def test_invalid_status(self):
        contract = make_contract(status="OK")
        errors = ocv.validate_contract(contract)
        assert any("status" in e for e in errors)

    def test_lowercase_status_rejected(self):
        contract = make_contract(status="pass")
        errors = ocv.validate_contract(contract)
        assert any("status" in e for e in errors)

    def test_empty_status_rejected(self):
        contract = make_contract(status="")
        errors = ocv.validate_contract(contract)
        assert any("status" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — required fields
# ---------------------------------------------------------------------------


class TestRequiredFields:
    @pytest.mark.parametrize("field", ocv.REQUIRED_FIELDS)
    def test_missing_required_field(self, field):
        contract = dict(VALID_CONTRACT)
        del contract[field]
        errors = ocv.validate_contract(contract)
        assert any(field in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — unknown fields
# ---------------------------------------------------------------------------


class TestUnknownFields:
    def test_unknown_top_level_field_rejected(self):
        contract = make_contract(extra_field="unexpected")
        errors = ocv.validate_contract(contract)
        assert any("extra_field" in e for e in errors)

    def test_two_unknown_fields_both_reported(self):
        contract = make_contract(foo="bar", baz=42)
        errors = ocv.validate_contract(contract)
        assert any("foo" in e for e in errors)
        assert any("baz" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — date field
# ---------------------------------------------------------------------------


class TestDateField:
    def test_invalid_date_format_rejected(self):
        contract = make_contract(date="01-03-2026")
        errors = ocv.validate_contract(contract)
        assert any("date" in e for e in errors)

    def test_date_with_time_rejected(self):
        contract = make_contract(date="2026-03-01T12:00:00")
        errors = ocv.validate_contract(contract)
        assert any("date" in e for e in errors)

    def test_non_string_date_rejected(self):
        contract = make_contract(date=20260301)
        errors = ocv.validate_contract(contract)
        assert any("date" in e for e in errors)

    def test_valid_date_no_error(self):
        contract = make_contract(date="2026-03-01")
        errors = ocv.validate_contract(contract)
        assert not any("date" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — session and model fields
# ---------------------------------------------------------------------------


class TestSessionField:
    def test_empty_session_rejected(self):
        contract = make_contract(session="")
        errors = ocv.validate_contract(contract)
        assert any("session" in e for e in errors)

    def test_whitespace_only_session_rejected(self):
        contract = make_contract(session="   ")
        errors = ocv.validate_contract(contract)
        assert any("session" in e for e in errors)

    def test_non_string_session_rejected(self):
        contract = make_contract(session=42)
        errors = ocv.validate_contract(contract)
        assert any("session" in e for e in errors)


class TestModelField:
    def test_empty_model_rejected(self):
        contract = make_contract(model="")
        errors = ocv.validate_contract(contract)
        assert any("model" in e for e in errors)

    def test_non_string_model_rejected(self):
        contract = make_contract(model=None)
        errors = ocv.validate_contract(contract)
        assert any("model" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — confidence field
# ---------------------------------------------------------------------------


class TestConfidenceField:
    def test_confidence_above_ceiling_rejected(self):
        contract = make_contract(confidence=90)
        errors = ocv.validate_contract(contract, confidence_ceiling=85)
        assert any("ceiling" in e for e in errors)

    def test_confidence_above_default_ceiling_rejected(self):
        contract = make_contract(confidence=86)
        errors = ocv.validate_contract(contract)
        assert any("ceiling" in e for e in errors)

    def test_confidence_above_100_rejected(self):
        contract = make_contract(confidence=101)
        errors = ocv.validate_contract(contract)
        assert any("100" in e for e in errors)

    def test_confidence_below_0_rejected(self):
        contract = make_contract(confidence=-1)
        errors = ocv.validate_contract(contract)
        assert any("0" in e for e in errors)

    def test_confidence_as_float_rejected(self):
        contract = make_contract(confidence=78.5)
        errors = ocv.validate_contract(contract)
        assert any("confidence" in e for e in errors)

    def test_confidence_as_bool_rejected(self):
        contract = make_contract(confidence=True)
        errors = ocv.validate_contract(contract)
        assert any("confidence" in e for e in errors)

    def test_confidence_as_false_bool_rejected(self):
        contract = make_contract(confidence=False)
        errors = ocv.validate_contract(contract)
        assert any("confidence" in e for e in errors)

    def test_custom_ceiling_higher_allows_higher_value(self):
        contract = make_contract(confidence=90)
        errors = ocv.validate_contract(contract, confidence_ceiling=95)
        assert not any("ceiling" in e for e in errors)

    def test_custom_ceiling_lower_rejects_value(self):
        contract = make_contract(confidence=70)
        errors = ocv.validate_contract(contract, confidence_ceiling=65)
        assert any("ceiling" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — files_changed field
# ---------------------------------------------------------------------------


class TestFilesChangedField:
    def test_invalid_operation_rejected(self):
        contract = make_contract(
            files_changed=[{"path": "src/foo.py", "operation": "updated"}]
        )
        errors = ocv.validate_contract(contract)
        assert any("operation" in e for e in errors)

    def test_missing_path_rejected(self):
        contract = make_contract(files_changed=[{"operation": "created"}])
        errors = ocv.validate_contract(contract)
        assert any("path" in e for e in errors)

    def test_missing_operation_rejected(self):
        contract = make_contract(files_changed=[{"path": "src/foo.py"}])
        errors = ocv.validate_contract(contract)
        assert any("operation" in e for e in errors)

    def test_unknown_key_in_file_entry_rejected(self):
        contract = make_contract(
            files_changed=[
                {"path": "src/foo.py", "operation": "created", "extra": "value"}
            ]
        )
        errors = ocv.validate_contract(contract)
        assert any("extra" in e for e in errors)

    def test_files_changed_not_list_rejected(self):
        contract = make_contract(files_changed="src/foo.py")
        errors = ocv.validate_contract(contract)
        assert any("files_changed" in e for e in errors)

    def test_file_entry_not_dict_rejected(self):
        contract = make_contract(files_changed=["src/foo.py"])
        errors = ocv.validate_contract(contract)
        assert any("files_changed[0]" in e for e in errors)

    def test_empty_path_rejected(self):
        contract = make_contract(files_changed=[{"path": "", "operation": "created"}])
        errors = ocv.validate_contract(contract)
        assert any("path" in e for e in errors)

    @pytest.mark.parametrize("op", sorted(ocv.VALID_OPERATIONS))
    def test_all_valid_operations_accepted(self, op):
        contract = make_contract(
            files_changed=[{"path": "src/foo.py", "operation": op}]
        )
        errors = ocv.validate_contract(contract)
        assert not any("operation" in e for e in errors), (
            f"Operation {op!r} should be valid"
        )


# ---------------------------------------------------------------------------
# validate_contract — not_verified field
# ---------------------------------------------------------------------------


class TestNotVerifiedField:
    def test_not_verified_not_list_rejected(self):
        contract = make_contract(not_verified="nothing")
        errors = ocv.validate_contract(contract)
        assert any("not_verified" in e for e in errors)

    def test_not_verified_item_empty_string_rejected(self):
        contract = make_contract(not_verified=[""])
        errors = ocv.validate_contract(contract)
        assert any("not_verified[0]" in e for e in errors)

    def test_not_verified_item_whitespace_rejected(self):
        contract = make_contract(not_verified=["   "])
        errors = ocv.validate_contract(contract)
        assert any("not_verified[0]" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — architectural_impact field
# ---------------------------------------------------------------------------


class TestArchitecturalImpactField:
    def test_invalid_impact_rejected(self):
        contract = make_contract(architectural_impact="critical")
        errors = ocv.validate_contract(contract)
        assert any("architectural_impact" in e for e in errors)

    @pytest.mark.parametrize("impact", sorted(ocv.VALID_ARCHITECTURAL_IMPACTS))
    def test_all_valid_impacts_accepted(self, impact):
        contract = make_contract(architectural_impact=impact)
        if impact == "high":
            contract = make_contract(
                architectural_impact=impact,
                requires_review=True,
                requires_review_reason="Significant change",
            )
        errors = ocv.validate_contract(contract)
        assert not any("architectural_impact" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — requires_review cross-validation
# ---------------------------------------------------------------------------


class TestRequiresReviewCrossValidation:
    def test_requires_review_true_without_reason_rejected(self):
        contract = make_contract(requires_review=True, requires_review_reason=None)
        errors = ocv.validate_contract(contract)
        assert any("requires_review_reason" in e for e in errors)

    def test_requires_review_true_empty_reason_rejected(self):
        contract = make_contract(requires_review=True, requires_review_reason="")
        errors = ocv.validate_contract(contract)
        assert any("requires_review_reason" in e for e in errors)

    def test_requires_review_false_with_reason_rejected(self):
        contract = make_contract(
            requires_review=False, requires_review_reason="Some reason"
        )
        errors = ocv.validate_contract(contract)
        assert any("requires_review_reason" in e for e in errors)

    def test_requires_review_not_bool_rejected(self):
        contract = make_contract(requires_review="yes")
        errors = ocv.validate_contract(contract)
        assert any("requires_review" in e for e in errors)

    def test_requires_review_false_null_reason_valid(self):
        contract = make_contract(requires_review=False, requires_review_reason=None)
        errors = ocv.validate_contract(contract)
        assert not any("requires_review" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_contract — non-dict input
# ---------------------------------------------------------------------------


class TestNonDictInput:
    def test_list_input_rejected(self):
        errors = ocv.validate_contract([])
        assert len(errors) == 1
        assert "dict" in errors[0]

    def test_string_input_rejected(self):
        errors = ocv.validate_contract("not a dict")
        assert len(errors) == 1
        assert "dict" in errors[0]

    def test_none_input_rejected(self):
        errors = ocv.validate_contract(None)
        assert len(errors) == 1
        assert "dict" in errors[0]

    def test_int_input_rejected(self):
        errors = ocv.validate_contract(42)
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# format_text_report
# ---------------------------------------------------------------------------


class TestFormatTextReport:
    def test_pass_result_in_output(self):
        output = ocv.format_text_report("output_contract.json", VALID_CONTRACT, [], 85)
        assert "RESULT: PASS" in output

    def test_fail_result_in_output(self):
        errors = ["confidence exceeds ceiling"]
        output = ocv.format_text_report(
            "output_contract.json", VALID_CONTRACT, errors, 85
        )
        assert "RESULT: FAIL" in output
        assert "1 error" in output

    def test_multiple_errors_plural(self):
        errors = ["error 1", "error 2"]
        output = ocv.format_text_report(
            "output_contract.json", VALID_CONTRACT, errors, 85
        )
        assert "2 errors" in output

    def test_single_error_singular(self):
        errors = ["one error"]
        output = ocv.format_text_report(
            "output_contract.json", VALID_CONTRACT, errors, 85
        )
        assert "1 error" in output
        assert "1 errors" not in output

    def test_ceiling_ok_note_present(self):
        contract = make_contract(confidence=75)
        output = ocv.format_text_report("f.json", contract, [], 85)
        assert "OK" in output

    def test_ceiling_exceeds_note_present(self):
        contract = make_contract(confidence=92)
        errors = ["confidence exceeds ceiling"]
        output = ocv.format_text_report("f.json", contract, errors, 85)
        assert "EXCEEDS CEILING" in output

    def test_contract_path_in_header(self):
        output = ocv.format_text_report("my/contract.json", VALID_CONTRACT, [], 85)
        assert "my/contract.json" in output

    def test_status_shown_in_report(self):
        output = ocv.format_text_report("f.json", VALID_CONTRACT, [], 85)
        assert "PASS" in output

    def test_files_count_shown(self):
        output = ocv.format_text_report("f.json", VALID_CONTRACT, [], 85)
        assert "1 files" in output


# ---------------------------------------------------------------------------
# format_json_report
# ---------------------------------------------------------------------------


class TestFormatJsonReport:
    def test_pass_json_report(self):
        output = ocv.format_json_report("output_contract.json", [], 85)
        parsed = json.loads(output)
        assert parsed["passed"] is True
        assert parsed["error_count"] == 0
        assert parsed["errors"] == []

    def test_fail_json_report(self):
        errors = ["missing field: status"]
        output = ocv.format_json_report("output_contract.json", errors, 85)
        parsed = json.loads(output)
        assert parsed["passed"] is False
        assert parsed["error_count"] == 1
        assert parsed["errors"] == errors

    def test_confidence_ceiling_in_json_report(self):
        output = ocv.format_json_report("f.json", [], 90)
        parsed = json.loads(output)
        assert parsed["confidence_ceiling"] == 90

    def test_contract_path_in_json_report(self):
        output = ocv.format_json_report("my/contract.json", [], 85)
        parsed = json.loads(output)
        assert parsed["contract"] == "my/contract.json"


# ---------------------------------------------------------------------------
# run — file I/O and exit codes
# ---------------------------------------------------------------------------


class TestRun:
    def test_valid_contract_returns_0(self, tmp_path):
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(VALID_CONTRACT), encoding="utf-8")
        assert ocv.run(f) == 0

    def test_invalid_confidence_returns_1(self, tmp_path):
        contract = make_contract(confidence=99)
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(contract), encoding="utf-8")
        assert ocv.run(f) == 1

    def test_missing_file_returns_1(self, tmp_path):
        assert ocv.run(tmp_path / "nonexistent.json") == 1

    def test_invalid_json_returns_1(self, tmp_path):
        f = tmp_path / "output_contract.json"
        f.write_text("not valid json { }", encoding="utf-8")
        assert ocv.run(f) == 1

    def test_json_format_pass(self, tmp_path, capsys):
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(VALID_CONTRACT), encoding="utf-8")
        exit_code = ocv.run(f, output_format="json")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["passed"] is True
        assert exit_code == 0

    def test_json_format_fail(self, tmp_path, capsys):
        contract = make_contract(confidence=99)
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(contract), encoding="utf-8")
        exit_code = ocv.run(f, output_format="json")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["passed"] is False
        assert exit_code == 1

    def test_custom_ceiling_fail(self, tmp_path):
        contract = make_contract(confidence=90)
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(contract), encoding="utf-8")
        assert ocv.run(f, confidence_ceiling=85) == 1

    def test_custom_ceiling_pass(self, tmp_path):
        contract = make_contract(confidence=90)
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(contract), encoding="utf-8")
        assert ocv.run(f, confidence_ceiling=95) == 0

    def test_missing_required_field_returns_1(self, tmp_path):
        contract = dict(VALID_CONTRACT)
        del contract["not_verified"]
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(contract), encoding="utf-8")
        assert ocv.run(f) == 1

    def test_text_output_contains_result(self, tmp_path, capsys):
        f = tmp_path / "output_contract.json"
        f.write_text(json.dumps(VALID_CONTRACT), encoding="utf-8")
        ocv.run(f, output_format="text")
        captured = capsys.readouterr()
        assert "RESULT: PASS" in captured.out


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    def test_parser_created(self):
        parser = ocv.build_parser()
        assert parser is not None

    def test_parser_default_ceiling(self):
        parser = ocv.build_parser()
        args = parser.parse_args(["output_contract.json"])
        assert args.confidence_ceiling == ocv.DEFAULT_CONFIDENCE_CEILING

    def test_parser_custom_ceiling(self):
        parser = ocv.build_parser()
        args = parser.parse_args(["output_contract.json", "--confidence-ceiling", "90"])
        assert args.confidence_ceiling == 90

    def test_parser_json_format(self):
        parser = ocv.build_parser()
        args = parser.parse_args(["output_contract.json", "--format", "json"])
        assert args.output_format == "json"

    def test_parser_default_format(self):
        parser = ocv.build_parser()
        args = parser.parse_args(["output_contract.json"])
        assert args.output_format == "text"
