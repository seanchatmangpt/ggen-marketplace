# Machine Handoff & Next Obligations

## 1. Active In-Flight Work
- **Branch**: `feat/aaif-gcp-roadmap-v26.10.5`
- **Release Target**: `v26.10.5`
- **Plan Reference**: [`i-had-you-running-memoized-parrot.md`](file:///Users/sac/.claude/plans/i-had-you-running-memoized-parrot.md)
- **Roadmap Status** (5-phase plan, prior plan `ok-so-the-goal-crispy-oasis.md`):
  - Phase 1 — modernize + activate `aaif-vanilla-pack`: **landed**
  - Phase 2 — `aaif-profile-tailoring-pack` + `profile_intake`: **landed**
  - Phase 3 — entitlement seam + monetization registry + paid-delivery receipts: **landed**
  - Phase 4 — `deploy_aaif_solution.py` deployer: **in flight**
  - Phase 5 — Diátaxis docs + exec-summary truth repair: **landed**

## 2. Delivered in Prior Milestone (superseded claims, retained for history)
1. **`ggmkt` CLI Substrate Wrapper**: Typer CLI (`search`, `info`, `list`, `validate`) backed by RDF ontology queries.
2. **GCP Marketplace Engine**: RS256 JWT entitlement procurement, Service Control metering, in-cluster Kubernetes reconciler.
3. **DfLSS Six Sigma Project Charter**: DMADV problem statement, VOC-to-CTQ flowdown, SPARQL tripwire gates.
4. **AAIF Upstream Stack Integration**: SDK execution across A2A, MCP, Goose, Agentgateway, Agent Router.
5. **The Autonomous Semantic Utility Thesis**: `A = μ(O*), R = receipt(A)`.
6. **IEEE OCEL v2 & Process Intelligence**: multi-object trace collection, PM4Py discovery, TBR alignments, OCPQ.
7. **`pm4pytest` Universal Testing Engine**: standalone binary CLI and Pytest plugin emitting TAP v13 and JUnit XML.

## 3. In Flight on Branch (`feat/aaif-gcp-roadmap-v26.10.5`)
1. **Modernized + activated `aaif-vanilla-pack`**: new `ggen.toml` (DeclarativeRules), `queries/*.rq` extracted from legacy template frontmatter, ORDER BY added to gates 090–190, `aaif:Agent` declared; activated in `marketplace.active.toml` (13 active packs, EXPECTED lists updated in `verify_msct_profile.py` / `verify_enterprise_kudzu_profile.py`).
2. **`packs/aaif-profile-tailoring-pack/`**: `aaift:DeploymentProfile` parameter surface (namespace/replicas/cmek/finops/siem/spiffe/pqc) with closed enums, fail-closed gates, witnesses, gate-court.
3. **`monetization.toml` + `scripts/marketplace_monetization.py`**: lifecycle.toml-shaped registry with `backend = "sim"|"real"`, billing-authority vocabulary, hooked into `marketplace.py validate`.
4. **Entitlement seam** (`scripts/entitlement.py`): typed `decide()` against the GCP sim (JWT via x509 metadata endpoint), sim↔real flip is a registry line.
5. **Paid-delivery receipt chain** (`scripts/paid_delivery_receipt.py`): `receipts/paid-delivery/<slug>.json` + hash-chained `chain.jsonl` (`paid-delivery-chain/v1`, plain sha256 fold).
6. **`scripts/profile_intake.py`**: JSON/HTML/text profile → normalized JSON + RDF individuals (vendored foaf/schema/org + parallel `aaif:Agent` individuals).
7. **`solutions/` scaffold + `examples/profiles/` fixtures**: two-pack path-pin consumer layout.
8. **Diátaxis docs** (5): deploy tutorial, Kind-rail + profile-ingest how-tos, deployer-contract reference, commerce-seams explanation; `docs/book.ttl` navigation entries.
9. **Exec-summary truth repair** (`docs/strategy/gcp-marketplace-executive-summary.md`): endpoint-set, DRAIN timing, refusal-ladder and standing reframe corrections.
10. **Phase 4 (in flight)**: `scripts/deploy_aaif_solution.py` + `tests/test_aaif_deployment_court.py` — 10-step deployer with refusal ladder, entitlement-before-manufacture, namespace-scope check, byte-identical replay.

## 4. Backlog Obligations
- ggen `v26.10.5` tag, then bump `marketplace.toml` `[ggen]` pin — **BLOCKED** until the tag exists upstream.
- Real GCP vendor onboarding (listing, EDP) → flip entitlement backend to `real` — **BLOCKED** (external).
- Publish `packages/pm4pytest/` to PyPI — **BLOCKED**: credentials.
- Affidavit: merge-prep gate, then merge + tag `feat/advanced-witness-capability-set` and pin marketplace seam.
- Introduce Mix and Cargo wrappers (`mix pm4pytest`, `cargo pm4pytest`).
- Finalize production GCP Marketplace Commercial SaaS listing package.
