# GGEN-MARKETPLACE AUDIT & ANTI-DUPLICATION RECEIPT

- **Root Path:** ~/ggen-marketplace
- **Commit HEAD:** `42b031cfa75d027bd2bef5ab6c963f73c0f9d023`
- **Branch:** `main`
- **Clean Working Tree:** false — 7 modified (`packs/rust-doc-hdit-pack/{courts/doc_quality.court, src/bin/doc-hdit.rs, src/info_theory/mod.rs, src/lib.rs, tests/verification_core.rs}`, `scripts/doc_surface.py`, `scripts/gen_doc_surface.py`) + 1 untracked (`tests/test_gen_doc_surface.py`) — active DOC-HDIT-PILOT lane. No other deltas.

## 1. Active vs. Deprecated Packs Census

**Total: 307 pack directories; 1,676 `*.tmpl` files repo-wide under `packs/`.**

True deprecations (named successors verified):

| Pack | Status | Superseded by |
|---|---|---|
| packs/rust-wasi-wasmex-pack | ACTIVE (canonical; `deprecated_precursors = ["wasi-json-abi-pack", "beam-wasmex-host-pack"]` in pack.toml) | — |
| packs/wasi-json-abi-pack | DEPRECATED (DEPRECATED.md) | rust-wasi-wasmex-pack |
| packs/beam-wasmex-host-pack | DEPRECATED (DEPRECATED.md) | rust-wasi-wasmex-pack |
| packs/clap-noun-verb-pack | DEPRECATED (compat-only route skeleton) | clap-noun-verb-{schema,crate,routing,behavior,boundary,verification}-pack (11-pack family incl. autonomic/policies/telemetry/zeroconfig) |
| packs/affidavit-pack | DEPRECATED (description marker) | affidavit-consumer-pack |
| packs/pack-authoring-pack | DEPRECATED (as independent pack-constructor authority) | ggen-self-pack (`ggen pack new`) |
| packs/chatman-ecosystem-v26-9-1-release-gate | DEPRECATED (as reusable release-law authority) | chatman-ecosystem-release-pack |

Incidental "deprecat*" word use only (NOT deprecated packs): gh-terraform-pack, dspy-pack, ma-case-study-pack, pack-consolidation-court-pack, cargo-cicd-pack (in-pack row), ash-runtime-integration-contract-pack (ggen.toml deprecation slot = generated capability).

Key ACTIVE pack structures:

| Pack | Subdirs | Notable templates/artifacts |
|---|---|---|
| aaif-vanilla-pack | dist/, fixtures/, gates/ (13 .rq), shapes/, queries/, render_aaif_pack.py | 13 tmpl: tier1_edge_router.yaml, tier2_agentgateway_mesh.yaml, gaie_inference_pool.yaml, agent_router_crds.yaml, goose_* (4), mcp_servers.json, a2a_agent_card.json, structured_agent_workspace.yaml, AGENTS.md |
| rust-wasi-wasmex-pack | fixtures/, gates/, queries/ (6 .rq), shapes/ (rww.shacl.ttl), .clap-noun-verb/ receipts | 13 tmpl: abi/{ffi.rs, abi_meta.rs, capability_registry.json, cargo_config.toml, artifacts.sha256, op_examples.json}, guest/{Cargo.toml, ffi.rs, cargo_config.toml}, host/{wasm_host.ex, mix_deps.exs, wasmex_host_manifest.json}, test/wasm_host_court.exs |
| rust-doc-hdit-pack | Real Rust crate (Cargo.toml/lock, src/{lib,certify,scaffold,vsa/encode}.rs, src/bin/doc-hdit.rs, tests/, **committed target/**), courts/doc_quality.court, scripts/, queries/ | 0 .tmpl — uses .tera (explanation/reference/how_to.md.tera). **ACTIVELY BEING EDITED (dirty tree)** |
| agent-fleet-isolation-pack | bootstrap/, gates/ (5 .rq), qualification/ | agent_preamble_sh, fleet_manifest_sh, fleet_report_md |
| chicago-graphlaw-court-pack | cases/, consumer/, gates/ (14 .rq), witnesses/, verify/, shapes.ttl, gate-court.toml | 1 tmpl |
| chicago-tdd-tools-pack | examples/ (full consumer crate), playground/, qualification/, gates/ (4 .rq), MATURITY.md | 4 tmpl |
| chicago-xaas-surface-pack | consumer/, source/, generated/ (4 JSON), test/ (Python courts), gates/ (7 .rq) | 4 tmpl |
| ggen-ecosystem-ocel-pack | gates/ (incl. pm4wasm/partial-order gates), receipts/ (TPS95/96), scripts/, tests/, tps/ | 3 tmpl |
| otel-weaver-ocel-pack | generated/ (**full Rust crate**: otel_to_ocel.rs, bin/ocel_accumulator.rs, tests/), examples/beam4pm-capability-refinement/, gates/, queries/ | 3 tmpl |
| wasi-json-abi-pack (deprecated) | generated/ (10 pre-built artifacts incl. guards.rs, ffi.rs), runners/, witnesses/, qualification/, gate-court.toml | 10 tmpl |
| clap-noun-verb family (11 packs) | gates/, qualification/ per pack | 16 tmpl total; zeroconfig = config-only, no templates/ |

In-pack Rust crates: `packs/rust-doc-hdit-pack/Cargo.toml`, `packs/otel-weaver-ocel-pack/generated/Cargo.toml`. No root Cargo.toml, no `crates/` dir. Largest template owners (sampled): ash-runtime-integration-contract-pack (~50 ex.tmpl), ai-chatbot-shadcn-pack, ggen-combinatorial-maximalism-pack, evidence-standing-pack.

## 2. Available Generators & Templates Matrix

- **Rust/WASM guest:** packs/rust-wasi-wasmex-pack/templates/guest/{Cargo.toml,ffi.rs,cargo_config.toml}.tmpl; templates/abi/{ffi.rs,abi_meta.rs}.tmpl (legacy: packs/wasi-json-abi-pack/generated/ wasm_ffi.rs, wasm_guards.rs, wasm_abi_meta.rs + 7 more)
- **Host Elixir:** packs/rust-wasi-wasmex-pack/templates/host/{wasm_host.ex,mix_deps.exs,wasmex_host_manifest.json}.tmpl; templates/test/wasm_host_court.exs.tmpl
- **Kubernetes/CRD:** packs/aaif-vanilla-pack/templates/{agent_router_crds.yaml,tier1_edge_router.yaml,tier2_agentgateway_mesh.yaml,gaie_inference_pool.yaml,structured_agent_workspace.yaml}.tmpl (+ goose_sandboxed_worker.yaml and 3 more goose_* tmpl)
- **A2A/MCP/Config:** packs/aaif-vanilla-pack/templates/{a2a_agent_card.json,mcp_servers.json,AGENTS.md}.tmpl
- Rust-doc-hdit (non-.tmpl): packs/rust-doc-hdit-pack/templates/*.md.tera

## 3. Established Test Courts & Verified Invariants

`tests/`: **115 test files, 1,631 `def test_` functions.** Custom markers in use: `conformance`, `expected_conformance_violation`, `ocpq`, `expected_ocpq_violation`, `temporal_sla` (plus parametrize/skipif/asyncio/xfail; module-level pytestmark in test_aaif_wrap_autofde_lab.py, test_commerce_seam_integration.py).

Directly-named courts from the directive:

| Test File | Tests | Invariants | Markers |
|---|---|---|---|
| test_aaif_enterprise_court.py | 12 | JWS identity, CEL PEP allow/deny, GAIE/InferencePool, hardened pod, SHACL, Petri TBR fitness ≥1.0, anti-vacuity tripwire | conformance, ocpq, expected_conformance_violation, expected_ocpq_violation, temporal_sla |
| test_rust_wasi_wasmex_court.py | 5 | FFI/wasmex host lifecycle conformance incl. violation expectations | conformance, expected_conformance_violation, temporal_sla |
| test_cdbr_isolation_court.py | 4 | CDBR-v1 container-disk-bound receipt isolation | — |
| test_pqc_closed_enum_court.py | 7 | Closed-enum DFA, in-WASM containment, PQC profiles | — |
| test_ocel2_pm4py_court.py | 5 | OCEL v2 + PM4Py + OCPQ integration | — |
| test_ggmkt_pm4pytest_court.py | 5 | pm4pytest applied to ggmkt CLI | conformance, ocpq, expected_conformance_violation, temporal_sla |
| test_pytest_ocpq_plugin.py | 3 | pytest-ocpq plugin | ocpq, expected_ocpq_violation |

Other high-density courts (do not rewrite): test_enterprise_operating_model_pack.py (77), test_industry_closure_pack.py (79), test_evolvable_capability_pack.py (60), test_aaif_deployment_court.py (40), test_paid_delivery_receipt.py (37), test_qri_consumer_binding_pack.py (43), test_aaif_vanilla_pack_court.py (28), capability-ecology family (lane courts: filesystem 16, network 18, durability 13, …), conference commerce family CG1–CG8 (test_conference_*: registration 9, provisioning 7, metering 4, isolation 10, MCP-booth 8, billing 4, signed-credential 8, dod-crosscheck 9), entitlement_seam 29 (real sim subprocess + real HTTP), marketplace_commerce_dod 18.

**Untracked:** tests/test_gen_doc_surface.py — 5 tests, DOC-HDIT-PILOT P2 (scope + external-allowlist extractor: elixir defp/@doc false internal, Rust pub vs internal dirs, known-external deps, extract_code entries).

## 4. Process Mining & Conformance Tooling Present

- **pm4pytest:** `packages/pm4pytest/` — hatchling pkg v0.1.0, deps pytest≥8 / pm4py≥2.7.23.8 / pandas / typer / rich. Entry points: `pm4pytest` + `pm4pytest-cli` (Typer, `pm4pytest.cli:app`; TAP v13/JUnit XML/JSON out, exits 0/1/2); pytest11 plugin. Fixtures: `pm4py_session` (PM4PySession over ProcessTraceCollector; register_object/emit_event/set_ocpq/set_conformance/set_temporal_sla/evaluate_all/OCEL v2 SQLite write_sqlite) + `ocpq_session` alias. Modules: plugin.py, cli.py, ocpq.py, ocel.py, conformance.py, temporal.py, reporters.py; own tests (test_cli_and_standards.py, test_pm4pytest_standalone.py). Installed in `.venv/bin/`.
- **pytest_ocpq DSL:** `src/ggen_marketplace/pytest_ocpq/{dsl.py,plugin.py}`
- **Other src/ggen_marketplace modules:** grammar/closed_enum_dfa.py (LangSec regular-grammar DFA admission), cdbr/{schema.py,sealer.py,extractor.py,pqc.py} (CDBR-v1 minting/extraction + PQC cipher suites), mining/engine.py, ocel2/{models.py,emitter.py} (IEEE OCEL v2 + SQLite emitter), aaif_node.py, cli.py
- **OCEL SQLite/PNML:** OCEL v2 SQLite traces produced by pm4pytest write_sqlite (witnessed in receipts: 8 events/11 relations + 5 events/7 relations); no *.pnml files inventoried at top levels — pm4py references appear in aloop-episode-ontology-pack/ontology.ttl; pm4wasm gates in ggen-ecosystem-ocel-pack.

## 5. Local CI Harness Assets

- Kind setup: `k8s/harness/setup_kind_cluster.sh` (invoked as `setup_kind_cluster.sh ephemeral-aaif-court`)
- Kind teardown: `k8s/harness/teardown_kind_cluster.sh`
- No `kind-cluster-config.yaml` under k8s/harness/ (kind v0.24.0 installed in workflow instead)
- **29 workflows** in `.github/workflows/`. Container/kind-wired ones:
  - `aaif-enterprise-chicago-court.yml` — kind v0.24.0 + cluster `ephemeral-aaif-court`, pip -e packages/pm4pytest, runs the 4 Chicago courts
  - `ci.yml` — full pytest (tests/ scripts/, worksteal-dist) + test_new_pack.py, advisory
  - `dsrust-compiler.yml`, `enterprise-connection-crown.yml` (subjects/ggen/tools/architecture-foundry cargo), `otel-weaver-ocel-pack.yml` (+nightly), `publish-packages.yml` (OCI images w/ SOURCE_SHA), `xaas-public-ash-projection.yml` (postgres:17), `xaas-ash-build.yml` (postgres:18), `chicago-work-equivalent.yml`, `semantic-fullstack-factory.yml`, plus 19 doc/qualification/court workflows (gate-witness-courts, vacuity-audit, shacl-rich-projection, scorecard, pages, etc.)
- Vendored binaries in `bin/`: agctl, agentgateway, aigw, goose. `packages/marketplace-cli/` is Elixir/Mix (not Rust).

## 6. Formal Receipts Present (maxdepth 2, `_*.md`)

All three are act-based container runs against ephemeral kind clusters; **none attests a HEAD SHA** (grep for HEAD/rev/commit/40-hex: zero hits — a gap, not an error):

| Receipt | Court scope | Verdict |
|---|---|---|
| `_CHICAGO_OCEL2_CONFORMANCE_RECEIPT.md` | AAIF-ENTERPRISE-2026; pm4pytest v0.1.0 + PM4Py v2.7.23.8, OCEL v2 SQLite | CLEAN PASS 9/9, 7 gates (JWS, CEL PEP, GAIE, hardened pod, SHACL, TBR fitness ≥1.0, anti-vacuity) |
| `_CDBR_V1_MULTIPACK_CONFORMANCE_RECEIPT.md` | Multi-pack Chicago + CDBR-v1 isolation; act + ubuntu:act-latest + kind v0.24.0, cluster ephemeral-aaif-court | CLEAN PASS 21/21 (AAIF 12/12, WASI/wasmex 5/5, CDBR 4/4) |
| `_PQC_CLOSED_ENUM_CONTAINMENT_RECEIPT.md` | PQC FIPS 204 + closed-enum LangSec containment; kind v1.31.0; branch feat/aaif-gcp-roadmap-v26.10.5; dated 2026-10-08 | EXIT=0, 28/28 across 4 courts + red-team neutralization (prompt injection, parser differentials, crypto downgrade, Lyapunov fuel DoW, unauthorized actuation) |

## 7. Work ALREADY COMPLETED (do NOT re-do)

1. Unified WASM surface: rust-wasi-wasmex-pack (canonical successor; precursors deprecated with named successor)
2. Enterprise AAIF topology templates (aaif-vanilla-pack: tier1/tier2/gaie/CRDs/goose/mcp)
3. pm4pytest process-mining engine + pytest plugin + Typer CLI (packages/pm4pytest)
4. pytest_ocpq DSL, closed-enum DFA grammar, CDBR-v1 minting/extraction, OCEL v2 emitter (src/ggen_marketplace)
5. Chicago/AAIF/CDBR/PQC/OCEL2 courts in tests/ (1,631 tests across 115 files) + aaif-enterprise-chicago-court CI wiring
6. Kind harness scripts (setup/teardown, cluster ephemeral-aaif-court) + 3 signed conformance receipts (9/9, 21/21, 28/28)
7. Commerce plane: monetization.toml registry, deploy_aaif_solution.py, paid-delivery receipt chain, conference CG1–CG8 courts, entitlement seam
8. DOC-HDIT-PILOT (in flight, dirty tree): doc-hdit Rust crate v1–P1 landed; P2 extractor tests written (untracked)

## 8. Remaining Unfinished Surface

1. **DOC-HDIT-PILOT P2 commit** — tests/test_gen_doc_surface.py untracked + 7 modified files uncommitted on main (P2 landing pending)
2. **Receipts lack SHA binding** — all 3 container receipts attest no HEAD/subject SHA (replay requires exact-subject identity)
3. **rust-doc-hdit-pack has a committed `target/` dir** — build artifact checked into git
4. **k8s/harness/ has no kind-cluster-config.yaml** (directive expected one; kind config is inline in workflow)
5. **Committed `erl_crash.dump`** in packages/marketplace-cli/
6. **No lifecycle.toml formal status field** in most packs — deprecation is prose/DEPRECATED.md-driven except the WASI family's `deprecated_precursors`
