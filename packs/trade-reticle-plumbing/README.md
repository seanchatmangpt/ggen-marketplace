# trade-reticle-plumbing

First Mechanical Prior trade reticle pack (Capability-2): formalizes Vince's
trade skepticism for commercial plumbing.

Semantic source: `ontology.ttl` (tr: urn:trade:reticle:plumbing:) — four
DiagnosticTree claim types (`drain_line_replacement`, `sewer_main_backup`,
`water_heater_failure`, `grease_trap_overflow`), each with required telemetry,
physical priors (pipe-material lifetimes, failure modes, USD part-cost
baselines), counter-punch evidence demands, and a closed refusal vocabulary
minted as individuals (`REFUSED_UNKNOWN_CLAIM_TYPE`, `REFUSED_MISSING_TELEMETRY`,
`REFUSED_NO_PRIOR`).

## Structure

- `pack.toml` / `ggen.toml` — identity + pack-local self-verification manifest
- `ontology.ttl` — semantic authority (4 claim-type tables, 4 pipe-material
  priors, 4 cost baselines, one positive-control claim instance
  `claim-drain-001` providing complete telemetry)
- `shapes.ttl` — SHACL structural contract complementing the SPARQL gates
- `queries/claims.rq` — SELECT bindings (one row per claim type) for the template
- `templates/trade_reticle_plumbing.ex.tmpl` — generates `TradeReticle.Plumbing`
  implementing the `AshA2A.Twin.MechanicalPrior` behaviour: `prior_verdict/2`
  (unknown claim type -> typed refuse; missing telemetry -> challenge with the
  exact missing-field list; complete telemetry -> admit)
- `gates/*.rq` — SELECT rows = violation: claim-table completeness, prior
  sanity (lifetime range, cost min<=max), and the telemetry coverage law
- `verify.py` — Chicago verifier: runs all gates, then an anti-vacuity court
  (deletes `camera_inspection_footage_id` from the positive control and PROVES
  gate 030 flips; a gate that cannot flip = VACUOUS GATE, exit 1), then
  spot-checks the generated module including a real `elixir` evaluation of
  `prior_verdict/2`: complete telemetry admits, partial telemetry challenges
  demanding exactly `camera_inspection_footage_id`, unknown claim type refuses
  typed (behaviour source compiled from `~/ash_a2a/lib/ash_a2a/twin/vince.ex`
  when present, else the documented contract)
- `generated/trade_reticle_plumbing.ex` — generated consequence, never hand-edited

## Usage

Pack-local self-verification:

```bash
ggen sync run --skip-ea-admission
python3 verify.py
```

Consumers copy `ggen.toml` into their own project, bind their own claim-type
individuals in their ontology, and sync. Wire the module into Vince:

```elixir
AshA2A.Twin.Vince.new(prior: TradeReticle.Plumbing)
```

## Verification

Last run: all gates 0 rows, anti-vacuity flip PASS, elixir-eval
admit/challenge(camera_inspection_footage_id)/refuse(unknown_claim_type) PASS,
marketplace validate 0 refusals.
