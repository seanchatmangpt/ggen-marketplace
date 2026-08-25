# Tutorial

Feed captured exact-subject observations from `github-live-evidence-ingestion-pack` into this pack's offline evaluators. Use `runtime/drift.py` to distinguish CURRENT, CONTAINED_AFTER_DRIFT, and DRIFT_UNCONTAINED. Use `runtime/latency.py` over discovery/realization timestamps. Use `runtime/ledger_refresh.py` to manufacture an append-only realization fact after a merge receipt exists. None of these steps capture data or actuate GitHub.
