# Changelog — ggen-marketplace (pack releases tracked per-pack; this file tracks the marketplace repo itself)

Versions follow CalVer: `vYY.MM.P` tags on this repo. Individual packs version per their own `pack.toml` / `mix.exs`.

All notable changes to the marketplace repository are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [v26.11.5-wave] — 2026-11-07

- feat(cscb): challenger-sales-cscb pack landed and qualified — full module set on
  disk under `packs/challenger-sales-cscb/lib/` (11 modules): `CscbArc` (six-stage
  fixed-order FSM), `CscbEconomics`, `CscbHardware`, `CscbAttest`, `CscbHarness`,
  `CscbMetricAdmission`, `CscbReceipt`, `CscbStatusQuo`, `CscbTerminal`,
  `CscbVerdict`, `CscbDemoSubjects` (R11 ingress-and-settlement demo subjects);
  plus `ontology.ttl`, `shapes.ttl`, `gates/`, `generated/`, `queries/`,
  `templates/` (incl. `templates/rust/` runner emission templates),
  `qualification/` (courts + fixtures + `rust_emission_note.md`), `verify.py`,
  `emitted_rust/`. Active-set registration 27→28 in `marketplace.active.toml`
  (lane R14, 2026-11-07) — 28th active candidate; both profile verifiers'
  EXPECTED_ACTIVE_PACKS + cardinality pins + display prints updated in the same
  dependency-closed transition (`verify_msct_profile.py`,
  `verify_enterprise_kudzu_profile.py`, both exit 0 at active_packs=28).
  Pack qualification gate now on disk and green: `python3
  packs/challenger-sales-cscb/verify.py` → exit 0 (3 SPARQL gates pass,
  SHACL conforms, anti-vacuity gate 030 flips under mutation, generated
  module spot-checks pass) — resolves R14's BLOCKED-for-pack-verify flip
  condition. End-to-end pipeline receipt: `docs/how-to/run-a-cscb-benchmark.md`
  (invocations copied from a script that ran green 2026-11-07, Elixir 1.19.5 /
  OTP 28; metric admission court 11/11). Measured run receipt:
  `receipts/cscb-ingress-run-2026-11-07.md` (lane R11 — attest-stamped
  side-by-side, pack/status-quo throughput 20.3x nominal / 23.5x burst, p99
  11.7x better, measured on this machine only). Honest notes: demo pack
  workload reconciled low-alloc→zero-alloc — the retired `<<>>`-encode +
  ring-put_elem form allocated per-op heap binaries; current `pack_subject/1`
  is a `:binary.at/2` byte-walk that builds no per-op heap terms
  (`lib/cscb_demo_subjects.ex`); Rust runner Apple Silicon CNTVCT_EL0
  counter-resolution limitation disclosed with remediation path ticketed to
  the runner owner lane (`qualification/rust_emission_note.md`); receipt PDF
  rendering deferred (`CscbReceipt.render_markdown/1` is the landed output path)

- feat(pack): xstate-v5-machine-pack registered in the active set — 26 tracked
  files on disk under `packs/xstate-v5-machine-pack/` (`ontology.ttl`, `pack.toml`,
  docs/fixtures/gates/qualification/templates/tools, qualification receipt
  `_XSTATE_V5_MACHINE_PACK_RECEIPT.md`); active-set registration 28→29 in
  `marketplace.active.toml` (lane M9, 2026-11-07) — 29th active candidate; both
  profile verifiers' EXPECTED_ACTIVE_PACKS + cardinality pins + display prints
  updated in the same dependency-closed transition (`verify_msct_profile.py`,
  `verify_enterprise_kudzu_profile.py`, both exit 0 at active_packs=29);
  PACK-INDEX regenerated via `scripts/gen_pack_index.py` (356 packs: 350 active,
  6 deprecated)

- feat(packs): 6 new packs admitted — financial-margin-envelope (margin-envelope law
  pack, 3 sync-time gates), latency-hazard-radar (latency hazard detection, 3 gates),
  forensic-audit-dossier-pack (forensic audit dossier projection, 4 gates),
  pack-scaffold-generator (pack scaffolding generator, 2 gates), trade-reticle-plumbing
  (trade reticle plumbing domain, 3 gates), trade-reticle-electrical (trade reticle
  electrical domain, 3 gates); gate counts read from `packs/<name>/gates/` on disk
- feat(active-set): candidate expansion 21→27 in `marketplace.active.toml` —
  registration of financial-margin-envelope, latency-hazard-radar,
  forensic-audit-dossier-pack, pack-scaffold-generator, trade-reticle-plumbing, and
  trade-reticle-electrical (2026-11-07 lane Z13 comment block, lines 55-56)
- docs(PACK-INDEX): regenerated via `scripts/gen_pack_index.py` — header now counts
  354 packs (348 active, 6 deprecated); per-pack rows cite disk-derived profile and
  lifecycle state
- docs(receipts): receipt Standing discipline (4 root receipts + 37 JSON remappings
  per wave report; verified representative: `docs/jira/v26.11.5/receipts/G04.md`,
  `G05.md`, `G15.md` carry `Standing:` lines)
- fix(packs): 8 unparseable TTLs repaired; eng prefix split; ~30 stale pack
  cross-references corrected; sa2a-governed-process-pack stale pins refreshed;
  k8s ConfigMap/kind-name fixes; es_chain_qualify made fail-closed; hardcoded-path
  removals (counts per wave report; es_chain_qualify referenced in
  `docs/reference/aaif-deployer-contract.md`)
- chore(blocked): ggen.lock re-lock BLOCKED — installed binary `ggen 26.11.4` vs
  frozen court pin `marketplace.toml` `[ggen].version = "v26.8.11"`; re-locking
  would mint lock entries from an unpinned identity
  (notes/fm-pack-008-relock-blocked.md)
- feat(cscb): RunnerProfile minted (runner-001→arc-001); verify 18 PASS; sync byte-identical

## [v26.11.4-wave] — 2026-11-04

- docs: marketplace recount + doc-drift closure (M8/M17, 2026-11-07) — corpus recounted
  347→352 from disk (`ls -d packs/*/ | wc -l`); docs/reference/PACK-INDEX.md regenerated via
  `python3 scripts/gen_pack_index.py` (352 packs: 346 active, 6 deprecated); README count and
  capability-coverage claim updated to measured current truth (1 of 352 lacking
  `[capabilities]`: packs/kafka-wire-pack/pack.toml); active-set description corrected from a
  stale frozen-v26.9.12 framing to marketplace.active.toml's own 21-pack CANDIDATE set at
  version 26.10.7; README version-authority line names the actual tagged release `v26.10.8-3`
  (no tag minted, no version bumped); examples-survey.md pack count 332→352;
  docs/reference/pack-contract.md template suffixes aligned with scripts/marketplace.py
  TEMPLATE_SUFFIXES (+.eex) and GATE_SOURCE_SUFFIXES (+.sh); AGENTS.md ADR range corrected to
  ADR-0001 through ADR-0006.
- feat(strata-ledger-pack): template snapshot-and-pin hand-law baseline (2d0064d50) — BASELINE.md pins templates as-of `5842ccb5be92bb767c308efb196d12fde7dba78a` with post-baseline edits without a refreshed freeze witness declared unauthorized drift (`packs/strata-ledger-pack/BASELINE.md:1-12`); `templates/*.tera` gain `freeze_policy: checksum` + `freeze_slots_dir: .ggen/freeze/strata-ledger-pack` frontmatter (kernel_laws.rs.tera:4-5); blake3 freeze witnesses minted by a real `ggen sync run --skip-ea-admission` (pack as its own consumer) at `.ggen/freeze/strata-ledger-pack/packs/strata-ledger-pack/generated/*.blake3` (3 files: kernel_laws, ledger_consts, ledger_state); tamper→frozen-refusal court, byte-exact restore→clean; root `ggen.toml` mounts the pack
- docs(affidavit-pack): DEPRECATION.md supersession record (5842ccb5b) — `packs/affidavit-consumer-pack` declared successor in `pack.toml` lifecycle metadata, DEPRECATION.md gains freeze-retention note (declarations retained, no post-deprecation witness refresh), pack.toml description cross-references DEPRECATION.md (pack.toml:8)
- feat(aoq-pack): P7 status_band_rs.tmpl STATUS_BAND projection for cgap-arrow (7f5b31431); header version field bumped 2→3 — `packs/aoq-pack/templates/header_h.tmpl:51` `#define CGAP_AOQ1_VERSION 3` and `packs/aoq-pack/templates/frame_rs.tmpl:42` `pub const AOQ1_VERSION: u16 = 3;` with encode/decode/assert at frame_rs.tmpl:85/93/111

## [v26.11.3] — 2026-11-04

- feat(packs): aoq-pack — AOQ (Async Ordered Queue) wire-law pack: 64-byte AOQ1 frame header field table, status constants in the frozen band 0x4347_A001..A008, KEM hand-law seam fence, closed Epoch/StreamType enums, projected into deterministic Rust kind-enums and status maps; 9 sync-time closure gates with pass/fail witnesses and an executable court (37dc9febc, d22285bcc)
- feat(packs): cscb-pack — Chicago Bare-Metal Qualification Standard v1 (CBMQS, AF-13) modeled as RDF: 7 CscbGate individuals with AF-2-corrected thresholds, 11 stress-receipt lanes, 6 TARGET-UNMEASURED rows as a standing work queue; 4 sync-time gates + witness court; projected into deployment matrix and open-targets queue (d22285bcc)
- feat(packs): tort-pack — p99 Torture Matrix pack (GA-12): five sovereign torture injections modeled as RDF individuals with measured sovereign ceilings and TARGET-UNMEASURED cloud blowout individuals; 4 sync-time gates with pass/fail witnesses, executable court, and tracked in the qualification baseline (72f5c019c, 608242384)
- feat(cgap-pack): avec-pack renamed to cgap-pack, namespace cgap.chatmangpt.com (110030ca2); grown to 19 gates with pass/fail witnesses including skill-conformance gates SA-5/SA-15 (a58f6e9a5)
- fix(baseline): qualification/baseline.json counts recomputed from the packs tally — 313 packs total (ALIVE 295 / WARN 9 / REFUSED 8 / SKIPPED 1), ALIVE 292→295 after aoq/cscb/tort admission (9ba2496b4)
- hardening(strata): strata hardening wave — 7 strata packs (protocol, signer, cas, pn64, valve, temprun, stratus) qualified ALIVE via per-pack `verify.py` courts with `witness.ttl` receipts; 12 gates hardened (incl. `strata-pn64-pack/gates/020_transition_pre_nonzero.rq`, `strata-protocol-pack/gates/010_header_layout.rq`); namespace unification across packs; docs/README + errc-tracker quadrants updated per pack; audit-wave test/court repairs; CI strata-packs-court (`--scope all`) justification; readiness verified
- fix(baseline): baseline-to-disk reconcile — full mechanical re-run of the qualification court and re-projection via `warn_ratchet.py baseline`; 2 phantom entries dropped (pack dirs absent on disk), 36 packs added (29 ALIVE / 7 REFUSED, real FM-PACK-005 / FM-GEN-008 defects), 14 existing changed; baseline 313→347 entries, ALIVE 295→322; no hand-written JSON (0e94adbb8; docs/jira/v26.11.3/receipts/zd-12-baseline-reconcile.md)
- fix(packs): 5 of the 7 REFUSED packs repaired to ALIVE through real file-level repairs, no court relaxed — court-kit-pack (missing `@prefix rdf:`), fortune5-enterprise-architecture / pack-bootstrap / rust-doc-hdit (zero templates → SPARQL-backed census templates), typer-azure-pack (FM-GEN-008 phantom `row.kind` discriminator removed, single-BGP query + Tera `group_by`); the 2 smalt packs honestly disclosed as blocked pending a `gac:Registry` individual in graphlaw-ash-capability-pack (d451e63e4; docs/jira/v26.11.3/receipts/zd-20-pack-repairs.md)
- feat(graphlaw-ash-capability-pack): `gac:Registry` individual vendored verbatim from the real graphlaw registry (graphlaw 26.10.28 @ 095ce07 — schemaId, blake3 surface/registry digests, opCount 14, dialectCount 14) plus `gac:registryIdentityOnly`; fixture registry moved to a distinct IRI so union-graph gate `010_registry_identity.rq` stops refusing dependent packs; baseline re-projected 327/9 → 332/5; unblocks the 2 blocked smalt packs (b408361c1; docs/jira/v26.11.3/receipts/zd-49-gac-registry.md)
- chore(baseline): WARN/SKIPPED qualification entries typed — 11 entries classified mechanically via `warn_class` + `annotation` fields (9 ratchet-residue, 1 real-signal `REPAIR-LANE:composition-closure-claim-unwitnessed-by-court` on clap-noun-verb-schema-pack, 1 skipped harness limitation); statuses untouched, counts unchanged (74397a441; docs/jira/v26.11.3/receipts/zd-52-warn-typing.md)
- chore(qualify): adopt ambient ggen 26.11.3 as the corpus-wide qualification court identity via the disclosed EA opt-out (`--skip-ea-admission` on both `sync run` invocations in `scripts/qualify_packs.py`, with WHY disclosure in the module docstring); `ggen_version` bumped, baseline re-projected (ALIVE 326 / WARN 13 / REFUSED 7 / SKIPPED 1 of 347), `warn_ratchet.py check` exit 0 (55925b64b; docs/jira/v26.11.3/receipts/zd-62-mkt01-adoption.md)
- chore(packs): smalt-semconv/smalt-substrate/ash-pplan-chaos inverted positive-style gates rewritten violation-style (6 gate files, per-gate flip witnesses); corpus ALIVE 332→337, REFUSED 5→0, 347/347 qualified (9d042c2cf; docs/jira/v26.11.3/receipts/zd-65-smalt-gates.md)

## [v26.10.8] — 2026-10-13

- feat(strata): strata activation — all 7 deferred packs ALIVE; active pack set 13→20 (575beb029); MSCT invariants ALIVE
- feat(airo): AIRo de-orphaned (8a8cd062c) — 46-class projection, fail-closed gate
- feat(strata): five cross-pack composition laws with fail-closed gates + negative witnesses + gate-surgery sabotage twins — temprun↔valve (8b888e884), net↔protocol (27ebb78c4), stratus↔valve (455de53e9), cas↔chain (b47853fe5), store↔cas (fb123a452)
- feat(crosswalk): 5-column refusal vocabulary (erlmcp/ash_a2a/valve/wire/ash_graphlaw); ash_graphlaw column 40/40 mapped with G7 totality gate; erlmcp column courted from both sides; ERR_REFUSED_* collision resolved (renumbered 1101-1110, disjointness courted on both repos)
- feat(canary): count canary (4273adf24) — tamper-evident validate-counts manifest, same-commit update law
- feat(temprun): ABI-v1 derivation pin (5432e27fc) with kg-42 merge tripwire
- ci(courts): strata-packs-court covers all 16 packs (a1d85e842); fleet-courts + git-trust-court wired (ddf601cfa); refusal-vocab union court (fad4671a1)
- docs: insa-law-vows reference page; graphlaw wasm freeze ledger (praxis v26.7.5 frozen at pin, C14 named as resolution) (8e7ef0ace)

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
