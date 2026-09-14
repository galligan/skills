# mg skills

A few skills for getting better work out of agents and better words out of them, too. These grew out of how I work with Claude and Codex. Take the ones that help.

## Skills 🔎

- [`redliner`](skills/redliner/SKILL.md): Audit agent instructions for conflicts, unnecessary work, and unintended consequences.
- [`agentish-styleguide`](skills/agentish-styleguide/SKILL.md): Write skills, prompts, and other agent instructions with clear behavior and boundaries.
- [`people-words`](skills/people-words/SKILL.md): Drop mannered prose while keeping the substance, technical detail, and your voice.

[Meet the skills](docs/skills.md) for why each one exists, when to use it, and what to expect.

## Installation 📦

<details open>
<summary><strong>npx skills</strong></summary>

```bash
npx skills@latest add galligan/skills
```

Pick the skills you want and the agents you want to use them with. To install one directly:

```bash
npx skills@latest add galligan/skills --skill redliner
```

Or browse the collection without installing anything:

```bash
npx skills@latest add galligan/skills --list
```

The installer copies ordinary skill files into your project. Pull later updates with `npx skills update`.

</details>

<details>
<summary><strong>Codex or ChatGPT desktop</strong></summary>

Use the [built-in skill installer](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use):

```text
$skill-installer Install redliner from https://github.com/galligan/skills/tree/main/skills/redliner
```

Swap `redliner` for either of the other skill names.

</details>

<details>
<summary><strong>Claude Code</strong></summary>

Ask Claude Code to install the bundle in its [native skills folder](https://code.claude.com/docs/en/skills#where-skills-live):

```text
Install redliner from
https://github.com/galligan/skills/tree/main/skills/redliner
into ~/.claude/skills/redliner. Include all supporting files without
cloning the repo. Check with me before replacing an existing installation.
```

Then invoke `/redliner`. Use `.claude/skills/redliner` for a project-only install. Swap the skill name and paths to install another.

</details>

Each skill is a complete bundle. You don't need Bun or Skillset to use one. ChatGPT web and mobile use [plugins](https://learn.chatgpt.com/docs/plugins); this collection currently ships standalone skills.

## How these are made

I built [Skillset](https://github.com/outfitter-dev/skillset) to manage agent instructions and skills, and use it to author and build this collection. The source lives in `.skillset/`; the complete, installable versions land in `skills/`.

Three references keep the instruction work grounded:

- [Instruction Selection](.skillset/shared/references/instruction-selection.md): does this directive earn its place?
- [Instruction Placement](.skillset/shared/references/instruction-placement.md): where should it live?
- [Agentish](.skillset/shared/references/agentish.md): how do we make the intended behavior clear?

`agentish-styleguide` uses these for writing; `redliner` uses them for review. Each gets its own bundled references, so you can install either on its own. `people-words` stays focused on expression.

`redliner` also draws on [OpenAI's Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [Anthropic's Claude API prompt audit](https://github.com/anthropics/skills/tree/main/skills/claude-api), with profiles for GPT-6 Astra and Claude Fable. Those profiles load when relevant; a model name or keyword match isn't evidence of a problem.

We use the guidance here, too. Our generated `AGENTS.md` and `.claude/CLAUDE.md` route substantive instruction changes through a scoped Redliner review. The [review notes](docs/reviews/2026-09-12-instruction-review.md) and [follow-up corrections](docs/reviews/2026-09-12-scope-and-pr-review.md) show what the first passes found and missed.

## Working on the collection

Use Bun 1.4.0. Skillset is pinned to `@skillset/cli@0.26.1`.

```bash
bun install --frozen-lockfile --ignore-scripts
bun run skillset new skill my-skill --yes
```

Edit `.skillset/skills/my-skill/SKILL.md` and keep its supporting files alongside it. Then rebuild and check the result:

```bash
bun run skillset change status
bun run build
bun run check
```

Record meaningful changes through Skillset's change commands, using the scope reported by `change status`. Commit source, change records, and generated output together. The [publishing guide](docs/publishing.md) covers change evidence, release commands, tests, and compiler details.

Edit the source and rebuild; let Skillset manage `skills/`, `AGENTS.md`, `.claude/CLAUDE.md`, and the locks. Building doesn't publish or install anything.

## License

[MIT](LICENSE). Use what helps, make it your own.
