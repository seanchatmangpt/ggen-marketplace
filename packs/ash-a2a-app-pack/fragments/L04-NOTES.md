# L04 aggregates notes

Standing: UNVERIFIED

## Seam

Per resource that has `aap:aggregate`, `templates/L04_aggregates.ex.tmpl` writes
`lib/<app_path>/<resource_file>_l04.ex` defining `<Module>Aggregates`
(`use Spark.Dsl.Fragment, of: Ash.Resource`). Coordinator adds to the resource template's
`use Ash.Resource` options (only for resources that have aggregates):

    fragments: [{{ module_name }}Aggregates]

(the line is `fragments: [Helpdesk.Support.TicketAggregates]` for the fixture). The fragment's
`aggregates` section imports Ash.Expr itself, so `expr(...)` in filters works.

## Vocabulary (ontology.d/L04-aggregates.ttl)

Resource `aap:aggregate` Aggregate; Aggregate props: `aap:name`, `aggKind`, `aggPath`
(comma list, no spaces) XOR `aggResource` (module), `aggField`, `aggType`, `aggImplementation`,
`aggFilter`, `aggSort`, `aggDefault` (raw Elixir strings), `aggDescription`, `aggPublic`,
`aggUniq`, `aggIncludeNil`, `aggReadAction`, `aggFilterable`, `aggSortable`, `aggSensitive`,
`aggAuthorize`, `aggMultitenancy`, `aggJoinFilter` -> node(`aggPath`, `aggFilter`).
Booleans are string literals "true"/"false" (existing pack convention).

## DSL citations

ash/lib/ash/resource/dsl.ex: count 1377, first 1415, max 1449, min 1475, sum 1501, avg 1527,
exists 1553, custom 1578, list 1618, join_filter 1353, section 1657.
ash/lib/ash/resource/aggregate/aggregate.ex: option schema 39-125, path/resource transform 152-169.

## Gates

- L04_010 shape/option applicability; L04_020 unknown path segments (3 hops); L04_030 duplicate
  names, attribute collision, aggField not on single-hop destination.

## Cross-lane assumption

Gates 020/030 need `aap:relationship [aap:name; aap:destination]` on resources. L04 declares
those two terms minimally; if the relationships lane mints different terms, rename in
gates/L04_020 and L04_030 (or alias in the shared ontology).

## Known gaps

- aggField not checked for multi-hop or resource-based aggregates; paths > 3 hops flagged only.
- Filter/sort/default/implementation are raw Elixir strings, not validated.
- Description is not escaped for embedded double quotes.
- Aggregates are not auto-exposed as a2a skill outputs or calculations-from-aggregates.
- Ash `aggregates` referencing other aggregates by path (nested aggregate fields) unmodeled.
- Template not run; Tera `default` + `!=` precedence is UNVERIFIED until coordinator sync.
