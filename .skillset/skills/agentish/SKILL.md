---
name: agentish
description: Write or revise agent-facing instructions, including instruction passages in mixed documents. Use for authoring or targeted wording edits in skills, agent definitions, prompts, and tool descriptions, not systematic audits, ordinary human-facing prose, or conversational style.
resources:
  references:
    - shared:references/instruction-selection.md
    - shared:references/instruction-placement.md
    - shared:references/agentish.md
---

# Agentish

**A Language Guide for Agents.**

Intended consumers include GPT-6 Astra and Claude Fable. Preserve model-specific requirements when they are supported by the target's documented or observed behavior; a model name does not establish that a workaround is obsolete.

Write instructions that make intended behavior clear. Preserve the user's policy and deliberately chosen wording; do not soften a tested prohibition into an open-ended judgment call merely to make it sound smoother.

Apply Agentish to text that directs agents, regardless of whether the file is public or private. In a mixed document, apply it to instruction passages only. It does not prescribe how an agent speaks to people.

Consider everyone who will read the document. Apply Agentish most strictly to agent-only control surfaces such as `AGENTS.md`, `CLAUDE.md`, skill instructions, and tool descriptions. In `docs/` and other material people also read, keep instruction passages natural and use uppercase requirement terms only when their formal distinction matters.

## Select, place, express

- Before adding a persistent directive, use [Instruction Selection](shared:references/instruction-selection.md) to decide whether it earns a place. When editing wording, preserve the existing scope unless the task also calls for changing policy.
- When choosing or changing where guidance lives, use [Instruction Placement](shared:references/instruction-placement.md). Verify the consuming harness before relying on loading, inheritance, or deferred context behavior.
- When writing the instruction, use [Agentish](shared:references/agentish.md). Start with its minimal profile; consult the sections relevant to the text being changed. Use explicit requirement levels where the distinction matters, without converting every sentence into a capitalized requirement.

## Check the result

For a consequential rule, identify a case where it applies and a case where it does not. Check that the wording preserves the intended action, scope, exception, and authority. If the boundary is uncertain, flag the ambiguity rather than inventing policy. For a wording-only edit, preserve the meaning and verify references without adding an audit or evaluation workflow.

When the task is implementation, edit the canonical source and follow the repository's generation and validation commands. When the task asks for a draft or discussion, provide that result. Do not turn a targeted edit into a systematic audit.

No external tools or services are required to use the bundled guidance. Editing and validation use the tools available in the target project.
