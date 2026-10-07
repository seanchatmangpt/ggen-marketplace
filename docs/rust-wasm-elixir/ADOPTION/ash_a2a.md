# ADOPTION DOSSIER — ash_a2a

Standing: **PARTIAL_ALIVE** (artifact vendored, digest-pinned, dual-host verified — but the artifact is the legacy wasm-bindgen bundler target and the host layer is hand-rolled and duplicated across Node and Elixir).

## 1. Current state (evidence, measured 2026-10-01)

Artifact (`~/ash_a2a/priv/graphlaw/`):

| File | Size/Lines | Notes |
|---|---|---|
| `praxis_graphlaw.wasm` | 3,249,361 bytes | vendored binary; sha256 `187688d9e7e33a575713d6911d75687adb38713ed37412e211af263dfcbe0c28`, blake3 `4724fbf950599642f898175319790bb35f192a60189e7b19963195fc3106cd36` (from `WASMEX_HOST_MANIFEST.json`) |
| `WASMEX_HOST_MANIFEST.json` | 1,926 bytes | `source_crate: praxis-graphlaw-wasm`, `source_build_target: "wasm-bindgen bundler target"`, `vendored_at: 2026-09-16`, `imports_required: [__wbindgen_object_drop_ref, __wbg_getRandomValues_3f44b700395062e5]` |
| `MANIFEST.json` | 4,442 bytes | second manifest (dual-manifest state) |
| `conformance_vectors.json` | 94 lines | conformance fixtures |
| `graphlaw_host.mjs` | 149 lines | Node host |
| `host/graphlaw_host.mjs` | 162 lines | SECOND Node host copy |
| `graphlaw_driver.mjs` / `graphlaw_invoke.mjs` / `graphlaw_host_peer.mjs` / `graphlaw_host_probe.mjs` | 132 / 113 / 110 / 142 | Node tooling — mjs total **808 lines** |

Elixir host stack (`wc -l`): `lib/ash_a2a/graphlaw/vendor.ex` 437, `graphlaw/manifest.ex` 246, `graphlaw/wasm_host.ex` 268 (AshA2A.GraphLaw.WasmexHost, wasmtime via wasmex ~> 0.15.1 per the manifest), `graphlaw.ex` 60, `sa2a/graphlaw.ex` 136, `chicago/courts/graphlaw_engine.ex` 656, `chicago/fixtures/graphlaw_engine.ex` 407, `mix/tasks/ash_a2a.verify_graphlaw.ex` 185, `mix/tasks/ash_a2a.vendor_graphlaw.ex` 193, `dfcm/generated/graphlaw*.ex` 10+10. Hand-rolled Elixir total = **2,588 lines** (sum above, excluding the 10+10 generated) + 808 mjs.

Key structural fact: the artifact requires wasm-bindgen JS glue imports even under wasmex (manifest `imports_required` names `praxis_graphlaw_wasm_bg.js` symbols). This is the pipeline ex4pm's `build-wasm.sh` zero-import staticlib explicitly replaces. There is no marketplace-pack consumption on this path (no wasi-json-abi-pack or ex4pm-wasm4pm-bindings-pack reference in the vendored lane).

## 2. Consolidation actions

1. Re-vendor onto the consolidated pipeline: once graphlaw adoption (see graphlaw.md) renders a `rust-wasi-wasmex-pack` module, run `mix ash_a2a.vendor_graphlaw` (193-line task already exists) against the NEW artifact instead of the praxis wasm-bindgen one. Commands: `cd ~/ash_a2a && mix ash_a2a.vendor_graphlaw --source ~/graphlaw/target/wasm32-wasip1/wasm/graphlaw_wasm.wasm` (exact flags per the task's opts) → `mix ash_a2a.verify_graphlaw` (185-line verifier). Gate: `WASMEX_HOST_MANIFEST.json` `imports_required` becomes `[]` and `verify_graphlaw` passes on the committed bytes.
2. Collapse the dual manifest: `MANIFEST.json` (4,442 B) and `WASMEX_HOST_MANIFEST.json` (1,926 B) both describe the artifact. Render ONE manifest from `rust-wasi-wasmex-pack`'s manifest template (`wasmex_host_manifest.json.tmpl`), retire the other. Gate: `mix ash_a2a.verify_graphlaw` reads only the surviving manifest; grep for the retired filename in lib/ = 0.
3. Render the host manifest + registry from the pack: `registry.rq`→`wasm_capability_registry.json.tmpl` for graphlaw's 13 ops, replacing hand-maintained export lists inside `manifest.ex` (246 lines). Gate: rendered registry lists exactly `exports_used` currently in WASMEX_HOST_MANIFEST.json minus the `__wbindgen_*` entries (which disappear with the new artifact).
4. Node host consolidation: `graphlaw_host.mjs` (149) and `host/graphlaw_host.mjs` (162) are duplicate hosts — keep one as the slow-rail reference driver, delete the other after `conformance_vectors.json` passes through it. Gate: the surviving driver runs all 94 lines of conformance vectors; `grep -c graphlaw_host.mjs` in CI = 1 path.
5. Assess Wasmex-host parity vs Node host: `wasm_host.ex` (268) must reach the same conformance-vector pass set as the surviving mjs driver before any mjs retirement beyond the duplicate. Gate: differential run of both hosts over `conformance_vectors.json` → identical results, recorded in the verify task output.

## 3. UNSUPPORTED ledger rows

- `UNSUPPORTED(wasi-json-abi-pack, wasmex-elixir-host-manifest)` — the pack renders no Elixir-side host manifest/module; `wasm_host.ex` + `manifest.ex` + `vendor.ex` (951 lines) are hand-rolled. Pack (or a new host pack) must grow `wasmex_host.ex.eex` + manifest template.
- `UNSUPPORTED(wasi-json-abi-pack, node-reference-driver)` — the mjs drivers (808 lines) have no pack-owned template; decide admit-as-fact vs retire-once-wasmex-parity-holds (action 5).
- `UNSUPPORTED(ash_a2a-local, conformance-vector-schema)` — `conformance_vectors.json` (94 lines) is repo-local; promoting it into `chicago-graphlaw-court-pack` would make the vector set shared admission evidence, not a private fixture.

## 4. 比 measurement

Today: manufactured pipeline lines = 10 + 10 (`dfcm/generated/` only) = **20** / (2,588 + 808 + 20) = 20/3,416 = **0.6%** (the vendored .wasm is a build artifact, not lines).
After actions 1-3: manifest + registry renders ≈ 38 + 74 (affidavit-class magnitudes) = 112 manufactured; hand-written drops by the retired manifest (≤200 lines of the 4,442-byte + 1,926-byte pair) but `vendor.ex`/`wasm_host.ex` remain until UNSUPPORTED row 1 is paid. 比 ≈ 112/3,300 ≈ **3.4%** — honest ceiling without new pack facts; the structural win of this repo is the zero-import re-vendor (removes the entire JS-glue class), not line ratio.

## 5. Falsifier

Adoption failed if: after re-vendoring, `WASMEX_HOST_MANIFEST.json` still names `__wbindgen_*` imports (the new artifact was not actually wired — the verify task passed against a stale path); or `mix ash_a2a.verify_graphlaw` passes while the committed `praxis_graphlaw.wasm` sha256 ≠ manifest sha256 — digest check is dead; or the surviving Node driver and `wasm_host.ex` disagree on any of the 94 conformance vectors and both report pass — the vectors are not a shared oracle; or `MANIFEST.json` retirement breaks `vendor.ex` (437 lines) and CI stays green — nothing reads it, so the manifest court has no consumer (zero-information check).

## 6. Risk / rollback

Snapshot: `git -C ~/ash_a2a rev-parse HEAD`; the committed artifact IS the rollback (3,249,361 bytes, sha256 pinned in-repo) — `git -C ~/ash_a2a checkout -- priv/graphlaw/praxis_graphlaw.wasm` restores it. Before action 2, `cp priv/graphlaw/MANIFEST.json /tmp/asha2a-manifest-<sha>.json` and `cp priv/graphlaw/WASMEX_HOST_MANIFEST.json /tmp/asha2a-wasmex-manifest-<sha>.json`. Before action 4, `cp -r priv/graphlaw /tmp/asha2a-graphlaw-hosts-<sha>/`. Never overwrite the vendored artifact without `mix ash_a2a.verify_graphlaw` green on the new bytes first; a failed verify leaves the old artifact in place (the vendor task's transaction boundary).
