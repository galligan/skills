---
description: Ask for and track human decisions in Slack with concise recommendations, scoped emoji choices, verified reactions, and one-line pending links. Use for Slack decision requests and follow-ups, not ordinary status updates or new approval workflows.
metadata:
  skillset.schema: "1"
  version: 0.1.0
name: slack-decisions
---

# Slack Decisions

Make decisions easy to answer without turning updates into permission checklists. This skill formats existing decision needs; it does not add approval gates, ownership handshakes, or review machinery. Existing repository, security, and release gates still apply.

## Tools and setup

Drafting needs no external tools. Sending and checking decisions requires an already-authorized Slack connection that can post messages, read the relevant message/thread, return real permalinks, and read reaction names with reactor user IDs. Prefer the harness's native Slack tool when available; otherwise use an equivalent existing MCP/API connection. No particular plugin is required.

Use the configured workspace, permitted channel/thread, and intended decider's Slack user ID. Resolve an ambiguous identity with the available user lookup. Do not hard-code personal IDs into the skill. Missing capabilities limit what can be sent or verified; report the limit and use an explicit text reply when reactions cannot be verified. Do not request secrets, change app scopes, or create polling automations, webhooks, custom apps, or buttons for this protocol.

Before relying on a surface feature, check current official Slack documentation and the actual sender's schema/help. The bundled [capability notes](references/capabilities.md) distinguish platform support from sender support and list the relevant API requirements.

## Write the ask

- Put each decision on its own physical line. Include a native `<@USERID>` mention of the intended decider, the question and exact scope, explicitly labeled emoji choices, a **bold recommendation**, and a brief reason. In Slack `mrkdwn`, bold uses `*single asterisks*`; use the verified dialect for other surfaces.
- Use distinct numbered alternatives (`:one:`, `:two:`, `:three:`) or symbols meaningfully tied to the options. Label every offered choice in that ask. Do not assume a global emoji permission grant or repeat permission history.
- Bind an authorization to the stated action and candidate: identify the relevant version, immutable revision/artifact, environment, or target when needed to distinguish it. A changed candidate or scope needs clarification; old reactions do not transfer.

Use these meanings when offering these symbols, always with the specific action labeled:

| Symbol | Meaning in this ask |
| --- | --- |
| `:large_green_circle:` | Go with the stated action. |
| `:large_yellow_circle:` | Pause or clarify the stated action. |
| `:red_circle:` | Stop the stated action. |
| `:rocket:` | Approve the **specified release** only. |
| `:white_check_mark:` | Looks good; continue the stated work. Not blanket release approval. |

Reactions attach to a whole message, not a line. Default to a separate anchored message for each reaction-based ask, then link those originals in a one-line-per-decision summary when useful. If several asks share one message, every offered emoji must be unique across the entire message and explicitly map to a decision and option. Never reuse a go/checkmark reaction ambiguously across decisions. If the mapping is ambiguous, ask for a text reply identifying the decision and option rather than interpreting the reaction.

Keep the scope, choices, recommendation, and reason visible. When extra context is necessary, hide only that extra context using a collapse feature verified for both surface and sender. Plain `mrkdwn` has no HTML `<details>` toggle. If collapse is unavailable, state that limitation briefly and add `Context: <real-permalink|details in thread>` or a labeled link to an existing source. Do not call a link native collapsing or build new UI infrastructure.

See [examples.md](references/examples.md) for standalone asks, the context fallback, and pending-link updates.

## Read the decision

Keep enough task context to associate the workspace/channel/message timestamp and permalink with the named decider, scope/candidate, emoji map, and unresolved status. No separate ledger service or file is required.

1. Read reactions on the **specific original decision message**, not its summary, context reply, or another message. Check that the fetched message and scope still match the ask.
2. Match the reactor's user ID to the named authorized decider. Ignore bot seed reactions and other people's reactions, regardless of count. Normalize skin-tone variants to the same base emoji, including API forms such as `+1::skin-tone-3`; treat `+1` and `thumbsup` as aliases when that choice was explicitly offered.
3. Interpret only explicitly mapped choices. One unambiguous selection resolves that decision within its stated scope. Multiple conflicting choices by the decider remain unresolved until clarified; do not pick the most popular or infer an order from counts. An unambiguous explicit reply from the decider can clarify the choice.
4. A withdrawn selection is no longer current authorization. Recheck when resuming deferred work before relying on an earlier observation. If the selection disappears before action, leave the decision unresolved. If action already happened, report that fact and clarify remaining work; do not claim the action was undone or invent rollback authority.

Reaction APIs can return incomplete reactor lists. A positive decider-ID match is evidence of that reaction; a count alone is not. If identity or conflicting-choice coverage is incomplete, do not infer approval or withdrawal from missing users: use a complete supported read or request an explicit reply.

Distinguish reading from notification. A successful reaction read verifies the state at that check; it does **not** prove a reaction will wake a sleeping agent. Thread-message watching is not evidence of reaction-event delivery. Unless the current harness has verified reaction wake-up, say reactions are checked when active and request a text reply if an immediate wake-up is needed. Do not promise automatic monitoring.

## Keep the pending footer current

At the bottom of a decision update, include exactly one physical line for unresolved asks that still need that decider:

```text
<@DECIDER_ID> Still waiting: <ORIGINAL_PERMALINK_A|short label>, <ORIGINAL_PERMALINK_B|short label>
```

Use only real permalinks returned by a tool or delivered Slack payload; never construct archives URLs from timestamps. Capture each original ask's permalink after posting, then include it in subsequent updates. If the sender cannot return it, retrieve it through a supported permalink lookup or report the limitation; do not substitute a fabricated link.

Include only decisions that actually need that user, not CI, agent-owned tasks, or resolved asks. Remove resolved links; omit the footer when none remain. Preserve the original ask instead of reposting the question. On later follow-ups, use the single comma-separated waiting line rather than repeating the options or reasons. If a materially changed scope needs a new ask, label the old ask superseded so its reactions cannot authorize the replacement.
