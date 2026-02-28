# Rollback and Recovery: Disaster Recovery for AI-Generated Changes

## 1. The Speed Problem

A solo developer using AI tools can produce 20–50 commits in a two-hour session. A team of ten developers each doing the same produces hundreds of commits per day. Traditional git-based rollback strategies — designed for a world where a developer produces 5–10 commits per day — break down at this tempo.

Consider the specific ways the speed creates new problems:

**Interleaved commits**: A session might contain commits from both the human developer and the AI agent, mixed together in chronological order. Reverting just the AI commits without touching the human commits becomes a surgical operation.

**Commit granularity mismatch**: AI agents often commit at a fine granularity — one commit per file modified, or one commit per function added. A session that produces 40 commits has 40 potential revert points, none of which may correspond to a "clean" state of the feature.

**Cascade dependencies**: A change in file A causes changes in file B and C. Rolling back A without rolling back B and C leaves the codebase in an inconsistent state that may not even compile.

**CI/CD lag**: Tests run asynchronously. A developer can be 10 commits ahead of the last CI run. If commit 7 introduced a bug that CI would have caught, commits 8–10 are already committed before anyone knows.

**The speed also creates a psychological problem**: at high velocity, developers are less likely to pause and verify before each commit. The discipline of stopping, reading the diff, and confirming correctness is hard to maintain when the agent is producing output faster than the developer can comfortably read it.

This combination means that **rollback strategy must be designed before it is needed**. Improvising a rollback strategy after something has gone wrong is slower and more error-prone than executing a pre-designed one.

---

## 2. What Can Go Wrong

### Cascading Changes

One logical change spreads across multiple files through a cascade of dependent changes. When the original change turns out to be wrong, all dependent changes are also wrong — but they may look correct in isolation.

```
user_profile.py     (changed: adds new field)
    ↓ imports
user_api.py         (changed: exposes new field)
    ↓ tests
test_user_api.py    (changed: tests new field)
    ↓ used in
admin_dashboard.py  (changed: displays new field)
```

If the schema for the new field turns out to be wrong, four files need to be rolled back — not one. And the tests, which were updated to match the incorrect implementation, will pass even after the rollback is incomplete.

### Architectural Drift

Over multiple sessions without careful scope management, the codebase can drift from the architecture defined in `ARCHITECTURE.md`. Each individual change seems reasonable. The cumulative effect is a codebase that no longer matches the mental model, making future AI sessions progressively less accurate.

Architectural drift is hard to roll back because it is not a single commit — it is the accumulated effect of many small deviations. The only recovery is a deliberate governance sync session that identifies and corrects the drift.

### Security Regressions

A session that was focused on performance optimization accidentally changes an authorization check. The change looks correct in isolation — the check still exists, it just has a different conditional logic. The regression is not caught by existing tests because the tests check that the check is present, not that it produces the correct result for all input combinations.

Security regressions are especially dangerous because they are invisible until exploited.

---

## 3. Strategy 1: Atomic Sessions

**Concept**: All AI-generated changes in one session are squash-committed into a single commit when the session ends. Rolling back the session means reverting one commit.

**How to implement:**

```bash
# During the session: commit freely (many small commits)
git commit -m "feat: add oura connector draft"
git commit -m "fix: correct timestamp parsing"
git commit -m "test: add smoke test"
git commit -m "docs: update changelog"

# At session end: squash into one commit
# Option A: squash merge from feature branch
git checkout main
git merge --squash feature/session-2026-03-01
git commit -m "feat(bronze): add oura sleep connector

- Implemented OuraSleepConnector following base pattern
- Added 3 entities to sources_config.yaml
- Smoke tested against mock fixture
- CHANGELOG updated for session 012

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# Rollback: one command
git revert HEAD
```

**Advantage**: Rollback is always `git revert HEAD` — simple, unambiguous, safe.

**Disadvantage**: Detailed session commit history is lost. If the bug is within the session, you cannot bisect to find which step introduced it.

**When to use**: For well-scoped sessions where the session scope is small enough that all-or-nothing rollback is acceptable. Ideal for single-feature or single-layer sessions.

---

## 4. Strategy 2: Feature Branches

**Concept**: All AI work happens on a feature branch. The feature branch is never directly on main. Rollback means deleting the branch or reverting the merge commit.

**How to implement:**

```bash
# Before session: create feature branch
git checkout -b feature/oura-connector-bronze

# Session proceeds on branch
# Many commits, all on feature branch

# PR created, review done, merged as squash merge to main:
git checkout main
git merge --squash feature/oura-connector-bronze
git commit -m "feat(bronze): oura sleep connector (session 012)"

# Rollback the feature:
git revert HEAD  # reverts the squash merge commit

# Or, if the branch is not yet merged:
# Simply close the PR and delete the branch — nothing was ever on main
```

**Advantage**: Clean separation between "in-progress" and "complete" work. Rolling back a merged feature is one revert. Abandoning an in-progress feature is branch deletion.

**Disadvantage**: Requires branch discipline. Developers must not work on main. Requires PR process to be followed consistently.

**When to use**: This is the recommended default strategy for all AI-assisted development. Feature branches are the standard pattern for a reason — they provide rollback, review gates, and clear scope boundaries.

---

## 5. Strategy 3: Checkpoint Tags

**Concept**: Tag the repository state immediately before each session starts. If the session goes wrong, reset to the tag.

**How to implement:**

```bash
# Before session: create checkpoint tag
SESSION_ID=$(date +%Y%m%d-%H%M)
git tag checkpoint/before-session-${SESSION_ID} -m "Pre-session checkpoint: ${SESSION_ID}"

# Session proceeds
# Many commits

# Rollback to checkpoint:
git reset --hard checkpoint/before-session-${SESSION_ID}
# WARNING: this is destructive — discards all commits since the checkpoint
# Use only if the feature branch strategy is not in use

# Alternative: create a revert commit that returns to checkpoint state
git diff checkpoint/before-session-${SESSION_ID}..HEAD | git apply --reverse
git commit -m "revert: undo session ${SESSION_ID}"
```

**Advantage**: Preserves full commit history. Recovery point is always available regardless of branching strategy. Enables `git bisect` within a session.

**Disadvantage**: Requires consistent discipline to tag before every session. Tags accumulate and need periodic cleanup. `reset --hard` is destructive — requires care.

**When to use**: As a complement to the feature branch strategy. Tag before each session within a feature branch as an additional safety net. Especially valuable for long, multi-session features where partial rollback within a feature may be needed.

---

## 6. The Cascade Problem

When a change to file A causes downstream changes in files B, C, and D, rolling back A without addressing B, C, and D leaves the codebase inconsistent.

### Blast Radius Analysis

Before reverting any change, map the blast radius:

```bash
# Step 1: List files changed in the commit or session
git diff HEAD~1 --name-only

# Step 2: For each changed file, find what depends on it
# (language-specific — for Python):
grep -r "from source_connectors.oura.sleep import" . --include="*.py"
grep -r "import oura_sleep" . --include="*.py"

# Step 3: Check if dependent files were also changed
# If yes: they are in the blast radius and must be reverted together
# If no: they will be broken by the revert and need updating

# Step 4: Map the dependency tree and revert in leaf-first order
# (revert the files with no dependents first, then work up to the root)
```

### Using `git bisect` When the Bug's Origin Is Unknown

When something is broken and it is not clear which commit introduced the problem:

```bash
git bisect start
git bisect bad HEAD                    # current state is broken
git bisect good checkpoint/before-session-20260301  # this state worked

# git automatically checks out the midpoint commit
# Test the code
# If broken:
git bisect bad
# If working:
git bisect good
# Repeat until git identifies the specific commit
# git bisect reset to return to HEAD
```

With 50 commits in a session, `git bisect` finds the culprit in roughly 6 steps (log₂(50) ≈ 5.6). Without bisect, manual inspection of 50 commits takes an hour or more.

### How CI/CD Helps Detect Cascades Before Merge

The cascade problem is significantly reduced when CI/CD runs tests on the feature branch before merge:

- If file A's change breaks file B's tests, CI fails before the PR is merged
- The developer sees the cascade during development, not after deployment
- Rollback on the feature branch costs nothing — just fix the cascade before creating the PR

This is the strongest argument for keeping all AI work on feature branches: **CI catches cascades early, when they are cheap to fix, not after they are on main**.

---

## 7. Prevention

The best rollback strategy is not needing to use it.

### Small, Scoped Sessions

A session that changes 3 files has a smaller blast radius than a session that changes 30. Scope discipline is the primary risk control for rollback scenarios.

**The 5-file rule**: A single session should generally not touch more than 5 distinct files. If the natural scope of a task requires touching more than 5 files, decompose the task into multiple sessions.

This is a guideline, not a hard rule. Some legitimate tasks (renaming a database table used throughout a codebase) touch many files and cannot be decomposed. But most sessions that touch 10+ files are doing too much.

### One Layer at a Time

The medallion architecture (or any layered architecture) creates natural session boundaries. A session that builds a bronze connector should not simultaneously update silver transforms and gold views. Mixing architectural layers in one session creates coupling that makes rollback impossible without touching multiple layers.

**Rule**: Sessions should operate within one architectural layer. Cross-layer changes require explicit justification and careful blast radius analysis.

### Run Tests Before Session Ends

The session end protocol should include running the test suite on all changed code. A failing test at session end is far cheaper than a failing production deployment.

```markdown
## on_session_end (in CLAUDE.md)
Before creating the session summary commit:
  1. Run: python -m pytest tests/ -x --timeout=60
  2. If tests fail: do not commit. Fix the failure or document it explicitly.
  3. If tests pass: proceed with session summary commit.
```

---

## 8. Recovery Playbook

When something has gone wrong and a rollback is needed, follow these steps in order:

### Step 1: Detect

Recognize that something is wrong and stop. Do not commit additional changes while diagnosing. Do not continue the session. The first rule of holes: stop digging.

Symptoms that indicate a rollback scenario:
- CI fails and the failure is in code the agent modified
- Production behavior changes unexpectedly after a deploy
- Code review reveals a fundamental design error that requires more than a small fix
- Security review finds a violation that cannot be fixed with a targeted edit

### Step 2: Assess Blast Radius

Run the blast radius analysis from section 6. Identify:
- Which files were changed in the problematic session?
- Which other files depend on those files?
- Which of those dependent files were also changed in the session?
- What is the minimum set of files that must be reverted to reach a consistent state?

### Step 3: Choose Strategy

| Situation | Strategy |
|-----------|---------|
| Session has not been merged to main | Close PR, delete feature branch. Nothing to revert on main. |
| Session was squash-merged to main | `git revert HEAD` on main. One command. |
| Session was merged with individual commits | Revert each commit in reverse chronological order, or use `git revert --no-commit` to batch. |
| Bug is within a session, not the whole session | `git bisect` to find the specific commit, revert that commit only, assess cascade. |
| Architectural drift (multiple sessions) | Governance sync session — identify all drift, create targeted fix commits. Do not batch-revert. |

### Step 4: Execute

For squash merge revert:
```bash
git checkout main
git revert HEAD
git push origin main
```

For multi-commit revert (reverting commits from HEAD back to a checkpoint):
```bash
# Identify the last good commit
git log --oneline | grep checkpoint  # if using checkpoint tags
# or identify by timestamp / commit message

# Revert each commit in reverse order (most recent first)
git revert HASH_N
git revert HASH_N-1
...
git revert HASH_1
```

For branch deletion (pre-merge):
```bash
git checkout main
git branch -d feature/problematic-session
git push origin --delete feature/problematic-session
```

### Step 5: Verify

After reverting:
1. Run the full test suite: `python -m pytest tests/`
2. Run the linter: `ruff check .`
3. Run the security scanner: `gitleaks detect --source=.`
4. Manually verify the behavior that was broken is now correct

Do not declare the recovery complete until all three verifications pass.

### Step 6: Post-Mortem

Document what happened in `docs/SECURITY_LOG.md` or `docs/DECISIONS.md`:

```markdown
## Recovery Event: [date]
- **Type**: Rollback due to [architecture violation / security regression / logic error]
- **Scope**: [which files, which sessions]
- **Detection**: [how was it found — CI, PR review, production incident]
- **Recovery strategy used**: [squash revert / multi-commit revert / branch deletion]
- **Time to recovery**: [minutes]
- **Root cause**: [what caused the problem]
- **Prevention**: [what check or rule was added to prevent recurrence]
```

---

*Related guides: [Security Guide](./security-guide.md) | [AI Code Quality](./ai-code-quality.md) | [Metrics Guide](./metrics-guide.md)*
