# strata-governance-pack

X5 candidate 1, construction lane T11: the Strata governance layer as an
ontology-backed ggen pack. The constitutional-diff law: consensus constants
are SEALED in `GovernanceCommitment` individuals (the constitution); any
sync whose projected constants drift from the sealed commitment is REFUSED
with violation rows citing the commitment.

## What it models

One RDF ontology (`https://strata.chatman.ai/ontology#`), no code
generation beyond the report:

- `GovernanceCommitment` — a sealed constitution. Five individuals:
  `Commitment-GenesisLayout` (GENESIS_HEIGHT, GENESIS_PREV,
  INITIAL_DIFFICULTY_TARGET) and `Commitment-BlockBudget` (MAX_BLOCK_TXS),
  both subject `strata-chain-pack GENESIS_CONSTANTS`;
  `Commitment-NetRateLimits` (ECLIPSE_SUBNET_CAP=8, MAX_MSGS_PER_SLOT=32),
  subject `strata-net-pack NET_CONSTANTS (rate limits)`;
  `Commitment-LedgerConstants` (MAX_ACCOUNTS=65536, TRANSITION_GAS=0,
  STATE_ROOT_LEN=32), subject `strata-ledger-pack LEDGER_CONSTANTS`;
  `Commitment-A2aWireLaw` (A2A_WIRE_CODE=-32000,
  A2A_WIRE_RANGE=server-error-implementation, A2A_RATE_LIMITED_CLASS=
  refused_bounds, A2A_SERVER_BUSY_CLASS=blocked_resource), subject
  `refusal-vocabulary-pack A2aWireMapping (A2A wire law)`.
- `SealedConstant` — authority side: name, value, and a SHA-256 seal digest
  over `NAME=value`. Sealed values match `strata-chain-pack`'s
  `GENESIS_CONSTANTS` exactly (read from
  `packs/strata-chain-pack/ontology.ttl` at pack-authoring time:
  GENESIS_HEIGHT=0, GENESIS_PREV=0x000…0, INITIAL_DIFFICULTY_TARGET=12,
  MAX_BLOCK_TXS=256).
- `ProjectedConstant` — projection side: what the family projection
  manufactures. The gate compares every projection against its seal.
- `ConstantDiff` — one diff-table row, derived by the report rule.

## Gates

- `gates/010_constitutional_diff.rq` — the law: drift (sealed vs projected
  value mismatch), unprojected constants, and uncommitted projections all
  fire violation rows citing the commitment. Zero rows = projection
  agrees with the constitution.
- `gates/020_commitment_closure.rq` — fail-closed V7 arms: no empty
  commitments, no orphan seals, no missing names/values/digests, malformed
  integers refused, GENESIS_PREV must be 0x + 64 hex chars.

## Build

```bash
cd packs/strata-governance-pack
ggen sync run    # regenerates generated/governance_report.rs from ontology.ttl
rustc --test -O generated/governance_report.rs -o /tmp/gov_report && /tmp/gov_report
python3 verify.py
```

## Verification ladder (receipted this session)

1. `ggen sync run` x2 -> byte-identical `generated/governance_report.rs`
   (sha256 `48f3cbd3…`).
2. `rustc --test` — 6/6 tests pass: `constitution_holds` (17 rows, all
   MATCH, `verify_constitution() == Ok(())`), `seal_digests_rederive`
   (all seventeen SHA-256 seals re-derive under the module's own FIPS 180-4
   SHA-256), `out_of_constitution_edit_refused` (the original falsifier),
   `law_surface_drift_refused` (L166: downgrading the sealed
   MEMPOOL_LEDGER_ADMISSION law is refused citing `MempoolLedgerAdmission`),
   `a2a_wire_law_drift_refused` (L192: projecting a different wire code,
   -32000 -> -32001, is refused citing `A2aWireLaw`), and
   `sabotage_twin_unframed_seal_digest_is_caught` (L124).
3. Gates zero-rows via rdflib (`verify.py`):
   010 constitutional-diff 0 rows; 020 commitment closure 0 rows.
4. FALSIFIER (mutation witness, rdflib): changing the projected
   INITIAL_DIFFICULTY_TARGET 12 -> 13 yields 1 violation row citing
   `GenesisLayout`:
   `constitutional_drift: INITIAL_DIFFICULTY_TARGET sealed in commitment
   GenesisLayout as 12 but projection manufactures 13`. Refusal is
   fail-closed in both directions (unprojected seals and uncommitted
   projections also refuse).
5. `python3 scripts/marketplace.py validate` — 324/324 packs validated.
6. `python3 scripts/qualify_packs.py` — strata-governance-pack
   **ALIVE** (isolated single-pack capsule, requires = []).

## Standing

ALIVE at this subject (sync receipt `.ggen-v2/receipt.json`,
graph_hash `14525cba…`), witnessed in `witness.ttl`. The seal digest is
tamper-evident: any edit to a sealed value breaks its SHA-256 re-derivation
in the generated test as well as the gate diff.
