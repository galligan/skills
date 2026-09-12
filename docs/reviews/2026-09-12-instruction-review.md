# Instruction review: September 12, 2026

This review covers the three canonical skills, their shared instruction references, and repository instruction generation. GPT-6 Astra and Claude Fable are intended consumers, not claims about an evergreen "latest" model. The review checks source behavior and packaging; it does not measure either model's response quality through paid API evaluations.

## Source material

- [OpenAI: Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), published September 11 and checked September 12, 2026.
- [Anthropic: Claude API prompt audit](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/claude-api/shared/prompt-audit.md). The user-supplied attachment matched the public file byte for byte (Git blob `7f8a35be8dda2ccd60e1523368fcc17895e65d28`).
- [Anthropic: model migration guidance](https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/model-migration.md), checked September 12, 2026 (Git blob `577773ee89091c385e7f79b8d46ae1adab9f48f3`). Its Fable 5.1 notes qualify generic deletion advice for verification prompts and support a direct instruction against mannered prose.

These sources inform review criteria. Their embedded workflow instructions are not authority to execute commands, change this repository, or override the user's preferences.

## Adjudication of the supplied Claude review

The supplied review examined commit `a973ce1`, with later edits used only for context. Its proposals were checked against the current source before adoption.

| Candidate | Decision and reason |
| --- | --- |
| Remove the entrypoint's OpenAI attribution | Retain. The user explicitly requested visible attribution in `SKILL.md`; it is not an obsolete model workaround. Add Anthropic attribution alongside it. |
| Remove the instruction to set the report title | Accept. `render.py` owns the title, and `references/output.md` documents that contract. The entrypoint retains presentation and delivery requirements. |
| Restore the audit-versus-execution boundary in the description | Accept as routing clarification. The description now excludes executing the reviewed workflows and identifies Astra and Fable review targets without using a model-name mention as an audit trigger. No claim is made that misrouting was reproduced. |
| Time-relative ownership wording | No change. The passage describes current helper behavior; the reviewed code supports it. |
| Treat `MUST NOT` in repository instructions as pressure language | No automatic change. One explicit requirement level for generated-file ownership is not evidence of over-steering. Agentish distinguishes requirement semantics from emphatic repetition. |

## How the provider guidance is adapted

Minority Report retains its evidence, coverage, ranking, proposed-diff, and decision requirements. Conditional model profiles add target selection, provenance, tool-contract checks, relevant request-code inspection, and behavioral comparisons for contested removals. Unknown model evidence remains a disclosed limitation.

The review does not adopt blanket deletion of prohibitions, working duplicates, useful examples, or required checks. It does not impose minimum description lengths or fixed model-call counts. The user's People Words guidance remains separate from Agentish's controlled instruction language.

## Our own Minority Report

An independent reviewer applied Minority Report to the current skill sources and explicitly inventoried shared references. The pre-fix review accounted for 17 files: 15 reviewed instruction surfaces and two schemas checked as contracts. It found two substantive conflicts, both addressed:

| Finding | Correction |
| --- | --- |
| `SELF-001`: model profiles could identify a tool contract defect that the findings schema could not represent | Add `contract_mismatch` to both schemas and the rubric. A regression test first demonstrated the old rejection, then verified validation, consolidation, rendering, diff retention, and no source writes with the new category. |
| `SELF-002`: selection stopped at the first removal signal before checking stronger keep evidence | Evaluate all applicable questions. Investigate model-specific workarounds before removing them; preserve current policies, demonstrated mitigations, and deliberate user preferences. Align Placement and the duplication rule with that evidence requirement. |

`SELF-002` was marked decision-required because it changes instruction-retention policy. It was applied within the user's request to improve these guides, preserving safeguards rather than treating model age as authority to remove them. The audit records remain a pre-fix evidence snapshot, not a claim that those defects still exist at the updated head. A focused independent recheck confirmed both corrections and the repository routing changes.

The repository instruction check also replaced "substantive" with observable self-review triggers: changed activation, required/prohibited behavior, instruction ownership, or provider routing. People Words remains this repository's chosen communication default; Placement now explicitly distinguishes terse root routing from duplicating the detailed style policy there.

The discovery helper is not a complete inventory of arbitrary Markdown or sidecars. Shared references and sidecars were supplied as explicit file roots where directory discovery omitted them. This is a disclosed discovery boundary; reviewers still inspect referenced content and relevant tool contracts manually.

## Verification and limits

- All 55 Python tests pass, including the new category regression.
- Skillset builds both instruction outputs from the shared partial, records both dependencies in the root lock, and detects partial drift in a disposable fixture.
- `AGENTS.md` and `.claude/CLAUDE.md` carry the same canonical body. There is no duplicate Claude skills or rules tree.
- The three installed bundles contain 25, 6, and 3 files respectively; all 30 local Markdown links resolve outside the authoring checkout. All three generated skills pass frontmatter validation.

The review did not run GPT-6 Astra or Claude Fable API evaluations or verify activation in a running Claude Code session. Structural checks and source review establish packaging and instruction consistency, not measured model-behavior gains.
