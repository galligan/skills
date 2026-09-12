# Matt Galligan's Skills

Shareable agent skills, authored once with [Skillset](https://github.com/outfitter-dev/skillset) and packaged as **mg-skills** for Claude, Codex, and Cursor. The marketplace is **galligan**.

The repository is initialized; the first public skills are still to be added.

## Authoring

Use Bun 1.4.0. The compiler is pinned to `@skillset/cli@0.26.1` in `package.json` and `bun.lock`.

```bash
bun install --frozen-lockfile --ignore-scripts
bun run skillset new skill my-skill --in mg-skills --yes
```

Edit `.skillset/plugins/mg-skills/skills/my-skill/SKILL.md`. Keep the skill's runtime resources self-contained, using Skillset `resources` for shared inputs.

```bash
bun run skillset change status
bun run build
bun run check
```

Record meaningful changes with Skillset's change commands using the scope reported by `change status`. Use `release plan` and `release apply` to advance versions and changelogs. Commit source, release evidence, and generated output together.

## Layout

| Path | Purpose |
| --- | --- |
| `skillset.yaml` | Workspace configuration and the explicit `galligan` catalog |
| `.skillset/plugins/mg-skills/` | Canonical plugin metadata and skill source |
| `.skillset/changes/` | Skillset change and release evidence |
| `plugins/mg-skills/claude/` | Generated Claude plugin |
| `plugins/mg-skills/codex/` | Generated Codex plugin |
| `plugins/mg-skills/cursor/` | Generated Cursor plugin |
| `.claude-plugin/marketplace.json` | Generated Claude catalog, also used by the skills CLI for discovery |
| `.cursor-plugin/marketplace.json` | Generated Cursor catalog |

Generated output is committed for consumers. Edit `.skillset/` and the root configuration, then rebuild.

## Installation and publication

Once the repository and its first skills are published, the intended individual-skill flow is:

```bash
npx skills add galligan/skills --list
npx skills add galligan/skills --skill my-skill
```

The explicit catalog currently directs that discovery to the generated Claude skill tree. Individual skills offered through this route must be portable and self-contained; choosing another agent in the skills CLI does not recompile a provider-specific skill or install the rest of its plugin.

See [publishing notes](docs/publishing.md) for the verified discovery behavior, limitations, and tracked Skillset improvements.

## License

[MIT](LICENSE).
