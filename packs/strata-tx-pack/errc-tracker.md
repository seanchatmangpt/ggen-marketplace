# errc-tracker.md — strata-tx-pack (roadmap slice S2)

## Eliminate
- No serde/allocator dependencies in the generated module — manual
  fixed-width encode/decode only (CLAP-PDU convention; a varint layer would
  be an unearned capability until a consumer demands it).

## Reduce
- `requires = []` with the FM-PACK-018 documentation-only relationship note
  (same remediation as `strata-pn64-pack`): the CLAP-PDU derivation is cited
  by ontology comment, never an unresolvable cross-pack dependency.
- Payload digest reduced to a documented deterministic placeholder over
  (n, m) so the tamper court has a real check without faking S3's signer.

## Raise
- Gates carry fail-closed datatype + malformed-integer arms (V7 pattern from
  `strata-pn64-pack/gates/010_place_offset_bounds.rq`): a string-typed or
  malformed constant fires a violation instead of silently passing the
  layout checks (engine-dependent fail-open; caught live during this build —
  untyped `"0"` literals fired 18 rows until typed `^^xsd:integer`).
- Gate 020 closure is bidirectional: missing declarations fire AND any
  property claiming `rdfs:domain st:Tx` outside the declared field set fires
  (undeclared fields cannot accrete silently).
- Generated module compiles edition-agnostically (`rustc --test` under the
  default 2015 edition via explicit `TryFrom`/`TryInto` imports) — no cargo
  required for the test court.

## Create
- `urn:strata:tx:model-v1` capability URN minted (S3 signer, S4 ledger, S5
  chain packs consume this framing).
- Replay-guard surface: `Tx::replay_guard(seen, nonce, inputs)` — same
  nonce over the same input set rejected; ledger-level uniqueness deferred
  to S4 (explicit non-goal here, not an omission).

## Standing
ALIVE (qualification receipt 2026-10-13: sync x2 byte-identical, 9/9 Rust
tests, 2/2 gates 0 rows, qualify_packs status ALIVE).
