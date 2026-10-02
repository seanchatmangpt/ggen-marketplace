# Family: maximalist-selection-control

> Absorbed from `dfcm-maximalist-selection-control-pack` (v2.2.0 consolidation, 2026-10-01). Synthesized note —
> the satellite shipped no README; content recovered from its manifest, structure, and
> courts. Namespace moved verbatim to `ontology/maximalist-selection-control.ttl` (no IRI changed); gates live
> family-prefixed in `../../gates/`; algorithms preserved verbatim below this directory.
> Superseded with absorption: the satellite's `pack.toml` (this pack is the one admission
> unit) and its `ggen.toml` generation wiring (queries/templates preserved as modules,
> not re-wired — they predate strict-mode ORDER BY and stay verbatim).

Bounded multi-winner SELECT control (compatibility, CTQ, evidence, rollback,
decisive-experiment, receipt, replay law). Algorithms preserved: `scripts/selector.py`
(pareto/maximin/information_gain), `scripts/receipt.py` (issue/replay with typed refusals);
courts in `tests/`. Merged gates: `dmsc_010_exact_subject`, `dmsc_020_authority`,
`dmsc_030_evidence_bounds` (ASK→violation-row conversions). Registered projection
`dfcm:SelectionControlProjection`; dms: terms are owl:equivalentProperty-mapped in
`ontology/option-capital.ttl`.
