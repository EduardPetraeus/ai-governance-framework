"""Validate an AI agent output contract JSON file against the standard schema.

The output contract is a machine-readable session artifact produced by the agent
at the end of each session. This validator checks structural correctness, field
types, required fields, and the confidence ceiling constraint.

Usage:
    python output_contract_validator.py output_contract.json
    python output_contract_validator.py output_contract.json --confidence-ceiling 90
    python output_contract_validator.py output_contract.json --format json

Exit code 0 = PASS, exit code 1 = FAIL.

See patterns/structured-output-contracts.md for the schema specification.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, List

DEFAULT_CONFIDENCE_CEILING = 85

VALID_STATUSES = {"PASS", "WARN", "FAIL"}
VALID_OPERATIONS = {"created", "modified", "deleted"}
VALID_ARCHITECTURAL_IMPACTS = {"none", "low", "medium", "high"}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_FIELDS = [
    "status",
    "session",
    "date",
    "model",
    "files_changed",
    "confidence",
    "not_verified",
    "architectural_impact",
    "requires_review",
    "requires_review_reason",
]


def validate_contract(
    data: Any,
    confidence_ceiling: int = DEFAULT_CONFIDENCE_CEILING,
) -> List[str]:
    """Validate the output contract data. Returns a list of error messages (empty = PASS)."""
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["Contract must be a JSON object (dict), got: " + type(data).__name__]

    # Check for unknown fields
    known_fields = set(REQUIRED_FIELDS)
    for key in data:
        if key not in known_fields:
            errors.append(f"Unknown field: {key!r}")

    # Check required fields are present
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Required field missing: {field}")

    # Return early if missing required fields — subsequent checks would fail
    if errors:
        return errors

    # status
    if data["status"] not in VALID_STATUSES:
        errors.append(
            f"status must be one of {sorted(VALID_STATUSES)!r}, got {data['status']!r}"
        )

    # session
    if not isinstance(data["session"], str) or not data["session"].strip():
        errors.append("session must be a non-empty string")

    # date
    if not isinstance(data["date"], str) or not DATE_PATTERN.match(data["date"]):
        errors.append(
            f"date must be a string in YYYY-MM-DD format, got {data['date']!r}"
        )

    # model
    if not isinstance(data["model"], str) or not data["model"].strip():
        errors.append("model must be a non-empty string")

    # files_changed
    if not isinstance(data["files_changed"], list):
        errors.append("files_changed must be an array")
    else:
        for i, entry in enumerate(data["files_changed"]):
            if not isinstance(entry, dict):
                errors.append(f"files_changed[{i}] must be an object")
                continue
            if (
                "path" not in entry
                or not isinstance(entry["path"], str)
                or not entry["path"].strip()
            ):
                errors.append(f"files_changed[{i}].path must be a non-empty string")
            if "operation" not in entry:
                errors.append(f"files_changed[{i}].operation is required")
            elif entry["operation"] not in VALID_OPERATIONS:
                errors.append(
                    f"files_changed[{i}].operation must be one of "
                    f"{sorted(VALID_OPERATIONS)!r}, got {entry['operation']!r}"
                )
            unknown_keys = set(entry) - {"path", "operation"}
            for key in sorted(unknown_keys):
                errors.append(f"files_changed[{i}] has unknown key: {key!r}")

    # confidence — must be int, not bool (bool is a subclass of int in Python)
    if isinstance(data["confidence"], bool) or not isinstance(data["confidence"], int):
        errors.append("confidence must be an integer")
    else:
        if data["confidence"] < 0 or data["confidence"] > 100:
            errors.append(
                f"confidence must be between 0 and 100, got {data['confidence']}"
            )
        elif data["confidence"] > confidence_ceiling:
            errors.append(
                f"confidence value {data['confidence']} exceeds configured ceiling "
                f"{confidence_ceiling}. Agents must not claim higher confidence than "
                f"the project ceiling. See patterns/automation-bias-defense.md."
            )

    # not_verified
    if not isinstance(data["not_verified"], list):
        errors.append("not_verified must be an array")
    else:
        for i, item in enumerate(data["not_verified"]):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"not_verified[{i}] must be a non-empty string")

    # architectural_impact
    if data["architectural_impact"] not in VALID_ARCHITECTURAL_IMPACTS:
        errors.append(
            f"architectural_impact must be one of "
            f"{sorted(VALID_ARCHITECTURAL_IMPACTS)!r}, "
            f"got {data['architectural_impact']!r}"
        )

    # requires_review
    if not isinstance(data["requires_review"], bool):
        errors.append("requires_review must be a boolean")

    # requires_review_reason cross-validation
    if isinstance(data["requires_review"], bool):
        reason = data["requires_review_reason"]
        if data["requires_review"]:
            if reason is None or not isinstance(reason, str) or not reason.strip():
                errors.append(
                    "requires_review_reason must be a non-empty string when "
                    "requires_review is true"
                )
        else:
            if reason is not None:
                errors.append(
                    "requires_review_reason must be null when requires_review is false"
                )

    return errors


def format_text_report(
    contract_path: str,
    data: Any,
    errors: List[str],
    confidence_ceiling: int,
) -> str:
    """Format a human-readable validation report."""
    header = f"Validating {contract_path}"
    lines: List[str] = [
        header,
        "=" * max(len(header), 32),
    ]

    if isinstance(data, dict):
        status = data.get("status", "(missing)")
        session = data.get("session", "(missing)")
        date = data.get("date", "(missing)")
        model = data.get("model", "(missing)")
        files_changed = data.get("files_changed")
        confidence = data.get("confidence")
        not_verified = data.get("not_verified")
        arch_impact = data.get("architectural_impact", "(missing)")
        requires_review = data.get("requires_review", "(missing)")

        fc_count = (
            len(files_changed) if isinstance(files_changed, list) else "(invalid)"
        )
        nv_count = len(not_verified) if isinstance(not_verified, list) else "(invalid)"

        conf_note = ""
        if isinstance(confidence, int) and not isinstance(confidence, bool):
            if confidence > confidence_ceiling:
                conf_note = f"  (ceiling: {confidence_ceiling})  EXCEEDS CEILING"
            else:
                conf_note = f"  (ceiling: {confidence_ceiling})  OK"

        lines += [
            f"  status               {status}",
            f"  session              {session}",
            f"  date                 {date}",
            f"  model                {model}",
            f"  files_changed        {fc_count} files",
            f"  confidence           {confidence}{conf_note}",
            f"  not_verified         {nv_count} items declared",
            f"  architectural_impact {arch_impact}",
            f"  requires_review      {str(requires_review).lower()}",
        ]

    lines.append("")

    if errors:
        for err in errors:
            lines.append(f"  FAIL: {err}")
        lines.append("")
        lines.append(
            f"RESULT: FAIL ({len(errors)} error{'s' if len(errors) != 1 else ''})"
        )
    else:
        lines.append("RESULT: PASS")

    return "\n".join(lines)


def format_json_report(
    contract_path: str,
    errors: List[str],
    confidence_ceiling: int,
) -> str:
    """Format a JSON validation report."""
    return json.dumps(
        {
            "contract": contract_path,
            "passed": len(errors) == 0,
            "confidence_ceiling": confidence_ceiling,
            "error_count": len(errors),
            "errors": errors,
        },
        indent=2,
    )


def run(
    contract_path: Path,
    confidence_ceiling: int = DEFAULT_CONFIDENCE_CEILING,
    output_format: str = "text",
) -> int:
    """Validate the contract file and return exit code (0 = PASS, 1 = FAIL)."""
    if not contract_path.is_file():
        print(f"Error: {contract_path} does not exist.", file=sys.stderr)
        return 1

    try:
        raw = contract_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading {contract_path}: {exc}", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Error: {contract_path} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate_contract(data, confidence_ceiling=confidence_ceiling)

    if output_format == "json":
        print(format_json_report(str(contract_path), errors, confidence_ceiling))
    else:
        print(format_text_report(str(contract_path), data, errors, confidence_ceiling))

    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Validate an AI agent output contract against the standard schema.",
        epilog="Exit code 0 = PASS, exit code 1 = FAIL.",
    )
    parser.add_argument(
        "contract_path",
        type=Path,
        help="Path to output_contract.json",
    )
    parser.add_argument(
        "--confidence-ceiling",
        type=int,
        default=DEFAULT_CONFIDENCE_CEILING,
        help=f"Maximum allowed confidence value (default: {DEFAULT_CONFIDENCE_CEILING})",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(
        run(
            contract_path=args.contract_path,
            confidence_ceiling=args.confidence_ceiling,
            output_format=args.output_format,
        )
    )
