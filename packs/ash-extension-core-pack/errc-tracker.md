# ash-extension-core-pack ERRC tracker

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
