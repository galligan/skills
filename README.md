# Matt Galligan's Skills

A few skills for getting better work out of agents—and better words out of them, too. These grew out of how I work with Claude and Codex. Take the ones that help.

## What's in here 🔎

| Skill | What it's for | Try asking |
| --- | --- | --- |
| [Minority Report](skills/minority-report/SKILL.md) | A second opinion on your agent instructions. Finds conflicts, unnecessary work, and rules with unintended consequences, then proposes changes with evidence. | “Use Minority Report to audit this repo's agent instructions.” |
| [Agentish](skills/agentish-styleguide/SKILL.md) | A language guide for agents. Helps you write skills, prompts, agent definitions, and tool descriptions with clear behavior and boundaries. | “Use Agentish to help me write this skill.” |
| [People Words](skills/people-words/SKILL.md) | Less mannered prose. More substance. Keeps your register and the technical detail, without making everything sound like a press release. | “Use People Words and take another pass at that.” |

Minority Report produces **the agent's minority report**. Yes, that's the reference. It can review one file, a skill, a repo, a specific diff, or a broader set of projects. Run it without a scope and it'll help you choose. A clean report is fine; dissent isn't a quota.

Agentish is for instructions you give agents. People Words is for what they write back to people: replies, docs, and other prose. Use it from the start or midstream when the writing gets a little much.

## Install a skill 📦

Each directory under `skills/` is a complete bundle. You don't need Bun or Skillset to use one.

> These skills are currently in [PR #1](https://github.com/galligan/skills/pull/1). The examples below use `main` and apply once it merges. To try the preview, give your agent the PR link and ask it to install from that branch instead.

### Ask Codex

Paste this into a local Codex session:

```text
$skill-installer Install people-words from https://github.com/galligan/skills/tree/main/skills/people-words
```

Swap `people-words` for `minority-report` or `agentish-styleguide` throughout the prompt to choose another skill. Codex's [built-in installer](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use) accepts skills from other GitHub repositories. If the new skill doesn't appear, restart Codex.

### Ask Claude Code

Paste this into Claude Code:

```text
Install the people-words skill from https://github.com/galligan/skills
for my personal use in Claude Code. Copy the complete skills/people-words
directory from main into ~/.claude/skills/people-words, including all
supporting files. If it's already installed, show me the differences
before replacing it. Confirm where it landed and how to invoke it.
```

Then try `/people-words`. Swap the skill name throughout the prompt to install either of the others. For a project-only install, use `.claude/skills/people-words` inside that project instead. These are [Claude Code's native skill locations](https://code.claude.com/docs/en/skills#where-skills-live).

### Do it yourself

Clone the repo, then copy the skill you want into your agent's skills folder. For example, to install People Words for your personal use in Claude Code:

```bash
git clone https://github.com/galligan/skills.git galligan-skills
mkdir -p ~/.claude/skills
cp -R galligan-skills/skills/people-words ~/.claude/skills/
```

Use the copy command for a fresh install; if the destination already exists, compare the two before replacing it.

| Agent | Personal skills | Project skills |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.agents/skills/` | `.agents/skills/` |

Copy the **whole skill directory**, including its references and scripts. The personal paths apply across projects on that machine; project paths are relative to the repo where you'll use the skill. See the native [Claude Code](https://code.claude.com/docs/en/skills#where-skills-live) and [Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) docs for discovery details.

**Using ChatGPT?** The Codex instructions above are for local Codex sessions, including in the desktop app. They don't install a skill into ChatGPT on the web or your phone. ChatGPT's shared install route uses [plugins](https://learn.chatgpt.com/docs/skills-and-plugins); this repo currently ships individual skill folders.

### Prefer `npx skills`?

That works too:

```bash
npx skills add galligan/skills --list
npx skills add galligan/skills --skill people-words
```

Replace `people-words` with `minority-report` or `agentish-styleguide` as needed.

### A note on requirements

People Words and Agentish need no external tools. Minority Report uses Python 3.10+ for discovery and `jsonschema` for validating and rendering reports. Its [skill instructions](skills/minority-report/SKILL.md) cover setup; copying the folder doesn't install Python dependencies.

## How these are made

I use [Skillset](https://github.com/outfitter-dev/skillset) to author and build the collection. The source lives in `.skillset/`; the complete, installable versions land in `skills/`.

Three references keep the instruction work grounded:

- [Instruction Selection](.skillset/shared/references/instruction-selection.md): does this directive earn its place?
- [Instruction Placement](.skillset/shared/references/instruction-placement.md): where should it live?
- [Agentish](.skillset/shared/references/agentish.md): how do we make the intended behavior clear?

Agentish uses these for writing; Minority Report uses them for review. Each gets its own bundled references, so you can install either on its own. People Words keeps its guidance separate and focused on expression.

Minority Report also draws on [OpenAI's Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [Anthropic's Claude API prompt audit](https://github.com/anthropics/skills/tree/main/skills/claude-api), with profiles for GPT-6 Astra and Claude Fable. Those profiles load when relevant; a model name or keyword match isn't evidence of a problem.

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
