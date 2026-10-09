# Fortune 5 EA-as-Code Pack — Fleet Reference

Reference for
[`packs/fortune5-enterprise-architecture-pack/`](../../packs/fortune5-enterprise-architecture-pack/)
as consumed across the fleet. Authoritative pack specification:
[`RFC_FORTUNE5_EA_AS_CODE.md`](../../packs/fortune5-enterprise-architecture-pack/RFC_FORTUNE5_EA_AS_CODE.md).
Companion to [`FLEET-SEMANTIC-MAP.md`](FLEET-SEMANTIC-MAP.md) (semantic A2A +
sjira plane, v26.10.8) and [`FLEET-DOC-MAP.md`](FLEET-DOC-MAP.md).

## Authority law

The pack's authority posture is **`NONE` / ceiling `SELECT`**, the same
grammar the fleet uses everywhere else:

- `pack.toml` declares authority `NONE`, ceiling `SELECT` — the pack can
  select among existing qualified SBB realizations and CONSTRUCT
  projections (manifests, lifted groups, rendered Terraform skeletons);
  it cannot actuate.
- Stage 2 of the qualification ladder refuses any `?s ?p ic:DO` triple
  outright (`queries/030-stage2-contract-approved.rq`) — DO out of grammar
  is TV-05, refused fail-closed
  (`tests/test_conformance_vectors.py::test_tv05_procedural_mutation_do_out_of_grammar`).
- This mirrors the ggen ABB/SBB kernel law
  (`ggen-abb-sbb/src/lib.rs`: `plan → Decision::Select`/`Decision::Manufacture`,
  `Authority::Do` always refused), where the marketplace pack is DoD #8's
  end-to-end fixture (standing ALIVE,
  `ggen/docs/rfc/v26.9.26/abb-sbb-implementation.md`, kernel/falsifier map).
- Rendered Terraform templates are skeletons with `bb:directActuation false`
  inherited from `fortune5-deployment-blocks-pack`; existence of a rendered
  file confers no actuation authority.

## Three pairwise-disjoint subcategories (DoD #9)

RFC v26.9.26 DoD #9 — "Never make Pack == ABB or Pack == SBB" — is mechanized
in the pack as **three** pairwise-disjoint subcategories, not a two-sided
special case:

| Subcategory | Carrier | Fence |
|---|---|---|
| Pack (`f5ea:SolutionGroup`) | clustering receipt over guest/host/network/verification domains | `owl:AllDisjointClasses` + SHACL `qualifiedMaxCount 0` in `ontology.ttl`; `references_only: const true` in the manifest schema |
| ABB (`ea:ArchitectureBuildingBlock`) | consumed by full IRI, never declared pack-locally | hygiene law: no `ea:`/`togaf:`/`eap:`/`eom:` term declared or re-typed (`docs/reference/industry-closure-contract.md:22`; semantic owner `chatman-ecosystem#296`) |
| SBB (`ea:SolutionBuildingBlock`) | digest-pinned `{iri, digest, role}` manifest references | lifting only through `queries/170-sbb-group-lifting.rq` with matching `ea:exactSubject` digest |

Enforcement: `tests/test_dod9_fences.py` (pairwise disjointness, ρ-dangling,
Girard fence, fiber completeness — each with an anti-vacuity mutation test),
plus the kernel-side falsifiers
`pack_named_as_abb_or_sbb_is_refused` /
`pack_colliding_with_any_element_id_is_refused_without_a_pack_list`
(`crates/ggen-abb-sbb/tests/falsifiers.rs:513,545`, DoD 9 row, standing ALIVE).

## The qualification ladder

Six stages, zero-rows-equals-pass gates (`queries/010..060`), with
whole-ladder monotonicity enforced by `queries/100-ladder-monotonicity.rq`
(skip a stage or regress and the monotonicity gate fires). Stage 5 is the
terminal admission gate: independent `ic:ExecutionEvidence` (producer ≠
verifier, subject == `ea:exactSubject` pin) plus head-snapshot LIVE coverage
— "QUALIFIED is not ALIVE" mechanized. Full stage/refusal table in the pack
[`README.md`](../../packs/fortune5-enterprise-architecture-pack/README.md).

## Relation to the dissertation

The dissertation [`docs/dissertation/KNOWLEDGE-CRYPTOGRAPHY-DISSERTATION.md`](../dissertation/KNOWLEDGE-CRYPTOGRAPHY-DISSERTATION.md)
(*Categorical Foundations of Knowledge Cryptography*, October 2026) is the
pack written as theory: its reconstruction provenance note names the pack's
own files (`RFC_FORTUNE5_EA_AS_CODE.md`, `ontology.ttl`, `queries/*.rq`,
`tests/test_conformance_vectors.py`) as the canonical sources, and its
mechanization note points at `tests/test_conformance_vectors.py` for
TV-01..TV-05.

- **Knowledge cryptography = the pack's fence set**: exact identity
  (stage-4 `ea:exactSubject` sha256 pinning), fail-closed verification
  (zero-rows-equals-pass gates), third-party replayability (real rdflib gate
  executions over real fixture graphs, no mocks). The dissertation's
  "narrative cannot refuse" thesis is the pack's zero-rows law stated as
  epistemology.
- **Chapter 3 identity fence = DoD #9**: the
  Pack/ABB/SBB pairwise disjointness above is the dissertation's identity
  fence at pack scale. The Grothendieck-fibration reading (base = EA layer,
  fiber = deployment realizations per ABB, Cartesian lift =
  `170-sbb-group-lifting.rq`, fiber completeness = surjective tier coverage
  + acyclic member DAG) is the categorical statement of why the fence is
  structural and not a naming convention.
- **Chapter 4 ladder = the pack's ladder**: the six stages are the same
  gates; the dissertation adds the epistemological reading (refusal-shaped
  admission is the only admission that scales).
- **Chapter 8 = TV-01..TV-05**: the dissertation's conformance court is
  mechanized in the pack's tests — fiber completeness, conflation
  injection, semantic alias, vacuous query, procedural mutation — each with
  a falsifier twin (`tests/test_dod9_fences.py`,
  `tests/test_conformance_vectors.py`).

The ggen-side kernel/falsifier map
(`ggen/docs/rfc/v26.9.26/abb-sbb-implementation.md`, DoD 9 row, standing
ALIVE) is the manufacture-seed counterpart: the pack holds the deployment
fiber, the kernel holds the manufacture law, and DoD #8's
`marketplace_fixture_is_the_exact_admitted_projection` binds the two.

## Relation to the semantic wave (v26.10.8)

The pack participates in the v26.10.8 semantic wave as the Fortune 5
EA-as-Code surface of the marketplace hub (workgraph:
`docs/sjira/v26.10.8/WORKGRAPH.ttl`, 6 typed `sj:WorkOrder` subjects,
re-counted on this branch 2026-10-08; the workgraph was last touched by
`b372fd334` — see [`FLEET-SEMANTIC-MAP.md`](FLEET-SEMANTIC-MAP.md) §1):

- **Authority posture parity**: the pack's `NONE`/`SELECT` matches the
  wave-wide agent-card finding — all six card surfaces carry authority
  NONE / CONSTRUCT-at-most, and no card grants DO authority by existence.
- **Exact-subject discipline**: the stage-4 `ea:exactSubject` sha256 pin and
  stage-5 evidence-subject equality are the same exact-subject qualification
  law the wave's receipts carry; "evidence subject == pin" is the pack-local
  shape of receipt-bound replay.
- **Independent producer/verifier**: stage 5 refuses evidence where
  `producedBy == verifiedBy` — the same Chicago separation the wave's courts
  use (a court is not the generator it judges).
- **Zero-rows-equals-pass**: the gate shape matches the hub's sjira SHACL
  validators (`f6bb82dfb`, `78e1481a1`) — real queries over real graphs,
  refusal as the primary output.

Validation surface (re-counted on this branch 2026-10-09): the f5ea
validator (`scripts/validate_f5ea_graph.py` — SHACL sweep over f5ea
SolutionGroup graphs, fixtures + TV-01 fiber modes) and the resource-graph
generator (`packs/fortune5-enterprise-architecture-pack/scripts/gen_resource_graph.py`
— renders `.tf` fixtures into f5ea resource graphs) back the conformance
vectors (`tests/test_conformance_vectors.py`, incl. TV-06
dangling-SBB SHACL violation). Pack suite:
`python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/ -q`
→ 96 passed, 0 failed (2026-10-09).

Current standing: pack tests green (96 passed, 2026-10-09:
`python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/ -q`),
kernel integration PARTIAL_ALIVE (kernel not yet wired into
ggen-cli/ggen-engine/sync; EA graph still a JSON projection in the kernel —
see the RFC's standing section). Rendered infrastructure remains
BLOCKED:vendor-onboarding in the commerce plane; pack projections are
CONSTRUCT-only.

## See Also

[`FLEET-SEMANTIC-MAP.md`](FLEET-SEMANTIC-MAP.md) ·
[`FLEET-DOC-MAP.md`](FLEET-DOC-MAP.md) ·
[`industry-closure-contract.md`](industry-closure-contract.md) ·
[`CONFORMANCE-COURTS.md`](CONFORMANCE-COURTS.md)
