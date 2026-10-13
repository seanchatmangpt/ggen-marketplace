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
- OCEL-v2 emission + PN64 conformance surface (X4 / innovation Tier-1, lane
  T2): every apply_transition emits one OcelEvent (type = transition name,
  timestamp = index, objects = touched accounts); `verify_conformance` replays
  the log against the PN64 normative model with wasm4pm-style alignment moves
  (sync=0, log/model=1; PROVENANCE ONLY from /Users/sac/wasm4pm — no code
  vendored). `inject_event` is the court-injection surface proving the checker
  non-vacuous. Gate 030 mirrors the law over the witness graph; all 4 arms
  fire under mutation (dropped link, drifted timestamp, dangling object,
  stripped type). Emit-then-verify round-trip: 200 transitions → 200 events,
  cost-0 alignment; a fabricated transition is refused as a log move.
