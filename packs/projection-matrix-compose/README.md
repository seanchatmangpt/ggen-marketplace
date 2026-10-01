# projection-matrix-compose

Subject-independent RDF projection matrix manufacturing: model subjects,
consumers, adapters and the N×N projection cells as admitted `pm:` individuals;
render consumer bindings and package manifests from them. **Single owner of the
`pm:` namespace** (`https://ggen.dev/ontology/projection-matrix#`).

## Supersession (v0.2.0, 2026-10-01 consolidation wave)

Absorbed and RETIRED:

| retired pack | what moved where |
|---|---|
| `projection-matrix-pack` (v0.1.1, chatmangpt.com IRI) | its 11-term strict subset maps 1:1 onto `ontology/core.ttl` — each old IRI carries a `dcterms:isReplacedBy` conservation record there; its 4 distinct renderer templates (stored twice as byte-identical `.tera`/`.tmpl` pairs) are deduped to the `.tmpl` set; `binding.ttl.tera` (no `.tmpl` twin) is ported to `templates/binding.ttl.tmpl`; its undeclared in-use renderer vocabulary (`sourceIdentity`, `emits`) is now declared in `ontology/bindings.ttl` (recorded failed edge) |
| `cs2-projection-matrix` (v0.1.0, minted THIS IRI) | the two-owners-one-IRI collision is resolved by this pack declaring `pm:` once; `pm:adapterKind` is conserved as a module term in `ontology/cs2-adapter.ttl` together with the cs2 profile's formerly-undeclared vocabulary (`sourceRepository`, `consumerRepository`, `consumerSlug`, `enabled` — recorded failed edge); its query and renderer move here repointed (`queries/cs2-projection-matrix.rq`, `templates/cs2-consumer-manifest.toml.tmpl`) |

## Layout

| path | content |
|---|---|
| `ontology/core.ttl` | Subject/Consumer/Adapter/Projection + core properties + retirement conservation records |
| `ontology/bindings.ttl` | generation contract as declared facts (`pm:Input`, `pm:ProjectionRule`; FM-PACK-003-safe — consumers bind in their own ggen.toml) |
| `ontology/cs2-adapter.ttl` | conserved `pm:adapterKind` + closed `pm:AdapterKind` vocabulary (turtle/json/elixir) + cs2 profile properties |
| `fixtures/` | prefix-named court data: `core_fleet.ttl`, `legacy_fleet.ttl`, `cs2_fleet.ttl` |
| `queries/` | `consumer-bindings.rq` (canonical), `legacy-projection-matrix.rq`, `cs2-projection-matrix.rq` (conserved, repointed) |
| `templates/` | 7 renderers, `.tmpl` only |
| `gates/` + `witnesses/` | exact-stem gate ladder — required identity (`010`), single-valued (`020`), value constraints with adapter-kind anti-join (`030`) — each with synthesized pass/fail witnesses |
| `qualification/verify.py` | the ONE uniform court (exit 0 = ADMITTED) |

## Evidence boundary

Marketplace admission + real-ggen qualification + the exact-stem witness court
only. Projections are consequences: edit the ontology/query/template, never the
generated output. Grants no execution authority; BRCE remains the sole
actuation boundary.
