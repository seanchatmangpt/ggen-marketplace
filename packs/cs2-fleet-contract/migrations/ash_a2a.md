# Ash A2A migration

Canonical target: `lib/ash_a2a/cs2/generated_fleet_contract.ex`.

1. Materialize the ggen `cs2-ash-a2a-fleet-contract` projection.
2. Install it at the canonical target path.
3. Route FleetAdapter/XaasBridge lookups through the generated module.
4. Delete consumer-local subject/work/target constants after callers migrate.

The generated module is a projection. It does not confer DO authority or standing.
