# Family: selection-evidence-acquisition

> Absorbed from `dfcm-selection-evidence-acquisition-pack` (v2.2.0 consolidation, 2026-10-01). Synthesized note —
> the satellite shipped no README; content recovered from its manifest, structure, and
> courts. Namespace moved verbatim to `ontology/selection-evidence-acquisition.ttl` (no IRI changed); gates live
> family-prefixed in `../../gates/`; algorithms preserved verbatim below this directory.
> Superseded with absorption: the satellite's `pack.toml` (this pack is the one admission
> unit) and its `ggen.toml` generation wiring (queries/templates preserved as modules,
> not re-wired — they predate strict-mode ORDER BY and stay verbatim).

Decisive evidence acquisition for sparse frontiers without collapsing reversible
alternatives. Namespace `dea:`. Algorithms preserved: `scripts/acquisition.py` (typed
`Refused` on non-decisive experiments), `scripts/scoring.py`, `scripts/receipt.py`
(tamper-refusing replay); courts in `tests/` (acquisition, no-ambient-DO source scan,
replay). Merged gates: `dsea_01_exact_candidate_subject`, `dsea_02_evidence_gap`,
`dsea_03_no_ambient_do` — the first two were positive-existence ASKs, converted to
per-individual violation form (conversion semantics recorded in the gate files).
