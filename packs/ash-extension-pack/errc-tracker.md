# ash-extension-pack ERRC tracker

## Cycle 1 — 2026-09-11 (consolidation of ash-extension-core-pack + ash-extension-starter-pack)

Triggered by: consolidation task on branch `feat/ash-extension-pack-consolidation`.
Builds `packs/ash-extension-pack/` as a new, standalone pack; the two source packs
(`ash-extension-core-pack`, `ash-extension-starter-pack`) are left unmodified on disk.

### What was merged

- `ontology.ttl`: the real union of both source ontologies. Every class/property from
  core-pack (`AshExtensionSpec`, `DslSection`, `SectionSchemaField`, `DslEntity`,
  `EntityArg`, `EntitySchemaField`, `FieldOneOfValue`, `Verifier`, `CompositionTarget`,
  `NestedEntity`, plus the v26.9.9/v26.9.10 scalar properties —
  `workflowReactor`/`workflowReversible`, `contextNormalize`+`contextTargetEntity`+
  `contextTargetField`, `afterTransformer`, `normalizeModule`+`normalizeFunction`,
  `provenanceSource`, `validateDelegateModule`+`validateDelegateFunction`,
  `legacyAdapterModule`+`legacyAdapterFunction`, `dualLevelFixture`) copied verbatim,
  plus every class/property from starter-pack (`ReactorStep` with `stepOf`/`stepName`/
  `stepOrder`/`stepModule`/`stepWaitFor`/`stepMaxRetries`/`stepHasCompensate`/
  `stepIsReturn`, `generatesReceiptedAction`, `receiptIdempotencyKeySource`) copied
  verbatim. Both worked fixture instances from core-pack (`AuditTrailSpec`,
  `AshR2RMLSpec`) retained verbatim.
- `gates/010_required_extension_contract.rq`, `020_schema_field_contract.rq`,
  `030_entity_identifier_contract.rq`: copied byte-identical from core-pack (confirmed
  via `diff`, zero output).
- `queries/reactor_steps.rq`, `queries/receipted_action.rq`: copied byte-identical from
  starter-pack (confirmed via `diff`, zero output) — these are referenced by template
  frontmatter and must stay byte-identical to what the (separately, concurrently built)
  templates expect.
- `templates/` is deliberately NOT touched by this cycle — built by a separate parallel
  agent in the same worktree.

### Two real conflicts resolved

1. **Competing `reactor_pipeline` templates targeting the same output path.**
   core-pack's `reactor_pipeline.ex.tmpl` hardcodes ash_r2rml's fixed five-step pipeline
   body; starter-pack's `reactor_pipeline_dynamic.ex.tmpl` generates an arbitrary
   spec-declared step DAG from `aex:ReactorStep` rows. Both would write the same
   generated module path for a spec with `aex:workflowReactor=true`. Resolution:
   starter-pack's dynamic, query-gated template is the sole winner for this pack —
   core-pack's fixed five-step template is retired and not carried into
   `ash-extension-pack` at all. See `pack.toml`'s own conflict-resolution note.
2. **The `aex:workflowReactor` vs `aex:generatesReceiptedAction` boundary.** Previously
   underspecified across the two source packs (each pack described its own property
   without stating the relationship to the other). `ontology.ttl` now carries an
   explicit comment block, placed directly above both properties, stating they are
   independent, composable capabilities — a spec may set either, both, or neither.

### Two new MUST properties added, with real citations

- `aex:installerRuntimeDep` — optional package+version-req pair (e.g.
  `"a2a ~> 0.2"`) the generated Igniter installer injects via
  `Igniter.Project.Deps.add_dep/2,3`. Real precedent:
  `/Users/sac/ash_a2a/lib/mix/tasks/ash_a2a.install.ex:58`,
  `Igniter.Project.Deps.add_dep({:a2a, "~> 0.2"})`.
- `aex:InfoGetter` (new class) with `aex:getterOf`/`aex:getterName`/
  `aex:getterSourceSection` — drives a 4-form Info-module getter (plain wrapper,
  `_result/1`, `!/1`, `?/1`, all delegating to the shared `_result/1`). Real precedent:
  `/Users/sac/ash_a2a/lib/ash_a2a/info.ex:39-45,64-71,88-99,117-120` — `capability_index/1`,
  `capability_index_result/1`, `capability_index!/1`, `capability_index?/1`.

### Three new gates added

- `gates/040_reactor_step_graph_contract.rq` — every `aex:ReactorStep`'s parent spec
  must have `workflowReactor="true"` OR `generatesReceiptedAction="true"`; among a
  spec's own `ReactorStep` rows, exactly one must have `stepIsReturn="true"` (zero or
  more than one is a violation).
- `gates/050_info_getter_quadruple_contract.rq` — every `aex:InfoGetter` has non-empty
  `getterOf`/`getterName`/`getterSourceSection`; `getterSourceSection` must resolve to a
  real `DslSection` whose own `sectionOf` equals the same `InfoGetter`'s `getterOf`
  (catches a getter wired to a section belonging to a different spec).
- `gates/060_installer_target_mode_contract.rq` — every spec with
  `dualLevelFixture="true"` has a well-formed `extensionTarget` in the closed
  `resource`|`domain` set — re-confirming gate 1's closure specifically for
  dual-fixture specs.

### New fixture

`aex:NotificationExtensionSpec` — third worked individual (alongside `AuditTrailSpec`/
`AshR2RMLSpec`), exercising the new properties together: one `aex:InfoGetter`
(`channel_index`, sourced from `NotificationExtensionSection`), one
`aex:installerRuntimeDep` (`"a2a ~> 0.2"`), `generatesReceiptedAction=true` with a
3-step `aex:ReactorStep` graph (`admit` → `deliver` → `seal_receipt`), exactly one
(`seal_receipt`) with `stepIsReturn=true`.

### Carried-forward Backlog (8 open items, verbatim from ash-extension-core-pack's
### errc-tracker.md — this consolidation does not resolve any of them)

- [ ] **[BLOCKING]** `templates/install.ex.tmpl:22-77` — the `nil ->` branch of
  `igniter/1` (no `--target` passed, i.e. the default/plain invocation) only calls
  `Igniter.add_notice` with manual instructions to add `extensions: [...]` by hand.
  The real `Igniter.Project.Module.find_and_update_module!` patch (line 71) only runs
  in the `target ->` branch. `pack.toml` claims this pack's installer "performs the
  real Igniter.Project.Module patch...so installation is one command, not a
  README-driven manual step," in explicit contrast to ash_r2rml's installer — that
  claim is false for the default invocation, reproducing the exact gap it claims to
  close.

- [ ] **[MAJOR]** `templates/install.ex.tmpl:79-83` — `add_extension/1`'s doc comment
  claims it "creates the `use Ash.X, extensions: [...]` option if absent, or
  appending to it if one already exists (never overwrites a sibling extension)." The
  actual body is a single unconditional `Igniter.Code.Common.add_code(zipper,
  "extensions: [...]", placement: :after)` call — no detect-or-append branching
  exists. The comment misdescribes the generated code's real behavior.

- [ ] **[MAJOR]** `templates/verify.ex.tmpl:40-43` — the generated `with
  {% for v in verifiers %}...{% endfor %} do :ok end` expression renders with zero
  clauses (`with  do :ok end`, invalid Elixir) when a spec has zero `aex:Verifier`
  rows. Legal per the ontology (0+ relation) but untested by either worked fixture
  (AuditTrail, AshR2RML both have >=1 verifier), so this is a latent generation
  defect for any future spec with no verifiers.

- [ ] **[MINOR]** `gates/020_schema_field_contract.rq:52` — the one_of-value-existence
  check only filters on `?s a aex:EntitySchemaField`, not `aex:SectionSchemaField`,
  even though `ontology.ttl` says `aex:sectionFieldType` shares the same closed
  vocabulary (including `"one_of"`). Also, `aex:oneOfValueOf`'s `rdfs:range` is fixed
  to `aex:EntitySchemaField` only, so there's currently no way to attach a
  `FieldOneOfValue` to a `SectionSchemaField` even if the gate were fixed — a
  two-part gap (gate + ontology range), not just a gate bug.

- [ ] **[MINOR]** `templates/composition_test.exs.tmpl:15` — header comment says the
  fixture is compiled "via `Code.eval_string/1`"; the generated body actually calls
  `Code.compile_string/1` (line 36). `compile_string/1` is in fact the correct API
  for the `[{module, binary}] = ...` destructuring used, so the generated code is
  functionally correct — only the comment is wrong.

- [ ] **[MINOR]** `templates/composition_test.exs.tmpl:48` — the per-composition-target
  test titled "composes with real `{{ t.composition_target }}` introspection" only
  asserts `function_exported?(X.Resource.Info, :type, 1)` on the library module
  itself; `fixture` is bound in the test context but never referenced. It checks the
  library is present and shaped as expected, not that the generated extension
  actually composes with it.

- [ ] **[MINOR]** `templates/extension.ex.tmpl:33-38` — the `entities` SPARQL query
  wraps `?entity_order` in `OPTIONAL` then does `ORDER BY ?entity_order`. SPARQL's
  `ORDER BY` over an unbound variable is implementation-defined. `ontology.ttl`'s own
  comment on `aex:entityOrder` says this exact ordering property exists because a
  prior parity check against ash_r2rml caught entities rendering reversed without
  it — the field being `OPTIONAL` while the render path's determinism silently
  depends on it reproduces the risk class that property was added to prevent.

- [ ] **[MINOR]** `gates/020_schema_field_contract.rq:1` — the header comment
  documents the required-property and closed-type-set checks but omits the
  one_of-value-existence rule the query body actually implements.

### Verification status — honest, not fabricated

This consolidation has **NOT** yet been verified via a real `ggen sync run` (the Rust
binary is still blocked, per both source packs' [FM-PACK-001]/[FM-PACK-002] disclosure —
`ggen 26.8.28` hardcodes `/workspace` for `[packs]` path resolution regardless of actual
cwd; not fixed by this consolidation). Verification instead goes through a separate
`ggen_igniter`-based script (`packs/ash-extension-pack/verify/render_check.exs`, run via
`cd ~/ggen_igniter && mix run <path>`), which is **another agent's real, in-progress work
this same session** — its results are not fabricated here because they do not yet exist
from this agent's vantage point. `python3 scripts/marketplace.py validate` is expected to
still fail admission at the time this file is written, since `templates/` has not yet
been populated by that parallel agent — that failure is expected, not a defect in the
files this cycle produced.
