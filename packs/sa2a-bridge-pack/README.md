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
- **Not yet run**: a live `ggen sync run` or `mix ggen_igniter.sync`
  rendering these templates into a real xaas checkout. That is xaas-side
  work (vendoring a project-local `ontology.ttl` instance, per the existing
  `priv/zcode_plugin/` precedent, since `ggen sync run` refuses ontology
  paths outside the project root) and is `UNKNOWN` until executed there.

## Templating grammar note

Templates here are authored in Tera syntax (`{{ }}` / `{% for %}`), matching
real `ggen`'s renderer and `xaas-castle-bridge-pack`'s own templates. If
rendered via `ggen_igniter` instead (its `Render` layer uses stdlib EEx, not
Tera, per `ggen-igniter-bootstrap-pack`'s documented decision), these
templates need either an EEx port or dual-authoring — decide during the
first real xaas-side render attempt, not speculatively here.
