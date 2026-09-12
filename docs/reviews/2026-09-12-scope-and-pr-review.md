# Scope selection and PR review

Follow-up to [the initial self-review](2026-09-12-instruction-review.md). The earlier review established structural consistency but missed the mismatch between People Words' declared activation and the repository's default, and did not adequately separate expression from behavioral policy. This follow-up corrects both.

## Scope behavior

Minority Report now distinguishes named targets from supporting context. Explicit file, skill, repository, PR, or change-set requests establish scope without another confirmation. A bare invocation uses lightweight directory and Git context to recommend a bounded scope, then asks through the harness's input tool or ordinary conversation and waits. Home or scratch directories never imply a recursive sweep. Change-focused reviews record their comparison and distinguish uncommitted work from branch commits.

Supporting files can explain a finding but do not become patch targets without an expanded user scope. Their coverage is marked `context_only`. The scope guide also explains non-interactive runs: a missing scope is reported as required, never inferred from a timeout.

## Review decisions

| Feedback | Resolution |
| --- | --- |
| People Words activation disagrees with root routing | Keep the deliberate repo style choice and declare governing-project opt-in in the skill description and body. |
| People Words adds verification and task-control policy | Remove instructions to verify, choose when to ask, proceed on assumptions, or create artifacts. Retain only expression, preservation of evidence/uncertainty, and audience/form. Those behavioral decisions belong to the task's governing instructions. |
| Model names compete in descriptions | Remove them from both descriptions; preserve model names and evidence guidance in bodies/profiles. Audit and authoring descriptions now explicitly distinguish their jobs. |
| Attachment history in the public Fable profile | Replace it with a public-source verification date. Attachment provenance remains in the review record. |
| Literal YAML in generated Claude instructions | Confirmed compiler limitation: headerless source still generates YAML delimiters and `{}`. Retain the descriptive header and document the limitation instead of hand-editing generated output. |
| Major bump and stale scaffold scopes | Ignore the superseded major and bootstrap records through the CLI, retain their history, and replace the rename with a minor record covering both selectors. Preview verifies `0.2.0` and excludes scaffold scopes from actual releases. |
| Inconsistent normative vocabulary | Use ordinary direct prohibitions consistently in the repository partial. This is consistency cleanup, not a claim that capitalization alone caused bad behavior. |
| Restore CI's combined command after the upstream fix | Publishing notes now call for verifying a released SET-535 fix before restoring `check --ci` with equivalent coverage. |

The PR and commit history remain intact pending the owner's decision about splitting or stacking. No history rewrite is part of these review fixes.

The [Codex P1 thread](https://github.com/galligan/skills/pull/1#discussion_r3997668892) is addressed by the explicit project activation contract and the removal of hidden behavioral policy, rather than by an argument that intentional routing alone resolved the mismatch.

## Focused verification

An independent scoped Minority Report checked the changed entrypoints, People Words policy boundary, and repository opt-in. It sharpened one precedence rule: an explicit PR or exact comparison takes precedence over incidental dirty working-tree state. The follow-up confirmed unambiguous paths for bare repository, bare skill directory, home/scratch directory, and explicit PR requests. No remaining finding was identified in that focused check. No live question UI or cross-model behavioral evaluation was run.

All 55 existing Python tests pass. Source/output validation and repeat-build checks pass, all 31 local bundle links resolve in isolated copies, and the release preview verifies the intended minor version without scaffold releases.
