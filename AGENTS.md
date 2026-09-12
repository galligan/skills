# galligan/skills

This repository authors Matt Galligan's shareable skills with Skillset and distributes complete individual skills from the root `skills/` directory.

## Source and generated output

- Author skills in `.skillset/skills/<name>/SKILL.md` and edit root `skillset.yaml` for workspace configuration.
- Keep scripts, references, schemas, tests, and other resources inside each skill directory. Installed skills must work without plugin hooks, plugin-root files, or undeclared MCP servers; document required tools and services.
- `skills/` is generated and committed for consumers. Rebuild it; do not hand-edit its files or `skills/skillset.lock`.
- The pinned compiler uses the Codex renderer with `codex.skills.path: skills`. This is one public collection, not a provider-neutral renderer or a plugin marketplace. Do not add parallel provider output roots.
- Keep public skill content independent of private machines, credentials, and user-specific paths. Keep Python bytecode and virtual environments out of source skill directories; the compiler copies sibling files.

## Workflow

Use the pinned Bun and Skillset versions from `.bun-version` and `package.json`.

```bash
bun install --frozen-lockfile --ignore-scripts
bun run skillset new skill <name> --yes
bun run skillset change status
bun run build
bun run check
```

Use the scope returned by `change status` when adding a change record. Use Skillset's change and release commands for version authority; do not edit generated changelogs or locks. Commit source, change records, and generated output together. When comparing against a branch predating Skillset initialization, use a baseline commit that contains `skillset.yaml` with `--since`.

Use a branch and review the diff before committing. Publishing, installation, and activation are separate from building. See `docs/publishing.md` for the distribution contract and validation evidence.
