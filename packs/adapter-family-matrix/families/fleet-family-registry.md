# family note: fleet-family-registry (absorbed 2026-09-30)

- Was: `packs/fleet-family-registry` v0.1.0 — "Construct-only registry of adapter
  families, consumers and bindings for fleet package projection, with authority
  NONE."
- Namespace: `fr: <https://ggen.dev/fleet-family-registry#>` → replaced by `af:`
  (ontology/conservation.ttl); terms conserved in
  `ontology/fleet-family-registry.ttl`.

## Term mapping (11 records + 2 metaclasses)

fr:Family→af:AdapterFamily · fr:Consumer→af:Consumer · fr:Binding→af:Projection ·
fr:name→af:name (new) · fr:templateKey→af:templateKey · fr:extension→af:fileExtension (new) ·
fr:consumer→af:consumer · fr:family→af:family · fr:targetRepo→af:targetRepo ·
fr:targetPath→af:targetPath · fr:authority→af:authority · fr:Class→rdfs:Class ·
fr:Property→rdf:Property (metaclasses).

## Gates absorbed (6 → archetype stems + ONE conserved unique)

010_required_identity → afm_010 · 020_authority_none → afm_020 ·
030_family_registered → afm_030 · 070_unique_target → afm_040 ·
080_template_key (strlen 0) → afm_080 · **060_repo_shape (targetRepo must contain
"/") → conserved verbatim as `gates/fr_060_repo_shape.rq`** — genuinely unique in
the cluster (no other pack constrained repo shape), re-expressed in `af:` terms.

## Asset disposition

- `families/*.ttl` (10 fr: family individuals with name/extension facts) →
  superseded by this pack's `families/*.ttl`; the extension facts are the one
  additive datum (now expressible as af:fileExtension, not yet materialized per
  family — extend `mappings/` if a consumer needs it).
- `consumers/*.ttl` (6) → superseded by this pack's `fixtures/consumers/*.ttl`.
- `fixtures/cs2-{elixir,json}.ttl` (2 Bindings) → conserved as
  `qualification/fixtures/fr-cs2-elixir.ttl` / `fr-cs2-json.ttl` in `af:`.
- `mappings/*.rq` (5 per-consumer SELECTs), `queries/**` (10 family + 3 project),
  `templates/*.tera` (9) + `registry.json.tmpl`, `ggen.toml` (self-proof render)
  → retired; nearest equivalents: this pack's `queries/project_*.rq` +
  `templates/*.tmpl` dispatch set.
- `schemas/{binding,family}.schema.json` → retired; nearest equivalent:
  `schemas/package-plan.schema.json` (unified owner).
- `tests/{registry,template}_contract.py` → family-sources-have-queries and
  authority-fenced-templates checks subsumed by the afm_ ladder + gate headers;
  not ported.
