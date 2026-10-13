# Reference: refusal-vocabulary-pack crosswalk

Contract reference for [`packs/refusal-vocabulary-pack/`](../../packs/refusal-vocabulary-pack/):
the canonical FAIL-CLOSED crosswalk between erlmcp's integer refusal codes
(`erlmcp_refusal.hrl`, 1001-1089) and ash_a2a's RFC-SA2A-001 S42 refusal
classes (`lib/ash_a2a/semantic/refusal.ex`, 18 classes) plus the JSON-RPC
error law of `lib/ash_a2a/protocol/jsonrpc/error.ex`.

Class: **EvidencePack**. Authority: SELECT/CONSTRUCT — nothing here grants
runtime actuation authority; consequential DO stays behind BRCE admission.

## Mapping table shape

The mapping surface is RDF in
[`packs/refusal-vocabulary-pack/ontology.ttl`](../../packs/refusal-vocabulary-pack/ontology.ttl),
projected by [`queries/crosswalk.rq`](../../packs/refusal-vocabulary-pack/queries/crosswalk.rq)
into `generated/crosswalk.rs`. One `rv:RefusalMapping` individual per erlmcp
code carrying:

| property | meaning |
|---|---|
| `rv:erlmcpCode` | the erlmcp integer code (1001-1089) |
| `rv:macro` | the erlmcp macro name (e.g. `REFUSAL_TIMEOUT`) |
| `rv:ashA2aClass` | the target `rv:RefusalClass` individual |
| `rv:jsonRpcCode` | optional JSON-RPC wire code where one applies |
| `rv:httpStatus` | HTTP status for the wire surface |
| `rv:severity` | severity tier |

Each `rv:RefusalClass` individual carries `rv:className`, `rv:classKind`,
and maps to one of the 18 ash_a2a S42 refusal classes. A separate
`rv:ValveMapping` surface maps `rv:ValveClass` individuals (knhk k-law valve
admission) to declared refusal classes.

## Forced placements and the adjudicated deviation

The pack records four **FORCED placements** — codes whose class assignment
was made by pack-side adjudication rather than derived from erlmcp's native
`@mapping`:

- 1012 (auth token expired), 1023 (URI format invalid),
  1040 (canonical path validation failed), 1077 (server shutting down) —
  each tagged `FORCED placement` with an adjudication note in `ontology.ttl`.

One **adjudicated deviation** from ash_a2a's native classification is pinned:

- **1069 `REFUSAL_TIMEOUT`** → `refused_bounds`. ash_a2a's native `:timeout`
  classifies as `blocked_resource` (a local resource/dependency failing to
  answer in time); the pack reads an erlmcp timeout as a declared temporal
  bound breached. Both readings are internally coherent but disagree on the
  same concept name, so the disagreement is pinned in the deviation ledger
  of the ash_a2a differential court
  (`~/ash_a2a/test/ash_a2a_refusal_crosswalk_test.exs`, `@expected_deviations`)
  rather than papered over.

The differential court runs against pinned sha256 fixtures of the pack
(`~/ash_a2a/test/fixtures/refusal_vocabulary_pack/`): it asserts the pack
totals 51/51 codes, that every overlapping code agrees with the native
`@mapping` *except exactly the pinned deviation set*, that no FORCED
placement collides with a native entry, and that exactly 4 `FORCED placement`
flags exist in the ontology.

## Totality gates (closure-style)

Two closure-style gates refuse manufacture on any returned row; neither
hardcodes a literal count:

- `gates/040_totality.rq` (G4) — two bijections: every mapping's `rv:macro`
  is declared exactly once in the `rv:DeclaredMacro` universe (undeclared
  macro, unused declared macro, or double use all refuse), and every declared
  `rv:RefusalClass` is targeted by ≥1 mapping.
- `gates/050_valve_totality.rq` (G5, both directions): every declared
  `rv:ValveClass` is mapped by exactly one `rv:ValveMapping`, and every
  `rv:ValveMapping` is complete (declared `valveClass` + declared
  `ashA2aClass`).

Earlier gates: `010_exactly_one_class.rq` (G1: every code maps to exactly one
class), `020_class_coverage.rq` (G2: every class targeted ≥1), and
`030_jsonrpc_law.rq` (G3: any claimed JSON-RPC code must be lawfully present
in the JSON-RPC error law).

## How to add a mapping

1. Add an `rv:RefusalMapping` individual in `ontology.ttl` with
   `rv:erlmcpCode`, `rv:macro`, `rv:ashA2aClass`, `rv:httpStatus`
   (`rv:jsonRpcCode` optional), plus an `rv:DeclaredMacro` individual with
   the same `rv:macroName`.
2. If the target class is new, declare it as an `rv:RefusalClass` — G4's
   class-closure branch will otherwise refuse
   (`mapping-macro-not-in-declared-universe` /
   `declared-class-targeted-by-zero-mappings` is safe, but a class declared
   with zero mappings refuses).
3. If the code was previously unmapped or re-mapped, the ash_a2a differential
   court will refuse on any disagreement with the native `@mapping` that is
   not in its pinned deviation ledger. A new disagreement means: either fix
   the placement, or extend `@expected_deviations` in
   `~/ash_a2a/test/ash_a2a_refusal_crosswalk_test.exs` with an adjudication
   note (and add the matching note to `ontology.ttl`).
4. If the macro is already used, G4 refuses
   (`declared-macro-used-more-than-once`); if you delete a mapping, both the
   macro-closure and class-closure branches refuse.
5. Regenerate (`ggen sync run`) and run the pack court
   (`python3 verify.py`); the fixture sha256 pins in the ash_a2a suite will
   refuse any drift in `ontology.ttl` / `generated/crosswalk.rs`, so update
   the fixtures there in the same dependency-closed transition.

## Standing

`PARTIAL_ALIVE`: the projection and its gates are witnessed on the pack's own
surface plus the ash_a2a differential court; no consumer runtime boundary
beyond that court is exercised by this pack.
