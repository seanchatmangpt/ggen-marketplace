# HANDWRITTEN.md — wasi-json-abi-pack ledger

Enumerable facts (module identity, export prefix, ABI version, limits, stack size,
imports policy, ops, error codes) live in `ontology.ttl` and consumer graphs; the
rendered projections are never hand-edited.

| path | kind | standing | reason |
|---|---|---|---|
| pack.toml, targets.toml, package.toml, ggen.toml | manifest | n/a (ggen-produced by definition) | pack admission and rule binding |
| ontology.ttl | ontology | n/a (ggen-produced by definition) | source graph |
| queries/*.rq | query | n/a (ggen-produced by definition) | SELECT projections over the ontology |
| templates/* | template | n/a (ggen-produced by definition) | render ontology facts |
| gates/*.rq, gate-court.toml | gate | n/a (ggen-produced by definition) | admission gates over consumer graphs |
| witnesses/{pass,fail}/*.ttl | witness | n/a (ggen-produced by definition) | gate court evidence |
| runners/semantic_runner.py | runner | n/a (copied verbatim) | gate court runner |
| consumer op bodies (request decoding, domain logic behind each wja:Op) | consumer code | UNSUPPORTED(generator-capability) | domain semantics of an op are not enumerable ontology facts; the consumer hand-writes them and the generated dispatch table names them |
| consumer host glue (native/WASI runners, build scripts, CI wiring) | consumer code | UNSUPPORTED(generator-capability) | host-side toolchain integration is outside the projection |
