# Reference: pack contract

Every admitted marketplace pack is a directory under `packs/` whose directory name equals `[pack].name`.

This contract defines **marketplace admission shape**. It does not by itself define Level-5 maturity or runtime standing.

## Manifest

`pack.toml` is required. `[pack]` contains:

- `name`: non-empty string equal to the directory name;
- `version`: SemVer string;
- `description`: non-empty string.

Do not add arbitrary unknown keys inside `[pack]`: the real ggen pack loader may enforce a narrower schema than the marketplace catalog projection. Lifecycle/class metadata must use a contract explicitly admitted by the relevant loader rather than assuming prose-level extensibility.

## RDF source

At least one Turtle source is required. The validator admits `*.ttl` at the pack root and recursively under `ontology/`. A conventional pack normally uses `ontology.ttl`; larger project packs may split semantic authority into multiple files under `ontology/`.

RDF carries admitted semantic facts. A README, generated artifact, catalog projection, or historical import repository does not silently supersede the admitted marketplace RDF/source bytes.

## Templates

Templates are optional at the marketplace level because semantic/catalog/gate packs can be useful without projecting files. When present under `templates/`, non-scaffolding files must end in `.tmpl` or `.tera`.

Templates are projection logic, not a second domain ontology.

## Gates

`gates/` is optional. Current admitted source roles are:

- `*.rq` — native SPARQL refusal gates;
- `*.py` — pack-owned bounded verifier gates for checks outside native SPARQL.

Dotfiles such as `.gitkeep` are scaffolding and are not cataloged as executable sources. Additional executable gate forms require an explicit contract change.

The existence of a gate is not evidence that its negative witness has executed successfully.

## Qualification inputs

Packs may own bounded positive qualification material under the recognized `qualification/` contract. These fixtures are synthetic admitted inputs for pack qualification, not claims that an external observation/customer/cloud event occurred.

See [ggen qualification contract](ggen-qualification-contract.md).

## Packaging profiles

The marketplace derives one packaging profile:

- `project` when `ggen.toml` exists;
- otherwise `projection` when templates exist;
- otherwise `semantic`.

Profiles describe package shape. They do **not** describe semantic responsibility, maturity, or execution standing.

## Semantic classes

A separate class taxonomy describes composition responsibility: KernelPack, CapabilityPack, ProfilePack, WorldPack, CompatibilityPack, EvidencePack, ReleaseControlPack, and UmbrellaPack.

See [Pack classes](pack-classes.md). Class assignment must be derived from semantic/consumer responsibility rather than suffix/name similarity.

## Level-5 extension

An admitted pack can remain L1–L4 on one or more maturity dimensions. Level-5 promotion additionally requires closure over:

- semantic source;
- admission and negative witnesses;
- deterministic manufacture;
- the claimed real execution boundary;
- receipt/replay;
- authority fencing;
- composition/class closure;
- Tutorial + How-to + Reference + Explanation correspondence.

`pack-maturity-pack` provides reusable mechanical infrastructure but cannot invent domain semantics or execution evidence. See [Level-5 maturity contract](level5-maturity-contract.md).

## Path safety

Symlinks below `packs/` are refused so reviewed pack source cannot escape through path aliasing. Qualification/configuration paths must remain relative and inside their owning pack when the contract requires pack-local authority.

## Generated-output rule

Generated consumer outputs are consequences and normally do not belong in marketplace pack source. Repository-generated documentation control files such as `docs/SUMMARY.md` are regenerated from admitted source during their manufacturing workflow and are not editing surfaces.
