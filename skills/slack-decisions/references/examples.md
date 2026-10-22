# Slack decision examples

These are templates, not messages to send verbatim. Replace `DECIDER_ID` with a resolved user ID and uppercase URL tokens with real tool-returned permalinks or verified source URLs. No sample Slack archives URL is invented here. Code fences show the exact `mrkdwn` text; omit the fences when sending.

## Numbered alternatives

One original message, one decision, one physical ask line:

```text
<@DECIDER_ID> Search UI for the settings page: :one: inline field, :two: modal, :three: defer; *recommend :one:* — keeps filtering beside the results.
```

Only reactions on this original message select its alternatives. A summary can link to it but does not collect votes for it.

## Go, hold, or stop

Send as a separate original decision message:

```text
<@DECIDER_ID> Run the read-only staging comparison for build BUILD_ID: :large_green_circle: go with comparison, :large_yellow_circle: pause for clarification, :red_circle: stop comparison; *recommend :large_green_circle:* — it changes no data. Context: <CONTEXT_REPLY_PERMALINK|comparison details in thread> (linked context; this sender cannot collapse it).
```

Post necessary extra detail in a thread reply and obtain its real permalink before referencing it, or use an existing source. Keep detail off the ask line without pretending the link is a toggle.

## Specified release versus continuing work

Separate original messages prevent shared reaction meanings:

```text
<@DECIDER_ID> Release VERSION, artifact DIGEST, to TARGET_ENV: :rocket: approve that release, :large_yellow_circle: hold that release, :red_circle: stop that release; *recommend :large_yellow_circle:* — the release check is still failing. Context: <RELEASE_CHECK_URL|release check>.
```

```text
<@DECIDER_ID> Continue the documentation edits in PR_URL: :white_check_mark: looks good, continue those edits, :large_yellow_circle: pause those edits, :red_circle: stop those edits; *recommend :white_check_mark:* — the examples match the agreed behavior.
```

The checkmark on the documentation message does not approve the release. The rocket covers only the named release candidate and target; existing gates still apply.

## Summary and later reminder

After the separate original asks exist, a summary can keep each decision on its own line and finish with one pending line. React on the linked original asks, not this summary:

```text
<@DECIDER_ID> <SEARCH_ASK_PERMALINK|Search UI choice>: *recommend inline field* — keeps filtering beside results; choose on the original ask.
<@DECIDER_ID> <RELEASE_ASK_PERMALINK|Release choice>: *recommend hold* — the release check is still failing; choose on the original ask.
<@DECIDER_ID> Still waiting: <SEARCH_ASK_PERMALINK|search UI>, <RELEASE_ASK_PERMALINK|specified release>
```

After the search choice resolves, a later reminder is only:

```text
<@DECIDER_ID> Still waiting: <RELEASE_ASK_PERMALINK|specified release>
```

## Interpretation fixtures

| Observation | Result |
| --- | --- |
| Decider reacts `one` to the original search ask | Select inline field only. |
| Bot seeds `one`, or another person chooses it | No decision by the named decider. |
| A prior ask explicitly offered thumbs-up for Option A; decider uses `+1::skin-tone-3` | Same choice as `thumbsup`; not a new global thumbs-up meaning. |
| Decider selects both `one` and `two` | Unresolved; request clarification. |
| Selection is withdrawn before action, confirmed by a complete read | Unresolved; no current authorization. |
| Count is positive but decider identity is unavailable | No verified decision; obtain an explicit reply. |
| `white_check_mark` appears on the documentation ask | Continue those edits only; no release authorization. |
| Candidate digest changes after a rocket reaction | Old reaction does not cover the replacement. |
| Two decision lines reuse the same green emoji in one message | Ambiguous; do not infer per-line votes. |
| Reaction read succeeds while agent is active | Verified read only; sleeping-session wake-up remains unverified. |
