# family note: fleet-package-compiler (absorbed 2026-09-30)

- Was: `packs/fleet-package-compiler` v0.1.0 — "Construct-only compiler plan for
  fleet package projection: 12 adapter-family templates, SPARQL transforms and 14
  gates over PackagePlan facts…"
- Namespace: `fp: <https://ggen.dev/ontology/fleet-package#>` → replaced by `af:`
  (ontology/conservation.ttl); terms conserved in
  `ontology/fleet-package-compiler.ttl`.

## Term mapping (12 records)

fp:PackagePlan→af:Projection · fp:Family→af:AdapterFamily · fp:Consumer→af:Consumer ·
fp:subject→af:subject · fp:consumer→af:consumer · fp:family→af:family ·
fp:targetRepo→af:targetRepo · fp:targetPath→af:targetPath · fp:templateKey→af:templateKey ·
fp:authority→af:authority · fp:sourceSha→af:sourceSha · fp:mode→retired fence
(no af: equivalent by design; superseded by `<urn:pack:adapter-family-matrix>
af:authority "NONE"`).

## Gates absorbed (14 → archetype stems)

010_required_identity/030_target_repo/040_target_path → afm_010 · 020_authority_none →
afm_020 · 090_family_declared → afm_030 · 080_unique_target → afm_040 ·
060_source_sha + 140_sha_shape → afm_050 · 100_consumer_declared → afm_060 ·
070_no_self_consumer → afm_070 · 110/120/130_nonempty_* → afm_080.
This pack carried the cluster's most complete archetype ladder; it is the
reference re-mint the canonical stems were collapsed against.

## Asset disposition

- `transforms/*.rq` (12 CONSTRUCT transforms) + `templates/*.tera` (12) +
  `queries/package_matrix.rq` → retired as a unit (construct-only compile pass
  over fp: IRIs); nearest equivalent: this pack's `queries/project_*.rq` +
  `templates/*.tmpl` dispatch set. Capability conserved; identity re-mint not.
- `schemas/package-plan.schema.json` → **survives**: unified owner is
  `schemas/package-plan.schema.json` here (union adds templateKey; the two
  former copies differed only in JSON key order).
- `ggen.toml` (project manifest, ontology.ttl-only) → retired; merged pack
  qualifies through the marketplace's synthetic semantic harness.
