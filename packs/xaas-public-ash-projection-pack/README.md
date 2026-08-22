# xaas-public-ash-projection-pack

**Purpose:** turn an admitted SHACL application profile over **public ontology terms** into a canonical Ash/Igniter construction program.

```text
public ontology locks
        ↓
public profile qualification
        ↓
SHACL application profile (this pack)
        ↓
SPARQL
        ↓
ggen / Tera
        ↓
xaas-public-ash-GENERATED.sh
        ↓
mix ash.gen.* / Igniter
        ↓
Ash source
```

This pack exists specifically to remove the transitional `xar:RenderTarget` / `xar:moduleName` pattern from the canonical XaaS semantic path. It does **not** declare a replacement XaaS ontology.

## Semantic law

- Local IRIs may identify `sh:NodeShape` / property-shape instances.
- `sh:targetClass` must be a public external class IRI.
- `sh:path` must be a public external RDF property.
- No local `owl:Class`, `rdf:Property`, `owl:ObjectProperty`, or `owl:DatatypeProperty` is admitted.
- Module names are mechanically derived from the public class IRI; they are implementation consequences, not RDF facts.
- Two public classes that derive the same module name are refused rather than guessed around.
- Only datatype properties are projected today. RDF object edges do **not** imply Ash `belongs_to` / `has_one` / `has_many` ownership semantics; relationship projection remains fail-closed until that correspondence is independently admitted.
- ODRL/SOSA/PROV resources remain descriptive/application resources. Their presence never grants BRCE DO authority.

## Initial public projection set

The application profile currently selects public concepts needed by the foundational XaaS competency surface:

- FnO — `Function`, `Mapping`, `Implementation`, `Execution`;
- DCAT — `Resource`;
- W3C ORG — `Organization`, `Role`, `Membership`;
- PROV-O — `Entity`, `Activity`, `Agent`;
- ODRL — `Policy`;
- SOSA — `Observation`, `Actuation`;
- P-PLAN — `Plan`, `Step`;
- QUDT — `QuantityValue`, `Unit`.

Selection is an application-profile decision, not a claim that these vocabularies are mutually equivalent or sufficient for all XaaS competency questions.

## Generate

From this pack directory with the admitted ggen toolchain:

```sh
ggen sync run
```

The disposable output is:

```text
xaas-public-ash-GENERATED.sh
```

Run that generated constructor **inside the target Ash project**. It uses only Ash/Igniter generators for Ash-shaped source mutation and finishes with format, warnings-as-errors compile, `ash.manifest.dump`, and tests.

Generated output is intentionally not committed as semantic source truth.

## Relationship to the other XaaS packs

`xaas-public-ontology-profile` owns public-artifact locks and competency qualification.

`xaas-public-ash-projection-pack` owns the public SHACL → Ash construction projection.

`xaas-ash-core-pack` currently preserves the larger Ash ecosystem research, speedrun, and the transitional 44-capability constructor. Its private `xar:` graph is historical/construction evidence, not the canonical XaaS ontology path.

## Standing

- public-only shape source: **PARTIAL_ALIVE**;
- private XaaS domain vocabulary: **REFUSED by gate**;
- datatype projection: **IMPLEMENTED**;
- object relationship projection: **REFUSED / not admitted**;
- `ggen sync run` on this exact new pack: **NOT YET EXECUTED** until an exact ggen runtime executes this branch;
- generated Ash runtime: **NOT YET EXECUTED** for this public-only projection.
