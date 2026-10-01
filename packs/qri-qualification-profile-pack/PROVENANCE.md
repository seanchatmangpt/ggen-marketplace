# Provenance

Semantic source: the QRI research brief supplied by the operator on 2026-09-30.

Reused capital (read, not modified):

- `/Users/sac/graphlaw` `wasm/src/lib.rs`: the `gl_alloc` / `gl_free` / `gl_call` ABI shape.
- `/Users/sac/ash_graphlaw` `lib/ash_graphlaw/{host,engine_load}.ex`: wasmex host, digest pin,
  import allowlist, typed refusals.
- `/Users/sac/ash_a2a` `lib/ash_a2a/graph_law/`: same bytes hosted twice, digest parity.
- `/Users/sac/beam4pm/native/graphlaw/graphlaw_wasm.wasm` (sha256 84113e6d...): admitted by the
  generated host against the `gl` contract during development (not asserted by a test).
- `packs/qualified-capability-ecology-pack`: related terms (`qce:QualificationReceipt`,
  `qce:SubstitutionClaim`); linked with `skos:relatedMatch`, not equated.

No ODRL, SPDX or QUDT pack exists in this repository; those are referenced by IRI only.

Formerly ledgered UNSUPPORTED(ontology-gap) deltas of the generated beam host against
`/Users/sac/ash_graphlaw`, now closed by vocabulary and projection (2026-09-30), values in
`ontology/examples/ash-graphlaw-contract.ttl`:

- zero-valid store limits (`table_elements`, `instances`, `tables`, `memories`): `qri:limitZeroOk` +
  `qri:limitZeroMeaning` (gate 090); `wasm_config.ex` generates `min_limit/1` and `@zero_ok`.
- `@recycle_codes` order: `qri:recycleRule` / `qri:recycleOrder` (gate 100); query 54 sorts by order.
- `Host.request/3` `@doc` example op: `qri:docExampleOp`.

Still residue (not generated): module `@moduledoc`/prose docs, SPDX headers and the
UNSUPPORTED(generator-capability) banner of the hand-written modules. `probeExpectKey` is `abi`, the
key the `capabilities` op actually returns.
