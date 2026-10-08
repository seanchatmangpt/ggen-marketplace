# ADOPTION DOSSIER — bcinr

Standing: **UNKNOWN** (no wasm pipeline exists — evidence-based assessment as a future consumer only; nothing to migrate today).

## 1. Current state (evidence, measured 2026-10-01)

- Rust workspace: `~/bcinr/Cargo.toml` declares `members = ["crates/bcinr-logic", ...]`, `default-members = ["crates/bcinr-logic"]`. Crates observed under `~/bcinr/crates/`: `bcinr-cmca`, `bcinr-guarded`, `bcinr-logic`, `bcinr-mfw-ir`, `bcinr-pddl`, `bcinr-powl`.
- Wasm artifacts: `find ~/bcinr -name "*.wasm" -not -path "*/target/*"` → **0 files**. `wasm_raw.txt` exists at repo root: **0 lines** (empty). No `wasm/` directory, no wasm CI job (grep for wasi/wasm in `ggen.toml`: zero hits), no wasm target in any observed build file.
- `~/bcinr/tools/ggen/`: single `src/main.rs` of **776 lines** — NOT the ggen RDF generator. Its own doc comment: "Counterfactual & Falsification Test Generator — discovers all 300+ algorithms and generates targeted falsification tests" over `crates/bcinr-logic/src/algorithms/`. This is a hand-written, walkdir-based test generator that collides with the marketplace `ggen` name.
- `~/bcinr/ggen.toml`: exists, **117 lines**, no wasm/wasi references.
- Constitutional context (repo AGENTS.md): `#![no_std]`, no alloc, no floating point, fixed-width, branchless authoritative code — i.e. the substrate is already shaped like an ideal wasm module source, but the constitution's seven-evidence requirements (contract, oracle, mutants, source audit, object-code audit, reproducible evidence) mean any wasm pipeline here must be admitted through the repo's own gates, not bolted on.

## 2. Consolidation actions (future-consumer plan; each action gated on the prior)

1. Name the consumer surface before any pipeline: pick one authoritative crate root (candidate: `bcinr-logic`) and declare its `wja:WasmModule` facts (export prefix, op set, error codes) in a bcinr ontology. Precondition gate: the crate compiles for `wasm32-wasip1` with `cargo check --target wasm32-wasip1` — the no_std/no-alloc constitution makes this plausible but UNVERIFIED today (no target in rust-toolchain.toml observed).
2. If (and only if) action 1's gate passes: adopt the rust-wasi-wasmex-pack render for the FFI shell (ffi.rs + guards + abi_meta + cargo fragments), pack path `../ggen-marketplace/packs/rust-wasi-wasmex-pack` (wasi-json-abi-pack is deprecated — its FFI shell capability lives in the unified pack). Gate: rendered shell passes `bcinr-cheat-scanner` + `cargo make scan-cheats`/`contract-gate` (repo's own admitted gates, per AGENTS.md §23) AND the rendered object code passes the repo's disassembly audit — the pack render must satisfy the host constitution, not bypass it.
3. Retire or rename `tools/ggen`: the 776-line walkdir test generator is a second, hand-rolled implementation of "ontology/test generation" that is not the marketplace ggen. Either rename it (`bcinr-falsifier-gen`) to end the namespace collision, or port its algorithm-discovery onto the marketplace ggen pack machinery. Gate: after rename, `grep -rn "tools/ggen" ~/bcinr --include="*.toml" --include="*.md" | wc -l` updated everywhere; after port, rendered tests pass `cargo make test-mutants`.
4. Artifact pin from day one: if a `.wasm` is ever produced, render `ARTIFACTS.sha256` + `artifact-pin.json` in the same change (no unpinned artifact may land). Gate: CI sha check present in the same PR that adds the build.

## 3. UNSUPPORTED ledger rows

- `UNSUPPORTED(wasi-json-abi-pack, no_std-no-fp-consumer-contract)` — the pack's render targets (affidavit, graphlaw) are std crates; no pack fact certifies the rendered FFI shell is `#![no_std]`/alloc-free/fp-free as bcinr's constitution demands. The pack must grow a `wja:noStdProfile` fact + gate before bcinr can consume it lawfully.
- `UNSUPPORTED(bcinr-local, wasm-toolchain-target)` — no wasm32 target pin exists in `rust-toolchain.toml` (observed); adding one is a bcinr-side decision requiring its own gate evidence.

## 4. 比 measurement

Today: pipeline lines = **0**; 比 = undefined (no denominator) — reported as UNKNOWN, not 0%.
If actions 1-2 fire: manufactured = full FFI surface (~304 lines at affidavit-class render magnitudes) vs hand-written op bodies; projected 比 at adoption ≈ 14-20% (graphlaw-class, since op bodies dominate), computed on real wc -l at that time. No number is claimed here because no render or op inventory exists to count.

## 5. Falsifier

Adoption (future) failed if: `cargo check --target wasm32-wasip1` passes but `cargo make scan-cheats` was not run on the rendered shell — a pack render admitted past the repo constitution without its seven evidences; or the rendered FFI shell contains any branch/allocation symbol under the repo's disassembly audit and is admitted anyway — gate-jurisdiction theater (CHEAT-010 class). Falsifier for THIS dossier: any claim that bcinr "has a wasm pipeline" — disproven by the zero `.wasm` files and zero wasm CI references measured above.

## 6. Risk / rollback

Nothing to snapshot today (no pipeline). When action 2 fires: snapshot the pre-render tree (`git -C ~/bcinr rev-parse HEAD` + archive `crates/<consumer-crate>/src/`), because the repo's own MaturityScrutiny protocol (AGENTS.md §25) freezes feature work on any gate failure — a bad render must be revertible without quarantining the substrate. Keep the bcinr gates (`scan-cheats`, `contract-gate`, `test-mutants`) as the outer boundary; the marketplace pack gates nest inside them, never replace them.
