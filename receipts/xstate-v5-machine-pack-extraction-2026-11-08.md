# Lane Receipt M10: xstate-v5-machine-pack Extraction

Standing: PARTIAL_ALIVE

Wave M lane M10, 2026-11-08. Repo: /Users/sac/ggen-marketplace. Lane owns
exactly one file (this receipt); pack files verified read-only.

## Provenance

Extracted from the srve machine-court wave (v26.11.7 conformance-maintenance
plan, srve `docs/diagrams/state/xstate/SHAPES.md`). The pack is the
marketplace projection of srve's 19-machine court capital: SHAPES.md laws,
ttl_court.py baselines (srve J14), conformance matrix, construct gate.
Provenance section of the pack seal receipt cites the same corpus inline
(w33-D2, w38, w45F, w51F, w57, w69-w93, w106, w149).

## Contents census (verified on disk 2026-11-08)

26 authored files under `packs/xstate-v5-machine-pack/` (excluding the
`tools/render_test/target/` release-build dir, disclosed below):

- manifest/ontology/qualification: pack.toml, ontology.ttl, consumer.ttl (3)
- docs: README.md, docs/SHAPES.md (2)
- fixtures: positive-machine.json/.ts, divergent-machine.json/.ts,
  divergent-notes.md (5)
- gates: 010_ttl_triple_counts.py, 020_compile_shape_scan.py,
  030_conformance.py, 040_smoke_run.sh, baselines.toml, shapes.toml (6)
- templates: machine, smoke, conformance-matrix .tera.tmpl (3)
- tools: construct_gate.py; render_test crate (Cargo.toml, Cargo.lock,
  src/main.rs, test_vars.json, RECEIPT.md) (6)
- seal receipt: _XSTATE_V5_MACHINE_PACK_RECEIPT.md (1)

The dispatch figure of 17 corresponds to the at-seal census (pack.toml,
ontology, 3 templates, 2 gates + 2 configs, construct_gate, 3 fixtures,
consumer.ttl, README, SHAPES.md); post-seal lanes added gates 030/040,
the render_test crate, and the .ts fixtures since.

## Gate outputs (cited from srve render-court-receipt.md)

Evidence sections in
`/Users/sac/srve/docs/diagrams/state/render-court-receipt.md`:
"## R-S5b" work is witnessed across sections R192b (line 3290) and
R192c (line 3254); cited sections are in srve's receipt, not this repo.

- R192b (line 3290): clean census, zero collisions; gate 010 vs baselines
  PASS exit 0 (finance 280, routes-forms 297, procurement 135, authz 87,
  4/4 terms); gate 020 pass fixture PASS exit 0.
- R192c (line 3254): construct_gate positive
  (srve wo-visits.machine.ts -> `woVisitsMachine OK`) and broken-machine
  FAIL both witnessed on real xstate 5 + esbuild; court flips both ways.
- render_test court (pack RECEIPT.md, Standing PASS): both templates
  render exit 0; rendered output passes construct_gate 1/1; 4 template
  defects found and fixed (context `: ` separator, action param
  order/separator, createActor actors-in-options, duplicate import).

## Fresh run this session (M10, real output)

    python3 gates/030_conformance.py fixtures/positive-machine.json
    CONFORMANCE-COURT: PASS — 0 violations (RC=0)
    python3 gates/030_conformance.py fixtures/divergent-machine.json
    4 violations (V-DIV-1, V-DIV-2 x2, V-DIV-3) — FAIL (RC=1)

Gate 030 flips both ways on real fixtures; closes the three V-DIV rows the
seal receipt listed as lacking runnable rejectors.

## Seal checklist status (vs pack seal receipt section 4)

- 010/020 positive PASS + 020 divergent REJECT: receipted at seal (exits
  0/0/1/0/0).
- construct gate exercised: BLOCKED at seal, later witnessed by R192c
  (real xstate 5, esbuild) and render_test court — PASS.
- gates 030/040: exist now (030 witnessed both ways this session; 040 is
  an exit-code wrapper around the consumer project's vitest run — court is
  the real test run, not the script).
- divergent coverage: 030 rejects V-DIV-1/2/3; 020's divergent reject
  rides the setup-seam arm. 3 of 5 divergent violations lacked rejectors
  at seal — disclosed honestly there; 030 closes V-DIV-1/2/3, V-DIV-4/5
  remain notes-asserted, not rejector-witnessed.

## Open items (honest)

1. Registration: no registry/ggen.toml reference to the pack found in a
   repo-wide sweep this session — registration pending M9 (concurrent);
   marked UNVERIFIED-pending, not confirmed.
2. V-DIV-4/5 rejectors still unwitnessed (notes assert, no gate run
   rejects on them). 020's JSON-fixture reject is seam-arm riding per
   R192b's FAIL-TO-FLIP finding.
3. Cross-repo pilot (non-source-repo consumer) pending — the standing
   condition on SHAPES.md and the seal receipt; slot 1 open.
4. `tools/render_test/target/` release-build dir (~build artifacts) sits
   inside the pack dir — lease-class cleanup item for the coordinator;
   Cargo.lock is a normal crate lock, keep.
5. Positive JSON fixture fails 020's TS-shaped setup-seam arm (seal open
   item 2) — unresolved.
