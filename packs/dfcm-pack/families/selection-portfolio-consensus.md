# Family: selection-portfolio-consensus

> Absorbed from `dfcm-selection-portfolio-consensus-pack` (v2.2.0 consolidation, 2026-10-01). Synthesized note —
> the satellite shipped no README; content recovered from its manifest, structure, and
> courts. Namespace moved verbatim to `ontology/selection-portfolio-consensus.ttl` (no IRI changed); gates live
> family-prefixed in `../../gates/`; algorithms preserved verbatim below this directory.
> Superseded with absorption: the satellite's `pack.toml` (this pack is the one admission
> unit) and its `ggen.toml` generation wiring (queries/templates preserved as modules,
> not re-wired — they predate strict-mode ORDER BY and stay verbatim).

Compatibility-aware multi-winner portfolio manufacture with deterministic consensus,
information gain, receipt and replay. Namespace `dspc:`. Algorithms preserved:
`scripts/{models,compatibility,portfolio,consensus,receipt,replay}.py`; court in
`tests/test_portfolio_consensus.py`. Merged gates: `dspc_010_exact_subject`,
`dspc_020_no_ambient_do`.
