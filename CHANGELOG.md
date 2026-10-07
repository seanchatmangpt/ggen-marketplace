# Changelog — ggen-marketplace (pack releases tracked per-pack; this file tracks the marketplace repo itself)

Versions follow CalVer: `vYY.MM.P` tags on this repo. Individual packs version per their own `pack.toml` / `mix.exs`.

All notable changes to the marketplace repository are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [v26.10.7] — 2026-10-07

- convergence(marker): `[active].version` 26.9.12 → 26.10.7 in `marketplace.active.toml` (version field only; absorbs the W618-era uncommitted 26.10.6 bump and advances it); active pack set unchanged at 13 packs, front door unchanged (`ggen-platform-pack`)
- closure(verify): `scripts/verify_msct_profile.py` exit 0 (MSCT profile invariants: ALIVE, active_packs=13) and `scripts/verify_enterprise_kudzu_profile.py` exit 0 (Enterprise Kudzu profile invariants: PARTIAL_ALIVE, active_packs=13) — verifiers key on the pack SET, not the version field (re-run at 26.10.7, see W650p receipt)
- (W126 lane; ash-extension-pack edits uncommitted pending pack commit + pin advance, mirrored in the ggen git-pack cache)
- closure(verify): `scripts/verify_msct_profile.py` exit 0 (MSCT profile invariants: ALIVE, active_packs=13) and `scripts/verify_enterprise_kudzu_profile.py` exit 0 (Enterprise Kudzu profile invariants: PARTIAL_ALIVE, active_packs=13) — verifiers key on the pack SET, not the version field
- fix(ash-extension-pack): gate `120_spark_dead_surface.rq` scope FILTER fix — add `FILTER (STRSTARTS(STR(?s), ".../ash-extension-core#"))` before the VALUES allowlist so ash_surface's `surf:*` rdf:Property declarations are out of the gate's jurisdiction; anti-vacuity preserved (a dead `aex:*` term still refuses)
- fix(ash-extension-pack): add `aex:fieldDoc` to `aex:AshA2aArgumentName` / `aex:AshA2aArgumentType` rows — template's `fields` SPARQL hard-requires it; without it rendered `@enforce_keys` defstructs were non-compiling
- feat(ash-extension-pack): `section_one_of_values` SPARQL + `one_of` branch in the section-field renderer, with three `aex:FieldOneOfValue` rows (two_port/open/disabled) — bare `type: :one_of` broke Spark 2.7.3 docs generation
- fix(ash-extension-pack): `aex:fixtureOnly true` on `aex:AshA2aSpec` — worked examples MUST NOT fan out consumer artifacts; stops `lib/ash_a2a/**` colliding with the real hex dep `ash_a2a`
- (W126 lane; pack edits uncommitted pending pack commit + pin advance, mirrored in the ggen git-pack cache)

## [v26.10.1] — 2026-10-01

- feat(pack): ash-ex4pm-evidence-pack — ProcessEvidence/Ex4pm adapter, realtime bridge, evidence court templates generalized from ash_pplan
- feat(chicago): chicago-xaas-surface-pack@26.10.1 — deterministic Chicago renderer
- feat(beam-wasmex-host-pack) 0.1.0: Wasmex host transport pack from the ex4pm RealTransport pattern; fail-closed RDF gate
- feat(wasi-json-abi-pack) 26.10.0: converged wasm ABI facts — out-len-pointer return variant, zero-import policy, replay companions, digest envelope; gate 110 + witnesses including anti-vacuity mutations
- refactor(packs): consolidation wave — dfcm 15→1, forced-top25 9→1, adapter/fleet 7→1+profile, tcps 5 crates→1, MCP trio→1, projection-matrix 3→1, beam4pm contracts 2→1, vocabulary de-redeclaration; ten capability packs merged into capability-ecology-pack
- refactor(marketplace): 7d-staleness deletion court — 68 packs retired
- feat(packs): workflow-corpus-pack adversarial corpus + fixtures 01-12 (HDDL, FOND replanning, durability, SA2A, dynamic branch/recursion, authority-denied, substitution)
- feat(packs): authority + evidence capability packs
- integrate: adoption wave — live-chain court fixes, leverage audit; closure courts wave — gate allowlist refresh, tera fixes, fixture chain unblock
- Spark ⟷ implementation closure receipt for ash-extension-pack (spark-closure-courts)

## [v26.9.30] — 2026-09-30

- release: v26.9.30 notes, qualification baseline, regenerated derived docs
- fix(packs): make the 7 packs refused by real ggen 26.9.28 qualify
- release: bump pack versions for 11 content-changed packs since v26.9.29
- fix(ash-extension-pack): installer --target uses Spark.Igniter.add_extension/5
- fix(qri-pack): beam-host host.ex renders when a contract declares no optional export
- feat(packs): TypeScript and Python wasm hosts; close affidavit consumer closure; deprecate affidavit-pack
- graphlaw: coverage ledger, typed models, wasi-json-abi graphlaw specimen, docs
- feat(packs): capability-closure-pack solver and affidavit-consumer-pack
- feat(packs): add qri-qualification-profile-pack (Qualified Runtime Interchangeability); QRI gate court covers all 8 gates
- feat(packs): add industry-closure ledger kernel, operating-model and retail-lending profile packs (#554, #550, #551)
- feat(marketplace): lifecycle registry for deprecation/replacement/upgrade flags; verified flags seeded for release, ash, shacl/shadcn, cnv, governance, forced-top25 families
- ci: install the pinned nightly in publish workflows; install Jinja2 and pyshacl for repo-mutating and strategic-doctrine tests (#540)

## [v26.9.29] — 2026-09-28

- fix(packs): make all 376 packs qualify through real ggen 26.9.28
- release: bump marketplace version to v26.9.29

## [v26.9.28] — 2026-09-28

- feat(packs): complete diataxis-documentation-pack and projection-matrix-pack
- feat(fleet): admit fleet-package-compiler, fleet-package-compose, fleet-projection-closure
- fix(ash-extension-pack): scope every query per spec; generate Reactor step modules; ORDER BY for Rust ggen strict_mode; generate the Receipt ledger and harden receipted_action (v26.9.27)
- fix(evolvable-capability-pack): restore branch hardening dropped by main-wins merge
- fix(packs): ash-r2rml-reactor-paas-pack ALIVE under qualification harness; greene-licensing-case-pack catalog digest refresh
- feat(cs2): authority-free consumer runtime — admission contracts, consumer execution factory, projection/acceptance/next-edge queries, consumer-work and admission-result schemas; consolidate cs2 branches onto the canonical pack
- Complete cs2-exact-subject-pack and supplier-equilibrium-pack, strategic-doctrine-compiler-pack, adapter-family-registry, canonical-ash-projection-generator, fleet-adapter-matrix packs

## [v26.9.24] — 2026-09-24

- feat(marketplace): admit ggen_igniter EEx templates; document and qualify EEx projection templates
- feat(collective-skill): README, validate_court_contract.py, court-contract.json.tera
- fix(pptx): repair generated writeFile boundary
- chore(marketplace): advance registry snapshot to v26.9.24

## [v26.9.14] — 2026-09-14

- (tag move; no commits on top of v26.9.13)

## [v26.9.13] — 2026-09-14

- fix(audit_vacuity): add MAX_SCANNED_FILE_BYTES size gate to scan_content
- feat(kudzu-case-studies-pack): promote 4/5 pilots to VERIFIED ALIVE, re-derive open-ontologies BLOCKED reason
- feat(pack-compatibility-pack): real dependency-order computation + cycle detection; real pack-to-runtime compatibility checker
- feat(protocol-integration-pack): add cli-subprocess adapter template family
- ci: run semantic court on candidate pushes; add exact-head semantic-subject receipt court
- fix(semantic-docs): close emitter-vocabulary identity gap

## [v26.9.12] — 2026-09-12

- feat(packs): canonical packs wave — state-transition, process-intelligence, ggen-platform (front-door, 11 canonical packs), experience-projection (MX/HX), enterprise-governance, repository-lifecycle (Source→Build→Verify→Release)
- docs: real legacy-pack consolidation census (issue #439)
- fix: close gym-pack-set drift in verify-gym-packs.py

## [v26.8.10] — 2026-08-14

- verify ggen release tag before asset admission; exact release tag verification plumbing
- document marketplace pack source authority; separate historical provenance from pack authority
- tighten source-authority verifier typing
- add self-contained standing ladder qualification specimen; make standing ladder reusable and self-contained; fix hidden cross-pack dependency

## [v26.8.9] — 2026-08-09

- Initial tracked marketplace release (history begins at this tag)
