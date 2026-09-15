# mg skills

Hey I'm [@mg](https://x.com/mg). Here are a few skills for getting better work out of agents and better words out of them, too. These grew out of how I work with my agents. Take the ones that might help and give them a test run.

## The Skills 🔍

Check out [the skills](docs/skills.md) for why each one exists, when to use it, and what to expect. Here's the tl;dr:

### [`/redliner`](skills/redliner/SKILL.md)

Audit the instructions behind your agents for conflicts, stale workarounds, and accidental busywork. Especially useful with frontier models like GPT-6 Astra and Claude Fable, where older prompting tricks can get in the way.

🖍️ **Try:** Fire up a session with Astra or Fable, and tell them to run `/redliner` in a project, or globally across your system. And don't worry about wasting context, the skill has been designed to keep usage under control.

### [`/agentish`](skills/agentish/SKILL.md)

Help agents say more with less, without losing the plot. Agentish is a language style to use where agents are writing for other agents, e.g. `AGENTS.md`, `CLAUDE.md`, skills, and prompts.

✍🏻 **Try:** Ask your agent "How would you write @AGENTS.md using /agentish?"

### [`/people-words`](skills/people-words/SKILL.md)

When every detail is "load-bearing" and every insight is "hiding in plain sight," the agentisms have taken over. Cut the mannered prose while keeping the substance, technical detail, and your voice.

🤦🏻 **Try:** After seeing annoying outputs, just run `/people-words` and watch the agent speak more naturally.

## Installation 📦

<details open>
<summary><strong><code>npx skills</code></strong></summary>

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
Install the `/redliner` skill from https://github.com/galligan/skills/tree/main/skills/redliner into `~/.claude/skills/redliner`. Include all supporting files without cloning the repo. Check with me before replacing an existing installation.
```

Then invoke `/redliner`. Use `.claude/skills/redliner` for a project-only install. Swap the skill name and paths to install another.

</details>

Each skill is a complete bundle. You don't need Bun or Skillset to use one. ChatGPT web and mobile use [plugins](https://learn.chatgpt.com/docs/plugins); this collection currently ships standalone skills.

## How these are made 🛠️

I built [Skillset](https://github.com/outfitter-dev/skillset) to manage agent instructions and skills, and use it to author and build this collection. Source files for the skills live in [`.skillset/`](https://github.com/galligan/skills/tree/main/.skillset/); the complete, installable versions land in [`skills/`](https://github.com/galligan/skills/tree/main/skills/).

Three references keep the instruction work grounded:

- [Instruction Selection](.skillset/shared/references/instruction-selection.md): does this directive earn its place?
- [Instruction Placement](.skillset/shared/references/instruction-placement.md): where should it live?
- [Agentish](.skillset/shared/references/agentish.md): how do we make the intended behavior clear?

`agentish` uses these for writing; `redliner` uses them for review. Each gets its own bundled references, so you can install either on its own. `people-words` stays focused on expression.

We use the guidance here, too. Our generated `AGENTS.md` and `.claude/CLAUDE.md` route substantive instruction changes through a scoped Redliner review. The [review notes](docs/reviews/2026-09-12-instruction-review.md) and [follow-up corrections](docs/reviews/2026-09-12-scope-and-pr-review.md) show what the first passes found and missed.

## Working on the collection 🏗️

Use [Bun 1.4.0](https://bun.sh). Skillset is pinned to `@skillset/cli@0.26.1`.

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

## License 📝

[MIT](LICENSE). Use what helps, make it your own.
