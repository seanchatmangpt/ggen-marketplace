# Target Architecture: ggen-marketplace

## 1. Vision & Ecosystem Topology
Transform `ggen-marketplace` into an automated, federated semantic registry providing certified capability discovery and closed-loop execution patterns across distributed ecosystems:

```text
public ontologies / ggen-marketplace
            ↓
      ggen_igniter
            ↓
 ash_r2rml / ash_a2a / ash_pplan / beam4pm
            ↓
┌──────────────────────────────────────────┐
│                   XaaS                   │
│                                          │
│ canonical Ash resources + Postgres       │
│ FOND/HDDL planning                       │
│ SemanticIR / knowledge hooks             │
│ A2A capability projection                │
│ DurableServer / OTP continuity           │
│ PPCX / identity / disclosure             │
│ ground-network primitives                │
│ OCEL / receipts / replay                 │
│ BRCE / Reactor — ONLY DO CROWN           │
└──────────────────────────────────────────┘
            ↑
      tenant/product graph
            │
┌──────────────────────────────────────────┐
│                  ZOELA                   │
│                                          │
│ ZOE ontology                             │
│ Kingdom Capability semantics             │
│ Planning Center adapter                  │
│ church-specific policies                 │
│ ZOE Marketplace                          │
│ mobile/web UX                            │
│ local/offline projections where useful   │
└──────────────────────────────────────────┘
```

## 2. Core Architectural Roles
- **XaaS** is the platform, canonical Ash execution runtime, institutional Postgres system of record, and sole DO crown. It consumes generic capability, planning, consequence, and Ash PaaS packs.
- **ZOELA** is the tenant product projection over XaaS. It consumes experience projection, deterministic dynamic UI, and presentation packs.
- See [`docs/adr/ADR-0003-ecosystem-topology-and-composition-boundary.md`](file:///Users/sac/ggen-marketplace/docs/adr/ADR-0003-ecosystem-topology-and-composition-boundary.md) for the complete decision record and pack allocation matrix.

## 3. The Closed-Loop Pattern Catalog (CalVer & Compatibility)
The 12 consolidated capability packs define the underlying capability topology. Over this topology, `ggen-marketplace` introduces the **Pattern Catalog**:
$$\boxed{O_t \rightarrow \text{HDDL} \rightarrow \text{FOND} \rightarrow \text{SELECT} \rightarrow \text{CONSTRUCT} \rightarrow \text{BRCE} \rightarrow R_t \rightarrow \text{Replay} \rightarrow \text{MX} \rightarrow O_{t+1}}$$

- **Pattern**: `patterns/fond-hddl-mx-loop/` (`fond-hddl-mx-loop@v26.9.13`)
- **Domain #1**: `domains/repo-closure/` (`repo-closure@v26.9.13`)
- **CalVer Invariant**:
  $$\text{VersionIdentity} \neq \text{CompatibilitySemantics}$$
  CalVer records admission date ($v26.9.13$), while machine-readable RDF predicates (`compatibleWith`, `supersedes`, `requires`, `projects`, `conformsTo`, `breakingAgainst`) govern compatibility.
- **Promotion Invariant**: $\text{Experience} \neq \text{Authority}$. No MX-derived candidate enters exploitation without formal verification and admission into a new CalVer release.
- See [`docs/adr/ADR-0004-fond-hddl-mx-loop-pattern-and-calver.md`](file:///Users/sac/ggen-marketplace/docs/adr/ADR-0004-fond-hddl-mx-loop-pattern-and-calver.md).

## 4. Key Marketplace Target Capabilities
1. **Level-5 Pack Maturity**: Full formal verification, automated SHACL shape validation, and Diátaxis documentation coverage for all packs.
2. **Deterministic Registry Distribution**: Release distribution with cryptographic provenance and tamper-evident receipts.
3. **Option-Hypergraph Amplification (R15)**: Hypergraph querying over pack capabilities, dependencies, and composition paths.
4. **Automated Admission Pipeline**: Zero-trust CI admission combining `star-toml`, containerized ggen execution, and consumer generation tests.

## 5. v26.10.2 Verified State — The Fleet Loop, One Page

Verified end-to-end state as of the v26.10.2 wave (2026-10-02). Source of record:
ggen_igniter `docs/jira/v26.10.2/RECEIPT.md` (per-hop standing, command ledger,
falsifiers). This section is the one-page fact sheet; the hop-by-hop pack
coverage table derived from it lives at
[`docs/sjira/v26.10.2/LOOP-CLOSURE-COVERAGE.md`](sjira/v26.10.2/LOOP-CLOSURE-COVERAGE.md).

### Repo roles and loop edges

| repo | role | carrier modules | witnessing test (this session) |
|---|---|---|---|
| ggen_igniter | loop kernel: admit / pack gate / generate / execute-local / verify / receipt / promote / plan-next journal | `GgenIgniter.SemanticJira` CLI (`admit_candidates`, frontier), `SemanticJira.TargetPack` + gate `065_target_pack_contract.rq` (refusal registry 132), `SemanticJira.Execute`, `SemanticJira.Bootstrap.Receipts.check/1` (fleet-R v2), vendored digest-pinned fleet-R v2 schema (`priv/schema/`) | `test/ggen_igniter_semantic_jira_execute_test.exs:324` ("an order naming a different pack refuses `target_pack_mismatch` before ANYTHING runs"); `test/ggen_igniter_semantic_jira_receipts_check_test.exs` (fleet-R v2 admits/refuses); `test/ggen_igniter_fleet_receipt_conformance_test.exs` (schema digest pin + mutants 1-3 killed) |
| xaas | fabric: bridge + crown + SemanticReceipt + RProjection v2 | `Xaas.CS2.SemanticJiraBridge` (live seam 2517f626), `Xaas.Ultracode.SemanticCrown` + weekly semantic-crown CI job (bd7c0ad9), `Xaas.Receipt.RProjection` | bridge suite 101/0 vs the hex-published ggen_igniter dep (`test/xaas/ultracode/semantic_jira_bridge_seam_test.exs` and the `semantic_jira_bridge_*` suite); `test/xaas/ultracode/semantic_drive_plan_next_test.exs` ("... the doc still journals a candidate") |
| ash_a2a | DO + capability plane: HILT invariant, Receipt.RProjection | `AshA2a.Hilt` (`lib/ash_a2a/hilt/`), `AshA2a.Receipt.RProjection` | `test/hilt_work_order_graph_digest_test.exs` ("agreeing graph digest admits" / "disagreeing graph digest is refused `:stale_graph_identity`"); `test/ash_a2a_receipt_r_projection_test.exs`; `chicago.mutate --require-killed` wired in CI |
| ash_pplan | planner: FOND PolicyCandidate + SjBridge | `AshPplan.Fond`, `AshPplan.Sa2a.PolicyCandidate`, `AshPplan.Standing.SjBridge` | `test/standing/sj_bridge_court_test.exs` (7 closed bases, ladder mapping over a fully evidenced run) |
| ash_affidavit | evidence-seal half | `AshAffidavit` (`verify.ex`, `persist.ex`, abi/wasm config) | no v26.10.2 witnessing test named in RECEIPT.md — standing UNKNOWN this pass |
| ash_graphlaw | wasm kernel | `graphlaw_wasm.wasm` hosted by wasmex; consumed by ggen_igniter `GgenIgniter.Engine.Graphlaw` (`lib/ggen_igniter/engine/graphlaw.ex`) | `test/ggen_igniter_sync_graphlaw_cli_test.exs` |
| ash_r2rml | mapping surface | `AshR2rml` compiler/data layer (`lib/ash_r2rml/`) | no v26.10.2 witnessing test named in RECEIPT.md — standing UNKNOWN this pass |
| ggen-marketplace | pack projection-of-record | `packs/sa2a-bridge-pack`, `receipt-provenance-unification-pack`, `sjira-marketplace-feedback-pack` (ontologies spot-checked 2026-10-02) | generated modules downstream: `~/xaas/lib/xaas/generated/sa2a_bridge_edges.ex`, `sa2a_bridge_contract.ex` |

Identity conserved on every edge (source:
`docs/sjira/v26.9.21/ECOSYSTEM-CLOSURE.md:18-26`): `work_order_iri +
checkpoint_iri + graph_digest + repository_identity + base_sha`.

### Deltas: the pattern-catalog loop vs what shipped

Section 3's formula `O_t -> HDDL -> FOND -> SELECT -> CONSTRUCT -> BRCE -> R_t
-> Replay -> MX -> O_{t+1}` describes the target. Three deltas between it and
the v26.10.2 verified state:

1. **plan-next journals candidates; it does not auto-admit.** The loop's
   plan-next hop emits a journaled candidate order (xaas
   `semantic_drive_plan_next_test.exs`: "... the doc still journals a
   candidate"; xaas `admit/2` seam is default-OFF, 4b848624). Admission still
   runs through the kernel's `admit_candidates` with the origin-authority and
   `sj:admissionDigest` law. The formula's arrow into the next O_t is
   therefore a journal + re-observation step, not an automatic SELECT.
2. **DO stays in xaas/a2a — no pack actuates.** `sa2a-bridge-pack` marks
   exactly one edge `doBoundary true` and generates contract/topology data
   only; the actuating wrapper stays hand-written in xaas. The formula's
   BRCE box is repo-side (xaas crown, a2a command bus), not a pack or
   marketplace surface.
3. **MX is the OCEL observation layer, not an actuation plane.** What
   corresponds to MX in the shipped loop is event observation: standing-
   transition events (`sj:StandingTransitionEvent`, gate
   `055_standing_projection.rq`), the TransitionLog/Reconciler append, and
   machine evidence under the execute hop (weekly semantic-crown CI job,
   bd7c0ad9). MX derives candidates for the next O_t; it writes no DO.

With those three deltas named, the shipped loop at v26.10.2 is ALIVE at
qualification scale: bridge suite 101/0 against the hex-published kernel
(decisive promote falsifier), fleet-R v2 receipts enforced, and the
targetPack admission gate witnessed refusing before any byte is written.
