# Publishing individual skills

Author each skill under `.skillset/skills/<name>/`. Keep reusable conventions under `.skillset/shared/references/` and declare the files a skill needs through `resources`. Skillset generates the complete public counterpart under `skills/<name>/`; commit the generated output with its source. Consumers receive the skill directory and all declared supporting files.

## Build configuration

Released `@skillset/cli@0.26.1` supports this configuration:

```yaml
compile:
  targets: [claude, codex]

claude:
  skills: false

codex:
  skills:
    path: skills
```

No plugin or marketplace declaration is needed. Claude compilation is enabled only for repository instructions; standalone skills still use the single `skills/` output. The small `.skillset/_claude/CLAUDE.md` wrapper is the only provider-native source needed here.

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

The generated Minority Report bundle contains 22 skill-local files and three declared shared references. Its model-review guide and Astra/Fable profiles load only when relevant. Skillset copies the shared references into the installed skill, rewrites shared-resource links in `SKILL.md` to bundle-relative links, and tracks the resource content in `skills/skillset.lock`. Put `shared:` links in `SKILL.md`; version 0.26.1 does not rewrite those aliases inside skill-local supporting Markdown. No private repository access is needed to use them.

Agentish contains its entrypoint, OpenAI metadata, full license, and the same three shared references: Instruction Selection, Instruction Placement, and Agentish. People Words contains only its entrypoint, OpenAI metadata, and full license. Neither new skill requires external tools or services for its guidance; project-specific editing and factual verification use available tools and sources.

The September 12, 2026 validation checked payload completeness and link resolution. Separate disposable fixtures verified generated-output and canonical-source drift detection. The repository has no parallel provider skill or plugin output directories.

## Generated repository instructions

`.skillset/partials/repository.md` owns the shared guidance. `.skillset/rules/repository.md` includes it for Codex, producing `AGENTS.md`; `claude: false` prevents a redundant Claude rule. `.skillset/_claude/CLAUDE.md` includes the same partial for `.claude/CLAUDE.md`. Root `skillset.lock` tracks both outputs and their partial dependency; `skills/skillset.lock` continues to own standalone skills.

Claude Code supports [`.claude/CLAUDE.md` as a project instruction file](https://code.claude.com/docs/en/memory). Released Skillset 0.26.1 cannot use `claude.projectRoot: .` to emit a root `CLAUDE.md`; it rejects the repository-root destination. Use the supported location instead of an extra copy or symlink step.

The shared body uses explicit repository-root-relative code paths. Destination-aware `shared:` links work for portable instructions but are not rewritten correctly in the native Claude wrapper in 0.26.1. Do not introduce broken relative Markdown links into the shared body. Only the small repository partial is expanded at build time; the referenced skills remain conditionally loaded guidance.

Changing the partial requires a build and source/output checks. For substantive instruction changes, apply the scoped self-review described in the generated guidance. Document unresolved model-evaluation limits rather than claiming prose checks prove model behavior.

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
