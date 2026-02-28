# AI Code Quality: Characteristics, Risks, and Review Strategy

## 1. The Quality Profile

AI-generated code has a recognizable quality profile. It passes the glance test. It fails the edge case test.

When a developer looks at a function written by a capable AI model, they see:
- Correct Python / SQL / YAML syntax
- Consistent formatting and indentation
- Logical variable names
- Appropriate comments
- A structure that matches familiar patterns

These signals typically indicate high-quality human code. For AI-generated code, they indicate *stylistic consistency*, not *semantic correctness*.

The underlying quality profile is different from human code in ways that are not visible at a glance:
- **Fewer surface errors**: typos, syntax mistakes, obvious naming inconsistencies are rare
- **More semantic errors**: logic that is plausible but incorrect for the specific domain
- **More edge case failures**: code that works in the happy path and fails silently at boundaries
- **Hallucinated specifics**: methods or APIs that do not exist, or that exist but with different signatures
- **Implicit assumptions**: code that assumes state that may not exist in the actual runtime environment

Understanding this profile is the foundation of an effective AI code review strategy.

---

## 2. Error Types

### Fewer: Syntax and Surface Errors

AI models rarely make syntax errors in languages they have been trained on extensively. Python, SQL, YAML, JavaScript — these will compile, parse, and format correctly. The age of spending 20 minutes finding a missing semicolon or an off-by-one indentation error is effectively over for AI-assisted development.

**Implication**: Do not review AI code for syntax errors. They will be caught by the linter. Reviewing for syntax is wasted human attention.

### More: Semantic Errors

Semantic errors are code that is syntactically correct but logically wrong for the specific context. These are the errors that pass linting, pass type checking, and often pass unit tests — but produce incorrect behavior in production.

**Example:**
```python
# Prompt asked for: "Calculate days between two dates"
# AI generated:
def days_between(start_date: str, end_date: str) -> int:
    from datetime import datetime
    fmt = "%Y-%m-%d"
    return (datetime.strptime(end_date, fmt) - datetime.strptime(start_date, fmt)).days
```

This function is syntactically correct. It passes obvious unit tests. It will fail if either date string uses a different format, if the developer passes `datetime` objects instead of strings, or if the business requires exclusive vs. inclusive end date counting. The AI matched the pattern "days between dates" correctly; it did not match the specific business logic requirements.

### More: Plausible-but-Wrong Logic

This is the most dangerous category. Code that implements a recognizable algorithm or pattern — but incorrectly for the specific domain.

**Example:**
```python
# Intended: calculate the 7-day rolling average of heart rate
# AI generated:
def rolling_average(readings: list[float], window: int = 7) -> list[float]:
    return [sum(readings[i:i+window]) / window for i in range(len(readings) - window + 1)]
```

The function produces a rolling average, and the implementation is mathematically correct. But:
- The output length is `len(readings) - window + 1`, not `len(readings)` — the first 6 days are silently dropped
- No handling for when `len(readings) < window` — the function returns an empty list with no warning
- The actual use case requires a forward-looking average aligned to the end of the window, not the beginning

This code will pass a review unless the reviewer thinks carefully about edge cases and alignment semantics. The implementation looks correct precisely because the algorithm is correct — the error is in the fit between algorithm and business requirement.

### Occurring: Hallucinated Methods and APIs

AI models occasionally generate calls to methods or APIs that do not exist, or that exist but with different signatures than what was generated. This happens when the model's training data contains deprecated or fictional API surfaces.

**Example:**
```python
import pandas as pd

# AI generated — pd.DataFrame.fillna_smart() does not exist
df.fillna_smart(method="forward", limit=3, axis=0)
```

This will fail immediately with an `AttributeError`. These errors are easy to catch because they fail at runtime. They are more common with newer APIs, niche libraries, or when the model conflates the API surfaces of multiple similar libraries.

---

## 3. The Confidence Problem

AI presents all code with equal confidence regardless of correctness.

A developer writing code knows when they are uncertain. They might leave a comment: `# TODO: verify this handles negative values`. They might write a note in the PR: "I am not sure about the edge case when the list is empty." They have the metacognitive awareness to recognize when they are in unfamiliar territory.

AI models do not have this awareness in a practical sense. The model that produces a correct sorting algorithm and the model that produces a subtly incorrect one will format both with the same clean style, comment both with the same professional tone, and present both with the same authoritative structure.

**This is dangerous because:**

1. The standard visual signals that indicate high-quality code (clean formatting, consistent naming, logical structure) are present in both correct and incorrect AI code
2. Reviewers trained on human code develop intuitions that fail for AI code — a well-formatted function by a senior developer is usually correct; a well-formatted function by an AI may not be
3. AI explanations of its own code are unreliable: the model may explain what the code is *supposed to do* rather than what it *actually does*, because the explanation is generated from the same pattern-matching as the code

**How to account for this:**

Do not use code appearance as an indicator of code correctness when reviewing AI output. Judge correctness only by: reading the logic carefully, running specific test cases, and checking against acceptance criteria.

Treat AI code as "confident but unverified" by default, and verify explicitly.

---

## 4. The Maintenance Problem

Code that nobody understands because nobody wrote it.

AI-generated code is often syntactically clean and logically structured. The developer who accepted it into the codebase reviewed it, approved it, and merged it. But there is a meaningful difference between reviewing code and understanding it. The reviewer may have confirmed that the code matches the acceptance criteria and passes the tests without developing a working mental model of how the code works.

Six months later, when a bug is reported or a feature needs to be extended, the code is "orphaned" — no one on the team has the knowledge that is usually carried by the person who wrote the code. The git history shows it was written by an AI and approved by a developer. The developer no longer remembers the details.

### The Orphaned Code Risk

Orphaned code has specific risks:
- **Bug fixes become guesswork**: without understanding how the code works, developers make changes that fix the symptom but not the cause
- **Extensions introduce inconsistencies**: new code added to the orphaned module follows different patterns, because the developer does not know the original design intent
- **The code becomes sacred**: developers are afraid to touch it because they do not understand it, so it accumulates technical debt

### Prevention

The rule is simple: if you cannot explain what a piece of code does and why it is implemented the way it is, do not commit it. This applies to AI-generated code as much as to code copied from Stack Overflow.

"The AI wrote it" is not an explanation. "It implements a sliding window average aligned to the end of each window, using a list comprehension for performance, with explicit handling for the case where the window is larger than the data" is an explanation.

If the developer cannot produce the second kind of explanation, they should either: (a) ask the AI to explain the code until they understand it, or (b) request a simpler implementation they can understand, or (c) implement it themselves with AI assistance rather than accepting the AI's implementation wholesale.

---

## 5. Review Strategy

### What to Skip

Do not spend time reviewing AI code for:
- Formatting and indentation (the linter catches this)
- Spelling errors in variable names (the linter catches this)
- Obvious import issues (Python will throw immediately)
- Style convention violations (the pre-commit hook catches this)

These are important quality dimensions, but they do not require human attention in an AI-assisted workflow. Automation handles them faster and more reliably.

### What to Review Intensively

Concentrate review attention on dimensions that automation cannot reliably check:

**Logic correctness at boundaries:**
- What happens when the input is empty, null, zero, or negative?
- What happens when the input is at the boundary (exactly at the limit, not comfortably inside it)?
- What happens when the input is larger than expected?

**Business logic alignment:**
- Does this code do what the business requirement actually specifies, or does it do something similar that would pass a naive test?
- Is the domain logic (business rules, calculation definitions, data semantics) correctly implemented?
- Would a domain expert reviewing this code recognize it as correct?

**Security assumptions:**
- Does the code assume inputs are validated upstream? Are they?
- Does authentication and authorization logic handle all failure cases, or just the happy path?
- Are there data paths that bypass the security controls?

**Implicit dependencies:**
- Does the code assume the existence of state, configuration, or data that may not always be present?
- Are there race conditions or ordering dependencies?

**Hallucinated specifics:**
- Run the code. Check that all method calls and API calls actually exist with the expected signatures.
- Verify against the actual library documentation for any external dependency usage.

---

## 6. Test Strategy

AI-generated code changes what needs to be tested, not just how much.

### Test More Of: Integration Behavior

Integration tests exercise the code's behavior across real boundaries — real database calls, real API responses, real file system interactions. AI-generated code is most likely to be wrong at these boundaries, because the model's training may not have included the specific behavior of the exact system being integrated.

An integration test that verifies the bronze table is populated correctly after the connector runs catches a wider class of errors than a unit test that mocks the API response.

**Priority**: Every AI-generated connector, transform, or integration point should have at least one integration test before being merged.

### Test More Of: Property-Based Testing

Property-based testing generates many input values automatically and checks that the code maintains stated properties across all of them. This is effective for catching edge cases that AI code commonly misses.

```python
# Using hypothesis
from hypothesis import given, strategies as st

@given(st.lists(st.floats(allow_nan=False), min_size=0))
def test_rolling_average_output_length(readings):
    result = rolling_average(readings, window=7)
    if len(readings) < 7:
        assert result == []  # or whatever the correct behavior is for short lists
    else:
        assert len(result) == len(readings)  # if we want full-length output
```

This test will immediately discover the length discrepancy in the rolling average example from section 2.

### Test Less Of: Happy-Path Unit Tests

AI models write unit tests well. If you ask an agent to write tests for its own code, it will generate tests that cover the cases it considered when writing the code. These tests will pass. They will not catch the cases the agent did not consider.

Do not rely on AI-generated unit tests as evidence of code correctness. Use them as a starting point and add edge case tests manually.

**Do not skip testing entirely because the AI generated tests.** The tests the AI generates and the tests that would actually catch the bugs are different sets.

---

## 7. Ownership Model

The developer who prompted the code and committed it is responsible for it. This is the ownership model, and it is not negotiable.

"I did not write it — the AI did" is not a valid response to a production incident. The developer who committed the code:
- Made the decision to use AI assistance for this task
- Reviewed the output before committing
- Accepted the code into the codebase
- Is the person who can explain (or should be able to explain) what the code does

This model exists not to distribute blame but to ensure that every line of code in the repository has a human owner who understands it and is accountable for its behavior.

**In practice:**

- Do not commit AI-generated code you have not read and understood
- Do not approve AI-generated code in a PR you have not read carefully
- If code is committed and later found to be wrong, the committer is responsible for the fix — regardless of whether AI generated the original

---

## 8. Code Review Checklist

Use this checklist for every PR that contains AI-generated code. Check each item explicitly — do not assume it is fine because the code looks good.

```
AI Code Review Checklist

Logic and correctness:
  [ ] What happens when the input is empty, null, or zero? Verified.
  [ ] What happens at the boundary conditions? Verified.
  [ ] Business logic matches the actual requirement (not just a plausible interpretation). Verified.

Dependencies and interfaces:
  [ ] All method calls and API calls actually exist with the claimed signatures. Verified.
  [ ] All imports are available (no hallucinated libraries or methods). Verified.
  [ ] The code's interface (inputs, outputs, side effects) matches what callers expect. Verified.

Security:
  [ ] No hardcoded credentials or configuration values. Verified.
  [ ] Authorization logic handles all failure cases, not just success. Verified.
  [ ] No sensitive data logged or transmitted unexpectedly. Verified.

State and assumptions:
  [ ] No implicit state assumptions that may not hold. Identified and verified.
  [ ] No race conditions or ordering dependencies. Verified.

Ownership:
  [ ] The developer who committed this code can explain what it does and why. Confirmed.
  [ ] The developer can explain what this code does NOT handle (known limitations). Confirmed.

Tests:
  [ ] At least one test covers an edge case (empty list, null, boundary). Exists.
  [ ] There is at least one integration test if this code touches an external system. Exists.
  [ ] AI-generated unit tests have been supplemented with manually written edge case tests. Confirmed.
```

---

## 9. The Refactoring Trap

AI-generated code is visually clean but structurally unfamiliar. This combination creates a strong temptation to refactor.

The refactoring trap looks like this:
1. Developer reviews AI-generated code
2. Code is correct but uses patterns the developer would not have chosen
3. Developer is tempted to rewrite it in a style they are more comfortable with
4. The rewrite introduces bugs the original code did not have

Alternatively:
1. AI generates a working solution
2. AI or developer notices the code could be "cleaner"
3. Refactoring session begins
4. The refactored version subtly changes behavior that tests did not cover

### When to Refactor

Refactor AI-generated code when:
- It is actively difficult to read due to naming or structure choices
- It will need to be extended in the near future, and its current structure makes extension error-prone
- It contains a known-bad pattern (e.g., it mixes concerns that should be separated)

### When to Leave It

Leave AI-generated code untouched when:
- It is correct and tests pass
- The only motivation is style preference
- The code is in a stable part of the codebase that rarely changes
- You cannot explain exactly what behavior the refactored version would preserve

**The rule of thumb**: if you cannot write the test that would catch a regression introduced by the refactoring, do not refactor. The refactoring adds risk without a safety net.

---

*Related guides: [Prompt Engineering](./prompt-engineering.md) | [Security Guide](./security-guide.md) | [Rollback and Recovery](./rollback-recovery.md) | [Compliance Guide](./compliance-guide.md)*
