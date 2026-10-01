# family note: fleet-adapter-matrix (absorbed 2026-09-30)

- Was: `packs/fleet-adapter-matrix` v0.1.0 — "Project-profile scaffold for a fleet
  projection matrix: RDF vocabulary (fm:Projection, fm:AdapterFamily), 12
  adapter-family declarations, 6 consumer declarations, 12 fixtures, SPARQL
  guards…"
- Namespace: `fm: <https://ggen.dev/ontology/fleet-matrix#>` → replaced by `af:`
  (ontology/conservation.ttl); terms conserved in `ontology/fleet-adapter-matrix.ttl`.

## Term mapping (11 records)

fm:Projection→af:Projection · fm:AdapterFamily→af:AdapterFamily · fm:subject→af:subject ·
fm:consumer→af:consumer · fm:adapterFamily→af:family · fm:targetRepo→af:targetRepo ·
fm:targetPath→af:targetPath · fm:key→af:templateKey · fm:templateKey→af:templatePath (new) ·
fm:deterministic→af:deterministic (new) · fm:authority→af:authority.

## Recorded drift (the reason this consolidation exists)

`fm:key` held the template key string while `fm:templateKey` held a template PATH
("templates/elixir.tera") — same local name, opposite semantics vs every other
cluster namespace. The fm: family individuals (families/*.ttl) used both without
their ontology declaring either. Conservation disambiguates:
fm:key≡af:templateKey, fm:templateKey≡af:templatePath. Failed edge recorded; not
silently normalized.

## Gates absorbed (8 guards → archetype stems)

010/020/030/040/050_guard (per-property presence) → afm_010 · 060_guard
(authority) → afm_020 · 070_guard (family declared) → afm_030 · 080_guard
(unique target) → afm_040.

## Asset disposition

- `families/*.ttl` (12 fm: family individuals), `consumers/*.ttl` (6), CSV
  mappings (family-template, family-extension, consumer-package) → superseded by
  this pack's `families/*.ttl` + `mappings/*.ttl` (superset, af:-native).
- `fixtures/consumer-01..12-*.ttl` → scene conserved as
  `qualification/fixtures/fm-consumer-json.ttl` (representative; the 12 were
  one-projection-each repeats of the same shape).
- `templates/*.tera` (12) → retired; nearest equivalent: this pack's
  `templates/<family>.tmpl` dispatch set.
- `queries/project_*.rq` (6) → retired; nearest equivalent: this pack's
  `queries/project_*.rq` (5, superset).
- `schemas/{family,package,projection}.schema.json` → retired; nearest
  equivalent: `schemas/package-plan.schema.json` (unified owner).
- `bench/bench_projection_matrix.py`, `bench/stress_fixture.py` → retired
  (single-use benches over fm: IRIs).
- `tests/test_*.py` (5, trivial constant asserts) → semantics subsumed by the
  afm_ gate ladder + court; not ported.
