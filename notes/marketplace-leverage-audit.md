# Marketplace Leverage Audit — ash_pplan vs ggen-marketplace

Read-only audit, lane D3, 2026-10-01. Repo `~/ggen-marketplace` @ spark-closure-courts
(9709b8c), consumer repo `~/ash_pplan`. No git commands run; `packs/` untouched.

Headline: **low leverage in both directions.** ash_pplan ships 6 ggen packs under
`priv/ggen/ash-pplan-*` that exist nowhere in the marketplace (284 packs, zero
pplan entries), and capability-closure-pack's index (`index/declared.ttl`) contains
**0** references to ash_pplan. Meanwhile ash_pplan consumes nothing from the
marketplace either: no pack reference in `ggen.toml`, `mix.exs`, `config/`, or
`bin/`. The marketplace is functioning as a read-only museum for this repo, not a
supply chain.

## 1. Marketplace capabilities ash_pplan should consume (top 5)

| # | Pack | Path | What it manufactures | What it would replace in ash_pplan |
|---|------|------|--------------------|-----------------------------------|
| 1 | ash-extension-pack v0.4.0 | `packs/ash-extension-pack` | Spark extension codegen (extension, info, persist, verify, reactor step/pipeline), 14 SPARQL gates, 13 court templates — spark/info/reactor parity, drift, dead surface, igniter idempotence, regeneration, composition, mutation league, runtime burn-in, closure receipt. | The closure-courts wave just landed here; ash_pplan's hand-rolled parity/drift/dead-surface checks (in `test/` and `bin/gate`) duplicate this shape. Consuming the pack's court templates against ash_pplan's own spec facts would replace local court hand-writing. |
| 2 | ash-runtime-integration-contract-pack | `packs/ash-runtime-integration-contract-pack` | ~30 generated runtime modules (authority gate, bulkhead, circuit breaker, compensation, cancellation, deadline, consistency, audit fields, causation/correlation IDs, deprecation, domain-error normalizer) + RuntimeShape/OCEL/receipt/replay boundaries + cross-contract courts. | Hand-written runtime contracts in `lib/ash_pplan/reactor/`, `sa2a/`, `workflow/` (adapter, oban, outbox patterns). authority_gate/compensation/cancellation templates map 1:1 onto ash_pplan's durable reactor stores and standing ceilings. |
| 3 | receipt-provenance-unification-pack | `packs/receipt-provenance-unification-pack` | One stdlib-only validator covering six receipt contracts, a machine-consumable contract matrix, gate report, qualification runner; already carries a `dfcm_fleet_v1` contract transcribed from `~/.claude/dfcm/receipt.schema.json`, including git-probe replay checks (notes_object, ancestor_of). | `lib/ash_pplan/standing/receipt.ex` + `chain.ex` validate field presence only — five fields with `R_missing_<field>` broken terms. The rp-pack adds value-form/pattern/durable-replay-git-probe validation ash_pplan's generated validator lacks; and its documented XOR standing-token divergence (`REFUSED[...]` vs `REFUSED:...`) is exactly the cross-repo standing-token drift chain.ex must not reintroduce. |
| 4 | capability-closure-pack | `packs/capability-closure-pack` | Requirement graph → REUSE/EXTEND/BUILD classification against a declared index of pack capabilities, each claim evidence-checked against the packs tree. Authority NONE (SELECT only). | This is the exact instrument the headline finding asks for: if ash_pplan's needs were declared in `index/declared.ttl`, the REUSE/EXTEND/BUILD solver would mechanically surface un-generalized local capability — instead of the manual audit this file is. |
| 5 | chicago-tdd-tools-pack | `packs/chicago-tdd-tools-pack` | Generates CliHarness boundary tests plus a systematic negative-witness (sabotage) suite from ctt: individuals; real-binary Chicago tests with verbatim stderrNeedle facts transcribed from live runs. | ash_pplan's conformance suites are state-asserting (Chicago-compliant) but the sabotage/negative-witness layer — mutants hitting real enforcement paths with verbatim stderr needles — is absent from ash_pplan's tests: `test/durable/*` asserts correct state, never sabotages. |

canonical-ash-projection-generator and pack-consolidation-court-pack surveyed and
correctly NOT consumed: the former targets canonical Ash resource-projection
profiles (ash_pplan has no Ash resources of that profile shape); the latter is a
meta-court for pack relationships — relevant to section 2 below, not to runtime
consumption.

## 2. ash_pplan capabilities that should be generalized INTO marketplace packs

Verified with grep across all 284 packs: no pack covers these. The six
`priv/ggen/ash-pplan-*` packs exist only in ash_pplan's tree.

| # | Local capability | Evidence | Proposed pack | Extend instead of fork |
|---|-----------------|----------|---------------|------------------------|
| 1 | Durable Store behaviour + ETS/Dets engines + conformance suite generated from ontology (`lib/ash_pplan/reactor/durable/store/{ets,dets}.ex`, `priv/ggen/ash-pplan-store-conformance-pack`, generated `AshPPlan.Test.StoreConformance`) | grep for Dets across packs: 0 hits in any pack | `durable-ets-dets-conformance-pack` | Extend `chicago-tdd-tools-pack` (its CliHarness/Chicago discipline); do NOT fork `ash-extension-pack` — that pack owns Spark extension codegen, not storage-behaviour conformance. |
| 2 | TLA+/tla-rs protocol court (`priv/ggen/ash-pplan-durable-tla-pack`: durable.cfg.eex, durable.tla.eex, stateright_model.rs.eex, transitions.exs.eex) | TLA+ appears in the marketplace only as a name-drop in `semantic-procedural-graph-pack/README.md`; no template manufactures .tla/.cfg or a Stateright model | `durable-protocol-court-pack` | Standalone; closest existing shape is chicago-graphlaw-court-pack's case-ontology→test-files pattern — share a vocabulary, do not fork. |
| 3 | Chaos invariants generated from ontology (`priv/ggen/ash-pplan-durable-chaos-pack` → manufactured chaos suites in `test/durable/`) | no chaos/property-suite pack exists (grep "chaos" across pack names: none) | `durable-chaos-pack` | Fold into `durable-protocol-court-pack` — one ontology vocabulary, two template families (model-checking + chaos). |
| 4 | Standing receipt API (5-field R with typed broken terms; generated `Standing.Receipt`/`Standing.Chain` via `bin/manufacture-standing`) | five-field R pattern exists in evidence-standing-pack (invariants) and receipt-provenance-unification-pack (field-shape validator) — but NEITHER generates a consumer-language receipt module; both are validators/invariants only | (generation family, not a new pack) | Extend `evidence-standing-pack` with a generation family (generated per-consumer receipt module). Note standing-ladder-pack also overlaps; classify per pack-consolidation-court-pack (EXTRACT_SHARED_ONTOLOGY / HARD_MERGE) before adding. |
| 5 | Migration/closure courts (`bin/gate`, `bin/conform-falsify`, closure receipts) | ash-extension-pack has regeneration/igniter-idempotence/dead-surface/closure-receipt courts — shape-mates exist, but ash_pplan's migration/closure gates over its own ontology migrations are local-only | (court template, not a new pack) | Extend `ash-extension-pack`'s court family with a migration-closure court template + gate over a generalized `MigrationClosure` vocabulary (aex: currently couples courts to Ash extension specs). |

## 3. Duplicates/overlaps between ash_pplan priv/ggen packs and existing marketplace packs

All six local packs are marketplace-missing; overlaps by court shape:

| ash_pplan local pack | Overlaps with | Overlap type | Resolution |
|---|---|---|---|
| ash-pplan-standing-pack | evidence-standing-pack, receipt-provenance-unification-pack, standing-ladder-pack | Partial: local pack GENERATES a receipt module; marketplace packs validate/define invariants only. | Extend evidence-standing-pack with a generation family; retire the local pack's generation into it. |
| ash-pplan-store-conformance-pack | chicago-tdd-tools-pack (method), cs2-conformance-pack (name only) | Method overlap only — no pack manufactures a Store-behaviour conformance suite. | Generalize (BUILD) as in §2.1. |
| ash-pplan-durable-tla-pack | semantic-procedural-graph-pack README mention only | Name overlap only. Genuinely missing. | Generalize as durable-protocol-court-pack. |
| ash-pplan-durable-chaos-pack | none | Genuinely missing. | Generalize (fold into durable-protocol-court-pack). |
| ash-pplan-workflow-pack (P-PLAN/PROV-O projection) | ash-ocel-revops-surface-factory-pack, beam4pm-process-model-pack, wasm4pm-compat-pack | Vocabulary-adjacent: P-PLAN/PROV-O onto Ash vs OCEL/process-model. | Publish as own pack; EXTRACT_SHARED_ONTOLOGY with the process-semantic family per pack-consolidation-court-pack. |
| ash-pplan-pack (core; the only one wired into ggen.toml) | ash-extension-pack | Court/gate structure overlap (gates/ + templates/ + ontology.ttl); semantics differ (process semantics vs Spark extension codegen). | KEEP_DISTINCT, but adopt ash-extension-pack's 14-gate layout as the canonical gate layout. |

## Falsifier

```
grep -rl "Dets\|stateright" packs/                              # 0 files → §2.1–2.3 genuinely missing
grep -c "ash_pplan" capability-closure-pack/index/declared.ttl  # 0 → ash_pplan invisible to closure solver
ls packs/ | grep -i pplan                                       # empty → no pplan pack published
```

All three were run during this audit and produced the stated results.
