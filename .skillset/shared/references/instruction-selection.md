# Instruction Selection

Every persistent directive must earn its place. Apply these questions in order — the first decisive answer sets the disposition. Use this guide before writing a new directive and when auditing existing ones.

## The questions

1. **Can software enforce it?** If a linter, formatter, test, hook, CI check, or permission boundary can guarantee the behavior, move enforcement there. Keep only the upstream decision the agent needs (the invariant and its safe path), never the tool's full configuration.
2. **Is it model-specific?** If it compensates for one model's current habits (double-check reminders, forced subagent counts, approval rituals, planning mandates), default to removal — most model workarounds outlive the behavior they patched. If the accommodation is still required, keep it in an explicitly scoped block that names the model or provider, and give it a review date. Do not write it as universal policy.
3. **Does it apply to most work in this scope?** Subtree-only rules move to scoped files. Task-class-only procedures move to skills, with a terse routing line left behind only if routing needs it.
4. **Can the agent discover it cheaply and reliably?** Visible package scripts, ordinary repo layout, standard framework conventions, and formatter settings do not need restating. Exception: a non-obvious command with dangerous alternatives may earn persistence despite being discoverable.
5. **Does the model already know it?** Generic quality advice — write clean code, handle errors, test your changes — is a deletion candidate unless the repo gives those words a specific local meaning. If "simple" means something here, encode the meaning, not the word.
6. **Would removal cause a repeatable or high-consequence failure?** This is the strongest keep signal. Evidence: repeated historical agent mistakes, a known invariant, an expensive failure mode, an incident. A rule with no evidence is **preventive/unproven** — record that status rather than treating it as validated.
7. **Is it concrete enough to test?** If two competent readers could disagree on what compliance looks like, rewrite before keeping (see [Agentish](agentish.md)).
8. **Is it stated once?** Choose one authoritative surface. Duplicates across root files, scoped files, skills, and tool descriptions compete and drift.

## Dispositions

When a review records directive dispositions, use the following action and surface terms. The owning review contract determines which directives need records and whether these terms appear as fields or prose:

```yaml
action: keep | move | merge | rewrite | remove | investigate
target_surface: global | root | scoped | skill | tool_description | task_prompt | output_style | docs | linter | hook | test | ci | permissions | null
```

A proposed disposition does not authorize applying the change. Follow the owning review contract for evidence and decision requirements.

Model-specific accommodations that survive question 2 are recorded as `keep` or `rewrite` with the scoping block noted — there is no separate model surface. See [instruction-placement.md](instruction-placement.md) for what each surface owns.
