# Select the audit scope

Explicit files, a skill, a repository, a PR, or a change set establish scope. Do not ask for confirmation of a scope the user already supplied. "This repo" means the repository containing the current working directory, not neighboring projects.

## Bare invocation

If the user invokes Minority Report without a scope, inspect only enough directory and repository metadata to offer a bounded recommendation before inventorying instruction bodies. Use the harness's question or user-input tool when available; otherwise ask one concise question in conversation. Wait for the answer. A highlighted recommendation, timeout, or unavailable question tool is not an answer.

- Inside an individual skill, recommend that skill.
- Elsewhere in a repository, recommend that repository's instruction sources.
- In a home directory, an unrelated scratch directory, or a location with no clear project, ask for a repository, skill, or path. Do not recommend scanning the entire home directory.

For example, inside a repository:

> What should I review in this repository: its instruction sources, recent instruction changes, or a broader set of locations?

Offer the context-appropriate recommendation first. Name the actual repository or skill when known. A broader-scope answer still needs concrete roots; ask for those before beginning. In a non-interactive run with no established scope, report that scope is required rather than silently starting an audit or repeatedly attempting a question tool.

## Audit targets and supporting context

| Scope | Targets | Context needed for a correct review |
| --- | --- | --- |
| Targeted | Named files, skill, or instruction change set | Applicable parent guidance, direct references, contracts, and affected consumers |
| Repository | The selected repo's canonical instruction sources, skills, rules, and relevant configuration | Applicable parent or shared guidance; generated copies used to verify projection |
| Broad sweep | Explicitly selected repositories or instruction roots | Shared guidance and cross-project relationships within the requested review |

Reading a supporting file does not make it an audit target. Map supporting sources and mark them `context_only` with a reason. Cite them when explaining a target finding, but do not propose patches to them unless the user's scope includes them. Put separately noticed out-of-scope concerns in `unresolved`, with their location and the scope limit, instead of expanding the audit. Generated copies point back to canonical sources; they are not independent policy owners.

For a named PR or exact comparison, use that comparison without another scope question. Exclude working-tree changes unless the user explicitly includes them. Otherwise, establish the comparison: if both uncommitted edits and branch commits are plausible, ask which the user means. Do not assume a branch is called `main`. Read complete surrounding instructions and affected consumers, while focusing findings on changed behavior and its consequences. A deletion may require reading the base version.

## State the boundary in the report

Start the human-readable overview with the targets, supporting context, comparison if any, target models, and exclusions or limits. Preserve target-versus-context distinctions in the discovery roots and coverage reasons so JSON-only delivery also exposes the boundary. Record missing context as a limitation rather than asserting an exhaustive review.

The discovery helper accepts explicit paths, but it is not a complete inventory of arbitrary references or request code. Add relevant omitted files explicitly. The selected scope governs what to review and patch even when discovery follows a link beyond it.
