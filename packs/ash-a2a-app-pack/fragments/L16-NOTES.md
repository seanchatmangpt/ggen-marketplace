# L16 notes: ash_pplan

Standing: UNVERIFIED

## Seam (no `fragments:` line)

ash_pplan is not an Ash.Resource DSL. `AshPPlan.Workflow` (`use Spark.Dsl`,
workflow.ex:25) and providers are standalone modules, so L16 emits standalone modules, not Spark
fragments. Coordinator adds NO `fragments: [...]` entry. Required wiring:

- mix.exs deps: `{:ash_pplan, path: "/Users/sac/ash_pplan"}` (or the hex dep); needs reactor.
- `Demo.Desk.Plan.*` modules compile once ash_pplan is a dep. Resource fragments untouched.
- ControlPlaneL16 per resource is `<Resource>.ControlPlaneL16` (separate module, not a fragment).

## Outputs

| template | output |
|---|---|
| L16_pplan_workflow.ex.tmpl | lib/<app_path>/pplan/<ppFile>.ex |
| L16_pplan_provider.ex.tmpl | lib/<app_path>/pplan/<ppFile>.ex |
| L16_pplan_capability_pack.ex.tmpl | lib/<app_path>/pplan/<ppFile>.ex |
| L16_pplan_control_plane.ex.tmpl | lib/<app_path>/<resourceFile>_control_plane_l16.ex |
| L16_pplan_manufacture_targets.ex.tmpl | lib/<app_path>/pplan/manufacture_targets_l16.ex |
| L16_pplan_court_test.exs.tmpl | test/<app_path>/pplan/<ppFile>_test.exs |

Unique `ppFile` per workflow/provider/pack within one domain or outputs collide.

## Reuse by reference

`aap:ppReusesPack` records ash-pplan-igniter-pack, -protocol-court-pack, -store-conformance-pack,
-chaos-pack on the Domain; surfaced in `ManufactureTargetsL16.packs/0`. Nothing copied.

## Known gaps

- Obligations are a pack-local construct; ash_pplan has no obligation DSL. They are enforced by
  gates 060/061 and the generated court test only.
- FOND/HTN/POWL: only `method` (HDDL) and outcomes are DSL-expressible (dsl entities). FOND
  (fond.ex), HTN (htn.ex), POWL (powl.ex) are runtime projections of the Model; no TTL surface yet.
- AshOban/AshStateMachine are not generated here; ControlPlane only verifies them if the
  resource already carries those extensions (another lane's fragments).
- `AshPPlan.Dsl` (`pplan` section) lacks `compensation:`; the template uses `AshPPlan.Workflow`.
- `Model.authorities` includes `:plan`, the DSL verifier list (capabilities_parse.ex:9) does not.
  Gate 040 admits `plan` per model/qualify; drop it if the verifier is authoritative.
- `GROUP_CONCAT` ordering of after/outcomes/properties is engine-defined; model normalizes sort.
- Adapter names must be keys of `AshPPlan.Reactor.adapters/0`; not gated (config-dependent).
- Custom capability families (`AshPPlan.Config.extra_capability_families`) fail gate 040.
- Not compiled or synced; query/template syntax unrun.
