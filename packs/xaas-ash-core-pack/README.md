# xaas-ash-core-pack

TOGAF-scoped, public-ontology-first construction of Ash applications.

## Non-negotiable semantic boundary

This pack does **not** define a private XaaS ontology and does not copy the old
44-capability JavaScript array into Turtle. Moving a hard-coded application
taxonomy from JavaScript into RDF would preserve the same defect in a different
syntax.

The semantic direction is:

```text
public ontology artifacts
        ↓
admission + locks + application profile
        ↓
public SHACL target classes/properties
        ↓
SPARQL projection
        ↓
ggen
        ↓
generated Ash/Igniter construction program
        ↓
mix ash.gen.*
        ↓
Ash source
```

`ontology.ttl` therefore identifies the application profile and its authorities
but declares **zero local `owl:Class` or RDF/OWL property vocabulary**.
`profiles/public-shapes.ttl` is initially empty on purpose. Public mappings are
admitted only after the referenced ontology artifacts are pinned and qualified.

TOGAF is used as the scope/governance lens for the whole enterprise architecture
problem. It is not treated as an RDF ontology. The complete coverage matrix is
in `reference/togaf-scope.toml`.

## Why ggen renders the generator program

Ash 3.32.0 owns the canonical source mutation semantics through Igniter. The
resource generator creates missing domains, registers resources, adds
attributes/relationships/actions supported by its CLI, and composes
`ash.extend`. For Ash-shaped work covered by that surface, this pack therefore
renders commands such as `mix ash.gen.resource` instead of rendering `.ex`
files directly.

The output `generated/xaas-ash.gen.sh` is disposable. It is not semantic truth
and is ignored by git.

## Current admitted projection

The first projection intentionally supports only:

1. one Ash resource per admitted public `sh:NodeShape/sh:targetClass`; and
2. Ash attributes for SHACL property shapes with a supported public RDF
   datatype.

It deliberately refuses to infer Ash relationship ownership from RDF object
properties. RDF edge direction and SHACL cardinality do not, by themselves,
prove whether the correct Ash persistence realization is `belongs_to`,
`has_one`, or `has_many`. Gate
`060_object_property_projection_pending.rq` keeps that boundary fail-closed.

Likewise, unsupported RDF datatypes are refused rather than silently coerced.

## Naming

The initial proof derives `Xaas.Public.<IRI-local-name>` from the public target
class IRI. No private namespace table is smuggled into the ontology. A collision
gate refuses public classes with the same local name. A later projection policy
may solve collisions, but it must remain implementation configuration rather
than ontology semantics.

## TOGAF scope

The architecture program covers Business, Data, Application, and Technology
Architecture plus the full change loop: preliminary architecture capability,
requirements management, vision, opportunities/solutions, migration,
implementation governance, and architecture change management.

This scope is intentionally larger than the current generated Ash surface.
`reference/togaf-scope.toml` is the competency-question backlog that the public
ontology profile must close. A scope item does not become "covered" because a
similarly named local class was invented.

## Validation gates

All gates return rows for violations.

- `010_no_custom_vocabulary.rq`: refuses local XaaS classes/properties.
- `020_public_target_classes.rq`: refuses local/non-IRI SHACL target classes.
- `030_profile_well_formed.rq`: checks basic property-shape structure.
- `040_resource_name_collisions.rq`: refuses ambiguous generated module names.
- `050_supported_datatypes.rq`: refuses unknown datatype→Ash mappings.
- `060_object_property_projection_pending.rq`: refuses unproved relationship
  generation.

## Run

From this pack directory with the pinned ggen toolchain available:

```bash
ggen sync run --dry-run
ggen sync run
```

Until at least one public SHACL target class is admitted,
`generated/xaas-ash.gen.sh` is expected to contain a typed refusal:

```text
REFUSED:NO_ADMITTED_PUBLIC_ASH_RESOURCES
```

That is correct standing. The constructor exists; the public semantic mapping
has not yet been admitted.

After mappings are admitted, execute the generated script **inside the intended
Ash consumer project**, not inside the marketplace source repository.

## Next semantic step

For each TOGAF competency area:

1. identify public ontology candidates;
2. pin and materialize exact artifacts;
3. record publisher/status/license/digest/import closure;
4. test competency questions against the public graph;
5. add SHACL application-profile shapes only for public terms that survive
   admission;
6. add XaaS-native semantics only when a competency question remains
   unanswerable after public mappings are exhausted.

No `xar:renderOf`, `xar:moduleName`, `xar:domainModule`, or equivalent private
bridge vocabulary is required for the current projection.
