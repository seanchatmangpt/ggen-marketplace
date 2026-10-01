# chicago-graphlaw-court-pack

Generates Chicago-style (real collaborators, no mocks) GraphLaw ABI court test files from an RDF
case ontology. One `#[test]` per case, each driving `graphlaw::abi::call` and asserting on the
final response.

Standing: UNVERIFIED. No committed run shows the corpus passing. A run on 2026-09-30 of
`verify/validate.sh witnesses` returned `WITNESSES_OK (0 bad)`, but `verify/validate.sh corpus` was
`REFUSED (3 problems)`: gate `130_compare_pairs_with_request_b` reported a violation, the SHACL check
was NONCONFORMANT (117 results), and `cases/*.ttl` carried a JSON request error (`step lacks op`).
Authority NONE; synthetic subject; no general financial safety claim. The 10M threshold
(`10000000000000` micros) is Chicago court policy, not FIBO's.

## Layout

| Path | Owner | Role |
|---|---|---|
| `ontology.ttl` | lane P | `cc:` vocabulary and the two court individuals |
| `shapes.ttl` | lane P | SHACL shapes (court, fibo threshold, case, axiom) |
| `cases/a.ttl`, `cases/b.ttl` | lanes A, B | cross-authority cases (ordinals 1-499), FIBO cases (500-999) |
| `queries/cases_xauth.rq`, `queries/cases_fibo.rq` | lane P | one row per case, per court |
| `templates/chicago_court.rs.tmpl` | lane P | the court test file |
| `gates/*.rq` | lane P | SPARQL ASK gates, true = violation |
| `witnesses/{pass,fail}/` | lane P | one pass and one fail graph per gate |
| `consumer/ggen.toml` | lane P | install as `<graphlaw>/ggen.toml`; writes `tests/chicago_*.rs` |
| `ggen.toml` | lane P | pack-local self-check; writes `generated/tests/` |
| `verify/validate.sh` | lane P | gates + SHACL + JSON-literal check |

## Case grammar

`cc:request` / `cc:requestB` are JSON: one ABI request object, or an array (a chain). In a chain,
a string equal to `"$PREV:/ptr"` is replaced by that RFC 6901 pointer into the previous response.
A string equal to `"$FILE:rel/path"` is read from `CARGO_MANIFEST_DIR` at test time.
`cc:expect` is a JSON array of assertions over the last response: `{"ptr","eq"}`,
`{"ptr","contains"}`, `{"ptr","len"}`, `{"ptr","absent":true}`. `cc:compare` is an array of
`{"a","rel":"eq|neq","b"}` over responses A and B. `cc:byteIdentity true` (single request only)
also asserts native and wasm raw responses are byte-identical.

Kinds: positive, negative, invariance, cross-authority, boundary-mutation. Each court needs all
five (gate 090). A boundary-mutation case names `cc:mutates` its base and must expect something
different from it (gate 100).

## Use

```sh
verify/validate.sh witnesses          # each gate: pass witness clean, fail witness violates
verify/validate.sh corpus             # gates + SHACL + JSON over ontology + cases/*.ttl
cp consumer/ggen.toml ../../../graphlaw/ggen.toml && (cd ../../../graphlaw && ggen sync run)
```

Needs `python3` with `rdflib` and `pyshacl`. ggen does not enforce imported shapes, so SHACL is a
separate step. The generated court files are never hand-edited.

## UNSUPPORTED

- `generated-oversize-payload`: request_bytes / json_depth caps cannot be expressed as cases.
- `generator-capability: plan-api`: Rust `Plan` / `LawState` API calls are not ABI requests.
- Ceiling on a case is documentation only; the generated test does not enforce it.
