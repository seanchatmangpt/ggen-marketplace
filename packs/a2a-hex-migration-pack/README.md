# a2a-hex-migration-pack

Regenerable migration capital for the `{:a2a, "~> 0.2"}` hex package
(a2a-elixir 0.3.0 lineage) onto ash_a2a v26.10.3's vendored protocol surface
(`AshA2A.Protocol.*` under `lib/ash_a2a/protocol/`).

The single authority is ash_a2a's migration guide,
`docs/how-to/migrate-from-a2a-hex.md`. This pack is a projection of that
guide -- where pack and guide disagree, the guide wins and the pack is
regenerated.

## Contents

- `pack.toml` -- pack identity; names ash-extension-pack as the format reference.
- `ontology.ttl` -- `MigrationSpec`, 5 `MigrationStep`s (each citing the guide
  section that defines it), 9 `ModuleMapping`s (the guide's verified table),
  4 `WireShapeDelta`s (guide section 2).
- `templates/migration_task.ex.tmpl` -- renders
  `lib/mix/tasks/a2a_hex_migrate.ex` into the consumer project: removes the
  `{:a2a, ...}` dep from `mix.exs`, applies the 9 verified literal mappings
  longest-first across `lib/ test/ config/`, renames any outside-table `A2A.`
  ref generically at a word boundary and FLAGS it as unverified, prints the
  wire-shape delta checklist and the migration steps, then runs the guide's
  section-7 sweep and refuses (exit 1) on any residual.
- `queries/` -- step, mapping, and delta listings.
- `gates/` -- violation-returning SPARQL gates (empty = pass):
  - `010_mapping_table_covers_guide_modules.rq` -- the template's rendered
    mapping table must cover every module the guide lists (A2A.Message /
    A2A.Part / A2A.Plug / A2A.Plug.Auth / A2A.AgentSupervisor / A2A.Agent);
  - `020_every_step_cites_guide_section.rq` -- every step cites the exact
    numbered guide heading;
  - `030_mapping_grounding_contract.rq` -- every mapping is grounded under
    `lib/ash_a2a/`.
- `falsifier/` -- the guide's own pass gate, run for real: the generated task
  ran on a scratch consumer and its sweep reported zero A2A. refs (see
  `falsifier/README.md`).

## Sibling-repo notes (guide section 5)

These are sibling-repo edits, tracked there -- the pack only records them.

### xaas

The xaas rehearsal finding: xaas still needs `{:a2a, "~> 0.2"}` as an
independent direct dep, OR the Zoe-agent path gets ported to the vendored
surface -- it is not covered by pinning the new ash_a2a alone. Grounding:
`/Users/sac/xaas/mix.exs:111` pins `{:a2a, "~> 0.2"}` alongside the pinned
ash_a2a git ref 3325032d9dea201e6deb82ef242c534aacb3b420 (mix.exs:103-105);
`/Users/sac/xaas/lib/xaas_web/a2a/zoe_event_plug.ex:3,10,13` calls `A2A.Plug`
directly (init/call delegation), and `lib/xaas_web/router.ex:205` forwards to
that plug. Removing `:a2a` without porting the Zoe path breaks the
Zoe event-simulation agent's HTTP surface.

### ggen_igniter

`test/ggen_igniter_semantic_a2a_manufacture_test.exs:66-68` asserts the
installer ADDED `{:a2a, "~> 0.2"}`; once the sibling pins the new ash_a2a the
assertion flips to asserting the dep is absent (guide section 5). The dispatch
test (`test/ggen_igniter_semantic_a2a_dispatch_test.exs:44-56`) still aliases
`A2A.Plug.Auth` / `A2A.Plug` / `%A2A.SecurityScheme.HTTPAuth{}` -- the pack's
generic rename covers those (`A2A.SecurityScheme` -> `AshA2A.Protocol.SecurityScheme`,
`lib/ash_a2a/protocol/security_scheme.ex`).

## Run

In the consumer project, render the pack and run:

    mix a2a_hex_migrate          # rewrites; refuses on any residual
    mix a2a_hex_migrate --dry-run   # plain-branch: prints planned rewrites only

## Falsifier

The guide's own pass gate: the generated task runs on a scratch consumer and
its sweep reports zero A2A. refs. Receipt: `falsifier/README.md`.
