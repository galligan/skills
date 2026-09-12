# Matt Galligan's Skills

Shareable agent skills, authored with [Skillset](https://github.com/outfitter-dev/skillset) and distributed as complete directories under `skills/`.

## Skills

- [audit-agent-instructions](skills/audit-agent-instructions/SKILL.md): audit agent guidance for instruction conflicts, excessive triggers, unnecessary work, and premature approval gates. Includes its scripts, reference material, schemas, and tests.

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

## Layout

| Path | Purpose |
| --- | --- |
| `skillset.yaml` | Workspace metadata and the single `skills/` output configuration |
| `.skillset/skills/<name>/` | Editable skill source and all supporting files |
| `.skillset/changes/` | Skillset change and release evidence |
| `skills/<name>/` | Generated, self-contained skill for consumers |
| `skills/skillset.lock` | Generated ownership and drift tracking |

The Codex renderer emits this collection at a custom path. It preserves the audit skill's body and supporting content while normalizing metadata and its OpenAI sidecar; this is not a claim of provider-neutral rendering.

## Installation

Once these changes are published to the repository's default branch:

```bash
npx skills add galligan/skills --list
npx skills add galligan/skills --skill audit-agent-instructions
```

See [publishing notes](docs/publishing.md) for the build contract, validation, and runtime requirements. Building locally does not publish or install anything.

## License

[MIT](LICENSE).
