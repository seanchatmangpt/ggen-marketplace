# CS2 semantic work pack

Canonical semantic projection pack for CS2 work (v26.9.27).

The pack owns the producer-side representation only: exact subject, exact Git source
binding, work identity, dependency edges, path scope, requested projections,
acceptance/falsifier text, and an explicit `authority = NONE` fence.

## Rendered surfaces (ggen `templates/**/*.tmpl`)

Every surface is a ggen frontmatter template; its SPARQL is inline in the frontmatter
(the single source for that projection). All output lands under
`generated/cs2-semantic-work/`.

- `templates/json/work-projection.json.tmpl` -> `work/<workKey>.json`, one per
  `cs2:WorkItem` (`schemas/work-projection.schema.json`).
- `templates/json/work-projection-batch.json.tmpl` -> `work-projection-batch.json`,
  rendered only when the graph holds a `cs2:WorkBatch`
  (`schemas/work-projection-batch.schema.json`).
- `templates/consumer/consumer-<kind>.json.tmpl` -> `consumer/consumer-<kind>.json`
  for kind in work, source, dependency, path, projection, admission, batch, roots
  (`consumer/schemas/consumer-*.schema.json` where one exists).
- `templates/elixir/consumer_adapter.ex.tmpl` -> batch admission adapter
  (module from `cs2:ConsumerAdmission cs2:elixirModule`, subject from
  `cs2:WorkProjection cs2:canonicalSubject`).
- `templates/elixir/consumer.ex.tmpl` -> single-projection admission
  (`cs2:ConsumerProjection cs2:elixirModule`).
- `templates/elixir/consumer_work.ex.tmpl` -> typed consumer rows
  (`Work`, `Admission`, `Source`, `Dependency`, `Projection`, `Batch`;
  `cs2:ConsumerWork cs2:elixirModule`).

## Gates

`gates/010`-`095` are ggen pack gates (violation-row SELECT, `FM-PACK-013`): exact
subject, source binding, authority NONE, unique work key, single subject, single
source binding, dependency target exists, no self dependency, acyclic, authority
cardinality. `fixtures/refused-*.ttl` each fire a gate; `fixtures/valid-work.ttl` and
`qualification/consumer/cs2-batch.ttl` pass.

UNSUPPORTED (ggen enforcement): `consumer/gates/*.rq` are ASK-form consumer contracts
that also require `pathScope`/`projectionType`/`originAuthority` on every work item.
ggen only runs `gates/*.rq`, and promoting them would refuse producer-only items such
as `fixtures/valid-work.ttl`, so they are shipped as consumer-side contracts with
`consumer/fixtures/`, not enforced during `ggen sync run`.

## Qualification

`qualification/consumer/cs2-batch.ttl` is the qualification consumer graph (two work
items, one dependency edge, one batch); `qualification/consumer.json` is the expected
`work/CS2-WRK-003.json` projection.

The pack does **not** manufacture Semantic-Jira standing, runtime leases, execution
authority, or XaaS actuation. Consumers expand this source-bound projection at their
own admission boundaries.

## Live Elixir fixture

`scripts/cs2_pack_live_fixture.sh` builds the qualification consumer with
`qualify_packs.prepare_consumer`, runs `ggen sync run` twice (sha256 byte-identical
check), copies `generated/cs2-semantic-work` verbatim into a capsule outside the pack,
and runs `mix deps.get && mix compile --warnings-as-errors && mix test` in `fixture/`
(`_build`/`deps` also live in the capsule). The tests read only the generated JSON
and modules: batch admission, duplicate key / unknown or self dependency / foreign
subject / `DO` authority / short SHA / empty batch refusals, per-item projection
admission, and the typed `ConsumerWork` modules over the consumer JSON rows.
