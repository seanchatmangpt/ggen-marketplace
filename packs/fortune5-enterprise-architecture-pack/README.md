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
```
