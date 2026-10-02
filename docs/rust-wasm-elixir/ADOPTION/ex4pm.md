# ADOPTION DOSSIER — ex4pm

Standing: **PARTIAL_ALIVE** (33 algo wrappers already pack-rendered; transport/admission infrastructure hand-rolled).

## 1. Current state (evidence, measured 2026-10-01)

`wc -l ~/ex4pm/lib/ex4pm_engine/wasm/*.ex` → **39 files, 2,609 lines total**.

Generated wrappers (33 algorithm adapters; header names the pack): e.g. `align.ex` (16 lines) — "generated from `~/ggen-marketplace/packs/ex4pm-wasm4pm-bindings-pack`, source crate `wasm4pm`". Wrapper size class 16-20 lines each.

Hand-rolled infrastructure (6 files, measured):

| File | Lines | Role |
|---|---:|---|
| `real_transport.ex` | 557 | Wasmex-backed transport (moduledoc: "all 33 registered algorithms") |
| `ferroplan_transport.ex` | 280 | second transport |
| `adapter.ex` | 332 | shared six-state standing shape |
| `admission.ex` | 274 | admission predicates |
| `algo_registry.ex` | 314 | algorithm registry |
| `host.ex` | 268 | wasm host lifecycle |

Local ggen fabric: `priv/ggen/manifest.json` (renders `standing_coded`, `standing_coded_test`, `algo_registry` from `priv/ontology/ex4pm.ttl` + vendored pack ontologies); `priv/ggen/gates/` = `010_every_binding_registered.rq`, `020_unique_algorithm_id.rq`; `priv/ggen/vendor/` = `PACKS.lock.json`, `ex4pm-wasm4pm-bindings-pack.ontology.ttl`, `standing-ladder-pack.ontology.ttl`, `provenance.ttl`, `sync.sh`, `gates/`.

Mix tasks: `lib/mix/tasks/ex4pm.wasm.verify.ex` (374 lines), `ex4pm.wasm.doctor.ex` (31). BLAKE3 host digests: `lib/ex4pm/engine/cmca_wasm.ex` (237 lines; `request_blake3`/`result_blake3`/`receipt_blake3` fields at lines 113-137).

Pack facts consumed today: `ex4pm-wasm4pm-bindings-pack` (marketplace pack.toml v0.1.2: 33 algorithm export pairs + version/alloc/dealloc/free buffer ABI, gates 010-060, `regen_ontology.py`), vendored into `priv/ggen/vendor/`. **No `wasi-json-abi-pack` consumption** (grep over mix.exs/priv: zero hits outside the vendored bindings pack).

## 2. Consolidation actions

1. De-vendor the pack: replace `priv/ggen/vendor/ex4pm-wasm4pm-bindings-pack.ontology.ttl` + `PACKS.lock.json` pinning with a direct marketplace path reference in `priv/ggen/manifest.json` (`../ggen-marketplace/packs/ex4pm-wasm4pm-bindings-pack`), mirroring `~/affidavit/ggen.toml` `[[packs]]` shape. Command: edit manifest, run `mix ggen` (the repo's admitted ggen mix drive per its manifest), then `git diff --exit-code -- lib/ex4pm_engine/wasm test`. Gate: zero diff = vendored copy was faithful; non-zero diff = the vendor had drifted, and the diff IS the defect report.
2. Swap the 33 hand-declared wrapper renders onto pack templates verbatim: confirm each of the 33 wrapper files renders byte-identical from the pack (pack pack.toml declares the 33 export pairs). Command: per-algo re-render + `git diff --exit-code -- lib/ex4pm_engine/wasm/*.ex`. Gate: zero diff across all 33.
3. Extend `priv/ggen/gates/` with the wasi-json-abi-pack gate set (zero-imports `060_imports_policy_wasi_only.rq` adapted to ex4pm's export pairs, artifact pin `090_artifact_pin_shape.rq`) evaluated against `priv/ontology/ex4pm.ttl`. Gate: witness-pair court (`gate-court.toml` pattern from the marketplace pack) exits 0, and an injected fail witness fails loudly (anti-vacuity).
4. Pin the consumed wasm artifact: add `priv/ggen/registry/artifact-pin.json` rendered from the wasi-json-abi-pack pin template, binding the `wasm4pm_ex4pm_bindings.wasm` sha256 that `.github/workflows/ex4pm-bindings.yml` (wasm4pm repo) already computes (CI line 82-84). Gate: `mix ex4pm.wasm.verify` (374-line task already exists) passes against the pinned digest.
5. Render `algo_registry.ex` from the pack ontology instead of hand maintenance: extend `priv/ggen/manifest.json` with an `algo_registry` render whose query is the pack's algorithm table joined to `ex4pm.ttl`. Gate: re-render → `git diff --exit-code -- lib/ex4pm_engine/wasm/algo_registry.ex` → zero.

## 3. UNSUPPORTED ledger rows

- `UNSUPPORTED(wasi-json-abi-pack, elixir-wasmex-host-transport)` — the pack renders the wasm side only; `real_transport.ex` (557 lines: call/replay, standing states) has no pack template. Pack must grow a host-side `wasmex_transport.ex.eex`.
- `UNSUPPORTED(wasi-json-abi-pack, six-state-standing-adapter)` — `adapter.ex` (332 lines, standing shape) is consumer-specific; a generalized standing-shape template belongs in `ex4pm-wasm4pm-bindings-pack` or a host pack.
- `UNSUPPORTED(ex4pm-wasm4pm-bindings-pack, admission-predicate-render)` — `admission.ex` (274 lines) derived per-algo but hand-maintained.

## 4. 比 measurement

Today: generated wrappers = 2,609 − 2,025 (infra sum: 557+280+332+274+314+268) = **584 lines**; total pipeline = **2,609**. 比 = 584/2,609 = **22.4%**.
After actions 2+5 (algo_registry 314 + admission 274 move to render): manufactured = 584 + 314 + 274 = 1,172 / 2,609 = **44.9%**. After action 1 (vendor retired): vendored ontology copy (~1 file) leaves the repo's hand-count entirely (source moves upstream). Remaining lawful hand-written: transports + host lifecycle (1,105 lines) until UNSUPPORTED row 1 is paid down.

## 5. Falsifier

Adoption failed if: re-render after de-vendoring produces a diff in any of the 33 wrappers while `test/algo_registry_test.exs` (generated test, named in `priv/ontology/ex4pm.ttl` evidenceRef assertions) still passes — proving the registry test is vacuous against the ontology; or `mix ex4pm.wasm.verify` accepts a wasm artifact whose digest differs from the pinned one — proving the pin gate is dead. Also: a new pack-side algorithm added to `ex4pm-wasm4pm-bindings-pack` that does NOT appear in `algo_registry.ex` after re-render — the render is not total.

## 6. Risk / rollback

Snapshot: record `git -C ~/ex4pm rev-parse HEAD` and `cp -r priv/ggen/vendor /tmp/ex4pm-vendor-backup-$(git -C ~/ex4pm rev-parse --short HEAD)` before action 1 (the vendored ontology is the only copy of pack facts inside the repo). Rollback: restore manifest.json + vendor dir from the recorded SHA. The 39-file wrapper set is regenerable — any render corruption is repaired by re-running `mix ggen` from the pack, never by hand-editing wrappers (wrapper headers already state this provenance).
