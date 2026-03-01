"""Scan a git diff for security patterns: API keys, secrets, PII, hardcoded paths.

Accepts a unified diff via stdin or a file path argument. Outputs structured
JSON with all findings and a severity summary. Exits with code 1 if any
CRITICAL findings are detected so it can serve as a hard CI gate.

Usage:
    git diff HEAD~1 | python3 scripts/ai_security_review.py
    python3 scripts/ai_security_review.py --file changes.diff
    python3 scripts/ai_security_review.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Finding:
    """One security finding from a scanned diff line."""

    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    file: str
    line: int
    pattern: str
    description: str


# Each entry: (severity, pattern_name, regex, description)
# Patterns are evaluated against every added line in the diff.
PATTERNS: List[Tuple[str, str, str, str]] = [
    # --- CRITICAL: credentials and keys that enable direct access ---
    (
        "CRITICAL",
        "anthropic_api_key",
        r"sk-ant-[A-Za-z0-9\-_]{20,}",
        "Anthropic API key detected",
    ),
    (
        "CRITICAL",
        "openai_api_key",
        r"\bsk-[A-Za-z0-9]{48}\b",
        "Possible OpenAI API key detected",
    ),
    (
        "CRITICAL",
        "aws_access_key_id",
        r"\bAKIA[0-9A-Z]{16}\b",
        "AWS access key ID detected",
    ),
    (
        "CRITICAL",
        "aws_secret_key",
        r'(?i)aws[_\-\s]?secret[_\-\s]?access[_\-\s]?key\s*[=:]\s*["\']?[A-Za-z0-9+/]{40}["\']?',
        "AWS secret access key assignment detected",
    ),
    (
        "CRITICAL",
        "github_token",
        r"\bghp_[A-Za-z0-9]{36}\b|\bgithub[_\-\s]?token\s*[=:]\s*[\"'][A-Za-z0-9\-_]{20,}[\"']",
        "GitHub personal access token detected",
    ),
    (
        "CRITICAL",
        "private_key_block",
        r"-----BEGIN\s+(RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "Private key block present in diff",
    ),
    (
        "CRITICAL",
        "hardcoded_password",
        r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}["\']',
        "Hardcoded password value detected",
    ),
    (
        "CRITICAL",
        "connection_string_with_credentials",
        r"(?i)(mongodb|postgresql|postgres|mysql|redis|amqp|mssql|jdbc)\+?://[^@\s]{1,64}:[^@\s]{1,64}@",
        "Database or message-broker connection string with embedded credentials",
    ),
    (
        "CRITICAL",
        "generic_api_key",
        r'(?i)\bapi[_\-]?key\s*[=:]\s*["\']?[A-Za-z0-9\-_]{20,}["\']?',
        "Possible API key assignment detected",
    ),
    # --- HIGH: sensitive references that are often exploitable ---
    (
        "HIGH",
        "secret_variable_assignment",
        r'(?i)(secret|token|credential|auth_key)\s*[=:]\s*["\'][A-Za-z0-9\-_+/=]{12,}["\']',
        "Possible secret value assigned to a variable",
    ),
    (
        "HIGH",
        "internal_ip_address",
        r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"|172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}"
        r"|192\.168\.\d{1,3}\.\d{1,3})\b",
        "Hardcoded internal / RFC-1918 IP address",
    ),
    (
        "HIGH",
        "sensitive_system_file",
        r"/etc/(passwd|shadow|sudoers|ssh/[a-z_]+)",
        "Reference to sensitive system file",
    ),
    (
        "HIGH",
        "hardcoded_ssh_path",
        r'(?i)["\']?/home/\w+/\.ssh/(id_rsa|id_ed25519|authorized_keys)["\']?',
        "Hardcoded SSH key or authorized_keys path",
    ),
    # --- MEDIUM: PII, environment assignments, and weak configurations ---
    (
        "MEDIUM",
        "email_address",
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        "Email address in diff — verify this is synthetic or intentional",
    ),
    (
        "MEDIUM",
        "sensitive_env_assignment",
        r"(?i)(ANTHROPIC|OPENAI|AWS|AZURE|GCP|DATABASE|DB|SECRET|TOKEN)"
        r"[_A-Z]*\s*=\s*[\"'][^\"']{8,}[\"']",
        "Direct assignment to a sensitive environment variable",
    ),
    (
        "MEDIUM",
        "hardcoded_localhost_port",
        r'(?i)(host|server|url)\s*[=:]\s*["\']?(localhost|127\.0\.0\.1):\d{4,5}["\']?',
        "Hardcoded localhost with port — verify this is not production config",
    ),
    (
        "MEDIUM",
        "pii_ssn_pattern",
        r"\b\d{3}-\d{2}-\d{4}\b",
        "Pattern matching a US Social Security Number",
    ),
    (
        "MEDIUM",
        "pii_credit_card",
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
        "Pattern matching a payment card number",
    ),
    # --- LOW: code quality and configuration concerns ---
    (
        "LOW",
        "security_todo_fixme",
        r"(?i)#\s*(TODO|FIXME|HACK|XXX).{0,60}(security|auth|cred|secret|password|token)",
        "Security-related TODO or FIXME comment left in code",
    ),
    (
        "LOW",
        "debug_mode_enabled",
        r"(?i)(debug\s*=\s*True|DEBUG\s*=\s*1|logging\.basicConfig\s*\(\s*level\s*=\s*logging\.DEBUG)",
        "Debug mode enabled — verify this is not present in production configuration",
    ),
    (
        "LOW",
        "insecure_ssl_verify_disabled",
        r"(?i)verify\s*=\s*False|ssl_verify\s*=\s*False|REQUESTS_CA_BUNDLE\s*=\s*['\"]?['\"]?",
        "SSL/TLS certificate verification disabled",
    ),
]


def parse_diff_lines(diff_text: str) -> List[Tuple[str, int, str]]:
    """Parse a unified diff and return (filename, line_number, line_content) for added lines.

    Only added lines (starting with '+') are returned — we care about what
    is being introduced, not what is being removed.
    """
    results: List[Tuple[str, int, str]] = []
    current_file = "<unknown>"
    current_line = 0

    for raw_line in diff_text.splitlines():
        # Track the current file being diffed.
        if raw_line.startswith("diff --git "):
            parts = raw_line.split(" b/")
            if len(parts) >= 2:
                current_file = parts[-1].strip()
            current_line = 0
            continue

        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:].strip()
            continue

        # Parse the hunk header to set the starting line number.
        if raw_line.startswith("@@ "):
            match = re.search(r"\+(\d+)", raw_line)
            if match:
                current_line = int(match.group(1)) - 1
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            current_line += 1
            results.append((current_file, current_line, raw_line[1:]))
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            # Removed lines do not advance the new-file line counter.
            pass
        elif not raw_line.startswith("\\"):
            # Context lines advance the line counter.
            current_line += 1

    return results


def scan_diff(diff_text: str) -> List[Finding]:
    """Scan added lines in a diff for all configured security patterns."""
    findings: List[Finding] = []
    parsed = parse_diff_lines(diff_text)

    for filename, lineno, line_content in parsed:
        for severity, pattern_name, regex, description in PATTERNS:
            if re.search(regex, line_content):
                findings.append(
                    Finding(
                        severity=severity,
                        file=filename,
                        line=lineno,
                        pattern=pattern_name,
                        description=description,
                    )
                )

    return findings


def build_summary(findings: List[Finding]) -> Dict[str, int]:
    """Count findings by severity level."""
    return {
        "critical": sum(1 for f in findings if f.severity == "CRITICAL"),
        "high": sum(1 for f in findings if f.severity == "HIGH"),
        "medium": sum(1 for f in findings if f.severity == "MEDIUM"),
        "low": sum(1 for f in findings if f.severity == "LOW"),
    }


def run(diff_text: str) -> int:
    """Scan diff, print JSON report, and return the appropriate exit code."""
    findings = scan_diff(diff_text)
    summary = build_summary(findings)

    result = {
        "findings": [
            {
                "severity": f.severity,
                "file": f.file,
                "line": f.line,
                "pattern": f.pattern,
                "description": f.description,
            }
            for f in findings
        ],
        "summary": summary,
    }

    print(json.dumps(result, indent=2))

    if summary["critical"] > 0:
        print(
            f"\nSECURITY GATE FAILED: {summary['critical']} CRITICAL finding(s) detected."
            "\nResolve all CRITICAL findings before merging.",
            file=sys.stderr,
        )
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Scan a git diff for security patterns: secrets, PII, hardcoded credentials.",
        epilog=(
            "Exits with code 1 if any CRITICAL findings are detected. "
            "Use as a CI gate: git diff origin/main...HEAD | python3 scripts/ai_security_review.py"
        ),
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        metavar="PATH",
        help="Path to a diff file. If omitted, reads from stdin.",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                diff_text = fh.read()
        except OSError as exc:
            print(f"Error: could not read diff file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print(
                "No input provided. Pipe a git diff or use --file. Try --help for usage.",
                file=sys.stderr,
            )
            sys.exit(1)
        diff_text = sys.stdin.read()

    sys.exit(run(diff_text))
