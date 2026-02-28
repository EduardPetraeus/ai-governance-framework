# Context Boundaries

## Name

Context Boundaries — give agents exactly the context they need, no more.

## Problem

AI agents given access to everything use everything. They make connections across unrelated files, suggest changes outside their task scope, and introduce coupling between components that should be independent. Full context is not always better context.

When an agent reads the entire codebase to fix a bug in one connector, it absorbs patterns from every module. Some of those patterns are intentionally different because the modules serve different purposes. The agent "harmonizes" them — applying patterns from the authentication module to the data pipeline, or importing conventions from a deprecated module into new code.

A second problem: context window saturation. When the agent's context is filled with irrelevant files, it has less capacity for deep reasoning about the relevant ones. The quality of analysis on the files that matter decreases as the number of irrelevant files increases.

A third problem: information leakage. An agent with access to the full codebase might reference internal implementation details of module A when working on module B, creating implicit coupling that makes both modules harder to change independently.

## Solution

Define explicit context boundaries for each agent and task. Specify what the agent is allowed to read, what it is allowed to modify, what is relevant to the task, and what project history it needs. Enforce boundaries through session configuration and review.

### Boundary Types

**Read boundary** — what files the agent is allowed to read:
- Source files relevant to the task
- Base classes and interfaces used by the target code
- Project conventions and style guides
- Relevant test files

**Write boundary** — what files the agent is allowed to modify:
- Only the files specified in the [output contract](output-contracts.md)
- Never governance files without explicit permission
- Never files outside the task scope

**Scope boundary** — what parts of the codebase are relevant to this task:
- The module being modified
- Direct dependencies of that module
- Shared utilities used by that module
- Not: other modules at the same level, unrelated features, deprecated code

**Knowledge boundary** — what project history and decisions the agent needs:
- Relevant ADRs (Architecture Decision Records)
- Recent changes to the target module (last 5 commits)
- Active CLAUDE.md rules
- Not: full git history, all ADRs, all documentation

## When to Use

- Multi-module projects where modules should remain independent
- Tasks where the agent has a tendency to expand scope
- Security-sensitive codebases where not all code should be accessible to all agents
- Projects with deprecated code that the agent should not learn from
- When using specialized agents that should focus on their domain (see [agents/](../agents/))

## When NOT to Use

- Small projects where the entire codebase fits easily in context
- Architectural review tasks where the agent genuinely needs to understand cross-cutting concerns
- Initial project setup where understanding the full structure is necessary
- When the task explicitly requires cross-module analysis

## Implementation

### Step 1: Define boundaries per task

For each task, specify the context boundaries before the session begins:

```yaml
task: "add error handling to the Oura connector"
context_boundaries:
  read:
    - src/connectors/oura/sleep.py           # the file being modified
    - src/connectors/base.py                 # base class with error handling patterns
    - src/connectors/oura/config.py          # connector configuration
    - docs/error-handling-guide.md           # project error handling conventions
    - tests/connectors/test_oura_sleep.py    # existing tests for context
  write:
    - src/connectors/oura/sleep.py           # primary modification target
    - tests/connectors/test_oura_sleep.py    # test updates
  explicitly_excluded:
    - src/connectors/fitbit/                 # different connector, not relevant
    - src/connectors/garmin/                 # different connector, not relevant
    - src/core/                              # core module, out of scope
    - src/auth/                              # authentication module, not relevant
    - docs/architecture.md                   # architecture decisions not needed for this task
```

### Step 2: Define boundaries per agent role

Specialized agents should have standing context boundaries that reflect their role:

```yaml
# Code reviewer agent — reads broadly, writes nothing
agent: "code-reviewer"
context_boundaries:
  read: ["src/", "tests/", "docs/", "CLAUDE.md"]
  write: []                                    # reviewers do not modify files
  knowledge: ["ADRs", "recent commits", "open issues"]

# Security reviewer agent — reads everything, writes findings only
agent: "security-reviewer"
context_boundaries:
  read: ["**/*"]                               # security needs full visibility
  write: ["SECURITY_FINDINGS.md"]              # findings report only
  knowledge: ["security ADRs", "CVE databases", "dependency audit"]

# Implementation agent — reads relevant module, writes within scope
agent: "implementation"
context_boundaries:
  read: ["task-specific — defined per session"]
  write: ["task-specific — defined per session"]
  knowledge: ["relevant ADRs", "module history", "conventions"]
```

See [agents/](../agents/) for complete agent definitions with built-in context boundaries.

### Step 3: Communicate boundaries to the agent

Include context boundaries in the session prompt:

```
Task: Add error handling to the Oura connector

Context boundaries:
  READ: src/connectors/oura/sleep.py, src/connectors/base.py, docs/error-handling-guide.md
  WRITE: src/connectors/oura/sleep.py, tests/connectors/test_oura_sleep.py
  EXCLUDED: all other connectors, core module, auth module

If you need to read a file outside the READ boundary, ask before proceeding.
If you need to modify a file outside the WRITE boundary, stop and explain why.
Do not reference patterns from excluded directories.
```

### Step 4: Verify boundary compliance at session end

After the session, verify that the agent stayed within boundaries:

```bash
# Check which files were modified
git diff --name-only HEAD~1

# Verify all modified files are within the write boundary
# Flag any files outside the boundary for review

# Check for references to excluded modules in new code
grep -rn "from src.connectors.fitbit" src/connectors/oura/
grep -rn "from src.core" src/connectors/oura/
# Any matches indicate boundary violation
```

### Step 5: Adjust boundaries based on experience

Track boundary violations and adjust:

```yaml
boundary_log:
  - date: "2026-02-15"
    task: "Oura connector error handling"
    violations:
      - type: "read"
        file: "src/connectors/fitbit/sleep.py"
        reason: "Agent read Fitbit connector to copy error handling pattern"
        action: "Added src/connectors/base.py to read boundary (has canonical error patterns)"
  - date: "2026-02-20"
    task: "Add retry logic"
    violations: none
    note: "Updated read boundary with base class was sufficient"
```

When violations are frequent for a specific file, add that file to the read boundary. When violations are frequent for a specific module, reconsider whether the module boundary is drawn correctly.

## Example

A team has a data pipeline with five connector modules (Oura, Fitbit, Garmin, Apple Health, Google Fit). Each connector follows the same base class pattern but has API-specific implementation details.

**Without context boundaries:** An agent tasked with adding retry logic to the Oura connector reads all five connectors. It notices that the Fitbit connector uses a different retry strategy (linear backoff instead of exponential). Trying to be helpful, it "harmonizes" the retry logic across all connectors, modifying files in all five modules. The Fitbit connector's linear backoff was intentional — the Fitbit API documentation recommends linear backoff for rate-limited requests. The "harmonization" introduces a bug in the Fitbit connector that causes API bans during peak usage.

**With context boundaries:** The agent reads only the Oura connector and the base class. It implements retry logic following the base class pattern (exponential backoff). It does not see the Fitbit connector's different strategy. The Fitbit connector remains correctly configured. The task is completed in scope, without unintended side effects.

The boundary prevented a bug not by catching it, but by preventing the conditions for it. The agent never had the opportunity to make the wrong cross-module connection because it never saw the other module.

## Evidence

Context boundaries apply the principle of least privilege — a foundational concept in security engineering — to AI agent information access. The principle states that an entity should have access only to the information necessary to perform its function.

In software architecture, this principle manifests as encapsulation and information hiding (Parnas, 1972). Modules expose interfaces and hide implementation. Context boundaries apply this to the development process itself: the agent working on module A should interact with module B through its interface, not by reading its implementation.

The practical advantage is twofold. First, bounded agents produce changes with fewer unintended dependencies, making the codebase easier to maintain. Second, bounded agents produce more focused output, because their context window is not diluted with irrelevant information. Teams report that agents with explicit context boundaries produce higher-quality code for their specific task, even though they have less total information available.

## Related Patterns

- [Blast Radius Control](blast-radius-control.md) — limits what the agent writes; context boundaries limit what it reads
- [Output Contracts](output-contracts.md) — contracts define the write boundary for a specific task
- [Human-in-the-Loop](human-in-the-loop.md) — boundary violations trigger human review
- [Progressive Trust](progressive-trust.md) — higher trust levels can allow broader context boundaries
- [Quality Control Patterns](../docs/quality-control-patterns.md) — context boundaries prevent errors by reducing the opportunity space
