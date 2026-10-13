# GraphLaw WASM pin freeze ledger

Date: 2026-10-13. Scope: the graphlaw law-kernel wasm artifacts consumed by
ash_a2a. Written from the two MANIFESTs as the sole number sources; no
invented claims.

## Two engine lineages

| | praxis-graphlaw wasm (ash_a2a vendored) | ash_graphlaw wasm |
|---|---|---|
| artifact | `priv/graphlaw/praxis_graphlaw.wasm` | `priv/graphlaw/graphlaw.wasm` |
| version | praxis-graphlaw v26.7.5 (wasm crate 26.7.5) | 26.9.29 (`abi_version` 1) |
| ABI | wasm-bindgen (wasm-bindgen 0.2.126, wasm-pack 0.13.1, target `wasm32-unknown-unknown`, bundler) | WASI (`wasi_snapshot_preview1`), exports `gl_alloc`/`gl_call`/`gl_free`/`memory` |
| sha256 pin | `187688d9e7e33a575713d6911d75687adb38713ed37412e211af263dfcbe0c28` | `7bb2a7e5ebcef7584b0b960451272d56fa75414d76a12138d41e8973e126eee0` |
| blake3 | `4724fbf950599642f898175319790bb35f192a60189e7b19963195fc3106cd36` | (not recorded in MANIFEST) |
| bytes | 3,249,361 | 6,641,876 |
| built | 2026-07-08T23:31:00Z (praxis git sha `bf96ea56d4055b5accd3f5124e559805f6502e2f`, INFERRED per provenance note) | release asset pinned by ontology.ttl; NOT a local build (file dated Sep 30 2026) |
| pinned by | `ash_a2a/priv/graphlaw/MANIFEST.json` (schema `ash_a2a.graphlaw.manifest/v1`) | `ash_graphlaw/priv/graphlaw/MANIFEST.json` (schema `ash_graphlaw.graphlaw.manifest/v1`), pinned via `ash_graphlaw` ontology.ttl |

ash_a2a ships the praxis artifact while also declaring
`{:ash_graphlaw, "~> 26.10"}` in `mix.exs` — one dependency (the graphlaw
law kernel), two unsynchronized engine lineages, distinct ABIs
(wasm-bindgen vs WASI), distinct pin registries.

## Materialized drift

The praxis lineage froze at v26.7.5 (built 2026-07-08); the ash_graphlaw
lineage advanced to 26.9.29. The drift is not latent: it has materialized
in the build surface.

## Upstream rebuild BLOCKED receipt

Measured this session (recorded in the praxis MANIFEST `rebuild` block):

- `pinned_sha_rebuild` at praxis `bf96ea5`: rebuilds are **semantically
  equivalent** to the committed artifact (identical `graphlaw_version()`
  and `graph_hash` over all three committed fixtures) but **not byte
  reproducible** — rebuilt sha256 `0582d595cd0d474fad90d67f1918509281067e6b8dc315df6048d8967edbec1a`,
  3,248,401 bytes, vs pinned `187688d9…`.
- `praxis_head_wasm32_build`: **BLOCKED** — praxis-graphlaw does not
  compile for `wasm32-unknown-unknown` at praxis HEAD (`31f149d`): E0599
  no associated function `open` for oxigraph `Store` at
  `crates/praxis-graphlaw/src/chatman/engine.rs:597`.

## Freeze decision (in principle)

The praxis wasm is **FROZEN at its pinned sha256**
(`187688d9e7e33a575713d6911d75687adb38713ed37412e211af263dfcbe0c28`) until
either:

1. **(a)** the upstream wasm32 build is fixed, a re-vendor lands, and a
   wasmex ABI port lands (M-L scale; its own work order); or
2. **(b)** praxis consumers migrate to the ash_graphlaw WASI artifact
   (same size class: MB-scale module, one kernel contract).

Neither path happens silently — each requires its own receipted work
order and a new pinned MANIFEST. Unfreeze without one of these two
receipts is a refusal, not a rotation.

## Eventual resolution: composition C14 (one admission kernel)

C14 (parts A+C+J) collapses N unsynchronized law-kernel implementations to
one admission kernel evaluated by one WASM law in every runtime, so
N-squared drift — the failure class recorded here — cannot recur. This
freeze is the holding pattern until that composition admits.
