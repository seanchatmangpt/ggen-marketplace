# STRATA-AUDIT-1 — CLOSED

- **Item**: STRATA-HARDENING-1 post-landing adversarial audit — a 20-lane wave
  (A1–A20) over the `strata-hardening-wave` branch, following the STRATA
  namespace-unification landing (commit `0ea25a5c8` / `bc54e0869` line), to
  attack the hardened gates, generated consumers, docs, and receipts the wave
  produced.
- **Status**: CLOSED 2026-10-13 (lane S9).
- **Fix shape**: every audit finding was dispositioned by a repair lane
  (R1–R21, S1–S9) against the same canonical checkout. Disposition summary:

  **ACCEPTED + FIXED**
  - pn64: gate presence arms — bounds/transition gates now fire on the arms
    they claim to cover (`packs/strata-pn64-pack/gates/010_place_offset_bounds.rq`,
    `020_transition_pre_nonzero.rq`).
  - valve: closure gate defect
    (`packs/strata-valve-pack/gates/010_refusal_atom_closure.rq`).
  - protocol: `010_header_layout.rq` and `020_refusal_receipt_len.rq` gate
    defects.
  - signer: README transpose (`packs/strata-signer-pack/README.md`).
  - CI: `--scope` comment corrected in `ci/courts/strata-packs-court.sh`.
  - firelaw: fake twin removed, tautological sweep added, 65536 docstring
    corrected (`tests/test_strata_firelaw.py`).
  - stratus: silent-file hole closed
    (`packs/strata-stratus-pack/templates/*.rs.tera`, regenerated
    `generated/registers.rs` / `generated/valves.rs`).
  - corpus: assert-message + 3 fake twins (`tests/test_strata_corpus.py`,
    `tests/test_strata_family_pack.py`).
  - docs: phantom `urn:strata` references removed
    (`docs/reference/pack-classes.md`, `docs/reference/strata-family-contracts.md`,
    `docs/how-to/generate-from-strata-ontologies.md`,
    `docs/tutorials/consume-the-strata-family.md`,
    `docs/explanation/strata-family-design.md`).
  - alpha overclaim tightened in pack READMEs
    (`packs/strata-cas-pack/README.md`, `packs/strata-stratus-pack/README.md`,
    `packs/strata-temprun-pack/README.md`).
  - NAMESPACE-MAP LANDED note aligned to actual landing state
    (`docs/sjira/v26.10.8/STRATA-NAMESPACE-MAP.md`).
  - cas: `depth()` recursion hazard fixed
    (`packs/strata-cas-pack/templates/cas.rs.tera` → `generated/cas.rs`).
  - temprun: admissionFuel projection corrected.
  - banners + README packaging-profile text aligned across the family.
  - receipt-index / sync-receipt records corrected to match observed state.

  **REJECTED ON WITNESS HIERARCHY**
  - A1 "gates are never executed": rejected — 4 independent lanes witnessed
    executed FM-LAW-018 refusals through the real court path; the claim
    described the gate definition, not the executed boundary.
  - `urn:strata` capability-token complaints: rejected — tokens are
    documented by-design (namespace map), not drift.

  **PRE-EXISTING (not introduced by this wave; recorded, not repaired here)**
  - industry-closure minimal-manifest test failure, traced to `f52ed0e85`.
  - qri unqualified references.
  - ggen pin 26.8.11 frozen-court `BLOCKED` (R16 root-caused the frozen-court
    FAIL to the pin, not to strata pack content).

- **Witnesses**:
  1. A8 gate-vacuity table: 12 gates audited, 0 empty-result rows after
     repair; vacuity ranking drove the pn64/valve/protocol gate fixes above.
  2. A9 byte-reproducibility: 7/7 strata generated files re-render
     byte-identical from their ontologies/templates.
  3. A20 drift sweep: zero drift outside the declared allowlist across the
     family's generated surfaces.
  4. R16 frozen-court FAIL root-cause receipt (pin 26.8.11), separating
     toolchain standing from pack standing.
  5. S14 pin-survey decomposition of the ~170 frozen-court refusals
     (163 FM-PACK-003 / 6 FM-CHAIN-003 / 1 FM-GRAPH-003; see
     SYNC-WAVE-RECEIPT.md §BLOCKED) — postdates the audit, confirms the
     R16 toolchain-vs-pack separation.

- **Consumer consequence**: future waves inherit hardened, non-vacuous gates
  and honest courts — the audit's fixes are landed on the same branch, so any
  consumer regenerating from the strata family gets the repaired gate set,
  corrected generated code (cas `depth()`, stratus file handling, temprun
  admissionFuel), and docs free of phantom `urn:strata` references. The
  pre-existing items above remain open against their origin commits, not
  against this wave.

## Per-lane disposition ledger (2026-10-13)

T18 ledger-gap repair: A1–A20 were dispositioned only in aggregate above. Each
audit lane's scope is read from `_STRATA_LANES.md` (L1–L19 pathspec partition);
findings are restated per lane. Lanes S13–S22, U1–U20, and V postdate the
original A-lane range and are appended below.

### A lanes (audit, A1–A20)

1. **A1** — gate-execution claim; REJECTED on witness hierarchy (4 lanes
   witnessed executed FM-LAW-018 refusals through the real court path; the
   claim described the gate definition, not the executed boundary).
2. **A2** — valve pack audit (`packs/strata-valve-pack/**`): runtime +
   closure-gate defect found; fixed (`gates/010_refusal_atom_closure.rq`).
3. **A3** — pn64 pack audit (`packs/strata-pn64-pack/**`): gate presence arms
   missing — bounds/transition gates now fire on the arms they claim to cover
   (`gates/010_place_offset_bounds.rq`, `020_transition_pre_nonzero.rq`).
4. **A4** — temprun pack audit (`packs/strata-temprun-pack/**`): clean; no
   defects.
5. **A5** — signer pack audit (`packs/strata-signer-pack/**`): README
   transpose fixed; typed-literal note recorded.
6. **A6** — stratus pack audit (`packs/strata-stratus-pack/**`): clean at the
   audit layer (silent-file hole was closed by a repair lane, see S-lanes).
7. **A7** — cas pack audit (`packs/strata-cas-pack/**`): clean at the audit
   layer.
8. **A8** — gate-vacuity table: 12 gates audited, 0 empty-result rows after
   repair; vacuity ranking drove the pn64/valve/protocol gate fixes.
9. **A9** — byte-reproducibility: 7/7 strata generated files re-render
   byte-identical from their ontologies/templates.
10. **A10** — namespace residue: phantom `urn:strata` references found in
    docs; removed across 5 doc files (see docs fixes above).
11. **A11** — pack.toml consistency (README packaging profiles, base_iri):
    banners + README packaging-profile text aligned across the family; the
    companion D3 overclaim was downgraded to the tightened alpha wording.
12. **A12** — lifecycle.toml conformance audit: conform; no defects.
13. **A13** — corpus audit (`tests/test_strata_corpus.py`): polish findings —
    assert messages + 3 fake twins repaired (with family-pack lane).
14. **A14** — family-test holes (`tests/test_strata_family_pack.py`): test
    holes closed.
15. **A15** — firelaw audit (`tests/test_strata_firelaw.py`): tautological
    sweep replaced + fake twin removed; 65536 docstring corrected.
16. **A16** — CI court audit (`ci/courts/strata-packs-court.sh`): `--scope`
    comment corrected.
17. **A17** — docs claims audit (`docs/**` strata files): alpha overclaim and
    NAMESPACE-MAP LANDED note aligned to actual state.
18. **A18** — docs navigation audit (`docs/book.ttl`): clean; no defects.
19. **A19** — receipt audit (`docs/sjira/v26.10.8` strata receipts):
    receipt-index / sync-receipt records corrected to match observed state.
20. **A20** — family-wide drift sweep: zero drift outside the declared
    allowlist across generated surfaces.

### R lanes (repairs, partial record)

- **R13** — citation audit (part 1): findings annotated into the affected
  pack errc-trackers.
- **R14** — citation audit (part 2): findings annotated into the affected
  pack errc-trackers.

### S lanes (post-range, S13/S16/S19/S22)

- **S13** — readiness criteria review: criteria applied across the family;
  S22 flipped as a result.
- **S16** — stratus coupling: coupling finding resolved via S21.
- **S19** — count sweep: stale counts found and fixed at their sources.
- **S22** — readiness status flipped (driven by S13's criteria pass).

### U lanes (U1–U20, summary)

Verify-gate audit lanes over the per-pack `verify.py`/`witness.ttl` surfaces.
Aggregate findings: the verify.py gate-set defect (→ V4); witness-hash
exactness verified; pre-existing triages recorded for qri references and
quickstart (not introduced by this wave); environment skew between lanes
noted; one fabricated capability verb found in a pack README and fixed.

### V lane (adversarial exploits)

- **V1/V2** — T20 exploits against D1/D2 both landed: the two defects found
  by the T-wave were repaired by V1 and V2.

**SATURATION**: the T-wave found 2 defects (D1, D2), both repaired by V1/V2;
the next full-wave verdict is pending.

## Per-lane ledger — Z-wave append (2026-10-12, lane Z19)

### C lanes (C1–C7 saturation recertification)

| lane | scope | verdict |
|---|---|---|
| C1 | gate-set saturation recert (pn64/valve/protocol arms) | CERTIFIED |
| C2 | generated-surface byte-reproducibility recert | CERTIFIED |
| C3 | docs residue sweep recert (`urn:strata` phantom class) | CERTIFIED |
| C4 | corpus/family-test hole recert | CERTIFIED |
| C5 | receipt/index consistency recert | CERTIFIED |
| C6 | CI court scope recert | CERTIFIED |
| C7 | family drift allowlist recert | CERTIFIED |

All seven C lanes returned CERTIFIED — no new defects at the recertified
surfaces.

### S-* rows (follow-up sweep)

- All S-rows green at append time.
- **S-R**: HARDENING-1 P10 row amended to the 6-deleted lifecycle closure
  (S-R defect) — fixed in `d2bbd0e9a` (docs(sjira)).
- The garbled Falsifier/Extensions clause splice (S-F defect) repaired in
  `9a7c3c7cb` (docs(strata)).

### Y-rows (redundant recertification wave)

- **Y1–Y5, Y7, Y8 (7 lanes)** — redundant recerts over already-CERTIFIED
  surfaces: 7/7 PASS, zero new findings. Confirms C-lane saturation at these
  surfaces.
- **Y6** — typed-malformed-lexical fail-open in the pn64/temprun gates:
  real residual, fixed in `fdd4df201` (fix(strata)) — the one defect the
  redundant wave surfaced, repaired and witnessed same-session.
- **Y14** — pre-existing suite-failure triage receipt: 30+5 failures all
  non-strata, root-caused on `main` (`d7466faf0`, docs(sjira)); recorded,
  not repaired in this wave.

### SATURATION (final, honest)

No formal zero-defect full wave has completed yet. Observed shape: the
redundant Y-wave returned 7/7 PASS with exactly one real residual (Y6,
repaired `fdd4df201`), and finding yield is declining to the doc-class tail
(S-F splice, S-R P10 row) — both repaired and witnessed in the same session
they were found. Per the saturation law, zero defects on a full wave is the
gate; this ledger records the trend toward it, not its arrival.
