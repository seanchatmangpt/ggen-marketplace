# fortune5-enterprise-architecture-pack

Fortune 5 **EA-as-Code**: heterogeneous SBB realization groups, a 6-stage
ABB/SBB qualification ladder, and per-provider (aws/gcp/azure) SBB
realization skeletons. Authority `NONE`, ceiling `SELECT`.

Authoritative specification: [`RFC_FORTUNE5_EA_AS_CODE.md`](RFC_FORTUNE5_EA_AS_CODE.md).

## Orthogonality: deployment topology layer vs enterprise architecture layer

This pack declares **deployment SBB solution groups** — provider-projected
clusters of realizations arranged across guest/host/network/verification
domains. It does not declare, contain, equal, or type-assert any
enterprise-architecture element.

Every member of every group in this pack is one of two things, and never
anything else:

1. a **ggen pack identity** (a manufacturing contract, resolved through
   `ggen bblock plan`/`enable` into `.ggen/bblocks/` artifacts); or
2. a **reference** to a pre-existing `ea:SolutionBuildingBlock` individual,
   carried as `{iri, digest, role}` in a manifest conforming to
   [`schema/f5ea.sbb-group-manifest.v1.json`](schema/f5ea.sbb-group-manifest.v1.json).

No group, pack, directory, or receipt in this pack is an
`ea:ArchitectureBuildingBlock` or an `ea:SolutionBuildingBlock`. The two
layers meet only through `sbb_references`, which point at EA individuals
they did not create and cannot modify.

This is the RFC v26.9.26 DoD #9 fence, quoted exactly:

> "Never make Pack == ABB or Pack == SBB."

(`/Users/sac/ggen/docs/rfc/v26.9.26/abb-sbb-implementation.md`, Definition of
done item 9; standing ALIVE per the kernel/falsifier map, DoD 9 row; enforced
by `pack_named_as_abb_or_sbb_is_refused` and
`pack_colliding_with_any_element_id_is_refused_without_a_pack_list` at
`/Users/sac/ggen/crates/ggen-abb-sbb/tests/falsifiers.rs:513` and `:545`.)

The deployment layer answers **where and with what packs a capability is
stood up** (aws/azure/gcp projection, dependency closure, directory law). The
EA layer answers **why the capability exists and what realizes it**
(Strategy → Capability → ABB → contract → SBB → qualification → evidence).
Keeping them orthogonal means an SBB can be deployed zero, one, or many times
across providers without its architecture identity changing, and a group's
provider variants can change without touching the EA graph.

## Hygiene law

Per `docs/reference/industry-closure-contract.md:22`, this pack never
declares, re-types or prefix-declares an `ea:`/`togaf:`/`eap:`/`eom:` term.
All `ea:` terms are consumed by full IRI; the semantic owner is
`seanchatmangpt/chatman-ecosystem#296`. Pack-local vocabulary lives in
`f5ea:` (`https://ggen.io/ontology/fortune5-enterprise-architecture#`).

## Layout

```
pack.toml                  authority NONE / ceiling SELECT
ontology.ttl               f5ea: vocabulary (groups, resources, fences)
schema/
  f5ea.sbb-group-manifest.v1.json   group manifest (references_only=true)
queries/
  010..060  6-stage qualification ladder gates (zero rows = pass)
  100       whole-ladder monotonicity gate
  110..160  provider select/ASK gates (aws, gcp, azure)
  170       manifest -> f5ea:SolutionGroup CONSTRUCT lifting
templates/
  aws-sbb.tf.tera  gcp-sbb.tf.tera  azure-sbb.tf.tera
tests/
  test_dod9_fences.py
  test_qualification_ladder.py
  test_provider_templates.py
  test_conformance_vectors.py
```

## Architecture: three pairwise-disjoint subcategories

RFC v26.9.26 DoD #9 ("Never make Pack == ABB or Pack == SBB",
`/Users/sac/ggen/docs/rfc/v26.9.26/abb-sbb-implementation.md`, standing ALIVE
per the kernel/falsifier map, DoD 9 row) is mechanized here as three
pairwise-disjoint subcategories over the pack's object surface, never two:

| Subcategory | Carrier in this pack | Fence |
|---|---|---|
| **Pack** (`f5ea:SolutionGroup`) | clustering receipt over deployment domains (guest/host/network/verification); `pack.toml` identity | `owl:AllDisjointClasses` + SHACL `qualifiedMaxCount 0` in `ontology.ttl`; `references_only: const true` in `schema/f5ea.sbb-group-manifest.v1.json` |
| **ABB** (`ea:ArchitectureBuildingBlock`) | consumed by full IRI; never declared pack-locally | `ea:`/`togaf:`/`eap:`/`eom:` terms never declared or re-typed (hygiene law above) |
| **SBB** (`ea:SolutionBuildingBlock`) | referenced as digest-pinned `{iri, digest, role}` in manifests | lifting query `queries/170-sbb-group-lifting.rq` only lifts resolved, digest-matching references; a corrupted manifest cannot inject `rdf:type ea:*` |

Pairwise disjointness means any two of the three may not share an individual,
so conflation of Pack with ABB, Pack with SBB, or ABB with SBB is one fence
with three horns, not a Pack-vs-SBB special case.

## Grothendieck fibration model

Reading the metamodel categorically: the deployment layer sits over the EA
layer as a fibration, and the qualification ladder is the discipline on the
fiber over each ABB.

- **Base category**: the EA layer
  (`ea:Strategy → ea:Capability → ea:ArchitectureBuildingBlock →
  ea:ArchitectureContract → ea:SolutionBuildingBlock`), owned externally and
  consumed by IRI — this pack cannot modify the base.
- **Fiber over an ABB** `p⁻¹(ABB)`: the SBB realizations and their deployment
  clusters — exactly the objects this pack declares
  (`f5ea:SolutionGroup`, `f5ea:Realization`, manifests, templates).
- **Cartesian lift**: `queries/170-sbb-group-lifting.rq` is the lifting
  operation — a group over an ABB exists only when each member reference
  resolves against the base with a matching `ea:exactSubject` digest. A
  corrupted manifest cannot manufacture a fiber element.
- **Fiber completeness** (DoD #9 fence 4,
  `tests/test_dod9_fences.py`): each `f5ea:SolutionGroup`'s member dependency
  DAG is acyclic and its tier coverage is surjective onto the closed
  four-tier universe {guest, host, network, verification} — the fiber over an
  ABB is checked, not assumed.
- **Synthesis fiber** (TV-01): the full base path
  requirement → capability → ABB → approved attributed contract → QUALIFIED
  SBB (sha256 pin) → independent `ic:OBSERVED` evidence → head-snapshot LIVE
  coverage → solution group → per-provider realizations is one complete fiber
  element, and `test_tv01_synthesis_fiber_completeness_admitted_at_stage5`
  witnesses that the ladder admits exactly this element and nothing shorter.

## Six-stage qualification ladder

Zero-rows-equals-pass gates, one per file (`queries/010..060`), per RFC §4;
`queries/100-ladder-monotonicity.rq` refuses skipped stages and regressions.

| Stage | Gate file | Fires (refuses) when |
|---|---|---|
| 0 | `queries/010-stage0-closure.rq` | IN_SCOPE requirement lacks an OPEN `DEFICIT_ABB` residual — `REFUSED:F5_STAGE0_ABB_DEFICIT_UNRECORDED` |
| 1 | `queries/020-stage1-contract-pending.rq` | ABB + contract not `PENDING_HUMAN_APPROVAL`, claim ≠ `NONE`, approval premature — `REFUSED:F5_STAGE1_*` |
| 2 | `queries/030-stage2-contract-approved.rq` | Approval unattributed, any `ic:DO` triple present, SBB premature — `REFUSED:F5_STAGE2_*` |
| 3 | `queries/040-stage3-sbb-candidate.rq` | Contract not approved, SBB not `ea:CANDIDATE`, candidate unrecorded — `REFUSED:F5_STAGE3_*` |
| 4 | `queries/050-stage4-qualified-no-evidence.rq` | Pin malformed/ambiguous, evidence premature, qualification unrecorded — `REFUSED:F5_STAGE4_*` |
| 5 | `queries/060-stage5-terminal.rq` | Evidence foreign/stale/malformed/not independent (producer ≠ verifier), frontier unrecorded — `REFUSED:F5_STAGE5_*` |

## Provider matrix

Per-provider Tera skeletons (`templates/`), rendered once per
`f5ea:Realization`; each renders AAIF-domain-tagged `f5ea:SbbResource`
facts. All templates are skeletons — `bb:directActuation false` law
inherited.

| Template | Provider law | Domains covered | Gates |
|---|---|---|---|
| `templates/aws-sbb.tf.tera` | zero-wildcard IAM: closed action maps, no `"*"` in any IAM action; explicit region | IAM Identity Center, Control Tower, Transit Gateway, VPC endpoints, CloudTrail Lake | `queries/110-aws-sbb-select.rq`, `queries/120-zero-wildcard-iam.rq` |
| `templates/gcp-sbb.tf.tera` | CMEK (KMS keys reference the key ring), no public IP, no-public-ingress org policy default | GKE Enterprise fleet, Shared VPC, PSC, CMEK, Org Policies | `queries/130-gcp-sbb-select.rq`, `queries/140-cmek-and-private-connectivity.rq` |
| `templates/azure-sbb.tf.tera` | NIST SP 800-53 Rev 5: every resource carries `f5ea:controlMapping` covering AC-2, SC-28, CM-6 | Management Groups, Virtual WAN, Guest Configuration, Dedicated HSM, Confidential Computing | `queries/150-azure-nist-800-53-rev5.rq`, `queries/160-azure-sbb-select.rq` |

## Test vectors (TV-01..TV-05)

`tests/test_conformance_vectors.py` runs the pack's real SPARQL gates via
real rdflib against fixture graphs — no mocks. Zero rows = pass; ASK gates
are fail-closed (true = PASS).

| Vector | Injects | Required verdict | Test |
|---|---|---|---|
| TV-01 | complete multi-tier synthesis fiber | stage-5 admission; removing the pin breaks stage 4 | `test_tv01_synthesis_fiber_completeness_admitted_at_stage5`, `test_tv01_falsifier_removing_the_pin_breaks_stage4` |
| TV-02 | Pack/SBB conflation (DoD #9 collision) | fail-closed | `test_tv02_conflation_injection_fail_closed` |
| TV-03 | `ea:` term re-declared pack-locally (semantic alias) | metamodel-hygiene fail-closed | `test_tv03_semantic_alias_metamodel_hygiene` |
| TV-04 | vacuous query | vacuous qualification rejected; a real defect makes the gate non-zero | `test_tv04_vacuous_query_rejected`, `test_tv04_falsifier_gate_goes_nonzero_on_real_defect` |
| TV-05 | procedural mutation (DO out of grammar) | refused | `test_tv05_procedural_mutation_do_out_of_grammar` |

## Running the tests

```bash
python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/test_dod9_fences.py -v
python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/test_qualification_ladder.py -v
python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/test_provider_templates.py -v
python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/test_conformance_vectors.py -v
```

Each command runs real gates against real files on disk (Chicago discipline:
the SPARQL gates, the ontology, and the templates are the collaborators;
nothing is mocked).
