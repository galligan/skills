# mg skills

A few skills for getting better work out of agents and better words out of them, too. These grew out of how I work with Claude and Codex. Take the ones that help.

## What's in here 🔎

- `minority-report`: Audit agent instructions for conflicts, unnecessary work, and unintended consequences. [SKILL.md](skills/minority-report/SKILL.md)
- `agentish-styleguide`: Write skills, prompts, and other agent instructions with clear behavior and boundaries. [SKILL.md](skills/agentish-styleguide/SKILL.md)
- `people-words`: Drop mannered prose while keeping the substance, technical detail, and your voice. [SKILL.md](skills/people-words/SKILL.md)

[Meet the skills](docs/skills.md) for why each one exists, when to use it, and what to expect.

## Install a skill 📦

```bash
npx skills add galligan/skills --skill people-words
```

Swap `people-words` for `minority-report` or `agentish-styleguide`. To browse the collection first:

```bash
npx skills add galligan/skills --list
```

Each skill is a complete bundle. You don't need Bun or Skillset to use one.

### Or ask your agent

**Codex or a local Codex task in ChatGPT desktop:** use the [built-in installer](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use).

```text
$skill-installer Install people-words from https://github.com/galligan/skills/tree/main/skills/people-words
```

**Claude Code:** ask it to download the bundle into its [native skills folder](https://code.claude.com/docs/en/skills#where-skills-live).

```text
Install people-words from
https://github.com/galligan/skills/tree/main/skills/people-words
into ~/.claude/skills/people-words. Include all supporting files without
cloning the repo. Check with me before replacing an existing installation.
```

Then invoke `/people-words` in Claude Code. Use `.claude/skills/people-words` for a project-only install. In either prompt, swap the skill name to choose another.

ChatGPT web and mobile use [plugins](https://learn.chatgpt.com/docs/plugins); this collection currently ships standalone skills.

## How these are made

I built [Skillset](https://github.com/outfitter-dev/skillset) to manage agent instructions and skills, and use it to author and build this collection. The source lives in `.skillset/`; the complete, installable versions land in `skills/`.

Three references keep the instruction work grounded:

- [Instruction Selection](.skillset/shared/references/instruction-selection.md): does this directive earn its place?
- [Instruction Placement](.skillset/shared/references/instruction-placement.md): where should it live?
- [Agentish](.skillset/shared/references/agentish.md): how do we make the intended behavior clear?

`agentish-styleguide` uses these for writing; `minority-report` uses them for review. Each gets its own bundled references, so you can install either on its own. `people-words` keeps its guidance separate and focused on expression.

`minority-report` also draws on [OpenAI's Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [Anthropic's Claude API prompt audit](https://github.com/anthropics/skills/tree/main/skills/claude-api), with profiles for GPT-6 Astra and Claude Fable. Those profiles load when relevant; a model name or keyword match isn't evidence of a problem.

We use the guidance here, too. Our generated `AGENTS.md` and `.claude/CLAUDE.md` route substantive instruction changes through a scoped self-review. You can read the [review notes](docs/reviews/2026-09-12-instruction-review.md) and [follow-up corrections](docs/reviews/2026-09-12-scope-and-pr-review.md), including what the first pass missed.

## Working on the collection

Use Bun 1.4.0. Skillset is pinned to `@skillset/cli@0.26.1`.

```bash
bun install --frozen-lockfile --ignore-scripts
bun run skillset new skill my-skill --yes
```

Edit `.skillset/skills/my-skill/SKILL.md` and keep its supporting files alongside it. To rebuild and check your work:

```bash
bun run skillset change status
bun run build
bun run check
```

Record meaningful changes through Skillset's change commands, using the scope reported by `change status`. Commit source, change records, and generated output together. The [publishing guide](docs/publishing.md) covers change evidence, release commands, tests, and compiler details.

| Path | What lives there |
| --- | --- |
| `.skillset/skills/` | Editable skills and their supporting files |
| `.skillset/shared/references/` | Shared instruction conventions |
| `.skillset/partials/repository.md` | Source for our repository instructions |
| `.skillset/rules/` and `.skillset/_claude/` | Wrappers selecting the generated instruction files |
| `.skillset/changes/` | Change and release records |
| `skills/` | Generated skill bundles and their `skillset.lock` |
| `AGENTS.md`, `.claude/CLAUDE.md`, and root `skillset.lock` | Generated repository instructions and ownership tracking |
| `skillset.yaml` | Build configuration |

Edit the source and rebuild; let Skillset manage the generated files. Building doesn't publish or install anything.

## License

[MIT](LICENSE). Use what helps, make it your own.
