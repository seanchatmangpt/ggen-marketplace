# beam-wasmex-host-pack

Generates the **Elixir/Wasmex HOST transport** for a zero-import (or WASI-only)
reactor wasm module, from RDF facts (`bwh:WasmexHostSurface` +
`bwh:AlgorithmBinding`):

- `templates/wasm_host.ex.tmpl` — the host module: `start/2` (digest-pin
  admission → `Wasmex.Engine.new` → `Wasmex.Store.new` → `Wasmex.Module.compile`
  → import-surface judge → `Wasmex.start_link`), `call/4` + `replay/4` over the
  real `alloc → write → call → read → free` sequence, `execute/5` (call + replay
  + receipt in one pass), `digest/1` / `verify_digest/2` host-authoritative
  digest hooks (fail-closed unpinned refusal), typed refusals
  (`{{Root}}.Refusal`), per-algorithm export-pair table (`algo_specs/0`),
  optional compile-time-embedded host manifest (`@external_resource`).
  Both guest return modes: **out-len-through-pointer**
  (`call_export(in_ptr,in_len,out_len_ptr) -> out_ptr`, LE-u32 length through
  the pointer — the mode `Ex4pmEngine.Wasm.RealTransport` actually drives) and
  **packed_u64** (`(out_ptr <<< 32) | out_len`).
- `templates/algo_wrapper.ex.tmpl` — one generated wrapper module per
  `bwh:AlgorithmBinding` (`call/3`, `replay/3`, `execute/3` over the export
  pair), rendered per row.
- `templates/wasmex_host_manifest.json.tmpl` — host manifest
  `beam.wasmex.host.manifest/v1`, field structure modeled on
  `~/ash_a2a/priv/graphlaw/WASMEX_HOST_MANIFEST.json` +
  `~/ash_a2a/priv/graphlaw/MANIFEST.json` (artifact sha256/blake3/bytes, host
  module/runtime/imports, export list, ABI version, string_abi,
  measurement_provenance). Measured digest fields are generated `null` — fill
  them from the real artifact bytes; the generated host refuses an unpinned
  digest.
- `templates/mix_deps.exs.tmpl` — mix.exs dependency snippet, wasmex pinned as
  ex4pm pins it: `{:wasmex, "~> 0.14"}` (`~/ex4pm/mix.exs` l.109; lock resolves
  0.15.1, `~/ex4pm/mix.lock` l.81) plus `{:jason, "~> 1.4"}`.
- `gates/010_host_surface_abi.rq` — fail-closed gate over the RDF facts
  (missing allocator/memory facts, out-of-vocabulary out/import modes,
  incomplete bindings, dangling hostModule). Witnessed: 0 rows on the worked
  fixture, 1 row after mutating `outMode` to `"handle_magic"`.

## Consumers targeted

- **ex4pm** — worked exemplar rows ground the ontology
  (`urn:beam:wasmex:host:ex4pm-bindings`): allocator trio
  `wasm4pm_ex4pm_bindings_alloc_v1/free_v1/dealloc_v1`, `memory`, limits
  16 MiB / 64 MiB / 5000 ms, digest prefix `sha256:`
  (`Ex4pm.Core.Hash`, `~/ex4pm/lib/ex4pm/core.ex` l.76+) — all read out of
  `~/ex4pm/lib/ex4pm_engine/wasm/real_transport.ex`,
  `.../wasm/admission.ex`, `.../wasm/mean.ex`.
- **ash_a2a** — `AshA2A.GraphLaw.WasmexHost` consumers of the manifest shape.
- **future graphlaw / affidavit hosts** — any BEAM app hosting a
  zero-import/WASI-only ptr/len-JSON wasm module.

## Ladder decision: INVENT (failed edges on every EXTEND candidate)

Search ladder run by capability family ("Elixir/Wasmex host transport"), not by
name; every candidate was read before this pack was created.

1. `beam4pm-wasm-engine-pack` — manufactures engine CATALOGS and reflection
   surfaces (manifests, wire-op schema, docs table) for beam4pm's four
   handle-ABI engines. No Wasmex call/store/transport code exists in its
   templates (`grep -rn Wasmex packs/beam4pm-wasm-engine-pack/templates/`
   matches only prose, `engine_ops_reference.md.tmpl:58`). FAILED EDGE: it has
   no host-transport semantics to extend.
2. `ex4pm-wasm4pm-bindings-pack` — owns the GUEST side (Rust `extern "C"`
   export templates + Cargo.toml). Its only Elixir template,
   `templates/elixir_adapter.tmpl` (30 lines), renders just a
   `use Ex4pmEngine.Wasm.Adapter, ...` wrapper and PRESUPPOSES a hand-written
   host (`Adapter`, `RealTransport`, `Admission` in ex4pm are exactly that
   hand-written residue). FAILED EDGE: guest ABI + consumer-specific wrapper
   only; the host transport is assumed, not expressed.
3. `elixir-mcp-a2a-pack` — MCP/A2A protocol surfaces (router/agent/descriptor).
   FAILED EDGE: different family; no wasm semantics.
4. Nearest miss found by the family sweep: `qri-qualification-profile-pack`
   `templates/beam-host/` DOES generate a Wasmex host — but it structurally
   REFUSES this pack's target ABI:
   - `host.ex.tmpl:112` —
     `{%- if p.out_mode != "packed_u64" or p.req_consumed != true or p.len_type != "u32" -%}{{ UNSUPPORTED_host_profile_not_packed_u64_consumed_u32 }}`
     — any non-packed_u64 / non-req-consumed profile is refused, so the
     out-len-through-pointer mode ex4pm actually uses
     (`real_transport.ex` l.23-27 moduledoc, l.414-449 `invoke/8`) cannot be
     generated;
   - `host.ex.tmpl:43` — free symbol derived as
     `COALESCE(?fs, CONCAT(?prefix, "_free"))` — a single deallocator; the
     ex4pm alloc/free/dealloc trio (`_v1` suffixed, split output-buffer free
     vs input-buffer dealloc, `admission.ex` l.56-58) is inexpressible;
   - `engine_load.ex.tmpl:95` — `@import_module "wasi_snapshot_preview1"`
     hardcoded; no zero-import admission shape (refuse-ANY-import);
   - no `<algo>_replay_v1` pair semantics anywhere in `beam-host/` (grep
     "replay" over those templates: 0 matches) — the replay-verified receipt
     identity `RealTransport.replay/3` implements
     (l.223-258) has no counterpart;
   - no per-algorithm wrapper generation (ops travel as a string-keyed `"op"`
     field of one request map, not as per-algorithm export pairs).
   QRI is also scoped to the qri:CapabilityContract qualification family, not a
   general host pack. failed(edge_QRI) ≠ failed(G) — but each edge above is a
   concrete, cited gap, and patching any of them would mean rewriting the QRI
   family's contract, not extending a fact.

None of the named packs expresses host-transport semantics; the one pack that
does refuses the target ABI on four independent edges. A new top-level pack is
therefore the lawful INVENT step under the search ladder; this README records
the failed edges as its admission evidence.

## Wiring a consumer

```bash
# in the consumer repo (one canonical checkout):
mkdir -p priv/ggen && cp <pack>/ggen.toml priv/ggen/ && cd priv/ggen
cp <pack>/ontology.ttl . && cp -r <pack>/templates .
ggen sync run          # renders host + wrappers + manifest + deps snippet
```

Then: merge `priv/ggen/wasmex_deps.exs` contents into `mix.exs` deps, run
`mix deps.get`, render the manifest's measured fields
(`shasum -a 256`, `b3sum`, `wc -c`) into
`priv/<app>/wasmex_host_manifest.json`, and point the host's embedded
`@manifest_path` at your real MANIFEST.json (the `bwh:manifestExpand` fact).

## Validation standing (measured 2026-10-01, ggen 26.9.28)

- ontology.ttl: rapper turtle parse EXIT 0 (126 triples); pack SPARQL queries
  return the worked rows (rdflib 7.1.4).
- ggen render: `ggen sync run` EXIT 0 in a /tmp consumer project — 5 artifacts
  (host 591 lines, 2 wrappers, valid JSON manifest `python3 -m json.tool` OK,
  deps snippet).
- Elixir syntax/structure check: `elixirc` (Elixir 1.18.4-otp-27, ex4pm's
  pin) over the rendered host + wrappers + /tmp-only Jason/Wasmex.EngineConfig
  stubs → EXIT 0, 6 .beam files; the only remaining diagnostics are
  `Wasmex.* is undefined (module not available)` — the dep-absence class, not
  template defects.
- gate: 0 violation rows on the fixture; 1 row after an outMode mutation
  (anti-vacuity witnessed).
- NOT yet established (named, not silently assumed): compile against REAL
  wasmex+jason (BLOCKED in the authoring lane: no `deps.get`, rustler NIF
  build); a real `Wasmex` execution against the actual
  wasm4pm_ex4pm_bindings artifact; `mix format --check-formatted` on generated
  output (generator does not format, same disclosed follow-up
  elixir-mcp-a2a-pack records). Standing of the templates: PARTIAL_ALIVE
  (rendered + syntax-proven); end-to-end ALIVE requires the missing dep-bound
  compile and a real artifact execution.

## Known limitations

- `algo_specs/0` row order follows GROUP_CONCAT row production (SPARQL has no
  ORDER BY inside aggregates); the map rows are order-independent, but a
  consumer wanting deterministic spec order should sort in the consumer.
- ggen renders each template once per row of its widest query
  (FM-WRITE-008 collision otherwise); this pack keeps every query at
  `LIMIT 1` and folds the algorithm list into the host row via
  `GROUP_CONCAT` — keep that shape when extending.
- Tera emits `{{ "{{" }}` escapes for literal `{{` case-clause tuples in the
  generated Elixir; do not "simplify" them.
