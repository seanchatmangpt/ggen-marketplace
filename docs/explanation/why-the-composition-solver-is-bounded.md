# Why the composition solver is bounded and fenced

This page explains the choices in `composition-solver-pack` and where its claims stop. Exact contracts are in [Composition solver contract](../reference/composition-solver-contract.md).

## What question it answers

Given requirements and a basis of capability atoms, which required propositions are derivable by composing atoms, and which remain? The remainder is the residual that [industry closure](industry-closure-as-architecture-strategy.md) turns into work. The solver feeds that loop; it does not replace it. A requirement the solver covers is a candidate plan at one exact subject, not a capability.

## Why the stage bound exists

ggen runs each inference rule once, in order, and later rules see earlier results. Repeating one CONSTRUCT a fixed number of times gives bounded derivation depth and nothing else, because a single query cannot compute "all requirements derivable" recursively. A bound alone would be unsafe, since a requirement deeper than the bound would look uncovered and a false residual would become false work. Gate 020 closes that hole: if a further stage would still change the graph, the sync is refused. A false residual becomes a typed refusal. The cost is a static depth, tracked as SJ-CSP-001.

## Why DO atoms are reported, not selected

Existence of a plan must not grant authority. A DO atom is never enabled, so the requirement stays in the residual as `BLOCKED_AUTHORITY` and the consequence stays with the separately admitted DO path. The fence is only as good as the label, and the label is self-declared today (SJ-CSP-002).

## What it does not do

It reaches, it does not choose: alternatives are all returned, with no ranking or constraint search (SJ-CSP-003). Its atoms are the basis author's reading of other packs, not those packs' own declarations (SJ-CSP-004). The Vision 2030 capabilities cannot yet be composed because they carry no dependency edges, and asserting some here would invent semantics (SJ-CSP-005).

## Why failures are written down

A pattern that does not work yet is knowledge. Each limit is a ticket with evidence, a deficit class, acceptance and a falsifier, so a future requirement lands on a known gap instead of rediscovering it. A test pins each limit, so a fix shows up as a failing test that forces the ticket to be updated.
