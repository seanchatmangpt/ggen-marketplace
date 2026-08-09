# Reference: pack contract

A marketplace pack directory is named exactly for its pack identity.

## `pack.toml`

Required. It contains exactly one top-level table, `[pack]`, with:

- `name`: non-empty string equal to the directory name.
- `version`: SemVer string.
- `description`: non-empty string.

## `ontology.ttl`

Required Turtle/RDF source. It carries facts used by templates and gates and is unioned with the relevant consumer graph by ggen.

## `templates/`

Required and non-empty. Marketplace validation admits files ending in `.tmpl`. ggen templates use frontmatter plus Tera content. A template may project one row or fan out rows to output paths according to the runtime's template contract.

## `gates/`

Optional. Files are `.rq` SPARQL queries. A matching gate is intended to refuse generation before consumer writes.

## Path safety

Symlinks anywhere below `packs/` are refused by marketplace validation so a pack cannot depend on path aliasing outside its reviewed tree.
