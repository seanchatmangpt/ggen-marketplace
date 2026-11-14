# ggen-marketplace-01

Standing: UNVERIFIED

Title: azure-terraform-pack legacy SHACL shapes migrated to sync-time gates

## Problem

`/Users/sac/ggen-marketplace/packs/azure-terraform-pack/pack.toml` (line 6) records that the
155-line closed-shape
SHACL file was relocated to `reference/legacy-shacl-shapes.ttl` because `ggen sync run`
refuses any root-level `shapes.ttl`. Migration to `gates/*.rq` was "not attempted".
`/Users/sac/ggen-marketplace/packs/azure-terraform-pack/` has no `gates/` dir, so sync-time
validation of the pack
is absent. `STANDING.md` still cites `--shapes
/Users/sac/ggen-marketplace/packs/azure-terraform-pack/shapes.ttl`,
a path that no longer exists.

## Acceptance

- `ls /Users/sac/ggen-marketplace/packs/azure-terraform-pack/gates/*.rq` lists at least one gate
  per closed shape.
- `grep -n "shapes.ttl" /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md` returns
  only text
  pointing at `reference/legacy-shacl-shapes.ttl`.
- `ggen sync run` in a scratch consumer exits 0 and a mutated instance (bad `sh:in`
  value) makes a gate refuse with a typed message.

## Falsifier

A gate set that exits 0 on an instance violating a `sh:in` enum from the legacy file.

## Owned files

- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/gates/ (new)
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/pack.toml

## Depends-on

None.

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/pack.toml : 10 lines
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md : 142 lines
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/reference/legacy-shacl-shapes.ttl : 155
  lines
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/ : 14 files, 1649 lines total (find|xargs
  wc -l)
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/gates/ : NEW (0 lines, to be created; est.
  LOC: ~150 across ~6-10 .rq files; basis: ~one gate per closed shape in 155-line legacy file,
  ~15-25 lines each)
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/shapes.ttl : NEW (0 lines, to be created;
  est. LOC: 0; basis: path no longer exists; cited only as stale reference)

## Result

Standing: UNVERIFIED (authored, nothing executed)

Files (all under /Users/sac/ggen-marketplace/packs/azure-terraform-pack/): gates/010_container_group.rq,
gates/020_container.rq, gates/030_evidence.rq (one gate per closed shape: sh:in enums, cardinality,
class, pattern, closed-shape; typed AZTF_* messages); STANDING.md (shapes.ttl ref now points at
reference/legacy-shacl-shapes.ttl); pack.toml (migration note updated).

Acceptance for coordinator: `ls .../gates/*.rq`; `grep -n shapes.ttl .../STANDING.md`; scratch consumer
`ggen sync run` exits 0, then mutate instance osType to "Solaris" and confirm the gate refuses with
AZTF_ENUM_OSTYPE. Unverified risk: the gate-runner row-count semantics and the OPTIONAL/VALUES missing-property form.

## Repair

Standing: UNVERIFIED. Audit W7-02 HIGH+MED fixed in gates/010,020,030 (not executed): bound
`?subject a <Class>` inside every MIN_PROPERTY/MIN_CONTAINER/MIN_EVIDENCE UNION branch; enum
checks require xsd:string datatype; cpuCores/memoryGb require xsd:decimal. pack.toml wording
softened. Rerun: `ggen sync run` on a scratch consumer with two ContainerGroups (one missing
aztf:osType) and expect a typed AZTF_MIN_PROPERTY row.
