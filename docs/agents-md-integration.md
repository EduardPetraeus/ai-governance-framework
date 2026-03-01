# AGENTS.md Integration Guide

AGENTS.md is an emerging cross-tool standard for portable AI agent instructions — adopted by
60,000+ projects and shepherded by the Linux Foundation. This guide explains how it fits into
the AI Governance Framework's layer architecture and how to run `CLAUDE.md` and `AGENTS.md`
side by side.

---

## The layer approach

The framework separates governance into two complementary files:

```
┌─────────────────────────────────────────────────────────┐
│  CLAUDE.md — Layer 1 Constitution (Claude Code-native)  │
│  Session protocol, slash commands, kill switch config,  │
│  constitutional inheritance (org → team → repo),        │
│  model routing, multi-agent orchestration, ADR refs     │
├─────────────────────────────────────────────────────────┤
│  AGENTS.md — Portable Bridge (cross-tool)               │
│  Commands (test, lint, build), naming conventions,      │
│  security rules, kill switch triggers — the subset      │
│  of governance that any AI tool can read and follow     │
└─────────────────────────────────────────────────────────┘
```

**CLAUDE.md** is the governance constitution. It encodes the full framework: session
lifecycle, multi-layer inheritance, confidence ceiling, and the complete kill switch
specification. It is designed for Claude Code and is loaded automatically at session start.

**AGENTS.md** is the portable bridge. It encodes the subset of governance that is
tool-agnostic: what commands to run, how to name things, what to never commit. Any agent
that reads the file benefits from the same baseline, whether it is Claude Code, Copilot,
Cursor, Windsurf, or Aider.

The two files are not redundant — they serve different audiences. CLAUDE.md governs the
session; AGENTS.md governs the code. Together they provide full-stack governance across
every tool in use on the project.

---

## When to use AGENTS.md

Add `AGENTS.md` to your repository if:

- The team uses more than one AI coding tool (Claude Code for architecture, Copilot for
  inline suggestions, Aider for quick patches)
- You contribute to open-source projects where you cannot control which tool contributors
  use
- You want a portable, readable summary of project conventions that any tool can act on
- You are integrating with a platform that reads AGENTS.md natively (e.g., CI runners
  that inspect AGENTS.md for command definitions)

AGENTS.md is optional when Claude Code is the only tool in use and the team has no
cross-tool portability requirement. In that case, `CLAUDE.md` alone is sufficient.

---

## Three coexistence options

### Option 1 — Manual dual maintenance

Maintain both files separately. CLAUDE.md holds the full governance specification;
AGENTS.md holds the portable subset, kept in sync manually when conventions change.

```
repo/
├── CLAUDE.md      # Full governance — session protocol, slash commands, inheritance
└── AGENTS.md      # Portable bridge — commands, naming, security
```

**When to use:** the team uses both Claude Code and one or more other tools actively.
Each file can be optimised for its audience without compromise.

**How to keep in sync:** update both files in the same PR whenever conventions change.
The CI governance check (`ci-cd/github-actions/governance-check.yml`) can be extended to
flag when `CLAUDE.md` conventions diverge from `AGENTS.md`.

**Pros:** each file is clean and tool-optimised. No coupling.
**Cons:** two files to maintain. Manual sync discipline required.

---

### Option 2 — Symlink (CLAUDE.md as source of truth)

Create a symlink so `AGENTS.md` points to `CLAUDE.md`. Both names refer to the same
content. Tools that read `AGENTS.md` see the full `CLAUDE.md`.

```bash
ln -sf CLAUDE.md AGENTS.md
git add AGENTS.md
git commit -m "chore: add AGENTS.md symlink to CLAUDE.md"
```

**When to use:** your `CLAUDE.md` is compact (under 100 lines) and already written in
tool-agnostic language — no Claude Code-specific slash command syntax, no
`inherits_from` directives, no kill switch configuration blocks. The file reads as plain
conventions that any tool can follow.

**Pros:** single source of truth. Zero sync overhead.
**Cons:** Claude Code-specific sections (kill switch config, model routing, slash command
references) appear in `AGENTS.md` and may confuse other tools. Works best when
`CLAUDE.md` is intentionally kept minimal. Symlinks require care in CI environments and
on Windows.

**Verification:**

```bash
# Confirm symlink resolves correctly
ls -la AGENTS.md
# Expected: AGENTS.md -> CLAUDE.md
```

---

### Option 3 — Generator (automated sync)

Use a script to extract governance sections from `CLAUDE.md` and write `AGENTS.md`
automatically. Run the generator in CI to keep them in sync.

**Generator script (`scripts/generate_agents_md.py`):**

```python
"""
Generate AGENTS.md from CLAUDE.md by extracting portable sections.
Portable sections: conventions, security_protocol, kill_switch.
Claude-specific sections: session_protocol, agents, commands, inherits_from.
"""
import re
import sys
from pathlib import Path

PORTABLE_SECTIONS = {"conventions", "security_protocol", "security", "kill_switch"}

def extract_sections(source: str) -> dict[str, str]:
    """Return a dict of {section_name: content} parsed from YAML-style headings."""
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    for line in source.splitlines(keepends=True):
        heading = re.match(r"^## (\w+)", line)
        if heading:
            if current:
                sections[current] = "".join(buffer)
            current = heading.group(1)
            buffer = [line]
        elif current:
            buffer.append(line)
    if current:
        sections[current] = "".join(buffer)
    return sections

def generate(claude_md: Path, agents_md: Path) -> None:
    source = claude_md.read_text()
    sections = extract_sections(source)
    portable = {k: v for k, v in sections.items() if k in PORTABLE_SECTIONS}
    header = (
        "# AGENTS.md — generated from CLAUDE.md\n"
        "# Do not edit directly. Run scripts/generate_agents_md.py to regenerate.\n\n"
    )
    agents_md.write_text(header + "\n".join(portable.values()))
    print(f"Written {agents_md} ({len(portable)} sections from {claude_md})")

if __name__ == "__main__":
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    generate(repo / "CLAUDE.md", repo / "AGENTS.md")
```

**GitHub Actions step to validate sync:**

```yaml
- name: Verify AGENTS.md is up to date
  run: |
    python scripts/generate_agents_md.py .
    git diff --exit-code AGENTS.md || \
      (echo "AGENTS.md is out of sync with CLAUDE.md. Run scripts/generate_agents_md.py" && exit 1)
```

**When to use:** your `CLAUDE.md` is the authoritative source but contains Claude-specific
sections that should not appear in `AGENTS.md`. The generator extracts only the portable
sections and writes a clean bridge file.

**Pros:** single source of truth with clean output for each audience. Zero manual sync
after setup.
**Cons:** requires maintaining the generator script. Section structure in `CLAUDE.md`
must be machine-parseable. Add the generator script to the repository before enabling the
CI step.

---

## Choosing an option

| | Option 1 — Manual | Option 2 — Symlink | Option 3 — Generator |
|---|:---:|:---:|:---:|
| Single source of truth | No | Yes | Yes |
| Clean output per tool | Yes | No | Yes |
| Setup effort | Low | Minimal | Medium |
| Ongoing maintenance | Medium | Zero | Low (generator) |
| Works on Windows | Yes | Risky | Yes |
| Best for | Active multi-tool teams | Minimal CLAUDE.md | Complex CLAUDE.md |

**Recommended default:** Option 1 (Manual). Keep `CLAUDE.md` as the governance
constitution and `AGENTS.md` as the portable bridge. Update both in the same PR when
conventions change. The discipline cost is low; the separation of concerns is clear.

**Upgrade to Option 3** when the repository has reached governance maturity Level 3+
(CLAUDE.md is stable, CI is in place, the conventions are unlikely to change frequently)
and the team wants zero-maintenance sync.

---

## Relationship to the 7-layer stack

AGENTS.md lives at Layer 1 (Constitution) alongside CLAUDE.md. It does not add a new
layer — it extends the constitution's reach to tools that cannot read CLAUDE.md.

```
Layer 1: CONSTITUTION
  ├── CLAUDE.md        — full governance (Claude Code)
  └── AGENTS.md        — portable subset (all tools)
Layer 2: ORCHESTRATION — session protocol (Claude Code only)
Layer 3: ENFORCEMENT   — CI/CD workflows (all tools, IDE-agnostic)
```

CI/CD enforcement at Layer 3 is the equaliser. The governance check, AI PR review, and
pre-commit hooks run the same checks regardless of which tool generated the code. A team
using Aider for day-to-day coding and Claude Code for architecture decisions gets the same
enforcement as a team using Claude Code exclusively.

---

## Core Edition addon

Core Edition users can add AGENTS.md without installing the full framework:

```bash
# Add AGENTS.md to an existing Core Edition setup
cp templates/AGENTS.md ./AGENTS.md
# Fill in project, stack, and commands sections
# Update CHANGELOG.md
git add AGENTS.md && git commit -m "chore: add AGENTS.md portable governance bridge"
```

This extends the Core Edition's CLAUDE.md constitution to all AI tools used on the
project. No additional CI configuration is required — the existing `governance-check.yml`
workflow already runs the relevant checks.

---

## Further reading

- [templates/AGENTS.md](../templates/AGENTS.md) — the portable bridge template
- [templates/CLAUDE.md](../templates/CLAUDE.md) — the full governance constitution
- [docs/multi-ide-support.md](multi-ide-support.md) — feature comparison across all supported tools
- [patterns/constitutional-inheritance.md](../patterns/constitutional-inheritance.md) — org → team → repo rules
- [examples/core-edition/](../examples/core-edition/) — minimum viable governance setup
