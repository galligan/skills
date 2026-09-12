# mg skills

A few skills for getting better work out of agents and better words out of them, too. These grew out of how I work with Claude and Codex. Take the ones that help.

## What's in here 🔎

- `minority-report`: Audit agent instructions for conflicts, unnecessary work, and unintended consequences.
- `agentish-styleguide`: Write skills, prompts, and other agent instructions with clear behavior and boundaries.
- `people-words`: Drop mannered prose while keeping the substance, technical detail, and your voice.

[Meet the skills](docs/skills.md) for why each one exists, when to use it, and what to expect.

## Install a skill 📦

Each directory under `skills/` is a complete bundle. You don't need Bun or Skillset to use one.

> These skills are currently in [PR #1](https://github.com/galligan/skills/pull/1). The examples below use `main` and apply once it merges. To try the preview, give your agent the PR link and ask it to install from that branch instead.

### Codex

Paste this into a local Codex session:

```text
$skill-installer Install people-words from https://github.com/galligan/skills/tree/main/skills/people-words
```

Swap `people-words` for `minority-report` or `agentish-styleguide` throughout the prompt to choose another skill. Codex's [built-in installer](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use) accepts skills from other GitHub repositories. If the new skill doesn't appear, restart Codex.

### ChatGPT desktop

Open a local Codex task in the desktop app and paste:

```text
Use Skill Installer to install people-words from
https://github.com/galligan/skills/tree/main/skills/people-words
```

You can find **Skill Installer** in the app's Skills list. OpenAI supports [standalone skills in the desktop app](https://learn.chatgpt.com/docs/build-skills). For ChatGPT on the web or mobile, installation goes through [plugins](https://learn.chatgpt.com/docs/plugins); this collection isn't packaged as a plugin yet.

### Claude Code

Paste this into Claude Code:

```text
Install people-words from
https://github.com/galligan/skills/tree/main/skills/people-words
for my personal use in Claude Code. Download the complete skill directory,
including its supporting files, into ~/.claude/skills/people-words without
cloning the repo. If it's already installed, show me the differences
before replacing it. Confirm where it landed and how to invoke it.
```

Then try `/people-words`. Swap the skill name throughout the prompt to install either of the others. For a project-only install, use `.claude/skills/people-words` inside that project instead.

Claude Code loads standalone skills from these [native skill folders](https://code.claude.com/docs/en/skills#where-skills-live). Its [`/plugin install` command](https://code.claude.com/docs/en/discover-plugins#install-plugins) is for packaged plugins; the prompt above installs the standalone bundle directly.

### Prefer `npx skills`?

That works too:

```bash
npx skills add galligan/skills --list
npx skills add galligan/skills --skill people-words
```

Replace `people-words` with `minority-report` or `agentish-styleguide` as needed.

### A note on requirements

`people-words` and `agentish-styleguide` need no external tools. `minority-report` uses Python 3.10+ for discovery and `jsonschema` for validating and rendering reports. Its [skill instructions](skills/minority-report/SKILL.md) cover setup; installing the skill doesn't install Python dependencies.

## How these are made

I use [Skillset](https://github.com/outfitter-dev/skillset) to author and build the collection. The source lives in `.skillset/`; the complete, installable versions land in `skills/`.

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
