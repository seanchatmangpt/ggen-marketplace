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

- `gates/` -- 10 conjunctive `SELECT DISTINCT` gates (complete PREFIX, ORDER BY
  on a projected variable, no positional filter args; the 26.9.28-class parser
  traps), one per ontology family.
- `verify/` -- one `*.unbound.rq` inverted companion per gate (ZERO ROWS is the
  pass condition) plus `cardinality.json` (every contract predicate-anchored,
  so contract + companion have disjoint blind spots).
- `templates/` -- 4 EEx templates with `to:`/`for_each:` frontmatter:
  - `corpus.ex.eex` -> `AshPPlan.Test.TokyoDepeg.Corpus`
  - `alignment_spec.exs.eex` -> required lifecycle as data (the Van der Aalst
    conformance model)
  - `stage_handler.ex.eex` -> one handler per stage (`for_each: stages`)
  - `burn_in_runner.ex.eex` -> `bin/tokyo-burn-in`
- `pack.toml`, `README.md`.

## Verify (fail-closed)

    MIX_BUILD_ROOT=_build-tdb-pack mix ggen_igniter.verify --pack-dir packs/tokyo-depeg-burn-in-pack

`mix ggen_igniter.verify` runs the gates plus the inverted companions plus the
per-gate cardinality contracts; deleting any required ontology row makes its
companion fire with the named missing property.

## Render

    MIX_BUILD_ROOT=_build-tdb-pack mix ggen_igniter.sync --pack-dir packs/tokyo-depeg-burn-in-pack \
      --template templates/<stem>.exs.eex --out <out-path>

(byte-identical on second render; see `pack.toml`'s description for the
measured run.)

## Consumption

Consumed by `~/ash_pplan` via ggen_igniter (W2 of the flash-depeg plan):
rendered `lib/ash_pplan/tokyo_depeg/*.ex` and `bin/tokyo-burn-in` carry
GENERATED headers; hand-written residue only in `test/tokyo_depeg/`.
