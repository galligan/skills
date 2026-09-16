---
name: discover-unknowns
description: Discover hidden assumptions, blind spots, and unresolved decisions before they derail work. Use for repository fieldwork, prompt preparation, prototype planning, implementation deviation logs, handoffs, or understanding checks when the main need is finding what the user, plan, codebase, or agent may be missing.
---

# Discover Unknowns

Use this skill when the task is less about executing a known change and more
about discovering what the user, prompt, repo, product, or agent may be missing.

The core idea: the prompt is the map, the work surface is the territory, and the
gap between them is where agent runs go wrong. Your job is to reduce that gap
with the smallest useful discovery artifact.

## When to use this skill

Use it when the user asks for:

- unknowns, blindspots, assumptions, ambiguities, or "what am I missing?"
- a broad repo/codebase pass before implementation
- help writing a better prompt for another agent or model
- design, product, architecture, or domain exploration where taste or criteria
  are not fully verbalized
- an implementation plan focused on decisions the user may want to change
- a post-run explainer, quiz, or merge-readiness understanding pass

Do not turn every small task into a discovery ceremony. If the work is obvious,
low-risk, and reversible, act normally.

## Unknown types

Classify useful findings with this vocabulary:

- `known`: what the user already said or the repo states plainly.
- `question`: a known unknown; the user or repo exposes an unresolved decision.
- `blindspot`: an unknown unknown; something the user may not know to ask about.
- `taste`: an unknown known; an expectation the user may recognize only when
  shown an example or violated.
- `reference`: a concrete source that can carry intent better than prose:
  source code, docs, designs, tests, examples, screenshots, logs, issues, or
  prior artifacts.

Prefer these singular labels in headings and reports. They are compact and easy
to scan.

## Modes

Pick the smallest mode that fits. Do not announce a mode unless it helps the
user.

### blindspots

Use before work in unfamiliar territory.

Goal: find what the user may not know to ask about.

Read enough repo, docs, issue, runtime, or domain context to identify the
highest-leverage gaps. Explain why each gap matters and what prompt, reference,
prototype, or question would reduce it.

Run blindspots as a depth loop, not a shallow inventory:

1. Start with the user's goal and the repo's stated contract.
2. Find the first layer of likely blindspots.
3. Pick the one to three findings most likely to change future prompts,
   architecture, risk, or verification.
4. Follow each selected finding one level deeper through code, docs, tests,
   issues, logs, or examples.
5. Repeat while the deeper pass is still producing materially new information.
6. Stop when the next pass would mostly add detail without changing the user's
   next decision, or when the run reaches the user's stated time/turn bound.

Use subagents when independent branches can be explored without interrupting the
main thread: separate packages, separate products, separate risk surfaces,
separate historical threads, or separate reference implementations. Give each
subagent a narrow question, the user's goal, the relevant scope fence, and the
same evidence requirement. Synthesize their results into the main report; do not
dump parallel notes raw.

When writing a prompt for a blindspots run, include a goal-shaped completion
condition even if you are not creating a goal packet. The condition should state
what the agent must surface, what evidence proves it looked deeply enough, what
is out of scope, and when to stop.

### brainstorm

Use when the scope, product shape, architecture, or strategy is too narrow or
too vague.

Goal: produce several meaningfully different directions so the user can react.

Keep directions concrete. Include tradeoffs, likely cost, and what evidence
would support choosing each one. For UI, design, data, or workflow work, prefer
an artifact the user can inspect over prose alone.

### prototype

Use when the user will know the answer by seeing or trying something.

Goal: make a cheap artifact that reveals taste, layout, interaction, feasibility,
or workflow fit before real implementation.

Keep prototypes separate from production code unless the user asked for a real
implementation. Use fake data when wiring the real substrate would distract from
the decision.

### interview

Use when user answers would materially change architecture, scope, or prompt
shape.

Goal: ask the fewest questions that change the outcome.

Ask one question at a time. Prioritize decisions that affect data models,
ownership, user experience, safety, rollout, or reversibility. Stop when the
prompt is good enough to proceed.

### reference

Use when the user cannot easily describe what they want, or when prose would be
lossy.

Goal: identify and hand the next agent concrete references.

Good references include source modules with desired semantics, similar features,
component libraries, tests that encode contracts, issue threads, docs, traces,
screenshots, or external examples. Tell the next agent what to copy, preserve,
or avoid from each reference.

### plan

Use when implementation is likely, but the user should review high-leverage
decisions first.

Goal: propose the plan around decisions that may change, not mechanical steps.

Lead with data model, type interface, API contract, UX flow, migration, rollout,
or safety choices. Put mechanical refactors and obvious code movement last.

### deviation

Use during implementation when the territory disagrees with the map.

Goal: preserve learning without stopping unnecessarily.

If a discovered edge case forces a plan change, pick the conservative option,
keep going when safe, and log the deviation. Capture what changed, why, evidence,
and whether the user should revisit it later.

### explainer

Use after work when reviewers or future agents need to understand the change.

Goal: package the artifacts, decisions, unknowns, and evidence into a readable
handoff.

Lead with outcome, then show what changed, why it matters, how it was verified,
what remains uncertain, and what follow-up prompt should happen next.

### quiz

Use after a large agent run when the user needs enough understanding to approve,
merge, or steer.

Goal: help the user rebuild the important mental model.

Provide a compact report first. Then ask a quiz focused on behavior, contracts,
risks, and what would break if assumptions change. Include the answer key only
after the user has had a chance to respond, unless they ask for a self-contained
artifact.

## Repo fieldwork output

For broad codebase passes, produce this shape:

```markdown
# Discover Unknowns: <repo or surface>

## Outcome
One paragraph on what kind of unknowns matter most here.

## Findings

### blindspot: <short label>
- What it is:
- Why it matters:
- Evidence:
- Reducing prompt:
- Worth using a stronger model: yes/no, with why

### question: <short label>
- What it is:
- Why it matters:
- Evidence:
- Reducing prompt:
- Worth using a stronger model: yes/no, with why

## Reference
- <path or source>: what future prompts should use it for.

## Next
- Top follow-up prompts.
- Things not worth spending scarce model time on.
- If there is time for one more run, do this.
```

Keep evidence specific. Prefer file paths, command outputs, issue IDs, failing
checks, docs, examples, or visible UI behavior. Do not invent certainty.

## Prompt-writing output

When writing a prompt for another agent, return a complete prompt, not a
checklist for the user to fill in. If facts are missing, either make the smallest
reasonable assumption and mark it as an assumption, or ask only the question that
materially changes the prompt.

This skill writes prompts. It does not build goal packets, planning packets, task
folders, or multi-file harnesses unless the user explicitly asks for those
artifacts. The premise of a goal loop is still useful: express the objective,
success evidence, scope constraints, and stopping condition inside the prompt.

Include:

- goal
- context and starting point
- in-bounds and out-of-bounds scope
- references to inspect
- unknown types to surface
- deliverable format
- evidence requirements
- stop condition or completion condition when the run is unattended

For blindspots prompts, also include:

- the depth loop to follow when a high-signal unknown appears
- when to spawn subagents for independent investigation branches
- how to synthesize subagent findings without flooding the report
- the rule that assessment stops short of implementation unless explicitly
  authorized

## Guardrails

- Do not modify production code during an assess-only unknowns pass.
- Do not run destructive commands as part of discovery.
- Do not create broad trackers or docs unless the user asks for durable output.
- Do not ask for internal reasoning in prompts. Ask for evidence, rationale, and
  tradeoffs instead.
- Do not overload reports with minor observations. Prioritize unknowns that
  change architecture, prompt quality, product direction, verification, or risk.
- When time or model access is scarce, recommend the smallest next run with the
  highest chance of changing the user's understanding.
