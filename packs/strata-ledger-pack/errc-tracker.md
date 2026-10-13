# errc-tracker.md — strata-ledger-pack (roadmap slice S4)

## Eliminate
- No serde, allocator overhead beyond BTreeMap, or crypto dependency in the
  generated module — placeholder root mixing only until S1 binds the real hash
  (an unearned capability until a consumer demands it).
- No coinbase/mint transition type: the transition law never creates value;
  supply enters only via documented genesis allocation (`with_genesis`), so
  conservation is total over ALL transitions (stronger than a mint-exempt law).

## Reduce
- `requires = []` with FM-PACK-018 documentation-only notes (strata-tx-pack S2
  remediation carried forward): TxLike mirrors the S2 Tx shape by provenance
  comment; unibit law by ontology comment citing
  /Users/sac/unibit/crates/unibit-kernel/src/lib.rs — no code vendored (BUSL-1.1).
- One query feeds both generation rules (`queries/ledger_constants.rq`): the
  constants table is the only ontology-projected data the state machine needs.

## Raise
- Gate 020 is the PROJECTED LAW as a SPARQL court over real witness-chain
  individuals (non-vacuous): presence, index uniqueness, receipt mirroring,
  prev→next linearity — 7 mutation witnesses each fire (verified live this
  build; the first receipt-mirror arm caught its own bug: joining all receipts
  instead of the transition's own receipt fired 2 rows on the clean graph).
- Masked commit is asserted as a test invariant, not prose: double-spend and
  conservation refusals assert bit-identical roots/balances post-refusal.
- Generated module compiles edition-agnostically (`rustc --test`, explicit
  casts, no cargo required for the test court).

## Create
- `urn:strata:ledger:state-v1` capability URN minted (S5 chain pack consumes
  the receipt chain; S8 consensus formalizes on the PN64 transition lattice).
- Receipt-chain verification API (`verify_receipt_chain`) projected as the
  abutment surface S5's chain-validity gate will consume.
