# Semantic Gate Witness Court Pack

Reusable GGen manufacturing capital for turning a directory of semantic gates into an explicit, replayable qualification court.

## Consumer contract

A consumer owns its semantic gates and witnesses. The court owns the reusable correspondence law:

- `gates/<case>.rq` or `.sparql` is an admitted semantic gate.
- `witnesses/pass/<case>.<ext>` is a positive witness that must be accepted by that gate.
- `witnesses/fail/<case>.<ext>` is a negative witness that must be refused when `require_fail = true`.
- `gate-court.toml` declares directories, extensions, and whether pass/fail coverage is required.
- case identity is exact filename stem; missing and orphan witnesses fail closed.
- the court emits deterministic JSON with SHA-256 identities for gates and executed witnesses.
- an optional runner delegates gate semantics without coupling the pack to a SPARQL engine; it is invoked without a shell and must return zero only when the requested expectation is observed.

Minimal consumer configuration:

```toml
[court]
schema = "ggen.semantic-gate-witness-court/1"
case_key = "exact-stem"
gate_dir = "gates"
pass_dir = "witnesses/pass"
fail_dir = "witnesses/fail"
require_pass = true
require_fail = false
```

The generated court can be run structurally with `python3 generated/semantic_gate_witness_court.py <pack-root>` or semantically with `--runner '... {gate} {witness} {expectation} ...'` once a consumer supplies its engine-specific adapter.
