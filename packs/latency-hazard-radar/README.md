# latency-hazard-radar

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Response-latency hazard radar: robust median (tilde-mu) and MAD (median
absolute deviation) estimation over an observation window; hazard Z-score
`Z = (t_elapsed - median) / MAD`; typed `:insufficient_dispersion` outcome on
MAD = 0; hazard threshold (default 2.5); triage-prompt event on trip —
projected from RDF to an Elixir module. Requires no other pack.

## Capability surface

```bash
$ ggen pack capabilities latency-hazard-radar
```

Generated module: `generated/hazard_radar.ex` — `LatencyHazard.HazardRadar`
with `observe/3`, `zscore/2`, `trip?/2`, `median/1`, `mad/1`.

## Verification

```bash
ggen sync run ggen.toml          # codegen (regenerates generated/)
ggen validate ggen.toml          # gates 010/020/030
elixir spot_check.exs            # median/MAD/Z arithmetic on the pinned window
```

Spot check math (pinned window, from ontology.ttl):
window `[95, 98, 100, 105, 110, 120, 400]` -> median 105, MAD 7, and
`t_elapsed = 400` gives `Z = (400 - 105) / 7 = 42.14` -> trip;
`t_elapsed = 120` gives `Z = 2.14` -> no trip;
flat window `[50, 50, 50]` -> `{:error, :insufficient_dispersion}`.

## Falsifier (anti-vacuity)

- Gate 020: rename `lhr:refusalAtom` in ontology.ttl -> gate returns a row
  (must fail).
- Gate 030: delete `lhr:hazardThreshold` -> gate returns a row (must fail).
- Gate 010: edit a median/MAD witness value away from the arithmetic of the
  declared window -> gate returns a row (must fail).
- Rendered-module court: `zscore/2` on the flat window must return
  `{:error, :insufficient_dispersion}` — any other value fails.

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only.
The generated module is not exercised on any runtime by marketplace CI;
standing is scoped to qualification + spot check, not production actuation.

## See Also

- [Pack contract](../../docs/reference/pack-contract.md)
- [Pack classes](../../docs/reference/pack-classes.md)
