# ADR-003: Automation-Bias Defense Pattern Hardcodes 85% Confidence Ceiling

## Status

Accepted

## Date

2026-02-28

## Context

Automation bias is a documented cognitive phenomenon: when an automated system produces a confident validation result, human reviewers reduce their own scrutiny in proportion to the stated confidence. A code review agent that reports 97% confidence causes human reviewers to allocate their attention to the remaining 3% — treating the agent's output as a baseline of correctness rather than a draft requiring verification.

This effect is compounded when multiple AI validation layers operate in sequence. Consider a pipeline where a code review agent (95% confident), a security agent (92% confident), and a QA agent (90% confident) all pass a pull request. A human reviewer, seeing three independent AI validations, may reason that the probability of an undetected issue is approximately (1 - 0.95) × (1 - 0.92) × (1 - 0.90) = 0.4% — effectively zero. This reasoning is mathematically incorrect because the agents are not independent. They share training data, exhibit correlated failure modes, may be the same base model with different system prompts, and their confidence scores are not calibrated probabilities. The actual residual risk is much higher than the compounded confidence math implies.

The framework's automation-bias-defense pattern was designed to address this. The pattern requires AI agents to structure their output not as "I found no issues (confidence: X%)" but as "I verified A, B, and C. I did not verify D, E, and F. Confidence capped at 85%." The explicit enumeration of what was not verified forces the agent's report to surface gaps rather than hide them behind a high confidence number.

The ceiling value was debated. 70% was proposed as maximally conservative but was rejected: confidence scores below 75% trigger a cognitive heuristic in human reviewers that classifies the agent output as low-quality, leading teams to disable or ignore the agent entirely — which eliminates the protection. 90% was proposed as close to current model capability but was rejected: at 90%, human reviewers cognitively classify the output as "probably correct, verify edge cases only," which is the automation bias behavior the pattern is designed to prevent. 85% was selected because it sits in the range where human reviewers maintain active engagement — treating the output as a strong draft that still requires real scrutiny — without producing the noise that causes teams to disable the pattern.

Making the ceiling configurable was explicitly considered and rejected. The governance value of the ceiling comes from its universality. If projects can configure the ceiling, the ceiling will be raised. A team that has deployed a capable AI model and trusts its output will set the ceiling to 92%. After six months without incidents, they will raise it to 95%. After twelve months, they will question why there is a ceiling at all. This is the correct local reasoning and the wrong systemic outcome: the automation bias protection disappears precisely when confidence in AI systems is highest, which is when the bias is strongest.

## Decision

The automation-bias-defense pattern hardcodes 85% as the maximum confidence score any AI agent governed by this framework may report in a validation context. This ceiling applies regardless of model, prompt, task domain, or organizational configuration. The ceiling is not exposed as a configurable parameter in any template, agent definition, command, or workflow included in this framework.

## Rationale

The specific value (85%) matters less than the property (non-negotiable). An 87% ceiling that cannot be changed is better governance than an 85% ceiling that can be raised to 95% by editing a YAML file. The decision to make it non-configurable is the core decision; the value is secondary.

The 85% value is not arbitrary: it sits above the range where AI output is dismissed as low-quality (roughly below 75%) and below the range where human reviewers shift from active to passive engagement (roughly above 90%). These thresholds are based on documented patterns in automation bias research and on practical observation: CI systems that produce too many low-confidence warnings are disabled; CI systems that produce consistent high-confidence passes are ignored.

The framing the pattern requires — "I verified X, did not verify Y, confidence capped at 85%" — is as important as the ceiling itself. It forces the agent to produce a gap enumeration, not just a confidence score. The ceiling without the gap enumeration would still allow "I found no issues, confidence capped at 85%," which reduces the automation bias only partially. The combination of a ceiling and mandatory gap enumeration produces a qualitatively different kind of AI validation output.

## Consequences

### Positive

- Human reviewers cannot rationalize reduced scrutiny on the basis of AI confidence scores. The ceiling is visible in every validation report and cannot be overridden.
- The framework produces consistent validation output across all projects. A team reading a validation report from any AI agent governed by this framework knows that "confidence capped at 85%" is a structural property, not a model capability signal.
- AI validation reports must enumerate what was not checked. Gaps become first-class output of the validation process. Over time, recurring gaps in AI validation become visible signals for improving agent prompts or adding human review checkpoints.
- The non-configurability simplifies framework governance. There are no per-project ceiling values to audit, compare, or enforce in the meta-governance layer.

### Negative

- Projects that have invested in high-quality AI validation pipelines and have empirical evidence of low defect escape rates cannot express higher trust through the confidence mechanism. Their agents will always report 85% maximum, even if model performance justifies higher reported confidence.
- The 85% value is based on reasoning and observed patterns, not on a controlled empirical study. There is no peer-reviewed evidence that 85% is the correct threshold for maintaining active human engagement. A different threshold might be equally or more effective.
- The non-configurability is a governance opinion embedded in tooling. Teams that disagree with this opinion cannot adopt the automation-bias-defense pattern without forking the framework or modifying the template. Modification is possible, but it is explicitly contrary to the framework's intent.

### Neutral

- All AI validation output in the framework uses consistent language: "Verified: [list]. Not verified: [list]. Confidence capped at 85% per automation-bias-defense policy." This language appears in agent definitions, command templates, and CI workflow comments. It becomes recognizable to developers who work across multiple projects using the framework.
- The 85% ceiling applies only in validation contexts — when an AI agent is producing a pass/fail or confidence-scored assessment of code, security, or compliance. It does not apply to generative tasks (writing code, drafting documentation) where confidence is not a meaningful output.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Configurable per-project threshold | Will be raised over time as teams gain confidence in their AI tooling. A configurable threshold is a threshold that trends toward 100%, eliminating the automation bias protection in every project that experiences prolonged periods without AI-caused incidents. |
| No confidence ceiling; surface all findings and let humans decide | Does not address the accumulation problem. When three AI agents all report findings-complete status, human reviewers apply compounded-probability reasoning even without explicit confidence scores. The ceiling forces a visible, non-negotiable signal that the agent's output is incomplete by design. |
| 70% ceiling | Produces output that human reviewers classify as low-quality AI validation. Teams disable the pattern or route around it. A protection that gets disabled provides no protection. |
| 90% ceiling | Insufficient separation from "AI probably got this right." At 90%, human reviewers shift from active verification to approval mode. The automation bias is not disrupted; it is slightly moderated. |
| Dynamic ceiling based on task type | Adds configuration complexity that creates exceptions. An exception-laden constraint is a constraint that will be argued away. A single universal value is enforceable. |

## Implementation Notes

The ceiling is enforced in two places: the agent definition templates in `agents/` include a system prompt instruction that explicitly caps self-reported confidence at 85%, and the command definitions in `commands/` include a post-processing instruction that strips any confidence value above 85% from structured output before it is written to a pull request comment or CI log.

The value 85 appears as a named constant (`CONFIDENCE_CEILING = 85`) in `automation/governance_dashboard.py`, which validates that agent output in CI logs does not exceed the ceiling. Changing the constant requires modifying the source file — it is not exposed in any configuration file, environment variable, or framework template option.

## Review Date

2028-02-28
