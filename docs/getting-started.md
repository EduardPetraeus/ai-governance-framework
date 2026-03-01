# Getting Started

Two paths. Choose based on how much governance you need today.

---

## Path A: Core Edition — 10 minutes

**The right choice if:** you are a solo developer or a team up to 10, you want AI agents that follow scope, don't commit secrets, and leave a written record — without spending a week on infrastructure.

**What you get:** a constitution the agent reads, a session protocol it follows, three CI checks that block the most common failures.

### Step 1: Copy CLAUDE.md to your repo root

```bash
# From inside the framework repo, or after cloning it
cp examples/core-edition/CLAUDE.md ./CLAUDE.md
```

Open it. Fill in the three lines under `## project`. That is the only required customization.

```markdown
## project

name: "customer-data-pipeline"
type: "data pipeline"
stack: "Python, dbt, PostgreSQL"
```

Commit it:

```bash
git add CLAUDE.md
git commit -m "chore: add AI governance constitution"
```

### Step 2: Install the slash commands

```bash
mkdir -p .claude/commands
cp examples/core-edition/commands/plan-session.md .claude/commands/
cp examples/core-edition/commands/end-session.md   .claude/commands/
```

These two commands are the session protocol. `/plan-session` starts every session with a scope check. `/end-session` closes every session with a written record.

### Step 3: Add CI checks

```bash
mkdir -p .github/workflows
cp examples/core-edition/ci-cd/governance-check.yml .github/workflows/
cp examples/core-edition/ci-cd/security-review.yml  .github/workflows/
cp examples/core-edition/ci-cd/pre-commit.yml        .github/workflows/
```

Push to GitHub. From this point on, every PR is checked for:
- CHANGELOG.md updated (governance check)
- No secrets or credentials in the diff (security review)
- CLAUDE.md present and non-empty (pre-commit)

### Step 4: Run your first governed session

Open your project in Claude Code. Type:

```
/plan-session
```

The agent reads your project state and confirms scope before writing any code. When you are done:

```
/end-session
```

The agent lists everything it changed, proposes a CHANGELOG entry, and commits the state update. That is the complete loop.

### What this gives you

- The agent reads before it codes. No more sessions that start with hallucinated context.
- Every session has a written trace. You can reconstruct what happened in session 1, session 20, session 47.
- Scope is explicit. The agent confirms what it will do before writing code. No silent expansion.
- CI blocks the most common failures: missing changelogs, committed secrets, placeholder governance files.

Core Edition covers Level 1-2 of the maturity model. Most solo developers and small teams stay here indefinitely. The [patterns](../examples/core-edition/patterns/) directory has three one-page guides for when you want more structure on specific problems.

---

## Path B: Full Framework — 30-60 minutes

**The right choice if:** you have a team larger than 10, you need compliance audit trails, you want specialized agents for code review and security, or you need cross-repo governance with constitutional inheritance.

**What you get:** the complete 7-layer system: constitution, session protocol, specialized agents, automated enforcement, observability, team governance, and self-updating meta-governance.

### Option 1: Interactive wizard (recommended)

```bash
npx ai-governance-init
```

Requires Node.js 14+. Run inside your project directory. The wizard asks about your project, team size, CI platform, and IDE — then scaffolds the right files automatically. Takes about 5 minutes to run, produces a complete Level 2 setup.

### Option 2: One-liner

```bash
curl -fsSL https://raw.githubusercontent.com/EduardPetraeus/ai-governance-framework/main/install.sh | bash
```

Clones the framework, runs the wizard, cleans up. Requires git and Node.js 14+.

### Option 3: Manual setup

**Prerequisites:**

- Claude Code installed — [claude.ai/code](https://claude.ai/code)
- A git repository
- 30-60 minutes

**Level 1 files (required):**

```bash
FRAMEWORK="path/to/ai-governance-framework"
cp "$FRAMEWORK/templates/CLAUDE.md"        ./CLAUDE.md
cp "$FRAMEWORK/templates/PROJECT_PLAN.md"  ./PROJECT_PLAN.md
cp "$FRAMEWORK/templates/CHANGELOG.md"     ./CHANGELOG.md
git add CLAUDE.md PROJECT_PLAN.md CHANGELOG.md
git commit -m "chore: add Level 1 governance files"
```

**Customize CLAUDE.md:**

Open it and fill in `project_context`. Keep all sections under `session_protocol`, `mandatory_task_reporting`, `forbidden`, and `definition_of_done` untouched until you have run at least three governed sessions.

**Level 2 additions:**

1. `ARCHITECTURE.md` — describe what has been built (not what is planned). Reference it in CLAUDE.md as a file to read at session start.
2. First ADR — document the next significant architectural decision. Copy from `docs/adr/ADR-000-template.md`.
3. `MEMORY.md` — cross-session knowledge: decisions, patterns, lessons learned.
4. Slash commands — copy from `commands/` to `.claude/commands/`. Start with `/plan-session`, `/end-session`, `/security-review`.
5. Specialized agents — define a code agent and a review agent with different scopes. See `agents/`.

**CI/CD enforcement (Level 3):**

Copy from `ci-cd/github-actions/` or your platform's directory (`gitlab/`, `circleci/`, `bitbucket/`, `azure-devops/`). The governance-check and ai-pr-review workflows are the highest-value additions.

**Full walkthrough:**

- [Maturity Model](maturity-model.md) — all 6 levels with upgrade paths and self-assessment checklists
- [Session Protocol](session-protocol.md) — the complete 4-phase lifecycle
- [Architecture](architecture.md) — the 7-layer framework, layer by layer
- [Multi-IDE Support](multi-ide-support.md) — configuration for Cursor, Copilot, Windsurf, Aider
- [Enterprise Playbook](enterprise-playbook.md) — compliance, cross-repo inheritance, role-based access

---

## Which path?

| | Core Edition | Full Framework |
|---|---|---|
| Setup time | 10 minutes | 30-60 minutes |
| Team size | 1-10 | Any |
| Compliance requirements | No | Yes |
| Specialized agents | No | 11 available |
| CI/CD platforms | GitHub Actions only | 5 platforms |
| Multi-IDE | No | Yes (4 IDEs) |
| Constitutional inheritance | No | Yes (org → team → repo) |

Start with Core Edition if in doubt. You can upgrade to the full framework at any point — Core Edition files are a strict subset of the full framework.
