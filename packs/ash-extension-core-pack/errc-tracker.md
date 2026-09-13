# ash-extension-core-pack ERRC tracker

## Cycle 4 — 2026-09-09 (requirements grounding for ash_a2a / ash_ex4pm, no pack changes)

Triggered by: "look at what is needed for ~/ash_a2a, also ~/ash_ex4pm" plus a mid-turn
OCEL-emission design note. Neither `~/ash_a2a` nor `~/ash_ex4pm` exists as a directory —
this cycle grounds their REQUIREMENTS in real adjacent repos (`~/ex4pm`, `~/ex4pm_engine`,
`~/A2A`, `~/xaas/deps`) rather than building either pack, since there is no real target
repo yet to extract a golden specimen from. Workflow `wf_51f67459-6e0`, 3 real-source
agents, 381k tokens.

**ash_ex4pm — corrections to the triggering design note (verified against real code):**
- `OcelNotifier` (real, confirmed shape) calls `Ex4pm.Stream.Ingest.ingest_batch/1` —
  that function **does not exist**. The real entrypoint is `ingest_envelope/2`
  (`lib/ex4pm/stream/ingest.ex:19`). The `function_exported?/3` guard
  (`ocel_notifier.ex:20`) is always false, so the notifier's apply/3 call is dead code
  today — it never actually reaches the ingest engine, contrary to what the design note
  implied.
- `OCELEventMiddleware` does not fire on "every" Reactor step transition — only
  `run_start`/`undo_start`-family events produce a message; `run_complete`/`run_error`/
  `compensate`/`retry` fall through a silent no-op catch-all (`ocel_event_middleware.ex:80`).
- `~/ex4pm_engine` on disk has no `lib/` — the real `Ex4pmEngine.*` modules physically
  live under `~/ex4pm/lib/ex4pm_engine/`, not in a separate repo.
- Confirmed correct: OCEL 2.0 only (no "2.1" anywhere); `Ex4pm.OCEL.normalize/1` is the
  sole real path to a canonical `%Ex4pm.Event{}`; no `Event.new/1` builder and no
  `Ex4pm.OCEL.Source` behaviour exist (real, unresolved gaps in ex4pm itself, as the note
  said). A real, copyable `Spark.Dsl.Extension` skeleton exists:
  `Ex4pmDomain.Extensions.SoundStateMachine` (`sound_state_machine.ex:1`, verifiers-only,
  no sections/entities of its own).

**ash_ex4pm — pack-vocabulary gap, named honestly:** v26.9.10's properties
(`afterTransformer`, `normalizeModule`/`normalizeFunction`, `validateDelegateModule`,
`legacyAdapterModule`) map cleanly onto wiring `OCEL.normalize/1`/`validate_envelope/1`
and even onto fixing the dead `ingest_batch` call via a `legacyAdapter`-style correct
call to `ingest_envelope/2`. But the design's two load-bearing mechanisms are **not**
covered by anything this pack generates today:
1. Spark-injecting a module into `Ash.Resource`'s own pre-existing `notifiers:` list
   (the `AshPaperTrail.Resource.Transformers.VersionOnChange` move) — this pack only
   generates a NEW extension's own DslSection/DslEntity surface, not a transformer that
   appends to a list owned by a *different*, already-declared extension. No
   `aex:globalNotifierInjection`-style property exists. Named as a real CREATE for a
   future cycle, not built here.
2. Per-Reactor middleware injection (no global registration point in Reactor) —
   `aex:workflowReactor` is the closest existing property but it is UNVERIFIED whether
   it already supports generating a per-Reactor `middlewares do ... end` injection or
   only a single named reactor reference. Flagged, not assumed either way.

**ash_a2a — correction that overturns the triggering plan's implicit premise:** the
plan (and the user's earlier composition formula) treated an "a2a protocol runtime" as
work still to be done. It already exists: a real, published Elixir hex package `:a2a`
0.2.0 (`github.com/actioncard/a2a-elixir`) is vendored/locked in
`/Users/sac/xaas/deps/a2a` — JSON-RPC 2.0, Agent Card discovery, Task/TaskStore
lifecycle, Message/Part/Artifact/Event domain model, Plug/Bandit HTTP server transport,
Req HTTP client, OTP agent supervision + registry, telemetry, Jason codec. `~/A2A`
itself (protobuf spec + Erlang SDK + Python docs) has zero Elixir code and would have
wrongly implied "unstarted" if read alone. Real remaining gaps: not confirmed wired to
`~/A2A/specification/a2a.proto`'s wire schema; no gRPC transport found (JSON-RPC/HTTP
only); not yet a dependency of `ex4pm` (`ex4pm/mix.lock` has no `a2a` entry). Net: build
`ash_a2a`'s `aex:AshExtensionSpec` against the existing `:a2a` package after adding it
as an ex4pm dependency -- do not build a JSON-RPC/HTTP/OTP runtime from scratch.

**No pack files changed this cycle** — this is a requirements/grounding pass for two
not-yet-existent consumer packages, recorded here so the corrections aren't lost before
either package is actually started.

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

## Cycle 5 — 2026-09-13 (backlog-checklist accuracy audit, no template/ontology changes)

Triggered by: "review the ggen marketplace ash extension pack to refactor using best
practices." Read every item in the Backlog section below against the real, current
template/gate content (not memory, not the Cycle 1 log alone) before touching
anything. Result: **every actionable item was already fixed in Cycle 1** (2026-08-26)
— the checkboxes below were simply never marked `[x]`, so the tracker itself had drifted
from the real repo state it exists to describe. This is the same class of defect this
session independently found and fixed elsewhere this cycle (a stale self-contradicting
status in another repo's README) — a tracker that says "open" about a closed item is as
real a defect as a template bug, since it costs a future reader (human or agent) the
same re-diagnosis effort a real bug would.

Verified fixed, this pass, by direct re-read of current file content (not re-trusting
the Cycle 1 log's own say-so):
- BLOCKING install.ex.tmpl nil-target claim — confirmed: lines 17-31 and 90-96 now
  carry the exact honest disclosure Cycle 1's ELIMINATE fix describes ("falls back to
  the same disclosed manual-notice... not claimed as one command for every invocation";
  "single unconditional insert, not a detect-or-append merge").
- MAJOR verify.ex.tmpl zero-verifier case — confirmed: a real `{% else %}` branch
  (lines 65-69) renders a plain `:ok` with an explanatory comment, not an empty
  `with ... do :ok end`. Structurally sound Tera (`{% if %}/{% elif %}/{% else %}/{% endif %}`,
  confirmed by direct inspection of the control-flow lines).
- MINOR extension.ex.tmpl entity ordering — confirmed: `ORDER BY COALESCE(?entity_order, 999999)`
  is the real query, with a comment explaining exactly which risk class it guards
  against and why it never fires today (every current `DslEntity` sets `entityOrder`
  explicitly).
- MINOR composition_test.exs.tmpl `Code.eval_string` comment — confirmed: the comment
  at line 17 now says `Code.compile_string/1`, matching the real call at lines 56/58.
- MINOR gates/020 header omitting the one_of rule — confirmed: the header (lines 1-13)
  now documents the one_of-value-existence check, including the known
  SectionSchemaField gap, in the same paragraph.

Left open, correctly, not touched:
- The gates/020 SectionSchemaField + `aex:oneOfValueOf` range gap remains genuinely
  unfixed — it is PARKED pending user sign-off because it touches the ontology's closed
  vocabulary/schema shape (widening `rdfs:range`), which Cycle 1 explicitly declined to
  do unilaterally. Still the right call; not re-attempted here.
- composition_test.exs.tmpl's per-target test still only asserts
  `function_exported?/3` rather than attaching and introspecting through the real
  target library — this is a disclosed, not a fixed, gap (pack.toml's own text says so),
  and fixing it for real needs live ash_graphql/ash_json_api testing per Cycle 1's own
  reasoning for not attempting it unverified. Still correctly deferred.

No template, ontology, or gate file changed this cycle — this is a tracker-accuracy fix
only. Branch: `errc-cycle-5-ash-extension-core-backlog-cleanup` (off `main`, per this
repo's own CLAUDE.md rule to branch before editing).

## Backlog

- [x] **[BLOCKING]** `templates/install.ex.tmpl:22-77` — nil-target branch. **Fixed in
  Cycle 1** (see Cycle 1's ELIMINATE entry and Cycle 5's re-verification above).
  Checkbox was stale; content was already correct.

- [x] **[MAJOR]** `templates/install.ex.tmpl:79-83` — `add_extension/1` doc comment.
  **Fixed in Cycle 1.** Checkbox was stale.

- [x] **[MAJOR]** `templates/verify.ex.tmpl:40-43` — zero-verifier `with` clause.
  **Fixed in Cycle 1** (the `{% else %}` branch exists and was re-verified structurally
  sound in Cycle 5). Checkbox was stale.

- [ ] **[MINOR, PARKED — needs user sign-off]** `gates/020_schema_field_contract.rq:52`
  — the one_of-value-existence check only covers `aex:EntitySchemaField`, not
  `aex:SectionSchemaField`; `aex:oneOfValueOf`'s `rdfs:range` (`ontology.ttl:69`) would
  also need widening. Two-part fix touching closed ontology vocabulary — genuinely
  still open, deliberately not attempted without sign-off.

- [x] **[MINOR]** `templates/composition_test.exs.tmpl:15` — `Code.eval_string`
  comment vs. real `Code.compile_string/1` call. **Fixed in Cycle 1.** Checkbox was
  stale.

- [ ] **[MINOR, DISCLOSED not fixed]** `templates/composition_test.exs.tmpl:48` — the
  per-composition-target test only asserts `function_exported?(X.Resource.Info, :type, 1)`;
  it does not attach and introspect through the real target library. Genuinely still
  open — needs live ash_graphql/ash_json_api testing to fix correctly, per Cycle 1's
  original reasoning for deferring it. `pack.toml` already discloses this gap; not
  silently passed off as full composition coverage.

- [x] **[MINOR]** `templates/extension.ex.tmpl:33-38` — entity `ORDER BY` over an
  `OPTIONAL` variable. **Fixed in Cycle 1** (`COALESCE(?entity_order, 999999)`).
  Checkbox was stale.

- [x] **[MINOR]** `gates/020_schema_field_contract.rq:1` — header comment omitting the
  one_of rule. **Fixed in Cycle 1.** Checkbox was stale.

- [x] **[NOTE]** `gates/030_entity_identifier_contract.rq` housing both rules together
  — organizational, confirmed not a defect, closed in Cycle 1.

- [x] **[NOTE]** Ontology<->template variable cross-check — zero orphans, confirmed
  clean in Cycle 1, nothing to fix.

- [x] **[NOTE]** `pack.toml`'s golden-specimen SHA claim — verified accurate in
  Cycle 1, informational only.
