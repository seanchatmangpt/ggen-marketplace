# trade-reticle-plumbing validation receipt (Lane A12, 2026-11-07)

Standing: PASS

## Scope
Pack: `packs/trade-reticle-plumbing/` in ggen-marketplace. All real exits,
run 2026-11-07 in `/Users/sac/ggen-marketplace`.

## Gate chain (real exits)

| gate | command (cwd) | exit |
|---|---|---|
| ggen sync | `ggen sync run --skip-ea-admission` (pack dir) | 0 (generated module unchanged, content identical) |
| pack verifier | `python3 verify.py` (pack dir) | 0 (3 gates 0 rows; anti-vacuity flip 2 rows; generated spot-check 5/5; elixir-eval 4/4) |
| marketplace validate | `python3 scripts/marketplace.py validate` (repo root) | 0 — 353 packs, 353 manifests, 585 ontologies, 1980 templates, 2044 native gates, 0 refusals for this pack |
| SHACL author-time court | `ggen law validate --format json` (scratch manifest `/tmp/a12-shacl/ggen.toml` pointing at pack ontology.ttl + shapes.ttl) | 0 — `{"conforms":true,"denials":0,"derived":0,"rules_loaded":0,"shapes_checked":1}` |

## SHACL compile status

`shapes.ttl` compiles clean under `ggen law validate` (conforms true,
shapes_checked 1, exit 0) via an author-time scratch manifest. Two wiring
facts witnessed:

- Wiring `validation.shacl` into the pack's own `ggen.toml` makes
  `ggen sync run` fail closed with `[FM-LAW-017]` (SHACL sync gates were
  replaced by SPARQL gate queries). The pack manifest therefore stays
  SPARQL-gates-only; SHACL is author-time tooling, per the ggen source
  (`crates/ggen-engine/src/config.rs`: shapes are "legacy, refused at sync
  time... `ggen law validate` (author-time tooling) still reads it").
- First wiring attempt caught a real defect: `tr:claim-drain-001` (positive
  control instance, carries `providedTelemetry`) is typed
  `tr:DiagnosticTree`, and `ClaimShape` demands `tr:requiredTelemetry`
  minCount 1 on every DiagnosticTree -> FM-LAW-013 minCount violation.
  Fix (within pack): added the claim type's three `tr:requiredTelemetry`
  triples to `tr:claim-drain-001` in `ontology.ttl`. Gates re-verified green
  after the fix (verify.py exit 0; sync exit 0; SHACL conforms true).

## 12-verdict matrix (all typed, real elixir eval)

Generated module compiled alongside
`~/ash_a2a/lib/ash_a2a/twin/vince.ex` (X2 landed); `@behaviour
AshA2A.Twin.MechanicalPrior` compiles clean; callback census
`behaviour_info(:callbacks)` = `[prior_verdict: 2]`, exported true.

Callback contract (vince.ex:185-188): `prior_verdict(claim :: term(),
telemetry :: term()) :: {:admit, map()} | {:challenge, evidence ::
[String.t()], msg :: String.t()} | {:refuse, reason :: term()}` — generated
module matches exactly (admit carries a map with claim_type/telemetry/prior;
challenge carries the exact missing-field list + demand string; refuse
carries a term).

Script: `/tmp/a12-shacl/matrix.exs`, exit 0. Matrix (4 claim types x
{complete, partial, unknown}):

| claim type | complete | partial | unknown telemetry |
|---|---|---|---|
| drain_line_replacement | admit (claim_type, telemetry, prior) | challenge, missing exactly `camera_inspection_footage_id` | challenge, all 3 required fields listed |
| water_heater_failure | admit | challenge, missing exactly `unit_age_years` | challenge, all 3 listed |
| grease_trap_overflow | admit | challenge, missing exactly `trap_capacity_gallons` | challenge, all 3 listed |
| sewer_main_backup | admit | challenge, missing exactly the first required field | challenge, all 3 listed |

Extra typed refusal: `prior_verdict("no_such_trade", %{})` ->
`{:refuse, {:unknown_claim_type, "no_such_trade"}}`. Closed refusal
vocabulary: `[:REFUSED_UNKNOWN_CLAIM_TYPE, :REFUSED_MISSING_TELEMETRY,
:REFUSED_NO_PRIOR]`.

The ungrounded-claim case (telemetry demanded but not supplied in the
fixture) is flagged by `prior_verdict/2` as a typed challenge naming the
exact missing field (witnessed for all 4 types).

## Connect-to-workflow check

`AshA2A.Twin.MechanicalPrior` behaviour source read on disk
(`~/ash_a2a/lib/ash_a2a/twin/vince.ex:175-189`); generated module compiles
against it in the same VM with zero warnings, `@behaviour` satisfied, and
verdict shapes match the `@callback` spec term-for-term. Vince integration
point: `AshA2A.Twin.Vince.check_claim/3` delegates to
`prior.prior_verdict(claim, telemetry)` (vince.ex:120-121).

## Files changed (lane A12 only)

- `packs/trade-reticle-plumbing/ontology.ttl` — added 3 `tr:requiredTelemetry`
  triples to `tr:claim-drain-001` (fixes the SHACL minCount violation; gates
  re-verified green post-fix).
- `packs/trade-reticle-plumbing/ggen.toml` — net zero: `validation.shacl`
  was added then removed after witnessing FM-LAW-017 (sync refuses SHACL
  wiring); file back at pre-lane content.
- `receipts/trade-reticle-validation-2026-11-07.md` — this receipt (new).

## Standing

PASS — all gates real-exit-0 post-fix; SHACL court conforms; 12/12 typed
verdicts; behaviour contract matched; no reds remaining.
