# Model-aware review

Establish the target models and consuming harness from the request, repository configuration, or an explicit migration plan. Record the evidence and any assumptions in the report introduction and the relevant coverage reasons. If the target is unknown, complete the general review and record that limit in `unresolved`; do not guess the newest flagship or treat the reviewer's own model as the target.

Load only the applicable profile: [GPT-6 Astra](gpt-6-astra.md) or [Claude Fable](claude-fable.md). For a shared instruction set, evaluate each intended consumer and distinguish common findings from provider-specific ones. These are named review targets, not permanent claims about which models are latest. Other targets use the common rubric and verified documentation for that model.

## Evidence before edits

Use history or blame when a candidate may be a model workaround. Identify the original failure and whether the rule also encodes a user preference, tool contract, or operational boundary. Age, an imperative, a keyword hit, or a model name is a lead, not evidence that the instruction is obsolete. Source guidance itself can conflict; resolve the exact model, version, harness, and task before proposing a change.

A model-dependent finding states the target and source or observed behavior in `confidence_reason`, and the concrete consequence in `impact`. Verify version-sensitive API claims against current official documentation or a reproduction. Pattern matches do not automatically earn medium or high confidence. Put unresolved hypotheses in `unresolved` rather than inventing a patch. Keep the existing findings schema and ranking; a profile supplements the rubric, not the output contract.

## Preserve what serves the task

Preserve author-specific context, precise tool mechanics, demonstrated mitigations, format-sensitive examples, and ordering required by fragile operations. A working duplicate or deliberate recap is not a defect by itself; require a conflict, stale copy, or demonstrated cost. A short description with a complete contract is valid, and a longer one may be necessary. Neither sentence quotas nor an arbitrary number of model calls proves quality.

Distinguish routing from behavior, and normative requirement levels from emotional emphasis. A direct prohibition against mannered prose can be an intentional, tested preference. Do not replace it with positive wording merely because an anti-pattern table matches it.

## Inspect the relevant implementation

When the scoped prompt depends on request construction, tool definitions, examples, or agent configuration, inspect those sources too. Add them to the discovery map before citing or patching them; the Markdown discovery helper is not a complete code inventory. Check the real input/output contract and supported configuration before recommending an API feature. Do not replace user-facing explanations with requests to reveal hidden reasoning.

Keep deterministic parsing and validation in code where that is the existing contract. Evaluate delegation and model calls by their distinct work and measured effects. Do not expand a prose audit into an unrelated architecture redesign.

## Check contested removals

Treat a behavioral improvement as a hypothesis until observed. When evaluation is authorized and available, compare the original and proposed instruction on a triggering case, a safe counterexample, and an unrelated task, using the target model and harness. Compare correctness, completion, scope, and useful communication; asking the model whether it needs a rule is not a behavioral test. Reuse an existing eval suite when it covers the question.

For consequential changes, isolate the change so a regression can be attributed. If it regresses, restore or revise the instruction and recheck. If target-model execution is unavailable, report that limitation and do not claim measured improvement. Audit-only requests still produce proposals; permission for an audit does not authorize source edits, paid evaluations, or live actions.
