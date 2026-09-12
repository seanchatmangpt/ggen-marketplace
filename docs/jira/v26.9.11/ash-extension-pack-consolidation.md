# ash-extension-pack: consolidate core-pack + starter-pack ontology/gates/queries

## Summary

Consolidated `packs/ash-extension-core-pack/` and `packs/ash-extension-starter-pack/`
into a new pack, `packs/ash-extension-pack/`, unifying ontology, gates, queries, and
templates under the shared `aex:` namespace. The two source packs were left untouched.
Work was split across parallel agents (ontology+gates+queries; templates/;
verify/render_check.exs) in one shared worktree, followed by an integration pass that
found and fixed real defects surfaced by an actual render run.

## Status

Done — already merged/committed (4 commits, this branch/worktree).

## Commits

- `c16ab7d03` fix(ash-extension-pack): integration pass -- real render_check.exs pass, boolean-literal gate fix
- `74d92be52` feat(ash-extension-pack): consolidate core-pack + starter-pack ontology/gates/queries
- `da0e79894` feat(ash-extension-pack): add render_check.exs verification script
- `a5ef7c613` feat(ash-extension-pack): create consolidated templates/ (8 files)

## Changes

### `74d92be52` — ontology/gates/queries consolidation
- New pack `packs/ash-extension-pack/` (`pack.toml`, name=ash-extension-pack,
  version=0.1.0). Source packs left untouched.
- `ontology.ttl`: real union of both source ontologies under the shared `aex:`
  namespace (no new namespace forked). Retains `AuditTrailSpec` and `AshR2RMLSpec`
  fixtures verbatim.
- Adds two new real, cited properties: `aex:installerRuntimeDep` (cites
  `Igniter.Project.Deps.add_dep` precedent, `ash_a2a.install.ex:58`) and the
  `aex:InfoGetter` class (cites the 4-form Info-module getter precedent in
  `ash_a2a/info.ex`).
- Adds an explicit comment clarifying `workflowReactor` and
  `generatesReceiptedAction` are independent, composable capabilities.
- Adds a new worked fixture, `aex:NotificationExtensionSpec`, exercising all three
  additions together (one InfoGetter, one installerRuntimeDep,
  `generatesReceiptedAction=true` with a 3-step ReactorStep graph, exactly one
  `stepIsReturn=true`).
- `gates/010,020,030`: byte-identical copies of core-pack's gates (confirmed via
  diff). `gates/040,050,060`: three new gate queries (ReactorStep parent capability
  + exactly-one-is_return check; InfoGetter quadruple-contract check;
  dualLevelFixture extensionTarget closure re-check).
- `queries/reactor_steps.rq`, `queries/receipted_action.rq`: byte-identical copies
  of starter-pack's queries (confirmed via diff).
- `errc-tracker.md`: carries forward all 8 open backlog items from
  ash-extension-core-pack's tracker verbatim; documents this cycle's merge/
  conflict-resolution work; discloses that ggen sync run verification (Rust
  binary) had not happened yet at this point, pending the parallel
  render_check.exs work.
- Resolves two real conflicts between the source packs: the `reactor_pipeline`
  template collision (starter-pack's dynamic template wins) and the
  `workflowReactor` vs `generatesReceiptedAction` independent-composable
  clarification.

### `a5ef7c613` — consolidated templates/ (8 files)
- Verbatim copies/renames (6): `extension.ex.tmpl`, `persist.ex.tmpl`,
  `verify.ex.tmpl`, `composition_test.exs.tmpl` (from ash-extension-core-pack,
  unchanged); `receipted_action.ex.tmpl` (from ash-extension-starter-pack,
  unchanged); `reactor_pipeline.ex.tmpl` (renamed from starter-pack's
  `reactor_pipeline_dynamic.ex.tmpl`, content unchanged — resolves the file-path
  collision with core-pack's own fixed-5-step `reactor_pipeline.ex.tmpl`, which is
  intentionally not copied).
- Additive-only extensions (2) over core-pack's originals:
  - `info.ex.tmpl`: adds an `info_getters` SPARQL frontmatter query
    (`aex:InfoGetter`/`aex:getterOf`/`aex:getterName`/`aex:getterSourceSection`) and
    a real 4-form block per getter (`<name>/1`, `<name>_result/1`, `<name>!/1`,
    `<name>?/1`) mirroring `ash_a2a/lib/ash_a2a/info.ex`'s capability_index 4-form
    shape; the original generic `compiled/1` 4-form block is untouched.
  - `install.ex.tmpl`: adds a `--type` schema option (`defaults: [type: "resource"]`)
    gated on `aex:dualLevelFixture = "true"`, and a real
    `Igniter.Project.Deps.add_dep/2` pipe call gated on `aex:installerRuntimeDep`,
    mirroring `ash_a2a/lib/mix/tasks/ash_a2a.install.ex`'s real `--type`/`--target`
    and `add_dep` shapes; unset/false on either property renders byte-identical to
    core-pack's original `install.ex.tmpl`.

### `da0e79894` — render_check.exs verification script
- Adds `packs/ash-extension-pack/verify/render_check.exs`, a self-contained Elixir
  script (403 lines) run via `mix run <path>` inside `ggen_igniter`'s compiled Mix
  project, exercising `Ontology.load!` -> `Query.Oxigraph.run` ->
  `Frontmatter.split_template` -> `Render.TeraWasm.render` against the pack's real
  `ontology.ttl`, gates 010-060, `queries/*.rq`, and `templates/*.tmpl`.
- Defensive by design: a missing referenced file prints `MISSING: <path>` and is
  skipped rather than crashing, since sibling agents were still writing
  ontology/gates/templates concurrently in the same worktree.

### `c16ab7d03` — integration pass (real defects found and fixed)
- `render_check.exs` referenced 4 gate files by names that didn't match what was
  actually built (e.g. `020_reactor_step_contract.rq` vs the real
  `020_schema_field_contract.rq`) — fixed to the real filenames.
- `render_check.exs`'s context-binding strategy fed every template a generic
  superset-guess context unrelated to that template's own frontmatter
  `sparql:`/`for_each:` declarations, causing all 8 templates to fail to render for
  a context-mismatch reason rather than a real TeraWasm defect. Rewritten to run
  each template's own frontmatter queries and bind via the real production
  function `Mix.Tasks.GgenIgniter.Sync.build_bindings/2`.
- `templates/reactor_pipeline.ex.tmpl`'s `steps:` and
  `templates/receipted_action.ex.tmpl`'s `spec:` frontmatter values were bare
  file-path strings, but the real frontmatter contract requires inline query text.
  Fixed by inlining the real query text from the corresponding `.rq` files
  verbatim.
- `templates/info.ex.tmpl`'s `info_getters` query selected a raw section IRI, which
  the template rendered as a full URI used as an Elixir map key (syntax error).
  Fixed by joining to `aex:sectionName` in the query and using the resolved
  atom-name value in the template body.
- `gates/040_reactor_step_graph_contract.rq` and
  `gates/060_installer_target_mode_contract.rq` filtered boolean properties
  against the string literal `"true"`, but `ontology.ttl` stores these as unquoted
  `xsd:boolean` literals — a type mismatch that produced a confirmed false
  positive on gate 040 (4 rows against `NotificationExtensionSpec`, which actually
  satisfies the contract) and made `receipted_action`'s query/template always
  return 0 rows. Fixed by removing the string quotes at all 5 filter sites.
- Disclosed, unfixed gap: `reactor_pipeline.ex.tmpl` renders 0 rows because no
  fixture in `ontology.ttl` sets `aex:workflowReactor=true`. A candidate fixture
  was drafted and reverted during this pass because the template's own `steps:`
  query has no per-spec scoping (`?step aex:stepOf ?spec` with no binding to the
  current `for_each` row) — it worked with exactly one existing
  `workflowReactor=true`+`ReactorStep` fixture, but a second one would leak all
  specs' steps into every rendered row. Left unfixed rather than patched with an
  unverified guess at the intended per-row scoping mechanism.
- Confirmed untouched: `packs/ash-extension-core-pack/` and
  `packs/ash-extension-starter-pack/` (`git diff --stat main` for both paths was
  empty).

## Verification

- `74d92be52`: `python3 scripts/marketplace.py validate` passes (300 packs, 451
  ontologies, 1807 templates, no errors). `pack.toml` parses via `tomllib`. All 8
  new/copied `.rq` files have balanced braces (grep-verified).
- `da0e79894`: real trial run of `render_check.exs` against the then-partial pack
  state (ontology.ttl not yet present) completed without a script-level exception,
  correctly reporting `MISSING:` lines and honest `{:error, _}` render results
  driven by empty context — no fix needed to the script's own Elixir code after
  the trial run.
- `c16ab7d03` (final integration verification, both run to completion in that
  session):
  - `python3 scripts/marketplace.py validate`: PASSED, no REFUSED lines.
  - `python3 scripts/marketplace.py catalog`: ash-extension-pack entry reports
    `native_gates=6`, `templates=8`, `ontology_files=1` — matches the real file
    tree.
  - `mix run packs/ash-extension-pack/verify/render_check.exs` (from
    `~/ggen_igniter`): gates run ok 6/6, queries run ok 2/2, templates rendered ok
    7/8, templates with valid syntax 7/8, four-module compile check `:compiles`.
  - Disclosed unfixed gap (see Changes above): `reactor_pipeline.ex.tmpl` renders 0
    rows for lack of a `workflowReactor=true` fixture; not fixed this pass.

No CI run output is stated in any of the four commit messages — verification
evidence above is the real local command output cited in each commit body, not CI.

## Related

No PR numbers or branch names are stated in any of the four commit subjects/bodies.
All four commits cite the same session: `https://claude.ai/code/session_01Q9CxAziKRC59z9Z1YVQ2NW`.
