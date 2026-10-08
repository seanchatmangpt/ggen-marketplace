# RFC: Fortune 5 EA-as-Code — Unified SBB Pack Groups, Qualification Ladder, and Multi-Cloud Realization

- **Pack:** `packs/fortune5-enterprise-architecture-pack/`
- **Version:** 26.10.9 (seed)
- **Drives from:** `ggen/docs/rfc/v26.9.26/abb-sbb-implementation.md`; `fortune5-deployment-blocks-pack` (`catalog/fortune5-bblocks.json`)
- **Authority:** `NONE`; **ceiling:** `SELECT`
- **Status:** DRAFT — every claim below cites file:line; unimplemented pieces are marked PROPOSAL.

## 1. Problem

Three prior threads exist separately on this workstation and none unifies
them:

1. **The EA metamodel (`ea:` namespace)** — TOGAF ABB/SBB classes consumed by
   `enterprise-architecture-pack` (live instance data,
   `packs/enterprise-architecture-pack/ontology.ttl:19-39`), skeleton
   generation in `enterprise-operating-model-pack`
   (`templates/abb-skeletons.ttl.tera:5-25`, `queries/20-abb-skeletons.rq:15`),
   and the 5-stage maturity fixture ladder in
   `industry-closure-ledger-pack/fixtures/closure-growth/`.
2. **The `ggen-abb-sbb` manufacture kernel** — IO-free SELECT∥MANUFACTURE
   admission (`crates/ggen-abb-sbb/src/lib.rs:708,684,835`), PARTIAL_ALIVE:
   excluded from the root workspace (`ggen/Cargo.toml:127`), no consumer.
3. **Deployment pack groups** — the `ggen bblock` homonym
   (`crates/ggen-cli/src/cmds/bblock.rs:46-78`,
   `fortune5-bblocks.json`), explicitly forbidden from identity conflation
   with EA elements (DoD #9).

"EA-as-Code" as a term exists nowhere in the fleet; what exists is xaas
RFC-STOGAF's "enterprise architecture as admitted, machine-addressable
state" (`xaas/docs/rfc/RFC-STOGAF-v26.9.22.md`) and the TOGAF-as-graph
design in `~/archive/cloud-strategy.txt:9110-9297` (ABB = DDD/C4 logical,
SBB = Terraform/OTP deployable, deliverables = SPARQL-generated
catalogs/matrices/diagrams).

This RFC unifies the three threads into one deterministic pipeline **without
conflating them**.

## 2. Invariants (non-negotiable)

| # | Invariant | Source | Enforcement here |
|---|---|---|---|
| 1 | `Pack != ABB`, `Pack != SBB`; a group references SBBs, never is one | RFC DoD #9 (abb-sbb-implementation.md DoD item 9; falsifiers `pack_named_as_abb_or_sbb_is_refused`, `crates/ggen-abb-sbb/tests/falsifiers.rs:513,545`) | OWL `AllDisjointClasses` + SHACL `qualifiedMaxCount 0` (`ontology.ttl`); `references_only: const true` in the manifest schema; class-assertion guards in the lifting query (`queries/170-sbb-group-lifting.rq`) |
| 2 | No `ea:`/`togaf:`/`eap:`/`eom:` term is declared, re-typed or prefix-redeclared by this pack | `docs/reference/industry-closure-contract.md:22` (semantic owner `chatman-ecosystem#296`) | All `ea:` IRIs appear only as `rdfs:range`/`sh:class`/`owl:disjointWith` targets in `ontology.ttl`; binding-test patch text in §7 |
| 3 | Kernel alignment: `SELECT` existing SBB realization when present ∥ `MANUFACTURE` missing realization when absent; never unstructured `DO` | `ggen-abb-sbb/src/lib.rs:708` (`plan` → `Decision::Select`/`Decision::Manufacture`), `Authority::Do` always refused (`lib.rs:670-674`) | The pack's authority posture is `NONE`/`SELECT`; ladder Stage-2 refuses any `?s ?p ic:DO` triple (`queries/030-stage2-contract-approved.rq`) |
| 4 | "QUALIFIED is not ALIVE" | `industry-closure-ledger-pack/pack.toml:5`; `gates/090_standing_evidence.rq:10-17` | Ladder Stage-5 requires `ic:OBSERVED` evidence + LIVE coverage (`queries/060-stage5-terminal.rq`) |

## 3. The metamodel

```
ea:Strategy ── ea:Capability
       ▲ ea:realizesCapability
ea:ArchitectureBuildingBlock ──ea:governedByContract──> ea:ArchitectureContract
       ▲ ea:satisfiesABB                                     │ ea:hasAuthorityBoundary
ea:SolutionBuildingBlock                                     ▼
  │ ea:hasStanding (CANDIDATE→QUALIFIED)            ea:AuthorityBoundary
  │ ea:exactSubject "sha256:<64hex>"
  │
  ▲ f5ea:groupsSBB (pack-local, reference-only)
f5ea:SolutionGroup ──f5ea:groupTargetsABB──> ea:ArchitectureBuildingBlock (read-only projection)
  domain ∈ {guest, host, network, verification}
```

- The `ea:` layer is owned externally and consumed by IRI.
- `f5ea:SolutionGroup` is a **clustering receipt**: it clusters heterogeneous
  SBB realizations per deployment domain and projects (never confers) the
  ABB coverage of its members.
- Realization individuals (`f5ea:Realization`) mirror, never assert, the
  standing of the SBB they render (`f5ea:hasStanding`, values consumed from
  the canonical `ea:` standing individuals).

## 4. The qualification ladder (gates/)

Six stages, zero-rows-equals-pass gates, one per file; the fixture precedent
is `industry-closure-ledger-pack/fixtures/closure-growth/` (stages 0–5 — a
`stage5-verified-covered.ttl` fixture already exists; the NEW element here is
the explicit terminal admission gate requiring independent producer/verifier
agents and head-snapshot LIVE coverage):

| Stage | Gate file | Admission condition | Primary refusal |
|---|---|---|---|
| 0 | `queries/010-stage0-closure.rq` | IN_SCOPE requirement with OPEN `DEFICIT_ABB` residual | `REFUSED:F5_STAGE0_ABB_DEFICIT_UNRECORDED` |
| 1 | `queries/020-stage1-contract-pending.rq` | ABB + contract `PENDING_HUMAN_APPROVAL`, claim `NONE` | `REFUSED:F5_STAGE1_{CONTRACT_PENDING_UNREASONED, AUTHORITY_CLAIM_NOT_NONE, APPROVAL_PREMATURE}` |
| 2 | `queries/030-stage2-contract-approved.rq` | Contract `APPROVED` + named human + receipt; no SBB yet; no `ic:DO` anywhere | `REFUSED:F5_STAGE2_{APPROVAL_UNATTRIBUTED, AUTHORITY_DO_FORBIDDEN, SBB_PREMATURE}` |
| 3 | `queries/040-stage3-sbb-candidate.rq` | SBB at `ea:CANDIDATE`, attributed contract | `REFUSED:F5_STAGE3_{CONTRACT_NOT_APPROVED, SBB_NOT_CANDIDATE, CANDIDATE_UNRECORDED}` |
| 4 | `queries/050-stage4-qualified-no-evidence.rq` | SBB `ea:QUALIFIED` + well-formed unambiguous `ea:exactSubject` | `REFUSED:F5_STAGE4_{PIN_MALFORMED, PIN_AMBIGUOUS, EVIDENCE_PREMATURE, QUALIFIED_UNRECORDED}` |
| 5 | `queries/060-stage5-terminal.rq` | `ic:ExecutionEvidence` (`VERIFIED`, `OBSERVED` kind, `producedBy != verifiedBy`, subject == pin) + head-snapshot `ic:Coverage` LIVE | `REFUSED:F5_STAGE5_{EVIDENCE_FOREIGN, STALE_SUBJECT, EVIDENCE_MALFORMED, EVIDENCE_NOT_INDEPENDENT, FRONTIER_UNRECORDED}` |

`queries/100-ladder-monotonicity.rq` refuses skipped stages and regressions
(R_CORE nested-IF classifier idiom, `industry-closure-ledger-pack
queries/10-residual.rq:34-40`).

**Gate registration (PROPOSAL):** adopt the source pack's
`gate-court.toml` convention (`schema "ggen.semantic-gate-witness-court/1"`,
`case_key = "exact-stem"`, `require_pass`/`require_fail` witness fixtures
under `witnesses/pass|fail`).

## 5. Realization groups (deployment ↔ EA bridge)

- **Manifest:** `schema/f5ea.sbb-group-manifest.v1.json` — `domain` is a NEW
  closed enum on the deployment layer so nobody borrows EA classes to type a
  group; members are digest-pinned `{iri, digest, role}` references
  (`role ∈ {realizes, consumes, verifies}` — a deployment-topology relation,
  not an EA classification).
- **Lifting:** `queries/170-sbb-group-lifting.rq` CONSTRUCTs
  `f5ea:SolutionGroup` individuals only when the reference resolves against
  the authoritative EA graph with a matching `ea:exactSubject` digest; a
  corrupted manifest cannot inject `rdf:type ea:*` triples through the lift.
- **Orthogonality statement:** see `README.md` (deployment layer answers
  *where/with what packs*; EA layer answers *why/what realizes*).

## 6. Multi-cloud realization skeletons (templates/)

Per-provider Tera skeletons, rendered once per `f5ea:Realization`
(per-row rendering idiom, `azure-terraform-pack/templates/main.tf.tmpl:1-14`);
each renders AAIF-domain-tagged resource descriptions consumed by the
pack-local vocabulary (`f5ea:SbbResource` + `f5ea:aaifDomain`,
`f5ea:controlMapping`, `f5ea:ingressMode`, `f5ea:hasCmekKey`):

| Template | Domains covered | Gate |
|---|---|---|
| `templates/aws-sbb.tf.tera` | IAM Identity Center, Control Tower, Transit Gateway, VPC endpoints, CloudTrail Lake; zero-wildcard IAM by closed action maps + Andon guard | `queries/110-aws-sbb-select.rq`, `queries/120-zero-wildcard-iam.rq` |
| `templates/gcp-sbb.tf.tera` | GKE Enterprise fleet, Shared VPC, PSC, CMEK, Org Policies (no-public-ingress default) | `queries/130-gcp-sbb-select.rq`, `queries/140-cmek-and-private-connectivity.rq` |
| `templates/azure-sbb.tf.tera` | Management Groups, Virtual WAN, Guest Configuration, Dedicated HSM, Confidential Computing | `queries/150-azure-nist-800-53-rev5.rq`, `queries/160-azure-sbb-select.rq` |

**Wire compatibility (GCP):** rendered facts map to
`cloudcommerceprocurement.googleapis.com` entities via the existing
`gcp-marketplace-saas-pack` vocabulary (`gcp:Account`/`gcp:Entitlement`/
`gcp:EntitlementPlan`, `ontology.ttl:26-29,60-72`); entitlement suspension
revokes PSC `ACCEPT_MANUAL` approvals, never key material. AAIF gateway
domain tagging is in-template (`f5ea:aaifDomain` per resource).

**NIST SP 800-53 Rev 5 (Azure):** every rendered `f5ea:SbbResource` must
carry `f5ea:controlMapping` covering AC-2, SC-28, CM-6.

All templates are **skeletons** — structural stubs, not live infrastructure;
`bb:directActuation false` law inherited
(`fortune5-deployment-blocks-pack/ontology.ttl:26`).

## 7. Hygiene-law extension (binding-test patch, PROPOSAL)

Append to `docs/reference/industry-closure-contract.md` line 22 paragraph:

> A pack-local `eap:` vocabulary is not extended, and no other pack-local
> vocabulary is either. A Fortune-5 pack declares its grouping vocabulary in
> `f5ea:` (`https://ggen.io/ontology/fortune5-enterprise-architecture#`) and
> never declares, re-types or prefix-declares an `ea:`, `togaf:`, `eap:` or
> `eom:` term. The same repository test binds every `f5ea:` local name to
> `packs/fortune5-enterprise-architecture-pack/ontology.ttl`; `f5ea:` terms
> may reference `ea:` classes as `rdfs:range`/`sh:class` values only — an
> `f5ea:SolutionGroup` references `ea:SolutionBuildingBlock` individuals
> through `f5ea:groupsSBB` and is never typed as an
> `ea:ArchitectureBuildingBlock`, `ea:SolutionBuildingBlock`,
> `ea:ArchitectureContract` or `ea:AuthorityBoundary` (RFC DoD #9).

## 8. Kernel integration (PROPOSAL — ggen repo, not this pack)

To move `ggen-abb-sbb` from PARTIAL_ALIVE to invoked (full plan in the
excavation receipt; summary):

1. Absorb the crate into the root workspace (strip nested `[workspace]`,
   `crates/ggen-abb-sbb/Cargo.toml:33-35`; remove from `exclude`,
   `ggen/Cargo.toml:127`; reconcile sha2 0.10→0.11).
2. Add `ggen-abb-sbb` dep to `ggen-engine`; new `sync_admission.rs` hooking
   `pub fn sync` at the Stage 3/4 boundary (`ggen-engine/src/sync.rs:816`,
   post-extract, pre-render, pre-Write) — `parse_graph` the
   `ggen.ea.graph.v1` projection, `plan(...)` per ABB, `Decision::Manufacture`
   → fail-closed `AppError::AdmissionRefused` (typed `Refusal` survives to
   the CLI as JSON).
3. `ggen pack new`'s self-pack sync call site (`ggen-cli/src/cmds/pack.rs:828`)
   inherits the gate automatically.
4. Boundary falsifier: projected graph with a pack id colliding with an
   element id must error with `Refusal::PackConflation` and write no files.

## 9. Cross-repo transport (PROPOSAL — xaas ↔ affidavit, out of pack scope)

The truthful absence is `xaas/lib/xaas/bridges/registry.ex:22-24`
("the affidavit CLI has no xaas bridge"). RFC DoD #7/#8 do **not** name
transport. Design (detailed in the excavation receipt): NDJSON
`xaas.sbb-qualification-wire.v1`, JCS (RFC 8785) canonical bytes,
self-describing opaque digests (`sha256:`/`blake3:` prefixes — never
re-hashed), native ledger chains stay native, bridge at the receipt-argument
level; `Xaas.Architecture.SBBManifest.semantic_identity/1`
(`sbb_manifest.ex:63-71`) is the transport key; affidavit consumes via
`from_json_verified` + `ArchitectureStandingLedger.admit/2`
(`architecture.rs:564,653`).

## 10. Falsifiers for this RFC

| # | Falsifier | Command (planned) |
|---|---|---|
| F1 | A group manifest typed as an `ea:` element lifts anyway | run `queries/170-sbb-group-lifting.rq` over a poisoned manifest graph — lift must drop |
| F2 | A ladder gate passes on its own fail fixture | `gate-court` run; `require_fail` witnesses must each produce ≥1 row |
| F3 | Zero-wildcard law vacuous | inject `f5ea:iamAction "*"` into the rendered graph; `queries/120-zero-wildcard-iam.rq` must return false |
| F4 | Hygiene violation | grep the pack for declarations of `ea:`/`togaf:` classes — zero matches ideal |
| F5 | Kernel conflation crosses the boundary (post-integration) | sync graph with `pack:abb:*` id errors `PACK_CONFLATION`, no files written |

## 11. Standing

- ALIVE (this session): all cited source facts (three-lane excavation,
  file:line verified by the emitting agents).
- CONSTRUCTED (new, unvalidated by a court): `ontology.ttl`, `queries/`,
  `templates/`, `schema/` — candidates until gates run against real
  witnesses.
- PROPOSAL: gate-court registration (§4), hygiene patch (§7), kernel wiring
  (§8), wire transport (§9).
