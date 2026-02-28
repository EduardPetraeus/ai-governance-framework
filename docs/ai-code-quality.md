# AI Code Quality: Characteristics, Risks, and Review Strategy

## 1. The Quality Profile

AI-generated code has a distinctive quality signature. It passes the glance test and fails at the edges.

When a developer looks at a function written by a capable AI model, they see:
- Correct syntax in the target language
- Consistent formatting and indentation
- Logical variable names that follow the project's conventions
- Appropriate comments and docstrings
- A structure that matches familiar patterns from production codebases

These signals — clean syntax, professional formatting, logical naming — are the same signals that indicate high-quality human code. Decades of code review experience have trained developers to use these visual cues as proxies for correctness. For AI-generated code, they indicate *stylistic consistency*, not *semantic correctness*. The proxy fails.

The underlying quality profile is different from human code in specific, predictable ways:

- **Fewer surface errors:** typos, syntax mistakes, obvious naming inconsistencies, missing imports — these are rare in AI-generated code. The model has seen enough correct code to avoid these.
- **More semantic errors:** logic that is plausible but incorrect for the specific domain. The code does *a* thing correctly, but not *the* thing that was needed.
- **More edge case failures:** code that works for the happy path and fails silently at boundaries — empty lists, null values, concurrent requests, network timeouts, malformed input.
- **Hallucinated specifics:** methods, API calls, or library functions that do not exist, or that exist with different signatures or behavior than what was generated.
- **Implicit assumptions:** code that assumes state, configuration, or data availability that may not exist in the actual runtime environment. These assumptions are never documented because the model did not know they were assumptions.
- **Plausible-but-wrong patterns:** code that implements a recognizable algorithm or design pattern correctly *in general*, but incorrectly *for the specific business requirement*. This is the most dangerous category because the code reads as correct to anyone who does not deeply understand the domain requirement.

Understanding this profile is the foundation of an effective AI code review strategy. You review differently when you know where the errors hide.

---

## 2. Error Taxonomy

### Fewer: Syntax and Surface Errors

AI models rarely make syntax errors in languages they have been trained on extensively. Python, SQL, YAML, JavaScript, TypeScript — these will parse, compile, and format correctly in virtually all cases. The age of spending 20 minutes finding a missing semicolon, an off-by-one indentation error, or a typo in a variable name is effectively over for AI-assisted development.

**Implication for review:** Do not spend review time on syntax, formatting, or naming in AI-generated code. These are handled by the model (during generation) and the linter (during CI). Reviewing for these is wasted human attention — attention that should be directed at the dimensions where AI code actually fails.

### More: Semantic Errors

Semantic errors are code that is syntactically correct but logically wrong for the specific context. They pass linting, pass type checking, and often pass unit tests — but produce incorrect behavior in production or for specific inputs.

**Example — date calculation:**
```python
# Prompt: "Calculate the number of business days between two dates"
# AI generated:
def business_days_between(start_date: str, end_date: str) -> int:
    from datetime import datetime, timedelta
    fmt = "%Y-%m-%d"
    start = datetime.strptime(start_date, fmt)
    end = datetime.strptime(end_date, fmt)
    days = 0
    current = start
    while current < end:
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            days += 1
        current += timedelta(days=1)
    return days
```

This function is syntactically correct. It handles weekday detection correctly. It will pass most unit tests. It will fail if:
- Either date string uses a different format (ISO with time component, European DD/MM/YYYY)
- The developer passes `datetime` objects instead of strings (type error at runtime, not at import)
- The business requires inclusive end date counting (this implementation is exclusive)
- The business operates in a jurisdiction with different weekend days (Friday-Saturday in some Middle Eastern countries)
- Public holidays need to be excluded (the function does not know about holidays)

The AI matched the pattern "business days between dates" correctly. It did not match the *specific business requirements* that motivated the task. The function is plausible, professional-looking, and wrong.

### More: Plausible-but-Wrong Logic

This is the most dangerous error category. Code that implements a recognizable algorithm correctly *in the abstract* but incorrectly *for the specific use case*.

**Example — rolling average:**
```python
# Intended: calculate 7-day rolling average of heart rate, aligned to each day
# AI generated:
def rolling_average(readings: list[float], window: int = 7) -> list[float]:
    return [
        sum(readings[i:i+window]) / window
        for i in range(len(readings) - window + 1)
    ]
```

The rolling average implementation is mathematically correct. But:
- The output has length `len(readings) - window + 1`, not `len(readings)`. The first 6 days are silently dropped — no warning, no error, no `None` values. Downstream code that assumes one output per input will misalign data.
- No handling for `len(readings) < window` — returns an empty list with no warning. A dashboard consuming this function will show no data instead of partial data.
- The function computes a backward-looking average aligned to the *start* of the window. If the business requirement is an average *ending* at each day (the common case for health metrics), the alignment is wrong. Every value is shifted by 6 days.
- Division by `window` even when the slice is shorter than `window` (though this cannot happen with the current range logic, it indicates the function was not designed with edge cases in mind)

This code will pass a review unless the reviewer thinks carefully about output length, alignment semantics, and the specific business use case. The implementation *looks* correct precisely because the algorithm *is* correct in the abstract — the error is in the fit between algorithm and business requirement.

### Occurring: Hallucinated Methods and APIs

AI models occasionally generate calls to methods or API endpoints that do not exist, or that exist but with different signatures than what was generated.

**Example — pandas hallucination:**
```python
import pandas as pd

# AI generated — this method does not exist
df = df.fillna_smart(method="forward", limit=3, axis=0)

# Correct pandas equivalent
df = df.fillna(method="ffill", limit=3, axis=0)
```

**Example — API version mismatch:**
```python
import anthropic

# AI generated — uses deprecated/non-existent parameter
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.7,  # May not exist or may behave differently than expected
    system_prompt="You are a helpful assistant",  # Wrong parameter name
    messages=[{"role": "user", "content": "Hello"}]
)
```

These errors are easier to catch because they fail at runtime with clear error messages (`AttributeError`, `TypeError`, `unexpected keyword argument`). They are more common with:
- Newer libraries (training data may not include latest API versions)
- Niche libraries (fewer training examples)
- Libraries with similar names (model conflates `pandas` and `polars`, or `requests` and `httpx`)

---

## 3. The Confidence Problem

AI presents all code with equal confidence regardless of correctness.

A human developer writing code knows when they are uncertain. They leave comments: `# TODO: verify this handles negative values`. They write PR notes: "I am not sure about the empty list case." They have metacognitive awareness — they can tell when they are in familiar territory versus when they are guessing.

AI models do not have this awareness in any practically useful way. The model that produces a correct sorting algorithm and the model that produces a subtly incorrect authentication bypass will format both with the same clean style, comment both with the same professional tone, and present both with the same authoritative structure.

**Why this is dangerous:**

1. The standard visual signals for code quality (clean formatting, consistent naming, logical structure) are present in both correct and incorrect AI code. The signal-to-noise ratio of visual review approaches zero.

2. Reviewers trained on human code have developed intuitions that fail for AI code. A well-formatted function written by a senior developer is usually correct. A well-formatted function written by AI may not be. The intuition "this looks professional, so it is probably correct" leads directly to rubber-stamping.

3. AI explanations of its own code are unreliable. When asked "is this correct?", the model may explain what the code is *supposed to do* rather than what it *actually does*, because the explanation is generated from the same pattern-matching process that generated the code. An incorrect function and its incorrect explanation are generated from the same source — they will be consistent with each other but inconsistent with reality.

4. AI does not flag uncertainty. A human might say "I think this handles the edge case but I'm not confident." An AI will generate the edge case handling and present it with the same confidence whether it is correct or subtly wrong. The absence of uncertainty signals is itself a signal — but only if the reviewer knows to look for their absence.

**How to compensate:**

- Do not use code appearance as an indicator of correctness when reviewing AI output. Judge correctness only by: reading the logic carefully, running specific test cases (especially edge cases), and checking against acceptance criteria.
- Treat AI code as "confident but unverified" by default. Verify explicitly.
- When an AI explains its own code, verify the explanation against the actual code behavior — do not trust the explanation as evidence of correctness.
- Allocate more review time per line for AI-generated code than for code written by a trusted senior developer. The visual quality savings (no syntax errors to find) should be redirected to logical review (more edge cases to verify).

---

## 4. The Maintenance Problem

Code that nobody understands because nobody wrote it.

AI-generated code is often syntactically clean and logically structured. The developer who accepted it into the codebase reviewed it, approved it, and merged it. But there is a meaningful and measurable difference between *reviewing* code and *understanding* code. The reviewer may have confirmed that the code matches acceptance criteria and passes tests without developing a working mental model of how the code works internally — what design decisions were made, why specific patterns were chosen, what the implicit assumptions are.

Six months later, when a bug is reported or a feature needs extension, the code is "orphaned." No one on the team has the knowledge that is normally carried by the person who wrote the code. The git history shows it was generated by an AI and approved by a developer. The developer no longer remembers the details. The AI that generated it does not exist as a persistent entity that can be asked questions.

### The Orphaned Code Risk

Orphaned code has specific, compounding risks:

- **Bug fixes become guesswork.** Without understanding the design intent, developers fix symptoms rather than causes. The fix introduces a new edge case that the original code handled correctly but the fixer did not know about.
- **Extensions introduce inconsistencies.** New code added to the orphaned module follows different patterns because the developer does not know the original design intent. Over time, the module becomes a patchwork of conflicting patterns.
- **The code becomes sacred.** Developers are afraid to touch code they do not understand, so it accumulates technical debt. Dependencies age. Patterns become outdated. Nobody refactors because nobody is confident they can do so without breaking something.
- **Knowledge debt compounds.** Each session that generates code without deep understanding adds to the knowledge debt. After a year, significant portions of the codebase may be orphaned.

### Prevention

The rule is simple and non-negotiable: **if you cannot explain what a piece of code does and why it is implemented the way it is, do not commit it.**

"The AI wrote it" is not an explanation. "It implements a sliding window average aligned to the end of each window, using a list comprehension for performance, with explicit handling for the case where the input is shorter than the window" is an explanation.

If the developer cannot produce the second kind of explanation, they have three options:
1. Ask the AI to explain the code line by line until they understand it
2. Request a simpler implementation they can understand, even if it is less "elegant"
3. Implement it themselves with AI assistance (the AI helps, but the developer drives the design decisions)

**AI-generated code needs MORE comments, not fewer.** The standard argument for "self-documenting code" assumes the reader is a developer who thinks like a developer. For AI-generated code, the reader is a developer who did not write it, did not design it, and may not share the AI's unstated assumptions. Comments that explain *why* (not just *what*) are essential for long-term maintainability.

---

## 5. Review Strategy

### What to Skip

Do not spend time reviewing AI code for dimensions that automation handles reliably:

- **Formatting and indentation:** the linter catches this
- **Spelling errors in variable names:** the linter catches this
- **Obvious import issues:** Python will throw immediately at import time
- **Style convention violations:** pre-commit hooks enforce these
- **Type annotation formatting:** mypy or pyright handles this

These are important quality dimensions, but they do not require human attention in an AI-assisted workflow. Redirecting this attention to logical review is the productivity gain of AI-aware code review.

### What to Review Intensively

Concentrate review attention on the dimensions where AI code actually fails — the ones that automation cannot reliably check:

**Business logic alignment:**
- Does this code do what the ticket/task *actually* specifies? Or does it do something similar that would pass a naive test but fail the real-world use case?
- Is the domain logic (business rules, calculation definitions, data semantics) correctly implemented? Would a domain expert reviewing this code recognize it as correct?
- Are there domain-specific edge cases that the AI could not have known about (holiday calendars, jurisdiction-specific rules, customer-specific configurations)?

**Logic correctness at boundaries:**
- What happens when the input is empty? Null? Zero? Negative?
- What happens at the exact boundary (the limit itself, not comfortably inside it)?
- What happens with input larger than expected? What happens with maximum values?
- What happens when a network call fails? Times out? Returns an unexpected status code?
- What happens under concurrent access?

**Security assumptions:**
- Does the code assume inputs are validated upstream? *Are they?*
- Does authentication logic handle all failure cases — not just successful authentication, but expired tokens, revoked tokens, malformed tokens, missing tokens?
- Are there data paths that bypass security controls?
- Does error handling reveal internal details (stack traces, file paths, SQL queries, internal hostnames)?

**Implicit dependencies:**
- Does the code assume the existence of state, configuration, or data that may not always be present?
- Are there ordering dependencies? Does this code assume another function ran first?
- Does it assume a specific database state? A specific API version?

**Hallucinated specifics:**
- Run the code. Verify that all method calls actually exist with the expected signatures.
- Check external dependency usage against the actual library documentation — not against what the AI says the documentation says.

---

## 6. Test Strategy

AI-generated code changes what needs to be tested, not just how much.

### Test More: Integration Behavior

Integration tests exercise code behavior across real boundaries — real database calls, real API responses (or realistic mocks), real file system interactions. AI-generated code is most likely to be wrong at these boundaries, because the model's training data may not include the specific behavior of the exact system being integrated.

An integration test that verifies the bronze table is populated correctly after the connector runs catches a wider class of errors than a unit test that mocks the API response. The unit test confirms the code processes a mock correctly. The integration test confirms the code works with the actual system.

**Priority:** Every AI-generated connector, transform, or integration point should have at least one integration test before merging. The test should use realistic fixtures, not trivial ones.

### Test More: Property-Based Testing

Property-based testing generates many input values automatically and checks that the code maintains stated properties across all of them. This is exceptionally effective for catching edge cases that AI code commonly misses.

```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
def test_rolling_average_output_length(readings):
    """Output length should equal input length for full-coverage rolling average."""
    result = rolling_average(readings, window=7)
    if len(readings) < 7:
        # Policy decision: what should happen with short inputs?
        # This test forces you to define the behavior explicitly.
        assert len(result) == 0 or len(result) == len(readings)
    else:
        assert len(result) == len(readings) - 6  # Discovers the length discrepancy

@given(st.lists(st.floats(min_value=0, max_value=300, allow_nan=False), min_size=7))
def test_rolling_average_values_in_range(readings):
    """Each rolling average should be between min and max of its window."""
    result = rolling_average(readings, window=7)
    for i, avg in enumerate(result):
        window = readings[i:i+7]
        assert min(window) <= avg <= max(window)
```

Property-based tests immediately discover the length discrepancy, alignment issues, and boundary behaviors in the rolling average example from section 2. They are a systematic antidote to the "looks correct for the test I wrote" problem.

### Test More: Acceptance Tests from Domain Experts

AI-generated unit tests test what the code *does*. Acceptance tests test what the code *should do* — as defined by the business requirement, not by the code's behavior.

The difference is critical: an AI will generate a test for `rolling_average` that confirms the function produces the expected output for a specific input. That test will pass, even if the function's behavior is wrong for the business use case. An acceptance test written by the domain expert says: "For a patient with these 14 days of heart rate data, the 7-day rolling average on day 10 should be 72 bpm." If the function's alignment is off by 6 days, this test catches it.

### Test Less: Happy-Path Unit Tests Written by AI

AI models write unit tests well — for the cases they considered. If you ask an agent to write tests for its own code, it will generate tests that cover the cases it thought about when writing the code. These tests will pass. They will not cover the cases the agent did not consider — which are precisely the cases where bugs hide.

Do not rely on AI-generated unit tests as evidence of correctness. Use them as a starting point and supplement them with:
- Edge case tests written manually (empty input, null, boundary values, concurrent access)
- Property-based tests (automated edge case discovery)
- Acceptance tests from domain experts (business logic verification)

**The tests the AI generates and the tests that would actually catch the bugs are different sets.** The overlap is smaller than it looks.

---

## 7. Ownership Model

The developer who prompted the code and committed it is responsible for it. This is the ownership model, and it is not negotiable.

"I did not write it — the AI did" is not a valid response to a production incident. The developer who committed the code:

- Made the decision to use AI assistance for this task
- Defined the scope and constraints (or failed to define them)
- Reviewed the output before committing (or failed to review it)
- Accepted the code into the codebase by clicking "approve"
- Is the person who should be able to explain what the code does and why

This model exists not to distribute blame but to ensure that every line of code in the repository has a human owner who understands it and is accountable for its behavior.

**In practice:**

- Do not commit AI-generated code you have not read and understood. If the code is too complex to understand, ask for a simpler version or implement it yourself with AI assistance.
- Do not approve AI-generated code in a PR you have not read carefully. A 500-line PR requires proportional review time — not a 30-second glance.
- If code is committed and later found to be wrong, the committer is responsible for the fix. This is true regardless of whether AI generated the original.
- If you cannot explain what a function does to a colleague in plain language, you do not understand it well enough to own it. Go back and understand it before committing.

The ownership model has a secondary benefit: it creates a natural brake on AI-generated code volume. A developer who knows they must understand and own every line will not accept 2,000 lines of generated code without review. The ownership requirement prevents the "AI generated it, so it must be fine" abdication of responsibility.

---

## 8. The 10-Item PR Review Checklist

Use this checklist for every PR that contains AI-generated code. Check each item explicitly — do not assume it is fine because the code looks professional.

```
AI Code Review Checklist

LOGIC AND CORRECTNESS:
  [ ] 1. What happens when input is empty, null, or zero? Tested and verified.
  [ ] 2. What happens at boundary conditions (exact limits, not comfortably inside)?
         Tested and verified.
  [ ] 3. Business logic matches the actual requirement — not just a plausible
         interpretation. Verified against the task description or ticket.

DEPENDENCIES AND INTERFACES:
  [ ] 4. All method calls, API calls, and library functions actually exist with the
         claimed signatures. Verified against documentation (not against AI's claims).
  [ ] 5. The code's interface (inputs, outputs, side effects, exceptions) matches what
         callers expect. No silent behavior changes to existing interfaces.

SECURITY:
  [ ] 6. No hardcoded credentials, configuration values, or internal hostnames.
         Scanner has run AND manual review confirms.
  [ ] 7. Authorization logic handles all failure cases: missing auth, expired tokens,
         valid auth but wrong permissions. Not just the happy path.

STATE AND ASSUMPTIONS:
  [ ] 8. No implicit state assumptions that may not hold at runtime (database state,
         config availability, environment variables, network access).
         Assumptions identified and documented in comments.

OWNERSHIP:
  [ ] 9. The developer who is committing this code can explain what it does, why it is
         implemented this way, and what it does NOT handle (known limitations).

TESTS:
  [ ] 10. At least one test covers an edge case (empty input, null, boundary value).
          AI-generated tests have been supplemented with manually written edge case tests
          or property-based tests. There is at least one integration test if the code
          touches an external system.
```

Print this checklist. Post it next to your monitor. Use it for every AI-generated PR until it becomes automatic. The checklist exists specifically to counteract the confidence problem — it forces explicit verification of dimensions that AI code is most likely to get wrong.

---

## 9. The Refactoring Trap

AI-generated code is visually clean but structurally unfamiliar. This combination creates a powerful temptation to refactor.

**The trap, version 1:**
1. Developer reviews AI-generated code
2. Code is correct but uses patterns the developer would not have chosen
3. Developer rewrites it in a style they are more comfortable with
4. The rewrite introduces bugs the original code did not have — because the developer changed behavior while trying to change only style

**The trap, version 2:**
1. AI generates a working solution
2. AI or developer notices the code could be "cleaner" or "more elegant"
3. Refactoring session begins
4. The refactored version subtly changes behavior that the existing tests do not cover
5. Tests pass. Behavior is different. Bug surfaces in production two weeks later.

**The trap, version 3:**
1. Developer refactors AI code to "understand it better"
2. The refactored version is actually simpler and clearer
3. But the refactoring took 2 hours and the original code was correct
4. Net productivity: negative. The 2 hours produced no new value.

### When to Refactor

Refactor AI-generated code when:
- It is actively difficult to read due to naming or structure choices that impede understanding
- It will need to be extended in the near future, and its current structure makes extension error-prone
- It contains a known-bad pattern (e.g., it mixes concerns that should be separated for testability)
- You can write a comprehensive test suite *before* refactoring that will catch behavioral regressions

### When to Leave It

Leave AI-generated code untouched when:
- It is correct and all tests pass
- The only motivation is style preference ("I would have written it differently")
- The code is in a stable part of the codebase that rarely changes
- You cannot write the test that would catch a regression introduced by the refactoring
- The refactoring time exceeds the time the original code will save over its lifetime

**The rule of thumb:** if you cannot write the regression test that would catch a behavioral change introduced by the refactoring, do not refactor. The refactoring adds risk without a safety net.

**The deeper principle:** Refactoring AI code to make it "yours" is a legitimate urge — you want to understand and own the code. But the productive response is not always to rewrite it. Sometimes the productive response is to add comments, write comprehensive tests, and document the design decisions — making the code understandable without changing it.

---

*Related guides: [Prompt Engineering](./prompt-engineering.md) | [Security Guide](./security-guide.md) | [Metrics Guide](./metrics-guide.md) | [Compliance Guide](./compliance-guide.md)*
