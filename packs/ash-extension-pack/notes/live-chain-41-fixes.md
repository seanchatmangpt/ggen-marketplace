# Live-chain 41-fixes — lane D5 close-out

Branch `spark-closure-courts` (HEAD 9709b8c). Subject:
`scripts/ash_pack_live_fixture.sh` end-to-end (ggen sync x2 determinism → capsule
copy → deps.get → compile --warnings-as-errors → mix test in the generated capsule).

Waves of the same chain run:

| run | result |
|---|---|
| baseline (stale `fixture/_build` symlinks removed first) | 98/140 passed, 42 failures |
| after cluster fixes (1)-(4) | 102/140, then 105/140 |
| transformer (b) + igniter deps plumbing | 110/140 → 110/140 |
| igniter install-task + a2a + timeouts | 131/140 → 133/140 → 134/140 |
| **final full chain (fresh capsule)** | **0 REFUSED, 77 files byte-identical, 134/140 passed, 6 failures** |

Owned files changed: `scripts/ash_pack_live_fixture.sh`,
`packs/ash-extension-pack/templates/{transformer,composition,verifier,info_parity,igniter_idempotence}_court.exs.tmpl`,
`packs/ash-extension-pack/fixture/mix.exs` (+ regen `fixture/mix.lock`),
`packs/ash-extension-pack/notes/live-chain-41-fixes.md`.

## Cluster 1 — transformer closure courts (10 failures → 0)

**Witness**: `court bug: transformer source not found for AshR2RML.Resource.Persist;
tried ["/tmp/d5-capsule/generated/lib/ash_r2rml/persist.ex"...]` — the capsule copies
the consumer's `lib/**` FLAT into `${ASH_PACK_GENERATED}` (`<pkg>/persist.ex`, no
`lib/` level), but the court's source candidates all assumed a `lib/` segment.

**Fix** (`transformer_court.exs.tmpl`): added the flat-layout candidate
`Path.join(ASH_PACK_GENERATED, "<pkg>/persist.ex")` ahead of the fixture-mount
candidate.

**Determinism leg (b)** — root-caused while fixing the same cluster: each draft
compiled its OWN uniquely-tagged specimen, and the persisted state embeds the entity
struct module name (`Court.Step<tag>`), so two PURE-transformer drafts could never
compare equal — the court measured its own tags, not the transformer. Byte-diff of
the two persisted binaries showed the first difference at the `__struct__` tag. Fix:
`compile_draft/2 → compile_specimen/0 + compile_draft/2` — one specimen shared by
both drafts (struct identity shared), drafts still independently compiled. Verified:
all 5 specs' (b) legs pass, (c) hidden-state audit passes.

## Cluster 2 — igniter idempotence install courts (20 failures → 0)

Four distinct capsule-plumbing gaps, each witnessed by the real subprocess output:

1. **fixture root**: the court used `File.cwd!()` as the spark-closure-consumer
   source dir; the chain runs mix test from `fixture/`, and the consumer app lives at
   `fixture/spark-closure-consumer/`. Fix: candidate resolution (`cwd/spark-closure-consumer`
   if it contains `lib/spark_closure_consumer`, else cwd; `AEX_IGNITER_FIXTURE_ROOT`
   override), and `vendor_extension_package` source likewise resolves
   `cwd/lib/<pkg>` OR `ASH_PACK_GENERATED/<pkg>`.
2. **deps**: the scratch copy had no `mix.lock` ("the dependency is not locked") and
   the shared deps path lacked igniter/sourceror ("the dependency is not available").
   Fix: court copies the parent `mix.lock` into the scratch;
   `fixture/mix.exs` gains `{:igniter, "~> 0.6", only: :test}` and
   `{:sourceror, "~> 1.7", only: :test}` — fetched into the shared
   MIX_DEPS_PATH. Also fixed the court's build-root default so scratch installs
   reuse the parent's compiled beams instead of a per-scratch cold build
   (60s ExUnit timeouts).
3. **install task**: the generated `mix <pkg>.install` task is projected into the
   live chain's capsule (`ASH_PACK_GENERATED/mix/tasks/`), not the committed consumer
   fixture, so `mix <pkg>.install` could not be found in the scratch. Fix: court
   copies `ASH_PACK_GENERATED/mix/tasks/<pkg>.install.ex` into the scratch's
   `lib/mix/tasks/`.
4. **installer runtime dep**: the notification installer adds `{:a2a, "~> 0.2"}`
   (aex:installerRuntimeDep); the scratch's NEXT install run dep-checks it. Fix:
   `fixture/mix.exs` gains `{:a2a, "~> 0.2", only: :test}` so the shared deps path +
   copied lock satisfy the check.

Plus typed refusal of the runner: the chain script now `rm -rf fixture/_build` at
start — a previous run's igniter scratch installs used to leave a `_build` tree with
deps symlinks inside the fixture dir, which the pack archiver refuses
(`REFUSED:PACK_SYMLINK:...fixture/_build/test/lib/...`) on the NEXT chain run.

## Cluster 3 — info-parity anti-vacuity capture legs (5 → 0)

**Witness**: `info parity court: mutant not found at
/Users/sac/ggen-marketplace/packs/ash-extension-pack/fixture/packs/ash-extension-pack/fixture/info_mutants/info_mutant.exs`
— cwd-doubled path. The mutant-path resolver joined the repo-relative path onto the
fixture cwd. Fix: candidate list (env `ASH_PACK_FIXTURE_DIR` → cwd-relative
`info_mutants/` → repo-relative) in `info_parity_court.exs.tmpl`; the chain exports
`ASH_PACK_FIXTURE_DIR` to the repo fixture dir.

## Cluster 4 — composition-court duplicate-singleton key (5 → 0)

**Witness**: `assert stderr =~ "imported from both CompositionSpecimens.AlphaClash
and CompositionSpecimens.Alpha"` vs actual compiler output
`"conflicting alpha/1 import from modules CompositionSpecimens.AlphaClash and
CompositionSpecimens.Alpha"` — the ambiguity wording is toolchain-owned and Elixir
changed it. Fix (`composition_court.exs.tmpl`): the court now names the two
modules + the conflicting fun (`alpha/1`) rather than one verbatim sentence, so both
wordings pass.

## Cluster 5 — verifier court (11 → 6, remainder = pack-content gaps, documented)

Fixed in scope:
- **Specimen applicability**: the court compiled ALL specimens against EVERY spec,
  but specimens call the spec's own section macros (`audit/1` exists only on
  audit_trail) — non-audit specs got `undefined function audit/1` CompileErrors that
  prove nothing. Fix: specimens are applicable only when the specimen's VERIFIER
  header is among the spec's declared `aex:Verifier` rows; with verifiers declared
  but zero applicable specimens the refusal leg fails typed ("refusal leg unproven"),
  never passes vacuously.
- **Diagnostics transparency**: the refusal-kind assert now prints the captured
  `Code.with_diagnostics` messages.

Remaining 6 failures — genuine pack-content gaps OUTSIDE this lane's file ownership
(ontology.ttl, verify.ex.tmpl are not court templates/fixture court-support):

| # | spec | failure | root cause |
|---|---|---|---|
| 1 | pipeline_probe | non-vacuous: "spec declares no aex:Verifier rows" | ontology.ttl declares no aex:Verifier rows for pipeline_probe |
| 2 | notification_extension | same | no aex:Verifier rows in ontology.ttl |
| 3 | ash_r2rml | same | no aex:Verifier rows in ontology.ttl | 
| 3 | ledger_probe | non-vacuous: witnessed "unique_event_name" vs declared "balanced_postings" | verifier row exists but no malformed_specimen witnesses balanced_postings |
| 5 | ledger_probe | refusal: "no malformed specimen witnesses any declared verifier [balanced_postings] -- refusal leg unproven" | same specimen gap |
| 6 | audit_trail | refusal: specimen duplicate_event_name expected `Spark.Error.DslError` matching "unique_event_name", got `FunctionClauseError ... Access.get/3` | verify.ex.tmpl's `check_unique_event_name/1` is an honest TODO stub returning :ok (the specimen header itself documents this as the vacuity witness); additionally the duplicate entity crashes inside Spark's own verifier machinery with an opaque `Access.get/3` FunctionClauseError instead of a typed DslError — Spark-upstream crash surface, not capsule plumbing |

## Chain-script hardening

- self-cleans `fixture/_build` at start (previous-run igniter scratch installs used
  to poison the next run's archiver with symlinks)
- pack-scoped preamble: the chain admits ash-extension-pack on its OWN marketplace
  issues; a concurrent wave's in-flight packs elsewhere in the marketplace (e.g.
  `REFUSED:MANIFEST_MISSING:chicago-xaas-surface-pack`) are typed
  `NOTE:FOREIGN_PACK_FLUX` to stderr, not a chain refusal
- exports `ASH_PACK_FIXTURE_DIR` for the courts' specimen/mutant resolution

## Final mix test tail

```
Finished in 123.8 seconds (3.6s async, 120.2s sync)

Result: 134/140 passed
Failed: 6 tests
```

Full final run: `/tmp/d5-final.log` (0 REFUSED, 77 files byte-identical across the
two sync passes, sha256 manifest `29f9...`-class; the six remaining failures are the
documented verifier-court pack-content gaps above). Also witnessed passing:
`reactor_parity_court` mutant-divergence capture, `pack_root` provenance scan
(87 declared properties / 43 corpus files), happy-path extension compile for all
five specs, and every igniter idempotence scenario (clean / twice / sibling / missing
target / formatter / install→regen→install) for all four installer packages.
