# Claude Fable review profile

Informed by Anthropic's [Claude API skill](https://github.com/anthropics/skills/tree/main/skills/claude-api), especially its [prompt audit](https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/prompt-audit.md) and [model migration guidance](https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/model-migration.md). Checked against the public source on September 12, 2026. The reviewed migration guidance distinguishes Fable versions, including 5.1. Confirm the actual target version before transferring a claim.

Apply [model-review.md](model-review.md) and the common rubric. This profile adapts the source's useful checks without adopting blanket deletion rules, numerical quotas, or its separate reporting format.

## Review candidates

- Trace pressure language, planning rituals, repeated reminders, and prohibition clusters to their purpose. Preserve explicit policies and demonstrated mitigations; investigate whether obsolete steering now causes misrouting or unnecessary work.
- Check whether examples establish a required output contract or unnecessarily force one style onto unrelated tasks. Preserve examples with a current format-sensitive purpose.
- Compare tool descriptions with actual behavior: activation boundaries, parameters, side effects, limits, and failure modes. Add missing contract detail when it changes tool selection or use. Do not impose a minimum sentence count or remove useful examples solely because they are examples.
- If request-building code is in scope, inspect prefill, JSON scaffolding, thinking configuration, sampling parameters, forced tool selection, and surrounding retry/parser code. Verify the exact model and provider support before claiming an error or recommending a replacement. Audit reachable paths and dependent tests, not just the prompt string.
- Check communication guidance against the target's behavior and the harness's visibility. Silence can come from the UI or configuration as well as a prompt. Prefer conditions for useful updates and formatting over blanket suppression.

## Fable-specific cautions

The reviewed Fable 5.1 migration guidance reports that a direct instruction against mannered prose can help. Preserve the user's chosen register and direct prohibition; do not delete it as a generic style tic. That guidance also describes under-formatting and fewer progress updates, so an anti-formatting or silence rule needs investigation rather than automatic preservation.

The migration guidance qualifies earlier advice to delete verification prompts: some Fable workflows may still benefit from them. Do not transfer an older Claude generation's recommendation, or Astra's behavior, to Fable without evidence. When prompt-audit heuristics conflict with a per-version migration note, resolve the applicable version and verify the behavior; do not choose whichever source permits more deletion.
