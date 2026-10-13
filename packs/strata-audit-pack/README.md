# strata-audit-pack

S10 — the final slice — of the Strata blockchain roadmap
(`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): the external audit
surface as an ontology-backed ggen pack. It is the AUDIT MANIFEST plus a
self-contained audit RUNNER, not an engine: it names the fuzz targets over
the landed S1–S8 engines and the known attacks those engines' refusals must
repel, then executes a deterministic corpus against them. strata-net-pack
(S9 hardening) is **corpus-pending** — no FuzzTarget cites it yet.

## What it projects

One generated Rust module from one RDF ontology
(`https://strata.chatman.ai/ontology#`):

- `generated/audit_corpus.rs` — the projected corpus manifest
  (`AUDIT_TARGETS`: 5 FuzzTarget rows with targetModule / corpusSize /
  oracleFn; `KNOWN_ATTACKS`: 5 attack→target→expected-refusal rows), a
  deterministic LCG corpus generator (seeded, 1000 cases per target, no RNG,
  no wall-clock), inline provenance COPIES of the audited engine functions
  (SHA-256 + Merkle from strata-hash-pack S1; framed tx encode/decode from
  strata-tx-pack S2; block validation from strata-chain-pack S5;
  heaviest-tip selection + selfish-mining detection from
  strata-consensus-pack S8; masked-commit conservation from
  strata-ledger-pack S4 — each copied with a provenance header), the audit
  runner (`run_audit()` reporting per-target clean/total counts and naming
  every mismatch by target + case index), and the 5 known-attack
  regression tests.

## Honest boundary

The runner executes INLINE COPIES of the engine functions, so the audit's
standing is exactly the standing of the copy: it audits the LAW AS CAPTURED
at the S10 copy point. After ANY edit to a landed engine pack, re-run this
audit against that engine's freshly regenerated module (regenerate the
engine pack, refresh the corresponding inline copy here, `ggen sync run`,
re-run the tests). A clean run does not certify a future engine revision.

## Gates

- `gates/010_audit_layout.rq` — fail-closed corpus-manifest layout (V7
  pattern): every FuzzTarget must carry targetModule + corpusSize +
  oracleFn with correct datatypes; AUDIT_PLAN must carry lastCleanRun.
- `gates/020_attack_closure.rq` — the dangling-attack refusal: every
  KnownAttack must map via st:targets to a known FuzzTarget and carry a
  non-empty attackClass and expectedRefusal; an attack naming an absent
  target is a violation row.

## Verify

```bash
cd packs/strata-audit-pack
ggen sync run    # ×2, byte-identical (determinism court)
rustc --test -O generated/audit_corpus.rs -o /tmp/audit_corpus && /tmp/audit_corpus
python3 verify.py                       # gates zero-rows + witness-hash court
python3 scripts/qualify_packs.py --pack strata-audit-pack
```

Corpus receipt (2026-10-13 refresh, ggen 26.10.11): 6/6 targets 1000/1000
clean (6000 corpus cases), 12/12 tests pass (manifest closure — 6 targets /
10 attacks —, corpus court, 10 attack regressions), gates 0 rows,
qualification ALIVE. S10 refresh added the pn64_mask_apply fuzz target
(strata-pn64-pack @ 00e0b086b) and 5 landed-work attack entries
(Pn64FireLawXorDivergence, Pn64T04MaskCorrection, ValveZeroRefusalReceipt,
LedgerTokenSumNonConservation, VacuousEunitHarness).

## Standing

`ALIVE` (qualification 2026-10-13, ggen 26.10.11). The pack projects a
specification + audit harness under the house SELECT/CONSTRUCT fence — it
projects code and grants no DO authority. It does not modify the landed
engine packs; it audits captured copies of their laws.
