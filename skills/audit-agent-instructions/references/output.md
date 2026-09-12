# JSON, validation, and presentation

Use one review JSON per reviewer, then one consolidated JSON for the audit. Discovery and findings are separate artifacts: candidate signals never become findings automatically.

## Paths and commands

Run commands from the audit workspace with paths to this skill's scripts. Examples below abbreviate that prefix as `scripts/`. Python 3.10+ is required. Discovery has no third-party dependencies; validation, consolidation, rendering, and their tests use `jsonschema` from `requirements.txt`. An isolated virtual environment is sufficient; `uv run --with jsonschema python ...` also works if uv is already available.

```sh
python scripts/discover.py /path/to/project --output audit/map.json
python scripts/validate.py audit/reviewer-a.json --map audit/map.json
python scripts/consolidate.py audit/reviewer-a.json audit/reviewer-b.json \
  --map audit/map.json --output audit/findings.json
python scripts/render.py audit/findings.json --output audit/report.md
python scripts/render.py audit/findings.json --output -
```

`validate.py` checks one review but does not require that reviewer to cover the entire map. `consolidate.py` requires the union of reviewer coverage to account for every mapped file. Conflicting coverage dispositions and duplicate finding IDs must be resolved. Single-reviewer audits use the same pipeline with one input.

Consolidation defaults to `audit/findings.json`; always link or state its actual path in the final response. The JSON includes all accepted findings, reviewer names, the complete discovery map and exclusions, one GitHub ownership context, per-file repository affiliation and per-remote relationships, per-file coverage, coverage counts, unresolved references, and rejected candidates with adjudication reasons. Unknown ownership evidence remains explicit. [consolidated.schema.json](consolidated.schema.json) defines this artifact; [review.schema.json](review.schema.json) defines reviewer inputs.

Coverage proves that files were accounted for, not that judgment was correct. A recorded missing/blocked reference is an audit limitation, not evidence that the referenced instruction is safe or absent. The final response should distinguish a completed review of accessible scope from unresolved material.

## Evidence and patches

Evidence paths and existing diff targets must be mapped canonical files. Add a newly discovered file or a remote-document snapshot to `map.json` with its current SHA-256 and line count before using it. Preserve source URLs alongside snapshot evidence. Do not refresh a changed fingerprint merely to make validation pass: recheck the affected finding first.

Quote each inclusive line range exactly, without a trailing newline. Diff headers may use absolute mapped paths or unambiguous `a/` and `b/` relative suffixes. Absolute paths avoid ambiguity across multi-project audits. Include real unified-diff hunk counts and positions; the checker verifies source context in memory and never changes audited files. New-file proposals use `/dev/null` and an absent absolute destination. File renames require separate delete/add proposals. Proposed diffs still need repository-specific tests if later approved and applied.

The checker verifies evidence and patch structure, not the wisdom of a proposal or actual harness behavior. Reviewer judgment must identify every safety/authority/verification decision; the script enforces the obvious verification and confirmation categories but cannot infer all consequences from prose.

## Coordinator adjudication

Keep reviewer returns intact when a coordinator rejects or changes a candidate. Pass `--adjudication audit/adjudication.json` using this shape:

```json
{
  "A-003": {
    "action": "exclude",
    "reason": "The surrounding paragraph already scopes this requirement."
  },
  "B-007": {
    "action": "override",
    "reason": "The proposed change narrows a required review gate.",
    "changes": {
      "decision_required": true,
      "decision_reason": "Owner must decide whether the remaining check is sufficient."
    }
  }
}
```

Overrides replace complete top-level fields and preserve the finding ID. Accepted overrides are revalidated. Rejected candidates remain in `excluded_findings`; their evidence/diffs are retained as unaccepted proposals and are not advertised as validated. Record alternative or overlapping proposals in `related_findings` and explain the choice in `smallest_change`.

## Complete output

The renderer does not truncate or impose a finding limit. It separates decisions from routine proposals, then uses H2 projects and H3 files. Within each file it ranks by severity, expected improvement, reach, and confidence. Coverage follows the findings, along with an Ownership signals section for included files whose `repository_affiliation` is `has_external_remote` or `unknown`, then exclusions and unresolved material. The section shows the authenticated identity context and each GitHub remote's explicit relationship. Ownership signals are advisory and do not reduce finding or coverage counts.

Thread delivery can introduce a short overview, then include the complete rendered report. If that exceeds the channel's limits, deliver the full Markdown file and consolidated JSON; explain the limit rather than quietly returning only high-priority findings. External publishing is a separate destination-specific step. Verify literal code-block content after conversion, especially when quoted instructions themselves contain Markdown fences.
