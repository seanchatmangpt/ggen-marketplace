# Family: selection-frontier-execution

> Absorbed from `dfcm-selection-frontier-execution-pack` (v2.2.0 consolidation, 2026-10-01). Synthesized note —
> the satellite shipped no README; content recovered from its manifest, structure, and
> courts. Namespace moved verbatim to `ontology/selection-frontier-execution.ttl` (no IRI changed); gates live
> family-prefixed in `../../gates/`; algorithms preserved verbatim below this directory.
> Superseded with absorption: the satellite's `pack.toml` (this pack is the one admission
> unit) and its `ggen.toml` generation wiring (queries/templates preserved as modules,
> not re-wired — they predate strict-mode ORDER BY and stay verbatim).

Deterministic reversible SELECT frontier execution with bounded evidence and authority.
Namespace `sfe:`. Algorithms preserved: `scripts/selector.py`, `scripts/uncertainty.py`
(INSUFFICIENT_SELECTION_EVIDENCE refusals), `scripts/receipt.py`, `scripts/replay.py`
(TAMPER refusals); courts in `tests/`. Merged gates: `dsfe_authority`,
`dsfe_exact_subject`, `dsfe_frontier_evidence`. The satellite's project-qualification
overlay ontology is preserved as `qualification-project-ontology.ttl`; the SelectionRun
policy exemplar was relocated to `fixtures/selection_run.ttl` (see README deviation 5).
