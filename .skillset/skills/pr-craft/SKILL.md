---
name: pr-craft
description: Write or rewrite a pull request's title and description so a reviewer can decide, check, and merge from the text. Use when opening a PR, when editing a PR's title or body, or when working on a PR that the user or an agent they directed authored and whose body does not follow this shape. Not for commit messages, code review, or deciding whether to open or merge a PR.
---

# PR Craft

Write the PR title and description for a reader who has not seen the session. A description has a one-line scope statement and three sections: Context, Changes, and Verify. Four more sections appear only when the change calls for them.

This skill governs the text of a PR. It does not decide whether to open, push, or merge. Follow the task and the repository's instructions for those decisions.

## Precedence

- If the repository has a PR template, fill in that template and map these sections onto its headings.
- If the repository has a title or commit convention, follow it.
- Apply the rules in this skill wherever the repository is silent.

## Title

- Use the Conventional Commits form: `type(scope): summary`. Example: `fix(search): trim the query before splitting it`.
- State what the software does after the change. Do not describe the edit.
- If one issue identifies the PR and the ID helps a reader scanning a list, put that one ID at the end of the title, bare: `fix(search): trim the query before splitting it ENG-140`. Linear links an issue from an ID anywhere in the title; the keyword on the link line still sets the relationship.
- Use the same name for a thing in the title, the description, and the commits.

## Shape

Sections appear in this order. Delete every optional part the change does not need. Most descriptions keep only the scope line, Context, Changes, and Verify.

| Part | When | Holds |
| --- | --- | --- |
| Scope line (no heading) | Always | Kind of change, size, whether behaviour changes |
| Link line (no heading) | The PR has an issue | A keyword and each issue it applies to |
| Callout | Rarely | The one thing the reader must see first |
| Context | Always | What happens today, and when |
| Changes | Always | What happens now, then where |
| Upgrading | Something breaks, or someone running the software must act | What breaks, how to make it work again, why |
| Comparison | The change has a before and an after worth showing | Paired screenshots, recordings, output, or numbers |
| Verify | Always | Steps for the reviewer, then what was run |
| Alternatives | The approach was a real choice | Routes not taken, and why |
| Open items | Something is unfinished after merge | Questions, decisions, follow-ups, what was left out |

```markdown
<scope line: kind of change, size, whether behaviour changes>

<link line: Closes #12, closes [ENG-123](https://linear.app/<workspace>/issue/ENG-123)>

> [!WARNING]
> <only when the reader must see something first; one or two sentences>

## Context
<what happens today, and when; two or three sentences>

## Changes
- <what happens now>, in `<file or function>`
  - <grouped detail, where it helps>

## Upgrading
<what breaks or needs doing, how to make it work again, why>

## Comparison
| Before | After |
| --- | --- |
| <screenshot, recording, output, or number> | <the same, captured the same way> |

## Verify
- <step the reviewer runs or clicks> → <what they should see>
- Ran: <what was run and the result>. Not verified: <anything that wasn't>.

## Alternatives
- <option>: <why not>

## Open items
- Question (reviewer): <something to decide>
- Follow-up (author): <work this leaves for later>
- Not included: <what was deliberately left out>
```

The seven H2 names are fixed. Add H3s inside a section only when it passes about six lines or holds more than one kind of content.

Weak and strong versions of each part, and one whole description, are in [examples.md](references/examples.md). Read it when unsure how a rule applies.

## Core sections

### Scope line

One unheaded line: the kind of change, its size, and whether behaviour changes. Example: `Docs only, 11 lines in one file, no behaviour change.` The reviewer uses it to decide when to look.

### Context

What happens today, and when. Two or three sentences, in the terms of the person affected.

- Fix: what breaks, for whom, and how to see it.
- Feature: what someone cannot do today.
- Refactor: what the current shape makes hard.

Leave out how the problem was found. If a fact is in the linked issue, link the issue and leave the fact out.

### Changes

What happens now, one bullet per change. Put the behaviour first, then the file or function in backticks.

- Name a file only where the reviewer needs it to find the change. The diff holds the inventory.
- If the reason for the approach is not obvious, give it here in one sentence.
- Use one level of sub-bullets where detail belongs to one item.

### Verify

What the reviewer does to confirm the change, and what they should see. Then one line on what was run.

- Each step is one action the reviewer can run or click in under a minute. Start with a verb, put any condition first, and end with the expected result.
- Report only checks that ran and results that were observed.
- State anything not tested on the last line: `Not verified: <what>`.
- "The suite passes" is a result. "The bug is fixed" is a claim; include the step that supports it.

## Optional sections

### Upgrading

Use it when merging breaks something, or when someone running the software must act, such as setting a new variable. Say what breaks, how to make it work again, and why the change is worth it. Write it to the people running the software. Add a `[!WARNING]` callout at the top that points to it.

### Comparison

Use it when the change has a before and an after worth showing. It sits directly after Changes.

- Show both sides, captured the same way: same viewport, same data, same state, same command.
- Lay it out as a two-column table, Before on the left and After on the right, one row per screen or state.
- For a new feature, Before is the same screen without the feature.
- Use text or numbers when the change is text or performance: the old line beside the new one, or output from each branch.
- Use a recording only when the change is about motion or interaction, and keep it to about fifteen seconds.

If the change has a visible before and after and the tools at hand can capture both sides the same way, capture them without being asked. If the tools cannot, use a text or numbers Comparison, or leave the section out. See `## Media` for attaching the files.

### Alternatives

Use it when the approach was a real choice and a reviewer would ask "why not X?" One bullet per option: what it was, then why it was not taken. Three at most. The reason for the chosen route stays in Changes.

### Open items

Use it when something is still unfinished after merge: a question for the reviewer, a decision that is theirs, follow-up work, or something deliberately left out.

- Start each bullet with its kind and who acts on it: `Question (reviewer):`, `Follow-up (author):`, `Not included:`.
- What was not tested goes on the last line of Verify, not here.

## Callouts

A callout shows something the reader must see before anything else. Use three types, each with one meaning.

| Callout | Means | Example |
| --- | --- | --- |
| `[!WARNING]` | Merging this breaks something or cannot be undone | "Breaking: existing deployments must set `X` before upgrading. See Upgrading." |
| `[!IMPORTANT]` | The reviewer must do or decide something before merge | "Merge after #12." |
| `[!NOTE]` | Context that changes how to read the PR | "Part of a stack." |

- Place a callout directly under the scope line and link line, never inside a section.
- Most descriptions have no callout. Two is the limit.
- Keep it to one or two sentences. If a section holds the detail, point to that section.
- Do not use a callout for emphasis on ordinary content.

## Linking issues

Put issue links on one line directly under the scope line. The keyword decides what happens to the issue when the PR merges, in GitHub and in Linear alike.

```text
Closes #351, closes [ENG-123](https://linear.app/acme/issue/ENG-123), part of [OPS-45](https://linear.app/acme/issue/OPS-45)
```

| Keyword | Use when | GitHub issue | Linear issue |
| --- | --- | --- | --- |
| `Closes` | This PR finishes the issue | Closed on merge | Moves to the team's merge status |
| `Part of` | This PR is one of several for the issue | Stays open | Follows the PR, but does not complete on merge |
| `Related to` | The issue is background | Stays open | Linked, no status change |

- Repeat the keyword for every issue.
- Write a GitHub issue bare: `#12` in the same repository, `owner/repo#12` in another.
- Write a Linear issue as a Markdown link with the ID as its text: `[ENG-123](https://linear.app/<workspace>/issue/ENG-123)`.
- Use the real issue IDs and the real workspace slug, including those of a private workspace. The examples here use generic ones; a link works only with the real ones.
- Issues from different teams go on the same line, each with its own keyword.
- Put keywords in the description, not in commit messages.
- If several PRs serve one issue, use `Part of` on every PR except the one whose merge finishes the issue.
- If the PR will merge into a branch other than the default branch, use `Part of`. GitHub ignores closing keywords on such a PR, and Linear completes a `Closes` issue on merge into any branch. A stacked PR that merges into the default branch keeps `Closes`.
- If the branch name carries an issue ID that the PR must not link, write `Ignore ENG-123` in the description.
- Linear posts the issue's title and description in a comment on the PR. If the repository is public, or people who cannot read the Linear issue can read the repository, and the issue's title or description is not meant for them, ask the user before adding the link.

### Creating the Linear issue from the PR

If the PR has no issue and the repository's PRs link Linear issues, write `<TEAM>-NEW` after the keyword: `Closes ENG-NEW`. Linear creates an issue in that team, links it, starts it, and assigns it to the PR author.

- Write it bare, in the description. There is no URL to link.
- Use a team key that the user, the repository's instructions, or the repository's other PRs establish. If none establishes a team key, leave the link line out.
- Do not combine it with a reference to an existing Linear issue. Linear creates nothing when the PR already links one.
- Leave the placeholder in place after the issue exists.

## Stacks

If the PR is part of a stack, add one `[!NOTE]` callout: "Part of a stack." Do not state the PR's position, the stack's size, or its sibling PRs; that text goes stale as the stack changes. The stack note points to no section. Leave any block a stacking tool manages as that tool wrote it. Each PR in the stack gets its own description in this shape.

## Media

Attach images and video with `gh`, version 2.99.0 or later. Write the body with local paths, then pass the same files to `--attach`. `gh` uploads each file and rewrites the matching reference in place.

```bash
gh pr create --title "<title>" --body-file body.md \
  --attach './before.png#Search for "tea " showing no results' \
  --attach './after.png#Search for "tea " showing 12 results'
```

- `--attach` works on `gh pr create`, `gh pr edit`, and `gh pr comment`.
- Give each image alt text after `#`.
- Accepted formats: PNG, JPEG, GIF, WebP, SVG, MP4, MOV, WebM. Images are limited to 10 MB.
- Attaching needs push access to the repository and is not available on GitHub Enterprise Server or on `gh` older than 2.99.0. If any of these blocks the upload, use a text or numbers Comparison, or name the files for the user to attach by hand.
- If `gh pr create` exits non-zero after printing a PR URL, the PR exists and some files did not upload. Do not create the PR again. Attach the missing files with `gh pr edit --attach`.

## Repositories the user does not own

- Follow the project's PR template, title convention, and contribution guide before anything here.
- Add an opener of one or two sentences above the scope line: who the contributor is and why they made the change. Draft it from what the user has said. Do not invent a motive.
- Reference only that project's own issues. Do not add a link to the user's tracker, do not put a tracker ID in the title, and do not use `<TEAM>-NEW`.
- If the change is breaking or has several workable designs, tell the user that an issue or discussion on the project comes before the PR.
- Expect `--attach` to fail without push access. Use the fallback in `## Media`.

## Existing PRs

If all of the following hold, rewrite the PR body into this shape:

1. The task names that PR, or the agent is committing to its branch.
2. The PR's author is the user, or an agent the user directed.
3. The body follows neither this shape nor the repository's PR template.
4. The agent's access allows editing the PR.

- Keep every fact a reviewer needs, and move each to the section that owns it. Drop only what `### Leave out` lists.
- Carry over the body's existing verification claims as written. Do not re-run them.
- Leave any block a tool manages as that tool wrote it, such as a stack list or a session link.
- Do not search for other PRs to rewrite.
- Do not rewrite a PR that someone else authored.

## Writing

Agents write most descriptions, and both people and agents read them. Keep the text short enough for a person to skim and literal enough for an agent to act on.

### Order

- Put the bottom line first. The scope line, link line, and callout tell a reader who stops there what the PR is, how big it is, and what it needs from them.
- Make the first sentence of each section that section's point.
- Do not label the bottom line with "Summary:" or "TL;DR".
- Do not end with a closing summary.

### Sentences

- Describe the software, not the author. The subject is the product, the user, or the file. It is not "I", "we", or "this PR".
- Use the present tense. Context says what happens today. Changes says what happens with the PR merged: "The guide says", not "Updated the guide to say".
- Give the number, not the adjective: "nine times", "11 lines", "40 ms".
- Use the exact name. Identifiers, commands, and paths go in backticks, as written in the code. Interface labels go in quotes, as they appear on screen.
- Repeat the noun when "it" or "this" could point at two things.
- Refer to a section by name: "See Upgrading", not "see below".
- State a doubt once, where it applies. Do not hedge a checked fact. Do not state an unchecked one as fact.
- Write for a reader outside the session. No "as discussed", "per your request", or "the earlier approach".

### Length

A description is as long as its reader needs. Say each thing once, in the fewest words that keep it exact, and keep anything a reviewer would otherwise have to ask for.

- A fix or docs change takes about a screen. A feature takes more.
- Shorten by cutting repetition and the items under `### Leave out`. Do not cut a fact to make the description shorter.
- Judge length by reading the draft once as the reviewer. Do not count words, and do not revise in a loop to reach a size.
- Leave out a section with nothing to say. Do not write a heading followed by "None" or "N/A".
- If a note concerns one line of the diff, put it in a review comment on that line.

### Leave out

- How the work was done: the order of attempts, the dead ends, the tools used.
- A file-by-file or function-by-function inventory.
- Text repeated from the title or the commit messages.
- Test totals, pass counts, and terminal output. Name the command and its result.
- Praise for the change: comprehensive, robust, seamless, clean, proper, significant.
- Openers and closers: "This PR", "In summary", "Overall", "Let me know", "Happy to adjust".
- Requests that are not decisions, such as "please review carefully".
- Emoji, decorative bold labels, horizontal rules, and checklists with every box ticked.

## By type of change

The headings stay the same for every kind of PR. What goes under them shifts.

| Type | Context | Changes | Verify | Usually adds |
| --- | --- | --- | --- | --- |
| Fix | What breaks, for whom, how to see it | The fix, and the test that fails without it | The repro steps, now passing | Comparison, when the bug is visible |
| Docs | What the docs say against what is true | The lines corrected | A search command, or a page to look at | Comparison, as text |
| Feature | What someone cannot do today | The new behaviour, then the files | A click path with the expected result | Comparison; Alternatives if the design was a choice |
| Refactor | What the current shape makes hard | What moved where, stated as move-only | The suite passes with no behaviour change | Open items, for the moves still to come |
| Performance | What is slow, with a number | The change | The benchmark command | Comparison, as numbers |
| Breaking | What the current behaviour costs | The new behaviour | Steps on an existing install | Upgrading, and a `[!WARNING]` callout |

## Before requesting review

Read the draft once as the reviewer, without the diff. It must answer three questions: what happens today, what changes, and how to check. In that one read, confirm:

- No heading is empty and no section restates another.
- Every Verify step has an expected result, and the "Ran" line lists only what ran.
- Every identifier and interface label is written as it appeared in the code or on screen during the work.

This is one read-through of the draft. Do not open the app or re-read the diff for it, do not repeat it, and do not re-check a posted PR's links or rendering unless the user asks.

## Requirements

Writing a description needs no external tools. Opening or editing a PR and attaching media use the GitHub CLI, `gh`; `--attach` needs version 2.99.0 or later. Linear linking needs the Linear GitHub integration on the repository.
