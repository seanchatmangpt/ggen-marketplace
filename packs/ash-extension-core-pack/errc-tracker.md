# ash-extension-core-pack ERRC tracker

## Cycle 3 — 2026-09-09 (RAISE + CREATE, to v26.9.9)

Triggered by user direction: "this pack should be what allows existing extensions to
use best practices and ERRC" -- reframes this pack's purpose from "generate new Ash
extensions" to "the standing best-practices vocabulary an EXISTING hand-written
extension is graded against and raised to." A background Workflow ran 3 parallel
research agents against real source (not memory, not the prior session's claims) --
`/Users/sac/xaas/deps/ash_ai` (ResourceTools transformer + Tool entity + execution
context threading), `/Users/sac/ash_r2rml` (Persist/Verify/Info/Reactor/install task),
`/Users/sac/xaas` (idempotency wrapper, real multi-extension stacking, mix.exs deps) --
plus a synthesis agent ranking 10 candidate capabilities the user's own plan proposed.
Full per-agent JSON reports and the synthesis memo: workflow run `wf_1740f3f0-7b3`,
journal at the session's `subagents/workflows/wf_1740f3f0-7b3/journal.jsonl`.

**Correction to the triggering plan (rule: re-derive on correction, don't carry a
prior conclusion forward):** the plan asserted ash_r2rml's installer uses
`Spark.Igniter.add_extension` plus "AST-aware idempotent block insertion." Direct read
of `lib/mix/tasks/ash_r2rml.install.ex` found zero references to `Spark.Igniter`
anywhere in the file and no `Igniter.Project.Module`/`Sourceror`/zipper-based
detection of an existing DSL block -- it only wires the formatter plugin
(`Igniter.Project.Formatter.import_dep`/`add_formatter_plugin`) and unconditionally
emits a static `Igniter.add_notice` telling the user to hand-edit. This pack's
existing `--target`-conditional real `Igniter.Project.Module` patch is already ahead
of the golden specimen on that axis. Not implemented as "modernize past ash_r2rml"
since the golden specimen does not exhibit the claimed pattern — see pack.toml's
v26.9.9 note.

**RAISE (implemented, existing extensions can now be regenerated/graded against
these):**
- `aex:contextNormalize`/`contextTargetEntity`/`contextTargetField` — resource/domain
  context-normalization transformer, the real `AshAi.Transformers.ResourceTools`
  pattern (`resource_tools.ex:13-55,125-127`, `@spark_is` module-attribute detection,
  implicit fill-in / explicit-reject / explicit-require cond). `templates/persist.ex.tmpl`.
- `aex:afterTransformer` — explicit `after?/1` clauses against real upstream Ash core
  transformers, verbatim `ash_r2rml/lib/ash_r2rml/resource.ex:188-194`'s five clauses
  (CachePrimaryKey/DefaultPrimaryKey/SetRelationshipInformation/BelongsToAttribute/
  BelongsToSourceAttribute). `templates/persist.ex.tmpl`.
- `aex:dualLevelFixture` — composition_test compiles a resource AND a domain fixture,
  each stacked with 2+ co-resident extensions, mirroring the real xaas exemplar
  (`lib/xaas/library.ex:8` domain + `lib/xaas/library/book.ex:36` resource, both
  stacking `AshAi` alongside `AshJsonApi`/`AshGraphql`/`AshAdmin`). `templates/composition_test.exs.tmpl`.

**Named, ranked lower by the synthesis agent, not yet built (still real gaps against
ash_r2rml's exact shape, cited for the next cycle):**
- Persist's `normalize/1` pre-persist pass + `metadata: {..., source: :ash_first}`
  provenance sub-map (`ash_r2rml/lib/ash_r2rml/resource.ex:197-249`) — current pack's
  `:{package}_compiled` persist has no equivalent normalize step or provenance field.
- Verify's exact 2-branch shape: nil-check stays inline, but business validation
  delegates to a *separate module's* `validate/1` and joins refusals as
  `Enum.map_join(refusals, "; ", &"#{&1.code}: #{&1.detail}")`
  (`resource.ex:486-512`) — current template's verifier stubs are inline, not
  delegate-and-join.
- Info's rescue-to-legacy-adapter fallback idiom on the result-tuple getter
  (`resource.ex:527-534`, `rescue _ -> Module.LegacyAdapter.convert(resource)`).
- Nested DSL entity support (`ax:NestedEntity`, ash_ai's `@tool` → `arguments: [@tool_argument]`,
  `dsl.ex:228-268`) — needed for any extension whose entities themselves take
  entity-typed children, not yet modeled in this pack's `aex:DslEntity` vocabulary.
- `Code.ensure_loaded?/1`-guarded optional-module generation (ash_r2rml gates its
  whole `igniter/1` branch on `Code.ensure_loaded?(Igniter)`; xaas gates `ReqLLM` the
  same way) — no ontology property yet for "this generated code path is optional."

**Verification status:** ontology + template edits are source-cited but UNVERIFIED
against a real `ggen sync run` with a fixture spec exercising `contextNormalize`/
`afterTransformer`/`dualLevelFixture` — not yet run this cycle. `python3
scripts/marketplace.py validate` passes structurally (manifest/RDF admission), which is
not evidence the generated Elixir compiles.

## Cycle 3 addendum — 2026-09-09, v26.9.10: remaining deferred items closed

Completed the 5 items Cycle 3 named as "ranked lower, not yet built": Persist's
`normalize/1` pipe + `metadata.source` provenance tag (`aex:normalizeModule`/
`normalizeFunction`/`provenanceSource`), Verify's delegate-and-join shape
(`aex:validateDelegateModule`/`validateDelegateFunction`), Info's rescue-to-legacy-
adapter idiom plus the full 4-form surface (`compiled`/`compiled_result`/`compiled!`/
`compiled?`, `aex:legacyAdapterModule`/`legacyAdapterFunction`), the install template's
`Code.ensure_loaded?(Igniter)` file-level guard with a plain-Mix.Task fallback, and
`aex:NestedEntity`/`nestedOf`/`nestedFieldName` for entity-within-entity support
(ash_ai's `@tool_argument`-under-`@tool` shape). All five gated by SPARQL OPTIONAL +
template `{% if %}` guards — a spec setting none of them renders byte-identical output
to v26.9.9. Bumped `26.9.9` → `26.9.10`.

**Attempted real verification, blocked by environment, not by the templates:**
built a fixture consumer project (`ggen.toml` + `schema/domain.ttl`) exercising every
new property in one spec (`aex:FixtureSpec`) and ran `ggen sync run` against it.
Failed with `[FM-PACK-001]`/`[FM-PACK-002]` path-resolution errors — the installed
`ggen 26.8.28` binary resolves `[packs]` paths against a hardcoded `/workspace` root
regardless of actual cwd. Confirmed this is a pre-existing environment issue, not
something these changes caused, by reproducing the identical failure against the
already-existing, unmodified `packs/github-actions-pack/examples/consume-github-actions-pack`
fixture. Real `ggen sync run` verification of this pack remains UNVERIFIED, not
falsely claimed as passed — a real blocker, not silently worked around.

## Cycle 2 — 2026-09-09 (CREATE, spun into a sibling pack)

Triggered by user request: "review this project and ash_r2rml to make the [starter]
pack as feature rich as possible." Two parallel real review passes (Explore agents,
file:line-cited, not workflow-run): one over `/Users/sac/ash_r2rml` (this pack's own
golden specimen), one over `/Users/sac/xaas` (a real, currently-active consumer
context). Full findings and rankings live in the two agents' own reports; only the
CREATE decisions are recorded here.

**CREATE (built as `~/ggen-marketplace/packs/ash-extension-starter-pack/`, not added
directly to this pack, since both are new capabilities rather than fixes to existing
templates):**
- `aex:ReactorStep` (ash_r2rml finding, ranked #1 of 5) — dynamic Reactor step-graph
  declaration, generalizing this pack's own `reactor_pipeline.ex.tmpl`'s hardcoded
  five-step body into a spec-declared arbitrary step DAG.
- `aex:generatesReceiptedAction` (xaas finding #5) — idempotency-key/receipt/replay
  wrapper generalizing xaas's real `Xaas.Actuation.run/4`, directly relevant to the
  `ash_ex4pm` extension's planned `brce_gate` capability.

**Confirmed-adequate, no action (from the ash_r2rml pass):** `single_extension_kinds`
coverage (finding #6); the composition test's `function_exported?/3`-only depth is a
pre-existing, already-disclosed pack.toml gap, not a new finding (finding #7); the
installer's manual-notice fallback (finding #8) and the embedded pack's name typo
(finding #9) were both already known/disclosed — confirmed still true, no new fix
needed.

**Named, not yet built (see starter-pack's own pack.toml/ontology.ttl follow-up
lists for full file:line citations):** Reactor middleware declaration; transformer
`after?`/`before?` ordering; verifier delegate-and-join-refusals idiom; Info module
getter/getter!/predicate? triple; arbitrary N-length third-party-extension
composition (xaas stacks 3-4 extensions per resource routinely — finding #1);
multi-phase orchestrating installer (xaas finding #3); a README-level disclosure that
this pack targets the Rust `ggen` binary, not the similarly-named Elixir
`ggen_igniter` hex package (xaas finding #4 — added to starter-pack's pack.toml,
should be back-ported to this pack's own docs too, not yet done).

**Verification status:** starter-pack's new ontology/templates are hand-reviewed
against their cited sources but not yet run through a real `ggen sync run` against a
live spec fixture. UNVERIFIED, not ALIVE, until that run happens.

## Cycle 1 — 2026-08-26

Ran via the `errc-cycle` skill. Note on process: the skill's generic Verify-phase
agents searched relative to the session's `cwd` (`chatgpt-cloud-elixir`) rather than
the absolute paths this tracker names in `~/ggen-marketplace/`, so 8 of 10 verify
results wrongly reported "stale/non-existent." The 2 that happened to read the real
absolute path (`verify.ex.tmpl`, `extension.ex.tmpl`) correctly confirmed the bugs,
matching the original audit workflow's findings exactly. Fixes below were applied
directly against the confirmed-real originals, not the mis-verified "stale" calls.

**RAISE (fixed):**
- `templates/verify.ex.tmpl` — zero-verifier spec now renders a bare `:ok` instead of
  an invalid empty `with ... do :ok end`.
- `templates/extension.ex.tmpl` — `entities` query now `ORDER BY COALESCE(?entity_order,
  999999)` instead of ordering directly on an OPTIONAL (sometimes-unbound) variable.

**ELIMINATE (fixed — corrected mismatched claims rather than changing behavior):**
- `templates/install.ex.tmpl` — header comment and `add_extension/1`'s doc comment no
  longer claim behavior the code doesn't have (real patch is `--target`-conditional,
  not universal; `add_extension/1` is a single unconditional insert, not
  detect-or-append). `pack.toml`'s gap-1 claim corrected to match: "one command" only
  holds when `--target` is given, not for the bare invocation.
- `templates/composition_test.exs.tmpl` + `pack.toml` — `Code.eval_string/1` →
  `Code.compile_string/1` (matches what the generated code actually calls).

**REDUCE (fixed):**
- `gates/020_schema_field_contract.rq` — header comment now documents the
  one_of-value-existence rule the query body already implemented, including the
  known SectionSchemaField gap (see parked item below).

**Left unfixed, tracked as follow-ups (not attempted — would need real testing against
live Igniter/ash_graphql/ash_json_api to trust generated-code correctness):**
- `templates/install.ex.tmpl` nil-target branch could, in principle, attempt real
  target auto-detection instead of falling back to a manual notice — not attempted
  here; the honest-fallback + corrected-claim fix above resolves the documentation
  defect without risking unverified generated code.
- `templates/composition_test.exs.tmpl` per-target test doesn't actually attach
  ash_graphql/ash_json_api to the fixture and introspect through it — noted in
  pack.toml, not fixed (same reasoning: needs real library testing to get right).

**Parked (needs user sign-off — touches ontology.ttl's closed vocabulary/schema shape):**
- `gates/020_schema_field_contract.rq`'s one_of check only covers
  `EntitySchemaField`, not `SectionSchemaField`; fixing this for real also requires
  widening `aex:oneOfValueOf`'s `rdfs:range` in `ontology.ttl` to permit attaching a
  `FieldOneOfValue` to a `SectionSchemaField`. Two-part fix, deferred.

**Closed as verified-clean, no action needed:**
- Ontology<->template variable cross-check (zero orphans).
- pack.toml's golden-specimen SHA claim (verified against real `ash_r2rml` git history).
- `gates/030` housing both entityIdentifier-match and argName-match rules together
  (organizational, not a defect).

Backlog seeded 2026-08-26 from a multi-agent audit workflow (dimension review:
ontology/gates/templates/pack.toml manifest, adversarially verified) run against
`/Users/sac/ggen-marketplace/packs/ash-extension-core-pack`. 11 of 12 raw findings
survived verification; ontology.ttl itself had zero findings.

## Backlog

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
  even though `ontology.ttl:38` says `aex:sectionFieldType` shares the same closed
  vocabulary (including `"one_of"`). Also, `aex:oneOfValueOf`'s `rdfs:range`
  (`ontology.ttl:69`) is fixed to `aex:EntitySchemaField` only, so there's currently
  no way to attach a `FieldOneOfValue` to a `SectionSchemaField` even if the gate were
  fixed — this is a two-part gap (gate + ontology range), not just a gate bug.

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
  `ORDER BY` over an unbound variable is implementation-defined. `ontology.ttl:44`'s
  own comment says this exact ordering property exists because a prior parity check
  against ash_r2rml caught entities rendering reversed without it — the field being
  `OPTIONAL` while the render path's determinism silently depends on it reproduces
  the risk class that property was added to prevent.

- [ ] **[MINOR]** `gates/020_schema_field_contract.rq:1` — the header comment
  documents the required-property and closed-type-set checks but omits the
  one_of-value-existence rule the query body actually implements at lines 52-57.

- [ ] **[NOTE]** `gates/030_entity_identifier_contract.rq` houses both the
  entityIdentifier-match rule and the argName-match rule together (organizational
  choice, not a defect — both concern an entity's own schema-field-name namespace).

- [ ] **[NOTE]** Ontology<->template variable cross-check across all 7 templates
  found zero orphan Tera variables — every `{{ }}` binding traces to a real declared
  `aex:` property. Nothing to fix; recorded for completeness.

- [ ] **[NOTE]** `pack.toml`'s golden-specimen SHA claim
  (`main@263aa768bbc5a933124409ee68f2b9efb9d09a3a`) checks out — the SHA is a real
  ancestor of `main` in `/Users/sac/ash_r2rml`, and all five cited file paths exist.
  The local ash_r2rml working tree just happens to currently be on a different
  branch (`errc/ash-extension-core-pack-installer-and-pack-name-fix`), not `main`
  itself — informational only, no correction needed.
