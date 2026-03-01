# Core Edition — Minimum Viable Governance

**Make AI a reliable engineer in your repo. Setup: 10 minutes.**

The full framework has 7 layers, 11 agents, and 273 tests. Core Edition has what actually matters for 80% of teams: a constitution the agent reads, a session protocol it follows, three CI checks, and three key patterns. Nothing else.

## Who This Is For

You are using an AI coding assistant (Claude Code, Cursor, Copilot). The agent produces good code in isolation but forgets context between sessions, expands scope silently, and sometimes ships things you did not ask for. You want that fixed without spending a week on governance infrastructure.

Core Edition is for solo developers and teams up to 10. If you have compliance requirements, multiple agent roles, or cross-repo governance needs, start with the full framework instead.

## What You Get

- **CLAUDE.md** — 10 rules the agent reads before every session. Covers what it cannot touch, when to stop and ask, and how to close a session.
- **2 commands** — `/plan-session` starts with a scope check; `/end-session` commits the state log.
- **3 patterns** — blast radius control, human-in-the-loop, output contracts. One page each.
- **3 CI checks** — governance check (CHANGELOG required), security review (no secrets), pre-commit guard.

## 10-Minute Setup

### Step 1: Copy CLAUDE.md to your repo root (2 min)

```bash
cp examples/core-edition/CLAUDE.md ./CLAUDE.md
```

Open it. Fill in the three lines under `## project`. Everything else works as-is.

### Step 2: Commit it (1 min)

```bash
git add CLAUDE.md
git commit -m "chore: add AI governance constitution"
```

### Step 3: Install the commands (2 min)

```bash
mkdir -p .claude/commands
cp examples/core-edition/commands/plan-session.md .claude/commands/
cp examples/core-edition/commands/end-session.md   .claude/commands/
```

### Step 4: Add CI checks (3 min)

Copy the three workflow files into your repo:

```bash
mkdir -p .github/workflows
cp examples/core-edition/ci-cd/governance-check.yml .github/workflows/
cp examples/core-edition/ci-cd/security-review.yml  .github/workflows/
cp examples/core-edition/ci-cd/pre-commit.yml        .github/workflows/
```

Commit and push. The checks run on every PR from this point on.

### Step 5: Run your first governed session (2 min)

Open Claude Code in your project. Type `/plan-session`. The agent reads your project state and confirms scope before writing any code. That is the whole mechanism.

## Upgrade Path

Core Edition is Level 1-2 of the maturity model. When you outgrow it:

- **More structure**: Add `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `CHANGELOG.md` from `templates/`
- **More enforcement**: Swap to the full CI/CD suite in `ci-cd/github-actions/`
- **More agents**: See `agents/` for specialized roles (security reviewer, code reviewer, test writer)
- **Full framework**: See [docs/getting-started.md](../../docs/getting-started.md)

## Files in This Directory

```
core-edition/
├── README.md              — this file
├── CLAUDE.md              — copy to your repo root
├── commands/
│   ├── plan-session.md    — copy to .claude/commands/
│   └── end-session.md     — copy to .claude/commands/
├── patterns/
│   ├── blast-radius-control.md   — read before configuring session limits
│   ├── human-in-the-loop.md      — read before defining checkpoints
│   └── output-contracts.md       — read before your first sprint
└── ci-cd/
    ├── governance-check.yml  — enforces CHANGELOG on every PR
    ├── security-review.yml   — blocks secrets and PII from merging
    └── pre-commit.yml        — catches issues before they reach CI
```
