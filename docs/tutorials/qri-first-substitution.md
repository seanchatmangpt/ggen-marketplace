# First QRI substitution

You will qualify two realizations of one capability and read the claim that results.

## 1. Read the contract

`packs/qri-qualification-profile-pack/qualification/reference/contract.ttl` declares the `gl`
ABI (`gl_alloc`, `gl_free`, `gl_call`), the allowed WASI imports and five invariants.

## 2. Run the pack's court

```bash
python3.11 -m pytest packs/qri-qualification-profile-pack/tests -q
```

The real-differential test generates the adapter and host with ggen, builds a native binary and a
wasm32-wasip1 module from one hand-written domain, hosts the module with the generated wasmex
host, and compares six corpus requests (including an empty one and an unsupported one).

## 3. Read the receipts

Each receipt lists the invariants it preserved. The substitution claim names both receipts and one
runtime context. Change the context on one side and gate `010_qualified_substitution` refuses it.

## 4. Break it

Hand `host_probe.exs` a wrong digest: the host answers `admission_refused` with
`wasm_digest_mismatch` instead of trapping.

## See Also

[Qualify a realization](../how-to/qualify-a-realization.md) ·
[QRI profile reference](../reference/qri-profile.md)
