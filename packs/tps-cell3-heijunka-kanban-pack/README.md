# TPS Cell3 Heijunka/Kanban Pack

Purpose: manufacture current-cycle legal ready-set allocation without rediscovering the portfolio.

## Input objects
A cycle, current-cycle Kanban cards, exact consumer/base/head identities, authority, dependencies, upstream GGEN primitive, qualification command, merge constraints, remaining takt, OCEL evidence contract, witnesses and falsifiers.

## Output law
Cards are typed `READY_NOW`, `READY_AFTER_BOUNDED_REPAIR`, `CLOSE_EARLY`, or `REFUSE_NOW`. Stale base, conflicts, failed prerequisites, missing generators, authority drift and unbounded repairs are Andons. Freed WIP slots pull independent admitted replacements immediately when inventory exists.

## Heijunka
Load is leveled across independent repositories and consumer families while preserving quality, same-hour terminal closure, zero spillover and GGEN-first reuse. Saturation shifts production to independent paths instead of idling.

## Jidoka
No sunk-cost WIP. A bounded repair may remain only when it fits remaining takt. Otherwise the card terminates `REFUSED_TYPED[TAKT_NOT_CLOSABLE]` and replacement search runs.

## Cell4 card completeness
Every selected card must carry exact repo/base/head, upstream primitive, manufacture/integration command, OCEL evidence contract, positive witness, negative falsifier, qualification command, merge constraints and expected terminal state.

## Authority
SELECT != CONSTRUCT != DO. This pack grants no consequential external DO. Process analysis remains owned by `wasm4pm/wasm4pm-compat`.
