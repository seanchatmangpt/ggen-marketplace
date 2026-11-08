# xstate-v5-machine-pack

Standing: PARTIAL_ALIVE

Pack-scoped vocabulary (`xs5:`) for XState v5 machine semantics, aligned via
`rdfs:seeAlso` to `state-transition-pack`'s `st:` FSM schema (Machine /
State / Transition / Guard) per the M15 cross-pack convention.

## What it generates

- Typed machine definitions (`xs5:Machine`): named actor schema, initial
  state, owned state nodes.
- Smoke-test scaffolds (`xs5:SmokeTest`): drive the machine through its
  happy path and assert final-state shape.
- Compile-shape assertions (`xs5:CompileShape`): per-language parse/
  typecheck checks over generated output.
- Conformance cases (`xs5:ConformanceCase`): named event-sequence cases
  exercising real transitions through declared guards.
- TTL baseline fixture (`xs5:TtlBaseline`): frozen RDF baseline diffed on
  every regeneration to detect serializer drift.

## Gate list

Gates are consumer-authored against the pack vocabulary; expected gate
families (mirroring `state-transition-pack` gate families):

- no state node reachable without a declaring machine
- every conformance case's event sequence stays inside declared transitions
- TTL regeneration matches `TtlBaseline` (deterministic serializer)
- every smoke test asserts on final state, not interactions

## Provenance

Truth source: `/Users/sac/srve/docs/diagrams/state/xstate/SHAPES.md`
(`Standing: PARTIAL_ALIVE`), the srve XState v5 machine-shape set. This
pack inherits that standing until qualified against the native ggen runtime.
