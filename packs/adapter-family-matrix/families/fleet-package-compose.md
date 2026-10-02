# family note: fleet-package-compose (absorbed 2026-09-30)

- Was: `packs/fleet-package-compose` v26.9.27 — "Composes a fleet package plan
  from six consumer registrations and twelve adapter families, with family
  mappings, projection queries, eight admission gates and JSON plan templates…"
- Namespace: `fpc: <https://chatman.ai/fleet-package-compose#>` → replaced by
  `af:` (ontology/conservation.ttl); terms conserved in
  `ontology/fleet-package-compose.ttl`.

## Term mapping (13 records + 2 metaclasses)

fpc:Subject→af:Subject · fpc:Consumer→af:Consumer · fpc:AdapterFamily→af:AdapterFamily ·
fpc:Projection→af:Projection · fpc:subject→af:subject · fpc:consumer→af:consumer ·
fpc:family→af:family · fpc:targetRepo→af:targetRepo · fpc:targetPath→af:targetPath ·
fpc:templateKey→af:templateKey · fpc:sourceSha→af:sourceSha · fpc:authority→af:authority ·
fpc:Class→rdfs:Class · fpc:Property→rdf:Property (metaclasses; only pack in the
cluster that re-declared its own metaclasses).

## Failed edge (conserved, not silently fixed)

Its re-minted `gates/050_source_sha.rq` was INVERTED: it fired on projections
whose SHA matched `^[0-9a-f]{40}$` (i.e. refused valid data, admitted missing/
malformed). The canonical afm_050 restores the majority semantics (fire on
missing/malformed only) and documents the inversion in its gate header. This is
`failed(edge_compose_050) ≠ failed(G)`: the archetype survived; the compose
re-mint's sign error did not.

## Gates absorbed (8 → archetype stems)

010_required_identity/030_target_repo/040_target_path → afm_010 · 020_authority_none →
afm_020 · 060_family_declared → afm_030 · 080_unique_target → afm_040 ·
050_source_sha → afm_050 (inversion noted) · 070_consumer_declared → afm_060.

## Asset disposition

- `mappings/*.ttl` (12 family mappings), `consumers/*.ttl` (6) → superseded by
  this pack's `mappings/*.ttl` + `fixtures/consumers/*.ttl` (superset, af:-native).
- `families/*.ttl` (12) → superseded by this pack's `families/*.ttl`.
- `queries/project_*.rq` (4), `templates/*.tera` (12), `bench/matrix_bench.py` →
  retired; nearest equivalents: this pack's `queries/` + `templates/*.tmpl`.
- `schemas/package-plan.schema.json` → **survives**: unified owner is
  `schemas/package-plan.schema.json` here (union adds templateKey).
- `schemas/{consumer-registry,family-registry}.schema.json` → retired; nearest
  equivalent: `schemas/package-index.schema.json`.
- `fixtures/cs2-fleet.ttl` (one fpc:Subject declaration) → scene conserved as
  `qualification/fixtures/fpc-cs2-subject.ttl`.
- `tests/{determinism,source_boundary}.py` (trivial) → determinism is enforced
  structurally by ORDER BY on every gate; family/template stem correspondence is
  visible by listing `families/*.ttl` vs `templates/*.tmpl`. Not ported.
