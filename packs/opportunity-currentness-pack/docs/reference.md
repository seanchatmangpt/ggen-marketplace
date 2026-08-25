# Reference

`drift.py` accepts `qualified_head`, `default_head`, and `contained_heads`; all heads are exact 40-hex SHAs. `latency.py` accepts an array of records with ISO-8601 `discovered_at` and optional `realized_at`. `ledger_refresh.py` accepts `opportunity`, `.jsonl` `source_ledger`, `capability_head`, and `merge_sha`.

Typed refusals include `REFUSED[INEXACT_HEAD]`, `REFUSED[INVALID_CONTAINMENT_SET]`, `REFUSED[INVALID_TIMESTAMP]`, `REFUSED[NEGATIVE_REALIZATION_LATENCY]`, `REFUSED[INVALID_OPPORTUNITY]`, and `REFUSED[INVALID_SOURCE_LEDGER]`.

HANDWRITTEN_IRREDUCIBLE_REASON: timestamp arithmetic, distribution calculation, exact-SHA validation, canonical digest computation, and deterministic runtime grouping/evaluation are executable algorithm substrate rather than static ontology projection.
