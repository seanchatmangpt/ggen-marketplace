# CS2 Fleet Contract Pack

Reusable distribution boundary for `RFC-CS2-001`.

The canonical semantic producer remains `seanchatmangpt/ggen/examples/cs2-projections`.
This pack does not fork that ontology. It packages its generated fleet contract and
declares installation targets for marketplace, Ash A2A, and XaaS consumers.

## Dependency chain

`ggen canonical.ttl → consumers.rq → fleet-contract.json → this pack → generated consumer target`

The Elixir adapter admits only the exact subject and `CONSTRUCT` ceiling before
repository-specific bridges inspect consumer rows.

## Consumer migration

- `CS2-WRK-003` → marketplace packaged fleet contract
- `CS2-WRK-012` → `AshA2A.CS2.GeneratedFleetContract`
- `CS2-WRK-013` → `XaaS.CS2.GeneratedFleetContract`

Consumer-local copies of subject/work/target semantics should be retired after
their bridge modules point at generated projections.
