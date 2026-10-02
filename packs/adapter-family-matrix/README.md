# adapter-family-matrix

Qualified adapter-family contracts for the fleet projection matrix a consumer
resolver and dispatch templates project against. **One pack, one version, one
admission unit, one canonical namespace** — consolidated (v26.9.30 wave) from
the adapter/fleet cluster's seven packs, which were a lane-partition artifact
of parallel minting, not a durable topology: one projection contract re-declared
in six namespaces, 46 re-minted gates over six archetypes, zero byte-identical
files. The consolidation applies the drift law ("N implementations of one
calculus → O(N²) drift; converge on one kernel with N bindings").

## Canonical namespace

`af:` `<https://ggen.dev/ontology/adapter-family#>` — the superset owner's.

The five absorbed namespaces are conserved, not renamed: each survives as
`ontology/<absorbed-pack>.ttl` with its original term declarations plus
`owl:equivalentClass` / `owl:equivalentProperty` mappings onto `af:`, and each
namespace IRI carries a `dcterms:isReplacedBy` record in
`ontology/conservation.ttl`. `fleet-projection-closure`
(`fp: <https://ggen.dev/ontology/fleet-projection#>`) is **not** absorbed: it
stays a separate profile pack holding the exact-subject instance triples.

## Layout

| path | content |
|---|---|
| `ontology.ttl` | canonical `af:` core (extended by the absorption: `af:Subject`, `af:moduleName`, `af:packageName`, `af:mediaType`, `af:name`, `af:fileExtension`, `af:templatePath`, `af:deterministic`) |
| `ontology/<absorbed>.ttl` | conserved vocabulary modules (afr, fm, fp, fpc, fr) with equivalence axioms |
| `ontology/conservation.ttl` | namespace-level `dcterms:isReplacedBy` records |
| `families/*.ttl` | 12 `af:AdapterFamily` individuals (json, elixir, sql, protobuf, openapi, graphql, jsonschema, jsonld, rust, python, typescript, yaml) |
| `families/<absorbed-pack>.md` | per-absorbed-pack provenance: term mapping, asset disposition, failed edges |
| `gates/` | 9 violation-row SELECTs: 8 canonical `afm_` archetype stems + conserved `fr_060_repo_shape` (was 46 gates across the cluster; the 4 fleet-projection-closure profile gates are unchanged in that pack) |
| `witnesses/{pass,fail}/<stem>.ttl` | exact-stem witnesses — pass silent, fail proven to fire |
| `qualification/verify.py` | the ONE uniform court (exact-stem, exit 0 = ADMITTED) |
| `qualification/fixtures/` | absorbed packs' data scenes, re-expressed in canonical `af:` under the conservation records |
| `fixtures/` | this pack's own positive consumers + targeted negatives (af:-native) |
| `mappings/`, `templates/*.tmpl`, `queries/`, `schemas/` | superset manufacture assets owned here before the wave, unchanged unless noted below |

## Schema unification

`schemas/package-plan.schema.json` is the ONE owner of the near-identical
package-plan schema previously minted by fleet-package-compiler and
fleet-package-compose (the two differed only in JSON key order); the union adds
`templateKey` to the required set. This pack's former
`schemas/projection.schema.json` was a strict subset of the union and is
subsumed. `schemas/package-index.schema.json` (consumer/repository/artifacts
shape) is a different schema and stays.

## Court

```bash
python3.11 qualification/verify.py   # exit 0 = ADMITTED (9/9 exact-stem cases)
```

`gate-court.toml` registers the same court structurally
(`ggen.semantic-gate-witness-court/1`, exact-stem) for the repo-wide scanner.

## Consumer join doctrine

Projections reference families by `af:templateKey` literals and consumers by
declared `af:Consumer` individuals; the join happens in the consumer resolver /
dispatch templates (`templates/*.tmpl` frontmatter SPARQL), never as cross-pack
imports.

## Invariants (encoded as gates)

Projection identity complete · Authority NONE (observation ceiling; BRCE remains
the sole actuation boundary) · Family declared + keyed · Unique (repo, path)
target · Exact 40-hex source SHA · Consumer declared · No self-consumer ·
Non-empty target strings · Owner/repo-shaped target repo.

## Supersession

Replaces `adapter-family-registry` (0.1.1), `fleet-adapter-matrix` (0.1.0),
`fleet-package-compiler` (0.1.0), `fleet-package-compose` (26.9.27),
`fleet-family-registry` (0.1.0) — vocabulary conserved via equivalence records,
gate archetypes collapsed to the one ladder, per-pack assets dispositioned in
`families/<absorbed-pack>.md`. `fleet-projection-closure` (26.9.27) intentionally
stays: its 470 exact-subject instance triples are lifecycle keep-separate
profile data, and it references none of the absorbed pack names.
