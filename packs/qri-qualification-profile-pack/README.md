# qri-qualification-profile-pack

Qualified Runtime Interchangeability (QRI): a thin qualification, admission and substitution
profile over SOSA/SSN, PROV-O, ODRL, SPDX, QUDT and SHACL, projected by ggen to WIT, a core-WASM
JSON ABI adapter (Rust) and a wasmex BEAM host (Elixir). Authority ceiling NONE.

## Layout

- `ontology.ttl` core profile; `ontology/alignments.ttl` (2017 SOSA/SSN, PROV, ODRL, in-repo
  `qualified-capability-ecology-pack`); `ontology/alignment-sosa-2023.ttl` (not imported);
  `ontology/context.jsonld`; `ontology/examples/graphlaw-contract.ttl` (contract for the real
  graphlaw ABI).
- `shapes/qri.shacl.ttl` SHACL Core + SHACL-SPARQL admission.
- `gates/*.rq` six gates, each with same-stem `witnesses/{pass,fail}`.
- `queries/`, `templates/`, `ggen.toml`: projection rules (WIT, ABI ledger, Rust adapter, host).
- `qualification/`: `verify.py` (gate court), `rdfc.py` (semantic digest), `qualify.py`
  (differential court), `host_probe.exs`, `reference/` (hand-written domain + contract).
- `tests/test_qri_pack.py`: real ggen, cargo, wasmex, pyshacl; no mocks.

## Evidence boundary

Marketplace admission, ggen qualification and the pack's own tests only. The Component Model
profile is WIT emission only. Not a Level-5 claim; no DO authority.
