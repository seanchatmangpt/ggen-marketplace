# Source provenance

## What this pack models

beam4pm's application source is already manufactured by ggen from a single
`ontology.ttl` (291 `bpm:RecordType` individuals projected into Erlang, Elixir,
Gleam, Ash, a JSON Schema, and a docs reference). One large surface sits
*outside* that graph: the four BEAM-hosted WASM engines and their facades.

`ontology.ttl` in the consumer repo admits no `WasmEngine` and no `EngineOp`
class. Its full class census (`grep -oE '\ba [a-z0-9]+:[A-Za-z]+' ontology.ttl |
sort | uniq -c`) is `bpm:Field`, `bpm:RecordType`, `aic:Field`, `gha:Step`,
`rdfs:Class`, `rdf:Property`, `aic:ContractType`, `gha:Job`,
`bpma:AdmittedActuation`, `bpmg:ProcessTransition`, `gha:Workflow`,
`bpmg:ProcessContract`, `rf2:AdmittedOracleStream`,
`ghtf:RepoManagementInstance`, `b4pi:PackerImage`, `b4pi:Deployment` — nothing
for the engines. Every mention of `wasm`/`rust4pm`/`ferroplan`/`petgraph`/
`tract` in that file is prose (`gha:stepName`, `gha:runCommand`,
`rdfs:comment`), never a typed individual.

This pack closes that gap for the *reflection* surface. It does not regenerate
the hand-written facades; it manufactures the catalog those facades have never
had.

## Where every fact came from

Read out of `seanchatmangpt/beam4pm` (local checkout
`/Users/sac/gym-ecosystem/vendor/beam4pm`, branch `main`), from real source, not
from names:

| Ontology fact | Source |
| --- | --- |
| engine names, `bpw:abiPrefix` | `lib/beam4pm_{rust4pm,ferroplan,petgraph,tract}.ex` moduledocs and `call/2` bodies (`r4pm_alloc`/`fp_alloc`/`pg_alloc`/`tr_alloc`) |
| `bpw:wasmRelPath`, `bpw:crateDir` | each facade's `@wasm_rel` module attribute |
| `bpw:genServerName` | each facade's `@engine_name` module attribute |
| `bpw:cheapTimeoutMs` / `bpw:heavyTimeoutMs` | each facade's `@cheap_timeout` / `@heavy_timeout` |
| `bpw:erlangModule` | `src/beam4pm_{rust4pm,ferroplan,petgraph,tract}.erl` |
| `bpw:gleamModule` | `gleam/src/beam4pm/{rust4pm,ferroplan,petgraph,tract}.gleam` |
| op names (72) | the literal `"op" => "..."` JSON keys sent by each facade |
| `bpw:requestField` names and order | the literal sibling keys in each op's request map |
| `bpw:timeoutClass` | which of `@heavy_timeout` / `@cheap_timeout` that call site passes |
| `bpw:needsBase64` | call sites wrapping payloads in `Base.encode64/1` (`import_xes_gz`, `import_ocel_xml`, `load_model`) |
| `bpw:handleReturning` / `bpw:freesHandle` | each op's documented return / the `free_*` family |
| `bpw:isSubmodule` | `native/ferroplan` and `native/tract-wasm` are submodules; `native/rust4pm-wasm` and `native/petgraph-wasm` are in-repo crates (stated in `scripts/petgraph_wasm_build.sh`) |

Op totals: rust4pm 28, ferroplan 30, petgraph 10, tract 4 — 72 ops, split 36
READ / 36 DO.

## Authority boundary

All four engines share one ABI: `<prefix>_alloc(len) -> ptr`,
`<prefix>_call(ptr, len) -> (out_ptr << 32) | out_len`,
`<prefix>_dealloc(ptr, len)`. Three of the four facades' moduledocs state this
verbatim — the wire sequence and crash semantics are "IDENTICAL to
`BeamPM.Rust4PM`'s ... only the export names and the op catalog differ."

Consequence classes follow the GymAct convention already used by
`chatgptgym-gymact-bridge-pack`:

- `urn:gymact:consequence:read` — pure or handle-local query.
- `urn:gymact:consequence:do` — mutation **inside the engine's own wasm linear
  memory** (mint a handle, free a handle, edit an in-engine session/graph/OCEL).

`do` here is *not* host authority. No op in this catalog touches the
filesystem, the network, or another process. `gates/010_execution_boundary.rq`
enforces that: it refuses any op whose name reads as a host effect
(`exec|spawn|shell|system|http|fetch|post|write_file|read_file|delete|deploy|publish`),
any engine outside the four audited ABI prefixes, any READ op that mints or
frees a handle, and any two engines sharing a Wasmex GenServer (which would
collide in linear memory). Manufactured artifacts are catalogs and reflection
only; they dispatch nothing. Consequential host actuation stays external,
behind GymAct/BRCE admission — the same boundary
`chatgptgym-gymact-bridge-pack` establishes.

## Verification

`ggen sync run` at ggen@26.8.28 wrote all four outputs; graph hash
`1264ba9840bb91136c8a6a6b488c16f1cd470aacf35acd8e81ae52637b3401c1`.

- `src/beam4pm_engine_manifest.erl` compiles under `erlc` and answers
  `stats() => #{engines => 4, ops => 72, read => 36, do => 36}`.
- `lib/beam4pm_engine_manifest.ex` loads under `elixir` and answers the same
  counts.
- `schema/beam4pm_engine_ops.schema.json` parses as JSON with 72 `$defs`.
- `gates/010_execution_boundary.rq` returns **0 rows** against this ontology,
  and returns 3 refusals against an injected negative control (a fifth engine
  with an unadmitted prefix, a `shell_exec` DO op, and a READ op that mints a
  handle).

## Consumer wiring

Additive. In beam4pm's `ggen.toml`:

```toml
beam4pm-wasm-engine = { path = "vendor/ggen-marketplace/packs/beam4pm-wasm-engine-pack" }
```

The four output paths (`lib/beam4pm_engine_manifest.ex`,
`src/beam4pm_engine_manifest.erl`, `schema/beam4pm_engine_ops.schema.json`,
`docs/reference/beam4pm_engine_ops_reference.md`) do not exist in the consumer
repo today, so wiring this pack overwrites nothing. The engine facades
themselves stay hand-written and untouched.

## Known consumer drift this pack would surface

`README.md` claims "31 `bpm:RecordType` individuals" while the consumer
ontology now admits 291 — stale by ~9x. `BeamPM.EngineManifest.stats/0` and
`beam4pm_engine_manifest:stats/0` exist so the engine-side counts are derived
rather than restated.
