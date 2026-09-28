# xaas-public-ash-projection-pack

**Purpose:** turn an admitted SHACL application profile over **public ontology terms** into a canonical Ash/Igniter construction program.

**Since 0.2.0 this is a thin compatibility pack.** It owns only its application-profile data
(`ontology.ttl`). The generator-command projection (`queries/ash-gen-commands.rq`,
`templates/gen-commands.sh.tmpl`) and all admission gates are owned by
[`xaas-ash-core-pack`](../xaas-ash-core-pack/) and referenced from `ggen.toml` as
`../xaas-ash-core-pack/...` (never copied). The output path `xaas-public-ash-GENERATED.sh`
and its command content are unchanged for existing consumers
(`.github/workflows/xaas-public-ash-projection.yml`). A shape is excluded from the
projection with the standard SHACL `sh:deactivated true`.

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

`xaas-ash-core-pack` owns the public SHACL → Ash construction projection (query, template,
gates) plus the larger Ash ecosystem research. `xaas-public-ash-projection-pack` owns only the
initial public application-profile selection and composes the core pack.

## Standing

- public-only shape source: **PARTIAL_ALIVE**;
- private XaaS domain vocabulary: **REFUSED by gate**;
- datatype projection: **IMPLEMENTED**;
- object relationship projection: **REFUSED / not admitted**;
- `ggen sync run` (ggen 26.9.18, twice, byte-identical) through the composed core pack: **ALIVE** in marketplace qualification;
- generated Ash runtime: **NOT YET EXECUTED** for this public-only projection.
