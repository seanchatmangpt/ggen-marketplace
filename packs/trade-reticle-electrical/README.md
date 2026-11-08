# trade-reticle-electrical

High-voltage electrical & switchgear Mechanical Prior trade reticle pack
(multi-trade expansion, lane Z14): formalizes Vince's trade skepticism for
commercial electrical claims.

Semantic source: `ontology.ttl` (el: urn:trade:reticle:electrical:) — four
DiagnosticTree claim types (`main_breaker_replacement`,
`switchgear_trip_investigation`, `transformer_failure`, `motor_circuit_fault`),
each with the 4-field required telemetry set (`resistance_readings_log`,
`voltage_log`, `thermal_image_id`, `breaker_serial_photo`), physical priors
(equipment lifetimes 15-35 years, ambient-temperature trip curves as textual
derate ranges, USD part-cost baselines), counter-punch evidence demands (the
Vince diagnostic counter-punch pattern: main-breaker claims demand voltage +
resistance logs BEFORE authorization; motor-failure claims at high ambient
demand capacitor bank check evidence FIRST), and a closed refusal vocabulary
minted as individuals (`REFUSED_UNKNOWN_CLAIM_TYPE`,
`REFUSED_MISSING_TELEMETRY`, `REFUSED_NO_PRIOR`).

## Structure

- `pack.toml` / `ggen.toml` — identity + pack-local self-verification manifest
- `ontology.ttl` — semantic authority (4 claim-type tables, 4 equipment priors,
  4 cost baselines, one positive-control claim instance `claim-mb-001`
  providing the complete 4-field telemetry set)
- `shapes.ttl` — SHACL structural contract complementing the SPARQL gates
- `queries/claims.rq` — SELECT bindings (one row per claim type) for the
  template, including the ambient trip curve
- `templates/trade_reticle_electrical.ex.tmpl` — generates
  `TradeReticle.Electrical` implementing the `AshA2A.Twin.MechanicalPrior`
  behaviour: `prior_verdict/2` (unknown claim type -> typed refuse; missing
  telemetry -> challenge with the exact missing-field list; complete telemetry
  -> admit)
- `gates/*.rq` — SELECT rows = violation: claim-table completeness, prior
  sanity (lifetime range, cost min<=max), and the telemetry coverage law
- `verify.py` — Chicago verifier: runs all gates, then an anti-vacuity court
  (deletes `voltage_log` from the positive control and PROVES gate 030 flips;
  a gate that cannot flip = VACUOUS GATE, exit 1), then drives the generated
  module through the 12-verdict matrix on a real `elixir` runtime: 4 claims x
  {complete -> admit, partial -> challenge demanding exactly
  `breaker_serial_photo`, unknown claim type -> typed refuse} (behaviour
  source compiled from `~/ash_a2a/lib/ash_a2a/twin/vince.ex` when present,
  else the documented contract)
- `generated/trade_reticle_electrical.ex` — generated consequence, never hand-edited
- `qualification/fixtures/` — expected-verdict pins for the headline hostile path

## Usage

Pack-local self-verification:

```
ggen sync run --skip-ea-admission   # regenerate generated/ from ontology.ttl
python3 verify.py                   # gates + anti-vacuity court + 12-verdict matrix
```

Consumers copy `ggen.toml` into their own project, point `el:` at their own
claim individuals, and sync.
