# PR Craft examples

Weak and strong versions of each part of a PR, written to the PR Craft convention. Each pair shows one decision the rules leave open to misreading. The running example is invented: a fix for a search that fails when the query ends in a space.

## Part by part

### Title

Weak:

```text
Fix search bug
```

Strong:

```text
fix(search): trim the query before splitting it
```

The strong title names the area and says what the software does now. With one issue that identifies the PR, the ID goes at the end: `fix(search): trim the query before splitting it ENG-140`.

### Opening paragraph

Weak:

```text
This PR introduces a comprehensive fix for an important search issue and significantly improves the overall user experience.
```

Also weak:

```text
Fix, 14 lines in two files; search results change for queries that end in a space.
```

Strong:

```text
Fixes search for queries that end in a space, which returned no results. Results for every other query are unchanged.
```

The strong paragraph says what the change does and what it leaves alone. Nothing in the first weak version can be checked. The second leads with a label and with counts that GitHub already shows and that go stale on the next push.

A change that reduces a problem without fully fixing it says so:

```text
Addresses slow search on large catalogs by caching parsed queries. Queries over 200 terms are still slow.
```

### Link line

Weak:

```text
Related to the search ticket. Linear: https://linear.app/acme/issue/ENG-140
```

Strong:

```text
Closes #208, closes [ENG-140](https://linear.app/acme/issue/ENG-140), part of [OPS-45](https://linear.app/acme/issue/OPS-45)
```

The keyword decides what happens on merge. "Related to" would leave every issue open, and "Linear:" is not a keyword. The strong line closes the two issues this PR finishes and marks the PR as one of several for an issue in another team.

With no issue yet, the PR creates one:

```text
Closes ENG-NEW
```

### Callout

Weak:

```markdown
> [!IMPORTANT]
> This PR fixes a long-standing search bug!
```

Strong:

```markdown
> [!IMPORTANT]
> Merge after #212, which adds the `terms` column this reads.
```

A callout tells the reviewer something they must act on. The weak one only adds emphasis, so it should not exist.

For a PR in a stack, the callout says only that:

```markdown
> [!NOTE]
> Part of a stack.
```

### Context

Weak:

```text
While working on the search page I noticed that some queries weren't returning results. After investigating, I traced the problem to the query parser, which was not handling whitespace properly. This has likely been an issue for a while and could be frustrating for users.
```

Strong:

```text
A search that ends in a space returns no results. `parseQuery` reads the trailing space as an empty second term, and an empty term matches nothing. Phone keyboards add that space after autocomplete, so most mobile searches fail.
```

The strong version opens with what happens, names where, and says who is affected. The weak version tells how the bug was found and guesses at its effect.

### Changes

Weak:

```markdown
- Updated `parse-query.ts` to handle whitespace properly
- Modified `search.test.ts`
- Refactored the tokenizer for cleaner, more maintainable code
- Various small improvements
```

Strong:

```markdown
- A query is trimmed before it is split into terms, in `parseQuery`.
- Empty terms are dropped, so a double space inside a query no longer adds one.
```

The strong bullets say what the software does now. The weak ones list files, praise the code, and name nothing. The tokenizer refactor is a second change and belongs in its own PR.

### Comparison

Weak: one screenshot of the results page after the fix.

Strong:

```markdown
| Before | After |
| --- | --- |
| `tea ` returns 0 results | `tea ` returns 12 results |
```

A comparison has two sides captured the same way. One side alone is an illustration.

With screenshots, the body uses local paths and `gh` rewrites them on upload:

```markdown
| Before | After |
| --- | --- |
| ![Search for "tea " showing no results](./before.png) | ![Search for "tea " showing 12 results](./after.png) |
```

### Verify

Weak:

```text
✅ All tests passing (4,290 tests)
✅ Manually tested and works as expected
✅ No regressions
```

Strong:

```markdown
- Search for `tea ` with a trailing space → the same results as `tea`.
- Run `pnpm test parse-query` → 2 new tests pass. Both fail on `main`.
- Ran: `pnpm typecheck` and `pnpm test`, both pass. Not verified: Safari on iOS.
```

The reviewer can repeat each strong step and knows what to expect. "No regressions" is a claim with nothing under it, and the weak version hides what was not checked.

### Alternatives

Weak:

```text
We considered several approaches but ultimately decided this was the best solution.
```

Strong:

```markdown
- Trim in the search box instead: other callers of `parseQuery`, such as the API, would still fail.
```

An alternative is named, with the reason it lost. If none can be named, the section is left out.

### Open items

Weak:

```text
Future work could include improving the search experience further. Let me know if you'd like me to make any other changes!
```

Strong:

```markdown
- Question (reviewer): should a query of only spaces show the empty state or recent searches?
- Follow-up (author): the API docs still say trailing spaces are significant. Separate PR.
```

Each strong item is one thing still open, with who acts on it. The weak version offers nothing to decide.

## Phrases to cut

| Phrase | Problem | Write instead |
| --- | --- | --- |
| "This PR adds", "This PR fixes" | The subject is the PR, not the software | Start with the software: "Search trims the query" |
| "Updated X to", "Refactored Y" | Describes the edit, not the behavior | "X now does" |
| comprehensive, robust, seamless, clean | Cannot be checked | The number, or nothing |
| minor, small, quick | The reviewer decides that | What the change affects |
| various, several, some files | Names nothing | The count, or the names |
| "should now work", "hopefully fixes" | Hedges something that can be checked | What was run and what it showed, or "Not verified" |
| "works as expected" | States no expectation | The step and its result |
| "All tests pass" with a tick | No command and no scope | "`pnpm test` passes" |
| "as discussed", "per feedback" | The reader was not there | The decision itself, with a link to the thread |
| "see below", "the above" | Breaks when text moves or is quoted | The section's name |
| "In summary", "Overall" | Repeats what was said | Nothing |
| "Let me know", "Happy to adjust" | Asks for no decision | Nothing, or a Question under Open items |
| "None" or "N/A" under a heading | The section is empty | Delete the heading |

## A whole description

Title:

```text
fix(search): trim the query before splitting it
```

Body:

```markdown
Fixes search for queries that end in a space, which returned no results. Results for every other query are unchanged.

Closes #208, closes [ENG-140](https://linear.app/acme/issue/ENG-140)

## Context
A search that ends in a space returns no results. `parseQuery` reads the trailing space as an empty second term, and an empty term matches nothing. Phone keyboards add that space after autocomplete, so most mobile searches fail.

## Changes
- A query is trimmed before it is split into terms, in `parseQuery`.
- Empty terms are dropped, so a double space inside a query no longer adds one.

## Comparison
| Before | After |
| --- | --- |
| `tea ` returns 0 results | `tea ` returns 12 results |

## Verify
- Search for `tea ` with a trailing space → the same results as `tea`.
- Run `pnpm test parse-query` → 2 new tests pass. Both fail on `main`.
- Ran: `pnpm typecheck` and `pnpm test`, both pass. Not verified: Safari on iOS.

## Alternatives
- Trim in the search box instead: other callers of `parseQuery`, such as the API, would still fail.

## Open items
- Question (reviewer): should a query of only spaces show the empty state or recent searches?
- Follow-up (author): the API docs still say trailing spaces are significant. Separate PR.
```

This description uses three optional sections because the fix has a visible before and after, a real alternative, and two things still open. A docs fix usually keeps only the opening paragraph, Context, Changes, and Verify.

## A contribution to someone else's project

The same fix, sent to a project the contributor does not maintain. The introduction comes first, the link line references only that project's issue, and the Comparison is text because attaching media needs push access.

```markdown
I run this for a small tea shop's catalog, and customers on phones kept reporting empty searches.

Fixes search for queries that end in a space, which returned no results. Results for every other query are unchanged.

Closes #208

## Context
A search that ends in a space returns no results. `parseQuery` reads the trailing space as an empty second term, and an empty term matches nothing.

## Changes
- A query is trimmed before it is split into terms, in `parseQuery`.
- Empty terms are dropped, so a double space inside a query no longer adds one.

## Comparison
| Before | After |
| --- | --- |
| `tea ` returns 0 results | `tea ` returns 12 results |

## Verify
- Search for `tea ` with a trailing space → the same results as `tea`.
- Ran: `pnpm test`, passes. Not verified: Safari on iOS.
```
