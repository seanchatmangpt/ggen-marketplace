# fnox-boundary-payload-pack

SHACL boundary payload shapes from fnox (FNOX-PRD-08) projected to Pydantic models.

## Contents

- `ontology/payload-shapes.ttl`: copy of `/Users/sac/fnox/ontology/boundary/payload-shapes.ttl`
  with a provenance comment. Public terms only (FIBO, PROV-O, DCTerms).
- `templates/boundary_models.py.tera`: frontmatter template; query variables `cls`, `field`,
  `dt`, `min`; output `pipeline/enterprise_pipeline/boundary/boundary_models.py`.
- `ggen.toml`: minimal `[project]`, `[ontology]`, `[templates]` (no `[validation]` table beside
  frontmatter templates).

## Exclusions

fnox `wireproxy` template, `justfile.d`, scratch files, and the fnox `LICENSE` were not copied.
The source TTL has no licence header.

## Differences from the fnox rule

fnox used one GROUP_CONCAT row joined by `%R%`; this pack returns one row per field and tracks
class boundaries in the template. Output intent is identical; byte parity is UNVERIFIED.

## See Also

`STANDING.md`
