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
