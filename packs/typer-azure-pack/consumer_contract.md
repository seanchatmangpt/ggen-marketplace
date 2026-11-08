# Consumer Contract — typer-azure-pack

## Python deps (derived mechanically from template imports)

`templates/typer_commands.py.tera` header imports, verbatim:
`json`, `typing.Optional` (stdlib) and `import typer` (third-party).
The generated module therefore requires:

- `typer` (>= 0.12; `typer.Typer`, `typer.Option`, `typer.echo`)

That is the complete third-party closure. No Azure SDK is imported —
the pack derives Azure CLI *conventions* (kebab-case `az`-style flags)
from the bicep-types-az schema; it does not call Azure. Stdlib `json`,
`typing` need no install.

Runtime dep of the pack itself (not the consumer): `rdflib` — used by
`gates/run_gates.py` to execute the SPARQL gates exit-checked. The
ggen actuator (`ggen sync run`) has no Python dependency.

## Consumer surface

- One output file, `generated/typer_storage.py` (mode Overwrite).
- Consumers embed the generated sub-app into their own Typer app
  (`app = storage_storage_accounts_app` alias is emitted for exactly
  this). The module is import-safe and main-free.

## Template interpolation law (what the template requires of the graph)

The template interpolates `pytype` directly into `Optional[{{ pytype }}]`
annotations and `{{ orow.pyname }}` into parameter names, so the graph
must only ever carry python-valid type strings and python-identifier
`pythonName`s. Both are guaranteed by `sources/mint_ontology.py`
(kebab/snake from the bicep property names). Known limitation, disclosed:
a top-level ArrayType property reaching the main minter loop is recorded
as `list[str] (JSON-encoded)` — that string would render an invalid
annotation. No such property exists in the vendored manifest today
(tags is not ArrayType at the top level), so the current render is valid;
a re-vendor that introduces one would need the minter fixed first.

## Gate surface (SPARQL, exit-checked)

- `gates/010_required_options.rq` — every `typer:TyperOption` carries
  `flagName`/`pythonName`/`pythonType`/`required`, and every
  `typer:TyperSubApp` has at least one option.
- `gates/020_typer_module.rq` — every `typer:TyperSubApp` carries
  `appName`/`resourceType`/`apiVersion` (all three are interpolated into
  the generated module).

Run: `python3 gates/run_gates.py` (exit 0 pass / exit 1 refusal with rows).
