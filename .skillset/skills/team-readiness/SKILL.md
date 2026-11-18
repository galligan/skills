---
name: team-readiness
description: Check whether an agent team has the peer access, tools, and settings its roles require. Use for one-off or recurring read-only readiness checks. Not for live delivery tests, access changes, or incident investigation.
---

# Team Readiness

## Set the scope

1. Identify the checker account, the team in scope, and the authorized report destination. If no destination is specified, return the report in the requesting context only if it is authorized to receive the findings.
2. Use the owner-approved baseline if available: roles, required sender → recipient handoffs, and the tools, settings, and authorization each role needs. Use exact resource scope when a requirement names one.
3. If the baseline is missing or partial, report the authorized inventory as observations, not as verified requirements. Mark readiness for roles without a baseline **Unverified**. Do not infer required grants from the current grant list or assume that every agent needs access to every peer.

## Gather evidence

Use only authorized, read-only configuration or capability metadata. Do not read private histories or inspect credentials. Do not send probes, impersonate agents, request new access, or change integrations, settings, or schedules as part of this check.

| Check | Evidence | Limit |
| --- | --- | --- |
| Peer handoff | Sender-scoped metadata for the required sender → recipient grant or route | A grant is directional. It does not prove reverse access or live delivery. |
| Tool or integration | Inventory for the relevant agent and runtime; explicit scope metadata if the role needs authorization | A listed tool, plugin, or server does not prove authentication, resource access, or operation. An install or grant does not prove the tool is loaded in that runtime. |
| Setting | Effective value for the relevant agent, role, or environment | An organization default or a settings-page link does not prove the effective value. |

If the platform paginates a relevant inventory, read all pages within the authorized scope before claiming absence. If a source is unavailable, denied, partial, or scoped to the wrong identity, record the limit. Do not use a different identity or a private history to fill it in.

### Requirements and Devin tools

The check needs a platform with authorized read-only metadata sources. The skill itself requires no package, repository checkout, or plugin. Without a source for a check, report the check as **Unverified**.

On Devin, use `devin_self_grant_search` with `type: bot` and `held_only: true` for the checker's held outbound peer grants. Follow the returned cursor with `after` if present. The `mcp` and `plugin` types with `held_only: true` show held grants, not the full runtime inventory. Use `mcp_list_servers` for the current session's visible MCP catalog. None of these calls establishes another agent's configuration.

## Classify and report

- **Verified configuration:** Evidence from the right scope matches the requirement. State exactly what was verified.
- **Gap:** An authoritative setting disagrees with a requirement, or a complete, correctly scoped inventory lacks a required capability. State the affected role or handoff and recommend the smallest next action to its owner.
- **Unverified:** Evidence or expectations are missing, incomplete, inaccessible, or out of date. State what authorized evidence would resolve the uncertainty. Mark live delivery **Unverified** in a metadata-only check.

Report the time, checker scope, and coverage limits. Summarize verified configuration and list actionable gaps and unknowns with their sources. If an earlier authorized report is available, call out changes only where requirements, identity, and evidence scope are comparable. Do not present a partial inventory as an all-clear.

Keep the report in the authorized destination. Do not include credentials, raw tool output, or team identifiers in public artifacts. Recommend changes without applying them.
