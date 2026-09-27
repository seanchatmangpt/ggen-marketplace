# CS2 semantic work pack

Canonical semantic projection pack for CS2 work.

The pack owns the producer-side representation only: exact subject, exact Git source binding, work identity, dependency edges, path scope, requested projections, acceptance/falsifier text, and an explicit `authority = NONE` fence.

## Projection surfaces

- `work-projection.schema.json` / `work-projection.json.tera`: one projected work item.
- `work-projection-batch.schema.json` / `work-projection-batch.json.tera`: a dependency-connected batch consumed by `ggen_igniter`.
- `project_work.rq`: deterministic work projection.
- `project_dependencies.rq`: deterministic dependency projection.
- gates 010–080: exact-subject/source/authority/identity/dependency refusals.

The pack does **not** manufacture Semantic-Jira standing, runtime leases, execution authority, or XaaS actuation. Consumers expand this source-bound projection at their own admission boundaries.
