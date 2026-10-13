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

L127 refresh (2026-10-13, ggen 26.10.11): 3 more real findings as additive
corpus entries — ChainWorkSaturationTie (strata-consensus-pack @ 0c7c9e594;
u64 saturating fold pinned as the sabotage twin, u128 fix `chain_work_u128`
in the audit copy, consensus tie-court regression),
GgenUnionBindingLeak (cross-repo ggen SPARQL OPTIONAL/UNION binding leak,
OPEN-UPSTREAM; rdflib row-shape differential court), and
WasmNonReproducibleBuild (graphlaw @ b473313, OPEN; ABI-surface gate).
Receipt: 6/6 targets 1000/1000 clean, 13/13 tests pass (manifest closure —
6 targets / 14 attacks —, corpus court, 11 attack regressions), gates 0
rows, byte-identical ×2, qualification ALIVE.

L156 refresh (2026-10-13, ggen 26.10.11) — inline-copy staleness sweep.
Three copies were PINNED-STALE (auditing dead laws) and were re-captured
at the current subject-pack law: (1) hash/merkle — domain-separated
leaf/node tags (strata-hash-pack @ 5c932f000; the copy predated the
domain-separation court); (2) tx digest — BLAKE3-256 over the FULL
canonical frame, digest slot zeroed (strata-tx-pack @ 320833d12; the
FNV-1a(n, m) stand-in was retired upstream in L125); (3) ledger funds
gate — duplicate-input DEBIT ACCUMULATION law (strata-ledger-pack
@ e1ee25fa2; the per-row check underflowed on the exact
[(a,5),(a,5)]->[(b,10)] Lean counterexample the corpus's own
DuplicateInputAccountValueCreation row names — now refused, state
bit-identical, with a dedicated regression test). PINNED-CURRENT: pn64
masks (t04 0x0010/0x0008 byte-equal since 00e0b086b; pin refreshed to
@ 5c932f000), consensus u128 work law + u64 sabotage twin (@ 0c7c9e594),
chain validate_block four-gate subset (@ e1ee25fa2). Added the
copy-staleness meta-court (FIPS 180-4 + BLAKE3 spec KATs anchoring the
copied hash primitives; sha256 pin over the canonical 48-byte pn64
mask-table serialization) and the duplicate-input attack regression.
Receipt: 6/6 targets 1000/1000 clean (6000 cases), 15/15 tests pass
(manifest closure — 6 targets / 14 attacks —, corpus court, 12 attack
regressions), gates 0 rows, byte-identical ×2, 0 rustc warnings,
qualification ALIVE.

## Standing

`ALIVE` (qualification 2026-10-13, ggen 26.10.11). The pack projects a
specification + audit harness under the house SELECT/CONSTRUCT fence — it
projects code and grants no DO authority. It does not modify the landed
engine packs; it audits captured copies of their laws.
