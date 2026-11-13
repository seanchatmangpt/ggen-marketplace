# L20 notes: courts

Standing: UNVERIFIED

## Seam

Courts are tests and scripts, not Ash DSL. No `fragments: [...]` line is required.
Outputs: `test/courts/*_test.exs`, `scripts/shim_court/<name>.sh`.

## Coordinator actions

- mix.exs deps (test only): `{:stream_data, "~> 1.1", only: [:test, :dev]}`. `ExUnitProperties`
  and `Ash.Generator.action_input/3` need it. ash_pplan dep needed for plan courts
  (`{:ash_pplan, "~> 26.10", only: :test}`); reactor courts need `:reactor`.
- test_helper stays `ExUnit.start()`.
- Fixture `fixtures/L20-courts.ttl` is self-contained; case classes assume other lanes emit the
  declarations (policies, identity `unique_title`, status attribute, `close` update action).
  A failing policy/identity/transition court there is a real finding, not a template defect.
- Shim script env: `SHIM_ROOT` (project root, default two dirs above script), `GGEN_SYNC_CMD` +
  `SHIM_PACK_ROOT` to mutate the pack template and regenerate; otherwise the generated file is
  mutated. Exit 0 PASS, 1 FAIL (incl. VACUOUS), 2 restore mismatch, 3 loud SKIP.
- Run all: `for s in scripts/shim_court/*.sh; do bash "$s" || exit 1; done`.

## DSL/API options covered (file:line)

- Dispatcher.dispatch/6: ash_a2a/lib/ash_a2a/dispatcher.ex:164-171; reply union :113-125;
  auth_identity semantics :145-154.
- FOND.new/2 ash_pplan/lib/ash_pplan/fond.ex:47-57, check/1 :71; Synthesis.synthesize/3
  ash_pplan/lib/ash_pplan/fond/synthesis.ex:70-81, modes :56.
- Ash.Generator.action_input/3, Ash.can?/3, Ash.Resource.Info.action/attribute/relationship/identity.
- Relationship court reads L02 vocab (aap:relationship, relKind, destination, aap:name).

## Gates

L20_040 unknown ashType; 041 duplicate moduleName; 042 duplicate action/skill name;
043 agent without domain; 044 resource without domain; 045 dangling court case action;
046 expect vocabulary; 047 generated path collision.

## Known gaps

- Transition court assumes pk attribute `id` (`Ash.get(@resource, seed.id)`).
- Policy court tests `Ash.can?` with `maybe_is: false`; filter-based policies on create inputs not
  modelled. Actor terms are raw Elixir.
- Reactor undo probe is a raw boolean expression; no per-step compensation introspection.
- No court yet for calculations/aggregates/multitenancy (L03/L04/L08 vocab not consumed).
- ashType whitelist in gate 040 is a hand-curated builtin list; custom types go via aap:ashTypeModule.
- Nothing compiled or run (no shell): Tera rendering and `validate_policy/4` arity unverified.
