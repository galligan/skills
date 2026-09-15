# The skills

These skills cover three parts of working with agents: reviewing their instructions, writing those instructions, and improving what they write for people. Each can be installed on its own. You can start with whichever problem is in front of you.

[Installation instructions](../README.md#installation-)

## redliner

Agent instructions tend to accumulate. A workaround helps once, so it becomes a rule. Another file adds an exception. Eventually, an agent is reading four documents before fixing a typo, or asking permission for something you already asked it to do.

`redliner` gives those instructions a second pair of eyes. It follows the relevant guidance, checks how the pieces interact, and produces an instruction redline: findings backed by specific passages, an explanation of the likely consequence, and proposed changes. The review still has to earn every mark it makes.

Use it when:

- A repo's agent keeps stopping, repeating checks, or doing work you didn't intend. Review the instructions that might be contributing to that behavior.
- You've changed a skill or `AGENTS.md` and want to check the diff against the surrounding guidance before merging.
- Shared instructions have spread across several repos and you want to find conflicting or redundant rules.
- You're updating instructions for a different model and need to check whether older workarounds still have a reason to exist.

You can name a file, a skill, a repository, a PR, or a set of instruction roots. For example:

> Use redliner to review the instruction changes in this PR. Check them against the repo guidance and flag any conflicts introduced by the diff.

A bare invocation asks which audit you want, using the current directory to suggest a scope. If you've already supplied the scope, it proceeds. A repo review and a review of recent changes can produce very different work, so that choice matters.

The report includes ranked findings, source excerpts, and proposed diffs, with a machine-readable `findings.json`. It also records missing context and uncertainty. Applying the changes is a separate task, and a report with no findings is a valid result. Long files, strong wording, and safety checks aren't automatically problems.

The review criteria draw on OpenAI and Anthropic guidance, with profiles for GPT-6 Astra and Claude Fable when the target makes them relevant. They're starting points for investigation, not proof that a particular instruction is wrong. The [skill](../skills/redliner/SKILL.md) links to those sources and documents the Python requirements.

## agentish

Writing agent instructions is a small design problem. You have to decide what behavior you want, when it applies, and where the instruction belongs. “Be thorough” leaves a lot open. “Before changing the API, check its existing callers” gives the agent a condition and an action.

The Agentish skill brings those decisions together through three references:

- **Instruction Selection** asks whether a directive earns its place. A useful instruction addresses a real need without adding unnecessary work to every task.
- **Instruction Placement** identifies the surface that owns it. A repository rule, a skill's activation description, and a reference file have different jobs.
- **Agentish** helps express the intended behavior with clear conditions, consistent terms, and meaningful exceptions.

Use it to write a new skill, sharpen a vague tool description, or revise an instruction that keeps getting interpreted differently than you intended. It's also useful when deciding whether guidance belongs in `AGENTS.md` or in a skill that loads only for a particular task.

For example:

> Use agentish to revise this skill's instructions. Preserve the existing policy, but make its activation conditions and approval boundary explicit.

The result is a draft or an edit, depending on what you asked for. For consequential rules, the skill checks both a case where the rule applies and one where it doesn't. That helps catch wording that sounds clear until an agent has to act on it.

Agentish applies to passages that direct agents, including instructions in public files. It doesn't impose its vocabulary on ordinary docs or conversation. When a file in `docs/` is meant for people as well as agents, keep it readable for people and go lighter on uppercase requirement terms. Terms such as `MUST` still belong in specifications, policies, and other places where their formal distinction matters.

Use [the Agentish skill](../skills/agentish/SKILL.md) for instruction authoring. If you want a systematic review of how existing instructions interact, that's `redliner`.

## people-words

Sometimes the answer is useful, but the writing makes you work to get to it. There's a ceremonial opening, a few grand claims, and a conclusion that repeats what you just read. I want the agent to get on with it and write at my register.

That's the job of `people-words`. Its starting point is direct: write conversationally, don't get more mannered or performative than the user, and lead with substance.

Use it when:

- A response needs another pass because it sounds stiff, inflated, or oddly promotional.
- You're drafting a README, explanation, or other document and want natural prose that still fits its audience.
- You want to set a conversational style at the start of a task, or explicitly select it in a project's governing instructions.

You can use it midstream:

> Use people-words and rewrite that. Keep the technical detail and uncertainty, but drop the mannered prose.

As a correction, it restates the substance and carries the adjustment forward in the conversation. You shouldn't need an apology or an announcement about the new tone.

The aim is to preserve what matters while improving how it's expressed. A detailed engineering explanation can stay detailed. A formal document can stay formal. Citations, qualifications, and exact technical terms stay intact. Natural writing doesn't require slang, forced brevity, or a personality transplant.

[The skill](../skills/people-words/SKILL.md) governs expression. Decisions about verification, permissions, and when to ask questions still come from the task's governing instructions. It can work alongside a specific writing voice or editorial guide when you have one.
