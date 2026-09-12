# Discovery scope and provenance

The helper maps explicit files/directories. It reads instruction bodies only within that scope or through explicit local references reached from it. It does not search the home directory for projects, fetch remote URLs, execute commands in audited text, or infer a finding from a keyword match.

## Managed content

The default audit queue excludes:

- **skills.sh installations:** concrete skill installation paths associated with a project `skills-lock.json` or a global `.skill-lock.json`. Global metadata normally lives under `.agents/` or the configured XDG state directory. A matching name elsewhere in an authored source directory is insufficient to exclude that source.
- **Installed Claude, ChatGPT, and Codex plugins:** known runtime plugin directories, symlinks whose canonical targets enter those directories, and Claude plugin registry `installPath` entries. Custom agent home directories are considered when configured.
- **Plugin source components:** skill directories declared in `.claude-plugin/plugin.json` or `.codex-plugin/plugin.json`, and the conventional `skills/` directory beside such a manifest. Unrelated repository instructions remain in scope.
- **Bundled system skills and build/dependency artifacts:** recognized system-skill paths plus VCS, dependency, cache/build output directories that are not authored instruction entry points.

Exclusion means “outside this audit's default scope,” not “safe” or “well written.” The map records the path, reason, and provenance evidence. Links from authored instructions into excluded components remain visible, so reviewers can assess the authored routing instruction without reading the excluded component's body.

Missing or malformed metadata creates warnings. It does not make every global skill an authored skill, nor justify excluding every same-named directory. Copies without lock/registry/path evidence and unusual plugin layouts may remain unclassified. Review that uncertainty explicitly. If a locally maintained fork should be included despite installation metadata, establish its canonical authored source and record the intentional scope exception; do not broadly disable exclusions.

The skills.sh locations and lock structure are based on its [global lock implementation](https://github.com/vercel-labs/skills/blob/main/src/skill-lock.ts), [project lock implementation](https://github.com/vercel-labs/skills/blob/main/src/local-lock.ts), and [agent installation paths](https://github.com/vercel-labs/skills/blob/main/src/agents.ts). These metadata conventions can evolve; unknown formats should stay visible as limitations.

## Ownership signals for included files

After mapping, the helper performs read-only local Git inspection for included files. When a repository has a GitHub remote, it may use the authenticated `gh` session to read the current GitHub user and [visible organization memberships](https://docs.github.com/en/rest/orgs/orgs#list-organizations-for-the-authenticated-user). It does not require authentication, prompt for login, modify repositories, or exclude files based on this check.

The result describes remote-owner affiliation, not authorship. A Git-tracked file has `repository_affiliation: "has_external_remote"` and `possible_external_source: true` when at least one GitHub remote owner does not match the authenticated user or any visible organization. It remains in the review queue. Untracked files keep their enclosing repository and per-remote relationships but remain `unknown`. A file is also `unknown` when repository, remote, authentication, or API evidence is insufficient. Failures stay unknown rather than becoming an external classification.

Organization visibility can be limited by GitHub membership privacy and token permissions. Forks, mirrors, multiple remotes, mixed personal and organization ownership, or a repository checked out from somebody else's remote can produce a flag even when the user maintains the local instructions. Mixed remotes retain their individual relationships even when the aggregate result is unknown. Each recognized remote owner is classified as `authenticated_user`, `user_organization`, `not_in_known_affiliations`, or `unknown`. GitHub Enterprise hosts, SSH host aliases, and non-GitHub remotes are currently unknown rather than affiliated or external. The helper does not look up owner profiles, so `not_in_known_affiliations` does not claim whether that owner is a person or organization. Treat `possible_external_source` as a triage hint and report the recorded reason and remote relationships in the final output; do not treat it as proof about the file's author or owner.

An ownership excerpt has this shape:

```json
{
  "ownership_context": {
    "host": "github.com",
    "status": "available",
    "user": {"login": "example-user"},
    "organizations": {
      "status": "available",
      "logins": ["example-org"]
    },
    "reason": "Authenticated user and visible organizations were read successfully."
  },
  "files": [
    {
      "path": "/path/to/project/AGENTS.md",
      "ownership": {
        "repository_affiliation": "has_external_remote",
        "possible_external_source": true,
        "repository": "/path/to/project",
        "tracked": true,
        "remotes": [
          {
            "name": "upstream",
            "host": "github.com",
            "repository": "other-owner/project",
            "url": "https://github.com/other-owner/project",
            "owner": {
              "login": "other-owner",
              "relationship": "not_in_known_affiliations"
            }
          }
        ],
        "reason": "A tracked file has a remote outside known affiliations."
      }
    }
  ]
}
```

## References and coverage

The scanner recognizes common agent instruction entry files, local Markdown links, `@` imports, backtick Markdown paths, and uniquely resolvable Obsidian links. It records canonical aliases and terminates directory/link cycles. Resolve an ambiguous link manually rather than choosing a same-named file arbitrarily.

External URLs are recorded without fetching them. Use available authorized tools only when a linked document is relevant to instruction behavior. To add a fetched source, save a UTF-8 snapshot in the audit workspace, add its canonical path, SHA-256, and line count to `map.json`, and retain its URL in reviewer evidence. Update the link's status and target to reflect the resolved snapshot. Review remote plugin provenance before adding any body to the queue.

Prominent source-relative and project-root-relative references should be checked even when the scanner misses them. Shorthand, dynamic imports, provider-specific interpolation, and generated configurations may require manual resolution. Account for those discoveries in the map and coverage.

Candidate signals identify passages worth inspecting: broad-trigger wording, universal reads, required checks, and approval gates. They neither score severity nor prescribe a finding. Read whole applicable sections and inspect files with no candidate matches. Report inaccessible roots, unresolved references, and any traversal limit; the helper cannot certify semantic completeness.
