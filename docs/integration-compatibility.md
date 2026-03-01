# Integration Compatibility

How this framework compares to three alternative approaches, and how to migrate from each.

---

## Comparison

| Dimension | This Framework | Fr-e-d | AI Governor | claude-code-config |
|---|---|---|---|---|
| Governance layers | 7 structured layers (Constitution through Evolution) | Single rule file | Single policy layer | Template collection (no layers) |
| Session protocol | Full lifecycle: start, during, end, auto-recovery | None | None | None |
| Multi-agent support | 11 specialized agents with master orchestration | None | None | None |
| CI/CD enforcement | 5 platforms (GitHub Actions, GitLab, CircleCI, Bitbucket, Azure DevOps) | None | GitHub Actions only (PR-level) | None |
| Multi-IDE support | 4 IDEs (Cursor, Copilot, Windsurf, Aider) via AGENTS.md bridge | Claude Code only | GitHub Copilot focus | Claude Code only |
| Maturity model | 6 levels (0-5) with upgrade paths and self-assessment | None | None | None |
| Test suite | 273 tests across 13 files | None | None | None |
| Migration tooling | CLI wizard (`npx ai-governance-init`) + Core Edition 10-min path | N/A | None | None |
| Zero core dependencies | Yes (Markdown + optional Python automation) | Yes (Markdown only) | Python + GitHub Actions | Markdown only |
| Template count | 16 templates including org/team inheritance | 1 rules file | Policy templates (threat-model generated) | 10+ project-type templates |
| Constitutional inheritance | Org, team, repo hierarchy with validation | None | None | None |
| Self-testing | Red team agent, drift detector, health score | None | None | None |

---

## What makes this framework different

Most AI governance approaches produce static documents: a rules file, a policy document, a template collection. They capture intent at a single point in time and rely on developers to maintain compliance through discipline. This works until deadline pressure, team growth, or agent autonomy erode the habits that made the rules effective.

This framework is a living system, not a static document. The drift detector agent identifies when governance files have diverged from actual practice. The health score calculator quantifies degradation across 15 dimensions. The red team auditor probes for gaps adversarially. CI gates reject changes that reduce governance quality. These mechanisms create a self-correcting loop: governance does not depend on developer discipline because the system detects and reports when discipline fails.

The structural difference is enforcement depth. Fr-e-d provides excellent single-file constraints. AI Governor generates security policies from threat models. claude-code-config offers well-curated starting points. All three stop at the document layer. This framework continues through orchestration (session protocol), enforcement (CI gates on 5 platforms), observability (audit trails, cost tracking), knowledge management (ADRs, cross-session memory), team governance (multi-agent coordination, role-based access), and evolution (self-updating, quarterly review). Each layer builds on the one below, and each layer has concrete enforcement mechanisms.

The constitutional inheritance hierarchy is the enterprise differentiator. An organization-level CLAUDE.md defines global constraints that cascade to every team and repository through `inherits_from` directives validated by CI. A team cannot weaken org-level security rules. A repository cannot bypass team naming conventions. This is governance by constraint, not governance by agreement. Static documents cannot enforce inheritance because they lack the machinery to validate compliance across organizational boundaries.

---

## Migration from Fr-e-d

### What maps directly

Fr-e-d's rule file maps to the `## conventions` and `## security_protocol` sections in CLAUDE.md. If your `.claude/rules` or `RULES.md` contains rules like "never commit .env files" or "use snake_case for Python files," these translate one-to-one into CLAUDE.md sections.

### What requires augmentation

Fr-e-d has no session protocol, no CI enforcement, no multi-agent coordination, no maturity tracking, and no cross-session memory. These are additive — you gain them by adopting the framework layers you need without losing your existing rules.

### Step-by-step migration

```bash
# 1. Initialize the framework
npx ai-governance-init
# Select your CI platform and IDE when prompted

# 2. Copy your existing rules into CLAUDE.md
# Open your .claude/rules or RULES.md and the generated CLAUDE.md side by side.
# Move each rule into the appropriate section:
#   - Naming rules     → ## conventions
#   - Security rules   → ## security_protocol
#   - Workflow rules   → ## session_protocol
#   - Forbidden items  → ## forbidden

# 3. Install session commands
mkdir -p .claude/commands
cp .claude/commands-templates/*.md .claude/commands/ 2>/dev/null || \
  cp node_modules/ai-governance-framework/commands/*.md .claude/commands/

# 4. Add CI enforcement
# The wizard already generated the workflow files for your chosen platform.
# Verify they exist:
ls .github/workflows/governance-check.yml  # GitHub Actions
# or the equivalent for your platform

# 5. Keep your original rules file as a reference
mv .claude/rules .claude/rules.migrated  # or RULES.md → RULES.md.migrated
# Once CLAUDE.md is validated, you can delete the migrated file

# 6. Verify the migration
npx ai-governance-init --check
# Or run the health score calculator:
python3 automation/health_score_calculator.py .
```

### What to keep, what to replace

| Fr-e-d artifact | Action | Destination |
|---|---|---|
| `.claude/rules` or `RULES.md` | Replace | Rules move into CLAUDE.md sections |
| Custom rules (naming, security) | Keep content | Copy into `## conventions` and `## security_protocol` |
| N/A (no CI) | Add new | `ci-cd/` workflows for your platform |
| N/A (no session protocol) | Add new | `## session_protocol` in CLAUDE.md |
| N/A (no agents) | Add new | `agents/` definitions as needed |

### Folder mapping

| Fr-e-d concept | This framework equivalent |
|---|---|
| `.claude/rules` | `CLAUDE.md` (repo root) |
| `RULES.md` | `CLAUDE.md` (repo root) |
| Individual rules | Sections within CLAUDE.md (`## conventions`, `## security_protocol`, `## forbidden`) |
| N/A | `commands/` (session commands) |
| N/A | `agents/` (specialized agent definitions) |
| N/A | `ci-cd/` (enforcement workflows) |
| N/A | `templates/` (governance file templates) |
| N/A | `patterns/` (governance patterns) |
| N/A | `docs/` (framework documentation) |

---

## Migration from AI Governor

### What maps directly

AI Governor's policy files map to the enforcement layer of this framework. Policies generated from threat models and user stories correspond to `## security_protocol` in CLAUDE.md and to CI gate definitions in `ci-cd/`. The GitHub Actions enforcement maps directly to `ci-cd/github-actions/`.

### What requires augmentation

AI Governor focuses on security policy generation at the PR level. It does not provide session continuity (no session protocol, no CHANGELOG, no PROJECT_PLAN), multi-agent orchestration, cross-session memory, maturity tracking, or multi-platform CI support. The framework's session protocol and knowledge management layers fill these gaps.

### Step-by-step migration

```bash
# 1. Initialize the framework alongside existing AI Governor setup
npx ai-governance-init
# Choose GitHub Actions as your CI platform (since AI Governor uses GitHub)

# 2. Migrate policy files into CLAUDE.md
# AI Governor generates policies in a policies/ directory or .github/ config.
# Open each policy file and map its rules:
#   - Threat model constraints  → ## security_protocol
#   - Code review rules         → ## conventions
#   - PR requirements           → CI workflow config (ci-cd/github-actions/)

# 3. Preserve AI Governor's threat model output
# If you have generated threat models, keep them as reference documents:
mkdir -p docs/threat-models
cp .github/ai-governor/threat-model-*.md docs/threat-models/

# 4. Replace the AI Governor GitHub Action with the framework's CI gates
# The framework provides governance-check.yml + ai-pr-review.yml which
# cover AI Governor's PR enforcement plus governance file validation.
# Remove or disable the AI Governor workflow:
mv .github/workflows/ai-governor.yml .github/workflows/ai-governor.yml.migrated

# 5. Add session protocol (new capability)
# AI Governor has no session lifecycle. Add it to CLAUDE.md:
# The wizard already generated the session_protocol section.
# Install slash commands:
mkdir -p .claude/commands
cp node_modules/ai-governance-framework/commands/*.md .claude/commands/

# 6. Add multi-platform CI if needed
# AI Governor only supports GitHub. If you also use GitLab or other platforms:
cp ci-cd/gitlab/.gitlab-ci.yml .gitlab-ci.yml  # example for GitLab

# 7. Verify
python3 automation/health_score_calculator.py .
```

### What to keep, what to replace

| AI Governor artifact | Action | Destination |
|---|---|---|
| Generated security policies | Keep content | Merge into `## security_protocol` in CLAUDE.md |
| Threat model documents | Keep as-is | Move to `docs/threat-models/` for reference |
| GitHub Actions workflow | Replace | `ci-cd/github-actions/governance-check.yml` + `ai-pr-review.yml` |
| User story-based policies | Keep content | Map to CLAUDE.md sections and CI gate rules |
| N/A (no session protocol) | Add new | `## session_protocol` in CLAUDE.md |
| N/A (no multi-agent) | Add new | `agents/` definitions as needed |
| N/A (no maturity model) | Add new | Self-assessment via `automation/health_score_calculator.py` |

### Folder mapping

| AI Governor concept | This framework equivalent |
|---|---|
| `.github/ai-governor/` config | `CLAUDE.md` sections + `ci-cd/github-actions/` |
| Generated policy files | `## security_protocol` in CLAUDE.md |
| Threat model output | `docs/threat-models/` (preserved as reference) |
| GitHub Actions enforcement | `ci-cd/github-actions/governance-check.yml` |
| PR-level checks | `ci-cd/github-actions/ai-pr-review.yml` |
| N/A | `commands/` (session commands) |
| N/A | `agents/` (specialized agents) |
| N/A | `templates/` (governance templates) |
| N/A | `patterns/` (governance patterns) |
| N/A | `docs/maturity-model.md` (maturity tracking) |

---

## Migration from claude-code-config

### What maps directly

claude-code-config templates map to `templates/CLAUDE.md` in this framework. If you are using a project-type template (Next.js, FastAPI, etc.), the conventions, naming rules, and project structure sections translate directly into the `## conventions` and `## project_context` sections of this framework's CLAUDE.md.

### What requires augmentation

claude-code-config is a template collection with no runtime behavior. There is no CI enforcement, no agent orchestration, no session protocol, no maturity model, and no self-testing. The templates are starting points; this framework provides the full governance lifecycle around those starting points.

### Step-by-step migration

```bash
# 1. Initialize the framework
npx ai-governance-init
# Select your CI platform and IDE when prompted

# 2. Merge your existing CLAUDE.md content
# Your claude-code-config template is already a CLAUDE.md.
# Open it alongside the framework's generated CLAUDE.md.
# Merge project-specific content:
#   - Project description    → ## project_context
#   - Coding conventions     → ## conventions
#   - Security rules         → ## security_protocol
#   - Stack-specific rules   → ## conventions (under a stack subsection)

# 3. Preserve the original template as reference
cp CLAUDE.md CLAUDE.md.from-claude-code-config
# Then replace with the merged version

# 4. Add session protocol
# claude-code-config templates have no session lifecycle.
# The framework's CLAUDE.md template includes session_protocol.
# Verify it is present in your merged CLAUDE.md:
grep "session_protocol" CLAUDE.md

# 5. Install session commands
mkdir -p .claude/commands
cp node_modules/ai-governance-framework/commands/*.md .claude/commands/

# 6. Add CI enforcement
# The wizard generated workflow files. Verify:
ls .github/workflows/governance-check.yml

# 7. Optionally add AGENTS.md for multi-IDE governance
cp templates/AGENTS.md ./AGENTS.md
# Fill in your project-specific sections

# 8. Verify
python3 automation/health_score_calculator.py .
```

### What to keep, what to replace

| claude-code-config artifact | Action | Destination |
|---|---|---|
| Project-type CLAUDE.md template | Merge content | Sections within the framework's CLAUDE.md |
| Coding conventions | Keep content | `## conventions` in CLAUDE.md |
| Stack-specific patterns | Keep content | `## conventions` in CLAUDE.md |
| Project structure rules | Keep content | `## project_context` in CLAUDE.md |
| N/A (no CI) | Add new | `ci-cd/` workflows |
| N/A (no session protocol) | Add new | `## session_protocol` in CLAUDE.md |
| N/A (no agents) | Add new | `agents/` definitions as needed |
| N/A (no AGENTS.md) | Add new | `AGENTS.md` for multi-IDE governance |

### Folder mapping

| claude-code-config concept | This framework equivalent |
|---|---|
| CLAUDE.md templates (by project type) | `templates/CLAUDE.md` (single template, customized per project) |
| Convention patterns | `## conventions` section in CLAUDE.md |
| Project-specific rules | `## project_context` section in CLAUDE.md |
| Community-curated examples | `examples/` (4 use cases: core-edition, solo-developer, small-team, enterprise) |
| N/A | `commands/` (session commands) |
| N/A | `agents/` (specialized agents) |
| N/A | `ci-cd/` (enforcement workflows) |
| N/A | `patterns/` (governance patterns) |
| N/A | `docs/maturity-model.md` (maturity tracking) |
| N/A | `templates/AGENTS.md` (cross-tool governance) |

---

## Further reading

- [docs/getting-started.md](getting-started.md) — full setup walkthrough for both Core Edition and full framework
- [docs/maturity-model.md](maturity-model.md) — the 6-level maturity model with upgrade paths
- [docs/agents-md-integration.md](agents-md-integration.md) — AGENTS.md cross-tool governance bridge
- [docs/enforcement-hardening.md](enforcement-hardening.md) — from governance by agreement to governance by constraint
