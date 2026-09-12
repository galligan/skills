# Publishing individual skills

Author each complete skill under `.skillset/skills/<name>/`. Skillset generates the public counterpart under `skills/<name>/`; commit the generated output with its source. Consumers receive the skill directory and its scripts, references, schemas, and other supporting files.

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

Skillset owns the generated files through `skills/skillset.lock`. Its checks detect edits to generated files, while `skillset diff` previews changes from canonical source. Do not hand-edit or remove the lock to silence drift.

The September 12, 2026 migration verified all 19 source files, including the full MIT license text, in the generated skill. Seventeen payload files were byte-identical; `SKILL.md` retained its body and `agents/openai.yaml` retained its values, with generated metadata and YAML normalization. Separate disposable fixtures verified generated-output and canonical-source drift detection. The repository has no parallel provider or plugin output directories.

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
