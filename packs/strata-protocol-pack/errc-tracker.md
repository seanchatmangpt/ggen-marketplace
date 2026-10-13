# errc-tracker.md — strata-protocol-pack projection + gate hardening (L7, wave v26.10.8)

ERRC pass over this wave's landing of the wire-class projection, the header-layout
and refusal-receipt gates, and the ontology's `wire:WireClass` typing. Format per
`packs/ex-noun-verb-cli-pack/errc-tracker.md`. Every entry cites a real file:line
re-read at write time.

## Eliminate

- `clap_frame.rs.tmpl` deleted this wave (commit `11c749278`,
  "refactor(strata packs): ontology hygiene + delete dead clap_frame template");
  no rule references it anymore — `packs/strata-protocol-pack/ggen.toml:29-35` is
  the only generation rule that survived in that family here, now joined by
  `wire-constants` (`ggen.toml:37-42`). Dead template weight is gone permanently.

## Raise

- **Gates landed and witnessed refusing**: `gates/010_header_layout.rq` (offset
  abutment chain MAGIC 0+4→4 … CANDIDATE 60+4→64 == `PDU_HEADER_LEN`, plus
  EPOCH_NONCE=8 / FUEL_LEASE=16 sentinels; distinctness is implied by the chain
  with strictly positive lengths) and `gates/020_refusal_receipt_len.rq`
  (REFUSAL_RECEIPT_LEN == RefusalReceipt fixedLen == 32 triangle). Both wired
  into `[validation]` at `packs/strata-protocol-pack/ggen.toml:20-24`) witnessed
  refusing sync with FM-LAW-018 on mutated
  ontology copies (negative witnesses run 2026-10-12, see /tmp receipts above —
  copies deleted after capture). Positive path: `ggen sync run` exit 0, twice,
  `generated/pdu_constants.rs` byte-identical (sha256 7bf79283… at write time; superseded by ed8c2600… after the namespace-migration banner regen) before and
  after.
- **Wire-class projection raised from untyped classes to a fixed-length
  vocabulary**: `ontology.ttl:103-115` now declares `wire:WireClass` and types
  `wire:ReceiptDigest`/`wire:RefusalReceipt` as `wire:WireClass`, each with
  `wire:fixedLen 32` (ReceiptDigest's 32-byte BLAKE3 ground truth is in its own
  comment, ontology.ttl:110). `queries/wire_classes.rq` + `templates/wire_constants.rs.tera`
  project them into `generated/wire_constants.rs` inside `pub mod wire` — no
  clash with the flat `pdu_constants.rs` namespace.

- **V-wave (T20 exploit repair) — label-omission closed by V1 VALUES
  presence branch**: T20 confirmed that deleting the
  `HISTORY_QUAD_COUNT_LEN` label from the ontology let gate
  `010_header_layout.rq` silently pass (the deleted label simply matched no
  row) while the generated constant was silently dropped from
  `generated/pdu_constants.rs` — gate green, artifact wrong. Closed by V1:
  a VALUES-driven branch enumerating all 23 required labels and asserting
  each is present, so any omission yields a gate row instead of silence.
  Negative witnesses re-run on the repaired gate (2026-10-12).

## Create

- **Cross-pack gate candidate (pending, valve side)**: strata-valve-pack already
  projects refusals (`packs/strata-valve-pack/templates/refusals.ex.tera`,
  modified this wave) from the same 32-byte refusal-receipt ground truth. A
  valve-side gate asserting the valve refusal record's fixed length matches this
  pack's `wire:RefusalReceipt` `wire:fixedLen` would turn the cross-pack
  constant-sharing assumption into an executed court. Out of L7's lane boundary
  (`packs/strata-protocol-pack/**` only) — recorded here as the next wave's
  Create item.

## Reduce

- **Namespace split pending wave migration**: `generated/wire_constants.rs`
  embeds its constants in `pub mod wire` while `pdu_constants.rs` stays flat —
  two namespace conventions in one `generated/` dir. Consolidating on the
  module-wrapped form (or migrating `pdu_constants.rs` into `pub mod pdu`) is a
  generated-output change requiring a coordinated wave across consumer repos;
  deferred to the next wave migration rather than patched ad hoc.

## S2 hardening wave (L77, 2026-10-13)

- **Gate 030 added** (`gates/030_refusal_taxonomy_closure.rq`): 4-atom
  refusal-taxonomy enum (MalformedFrame/FuelExhausted/ParentDiscontinuity/
  ArenaFailure) fail-closed on both sides — missing atom or fifth atom both
  yield rows — plus per-atom receiptLen == RefusalReceipt fixedLen and
  fixedLen == 32. Registered in ggen.toml, pack.toml, witness.ttl.
- **Ontology**: `wire:RefusalTaxonomy` class + 4 atoms added (the wire-level
  law the valve pack's projection mirrors).
- **Rust courts (7 total, 0 warnings, edition-2015-clean)**:
  pdu_constants — abutment tiling of [0,64) from ontology-derived constants
  with fail-closed 9-field enumeration (dropped field breaks compilation);
  sabotage twins (widened RESERVED_LEN, gap, overlap) trip the same checker.
  wire_constants — exhaustive 2-class wire enum; taxonomy closure court
  against `pinned/strata-valve-refusals.ex` (sha256 header pin
  de7bd39b05b4cc78a6356cc84286301fc1b424c7bb592582ebbc3ca792740335,
  re-verified by verify.py against the pinned body AND the live valve
  projection). Resolves the cross-pack gate candidate above from this side.
- **Sabotage witnessed (real runs)**: mutated RESERVED_LEN 2→3 refuses at the
  actuator (FM-LAW-018, ggen 26.10.11); with the gate removed, the rendered
  module's abutment test fails (`field 4: [8,16) OVERLAP`, exit 101). Dropped
  FuelExhausted atom → gate 030 row `MISSING-ATOM`, verify.py exit 1.
- **Receipts**: regen ×2 byte-identical; verify.py zero-rows + pinned court
  PASS; qualify_packs.py → status ALIVE (consequence_sha256
  c0b0c667a090171753815692b594028c8a668a31969d1acff68f292c6770ac17,
  0.091s pass).
