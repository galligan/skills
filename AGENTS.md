# galligan/skills

This repository authors Matt Galligan's shareable skills with Skillset. The public plugin is `mg-skills`; the marketplace is `galligan`.

## Source and generated output

- Author skills in `.skillset/plugins/mg-skills/skills/<name>/SKILL.md`.
- Edit root `skillset.yaml` for workspace configuration and the plugin-local `skillset.yaml` for plugin metadata.
- `plugins/`, `.claude-plugin/marketplace.json`, and `.cursor-plugin/marketplace.json` are generated. Rebuild them; do not hand-edit them.
- Keep copied references, scripts, and assets inside each installed skill. Declare shared inputs with Skillset `resources` so the compiler copies them into the generated skill.
- Skills intended for individual installation must work without plugin hooks, plugin-root files, or undeclared MCP servers. Document required tools and services in the skill.
- Keep public skill content independent of private machines, credentials, and user-specific paths.

## Workflow

Use the pinned Bun and Skillset versions from `.bun-version` and `package.json`.

```bash
bun install --frozen-lockfile --ignore-scripts
bun run skillset new skill <name> --in mg-skills --yes
bun run skillset change status
bun run build
bun run check
```

Use the scope returned by `change status` when adding a change record. Use Skillset's change and release commands for version authority; do not edit generated changelogs or locks. Commit source, change records, and generated output together.

Use a branch and review the diff before committing. Publishing, installation, and activation are separate from building. See `docs/publishing.md` for the current individual-skill distribution contract and tracked follow-up work.
