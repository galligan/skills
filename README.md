# Matt Galligan's Skills

Shareable agent skills, authored with [Skillset](https://github.com/outfitter-dev/skillset) and distributed as complete directories under `skills/`.

## Skills

- [Minority Report](skills/minority-report/SKILL.md): an independent, evidence-backed audit of agent instructions for conflicts, unnecessary work, and unintended consequences. Includes conditional GPT-6 Astra and Claude Fable review profiles, scripts, schemas, and tests.
- [Agentish](skills/agentish-styleguide/SKILL.md) (`agentish-styleguide`): a language guide for agents. Author skills, agent definitions, prompts, and tool descriptions with precise behavior and boundaries.
- [People Words](skills/people-words/SKILL.md) (`people-words`): drop mannered, performative prose and lead with substance. Use up front or as a midstream correction, while preserving technical precision and the user's register.

## Authoring

Use Bun 1.4.0. The compiler is pinned to `@skillset/cli@0.26.1` in `package.json` and `bun.lock`.

```bash
bun install --frozen-lockfile --ignore-scripts
bun run skillset new skill my-skill --yes
```

Edit `.skillset/skills/my-skill/SKILL.md`. Keep supporting files inside that directory so the complete skill travels with an individual installation.

```bash
bun run skillset change status
bun run build
bun run check
```

Record meaningful changes with Skillset's change commands using the scope reported by `change status`. Use `release plan` and `release apply` to advance versions and changelogs. Commit source, change records, and generated output together.

## Instruction conventions

Three references guide instruction authoring:

- [Instruction Selection](.skillset/shared/references/instruction-selection.md): decide whether a directive earns its place.
- [Instruction Placement](.skillset/shared/references/instruction-placement.md): choose the surface that owns the instruction.
- [Agentish](.skillset/shared/references/agentish.md): express behavior with observable conditions, consistent terms, and testable outcomes.

These conventions govern agent-facing instructions. Agentish uses them for authoring; Minority Report uses them as review criteria. Skillset bundles the declared references with each skill so installation does not depend on this checkout or another installed skill.

People Words has separate, self-contained guidance for human-facing communication. It preserves the direct instruction not to use mannered prose, qualified by the user's register or an explicitly requested style. It does not import Agentish's normative vocabulary or make brevity and informality universal goals. This repository's `AGENTS.md` routes to the skills for their respective work.

Minority Report adapts both [OpenAI's Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [Anthropic's Claude API prompt audit](https://github.com/anthropics/skills/tree/main/skills/claude-api). Model-specific claims require evidence for the actual target; a keyword match is not a finding. See the [self-review and source decisions](docs/reviews/2026-09-12-instruction-review.md).

Repository instructions are also compiled: edit [the shared source](.skillset/partials/repository.md), then build both `AGENTS.md` and `.claude/CLAUDE.md`. They direct future agents to review substantive instruction changes with our own guidance, scoped to the changed source and affected consumers.

## Layout

| Path | Purpose |
| --- | --- |
| `skillset.yaml` | Workspace metadata and the single `skills/` output configuration |
| `.skillset/skills/<name>/` | Editable skill source and all supporting files |
| `.skillset/shared/references/` | Shared conventions for instruction authoring and review |
| `.skillset/partials/repository.md` | Canonical repository instructions |
| `.skillset/rules/` and `.skillset/_claude/` | Thin wrappers selecting the Codex and Claude instruction surfaces |
| `.skillset/changes/` | Skillset change and release evidence |
| `skills/<name>/` | Generated, self-contained skill for consumers |
| `skills/skillset.lock` | Generated ownership and drift tracking |
| `AGENTS.md` and `.claude/CLAUDE.md` | Generated project instructions for Codex and Claude Code |
| `skillset.lock` | Generated instruction ownership and shared-source dependency tracking |

The Codex renderer emits this collection at a custom path. It preserves the audit skill's body and supporting content while normalizing metadata and its OpenAI sidecar; this is not a claim of provider-neutral rendering.

## Installation

Once these changes are published to the repository's default branch:

```bash
npx skills add galligan/skills --list
npx skills add galligan/skills --skill minority-report
npx skills add galligan/skills --skill agentish-styleguide
npx skills add galligan/skills --skill people-words
```

See [publishing notes](docs/publishing.md) for the build contract, validation, and runtime requirements. Building locally does not publish or install anything.

## License

[MIT](LICENSE).
