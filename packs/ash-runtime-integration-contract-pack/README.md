# Ash Runtime Integration Contract Pack

Deterministic GGen source for generating Ash/Reactor runtime seams from admitted RDF facts. The pack binds exact subjects, authority, runtime actions, RuntimeShape semantic identity, receipts, replay, refusals, OCEL evidence, persistence, API/CLI surfaces, and failure semantics without granting model or planner output ambient execution authority.

`RuntimeShape` is the CONSTRUCT-time bridge into `GgenIgniter.RuntimeShape`: the ontology remains canonical, the query selects only shapes explicitly marked `"admitted"`, and the template manufactures a consumer module that calls `GgenIgniter.RuntimeShape.new!/1`. This pack does not make generated Elixir a new source of truth and does not grant a shape DO authority.

## Semantic rails

This pack deliberately separates the three ggen semantic roles instead of reusing one file for incompatible execution paths:

1. **Projection queries** live under `queries/` and are referenced only by `[[generation.rules]]`. They are deterministic SPARQL `SELECT` queries whose rows feed templates.
2. **Admission gates** live under `gates/` and are referenced by `[validation].gates`. A gate returns rows only for violations, so generation fails closed before output is emitted when the pack vocabulary or provenance root is incomplete.
3. **GraphLaw rules** belong under `[law].rules` only when this pack has actual N3/Datalog inference or denial rules. The pack currently declares no GraphLaw rules because its existing `.rq` files are projections, not law programs.

That separation is load-bearing: a generation `SELECT` must never also appear in `[law].rules`, because ggen correctly parses law rules as N3/Datalog rather than SPARQL. Likewise, a positive projection query must not be moved into `[validation].gates`, where returned rows mean a violation. Version `26.8.29` fixes that role collision while preserving strict deterministic generation.

The pack is source-only. Consumer projections belong in consumer repositories. Process-intelligence algorithms remain outside this pack and are consumed through wasm4pm/wasm4pm-compat interfaces.
