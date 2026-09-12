# Publishing individual skills

Author each skill under `.skillset/skills/<name>/`. Keep reusable conventions under `.skillset/shared/references/` and declare the files a skill needs through `resources`. Skillset generates the complete public counterpart under `skills/<name>/`; commit the generated output with its source. Consumers receive the skill directory and all declared supporting files.

## Build configuration

Released `@skillset/cli@0.26.1` supports this configuration:

```yaml
compile:
  targets: [codex]

codex:
  skills:
    path: skills
```

No plugin or marketplace declaration is needed. Keep provider-native source islands and plugin sources out of this skills-only repository so they do not introduce additional output roots.

This uses the Codex renderer at a generic public path. The release has no provider-neutral target. Review any provider-specific frontmatter or services when adding another skill; a directory path does not establish compatibility with every agent.

## Validation

```bash
bun run build
bun run check
bun run skillset check --only outputs
```

CI runs `bun run check` for source and generated-output validation, then `bun run check:changes --since origin/main` for skill change coverage. Released Skillset 0.26.1 also applies compiler-package Changesets rules in `check --ci`; those npm release rules do not apply to this skills-only repository. The upstream fix is tracked in [SET-535](https://linear.app/outfitter/issue/SET-535).

Skillset identifies source units by selector. Renaming a skill is a removal plus an addition: record both selectors and commit removal of the old generated directory together with the new source, output, and lock. Refresh pending change evidence after source edits, then check against the PR base. For Minority Report, the rename record covers `skill:audit-agent-instructions` and `skill:minority-report`.

Skillset owns the generated files through `skills/skillset.lock`. Its checks detect edits to generated files, while `skillset diff` previews changes from canonical source. Do not hand-edit or remove the lock to silence drift.

The generated Minority Report bundle contains 19 skill-local files and three declared shared references. Skillset copies the shared references into the installed skill, rewrites shared-resource links in `SKILL.md` to bundle-relative links, and tracks the resource content in `skills/skillset.lock`. Put `shared:` links in `SKILL.md`; version 0.26.1 does not rewrite those aliases inside skill-local supporting Markdown. No private repository access is needed to use them.

Agentish contains its entrypoint, OpenAI metadata, full license, and the same three shared references: Instruction Selection, Instruction Placement, and Agentish. People Words contains only its entrypoint, OpenAI metadata, and full license. Neither new skill requires external tools or services for its guidance; project-specific editing and factual verification use available tools and sources.

The September 12, 2026 validation checked payload completeness and link resolution. Separate disposable fixtures verified generated-output and canonical-source drift detection. The repository has no parallel provider or plugin output directories.

## Minority Report runtime and tests

Discovery requires Python 3.10+. Validation, consolidation, rendering, and tests also require `jsonschema`, declared in the skill's `requirements.txt`. Install dependencies in an isolated environment outside the skill source directory. If uv is available:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --with jsonschema python -m unittest discover \
  -s .skillset/skills/minority-report/tests
```

The compiler copies sibling files, including runtime debris if it exists. Keep `__pycache__`, `.pyc`, and virtual environments out of source skill directories. Tests above disable bytecode generation.

## Distribution

After the source and generated collection are published, users can select a skill with:

```bash
npx skills add galligan/skills --skill minority-report
```

This installs an individual skill. It does not install Python dependencies or supply external tools, credentials, plugin services, or permission to perform the skill's actions. Requirements are documented inside each skill.

Publication, user installation, and runtime activation remain separate actions from a successful build. This layout does not depend on the broader Skillset plugin or marketplace work.
