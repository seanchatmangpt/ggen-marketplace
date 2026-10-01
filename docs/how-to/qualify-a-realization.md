# Qualify a realization against a QRI contract

Goal: produce two qualification receipts and a substitution claim for a native and a WASM
realization of one contract, then re-admit the result.

## Prerequisites

`ggen`, `cargo` with the `wasm32-wasip1` target, `mix` with Hex access (wasmex `~> 0.15.1`),
and `python3.11` with `rdflib`, `pyshacl`, `pyld`.

## Steps

1. Generate the projection in a scratch copy of the pack (never commit `generated/`):
   `ggen sync run`.
2. Add your hand-written `domain.rs` beside the generated `adapter/src/lib.rs`, build
   `cargo build --release --target wasm32-wasip1 --lib` and a native binary over the same domain.
3. Put `generated/beam/qri_host.ex` in a mix project that depends on wasmex.
4. Run the court:

   ```bash
   python3.11 qualification/qualify.py --contract <contract.ttl> --wasm <module.wasm> \
     --native <native-bin> --mix-dir <mix-project> --out receipts.ttl
   ```

5. Re-admit `receipts.ttl`: every `gates/*.rq` must return zero rows and
   `shapes/qri.shacl.ttl` must conform (`tests/test_qri_pack.py` does both).

## Refusals to expect

`wasm_digest_mismatch` (pinned hash differs), `wasm_import_surface_mismatch` (import outside the
contract), exit code 1 from `qualify.py` (an invariant was not established, so no claim).

## See Also

[QRI profile reference](../reference/qri-profile.md)
