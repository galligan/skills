# Review contract and calibration

Review instruction behavior, not prose style. Flag only distinct, substantive issues with a concrete consequence:

- **Broad trigger:** a description attracts unrelated tasks or a topic mention starts a specialized workflow.
- **Unconditional read:** every task or skill invocation loads material whose applicability is narrower.
- **Redundant verification:** the same evidence is requested again with no changed state or distinct question.
- **Conflict:** two active requirements cannot both be satisfied. Cite both; distinguish a legitimate local override from a contradiction.
- **Premature confirmation:** a rule stops authorized preparation before producing a useful, reviewable result, despite adequate scope.
- **Overprescribed workflow:** fixed steps, delegation, tooling, or bookkeeping impose a demonstrated task-specific cost.
- **Stale reference:** an active instruction routes to missing, retired, or superseded material and impedes work.
- **Contract mismatch:** a tool description, prompt, schema, or request configuration contradicts the actual supported input/output contract or omits a constraint required for correct use. Cite the contract and implementation or verified provider evidence; an instruction-only keyword match is insufficient.

A long file, strong imperative, mandatory test, safety boundary, or repeated reminder is not intrinsically a finding. Specialized expertise and useful operational invariants belong in skills. Judge whether wording forces irrelevant work or an incorrect decision. Avoid blanket recommendations to weaken testing, ask fewer questions, or remove safeguards.

For model-dependent candidates, use [model-review.md](model-review.md) and only the applicable target profile. Distinguish normative vocabulary from pressure language and working duplication from conflicting requirements. A provider anti-pattern match is a lead; it does not establish applicability, consequence, or confidence by itself. If a candidate does not fit this findings contract, describe the limitation in `unresolved` rather than forcing it into an unrelated category.

## Instruction design criteria

When deciding whether a directive should remain, move, merge, or change, apply the **Instruction Selection**. State the proposed action and owning surface in `smallest_change`; do not create a record for every directive merely to populate a checklist.

When a finding depends on where an instruction loads, consult **Instruction Placement**. Verify the consuming harness before claiming that a move reduces persistent context. Task-specific invariants may remain in the skill whose procedure needs them.

When ambiguous wording changes a decision or action, apply the relevant **Agentish** criteria. Start with its minimal profile. Style nonconformance alone is not a finding; identify the concrete behavioral consequence.

A preventive rule without historical incident evidence is unproven, not automatically unnecessary. Describe that uncertainty in `confidence_reason`. Preserve the evidence and decision requirements below when proposing changes to safeguards.

## Evidence and proposals

Every finding requires a verbatim contiguous excerpt with 1-based inclusive line numbers; no ellipses or reconstructed wording. Use the map's exact canonical paths. For remote documents cite the snapshot path and `source_url`. Check the surrounding section and applicable root guidance. Describe potential consequences as conditional unless directly observed; do not invent token savings, timing, or failure rates.

Provide the smallest complete unified diff. It must remove the behavior at each repeated active location implicated by the finding, preserve unrelated requirements, and use real target paths. Do not invent an unavailable replacement tool or source. For generated instructions, target the generator or canonical source and explain regeneration. Related files used as evidence or patch targets must also be mapped.

Diffs are independent proposals against the snapshot, not a cumulative patch series. Use `related_findings` to identify alternatives or overlaps and explain the relationship in `smallest_change`. For an inherently unavailable replacement or owner decision, propose a concrete wording change that makes the unresolved state honest; do not claim a speculative implementation is verified.

Mark `decision_required: true` for any proposal involving safety, authority, external-action permissions, confirmation gates, or narrowed verification/review. Explain the exact tradeoff in `decision_reason`. This classification neither grants authority nor requires interrupting the audit to obtain approval.

## Rank without a quota

Use these anchors consistently. Give a brief reason for severity, improvement, and confidence.

| Field | Anchors |
|---|---|
| `severity` | `critical`: credible severe harm or destructive/unauthorized action; `high`: materially wrong work, significant authority ambiguity, or a blocked common completion path; `medium`: meaningful repeated overhead, misrouting, or bounded workflow failure; `low`: limited but concrete friction or maintainability cost. |
| `improvement.level` | `high`: removes a major failure path or recurring work across broad scope; `medium`: materially improves a common or costly workflow; `low`: modest benefit in a narrow case. This is expected benefit, not measured performance. |
| `improvement.areas` | One or more of correctness, completion, context, tool_usage, maintainability. |
| `reach` | `pervasive`: applied at startup or most tasks in scope; `common`: a regularly used workflow; `occasional`: a specialized trigger. Infer applicability from instructions, not unsupported usage statistics. |
| `confidence` | `high`: direct unambiguous text plus relevant context; `medium`: concrete evidence but a material interpretation or harness condition remains; `low`: plausible concern with unresolved applicability. Low-confidence items must clearly state uncertainty; omit mere speculation. |

Severity measures consequence. Improvement measures the proposed change's benefit. Reach measures applicability. Confidence measures evidence. Keep them separate; a rare dangerous action should not disappear beneath a frequent context-loading nuisance.

## Calibration examples

- **Flag:** “Use this deployment skill whenever hosting is mentioned,” where the body creates and publishes infrastructure. **Do not flag:** “Use this skill when deploying this application,” with deployment-specific checks.
- **Flag:** “Before every change, read all four architecture manuals,” including unrelated typo edits. **Do not flag:** a short routing index that loads each manual only for its applicable subsystem.
- **Flag:** run an identical unchanged-head check again solely to satisfy a numeric pass count. **Do not flag:** rerun after a fix or perform an independent review that asks a distinct question.
- **Flag:** “Always wait for approval before read-only research” after the user gave a concrete research scope. **Do not flag:** pause before an unauthorized send, deployment, deletion, or genuinely consequential missing choice.
- **Do not flag:** a memory skill triggered by relevant prior context merely because many tasks benefit from it. Broad usefulness is not an over-trigger.
- **Do not flag:** “address or discuss review comments” as a requirement to implement every comment. Read the exception before claiming a conflict.
- Shell prefetch/import syntax runs only in supporting harnesses. Qualify impact unless the consuming runtime is established.

## Coverage and handoff

Each review JSON identifies one `reviewer`, has `schema_version: "1.0"`, and contains `coverage`, `findings`, and `unresolved`. Account for every assigned path with `reviewed`, `duplicate`, `context_only`, `missing`, or `blocked`, plus a concrete reason. `duplicate` needs a verified canonical path; matching names alone are insufficient. Excluded managed content remains in the map's exclusions, not the review queue.

No finding quota or early exit after a handful of examples. Consolidate genuinely duplicated policies using related evidence without collapsing distinct owning files or decisions. Hand off the JSON path and any access, provenance, or interpretation limits. Do not apply proposed edits during the audit.

Provider attribution and version-specific review criteria are in [GPT-6 Astra](gpt-6-astra.md) and [Claude Fable](claude-fable.md). This bundled contract does not require fetching those sources for every audit.
