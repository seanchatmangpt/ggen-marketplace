# tokyo-depeg-burn-in-pack

Manufactures the Tokyo flash-depeg Chicago burn-in as data. One `tdb:` ontology
carries the 6 protocol stages, the required trade lifecycle
(RiskPreflight -> CollateralCheck -> SanctionsScreen -> Execution) as a Petri
net, effect-identity invariants (BLAKE3 over the JCS-canonical payload, one
effect_instance_id per accepted mutation), typed refusal classes (scenario-level `REFUSED_*` rows plus consumer-grounded rows
carrying `tdb:emittedAtom` naming the exact atom ash_pplan emits; each
carrying a receipt subject), the four-participant settlement set, one
`tdb:BurnCycle` row (cycles/concurrency/kill policy), and `tdb:Surface` rows
for the read-only burn-in dashboard (projected by ash_surface; zero actuation
authority in the client).

## Layout

- `gates/` -- 10 violation-polarity gates, one per ontology family (zero rows =
  pass; any row = a named contract violation). Complete PREFIX header, ORDER BY
  on projected variables, no positional filter args. Each gate carries an
  `empty-*-family` anti-vacuity branch so a fully-deleted ontology family is a
  refusal, never a vacuous pass. (These were originally completeness
  projections under the ggen_igniter gate polarity, which is the inverse of
  the ggen 26.9.28 marketplace loader polarity; rewritten to the loader
  contract.)
- `verify/` -- one `*.unbound.rq` inverted companion per gate (ZERO ROWS is the
  pass condition): the completeness census — deleting any required ontology
  row makes its companion fire with the named missing property.
- `templates/` -- 4 EEx templates with `to:`/`for_each:` frontmatter:
  - `corpus.ex.tmpl` -> `AshPPlan.Test.TokyoDepeg.Corpus`
  - `alignment_spec.exs.tmpl` -> required lifecycle as data (the Van der Aalst
    conformance model)
  - `stage_handler.ex.tmpl` -> one handler per stage (`for_each: stages`)
  - `burn_in_runner.ex.tmpl` -> `bin/tokyo-burn-in`
- `pack.toml`, `README.md`.

## Verify (fail-closed)

    python3 scripts/qualify_packs.py --pack tokyo-depeg-burn-in-pack --report /tmp/tdb-qual.json

runs the marketplace court: ggen 26.9.28 sync (gates at violation polarity)
plus real template rendering. The `verify/*.unbound.rq` companions remain the
fail-closed completeness census for the ggen_igniter consumer (`mix
ggen_igniter.verify --pack-dir` runs them alongside the gates; note the
ggen_igniter gate polarity is the inverse, so the gates' pass condition there
is the companions' concern — the companions are the deletion detectors).

## Render

    MIX_BUILD_ROOT=_build-tdb-pack mix ggen_igniter.sync --pack-dir packs/tokyo-depeg-burn-in-pack \
      --template templates/<stem>.exs.tmpl --out <out-path>

(byte-identical on second render; see `pack.toml`'s description for the
measured run.)

## Consumption

Consumed by `~/ash_pplan` via ggen_igniter (W2 of the flash-depeg plan):
rendered `lib/ash_pplan/tokyo_depeg/*.ex` and `bin/tokyo-burn-in` carry
GENERATED headers; hand-written residue only in `test/tokyo_depeg/`.
