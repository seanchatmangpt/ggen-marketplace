# Reference: pack contract

Every admitted marketplace pack is a directory under `packs/` whose name equals `[pack].name`.

## Manifest

`pack.toml` is required. `[pack]` contains:

- `name`: non-empty string equal to the directory name;
- `version`: SemVer string;
- `description`: non-empty string.

Pack-specific extension tables are allowed. The marketplace catalog reads identity only from `[pack]`; extension metadata cannot override that identity.

## RDF source

At least one Turtle source is required. The validator admits `*.ttl` at the pack root and recursively under `ontology/`. A conventional pack normally uses `ontology.ttl`; larger project packs may split semantic authority into multiple files under `ontology/`.

## Templates

Templates are optional at the marketplace level because semantic/catalog/gate packs can be useful without projecting files. When present under `templates/`, non-scaffolding files must end in `.tmpl` or `.tera`.

## Gates

`gates/` is optional. Current admitted source roles are:

- `*.rq` — native SPARQL refusal gates;
- `*.py` — pack-owned verifier gates for bounded checks outside a native SPARQL gate.

Dotfiles such as `.gitkeep` are scaffolding and are not cataloged as executable sources. Additional executable gate forms require an explicit contract change.

## Profiles

The catalog derives one profile:

- `project` when `ggen.toml` exists;
- otherwise `projection` when templates exist;
- otherwise `semantic`.

Profiles describe packaging shape, not execution standing.

## Path safety

Symlinks below `packs/` are refused so reviewed pack source cannot escape through path aliasing.

## Targets extension

A pack may declare the languages its templates project to in a sidecar `packs/<name>/targets.toml` holding a top-level `[targets]` table (not under `[pack]`, and not in `pack.toml`: ggen-engine denies unknown `pack.toml` tables, and `validate` refuses one with `TARGETS_IN_MANIFEST`):

```toml
[targets]
languages = ["ts", "py", "rs", "ex"]
```

`languages` is a non-empty, duplicate-free list of lowercase identifiers matching `[a-z][a-z0-9_+-]*`. `validate` refuses a malformed table with `TARGETS_LANGUAGES`; `catalog` emits `target_languages` (empty list when absent).
