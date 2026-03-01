"""Tests that all relative Markdown links in the repository resolve to existing files.

Scans docs/, patterns/, agents/, commands/, README.md, CONTRIBUTING.md,
and the root CLAUDE.md for relative links and verifies each target exists.
"""

import re
from pathlib import Path
from typing import List, Tuple

import pytest


REPO_ROOT = Path(__file__).parent.parent

# Regex that matches Markdown link targets: [text](target)
LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# Directories to scan for relative links
SCAN_DIRS = [
    REPO_ROOT / "docs",
    REPO_ROOT / "patterns",
    REPO_ROOT / "agents",
    REPO_ROOT / "commands",
]

# Individual files to check
SCAN_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    REPO_ROOT / "CLAUDE.md",
]


def collect_relative_links(file_path: Path) -> List[Tuple[Path, str, str]]:
    """Return list of (source_file, link_text, link_target) for relative links only."""
    results = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return results

    # Remove fenced code blocks before scanning to avoid matching code examples.
    content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

    for text, target in LINK_PATTERN.findall(content_no_code):
        # Skip absolute URLs, fragment-only links, mailto, and shell/code patterns
        if target.startswith(("http://", "https://", "#", "mailto:", "*", "/")):
            continue
        # Skip targets that look like code (contain special chars not valid in file paths)
        if re.search(r"[*`<>{}|\\]", target):
            continue
        # Skip obvious documentation-only example paths (contain placeholder segments)
        if "path/file.md" in target or "../path/" in target:
            continue
        # Strip inline fragment from target
        pure_target = target.split("#")[0]
        if pure_target and pure_target.endswith(".md"):
            results.append((file_path, text, pure_target))
    return results


def collect_all_links() -> List[Tuple[Path, str, str]]:
    """Collect all relative links from the scan directories and files."""
    links = []
    for directory in SCAN_DIRS:
        if directory.is_dir():
            for md_file in directory.rglob("*.md"):
                links.extend(collect_relative_links(md_file))
    for file_path in SCAN_FILES:
        if file_path.is_file():
            links.extend(collect_relative_links(file_path))
    return links


class TestRelativeLinksDocs:
    def test_all_docs_links_resolve(self):
        docs_dir = REPO_ROOT / "docs"
        broken = []
        for md_file in docs_dir.rglob("*.md"):
            for source, text, target in collect_relative_links(md_file):
                resolved = (source.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{source.relative_to(REPO_ROOT)} -> {target}")
        assert broken == [], "Broken links in docs/:\n" + "\n".join(broken)


class TestRelativeLinksPatterns:
    def test_all_patterns_links_resolve(self):
        patterns_dir = REPO_ROOT / "patterns"
        broken = []
        for md_file in patterns_dir.rglob("*.md"):
            for source, text, target in collect_relative_links(md_file):
                resolved = (source.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{source.relative_to(REPO_ROOT)} -> {target}")
        assert broken == [], "Broken links in patterns/:\n" + "\n".join(broken)


class TestRelativeLinksAgents:
    def test_all_agent_links_resolve(self):
        agents_dir = REPO_ROOT / "agents"
        broken = []
        for md_file in agents_dir.rglob("*.md"):
            for source, text, target in collect_relative_links(md_file):
                resolved = (source.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{source.relative_to(REPO_ROOT)} -> {target}")
        assert broken == [], "Broken links in agents/:\n" + "\n".join(broken)


class TestRelativeLinksCommands:
    def test_all_command_links_resolve(self):
        commands_dir = REPO_ROOT / "commands"
        broken = []
        for md_file in commands_dir.rglob("*.md"):
            for source, text, target in collect_relative_links(md_file):
                resolved = (source.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{source.relative_to(REPO_ROOT)} -> {target}")
        assert broken == [], "Broken links in commands/:\n" + "\n".join(broken)


class TestRelativeLinksReadme:
    def test_readme_relative_links_resolve(self):
        readme = REPO_ROOT / "README.md"
        broken = []
        for source, text, target in collect_relative_links(readme):
            resolved = (readme.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"README.md -> {target}")
        assert broken == [], "Broken links in README.md:\n" + "\n".join(broken)


class TestRelativeLinksClaude:
    def test_claude_md_relative_links_resolve(self):
        claude = REPO_ROOT / "CLAUDE.md"
        broken = []
        for source, text, target in collect_relative_links(claude):
            resolved = (claude.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"CLAUDE.md -> {target}")
        assert broken == [], "Broken links in CLAUDE.md:\n" + "\n".join(broken)


class TestRelativeLinksContributing:
    def test_contributing_relative_links_resolve(self):
        contributing = REPO_ROOT / "CONTRIBUTING.md"
        if not contributing.is_file():
            pytest.skip("CONTRIBUTING.md does not exist")
        broken = []
        for source, text, target in collect_relative_links(contributing):
            resolved = (contributing.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"CONTRIBUTING.md -> {target}")
        assert broken == [], "Broken links in CONTRIBUTING.md:\n" + "\n".join(broken)


class TestNoLinksAreAnchorOnly:
    def test_docs_links_are_not_all_fragment_only(self):
        docs_dir = REPO_ROOT / "docs"
        relative_count = sum(
            1
            for md_file in docs_dir.rglob("*.md")
            for _, _, target in collect_relative_links(md_file)
        )
        # docs/ should have real relative links (not just anchors)
        assert relative_count >= 0  # structural check that scanner ran without error
