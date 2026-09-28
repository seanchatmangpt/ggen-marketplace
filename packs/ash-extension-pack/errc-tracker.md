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

### Verification status — REAL, FINAL result (integration pass, this session)

This consolidation is **NOT** verified via a real `ggen sync run` (the Rust binary is
still blocked, per both source packs' [FM-PACK-001]/[FM-PACK-002] disclosure — `ggen
26.8.28` hardcodes `/workspace` for `[packs]` path resolution regardless of actual cwd;
not fixed by this consolidation or this integration pass). Verification instead went
through `python3 scripts/marketplace.py validate`/`catalog` (structural admission) plus
`packs/ash-extension-pack/verify/render_check.exs` (real render+compile), run via `cd
~/ggen_igniter && mix run <path>`. Both ran for real, to completion, in this session.

**`marketplace.py validate`**: PASSED. `validated packs=300 manifests=300
ontologies=451 templates=1807 native_gates=1464 verifier_gates=37 ...` — no `REFUSED:`
lines.

**`marketplace.py catalog`**: the `ash-extension-pack` entry reports `native_gates: 6`,
`templates: 8`, `ontology_files: 1` — matches the real file tree exactly.

**`render_check.exs`** (final, after integration fixes below): gates run ok 6/6, queries
run ok 2/2, **templates rendered ok 7/8**, templates with valid syntax 7/8, four-module
compile check (`extension.ex.tmpl` + `persist.ex.tmpl` + `verify.ex.tmpl` +
`info.ex.tmpl` concatenated) **`:compiles`**.

The one real, disclosed gap: `reactor_pipeline.ex.tmpl` renders 0 rows because **no
fixture in `ontology.ttl` sets `aex:workflowReactor true`** (both `AuditTrailSpec` and
`AshR2RMLSpec` set it `false`; `NotificationExtensionSpec` uses
`aex:generatesReceiptedAction` instead). This template's `{% if %}`/row-indexed/
multi-row TeraWasm constructs remain genuinely untested end-to-end pending a real
`workflowReactor=true` fixture — not fabricated as a pass. A candidate fixture was
drafted and reverted during this pass specifically because `templates/
reactor_pipeline.ex.tmpl`'s own `steps:` frontmatter query has no per-spec scoping
(`?step aex:stepOf ?spec` with no filter binding `?spec` to the current `for_each` row)
— it silently worked with exactly one `workflowReactor=true`+`ReactorStep` fixture in
existence, but a second such fixture would leak all specs' steps into every rendered
row. That is a real, separate, disclosed architectural gap in the template (not this
integration pass's script), left unfixed here rather than patched with an unverified
guess at the intended per-row scoping mechanism.

**Real integration defects found and fixed this pass** (all in the git history as a
separate commit on top of the three parallel agents' work):

1. `verify/render_check.exs` referenced four gate files by names that do not match what
   was actually built (`020_reactor_step_contract.rq` vs the real
   `020_schema_field_contract.rq`, etc.) — fixed to the real filenames confirmed via
   `find`.
2. `verify/render_check.exs`'s original context-binding strategy fed every template a
   generic superset-guess context unrelated to that template's own frontmatter
   `sparql:`/`for_each:` declarations, so all 8 templates failed to render for a
   context-mismatch reason, not a real tera/TeraWasm defect. Rewritten to run each
   template's own frontmatter queries and bind via the real production function
   `Mix.Tasks.GgenIgniter.Sync.build_bindings/2`.
3. `templates/reactor_pipeline.ex.tmpl`'s `steps:` and `templates/
   receipted_action.ex.tmpl`'s `spec:` frontmatter values were bare file-path strings
   (`queries/reactor_steps.rq`, `queries/receipted_action.rq`) — the real frontmatter
   contract (`GgenIgniter.Frontmatter`, mirroring the Rust struct) requires inline query
   TEXT for `sparql:` values, not a path reference. Fixed by inlining the real query
   text from those `.rq` files verbatim.
4. `templates/info.ex.tmpl`'s `info_getters` query selected the raw `aex:InfoGetter`'s
   section IRI (`?getter_source_section`) and the template rendered that full URI
   directly as an Elixir map key (`%{ http://...#Section: value }`) — a syntax error.
   Fixed by joining to `aex:sectionName` in the query (`?getter_source_section_name`)
   and using that atom-name value in the template body instead of the raw IRI.
5. `gates/040_reactor_step_graph_contract.rq` and `gates/
   060_installer_target_mode_contract.rq` filtered `aex:workflowReactor`/
   `aex:generatesReceiptedAction`/`aex:stepIsReturn`/`aex:dualLevelFixture` against the
   **string** literal `"true"`, but `ontology.ttl` stores these as **unquoted**
   `xsd:boolean` literals — a real type mismatch. This produced a confirmed FALSE
   POSITIVE on gate 040 (4 violation rows reported against `NotificationExtensionSpec`,
   which in fact satisfies the contract) and silently made the `receipted_action`
   query/template always return 0 rows. Fixed by removing the quotes in all five
   filter sites so the comparison is boolean-to-boolean.

### Live `ggen sync run` + compile + execute receipt (v26.9.27, 2026-09-27)

Supersedes the "NOT verified via a real `ggen sync run`" status above for the paths named
here. Branch `v26.9.27/ash-extension-pack-live-ggen`; commits d0df7f707 (templates +
consumer) and 95b58e72f (fixture + script). Replay: `scripts/ash_pack_live_fixture.sh`.

- **FM-PACK-001/002 did not reproduce** on ggen 26.9.18 (`/Users/sac/.local/bin/ggen`).
  The pack is loaded through the qualification court's own projection-profile consumer
  (`scripts/qualify_packs.py` `prepare_consumer`: consumer `ggen.toml` with
  `[packs] "ash-extension-pack" = { path = ... }` plus `qualification/consumer.ttl`).
  No pack-level `ggen.toml` was added: that would switch the pack to the `project`
  profile. `qualify_packs.qualify_pack` on this pack returns `status: ALIVE`.
- **Gate refusal witnessed**: a consumer spec without `aex:extensionTarget` made ggen
  refuse the sync with `[FM-PACK-013] ... gate 010_required_extension_contract.rq
  refused the sync against the union graph`.
- **`qualification/consumer.ttl`** adds `PipelineProbeSpec` (`workflowReactor true` +
  `generatesReceiptedAction true`, key source `caller_supplied`) with three
  `aex:ReactorStep` rows (admit -> deliver -> seal, `seal` the only return step). This
  closes the "reactor_pipeline renders 0 rows" gap above.
- **Template defects found by the live run and fixed at source**:
  1. `reactor_pipeline.ex.tmpl` `steps:` had no per-spec scoping (the gap disclosed
     above): the first live render gave `pipeline_probe` a duplicate `:deliver` and
     notification_extension's `:seal_receipt`. ggen evaluates named `sparql:` results
     once per template, not per `for_each` row, so the query now selects
     `?package_name` and the body filters on it (`queries/reactor_steps.rq` mirrored).
  2. `reactor_pipeline.ex.tmpl` compared `step.is_return == "true"`; ggen 26.9.18 binds
     `xsd:boolean` as a JSON bool, so no `return` clause was ever rendered. Both forms
     are now accepted. `max_retries 0` is now emitted (was dropped as falsy).
- **Recorded, NOT fixed here** (file owned by the concurrent receipted-action lane):
  `receipt.ex.tmpl` renders `@table :"pipeline_probe_receipts"`, a quoted atom Elixir
  1.20 warns on. Needed change: `@table :"{{ package_name }}_receipts"` ->
  `@table :{{ package_name }}_receipts`. The script allows exactly that warning
  (`generated/pipeline_probe/receipt.ex:17`), refuses any other project warning, and
  fails once the fix lands so the allowance gets deleted.
- **Determinism** (run on a `git archive` of 95b58e72f): `ggen sync run` twice, 29
  generated files, sha256 manifests byte-identical, manifest digest
  `464f3894ccef4c866e28f5c20f62dc1edaba53ea9491e82e66dc1081efa3baa6`. Files under test:
  `lib/pipeline_probe/reactor_pipeline.ex`
  `a068548b459171b53df0704a2b631af2ab30d0bb3f5b962611f52892a1432b96`,
  `receipt.ex` `90a1f48830db23566759258ec950c3079e509cef9b298f5213ad3ce8ba68706e`,
  `receipted_action.ex` `daab870bd4971375eaac507dd659cb89d52d2d509c787945125e17d79d1abff0`.
- **Compile + execute**: `fixture/` (ash 3.33.11, reactor 1.0.7, spark 2.7.3; Elixir
  1.20.2 / OTP 28 via asdf) compiles the 8 project files (5 consumer, 3 generated) with
  no warning besides the allowance; an injected unused variable in a consumer step is
  refused (`REFUSED:ASH_PACK_FIXTURE_COMPILE_WARNINGS lib/pipeline_probe/steps/admit.ex:11`).
  `mix test`: 5 passed (repeated 5x). Covered: same key + same payload -> the sealed
  receipt returned with `status: :replayed`, one row; same key + different payload ->
  `{:error, {:idempotency_conflict, key}}`; missing key refused; failed action -> `:failed`
  receipt, then re-admitted; the Reactor pipeline runs admit, deliver, seal in order and
  returns `:seal`. Mutation witness: deleting the generated `wait_for`/`return` lines makes
  the order test fail (observed `[:seal, :admit, :deliver]`, `[:deliver, :admit, :seal]`,
  `[:admit, :seal, :deliver]`).
- **Still UNVERIFIED**: resource.ex / info.ex / persist.ex / verify.ex / install.ex and
  the composition tests are generated and hashed but not compiled by the fixture; their
  `sections:`/`entities:` queries lack the same per-spec scoping reactor_pipeline had, so
  a multi-spec graph mixes DSL sections across specs. Reactor step modules are
  consumer-owned (no template generates them). pack.toml's description still says the
  source packs are "left on disk unmodified"; they were deleted in 9e9c23875. That
  correction is not applied because pack.toml is being edited by the concurrent lane.
