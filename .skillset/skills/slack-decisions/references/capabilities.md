# Slack capability boundaries

Official Slack documentation and the native Devin Slack tool schema/help were checked on October 22, 2026. Recheck the current docs and sender before relying on a feature; this snapshot is not a promise about another harness or connection.

## Formatting and context

- [Formatting message text](https://docs.slack.dev/messaging/formatting-message-text): `mrkdwn` uses `*bold*`, `<@USERID>` mentions, and `<url|label>` links. Do not assume HTML `<details>` or standard Markdown links work in plain Slack messages.
- [Container block](https://docs.slack.dev/reference/block-kit/blocks/container-block): Slack documents `is_collapsible: true` and `default_collapsed: true` for a container on supported surfaces. Use it for optional context only when the existing sender accepts that block. Keep the decision itself outside the collapsed context; no interactive actions are needed.
- [Section block](https://docs.slack.dev/reference/block-kit/blocks/section-block): `expand: false` or omitted means text **may** render with “see more.” It does not guarantee a hideable context section or initial collapse.

The inspected native Devin `slack` sender accepts only presentational `header`, `section` (no accessory), `context`, `divider`, and `markdown` blocks. It does not accept `container` blocks or interactive blocks. Its plain `text` uses `mrkdwn`. For this sender, use a labeled thread-reply or source link instead of claiming collapsible context. Slack platform support does not override the sender's allowlist. Another sender may support containers; verify its schema rather than copying this limitation to all Slack tools.

## Connection requirements and operation equivalents

Use the existing authorized connection and its documented argument names. These are operation equivalents, not a required tool package:

| Need | Native Devin Slack operation | Equivalent Slack API capability |
| --- | --- | --- |
| Send an ask or context reply | `post_message`, with thread timestamp for a reply | `chat.postMessage`; existing write permission for that conversation |
| Read the original ask and replies | `thread_replies` or relevant message read | `conversations.replies` / conversation history with existing read access |
| Resolve a user identity | `lookup_slack_resource` for user | Existing user lookup returning stable Slack user IDs |
| Obtain a real permalink | Returned `permalink` / delivered payload `url` | [`chat.getPermalink`](https://docs.slack.dev/reference/methods/chat.getPermalink), with channel and message timestamp |
| Check reactions on one ask | `reaction`, `reaction_action: get`, channel and message timestamp | [`reactions.get`](https://docs.slack.dev/reference/methods/reactions.get), with channel and timestamp; requires existing `reactions:read` |

`reactions.get` documents that `users` may omit reactors even when `count` includes them. Its `full` option requests a complete reaction list, but a count without the decider's ID is not identity evidence. Do not assume every adapter exposes `full` or all users. Verify completeness before concluding that a reaction was withdrawn or that no conflicting choice exists.

The inspected native tool supports reading reactions and their reactor IDs on one message. A reported active-session check selected an explicitly mapped Option A from the authorized decider's skin-toned thumbs-up. That observation verifies reading, not automatic notification or sleeping-session wake-up. Its `watch_thread` contract describes delivery of subsequent human **messages**, not reaction events. Neither contract establishes reaction wake-up. Use a text reply for immediate attention when wake-up is unverified; do not create monitoring infrastructure for this skill.
