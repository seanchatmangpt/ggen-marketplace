# Ash Runtime Integration Contract Pack

Deterministic GGen source for generating Ash/Reactor runtime seams from admitted RDF facts. The pack binds exact subjects, authority, runtime actions, RuntimeShape semantic identity, receipts, replay, refusals, OCEL evidence, persistence, API/CLI surfaces, and failure semantics without granting model or planner output ambient execution authority.

`RuntimeShape` is the CONSTRUCT-time bridge into `GgenIgniter.RuntimeShape`: the ontology remains canonical, the query selects only shapes explicitly marked `"admitted"`, and the template manufactures a consumer module that calls `GgenIgniter.RuntimeShape.new!/1`. This pack does not make generated Elixir a new source of truth and does not grant a shape DO authority.

The pack is source-only. Consumer projections belong in consumer repositories. Process-intelligence algorithms remain outside this pack and are consumed through wasm4pm/wasm4pm-compat interfaces.
