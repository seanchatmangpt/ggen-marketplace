# ADOPTION DOSSIER — graphlaw

Standing: **PARTIAL_ALIVE** (wasm32-wasip1 cdylib built and differentially tested in CI; 100% of the pipeline hand-rolled; the marketplace pack is already staged for this consumer).

## 1. Current state (evidence, measured 2026-10-01)

Pipeline surface (`wc -l`):

| File | Lines | Origin |
|---|---:|---|
| `~/graphlaw/wasm/src/lib.rs` | 93 | hand-written FFI shell: `gl_alloc/gl_call/gl_free`, packed-u64 `(out_ptr << 32) | out_len`, OUTSTANDING atomic, saturation arithmetic |
| `~/graphlaw/wasm/Cargo.toml` | 14 | hand-written (cdylib wasm32-wasip1) |
| `~/graphlaw/src/abi.rs` | 1,057 | hand-written JSON op layer; `dispatch()` at line 407 has **13 arms**: capabilities, sniff, parse, convert, canonical, sparql, shacl, shex, entail, datalog, hooks, law, policy |
| `~/graphlaw/tests/wasm_abi.rs` | 942 | hand-written wasmi differential harness |

Pipeline total = **2,106 lines**, 0 lines rendered from any pack.

Vendor patch: `~/graphlaw/vendor/upstream/purrdf-sparql-eval.patch` + `.md` — re-gates upstream clock/entropy reads from `target_arch = "wasm32"` to `all(target_arch = "wasm32", target_os = "unknown")` so wasip1 uses real WASI clock/RNG instead of panicking wasm-bindgen stubs (vendor/README.md).

CI: `.github/workflows/ci.yml` builds `graphlaw-wasm` for wasm32-wasip1 (line 35), uploads the artifact (lines 45-46) — no drift court, no pin, no pack. `ggen.toml` exists at repo root but contains no wasi-json-abi reference (grep: zero hits).

Pack side is staged: `~/ggen-marketplace/packs/wasi-json-abi-pack/qualification/graphlaw-consumer.ttl` + `graphlaw-ops.ttl` exist, and `packs/wasi-json-abi-pack/generated/graphlaw/` already holds a rendered candidate set (`ffi.rs`, `abi_meta.rs`, `guards.rs`, `cargo-config.toml`, `cargo-profile.toml`, `capability-registry.json`, `op-examples.json`, `tests_common.rs`, `ARTIFACTS.sha256` — 9 files). Also related: `graphlaw-ash-capability-pack`, `chicago-graphlaw-court-pack` in the marketplace.

Hand-rolled today: everything on the wasm path, including exactly the surfaces the pack renders for affidavit (FFI shell, ABI metadata, guards, cargo fragments, artifact hashes).

## 2. Consolidation actions

1. Admit the staged render: diff `packs/rust-wasi-wasmex-pack/templates/guest/ffi.rs.tmpl` (consolidated from `wasi-json-abi-pack`) against graphlaw's hand-written FFI shell to confirm export alignment (export_prefix `gl`, packed-u64 call, outstanding byte accounting), then promote it into `~/graphlaw/wasm/src/` replacing the 93-line `lib.rs`. Commands: from `~/graphlaw`, add `ggen.toml` `[[packs]]` entry (name `rust-wasi-wasmex-pack`, path `../ggen-marketplace/packs/rust-wasi-wasmex-pack`) + `[ontology]` source declaring the pipeline graph for graphlaw → `ggen sync` → `git diff --exit-code -- wasm/src/ffi.rs` against the staged candidate. Gate: rendered FFI compiles `cargo build --locked -p graphlaw-wasm --target wasm32-wasip1 --profile wasm` and `tests/wasm_abi.rs` passes unchanged (the 942-line harness is the differential oracle — it must NOT need edits for the shell swap).
2. Render ABI metadata + guards: `meta.rq`→`wasm_abi_meta.rs.tmpl` and `guards.rq`→`wasm_guards.rs.tmpl` for the 13 ops. Gate: `abi_version` and op table in the render match `abi.rs:407` dispatch arms exactly (13); a 14th/12th op in the render is a REFUSED build.
3. Vendor patch promotion: evaluate moving the purrdf-sparql-eval clock re-gating into the pack as a declared patch fact (`wja:requiresVendorPatch`), so consumers inherit it. Gate: a consumer ontology without the patch fact fails the `080_wasi_import_closure.rq` gate (wasm-bindgen import present) — anti-vacuity witness required.
4. Wire drift court + pin into `ci.yml`: render `ARTIFACTS.sha256` (template `wasm_artifacts.sha256.tmpl`) into `~/graphlaw/wasm/registry/`, CI does `git diff --exit-code` post-render + `cmp` double-build (affidavit CI lines 68-98 pattern). Gate: sha of uploaded `graphlaw-wasm.wasm` (CI lines 45-46) matches the rendered pin.
5. Run the 10 marketplace gates + `gate-court.toml` witness court against graphlaw's ontology. Gate: all pass with witness pairs; injected fail witness fails exactly one gate.

## 3. UNSUPPORTED ledger rows

- `UNSUPPORTED(wasi-json-abi-pack, 13-op-graphlaw-table)` — `qualification/graphlaw-ops.ttl` exists but the 13 dispatch ops are not yet a closed, gated op table; until the render's op list provably equals `abi.rs:407`, the dispatch stays hand-owned.
- `UNSUPPORTED(wasi-json-abi-pack, packed-u64-call-variant)` — graphlaw's `gl_call(ptr,len) -> (out_ptr<<32)|out_len` packed return differs from the affidavit-class `_call` shape (separate out_ptr/out_len exports per pack.toml description); pack must grow a `packed-return` ABI variant fact or graphlaw keeps a thin adapter as lawful hand-written.
- `UNSUPPORTED(wasi-json-abi-pack, vendor-patch-fact)` — the WASI clock re-gating patch (vendor/upstream) is repo-local; no pack fact carries it.

## 4. 比 measurement

Today: manufactured = 0 / 2,106 = **0%**.
After actions 1-2+4 (rendered: ffi 174-class + abi_meta 47 + guards + registry 74 + ARTIFACTS 9; sizes = affidavit's measured render outputs, the only observed magnitudes): manufactured ≈ 174+47+74+9 = **304** (guards render unmeasured — excluded, counted hand-written until first render exists). Hand-written remainder = 2,106 − 304 = 1,802 (op bodies in abi.rs 1,057 + differential harness 942 are lawful residue; lib.rs 93 retired). 比 = 304/2,106 ≈ **14.4%**. Attainable ceiling this repo ≈ 14-20% until the 13 op bodies themselves are pack-templateable (they are graphlaw's product semantics — likely permanent hand-written under `HANDWRITTEN-graphlaw.md`, a file already present in the pack root).

## 5. Falsifier

Adoption failed if: the rendered FFI shell passes `tests/wasm_abi.rs` with the OLD `abi.rs` but the swap changes any observable response byte on the 13 ops (differential harness must be byte-identical pre/post swap — capture baseline outputs first); or the rendered op table disagrees with `dispatch()` arms (13) and CI stays green — the metadata gate is vacuous; or `gl_call` packed-u64 semantics break under the pack's split out_ptr/out_len convention and the harness still passes — the harness never exercises buffer lifetime (OUTSTANDING accounting).

## 6. Risk / rollback

Snapshot: `git -C ~/graphlaw rev-parse HEAD`; `cp wasm/src/lib.rs /tmp/graphlaw-ffi-<sha>.rs` (the 93-line shell is the only implementation of the packed-u64 protocol until the render is proven); `cp src/abi.rs /tmp/graphlaw-abi-<sha>.rs`. Keep `vendor/` untouched in the adoption change (patch promotion is its own transition). Rollback: `git -C ~/graphlaw checkout -- wasm/src` restores the cdylib; the differential harness (942 lines) is the boundary re-run after any rollback (`cargo test -p graphlaw --test wasm_abi`).
