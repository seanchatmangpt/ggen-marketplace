# CSCB Rust Emission — Binding Contract (lane R7, RFC-2026-0042 §4.1)

Standing: PARTIAL_ALIVE

## Status vs R1

R1 has landed `ggen.toml` (pack-local, self-verification manifest) with one
rule (`arc-verdict`, Elixir template) but NOT the `templates/rust/` paths and
no `ontology.ttl` yet. Per the coordinate clause, this lane places templates
plus this sync-addendum note; the `ggen.toml` edit and ontology binding belong
to R1/R14.

## Scope honesty

The `cscb-runner` Rust harness measures **Rust subjects** on
no_std/edge targets per RFC-2026-0042 §4.1. BEAM-subject comparison lives in
the BEAM harness (lane R5). This harness is **not a BEAM comparator**; any
Rust-vs-BEAM claim must cite both harnesses run on the same host, same core
policy, and the same stage structure — never this harness alone.

## Binding contract (variables consumed by the templates)

Templates read these Tera variables. Names are PROPOSED here (R1/R14 to
confirm against `ontology.ttl` when it lands); until then the emitted output
in `emitted_rust/` uses these defaults.

| Variable | Type | Emitted default | Ontology source (proposed) |
|---|---|---|---|
| `crate_name` | string | `cscb-runner` | `cscb:RunnerProfile/name` |
| `description` | string | pack description line | `cscb:RunnerProfile/description` |
| `rust_edition` | string | `2021` | fixed |
| `metric_names` | string[] | six CSCB metrics | `cscb:Metric/name` (via `queries/metrics.rq`) |
| `stages` | `{name, id}[]` | S1..S6 | `cscb:BenchmarkArc/stages` (ordered S1 Warmer → S6 Solution) |
| `n_stages` | integer | 6 | derived: length of `stages` |
| `iterations` | integer | 10000 | `cscb:RunnerProfile/iterations` |
| `warmup_iterations` | integer | 1000 | `cscb:RunnerProfile/warmupIterations` |
| `percentile_points` | number[] | `[50, 90, 99]` | `cscb:RunnerProfile/percentiles` |
| `output_basename` | string | `cscb_results` | `cscb:RunnerProfile/outputBasename` |
| `stage_loop_var` | string | `s` | Tera loop variable over `stages` |

Note: `metric_names` labels WHAT a stage measures (R1's `mapsToLoss` metric
surface); `stages` defines the arc structure the runner iterates. Both are
emitted as static data so the runner stays allocation-light at the edge.

## Sync addendum (for R1/R14 to apply to pack `ggen.toml`)

Add under `[generation]` once `ontology.ttl` lands (output paths relative to
pack root; `emitted_rust/` is the emission target):

```toml
[[generation.rules]]
name = "rust-runner-manifest"
query = { file = "queries/runner_profile.rq" }
template = "templates/rust/Cargo.toml.tmpl"
output_file = "emitted_rust/Cargo.toml"
skip_empty = false
mode = "Overwrite"

[[generation.rules]]
name = "rust-runner-cycle-counter"
query = { file = "queries/runner_profile.rq" }
template = "templates/rust/cycle_counter.rs.tmpl"
output_file = "emitted_rust/src/cycle_counter.rs"
skip_empty = false
mode = "Overwrite"

[[generation.rules]]
name = "rust-runner-main"
query = "SELECT ?crate_name ?description ?iterations ?warmup_iterations ?output_basename ?n_stages WHERE { ... }"
query = { file = "queries/runner_profile.rq" }
template = "templates/rust/main.rs.tmpl"
output_file = "emitted_rust/src/main.rs"
skip_empty = false
mode = "Overwrite"
```

(Drop the stray literal `query = "..."` line — the file-based one is
authoritative; it is reproduced here only as the variable surface the query
must bind: `crate_name, description, iterations, warmup_iterations,
output_basename, n_stages`, plus `stages` as a nested loop context.)

## Compile smoke

Ran against a hand-instantiated render of these templates in `/tmp`
(defaults above). See `qualification/rust_emission_note.md` for the exact
commands and exits.
