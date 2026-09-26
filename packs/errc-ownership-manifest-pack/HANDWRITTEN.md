# Ownership boundary

Handwritten semantic source:
- ontology.ttl
- shapes.ttl
- gates/*.rq
- queries/*.rq
- templates/*.tera
- qualification/*.py
- qualification/fixtures/*.ttl
- ggen.toml
- pack.toml

Generated:
- generated/ownership-manifest.json

The generated manifest is consumed by
`unrdf-errc-receipt --ownership generated/ownership-manifest.json`.

A path absent from the manifest is intentionally UNKNOWN to UNRDF and is
therefore charged as handwritten. A generated/reused/materialized declaration
that fails this pack's evidence gates must not reach the manifest.
