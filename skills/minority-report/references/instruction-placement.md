# Instruction Placement

Choose the surface that owns an instruction and verify when the consuming agent loads it. Placement determines which tasks receive the guidance.

## Surface table

| Surface | Owns | Refuses |
|---|---|---|
| **User/global instructions** | Personal boundaries, cross-project workflow defaults, routing to personal tools | Repository architecture, project commands, temporary model workarounds |
| **Root instruction file** (`CLAUDE.md`, `AGENTS.md`) | Non-obvious invariants, repo-wide action boundaries, unusual commands with dangerous alternatives, generated-source relationships, concise routing to scoped rules and skills | Repo tours, tutorials, generic advice, linter settings restated, task checklists, volatile facts, model rituals, output-style preferences |
| **Scoped rules** (subtree files, `.claude/rules/**`) | Rules true throughout one package, service, or path pattern | Anything repo-wide (promote to root) or task-class-specific (move to a skill) |
| **Skills** | Repeatable task-class procedures: releases, migrations, reviews, debugging playbooks | Repo-wide invariants unrelated to the skill’s task; task-specific invariants may remain with the procedure that needs them |
| **Tool descriptions** | What the tool does, when it is the correct tool, key input semantics, consequential side effects | Tutorials, duplicated procedure, generic warning walls |
| **Hooks / tests / linters / CI / permissions** | Anything guaranteeable mechanically: formatting, generated drift, forbidden dependency edges, path restrictions | Nothing — but prose may still state the invariant and safe path the agent needs upstream of the mechanical check |
| **Docs** | Architecture explanation, ADRs, rationale, subsystem maps | Nothing — route from persistent context only when the route itself is load-bearing |
| **Task prompt** | Today's scope, one-off constraints, task-specific risk tolerance and exceptions | Anything that recurs (promote it) |
| **Output style** | Human-facing presentation: update cadence, format, tone | Implementation policy |

## Model-specific accommodations

There is no dedicated model-profile surface, and this guide does not invent one. When an accommodation for a named model survives Instruction Selection's challenge, keep it in an explicitly scoped block ("Claude Code only", "Codex only") with a review date, or emit it per-provider at compile time when the toolchain supports provider targets (Skillset does). The default disposition remains removal — most model workarounds outlive the behavior they patched.

## Skill descriptions are compiled policy

When a harness exposes skill descriptions before activation, those descriptions are persistent routing context even while the bodies remain on demand. Weigh descriptions like root content, and write them to the routing rules in [Agentish](agentish.md) (`## Skill and tool descriptions`).

## Verify how the consuming harness loads instructions

Before recommending a placement change, verify how the consuming harness loads the affected files. Check whether files accumulate or override one another, when imports expand, and when scoped rules or skill bodies load.

Moving a paragraph to a different file reduces persistent context only if the harness defers loading that file. Do not assume that an import provides progressive disclosure or that the nearest file replaces all ancestor instructions.

Treat provider defaults and size limits as version-dependent facts. Check current provider documentation or observed runtime behavior when a finding depends on them. Do not use an unverified limit as a writing target.
