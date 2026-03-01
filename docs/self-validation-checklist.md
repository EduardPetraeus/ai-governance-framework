# Self-Validation Checklist

A structured checklist for validating governance health across six dimensions. Run this
against any repo using the AI governance framework. Each check is binary — pass or fail —
with clear criteria and failure actions.

Use `commands/validate.md` to run automated checks, or work through this manually at the
start of a sprint or quarterly review.

---

## 1. Constitution Health

The CLAUDE.md is the foundation. If it drifts or goes stale, every downstream check
is unreliable.

| Check | Pass Criterion |
|---|---|
| CLAUDE.md exists at repo root | File present |
| `project_context` section present | Section heading and non-empty content |
| `conventions` section present | Naming rules, file structure documented |
| `mandatory_session_protocol` section present | Phase 1–3 defined with concrete steps |
| `security_protocol` section present | No-commit rules explicitly listed |
| No placeholder text | No `N/A`, no `TODO`, no `...` in non-template files |
| Last modified < 90 days OR used in most recent sprint | File modification date or CHANGELOG reference |
| All cross-references resolve | Every relative link in CLAUDE.md points to an existing file |

**Failure action:** Update or complete the section. If CLAUDE.md is older than 90 days
with no sprint activity, run `/upgrade` to check for framework changes. Verify
cross-references with `commands/validate.md`.

---

## 2. Session Hygiene

Sessions leave artifacts. Without them, the next session starts blind.

| Check | Pass Criterion |
|---|---|
| CHANGELOG.md exists at repo root | File present |
| CHANGELOG.md has 3+ entries | At least 3 `## Session` or `## v` headers |
| Most recent entry < 30 days old (if work is active) | Date in last entry header within 30 days |
| MEMORY.md exists | Cross-session knowledge base file present |
| MEMORY.md contains at least 1 confirmed pattern | Non-empty content with documented pattern |
| PROJECT_PLAN.md exists with current sprint | Active sprint section present and non-empty |
| No uncommitted governance decisions | Git status clean, or decision logged in ADR |

**Failure action:** Create missing files from `templates/`. Run `/end-session` to generate
a CHANGELOG entry for the current session. If MEMORY.md is missing, create it from
`templates/MEMORY.md` and populate the patterns discovered in previous sessions.

---

## 3. Enforcement Active

Governance without enforcement is documentation. The gates must be on.

| Check | Pass Criterion |
|---|---|
| `.pre-commit-config.yaml` exists | File present at repo root |
| Pre-commit hooks include secrets detection | Hook for secrets scan or security review present |
| CI workflow exists | `.github/workflows/` (or CI equivalent) has at least 1 file |
| AI review workflow active | Workflow file references `anthropic` or `claude` |
| Governance check CI exists | Workflow enforces CHANGELOG or governance file updates on PRs |
| Security reviewer runs on PRs | `ai-pr-review.yml` or equivalent deployed |

**Failure action:** Copy the relevant workflow from `ci-cd/` to `.github/workflows/`.
Run `scripts/deploy_commands.sh` to install slash commands. Add the pre-commit config
from `ci-cd/pre-commit/.pre-commit-config.yaml`.

---

## 4. Knowledge Freshness

Stale knowledge misleads agents. ADRs that are never reviewed become dangerous context.

| Check | Pass Criterion |
|---|---|
| At least 1 ADR in `docs/adr/` | At least 1 ADR file present |
| No ADR older than 1 year without review annotation | Last modified < 365 days, or `reviewed:` field in ADR |
| MEMORY.md updated within last 30 days (if work is active) | File modification date |
| Deprecated patterns are removed or marked with migration notes | No unlabelled deprecated sections |
| Model version references in CLAUDE.md match current team default | Version strings current and intentional |
| `docs/` directory reflects actual file inventory | No references to files that no longer exist |
| Self-validation checklist exists | `docs/self-validation-checklist.md` present |

**Failure action:** Run `/research` to surface new best practices. Mark stale ADRs as
"Under Review" and schedule a decision renewal. Update MEMORY.md with patterns confirmed
in recent sessions. See [knowledge-lifecycle.md](knowledge-lifecycle.md) for decay thresholds.

---

## 5. Agent Accountability

Unconstrained agents drift toward maximum scope. Accountability requires explicit limits.

| Check | Pass Criterion |
|---|---|
| All agent definitions specify write access constraints | `write_access:` field or equivalent present in each agent file |
| Agent blast radius is defined | `max_files_per_session` or equivalent documented |
| At least 1 agent requires human-in-the-loop approval | `requires_human_approval:` or equivalent |
| Session logs exist for the last 3 sessions | CHANGELOG entries or session artifacts present |
| No agent grants unconstrained file system access | No agent write path is `/` or `**` without qualifiers |
| Audit log path is defined | `audit_log:` field in at least 1 agent, or audit log referenced in CLAUDE.md |
| Kill switch procedure is documented | `patterns/kill-switch.md` is present and referenced in CLAUDE.md or commands |
| AGENTS.md portable governance bridge exists | `AGENTS.md` at repo root for cross-tool governance |

**Failure action:** Review agent definitions against `agents/` templates. Add
`write_access:` constraints to any agent missing them. Create `AGENTS.md` from
`templates/AGENTS.md` for cross-tool coverage. Implement kill switch from
`patterns/kill-switch.md`.

---

## 6. Friction Check

If governance overhead exceeds its value, people bypass it. Measure and manage friction
explicitly.

| Check | Pass Criterion |
|---|---|
| Session start time under 5 minutes | Phase 1 (read state, confirm scope) completes within 5 min |
| Session close adds under 3 minutes | Phase 3 (CHANGELOG update) completes within 3 min |
| No CI check has failed 3+ times on unrelated governance issues | Review CI failure history for false positives |
| Governance file count is documented and justified | File count visible in README or `commands/health-check.md` |
| Last `/audit` ran within 90 days | Audit entry in CHANGELOG or `v030_build_logs/audit.log` |
| Framework version is current or intentionally pinned | `docs/self-updating-framework.md` has been reviewed |
| No governance bypasses in last sprint | No `--no-verify` commits, no manual CHANGELOG skips in git log |

**Failure action:** Run `python3 automation/health_score_calculator.py .` to get a
quantified score. If more than 20% of session time is spent on governance overhead,
open a governance issue to identify and remove the bottleneck. See
[friction-budget.md](../patterns/friction-budget.md) for the pattern.

---

## Running This Checklist

**Automated score (covers most checks):**

```bash
python3 automation/health_score_calculator.py .
```

**Full audit in Claude Code:**

```
/audit
```

**Manual review cadence:**

| Cadence | Sections |
|---|---|
| Sprint start | Constitution health, Enforcement active |
| Sprint end | Session hygiene, Knowledge freshness |
| Quarterly | All six sections + Agent accountability deep review |

**Score interpretation (of 30 binary checks above):**

| Checks passing | Status |
|---|---|
| 0–9 | Critical — governance is not functioning |
| 10–17 | Partial — enforcement active, knowledge and accountability gaps remain |
| 18–23 | Operational — all dimensions covered, optimize friction |
| 24–27 | Measured — self-optimizing governance in place |
| 28–30 | Reference implementation |

---

## Related

- [Automated score](../automation/health_score_calculator.py)
- [Maturity model](maturity-model.md)
- [Friction budget pattern](../patterns/friction-budget.md)
- [Knowledge decay pattern](../patterns/knowledge-decay.md)
- [Kill switch pattern](../patterns/kill-switch.md)
- [Session protocol](session-protocol.md)
