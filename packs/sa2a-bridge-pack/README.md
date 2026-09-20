# sa2a-bridge-pack

Bridges `~/xaas` (Elixir/Ash outer control plane) to `~/autofde-lab`'s SA2A
(Semantic Agent-to-Agent) calculus — Observation → Candidate → Admission →
Authority → Actuation → Receipt → Replay (`autofde_lab.sa2a.algebra`) —
over autofde-lab's real stdio JSON-lines BEAM port bridge
(`src/autofde_lab/beam/beam_port_bridge.py`, `sa2a_validate` / `sa2a_admit`
/ `sa2a_plan` / `sa2a_execute` / `sa2a_replay` ops, added in autofde-lab
commit `b70331aa`).

Shape: same edge-chain / proof-obligation / SHA-pinning discipline as
`xaas-castle-bridge-pack`, composed rather than reinvented (REUSE→COMPOSE
per the ecosystem's own doctrine) — one `s2b:EdgeSpec` per port op, exactly
one (`sa2a_execute`) marked `doBoundary true`. This pack generates only the
contract/topology/proof/SHACL/test layer as plain Elixir data modules
(`@identity`, `@edges`); the actual `Port.open/2` GenServer wrapper and any
Ash action calling `execute/1` remain hand-written in xaas, referenced by
name from the ontology only — never generated, per `ggen_igniter`'s
construct-only boundary.

## Standing (as of this pack's authoring commit)

- `ontology.ttl` — real, loads via `rdflib.Graph().parse(..., format="turtle")`.
- `gates/*.rq` — 6 real SPARQL ASK-shaped gates, run for real against
  `ontology.ttl` via `rdflib`; all 6 pass (0 rows each) as of this commit.
- `templates/*.tmpl` — 5 templates; each embedded SPARQL query was run for
  real against `ontology.ttl` and returns the expected row shape (contract:
  1 row, edge-catalog: 5 rows in sequence order, SHACL: 1 row, ERRC: 4 rows
  one per category, test: 1 row).
- **`ggen_igniter` (real Elixir renderer) round-trip: ALIVE.** Ran, for
  real, from `~/ggen_igniter` (the real, live `ggen_igniter` checkout, not a
  stub):
  ```
  mix ggen_igniter.sync --ontology <this pack>/ontology.ttl \
    --query spec=<this pack>/ggen_igniter/queries/contract.rq \
    --template <this pack>/ggen_igniter/templates/sa2a_bridge_contract.ex.eex \
    --out tmp_out/sa2a_bridge_contract_dryrun.ex --yes
  # -> "wrote tmp_out/sa2a_bridge_contract_dryrun.ex (engine: oxigraph, 1 query, 1 total row(s)) (via reactor)"

  mix ggen_igniter.sync --ontology <this pack>/ontology.ttl \
    --query edges=<this pack>/ggen_igniter/queries/edges.rq \
    --template <this pack>/ggen_igniter/templates/sa2a_bridge_edges.ex.eex \
    --out tmp_out/sa2a_bridge_edges_dryrun.ex --yes
  # -> "wrote tmp_out/sa2a_bridge_edges_dryrun.ex (engine: oxigraph, 1 query, 5 total row(s)) (via reactor)"
  ```
  Both rendered outputs are valid Elixir (`defmodule Xaas.Sa2a.Generated.Contract`,
  `defmodule Xaas.Sa2a.Generated.EdgeCatalog`); the edge catalog's 5 rows are
  in sequence order and exactly one (`sa2a_execute`, sequence 40) has
  `do_boundary?: true`. Both scratch outputs were removed after verification
  (`ggen_igniter/tmp_out/` is that repo's own scratch dir, not this pack's).
- **Not yet run**: wiring this into a real xaas checkout as a tracked,
  committed generation target (vendoring a project-local `ontology.ttl`
  instance per the existing `priv/zcode_plugin/` precedent, adding a
  `mix ggen_igniter.sync` invocation to xaas's own build/CI, and writing the
  hand-written `Xaas.Sa2a.Bridge` `Port.open/2` GenServer residue that calls
  these generated modules). That is xaas-repo work, tracked separately, and
  is `UNKNOWN` until executed there — the renderer itself is proven `ALIVE`
  above; only the target-repo integration remains.

## Two template flavors, both real

- `templates/*.tmpl` — Tera syntax (`{{ }}` / `{% for %}`) with YAML
  frontmatter (`to:`, `sparql: results: |`), matching real `ggen`'s renderer
  and `xaas-castle-bridge-pack`'s own templates. Each embedded SPARQL query
  was verified against `ontology.ttl` via `rdflib` (see above) but not
  rendered end-to-end by the real `ggen` Rust binary in this session.
- `ggen_igniter/{queries,templates}/*` — plain `.rq` query files (no
  frontmatter) + `.eex` templates, matching `ggen_igniter`'s real
  `--query name=path.rq --template path.eex --out path` CLI convention
  (confirmed different from real `ggen`'s frontmatter-embedded-routing
  convention this session — `ggen_igniter` takes one query/template/out set
  per invocation, not a directory of self-routing templates). This is the
  set actually proven end-to-end above.
