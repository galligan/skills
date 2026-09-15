# Agentish

**A Language Guide for Agents.**

Inspired by Simplified Technical English principles and adapted for agent-facing instructions: instruction files, scoped rules, skills, tool descriptions, workflow procedures, and review criteria.

## What this guide is

Agent-facing instructions are closer to configuration than prose. Their goal is not elegance; it is to communicate behavior with the smallest practical amount of ambiguity. Agentish is the writing style for instructions that reduce interpretation and make intended behavior observable.

Agentish is for agent-speak: skills, agent definitions, prompts, and other text that directs agent behavior. Human-facing replies and documentation are outside its scope. In a mixed document, apply it only to the passages that instruct agents.

### Match the document and its audience

Identify both the intended agent behavior and everyone who will read the document. Apply this guide most strictly to agent-only control surfaces such as `AGENTS.md`, `CLAUDE.md`, skill instructions, tool descriptions, invariants, and procedures.

In `docs/` and other material written for people as well as agents, keep the prose readable for people. Apply Agentish only to passages that direct agent behavior, and use the lightest wording that preserves the instruction's meaning. Do not make surrounding explanation sound like a compliance specification merely because an agent may read it.

This guide is a styleguide, not policy:

- It governs **how to write** an instruction. Whether an instruction earns its place, and which surface owns it, are separate decisions governed by the [Instruction Selection](instruction-selection.md) and [Instruction Placement](instruction-placement.md).
- It sets no compliance requirements. Each project decides where and how strictly to apply it. As a default, apply it most strictly to the surfaces that most directly control behavior or routing: skill descriptions, tool descriptions, invariants, and procedures.
- It does not require literal ASD-STE100 compliance, does not govern ordinary agent conversation or user-facing documentation, and does not exist to make writing shorter at the expense of precision.

Do not use this guide as a reason to add instructions. Use it on instructions that have already earned their place.

One note on self-application: this guide contains rules and explanation. The rules and examples follow the guide. The explanation is ordinary technical prose and is not written at instruction strictness — explanation never is.

## Normative vocabulary

Use normative terms consistently when a statement controls behavior. Match their formality to the document and its audience.

On an agent-only control surface, uppercase terms can make distinct requirement levels explicit. In human-facing or mixed documentation, prefer plain language such as *must*, *should*, *can*, and *do not* unless the document is a specification, policy, or contract where RFC-style requirement levels carry formal meaning. Do not add uppercase terms only for emphasis.

> Agent-only control surface: `MUST NOT edit generated files.`
> Human-facing guide: `Do not edit generated files directly. Update the source and rebuild.`

- **MUST** — the behavior is required. Violation is a failure. `MUST NOT edit generated files.`
- **MUST NOT** — the behavior is prohibited. Violation is a failure. `MUST NOT refactor unrelated code.`
- **SHOULD** — the expected default. Deviate only for a concrete reason relevant to the task. Use sparingly; prefer an explicit condition. `SHOULD reuse an existing parser when it satisfies the required grammar.`
- **SHOULD NOT** — normally undesirable, with legitimate exceptions.
- **MAY** — explicit permission, used only where uncertainty is real. `MAY add a regression test in the nearest existing test file.`

### Avoid weak normative synonyms

Do not control behavior with: *ideally, preferably, generally, normally, where appropriate, where reasonable, when practical, if possible, when it makes sense, use your judgment.*

Replace them with an observable condition.

> Before: Prefer the existing abstraction where appropriate.
> After: Reuse the existing abstraction if it satisfies the requirement.

## Terminology

### Use one canonical term for one concept

Once a project establishes a term, use it consistently. Do not introduce synonyms for variety: if `adapter` is canonical, do not alternate among *connector*, *integration*, *bridge*, or *provider* unless those name different concepts. Repetition is acceptable in instructions; terminological consistency outranks prose variety.

The project's established term wins over the industry-standard term. Do not propose renaming an established term for standardness alone — consistency, not conventionality, is the requirement.

### Do not use one term for different concepts

If two concepts have different behavior, give them different names. Do not overload a term because the concepts are related.

### Preserve exact technical vocabulary

Do not simplify or paraphrase identifiers, type names, commands, filenames, configuration keys, protocol names, or established domain terms.

> Write: Run `skillset check`.
> Not: Run the command that checks the Skillset configuration.

### Define new project terms

If an instruction introduces a project-specific term, define it at first use or reference the authoritative definition. Do not invent shorthand only to shorten the instruction.

## Sentence structure

### One normative instruction per sentence or bullet

Do not combine independent obligations. Independent instructions are independently reviewable.

> Before: Reuse existing components, update the tests, and make sure the documentation stays current.
> After:
> - Reuse an existing component if it satisfies the requirement.
> - Update affected tests when behavior changes.
> - Update user documentation when public behavior changes.

### Prefer short procedural sentences

A procedural sentence expresses one action, condition, prohibition, or decision. Do not shorten a sentence if shortening removes technical precision.

### Use direct verbs

> Write: Validate the schema.
> Not: Perform schema validation.

### Prefer active voice for instructions

> Write: Run the affected tests.
> Not: The affected tests should be run.

Passive voice MAY be used when the actor is intentionally irrelevant.

## Conditions and decisions

### Put the condition before the action

> Write: If public behavior changes, update the documentation.
> Not: Update the documentation if public behavior changes.

The first form exposes the control structure before the dependent action.

### Make decision criteria observable

> Before: Create a new abstraction when necessary.
> After: Create a new abstraction only if no existing abstraction satisfies the requirement.

> Before: Use the migration workflow for significant schema changes.
> After: Use the migration workflow when the change modifies a persisted schema.

### Separate branches when behavior differs

> Before: Update or create the file depending on whether one already exists.
> After:
> - If the file exists, update it.
> - If the file does not exist, create it.

### State exceptions explicitly

Do not hide exceptions inside vague qualifiers. Name the condition that makes the exception valid.

> Before: Do not edit generated files unless really necessary.
> After:
> - MUST NOT edit generated files.
> - If the generator itself is defective, modify the generator and regenerate the output.

## Actors and targets

### Name the actor when it is ambiguous

Imperatives already imply the agent: `Run the affected tests.` needs no actor. When several components act, name them.

> Before: It validates the result before writing it.
> After: The compiler validates the result before it writes the lockfile.

### Name the target

Do not write behavioral instructions whose object must be inferred.

> Before: Keep the change focused.
> After: MUST NOT modify files outside the requested feature unless the implementation requires the change.

When the boundary is concrete, state it directly: `MUST NOT modify files outside packages/core/.`

### State action boundaries

For consequential operations, state what the instruction permits and what it excludes.

> Before: Clean up the affected configuration.
> After:
> - Remove obsolete entries from `providers.json`.
> - MUST NOT modify unrelated provider configuration.

## Pronouns and references

### Avoid ambiguous pronouns

Do not use *it, this, that, they, these* when more than one antecedent is plausible. Repeat the noun.

> Before: Update the adapter after the provider validates it.
> After: Update the adapter after the provider validates the configuration.

### Prefer explicit references over directional prose

Avoid *the above, the following section, as mentioned earlier, this process* when a stable name can identify the reference.

> Write: Follow the requirements in `## Generated files`.

## Ambiguous qualifiers

Words that describe quality are not decision criteria. Treat these as suspicious when they control behavior: *appropriate, clean, clear, correct, efficient, excessive, important, maintainable, meaningful, minimal, necessary, obvious, proper, reasonable, relevant, significant, simple, substantial.*

These words are acceptable in explanation. When one determines an action, define the criterion.

> Before: Add tests for significant behavior changes.
> After: Add or update tests when the change modifies observable behavior.

> Before: Avoid unnecessary dependencies.
> After: Do not add a dependency when the repository already provides the required capability.

## Prohibitions

### State prohibitions directly

> Before: Keep unrelated refactors to a minimum.
> After: MUST NOT refactor unrelated code.

### State the safe path

A prohibition is more actionable when the agent knows what to do instead.

> MUST NOT edit generated files.
> Modify the source schema and regenerate the files.

Omit the safe path when it is obvious or when several valid alternatives exist.

### State escalation when no safe path exists

If a prohibited action appears required and no safe path applies, the instruction states what the agent does instead of guessing.

> If backward compatibility cannot be preserved, stop and report the breaking change before implementation.

## Procedures

### Use explicit sequence when order matters

Use ordered steps for required ordering. Do not rely on paragraph order to communicate a mandatory sequence.

### Keep steps atomic

One primary action per step.

> Before: Update the schema, regenerate the client, run tests, and inspect the diff.
> After:
> 1. Update the schema.
> 2. Regenerate the client.
> 3. Run the affected tests.
> 4. Inspect the generated diff.

### State verification explicitly

Identify what to verify, when to verify it, and what success means.

> Before: Make sure everything still works.
> After:
> - Run `bun test packages/core`.
> - Continue only if the command succeeds.

## Skill and tool descriptions

Descriptions are routing instructions: a harness may read them before loading the body to decide activation, so they deserve the strictest treatment in this guide.

### A skill description states capability and activation

> Weak: Verify code changes.
> Better: Verify runtime, test, or build-behavior changes before task completion.

> Weak: Work with database migrations.
> Better: Create, review, or repair a database migration when a change modifies a persisted schema.

Do not fill a description with implementation detail that belongs in the body.

### Structure a skill body by function

A useful order: purpose; activation conditions ("use when"); exclusion conditions ("do not use when"), if needed; rules; procedure; verification; references. Not every skill needs every section. Keep long examples, exhaustive references, and edge cases behind progressive disclosure so the activation surface stays small.

### A tool description states capability, activation, and side effects

> Weak: Search project information.
> Better: Search project documents when the requested information is not present in the current context.

If invoking the tool mutates state, say so: `Creates or updates a Linear document.` is better than `Manages Linear documents.`

When tools overlap, describe the decision boundary:

> Use `search` to find unknown files by topic.
> Use `find` only when you know the file and need an exact phrase.

Do not copy a procedure into a tool description; descriptions support selection, workflows belong in skills.

## Examples

An example earns its place by demonstrating a decision boundary that prose leaves unclear. Do not add examples that merely restate a rule. Prefer contrasting pairs:

Rule: `Reuse an existing abstraction if it satisfies the requirement.`

> **Reuse:** An existing `StorageAdapter` supports the required backend. Extend that adapter.
> **Create:** No current adapter supports streaming writes. Add a new adapter.

Contrasting pairs also become natural seeds for behavioral eval cases.

## Evalability

Write consequential instructions so compliance is testable. A strong rule exposes its behavioral structure — condition, actor, action, target, exception, expected outcome:

> If a public API change cannot remain backward compatible, stop and report the breaking change before implementation.

exposes: condition (compatibility cannot be preserved), action (stop), required output (report the breaking change), lifecycle boundary (before implementation).

For a consequential rule, it should be possible to construct:

- a **triggering case**, where the rule must apply;
- a **safe counterexample**, where the rule must not over-apply;
- an **unrelated case**, where the rule has no effect.

Language conformance is one layer, not the result. A sentence can follow this guide perfectly and encode a bad policy. Evaluate language clarity, policy correctness, behavioral adherence, and task outcome separately.

## Minimal profile

When applying the full guide is impractical, use this subset:

- Use one canonical term for one concept.
- Preserve exact technical terminology and identifiers.
- Write one normative instruction per sentence or bullet.
- Put conditions before actions.
- Use direct verbs and active voice.
- Name targets and boundaries when they are not obvious.
- Avoid pronouns with more than one plausible antecedent.
- Remove or define vague decision qualifiers.
- Match normative vocabulary to the document's audience. Use `MUST`, `MUST NOT`, `SHOULD`, and `MAY` consistently when their formal distinction matters.
- State the safe path for important prohibitions, and escalation when no safe path exists.
- Write consequential rules so they can produce behavioral eval cases.

## Summary

Agentish treats agent-facing prose as an engineering control surface. Its purpose is to make instructions smaller, more precise, less ambiguous, easier to review, and easier to evaluate — never to make agents sound simpler, and never to justify adding instructions that have not earned their place.
