# Governed runtime evidence matrix

This directory composes `governed-runtime-adapter-pack` with `semantic-gate-witness-court-pack`.

For every `gates/<case>.rq`, a same-case `witnesses/pass/<case>.ttl` proves the admitted proposition can clear the gate. Authority-sensitive gates additionally require `witnesses/fail/<case>.ttl` proving the court detects the forbidden state. Missing or orphan witnesses are refusal conditions delegated to the reusable witness court.

Consumers supply framework-specific RDF mappings; they do not copy the court implementation. Runtime execution remains fenced by the adapter contract and process-intelligence algorithms remain owned by `wasm4pm/wasm4pm-compat`.
