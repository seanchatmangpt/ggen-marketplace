# family note: adapter-family-registry (absorbed 2026-09-30)

- Was: `packs/adapter-family-registry` v0.1.1 — "Registry ontology of adapter
  families (template key, media type) and the projections that bind a subject and
  consumer to a family, target path, module name and package name…"
- Namespace: `afr: <https://chatmangpt.com/ontology/adapter-family-registry#>`
  → replaced by `af:` (ontology/conservation.ttl); terms conserved in
  `ontology/adapter-family-registry.ttl`.

## Term mapping (12 records)

afr:Subject→af:Subject · afr:Consumer→af:Consumer · afr:AdapterFamily→af:AdapterFamily ·
afr:Projection→af:Projection · afr:subject→af:subject · afr:consumer→af:consumer ·
afr:adapterFamily→af:family · afr:targetPath→af:targetPath ·
afr:moduleName→af:moduleName (new) · afr:packageName→af:packageName (new) ·
afr:templateKey→af:templateKey · afr:mediaType→af:mediaType (new).

## Unique contributions (why the absorption is not a loss)

- Only pack in the cluster modeling `moduleName` / `packageName` per projection and
  `mediaType` per family — all three promoted into the canonical `af:` core.
- Ships no gates (stated in its own manifest): nothing collapses here; its
  semantics live inside afm_010/020 identity+authority archetypes.

## Asset disposition

- `fixtures/fleet.ttl` (3 projections, 5 families with mediaType) → conserved as
  `qualification/fixtures/afr-fleet.ttl`, re-expressed in `af:`.
- `templates/adapter-manifest.toml.{tera,tmpl}`, `runtime-binding.ex.{tera,tmpl}` →
  retired; nearest equivalent: this pack's `templates/<family>.tmpl` dispatch set
  (duplicated dual-extension pairs; the .tera/.tmpl twin was redundant).
- `qualification.toml` → retired (pack-level; the merged pack qualifies as one unit).
