# errc-tracker.md — strata-audit-pack S10 construction lane

ERRC pass over the S10 construction lane (2026-10-13 session). All claims
verified against the working tree at edit time.

## Eliminate

- **No cross-pack require.** `requires = []` with the FM-PACK-018
  documentation-only note (same remediation as S2/S4/S5/S8); engine
  relationships are ontology comments + inline provenance copies, never
  owl:imports.
- **No engine-pack edits.** The audit is a read-only consumer of the
  landed laws: hash/merkle (S1), tx (S2), ledger (S4), chain (S5),
  consensus (S8) are provenance-copied minimally into the runner; the five
  engine packs are untouched.
- **No RNG, no wall-clock.** The corpus is a seeded LCG keyed by target
  name + case index; the same corpus is reproduced byte-for-byte on every
  run, so a failure is replayable by case number.
- **No net-pack target.** S9 hardening is corpus-pending; no FuzzTarget
  cites strata-net-pack — recorded in the ontology header and README.

## Reduce

- **One query, one rule.** `queries/audit_corpus.rq` projects both row
  kinds (target/attack) via a kind column; one template emits both tables.
- **Engine copies reduced to the audit-relevant subset.** No signer, no
  mempool, no tx-set Merkle in the block shape; each copy carries only the
  law under attack (e.g. chain validation drops the tx cap/duplicate arms
  because the corpus targets height/parent/slot/PoW).
- **The mismatch surface is one type** (`Mismatch`: target, case_index,
  detail) — a failure names its case; there is no bare-count path.

## Raise

- **Gates ARE the manifest.** 010 fails closed on any FuzzTarget missing
  targetModule/corpusSize/oracleFn (typed/malformed arms); 020 is the
  dangling-attack refusal — an attack whose st:targets does not resolve to
  a known FuzzTarget is a violation row (negative-controlled this session:
  breaking one mapping yields exactly the typed row).
- **The corpus court is a test, not prose**: `corpus_runs_1000_clean_per_target`
  asserts 1000/1000 clean on all 5 targets and prints the named mismatches
  on failure; `manifest_is_closed` pins 5 targets / 5 attacks / registered
  oracles / resolved attack targets.
- **Honest boundary raised to a contract**: the README and the generated
  module header both state that inline copies audit the LAW AS CAPTURED at
  the S10 copy point and must be refreshed after any engine edit — the
  audit's standing is the copy's standing.
- **Witness + verifier court**: `witness.ttl` pins the sync graph hash
  (d18c2d4d…); `verify.py` (provenance-copied strata-consensus-pack S8
  pattern) re-runs both gates and cross-checks the witness hash against
  the runtime receipt. Zero rows on this session's tree.

## Falsifiers (what would refute the standing claim)

- `ggen sync run` twice producing non-byte-identical `audit_corpus.rs`.
- Any of the 7 tests failing, or any corpus case reporting a MISMATCH.
- Any gate returning a violation row, or `verify.py` reporting a
  witness-hash drift.
- Qualification returning anything but ALIVE.
- A landed engine edit landing without the corresponding inline-copy
  refresh here (the audit would then certify a stale law).
