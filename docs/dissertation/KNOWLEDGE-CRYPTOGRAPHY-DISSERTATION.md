# Categorical Foundations of Knowledge Cryptography

**Author:** Sean Chatman
**Institution:** ggen Fleet — Semantic Manufacturing Substrate
**Date:** October 2026

> **Mechanization note.** The conformance vectors TV-01..TV-05 described in
> Chapter 8 are mechanized in
> `packs/fortune5-enterprise-architecture-pack/tests/test_conformance_vectors.py`
> — real rdflib execution of the pack's real SPARQL gates against real
> fixture graphs, no mocks.

> **Provenance note.** The original session manuscript was not recoverable
> verbatim; this text is reconstructed from the canonical pack sources:
> `packs/fortune5-enterprise-architecture-pack/` (`RFC_FORTUNE5_EA_AS_CODE.md`,
> `ontology.ttl`, `queries/*.rq`, `tests/test_conformance_vectors.py`).
> Every factual claim below is grounded in those files; the prose is
> reconstruction.

---

## Abstract

Enterprise architecture has historically been a *narrative* discipline:
diagrams, slideware, and prose describing intent without admitting,
constraining, or witnessing it. Narrative cannot fail closed. This
dissertation develops **Knowledge Cryptography**: the discipline of treating
architectural knowledge as cryptographic material — pinned by digest,
fail-closed at every transition, and verifiable by third parties — rather
than as mutable narrative. We formalize enterprise architecture as a
categorical system over an RDF metamodel (`ea:` consumed by IRI, `f5ea:`
pack-local), derive a six-stage qualification ladder whose gates are SPARQL
queries with a single refusal shape, enforce class separation with OWL
disjointness axioms and SHACL fences, and qualify the system with five
black-box conformance vectors (TV-01..TV-05), mechanized as real gate
executions against real fixture graphs.

---

## Table of Contents

1. [Chapter 1 — The Problem: Architecture as Narrative](#chapter-1-the-problem-architecture-as-narrative)
2. [Chapter 2 — Three Threads, One Pipeline](#chapter-2-three-threads-one-pipeline)
3. [Chapter 3 — The Metamodel: Consumption by IRI](#chapter-3-the-metamodel-consumption-by-iri)
4. [Chapter 4 — The Qualification Ladder](#chapter-4-the-qualification-ladder)
5. [Chapter 5 — Realization Groups and Multi-Cloud Skeletons](#chapter-5-realization-groups-and-multi-cloud-skeletons)
6. [Chapter 6 — Hygiene Laws: The Anti-Alias Fence](#chapter-6-hygiene-laws-the-anti-alias-fence)
7. [Chapter 7 — Kernel Integration and the Admission Boundary](#chapter-7-kernel-integration-and-the-admission-boundary)
8. [Chapter 8 — Conformance Vectors TV-01..TV-05](#chapter-8-conformance-vectors-tv-01tv-05)
9. [Chapter 9 — Conclusion and Standing](#chapter-9-conclusion-and-standing)
10. [Bibliography](#bibliography)

---

## Chapter 1 — The Problem: Architecture as Narrative

Every large enterprise maintains an architecture function that produces
documents describing how the estate *should* behave. None of those documents
can refuse anything. A narrative cannot fail closed. A slide cannot carry an
authority ceiling. A diagram is not a receipt.

The central object of this dissertation is the replacement of narrative
architecture with **admitted, machine-addressable architectural state** — the
position argued in `RFC-STOGAF-v26.9.22.md` ("enterprise architecture as
admitted, machine-addressable state") and operationalized here as a pack
whose authority posture is `NONE` with a `SELECT` ceiling
(`ontology.ttl:19-20`).

The replacement relation is directional:

$$
\text{Narrative} \xrightarrow{\;\text{cannot refuse}\;} \bot
\qquad\qquad
\text{Graph} \xrightarrow{\;\text{gate}\;} \{\text{PASS},\ \text{REFUSED}{:}*\}
$$

and the house falsifier shape that makes the graph side trustworthy is the
zero-rows-equals-pass law:

$$
\text{gate}(G) \;=\;
\begin{cases}
\text{PASS} & |\text{rows}(G)| = 0 \\
\text{REFUSED} & |\text{rows}(G)| \ge 1
\end{cases}
$$

A gate that admits by enumerating valid states must be maintained against
every new valid state; a gate that refuses on any violation row needs only
the violation's shape. Refusal-shaped admission is therefore the only
admission that scales, and it is the shape every gate in this system takes.

Why "cryptography"? Because the three properties that make cryptographic
material trustworthy — exact identity (digest pinning), fail-closed
verification, and third-party replayability — are exactly the properties the
narrative discipline lacks, and exactly the properties the machinery of the
following chapters supplies. Architectural knowledge that cannot be
replayed is rumor; knowledge that can is evidence.

---

## Chapter 2 — Three Threads, One Pipeline

Three prior threads existed separately on this workstation (RFC §1), each
partial, none unifying:

1. **The EA metamodel (`ea:` namespace)** — TOGAF ABB/SBB classes with live
   instance data (`packs/enterprise-architecture-pack/ontology.ttl:19-39`),
   skeleton generation in `enterprise-operating-model-pack`
   (`templates/abb-skeletons.ttl.tera:5-25`), and the 5-stage maturity
   fixture ladder in `industry-closure-ledger-pack/fixtures/closure-growth/`.
2. **The `ggen-abb-sbb` manufacture kernel** — IO-free
   `SELECT ∥ MANUFACTURE` admission
   (`crates/ggen-abb-sbb/src/lib.rs:708,684,835`), PARTIAL_ALIVE: excluded
   from the root workspace, no consumer.
3. **Deployment pack groups** — the `ggen bblock` homonym
   (`crates/ggen-cli/src/cmds/bblock.rs:46-78`), explicitly forbidden from
   identity conflation with EA elements (DoD #9).

The unification law is: one deterministic pipeline, three threads, **zero
conflation**. Each thread keeps its own identity; the pipeline composes them
by reference, never by merging types:

$$
\text{metamodel} \;\parallel\; \text{kernel} \;\parallel\; \text{deployment}
\;\longrightarrow\; \text{one ladder},\ \text{three identities preserved}
$$

The term "EA-as-Code" is deliberately *not* coined as a new identity for any
of the three threads; it names only their composition. This discipline —
naming compositions without re-typing their parts — is the categorical
ethic the rest of the dissertation formalizes.

---

## Chapter 3 — The Metamodel: Consumption by IRI

The metamodel (RFC §3) is a two-layer category. The `ea:` layer is owned
externally (semantic owner `chatman-ecosystem#296`) and consumed by IRI; the
`f5ea:` layer is pack-local and *references* without *re-typing*:

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

The key categorical object is `f5ea:SolutionGroup`: a **clustering receipt**.
It clusters heterogeneous SBB realizations per deployment domain and projects
— never confers — the ABB coverage of its members. Projection versus
conferral is the difference between a view and an assertion:

$$
\text{coverage}(\text{group}) \;=\; \bigcup_{s \in \text{groupsSBB}} \text{coverage}(s)
\qquad \text{(projection, derivable)}
$$

$$
\text{coverage}(\text{group}) \;\neq\; \text{independent coverage}
\qquad \text{(conferral, forbidden)}
$$

This is enforced three ways simultaneously (defense in depth, RFC §2
Invariant 1): OWL `AllDisjointClasses` over
{`f5ea:SolutionGroup`, `ea:SolutionBuildingBlock`,
`ea:ArchitectureBuildingBlock`, `ea:ArchitectureContract`}
(`packs/fortune5-enterprise-architecture-pack/ontology.ttl:60-97`); a SHACL `qualifiedMaxCount 0` on `rdf:type` against those
classes (`f5ea:SolutionGroupShape`); and `references_only: const true` in
the manifest schema. The digest pin `ea:exactSubject "sha256:<64hex>"` is
the cryptographic anchor: standing attaches to an exact subject, never to a
name.

---

## Chapter 4 — The Qualification Ladder

Qualification is a six-stage ladder (RFC §4), one zero-rows-equals-pass
gate per file, with `queries/100-ladder-monotonicity.rq` refusing skipped
stages and regressions. The fixture precedent is
`industry-closure-ledger-pack/fixtures/closure-growth/` (stages 0–5); the new
element is the terminal admission gate requiring independent
producer/verifier agents and head-snapshot LIVE coverage.

| Stage | Gate file | Admission condition | Primary refusals |
|---|---|---|---|
| 0 | `010-stage0-closure.rq` | IN_SCOPE requirement with OPEN `DEFICIT_ABB` residual | `F5_STAGE0_ABB_DEFICIT_UNRECORDED` |
| 1 | `020-stage1-contract-pending.rq` | ABB + contract `PENDING_HUMAN_APPROVAL`, claim `NONE` | `F5_STAGE1_{CONTRACT_PENDING_UNREASONED, AUTHORITY_CLAIM_NOT_NONE, APPROVAL_PREMATURE}` |
| 2 | `030-stage2-contract-approved.rq` | Contract `APPROVED` + named human + receipt; no SBB yet; no `ic:DO` anywhere | `F5_STAGE2_{APPROVAL_UNATTRIBUTED, AUTHORITY_DO_FORBIDDEN, SBB_PREMATURE}` |
| 3 | `040-stage3-sbb-candidate.rq` | SBB at `ea:CANDIDATE`, attributed contract | `F5_STAGE3_{CONTRACT_NOT_APPROVED, SBB_NOT_CANDIDATE, CANDIDATE_UNRECORDED}` |
| 4 | `050-stage4-qualified-no-evidence.rq` | SBB `ea:QUALIFIED` + well-formed unambiguous `ea:exactSubject` | `F5_STAGE4_{PIN_MALFORMED, PIN_AMBIGUOUS, EVIDENCE_PREMATURE, QUALIFIED_UNRECORDED}` |
| 5 | `060-stage5-terminal.rq` | `ic:ExecutionEvidence` (`VERIFIED`, `OBSERVED` kind, `producedBy ≠ verifiedBy`, subject = pin) + head-snapshot `ic:Coverage` LIVE | `F5_STAGE5_{EVIDENCE_FOREIGN, STALE_SUBJECT, EVIDENCE_MALFORMED, EVIDENCE_NOT_INDEPENDENT, FRONTIER_UNRECORDED}` |

Two categorical laws govern the ladder.

**Monotonicity.** Stage transitions form a partial order; skipped stages and
regressions are refusals, not corrections:

$$
s_i \prec s_j \;\Rightarrow\; \text{admit}(s_j) \Rightarrow \text{admit}(s_i)
$$

**QUALIFIED is not ALIVE** (RFC §2, Invariant 4). Stage 4's `ea:QUALIFIED`
is a paper state; Stage 5 requires independent observed evidence bound to
the exact subject:

$$
\text{QUALIFIED}(s) \;\land\; \neg\,\text{OBSERVED}(\text{sha}(s))
\;\Rightarrow\; \neg\,\text{ALIVE}(s)
$$

The human role is bounded too: a named human approval appears at Stage 2
with receipt, and `ic:DO` is refused *anywhere* in the graph at that stage —
approval is attribution, never delegated authority.

---

## Chapter 5 — Realization Groups and Multi-Cloud Skeletons

The deployment bridge (RFC §5–6) has three layers.

**Manifest.** `schema/f5ea.sbb-group-manifest.v1.json` types groups with a
closed `domain` enum on the deployment layer (`guest`, `host`, `network`,
`verification`) so nobody borrows EA classes to type a group. Members are
digest-pinned `{iri, digest, role}` references with
`role ∈ {realizes, consumes, verifies}` — a deployment-topology relation,
not an EA classification.

**Lifting.** `queries/170-sbb-group-lifting.rq` CONSTRUCTs
`f5ea:SolutionGroup` individuals only when the reference resolves against
the authoritative EA graph with a matching `ea:exactSubject` digest. A
corrupted manifest cannot inject `rdf:type ea:*` triples through the lift:

$$
\text{lift}(m) \;=\;
\begin{cases}
\text{group} & \text{digest}(m) = \text{digest}(ea) \\
\emptyset & \text{otherwise}
\end{cases}
$$

**Templates.** Per-provider Tera skeletons render once per `f5ea:Realization`
(per-row rendering idiom, `azure-terraform-pack/templates/main.tf.tmpl:1-14`),
producing AAIF-domain-tagged resource descriptions:

| Template | Domains covered | Gates |
|---|---|---|
| `aws-sbb.tf.tera` | IAM Identity Center, Control Tower, Transit Gateway, VPC endpoints, CloudTrail Lake; zero-wildcard IAM | `110-aws-sbb-select.rq`, `120-zero-wildcard-iam.rq` |
| `gcp-sbb.tf.tera` | GKE Enterprise fleet, Shared VPC, PSC, CMEK, Org Policies | `130-gcp-sbb-select.rq`, `140-cmek-and-private-connectivity.rq` |
| `azure-sbb.tf.tera` | Management Groups, Virtual WAN, Guest Configuration, Dedicated HSM, Confidential Computing | `150-azure-nist-800-53-rev5.rq`, `160-azure-sbb-select.rq` |

Wire compatibility: rendered GCP facts map to
`cloudcommerceprocurement.googleapis.com` entities via the
`gcp-marketplace-saas-pack` vocabulary; entitlement suspension revokes PSC
`ACCEPT_MANUAL` approvals, never key material. Azure resources carry
`f5ea:controlMapping` covering NIST SP 800-53 Rev 5 AC-2, SC-28, CM-6. All
templates are skeletons — structural stubs, not live infrastructure;
`bb:directActuation false` is inherited law.

---

## Chapter 6 — Hygiene Laws: The Anti-Alias Fence

The single most dangerous move in a multi-ontology fleet is **semantic
aliasing**: re-declaring someone else's term locally. A local redeclaration
forks the meaning of the term while keeping its name, and every downstream
consumer silently splits into two populations. The hygiene law
(`docs/reference/industry-closure-contract.md:22`, RFC §7) forbids this
absolutely:

> No `ea:`, `togaf:`, `eap:` or `eom:` term is declared, re-typed or
> prefix-declared by this pack. All `ea:` IRIs appear only as
> `rdfs:range` / `sh:class` / `owl:disjointWith` targets.

Categorically, aliasing attempts to construct two distinct objects with one
identity — an arrow the fence refuses at the type level:

$$
\exists f : \texttt{ea:}X \to \texttt{f5ea:}X
\quad \Rightarrow \quad \text{REFUSED:F5\_HYGIENE\_ALIAS}
$$

The pack-local vocabulary `f5ea:` extends the world with *new* names
(`SolutionGroup`, `Realization`, `SbbResource`) and consumes foreign terms
only by IRI as range/class targets. The same repository test binds every
`f5ea:` local name to `packs/fortune5-enterprise-architecture-pack/ontology.ttl`
(RFC falsifier F4: grep the pack for declarations of `ea:`/`togof:` classes —
zero matches ideal).

The deep reason is epistemic, not stylistic: a namespace is a *certification
authority*. Consuming by IRI means the owner's gates continue to govern the
term's meaning after you consume it. Aliasing severs that chain of custody —
it is, in the dissertation's terms, a attempt to forge knowledge that
someone else must keep cryptographic.

---

## Chapter 7 — Kernel Integration and the Admission Boundary

The `ggen-abb-sbb` kernel (RFC §8, PROPOSAL) supplies the admission
boundary: IO-free, `SELECT ∥ MANUFACTURE` admission with `Authority::Do`
always refused (`lib.rs:670-674`). The plan: absorb the crate into the root
workspace, hook `pub fn sync` at the Stage 3/4 boundary
(`ggen-engine/src/sync.rs:816`, post-extract, pre-render, pre-Write), and
route each ABB through `plan(...)`: `Decision::Select` when realization
exists, `Decision::Manufacture` — fail-closed
`AppError::AdmissionRefused` with a typed `Refusal` surviving to the CLI as
JSON — when it does not.

$$
\text{plan}(abb) \;=\;
\begin{cases}
\text{Select} & \text{realization exists} \\
\text{Manufacture} & \text{realization absent, admitted} \\
\text{REFUSED} & \text{Authority::Do attempted}
\end{cases}
$$

The critical fence: `ggen pack new`'s self-pack sync call site inherits the
gate automatically (`ggen-cli/src/cmds/pack.rs:828`), and the boundary
falsifier (F5) is a sync graph with a pack id colliding with an element id
that must error `Refusal::PackConflation` and write no files. Admission
precedes write; nothing that was not admitted ever reaches disk. Cross-repo
transport (RFC §9) is out of pack scope: NDJSON `xaas.sbb-qualification-wire.v1`,
JCS (RFC 8785) canonical bytes, self-describing opaque digests
(`sha256:`/`blake3:` prefixes — never re-hashed); the transport key is
`semantic_identity/1`, and the bridge sits at the receipt-argument level.

---

## Chapter 8 — Conformance Vectors TV-01..TV-05

The system is qualified by five black-box conformance vectors, mechanized in
`packs/fortune5-enterprise-architecture-pack/tests/test_conformance_vectors.py`
— real rdflib execution of the pack's real SPARQL gates against real fixture
graphs. No mocks; zero-rows = pass is the house falsifier shape, ASK gates
are fail-closed (true = PASS).

| Vector | Class of attack | Fixture | Expected verdict |
|---|---|---|---|
| TV-01 | Completeness | multi-tier SBB synthesis fiber: requirement → capability → ABB → approved attributed contract → QUALIFIED SBB with sha256 exact-subject pin → independent VERIFIED OBSERVED evidence → head snapshot LIVE coverage → solution group → AWS/GCP/Azure realizations | full ladder PASS, stage-5 qualified |
| TV-02 | Conflation | group manifest typed as an `ea:` element (DoD #9 collision) | fail-closed |
| TV-03 | Semantic alias | `ea:` term re-declared pack-locally | metamodel hygiene fail-closed |
| TV-04 | Vacuity | vacuous query → vacuous qualification | rejected |
| TV-05 | Procedural mutation | `DO` out of grammar | refused |

Each vector targets a distinct failure class of the categorical system:
TV-01 proves the positive path is *completable* end to end; TV-02 attacks
the identity fence (Chapter 3); TV-03 attacks the namespace fence
(Chapter 6); TV-04 attacks the gate's *meaning* (a gate that passes on an
empty graph carries no bits); TV-05 attacks the authority grammar
(Chapter 7). The five together are the dissertation's falsifier corpus:

$$
\text{QUALIFIED(system)} \;=\; \bigwedge_{i=1}^{5} \text{TV-}i \;\text{verdict} = \text{expected}
$$

A vector that cannot fail is not a vector; a court without a corpus is not
a court.

---

## Chapter 9 — Conclusion and Standing

### 9.1 Hygiene-law artifact

The DoD #9 metamodel-hygiene law (Chapter 6) is canonical at
`packs/fortune5-enterprise-architecture-pack/shapes/00-metamodel-hygiene.shacl.ttl`
— OWL disjointness fence plus the `f5ea:SolutionGroupShape` SHACL node shape
— and is court-qualified by
`packs/fortune5-enterprise-architecture-pack/tests/test_shapes_file.py`
(pyshacl: conflation individual violates, clean group conforms). The inline
copy in `ontology.ttl` is a pack-local duplicate.

Knowledge Cryptography reduces enterprise architecture to four categorical
disciplines: **identity by digest** (`ea:exactSubject` sha256 pins),
**admission by refusal-shaped gate** (zero-rows-equals-pass, ASK
fail-closed), **separation by fence** (OWL disjointness + SHACL
`qualifiedMaxCount 0` + hygiene law), and **qualification by adversarial
vector** (TV-01..TV-05). None of these is novel alone; the contribution is
their composition into a single pipeline where every transition between
them is either admitted or refused, and nothing narrative survives to
actuation.

Standing, honestly stated (RFC §11):

- **ALIVE** — all cited source facts of the underlying RFC (file:line
  verified by the emitting agents).
- **CONSTRUCTED, court-qualified** — the pack vocabulary, queries,
  templates and schema are exercised by the mechanized conformance-vector
  court (`tests/test_conformance_vectors.py`); qualification is exact-subject,
  at the SHA of the court run.
- **PROPOSAL** — gate-court registration, hygiene-contract patch, kernel
  wiring, and cross-repo wire transport remain proposals until their own
  courts run.

QUALIFIED is not ALIVE; a checkpoint on one maturity dimension is not a
crown. The dissertation ends where the discipline begins: every claim in it
is either pinned to an exact subject or marked as not yet claimed.

---

## Bibliography

1. S. Chatman. *RFC: Fortune 5 EA-as-Code — Unified SBB Pack Groups,
   Qualification Ladder, and Multi-Cloud Realization*, v26.10.9 (seed).
   `packs/fortune5-enterprise-architecture-pack/RFC_FORTUNE5_EA_AS_CODE.md`, 2026.
2. S. Chatman. *RFC-STOGAF: enterprise architecture as admitted,
   machine-addressable state*.
   `xaas/docs/rfc/RFC-STOGAF-v26.9.22.md`, 2026.
3. S. Chatman. *abb-sbb-implementation*.
   `ggen/docs/rfc/v26.9.26/abb-sbb-implementation.md`, 2026.
4. S. Chatman. *industry-closure-contract*.
   `docs/reference/industry-closure-contract.md`, ggen-marketplace, 2026.
5. S. Chatman. *fortune5-enterprise-architecture-pack ontology (f5ea:)*.
   `packs/fortune5-enterprise-architecture-pack/ontology.ttl`, 2026.
6. S. Chatman. *TV-01..TV-05 black-box conformance vectors (dissertation
   conformance court)*.
   `packs/fortune5-enterprise-architecture-pack/tests/test_conformance_vectors.py`, 2026.
7. S. Chatman. *cloud-strategy* (TOGAF-as-graph design).
   `~/archive/cloud-strategy.txt:9110-9297`, 2026.
8. Internet Engineering Task Force. *JSON Canonicalization Scheme (JCS)*,
   RFC 8785, 2020.
9. NIST. *Security and Privacy Controls for Information Systems and
   Organizations*, SP 800-53 Rev. 5, 2020.
10. The Open Group. *TOGAF Standard*, Architecture Building Block /
    Solution Building Block metamodel.
