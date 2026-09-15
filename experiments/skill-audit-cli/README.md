# Skill audit CLI experiment

This spike tests whether a thin skill plus deterministic tooling helps an agent produce a useful skill-maintenance audit. It does not migrate Redliner or publish a package.

The package is authored, tested, and bundled with Bun, but the distribution runs on Node. That lets npm/npx launch it without a separate Bun installation. A compiled native Bun executable would need platform-specific packaging; this prototype has no requirement that justifies that extra work.

The tool inventories explicit filesystem roots and emits evidence. It does not rank skill quality, infer actual usage, fetch updates, read credentials, or modify skills. Native catalogs, profile usage data, memories, and exports can supplement its output. Those sources remain optional and provider-specific.

The package name is provisional and private. Use a local packed tarball for the npx test. Do not run an unverified public package of the same name.

```sh
bun test
bun run build
mkdir -p /tmp/skill-audit-package
npm pack --pack-destination /tmp/skill-audit-package
npm exec --yes --package=/tmp/skill-audit-package/skill-audit-lab-0.0.0.tgz -- skill-audit-lab --help
```

The canonical prototype skill is `.skillset/skills/skill-audit/`; Skillset generates its public-layout copy. The generated copy is experimental and not installed by this experiment.

## Trial

1. Verify inventory behavior on temporary fixtures: canonical aliases, broken links, identical copies, same-name divergent files, externally sourced entries, and unknown ownership.
2. Run the packed Node executable from an unrelated temporary directory to prove it does not require the authoring checkout or Bun runtime.
3. Give a reviewer the skill, inventory, and a small evidence brief. Require recommendations with evidence and explicit limits. Read-only audit only.
4. Have the coordinator judge findings against fixture ground truth and scoped real inventory. Do not expose fixture answers to the trial reviewer.
5. Record the actual model/effort, inputs, outputs, corrections and limits. A single successful run is feasibility evidence, not a comparison proving a smaller model matches a frontier model. A later comparison should hold inputs constant and distinguish tools-only, skill-only, and combined conditions.

## Potential shared code

Canonical-path identity, provenance evidence, fingerprints, coverage and result validation overlap Redliner. This experiment does not port its instruction parser, exclusions, ownership rules, or review schema. Extract shared modules only after both consumers demonstrate the same contract. Provider-specific discovery and metric meanings must remain explicit.

External dependencies belong in the skill's declared requirements. If a CLI eventually becomes required, publish and pin a real package/version before presenting npx as an installation route. An npx CLI serves environments with Node and a shell; it does not by itself provide tools to web/mobile harnesses. Keep the audit workflow usable through native tools there.

## Observed results

The September 15, 2026 trial passed seven tests with twenty assertions. A local tarball invoked through offline `npm exec` from outside this checkout wrote both fixture and real inventory reports under Node 26.7.0. Node 22 is the declared minimum and has not been separately exercised.

The package smoke test caught a silent startup failure caused by npm's executable symlink. The corrected entrypoint resolves both paths; its regression test verifies that the report exists and contains the expected record. Unexpected skill-file resolution errors now appear in coverage. Output guards cover scanned roots and canonical skill directories reached through symlinks.

The bounded real scan found 83 entrypoints backed by 81 canonical files, three broken links, and two alias pairs. It left 77 provenance classifications unknown. That supports using the collector to gather facts and directing the agent to enrich them from installation history; the collector alone does not produce a maintenance verdict. Plugin-cache discovery and native usage metrics were outside this run.

The instruction review corrected the trial format to retain run conditions and coordinator adjudication. No smaller-model comparison has been performed, so these results establish packaging and inventory feasibility only.
