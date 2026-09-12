# galligan/skills

Author shareable skills with Skillset. Distribute complete individual skills from `skills/`.

## Source ownership

- Edit skill source under `.skillset/skills/<name>/` and workspace configuration in `skillset.yaml`.
- Edit reusable authoring references under `.skillset/shared/references/`. If an installed skill needs a shared reference, declare that reference in the skill’s `resources` so Skillset includes it in the generated bundle.
- MUST NOT hand-edit generated files under `skills/`, including `skills/skillset.lock`. Change the source and rebuild.
- Keep the single public output root configured by `codex.skills.path: skills`. Do not add plugin bundles or parallel provider output roots.
- If an installed skill needs a file, include that file in the generated skill bundle.
- Document each skill’s required external tools and services.
- An installed skill must work without the authoring checkout or undeclared plugin services.
- Keep credentials and private machine paths out of public skill content. Keep Python bytecode and virtual environments out of source skill directories because the compiler copies sibling files.

## Authoring and communication

- Before adding or reviewing a persistent directive, apply [Instruction Selection](.skillset/shared/references/instruction-selection.md) to decide whether the directive earns its place.
- When choosing or changing an instruction’s owning surface, use [Instruction Placement](.skillset/shared/references/instruction-placement.md).
- When writing skills, agent definitions, prompts, or other agent-facing instructions, use [agentish-styleguide](.skillset/skills/agentish-styleguide/SKILL.md). It routes to the shared [Agentish language guide](.skillset/shared/references/agentish.md).
- For human-facing replies and prose, apply [People Words](.skillset/skills/people-words/SKILL.md). Preserve the intended audience and document form; Agentish's controlled instruction conventions do not apply to ordinary prose.
- For a requested systematic instruction audit, use [Minority Report](.skillset/skills/minority-report/SKILL.md).

Use the pinned runtime and compiler versions. Follow [README.md](README.md#authoring) for build and change-record commands and [publishing.md](docs/publishing.md) for validation and distribution. Record version changes through Skillset’s change and release commands. Commit source, change evidence, and generated output together.

Use a branch and review the diff before committing. Publishing, installation, and activation are separate from building.
