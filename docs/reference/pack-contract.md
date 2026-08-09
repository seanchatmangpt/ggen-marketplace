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

Optional admission/verification source. Two gate roles are currently admitted and deliberately distinguished:

- `*.rq` — native ggen SPARQL refusal gates evaluated by the pack/runtime contract.
- `*.py` — pack-owned verifier gates used by packs whose validation requires computation beyond a native SPARQL gate. These are not mislabeled as SPARQL and are only executed when the pack's own verification procedure invokes them.

The allowlist is fail closed; additional executable gate forms require an explicit marketplace contract change.

## Path safety

Symlinks anywhere below `packs/` are refused by marketplace validation so a pack cannot depend on path aliasing outside its reviewed tree.
