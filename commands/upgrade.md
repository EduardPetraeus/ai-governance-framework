# /upgrade

Check for and apply updates from the upstream AI Governance Framework repository. This command keeps your project's governance current without requiring you to manually track releases, read changelogs, or diff templates.

## Usage

```
/upgrade
```

No arguments needed. The command reads the current version, checks for updates, and walks you through applying them.

## Steps

### Step 1: Determine current version

Check for the framework version in this order:
1. `.governance-version` file in the project root (contains a single version string, e.g., `v1.2.0`)
2. CLAUDE.md metadata section (if it includes a `framework_version` field)
3. If neither exists, report: "No framework version marker found. I will compare your files against the latest templates to identify gaps."

### Step 2: Check upstream for new releases

Check the upstream `ai-governance-framework` GitHub repository for releases newer than the current version.

If the upstream repository is available as a local clone or a configured remote:
- Run `git ls-remote --tags` to list available versions
- Compare against the current version using semantic versioning

If the upstream is not configured locally:
- Check the GitHub releases page for the repository
- Parse version tags and changelogs

If no upstream is reachable:
- Report: "Cannot reach the upstream repository. Check your network connection or verify the repository URL. You can also run a manual comparison by cloning the latest framework and diffing against your governance files."

### Step 3: List available updates

For each release between the current version and the latest, parse the CHANGELOG and categorize changes:

- **New agents** (`+`): agent definition files added to `agents/`
- **New commands** (`+`): slash command definitions added to `commands/`
- **New patterns** (`+`): pattern files added to `patterns/`
- **New docs** (`+`): documentation files added to `docs/`
- **Updated files** (`*`): existing files modified (templates, guides, agents, commands)
- **Breaking changes** (warning): changes that require migration (renamed sections, changed contracts, restructured directories)

Classify each change as:
- **Non-breaking:** new files, additive changes, documentation updates. Can be applied without modifying existing customized files.
- **Breaking:** renamed or removed sections, changed agent input/output contracts, restructured CLAUDE.md template. Requires migration steps.

### Step 4: Present the update report

```
/upgrade Check
==============
Your version: v[current]
Latest version: v[latest]
Releases to apply: [N]

v[version] changes:
  + New agent: [filename]
  + New command: [filename]
  + New pattern: [filename]
  * Updated: [filename] ([summary of what changed])
  [warning] Breaking: [description of breaking change]

v[version] changes:
  + [additions]
  * [updates]
  [warning] [breaking changes, if any]

Non-breaking updates: [N] files
Breaking updates: [N] files

Apply all non-breaking updates? [Y/n]
Show migration guide for breaking changes? [Y/n]
```

Wait for the user's response before applying anything.

### Step 5: Apply non-breaking updates

For each non-breaking update the user approves:

**New files (agents, commands, patterns, docs):**
- Place the file in the correct directory
- If the file should also be installed in `.claude/agents/` or `.claude/commands/`, install it there too
- Verify cross-references in the new file resolve to existing files

**Updated templates:**
- Show a diff between the current template and the new template
- Ask whether to apply the update or keep the current version
- Never overwrite a customized file without explicit confirmation

**Updated guides and documentation:**
- Apply the update directly (these are framework reference docs, not project-specific)
- Note any new sections or changed recommendations

### Step 6: Handle breaking changes

For each breaking change, present:
1. **What changed:** specific description of the breaking change
2. **Why it changed:** the rationale from the upstream CHANGELOG
3. **Migration steps:** exact steps to update the project's files
4. **Risk:** what happens if you do not migrate (e.g., "agent definitions using the old input format will fail")

Do not apply breaking changes automatically. Present the migration guide and wait for the user to confirm each one.

### Step 7: Update version marker and log

After applying updates:
1. Update `.governance-version` to the new version (or create it if it does not exist)
2. Add a CHANGELOG.md entry:

```markdown
## Governance Upgrade -- [date]

### Framework upgrade: v[old] to v[new]
- [list of files added]
- [list of files updated]
- [list of breaking changes applied, if any]
```

3. Commit the changes:

```bash
git add .governance-version CHANGELOG.md [all updated files]
git commit -m "docs: upgrade governance framework from v[old] to v[new]"
```

## Output Format

The primary output is the update report from Step 4. After applying updates, the command produces a summary:

```
/upgrade Applied
================
Previous version: v[old]
New version: v[new]

Applied:
  + [file]: [action taken]
  * [file]: [action taken]

Skipped:
  [file]: [reason -- user declined, breaking change deferred, etc.]

CHANGELOG.md updated with upgrade entry.
.governance-version updated to v[new].

Committed: "docs: upgrade governance framework from v[old] to v[new]"
```

## Rules

- Never overwrite a file the user has customized without explicit confirmation. Always show the diff first.
- Never apply breaking changes automatically. Always present the migration guide and wait for approval.
- If the user has modified a template file (e.g., CLAUDE.md), compare section by section rather than replacing the whole file. New sections can be added; existing customized sections should be preserved.
- If the upstream introduces a new required section in CLAUDE.md, flag it clearly: "The new version adds a required section: [section name]. Your CLAUDE.md does not have this section. Add it now? I will populate it with defaults that you can customize."
- Always update `.governance-version` after a successful upgrade so future upgrades have the correct baseline.
- If the upgrade fails partway through (e.g., a file conflict), report exactly what was applied and what was not. Do not leave the project in an inconsistent state -- either complete the upgrade or roll back the partial changes.
- The `/upgrade` command checks for updates but does not auto-run on a schedule. For automated upgrade notifications, configure a GitHub Action that runs `/upgrade --check-only` weekly and opens an issue when updates are available.

## Implementation Note

This command currently requires manual comparison against the upstream repository. The framework roadmap includes a CLI tool (`npx ai-governance-upgrade`) that will automate the version comparison, diff generation, and selective application. Until that tool ships, this command relies on the agent reading both the local governance files and the upstream repository to perform the comparison.

---

## Example Output

### Check with updates available

```
/upgrade Check
==============
Your version: v1.2.0
Latest version: v1.4.0
Releases to apply: 2

v1.3.0 changes:
  + New agent: drift-detector-agent.md
  + New command: validate.md
  + New pattern: context-boundaries.md
  * Updated: maturity-model.md (Level 4 criteria refined: added master agent requirement)
  * Updated: architecture.md (Layer 5 expanded: onboarding added to Knowledge layer)

v1.4.0 changes:
  + New agent: research-agent.md
  + New agent: onboarding-agent.md
  + New command: research.md
  + New command: upgrade.md
  + New command: health-check.md
  + New docs: research-pipeline.md
  + New docs: self-updating-framework.md
  * Updated: README.md (new sections: roadmap, agents table updated)
  * Updated: CLAUDE.md template (new optional section: model_routing)

Non-breaking updates: 12 files
Breaking updates: 0 files

Apply all non-breaking updates? [Y/n]
```

### After applying

```
/upgrade Applied
================
Previous version: v1.2.0
New version: v1.4.0

Applied:
  + agents/drift-detector-agent.md: installed to agents/ and .claude/agents/
  + agents/research-agent.md: installed to agents/ and .claude/agents/
  + agents/onboarding-agent.md: installed to agents/
  + commands/validate.md: installed to commands/ and .claude/commands/
  + commands/research.md: installed to commands/ and .claude/commands/
  + commands/upgrade.md: installed to commands/ and .claude/commands/
  + commands/health-check.md: installed to commands/ and .claude/commands/
  + patterns/context-boundaries.md: installed to patterns/
  + docs/research-pipeline.md: installed to docs/
  + docs/self-updating-framework.md: installed to docs/
  * docs/maturity-model.md: updated (Level 4 criteria refined)
  * docs/architecture.md: updated (Layer 5 expanded)

Skipped:
  README.md: user declined (local README has project-specific content)
  CLAUDE.md template: model_routing section noted for manual addition

CHANGELOG.md updated with upgrade entry.
.governance-version updated to v1.4.0.

Committed: "docs: upgrade governance framework from v1.2.0 to v1.4.0"
```

### Check with breaking changes

```
/upgrade Check
==============
Your version: v1.4.0
Latest version: v2.0.0
Releases to apply: 1

v2.0.0 changes:
  * CLAUDE.md template: mandatory_session_protocol renamed to session_protocol
    (breaking -- all CLAUDE.md files must rename this section)
  * Agent contracts: all agents now require a "confidence" field in output
    (breaking -- custom agents must add confidence scoring)
  + New agent: cost-tracker-agent.md
  + New pattern: confidence-scoring.md
  * Updated: all existing agent definitions (added confidence output)

Non-breaking updates: 3 files
Breaking updates: 2 changes requiring migration

Apply all non-breaking updates? [Y/n]
Show migration guide for breaking changes? [Y/n]

---

Migration Guide: v1.4.0 to v2.0.0
===================================

1. CLAUDE.md section rename
   Old: ## mandatory_session_protocol
   New: ## session_protocol
   Action: Rename the section header in your CLAUDE.md. Content is unchanged.
   Risk if skipped: Agents reading the v2.0 template will not find the session
   protocol under the old name.

2. Agent confidence output
   Old: Agent output ends with findings and recommendations.
   New: Agent output must include a "Confidence: [0-100]" field.
   Action: If you have custom agent definitions in .claude/agents/, add a
   confidence field to their output format section.
   Risk if skipped: The master agent and quality gate agent will flag missing
   confidence scores as validation failures.

Apply migration step 1? [Y/n]
Apply migration step 2? [Y/n]
```
