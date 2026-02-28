"""Tests for scripts/ai_security_review.py.

Covers: diff parsing, pattern detection across severity levels,
JSON output format, and exit code logic.
"""

import json

import pytest

import ai_security_review as asr


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_diff(filename: str, added_lines: list[str]) -> str:
    """Build a minimal unified diff that adds the given lines to filename."""
    header = (
        f"diff --git a/{filename} b/{filename}\n"
        f"--- a/{filename}\n"
        f"+++ b/{filename}\n"
        f"@@ -1,1 +1,{len(added_lines) + 1} @@\n"
        " # existing line\n"
    )
    return header + "".join(f"+{line}\n" for line in added_lines)


# ---------------------------------------------------------------------------
# parse_diff_lines
# ---------------------------------------------------------------------------

class TestParseDiffLines:
    def test_returns_added_lines_only(self):
        diff = make_diff("file.py", ["added = True"])
        results = asr.parse_diff_lines(diff)
        assert any("added = True" in content for _, _, content in results)

    def test_does_not_return_removed_lines(self):
        diff = (
            "diff --git a/f.py b/f.py\n--- a/f.py\n+++ b/f.py\n"
            "@@ -1,2 +1,1 @@\n"
            "-removed_line = True\n"
            " context_line = 1\n"
        )
        results = asr.parse_diff_lines(diff)
        assert not any("removed_line" in content for _, _, content in results)

    def test_filename_is_extracted(self):
        diff = make_diff("src/config.py", ["x = 1"])
        results = asr.parse_diff_lines(diff)
        assert results[0][0] == "src/config.py"

    def test_line_numbers_start_at_correct_offset(self):
        diff = (
            "diff --git a/f.py b/f.py\n--- a/f.py\n+++ b/f.py\n"
            "@@ -5,3 +5,4 @@\n"
            " ctx = 1\n"
            "+new_line = True\n"
        )
        results = asr.parse_diff_lines(diff)
        assert results[0][1] == 6  # starts at hunk +5, context advances to 6

    def test_empty_diff_returns_empty_list(self):
        assert asr.parse_diff_lines("") == []


# ---------------------------------------------------------------------------
# scan_diff — CRITICAL patterns
# ---------------------------------------------------------------------------

class TestScanDiffCritical:
    def test_detects_anthropic_api_key(self):
        diff = make_diff("config.py", ["KEY = 'sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWXYZabcde'"])
        findings = asr.scan_diff(diff)
        assert any(f.severity == "CRITICAL" and "anthropic" in f.pattern for f in findings)

    def test_detects_aws_access_key(self):
        diff = make_diff("aws.py", ["AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'"])
        findings = asr.scan_diff(diff)
        assert any(f.pattern == "aws_access_key_id" for f in findings)

    def test_detects_private_key_block(self):
        diff = make_diff("key.pem", ["-----BEGIN RSA PRIVATE KEY-----"])
        findings = asr.scan_diff(diff)
        assert any(f.severity == "CRITICAL" for f in findings)

    def test_detects_hardcoded_password(self):
        diff = make_diff("db.py", ['password = "s3cr3tP@ssw0rd"'])
        findings = asr.scan_diff(diff)
        assert any(f.pattern == "hardcoded_password" for f in findings)

    def test_detects_connection_string_with_credentials(self):
        diff = make_diff("db.py", ["DB_URL = 'postgresql://admin:hunter2@db.internal/prod'"])
        findings = asr.scan_diff(diff)
        assert any(f.pattern == "connection_string_with_credentials" for f in findings)


# ---------------------------------------------------------------------------
# scan_diff — HIGH patterns
# ---------------------------------------------------------------------------

class TestScanDiffHigh:
    def test_detects_internal_ip_10_x(self):
        diff = make_diff("infra.py", ["HOST = '10.0.1.42'"])
        findings = asr.scan_diff(diff)
        assert any(f.severity == "HIGH" and "ip" in f.pattern for f in findings)

    def test_detects_internal_ip_192_168(self):
        diff = make_diff("config.py", ["server = '192.168.1.100'"])
        findings = asr.scan_diff(diff)
        assert any(f.severity == "HIGH" for f in findings)

    def test_detects_sensitive_system_file(self):
        diff = make_diff("setup.sh", ["cat /etc/passwd"])
        findings = asr.scan_diff(diff)
        assert any(f.pattern == "sensitive_system_file" for f in findings)


# ---------------------------------------------------------------------------
# scan_diff — MEDIUM patterns
# ---------------------------------------------------------------------------

class TestScanDiffMedium:
    def test_detects_email_address(self):
        diff = make_diff("data.py", ["contact = 'john.doe@example.com'"])
        findings = asr.scan_diff(diff)
        assert any(f.severity == "MEDIUM" and f.pattern == "email_address" for f in findings)

    def test_detects_ssn_pattern(self):
        diff = make_diff("records.py", ["ssn = '123-45-6789'"])
        findings = asr.scan_diff(diff)
        assert any(f.pattern == "pii_ssn_pattern" for f in findings)


# ---------------------------------------------------------------------------
# scan_diff — LOW patterns
# ---------------------------------------------------------------------------

class TestScanDiffLow:
    def test_detects_debug_mode_enabled(self):
        diff = make_diff("settings.py", ["debug = True"])
        findings = asr.scan_diff(diff)
        assert any(f.severity == "LOW" and "debug" in f.pattern for f in findings)

    def test_detects_ssl_verify_false(self):
        diff = make_diff("client.py", ["requests.get(url, verify=False)"])
        findings = asr.scan_diff(diff)
        assert any(f.pattern == "insecure_ssl_verify_disabled" for f in findings)


# ---------------------------------------------------------------------------
# Clean diff produces no CRITICAL findings
# ---------------------------------------------------------------------------

class TestCleanDiff:
    def test_clean_diff_has_no_critical_findings(self, sample_diff_clean):
        findings = asr.scan_diff(sample_diff_clean)
        assert not any(f.severity == "CRITICAL" for f in findings)

    def test_clean_python_function_returns_empty(self):
        diff = make_diff("math.py", [
            "def add(a: int, b: int) -> int:",
            "    return a + b",
        ])
        findings = asr.scan_diff(diff)
        assert findings == []


# ---------------------------------------------------------------------------
# build_summary
# ---------------------------------------------------------------------------

class TestBuildSummary:
    def test_empty_findings_all_zeros(self):
        summary = asr.build_summary([])
        assert summary == {"critical": 0, "high": 0, "medium": 0, "low": 0}

    def test_counts_severities_correctly(self):
        findings = [
            asr.Finding("CRITICAL", "f.py", 1, "p1", "d1"),
            asr.Finding("CRITICAL", "f.py", 2, "p2", "d2"),
            asr.Finding("HIGH", "f.py", 3, "p3", "d3"),
            asr.Finding("MEDIUM", "f.py", 4, "p4", "d4"),
        ]
        summary = asr.build_summary(findings)
        assert summary["critical"] == 2
        assert summary["high"] == 1
        assert summary["medium"] == 1
        assert summary["low"] == 0


# ---------------------------------------------------------------------------
# run — JSON output and exit codes
# ---------------------------------------------------------------------------

class TestRun:
    def test_clean_diff_exits_zero(self, sample_diff_clean, capsys):
        code = asr.run(sample_diff_clean)
        assert code == 0

    def test_diff_with_critical_exits_one(self, sample_diff_with_api_key, capsys):
        code = asr.run(sample_diff_with_api_key)
        assert code == 1

    def test_output_is_valid_json(self, sample_diff_clean, capsys):
        asr.run(sample_diff_clean)
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "findings" in parsed
        assert "summary" in parsed

    def test_json_findings_is_list(self, sample_diff_clean, capsys):
        asr.run(sample_diff_clean)
        parsed = json.loads(capsys.readouterr().out)
        assert isinstance(parsed["findings"], list)

    def test_json_summary_has_all_severity_keys(self, sample_diff_clean, capsys):
        asr.run(sample_diff_clean)
        summary = json.loads(capsys.readouterr().out)["summary"]
        for key in ("critical", "high", "medium", "low"):
            assert key in summary

    def test_critical_finding_is_included_in_json(self, sample_diff_with_api_key, capsys):
        asr.run(sample_diff_with_api_key)
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["summary"]["critical"] >= 1
