# ADR-001: Constitutional Inheritance Supports Both URL References and Local File Paths

## Status

Accepted

## Date

2026-02-28

## Context

The framework supports a constitutional inheritance hierarchy: an organization defines a CLAUDE.org.md, teams define CLAUDE.team.md files that inherit from it, and individual repositories define CLAUDE.md files that inherit from their team constitution. The `inherits_from:` key is the mechanism that wires these layers together.

Two incompatible topologies exist in practice. In a monorepo, all CLAUDE files live in the same repository. A repo-level CLAUDE.md can reference its parent with a relative file path (`inherits_from: ../governance/CLAUDE.team.md`) because the file is guaranteed to be present on disk during validation. In a multi-repo organization, each team or repository is a separate git repository. A file path reference cannot cross repository boundaries — `../CLAUDE.org.md` would point outside the repository checkout and fail in any CI environment.

The validator (`inherits_from_validator.py`) must resolve the parent constitution at validation time to check that mandatory sections are inherited and not overridden without justification. This means the validator must be able to fetch the parent document, either from disk or from a network location.

URL references (e.g., `inherits_from: https://raw.githubusercontent.com/acme-corp/governance/main/CLAUDE.org.md`) work across repo boundaries and require no special checkout configuration. They are also naturally version-controlled at the source: changing the organization-level constitution takes effect in all child repositories on the next CI run without requiring pull requests in each child repo.

However, URL references introduce a network dependency. CI pipelines running in air-gapped environments, behind strict egress firewalls, or with no outbound HTTPS to GitHub raw content cannot resolve URL references. Adding `requests` as a required dependency solely for URL fetching would create a pip install requirement in CI for every repository using the framework — a bootstrapping problem for governance tooling that is supposed to work immediately.

## Decision

The `inherits_from_validator.py` script supports both URL references and local file paths. Local file paths (relative or absolute) are read directly from disk using standard `pathlib` operations. URL references (any value beginning with `https://`) are fetched using `urllib.request` from the Python 3.10+ standard library. No external dependency is required for either mode. URL references are the recommended approach for cross-repository inheritance. Local file paths are the default for same-repository inheritance in monorepos.

## Rationale

Neither mode alone covers all organizational topologies. Restricting to local paths would make the framework unusable for multi-repo organizations, which represent the majority of medium and large engineering teams. Restricting to URLs would make the framework unnecessarily complex for solo developers and monorepos where the constitution is two directories up the file tree.

`urllib.request` handles HTTPS fetching without adding any dependency to the project. The standard library constraint is non-negotiable for core governance scripts (see ADR-002). A governance tool that requires `pip install requests` before it can validate governance cannot be trusted to be present when it is needed most — in a fresh CI runner or a newly onboarded developer's environment.

URL references mapping to GitHub raw content URLs are an established pattern in the ecosystem (e.g., `curl https://raw.githubusercontent.com/...` in shell scripts). Organizations already publish governance standards this way. The framework aligns with existing practice rather than inventing a custom distribution mechanism.

## Consequences

### Positive

- The framework functions correctly across monorepos, multi-repo organizations, and hybrid topologies without requiring any architectural changes to the repositories being governed.
- Zero additional dependencies. The validator runs with `python3 inherits_from_validator.py` in any environment with Python 3.10+.
- URL-referenced constitutions are version-controlled at the source. Rolling out an updated organizational policy requires one commit to the org-level repository, not pull requests in every child repository.
- Validation errors reference the specific URL or path that failed to resolve, making misconfigured inheritance immediately debuggeable.

### Negative

- URL references add a network dependency at validation time. A CI runner without outbound HTTPS access to the host serving the parent constitution will fail validation, even if the CLAUDE.md content itself is correct.
- Private organizational constitutions hosted on private GitHub repositories require authentication. The current validator does not support authentication tokens for URL fetching. Teams with private governance repositories must either use local path references (via git submodule or similar) or publish their constitution to a location accessible without authentication.
- Two modes increase the configuration surface area. A misconfigured `inherits_from:` value that looks like a file path but was intended as a URL (or vice versa) produces a confusing error.

### Neutral

- The validator detects the mode based on whether the `inherits_from:` value begins with `https://`. This is a simple heuristic, not a schema-validated field. Teams using HTTP (not HTTPS) URLs will get a file-not-found error, not a helpful URL-mode error. HTTPS is the only supported URL scheme.
- Documentation for the framework must cover both modes and explain which to use in which topology. This is two paragraphs of documentation, not a significant burden, but it is ongoing maintenance.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Local file paths only | Cannot cross repository boundaries. Multi-repo organizations would have no supported inheritance mechanism, making the constitutional hierarchy feature inapplicable to the most common enterprise topology. |
| URL references only | Fails in air-gapped environments and adds unnecessary complexity for monorepos where the parent constitution is on disk. Forces solo developers and monorepo teams through a URL indirection that provides no benefit. |
| Git submodules for constitution distribution | Solves the cross-repo access problem but requires all governed repositories to add a git submodule, configure `.gitmodules`, and ensure submodule initialization in CI. This is significant onboarding friction for governance tooling meant to be adopted incrementally. |
| Custom registry or package manager for constitutions | Over-engineering. A governance constitution is a markdown file, not a versioned software package. Adding a registry adds infrastructure and a single point of failure. |

## Implementation Notes

The validator checks the `inherits_from:` value using `str.startswith("https://")`. If true, it uses `urllib.request.urlopen()` with a 10-second timeout and reads the response as UTF-8 text. If false, it resolves the value as a `pathlib.Path` relative to the location of the child CLAUDE.md file. Both code paths produce the same internal representation (a string of markdown text) for the inheritance check logic.

Network failures in URL mode produce a warning, not a hard failure, when the `--lenient` flag is passed. This allows CI pipelines to pass during network outages without disabling the validator entirely. The default (strict) mode fails validation on any network error.

## Review Date

2027-02-28
