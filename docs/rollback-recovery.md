# Rollback and Disaster Recovery for AI-Generated Changes

> The document you read before something goes wrong. Or the one you wish you had read before it did.

---

## 1. The Speed Problem

A human developer typically produces 3--8 commits per day. A developer working with an AI agent produces 20--50 commits in a single two-hour session. This is not an incremental difference -- it is a categorical change that breaks the assumptions behind traditional rollback strategies.

Traditional post-hoc code review assumes the reviewer can catch up to the developer. At AI-assisted velocity, by the time you notice a problem at commit 12, thirty more commits have been built on top of it. The dependency graph is deeper, the blast radius is wider, and surgical rollback is no longer possible.

The speed also creates four specific failure modes that do not exist in traditional development:

**Interleaved commits.** Sessions mix human and AI commits in chronological order. The human writes a config file, the agent builds the implementation, the human tweaks the config, the agent updates the implementation. Reverting "just the AI commits" is a surgical operation that risks inconsistency.

**Granularity mismatch.** AI agents commit at fine granularity -- one commit per file, one commit per function. A session that produces 40 commits has 40 potential revert points, but none of them may correspond to a clean, consistent snapshot of the feature.

**CI/CD lag.** Tests run asynchronously. The developer can be 15 commits ahead of the last green CI run. If commit 7 introduced a regression, commits 8 through 15 are already committed on top of broken foundations.

**Cognitive saturation.** At high velocity, developers stop reading diffs carefully. The discipline of pausing, reading, and confirming correctness breaks down when the agent is producing output faster than the developer can absorb it. This is the "yes-man" anti-pattern applied to commits: the developer approves without genuinely reviewing.

The consequence is unambiguous: **rollback strategy must be designed proactively, before the first AI session, not improvised after something breaks**.

---

## 2. What Can Go Wrong: A Taxonomy of AI Development Disasters

### Architectural Drift

The agent introduces a pattern that conflicts with the existing architecture. Not deliberately -- it simply does not know the existing pattern exists, or it optimizes for the immediate task rather than the system as a whole.

Over multiple sessions without governance, each small deviation looks reasonable in isolation. The cumulative effect is a codebase that no longer matches anyone's mental model. Architectural drift is particularly dangerous because it is not a single commit you can revert -- it is the accumulated effect of dozens of small deviations across many sessions.

**Example:** Three different connectors use three different error handling patterns. Each works. Together, they make the codebase unpredictable and the error handling story impossible to explain.

### Security Regression

The agent changes an authorization check during a "performance optimization" session. The check still exists, but its conditional logic has changed. Existing tests verify the check is present, not that it produces the correct result for all input combinations. The regression is invisible until exploited.

AI agents have no instinct for "this looks dangerous." They optimize for functionality, not safety. A security regression from an AI agent looks exactly like intentional code -- syntactically perfect, confidently written, and plausibly correct.

### Cascade Failures

One logical change spreads across multiple files through a chain of dependencies:

```
File A: oura_connector.py     (changed: new field added)
    depends on
File B: sources_config.yaml   (changed: references A's interface)
    depends on
File C: run_merge.py           (changed: uses A's output)
    depends on
File D: silver/oura_sleep.sql  (changed: expects A's column names)
    depends on
File E: gold/daily_summary.sql (changed: aggregates from D)
```

Rolling back A without addressing B through E leaves the codebase in an inconsistent state that may not even compile. The blast radius is wider than it appears from the initial diff.

### Scope Explosion

The agent adds "helpful" features beyond the requested scope. You asked for a data connector; the agent also added a caching layer, a retry mechanism, and a monitoring hook. Each addition is reasonable. Together, they triple the blast radius of a potential rollback.

Scope explosion is insidious because the extra work often looks like good engineering. The problem only becomes visible when you need to revert and discover that the "simple connector" is now entangled with three other subsystems.

### The "It Was Fine Yesterday" Problem

Something broke, but it is unclear when. With 50 AI-generated commits per day, the search space for the breaking change is large. Manual inspection of 50 commits is a multi-hour investigation. Without a strategy, you are searching for a needle in a haystack.

---

## 3. Strategy 1: Atomic Sessions

**Concept:** All AI-generated changes in one session are squash-committed into a single commit when the session ends. Rolling back the session means reverting one commit.

```bash
# During the session: commit freely on a feature branch
git checkout -b feature/session-2026-03-01
git commit -m "feat: add oura connector draft"
git commit -m "fix: correct timestamp parsing"
git commit -m "test: add smoke test for oura"
git commit -m "docs: update changelog for session 012"

# At session end: squash merge to main
git checkout main
git merge --squash feature/session-2026-03-01
git commit -m "feat(bronze): add oura sleep connector

- Implemented OuraSleepConnector following BaseConnector pattern
- Added 3 entities to sources_config.yaml
- Smoke tested against mock fixture
- CHANGELOG updated for session 012

Co-Authored-By: Claude <noreply@anthropic.com>"

# Rollback is one command
git revert HEAD
```

**When to use:** For well-scoped sessions where the scope is small enough that all-or-nothing rollback is acceptable. Sessions limited to a single feature or a single architectural layer are ideal candidates.

**Advantage:** Rollback is always `git revert HEAD`. Simple, unambiguous, safe. No blast radius analysis needed because the entire session is one atomic unit.

**Trade-off:** You lose the detailed commit history within the session. If the bug is within the session, you cannot `git bisect` to find which step introduced it. You can only revert the entire session and redo the work.

**Mitigation of the trade-off:** Keep the feature branch alive (do not delete it after squash merge). If you need to investigate within the session, the branch still has the granular history. Configure branch retention with:

```bash
# Keep the branch for 30 days after merge
git config --local branch.feature/*.retain 30d
```

---

## 4. Strategy 2: Feature Branches with Squash Merge

**Concept:** All AI work happens on a feature branch. Never on main. The feature branch is the blast radius container. Rollback means reverting the merge commit on main or simply deleting the branch if it has not been merged.

```bash
# Before session: create feature branch from main
git checkout main && git pull
git checkout -b feature/oura-connector-bronze

# Session proceeds on the branch
# Many commits, all isolated from main
# ...

# PR created, reviewed, CI passes
# Merge to main as squash merge:
git checkout main
git merge --squash feature/oura-connector-bronze
git commit -m "feat(bronze): oura sleep connector (session 012)"

# Rollback option A: revert the merge on main
git revert HEAD

# Rollback option B: if not yet merged, discard the branch entirely
git checkout main
git branch -D feature/oura-connector-bronze
git push origin --delete feature/oura-connector-bronze
```

**When to use:** This is the recommended default strategy for all AI-assisted development. Feature branches provide rollback, review gates, CI validation, and clear scope boundaries. If you adopt only one strategy from this document, adopt this one.

**Advantage:** Clean separation between "in-progress" and "complete" work. Rollback on main is always one revert. Abandoning in-progress work is branch deletion. CI catches cascade problems on the branch before they reach main.

**Trade-off:** Requires branch discipline. Every developer must follow the pattern consistently. Long-lived branches create merge conflicts. Address this with small, frequent sessions rather than large, multi-day branches.

**Step-by-step implementation:**

1. Configure branch protection on main: require PR, require CI pass, require at least one approval.
2. Add a naming convention to `CLAUDE.md`: branches named `feature/session-YYYY-MM-DD-NNN` or `feature/[short-description]`.
3. Add a pre-session step to `CLAUDE.md`: "Create a feature branch before writing code."
4. Add a session-end step: "Create PR from feature branch. Squash merge after CI passes."
5. Configure auto-delete branches after merge in GitHub settings.

---

## 5. Strategy 3: Checkpoint Tags

**Concept:** Tag the repository state immediately before each session starts. The tag is a guaranteed-good recovery point. If anything goes wrong, you can return to the exact pre-session state.

```bash
# Automated pre-session checkpoint (add to session start protocol)
SESSION_ID=$(date +%Y%m%d-%H%M)
git tag "checkpoint/before-session-${SESSION_ID}" \
    -m "Pre-session checkpoint: session ${SESSION_ID}"

# Session proceeds normally (on a feature branch)
# ...

# If session goes badly: return to checkpoint
# Option A: on a feature branch (safe, non-destructive)
git checkout main
git branch -D feature/bad-session

# Option B: if commits were made on main (destructive, use with care)
git reset --hard checkpoint/before-session-${SESSION_ID}
# WARNING: this discards all commits since the tag

# Option C: create a revert commit that returns to checkpoint state (non-destructive)
git diff checkpoint/before-session-${SESSION_ID}..HEAD | git apply --reverse
git commit -m "revert: undo session ${SESSION_ID} — returning to checkpoint"
```

**When to use:** As a complement to the feature branch strategy. Tag before each session within a feature branch as an additional safety net. Valuable for long, multi-session features where partial rollback within a feature may be needed.

**Automating checkpoint creation:** Add a Claude Code hook or a shell alias:

```bash
# In ~/.zshrc or ~/.bashrc
alias ai-session-start='git tag "checkpoint/before-session-$(date +%Y%m%d-%H%M)" -m "Pre-session checkpoint" && echo "Checkpoint created."'

# Or as a git alias
git config --global alias.checkpoint '!git tag "checkpoint/before-session-$(date +%Y%m%d-%H%M)" -m "Pre-session checkpoint"'
```

**Tag cleanup:** Checkpoint tags accumulate. Clean them periodically:

```bash
# Delete checkpoint tags older than 30 days
git tag -l "checkpoint/*" | while read tag; do
    tag_date=$(git log -1 --format=%ai "$tag" 2>/dev/null)
    if [[ $(date -d "$tag_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "${tag_date:0:10}" +%s) -lt $(date -d "30 days ago" +%s 2>/dev/null || date -v-30d +%s) ]]; then
        git tag -d "$tag"
    fi
done
```

---

## 6. Using `git bisect` for Large Sessions

When something is broken and you have 30+ commits in a session, `git bisect` is the fastest path to identifying the breaking commit. It performs a binary search: with 50 commits, it finds the culprit in approximately 6 steps (log2(50) = 5.6). Without bisect, manual inspection takes an hour or more.

```bash
# Start bisect
git bisect start

# Mark the current state as broken
git bisect bad HEAD

# Mark the last known good state (your checkpoint tag)
git bisect good checkpoint/before-session-20260301-1430

# Git checks out the midpoint commit automatically
# Run your verification (tests, manual check, whatever catches the bug)
python -m pytest tests/ -x --timeout=60

# If broken at this midpoint:
git bisect bad

# If working at this midpoint:
git bisect good

# Repeat 4-5 more times. Git narrows down to the exact breaking commit.
# When found, git reports: "<hash> is the first bad commit"

# Return to HEAD
git bisect reset
```

**Automating bisect with a test script:**

If you have a test that reliably catches the bug, automate the bisect entirely:

```bash
git bisect start HEAD checkpoint/before-session-20260301
git bisect run python -m pytest tests/test_oura_connector.py -x --timeout=30
# Git runs the test at each midpoint automatically and identifies the breaking commit
```

**When bisect does not work well:** If the session has commits that do not compile (partial implementations committed mid-task), bisect will hit false negatives. This is an argument for the squash merge strategy -- either revert the whole session or bisect a branch where every commit is a compilable state.

---

## 7. Blast Radius Analysis

Before reverting any change, assess how far the damage extends. Reverting a file that other files depend on creates new breakage. The blast radius analysis prevents making the situation worse.

**Step-by-step procedure:**

```bash
# Step 1: List all files changed in the problematic commit or session
git diff HEAD~1 --name-only
# Or for a range:
git diff checkpoint/before-session-20260301..HEAD --name-only

# Step 2: For each changed file, find what depends on it
# Python imports:
grep -r "from oura_connector import" . --include="*.py"
grep -r "import oura_connector" . --include="*.py"

# SQL references:
grep -r "oura_sleep" . --include="*.sql"

# Config references:
grep -r "oura" . --include="*.yaml" --include="*.yml" --include="*.json"

# Step 3: Build the dependency map
# For each dependent file:
#   - Was it also changed in this session? → It is in the blast radius
#   - Was it NOT changed? → It will break when you revert and needs updating

# Step 4: Determine the minimum revert set
# The minimum revert set is: all changed files + all files that depend
# on changed interfaces that will break after revert

# Step 5: Revert in leaf-first order
# Revert files with no dependents first, then work up the dependency tree
# This prevents intermediate broken states
```

**Quick blast radius estimate:** Count the files changed and the imports. If a session changed 3 files and each file has 2 dependents, the blast radius is approximately 9 files. If a session changed 15 files with complex cross-dependencies, the blast radius may span the entire application. The latter case is an argument for reverting the entire session rather than attempting surgical removal.

---

## 8. The Cascade Problem

When a well-intentioned change in one file breaks five dependent files, you have a cascade failure. This is the most common disaster scenario in AI-assisted development because agents operate locally -- they optimize the file they are editing without fully simulating the impact on distant dependents.

### How Cascades Form

```
Session scope: "Add a new field to the Oura connector"

Commit 1: oura_connector.py — add hrv_score field to output
Commit 2: sources_config.yaml — add hrv_score to entity list
Commit 3: run_merge.py — update merge logic for new field
Commit 4: silver/oura_sleep.sql — add hrv_score to transform
Commit 5: gold/daily_summary.sql — include hrv_score in aggregation

All five commits look correct individually.
But if the hrv_score field name was wrong in commit 1 (hrv_score vs. hrv_value),
the error propagates silently through commits 2-5.
Rolling back commit 1 alone leaves commits 2-5 referencing a field that no longer exists.
```

### Early Detection via CI/CD

The cascade problem is dramatically reduced when CI/CD runs tests on the feature branch before merge:

- If commit 1's change breaks commit 4's SQL tests, CI fails before the PR is merged.
- The developer sees the cascade during development, not after deployment.
- Fixing a cascade on a feature branch is cheap. Fixing one on main is expensive.

This is the strongest argument for feature branches: **CI catches cascades early, when they are cheap to fix**.

### Containment via Feature Branches

Each feature branch is a blast radius container. A cascade that spans 5 files within a feature branch affects nothing on main. The developer can fix the cascade, abandon the branch, or ask for help -- all without impacting other team members.

### Recovery from a Cascade on Main

If a cascade reaches main (because CI did not catch it, or because the developer merged without waiting for CI):

1. **Do not attempt surgical revert.** Reverting individual commits in a cascade risks creating new inconsistencies.
2. **Revert the entire merge commit** that brought the cascade onto main: `git revert -m 1 <merge-commit-hash>`
3. **Fix the cascade on the feature branch** where it is isolated.
4. **Re-merge** after the fix is confirmed by CI.

---

## 9. Prevention: The 5-File Rule and One-Layer Discipline

The best rollback strategy is not needing one.

### The 5-File Rule

**A single session should not touch more than 5 distinct files.** If the natural scope of a task requires touching more than 5 files, decompose the task into multiple sessions.

Why 5? It is the number at which blast radius analysis remains tractable. With 3 changed files and 2 dependents each, you can reason about the impact in your head. With 15 changed files and complex cross-dependencies, you cannot.

This is a guideline, not a hard rule. Some legitimate tasks (renaming a database column used throughout a codebase) touch many files. But most sessions that touch 10+ files are doing too much at once.

**Enforce it in CLAUDE.md:**

```markdown
## scope_management
- Maximum 5 files per session unless explicitly authorized
- If a task naturally requires more than 5 files, decompose into sub-tasks
- Cross-layer changes (e.g., bronze + silver in the same session) require
  explicit user confirmation before proceeding
```

### One Layer at a Time

Any layered architecture -- medallion (bronze/silver/gold), MVC, clean architecture -- creates natural session boundaries. A session that builds a bronze connector should not simultaneously update silver transforms. Mixing layers in one session creates coupling that makes rollback impossible without touching multiple layers.

**Rule:** Sessions operate within one architectural layer. Cross-layer sessions require explicit justification and careful blast radius planning.

### Run Tests Before Session End

The session-end protocol must include running the test suite on all changed code. A failing test at session end is orders of magnitude cheaper than a failing production deployment.

```markdown
## on_session_end (in CLAUDE.md)
Before creating the session summary commit:
  1. Run: python -m pytest tests/ -x --timeout=60
  2. If any test fails: do not commit. Fix the failure or document it explicitly
     as a known issue with a linked task in PROJECT_PLAN.md.
  3. Run: ruff check . (linting)
  4. Run: gitleaks detect --source=. (security scan)
  5. Only if all three pass: proceed with session summary commit.
```

---

## 10. Recovery Playbook

When something has gone wrong, follow these six steps in order. Do not skip steps. Do not improvise.

### Step 1: Detect

Stop. Do not commit additional changes. Do not continue the session. The first rule of recovery: stop making the situation more complex.

**Symptoms that indicate a rollback is needed:**

| Symptom | Likely Cause | Urgency |
|---------|-------------|---------|
| CI fails on code the agent modified | Logic error or cascade failure | Medium -- fix before merge |
| Production behavior changes after deploy | Security regression or logic error | High -- revert immediately |
| Code review reveals fundamental design error | Architectural drift or scope explosion | Medium -- revert PR |
| Security scan finds a violation | Secret exposure or PII leak | Critical -- revert and rotate credentials |
| Agent introduced incompatible pattern | Architectural drift | Low -- fix forward or revert session |

### Step 2: Assess Blast Radius

Run the blast radius analysis from section 7. Answer these questions:

1. Which files were changed in the problematic session or commit?
2. Which other files import, reference, or depend on the changed files?
3. Were those dependent files also changed in the session?
4. What is the minimum set of files that must be reverted to reach a consistent state?

Document the answers before proceeding. Do not revert based on intuition.

### Step 3: Choose Strategy

| Situation | Strategy | Command |
|-----------|----------|---------|
| Session has not been merged to main | Close the PR, delete the branch | `git branch -D feature/bad-session` |
| Session was squash-merged to main | Revert the single merge commit | `git revert HEAD` |
| Session was merged with individual commits | Revert the merge commit | `git revert -m 1 <merge-hash>` |
| Bug is within a session (not the whole session) | `git bisect` to find the commit, revert it, assess cascade | See section 6 |
| Architectural drift (across multiple sessions) | Governance sync session: identify all drift, fix incrementally | Do not batch-revert |
| Secret was committed and pushed | Revoke credential immediately, rewrite history | See security incident response below |

### Step 4: Execute

**For squash merge revert (most common):**

```bash
git checkout main
git pull origin main
git revert HEAD
# Edit the revert commit message to explain why:
# "revert: undo session 012 oura connector — schema incompatibility with silver layer"
git push origin main
```

**For multi-commit revert:**

```bash
# Identify the merge commit
git log --oneline --merges | head -5

# Revert the merge (mainline parent is -m 1)
git revert -m 1 <merge-commit-hash>
git push origin main
```

**For pre-merge branch deletion:**

```bash
git checkout main
git branch -D feature/problematic-session
git push origin --delete feature/problematic-session
```

**For security incidents (secret committed and pushed):**

```bash
# 1. IMMEDIATELY revoke the exposed credential (do this first, before anything else)
# 2. Rewrite git history to remove the secret
git filter-branch --force --index-filter \
    "git rm --cached --ignore-unmatch path/to/secret-file" \
    --prune-empty --tag-name-filter cat -- --all
# Or use BFG Repo-Cleaner (faster):
bfg --delete-files secret-file.env
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force --all
# 3. Rotate ALL secrets that were exposed, not just the one found
# 4. Document the incident in DECISIONS.md
```

### Step 5: Verify

After reverting, confirm the codebase is healthy:

```bash
# Run the full test suite
python -m pytest tests/ -x --timeout=120

# Run linting
ruff check .

# Run security scanning
gitleaks detect --source=.

# Verify the specific behavior that was broken is now correct
# (this is manual — you need to test the exact scenario that revealed the problem)
```

Do not declare recovery complete until all verifications pass. If any verification fails, the revert was incomplete -- return to step 2 and reassess blast radius.

### Step 6: Post-Mortem

Document what happened. The post-mortem prevents recurrence and improves the governance framework.

```markdown
## Recovery Event — YYYY-MM-DD

**Type:** [Architecture violation | Security regression | Logic error | Cascade failure]
**Scope:** [Which files, which sessions, which branches]
**Detection:** [How was it found: CI failure, PR review, production incident, manual test]
**Recovery strategy used:** [Squash revert | Multi-commit revert | Branch deletion | History rewrite]
**Time to detection:** [How long between the breaking change and discovery]
**Time to recovery:** [How long between discovery and verified fix]
**Root cause:** [What caused the problem — be specific]
**Prevention:** [What check, rule, or gate was added to prevent recurrence]
**Governance gap:** [Was this a gap in CLAUDE.md, CI/CD, or the session protocol? If so, how was it closed?]
```

Add this entry to `DECISIONS.md` or a dedicated `docs/incidents/` directory.

**The most important part of the post-mortem:** the prevention step. Every incident should result in a new deterministic check (CI gate, pre-commit hook, CLAUDE.md rule) that catches the same class of problem automatically next time. Probabilistic prevention ("we'll be more careful") is not prevention.

---

## Decision Table: Quick Reference

| I need to... | Do this |
|---|---|
| Undo an entire session that was squash-merged | `git revert HEAD` |
| Abandon a session before it reaches main | Delete the feature branch |
| Find which commit broke something in a 50-commit session | `git bisect` with a test script |
| Understand how many files a revert will affect | Blast radius analysis (section 7) |
| Prevent cascade failures | Feature branches + CI/CD before merge |
| Reduce rollback complexity for future sessions | 5-file rule, one-layer-at-a-time |
| Handle a committed secret | Revoke immediately, rewrite history, rotate all secrets |
| Practice rollback before you need it | Schedule a 30-minute rollback drill (break something on purpose, practice recovery) |

---

*Related guides: [Security Guide](./security-guide.md) | [AI Code Quality](./ai-code-quality.md) | [Maturity Model](./maturity-model.md) | [Getting Started](./getting-started.md)*
