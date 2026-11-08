# typer-azure-pack

Projects an Azure CLI-style **Typer** command module GENERATED from the real
microsoft/bicep-types-az schema — one resource type per pack render:
`Microsoft.Storage/storageAccounts@2022-09-01` (vendored frozen manifest
excerpt, upstream commit `03f72b6d1309458d28f4369d382d701e638b904f`).

## What It Projects

- `generated/typer_storage.py` — a `typer.Typer()` sub-app with a `create`
  command whose options are the resource's writable/required bicep
  properties: kebab-case `az`-style flags (`--properties-allow-blob-public-access`),
  python-typed (`str`/`int`/`bool`, `Optional[...]` when not required),
  enum choices flattened into the ontology (`typer:choice`), 23 options for
  storageAccounts@2022-09-01.

## Consumer Contract

See [consumer_contract.md](consumer_contract.md) — deps derived mechanically
from the template imports: **`typer`** (the only third-party import; no Azure
SDK). Gates require `rdflib`. Known limitation on ArrayType properties
disclosed there.

## Rendering

Bind the pack by path in a consumer `ggen.toml` (v26.11.3 semantics —
`[packs]` binding alone does NOT run pack rules, so declare the generation
rule in the consumer and symlink the pack's query/template, all paths
relative; `[project]` requires a `version` or FM-CONFIG-101 fires):

```toml
[project]
name = "my-consumer"
version = "0.1.0"

[ontology]
source = "ontology.ttl"   # symlink to the pack's ontology.ttl

[templates]
dir = "local-templates"   # empty local dir; NOT the pack's templates dir

[[generation.rules]]
name = "typer-storage-commands"
query = { file = "q/typer.rq" }              # symlink to pack queries/typer.rq
template = { file = "t/typer_commands.py.tera" }
output_file = "generated/typer_storage.py"
mode = "Overwrite"
```

Then `ggen sync run --skip-ea-admission` renders the module
(exit 0, `generated/typer_storage.py` written; re-render is content-identical,
reported `skipped: unchanged`).

## Gates (SPARQL, exit-checked)

Two gates over the minted ontology, run by `gates/run_gates.py` (rdflib;
exit 0 = pass, exit 1 = refusal listing violating rows):

- `010_required_options.rq` — option metadata completeness + non-empty sub-app
- `020_typer_module.rq` — sub-app module metadata (appName/resourceType/apiVersion)

Both proven non-vacuous by mutation: stripping `--sku-name`'s `flagName` flips
010 (exit 1); stripping `apiVersion` flips 020 (exit 1). Court log:
`docs/jira/v26.11.5/receipts/G14.md`.

## Verification Court (v26.11.5)

Scratch consumer at `/tmp/g14-consumer`, court copy at `/tmp/g14-court`,
venv at `/tmp/g14-venv`:

- `python3 sources/mint_ontology.py` → "minted ...: 1 sub-app, 23 options", exit 0
- `ggen sync run --skip-ea-admission` → exit 0, `generated/typer_storage.py` written
- `python3 gates/run_gates.py` → exit 0, both gates PASS
- mutation courts → each gate flips to exit 1
- py_compile tier: exit 0 on the rendered module
- pip tier: real render executed under a fresh typer install (see receipt)

## Sources

Frozen manifest law and regenerate commands: [SOURCES.md](SOURCES.md).
The ontology is GENERATED (`python3 sources/mint_ontology.py`), never hand-edited.
