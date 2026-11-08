# Pack Seal Receipt: xstate-v5-machine-pack

Standing: PARTIAL_ALIVE

Seal receipt for `packs/xstate-v5-machine-pack` v0.1.0, written per the M1
cs2-conformance-pack seal standard (positive fixture qualifies every gate;
divergent fixture every gate must REJECT). Standing inherited PARTIAL_ALIVE
from `docs/SHAPES.md`: shapes are court-witnessed on the srve source corpus;
cross-repo pilot confirmation is pending (see Open Items).

## 1. Contents census (verified on disk 2026-11-07)

| component | path | present |
|---|---|---|
| manifest | `pack.toml` (v0.1.0, xs5: vocab, M15 st: align) | yes |
| ontology | `ontology.ttl` | yes |
| templates | `machine.tera.tmpl`, `smoke.tera.tmpl`, `conformance-matrix.tera.tmpl` | yes (3) |
| gates | `gates/010_ttl_triple_counts.py`, `gates/020_compile_shape_scan.py` | yes (2) |
| gate configs | `gates/baselines.toml` (srve J14 baselines), `gates/shapes.toml` | yes |
| tool | `tools/construct_gate.py` (esbuild bundle + createActor().start()) | yes |
| fixtures | `positive-machine.json`, `divergent-machine.json`, `divergent-notes.md` | yes (3) |
| qualification | `qualification/consumer.ttl` (st: identity facts, M15 non-dangling) | yes |
| docs | `README.md`, `docs/SHAPES.md` | yes |

All components of the census family (pack.toml/ontology/templates/gates/
tools/fixtures/qualification/docs) are present. No missing cells.

## 2. Gate self-test results (real runs, 2026-11-07)

### Gate 010 — TTL triple counts vs srve J14 baselines

    python3 gates/010_ttl_triple_counts.py --root /Users/sac/srve

    OK    finance.ttl: actual=280 expected=280
    OK    routes-forms.ttl: actual=297 expected=297
    OK    procurement.ttl: actual=135 expected=135
    OK    authz.ttl: actual=87 expected=87
    OK    4/4 terms present (APBill, FormLifecycleAction, typeGatedTo,
          ImpersonationWriteAuthority)
    COURT: PASS — all triple counts match baselines, all terms present
    EXIT=0

### Gate 020 — compile-shape scan vs srve registered subject

    python3 gates/020_compile_shape_scan.py --config gates/shapes.toml \
      --root /Users/sac/srve

    SHAPE-COURT: PASS — 1 subject(s), 0 violations
      (3 banned-token laws + setup-seam)
    EXIT=0

### Gate 020 — divergent-fixture reject proof

Temp config pointed at `fixtures/divergent-machine.json`:

    SHAPE-COURT: FAIL — 1 subject(s)
    VIOLATION divergent-machine.json [setup-seam] required seam not found
    EXIT=1

REJECT confirmed (exit 1) on a live gate. Non-vacuity: the court flips —
PASS on the srve subject (exit 0) and FAIL on the divergent fixture (exit 1)
in the same session with the same script.

### construct_gate (tool self-describe)

    python3 tools/construct_gate.py --help  -> usage + options, EXIT=0

The construct court itself needs a real `.ts` machine + xstate resolve path;
not exercised against the JSON fixtures (see Open Items).

## 3. srve provenance

Source corpus: `srve/docs/diagrams/state/xstate/SHAPES.md` (court-wave
receipts cited inline by wave id: w33-D2, w38, w45F, w51F, w57, w69-w93,
w106, w149). Baselines: srve J14 (`scripts/ttl_court.py` BASELINES dict,
v26.11.7 conformance-maintenance plan). Registered 020 subject: srve
`wo-visits.machine.ts` (clean census 2026-11-07). The pack is the
marketplace projection of srve v26.11.7 machine-court capital.

## 4. Seal checklist vs the M1/M5 standard

| checklist item | status |
|---|---|
| pack.toml manifest with capabilities | PASS |
| ontology + pack-scoped vocabulary (xs5:) | PASS |
| M15 cross-pack alignment (st: seeAlso, qualification identity) | PASS |
| templates (machine/smoke/conformance-matrix) | PASS |
| runnable gates with configs | PASS (010, 020) |
| positive fixture present | PASS |
| divergent fixture + violation map | PASS |
| gate positive PASS run receipted | PASS (010, 020) |
| gate divergent REJECT run receipted | PARTIAL (020 only, real run) |
| construct gate exercised on real machine | BLOCKED (needs .ts + xstate) |
| gates 030_conformance / 040_smoke_run | MISSING (named in fixture map) |
| cross-repo pilot (non-source-repo consumer) | PENDING |

## 5. Open items (honest)

1. **030/040 gates absent.** `divergent-notes.md` maps V-DIV-1/2/3 to
   `030_conformance` and `040_smoke_run`; no such files exist under
   `gates/`. The divergent fixture's expected_gates block names five gates;
   only 010 and 020 are runnable today.
2. **Positive JSON fixture fails 020's setup-seam arm.** Real run: the
   positive fixture exits 1 (`[setup-seam] required seam not found`) —
   020's default required-seam regex is TS-shaped (`setup\s*\(`) and the
   fixture is JSON. The divergent fixture's rejection is genuine but rides
   the same arm, so 020's JSON-mode verdict is not yet discriminating.
   Fix: JSON-mode seam check on the `"setup"` key, or a `.ts` positive
   fixture.
3. **construct_gate unexercised.** Requires a real `.ts` machine and a
   resolvable xstate dependency; the pack ships no `.ts` fixture, so the
   w149 construction-proof law is unproven inside the pack itself.
4. **010 divergent path not directly runnable.** baselines.toml pins srve
   TTL graphs; the JSON fixture is not in its scan set, so the V-DIV-5
   010-reject mechanism is asserted by the notes, not witnessed here.
5. **Cross-repo pilot pending.** Standing stays PARTIAL_ALIVE until one
   non-source-repo consumer machine passes the SHAPES.md gate checklist
   end to end (SHAPES.md Pending Pilots, slot 1 open).

## 6. Receipt

- Subject: `packs/xstate-v5-machine-pack` @ HEAD (files stamped 2026-11-07
  22:39-22:40, uncommitted at receipt time; lane S5 owns only this file).
- Commands: gate runs quoted verbatim in section 2; exits 0/0/1/0/0 as
  shown.
- Verification ladder: census (disk) -> gate 010 positive (exit 0) ->
  gate 020 positive (exit 0) -> gate 020 divergent (exit 1) -> tool
  self-describe (exit 0).
- Standing: PARTIAL_ALIVE (inherited from SHAPES.md; gates 010/020 PASS on
  srve with real output; divergent reject witnessed on 020 only).
