# shacl-to-pydantic-pack

Projects admitted SHACL NodeShapes into `pydantic.BaseModel` classes. Companion to
`shacl-projection-pack` law: the consumer composes both packs (pack-to-pack dependencies
are not declarable in pack.toml); this pack renders `src/shacl_pydantic_models.py` and
ships zero domain individuals.

## What It Projects

- `src/shacl_pydantic_models.py` — one `class <sp:className>(pydantic.BaseModel)` per
  `sp:PydanticModel` individual in the merged graph (imports `pydantic`; `typing` is
  stdlib), plus a trailing `model_rebuild()` pass per class.

Field mapping (reuses shacl-projection-pack vocabulary, namespace
`http://seanchatmangpt.github.io/packs/shacl-projection#`):

| consumer fact | projection |
|---|---|
| `sh:datatype xsd:string` | `str` |
| `sh:datatype xsd:boolean` | `bool` |
| `sh:datatype xsd:integer` / `xsd:long` | `int` |
| any other `sh:datatype` | `float` |
| `sh:in` string list | `typing.Literal["...", ...]` |
| `sp:nullable true` | `... \| None` |
| `sp:collection true` | `list[...]` |
| `sh:node` nested shape | `<sp:projectionName>` of the nested shape |

`from __future__ import annotations` plus the trailing `model_rebuild()` loop mean nested
classes may be referenced before their declaration order would otherwise allow.

## Consumer Contract

pip deps: `pydantic` — `src/shacl_pydantic_models.py` imports `pydantic`; there is no other
third-party import in any template (verified by grep over `templates/`; `typing` is stdlib).

Beyond pip deps, the consumer must:

- mint its own `sp:PydanticModel` individuals in its ontology (`sp:className` legal Python
  identifier, `sp:derivedFromShape` → a real `sh:NodeShape`). The pack ships zero
  individuals; **zero individuals is a silent stub** — the template still renders a file
  containing only the imports;
- compose `shacl-projection-pack` for shape-validity law (missing/ambiguous value kinds,
  invalid datatypes, unresolved nested shapes);
- supply `sp:projectionName` on any nested shape referenced via `sh:node`;
- supply `sp:nullable` / `sp:collection` as boolean literals (absent = false — the SPARQL
  COALESCE defaults to `"false"`).

## Output Paths Are Template-Authored (truth-telling)

The render target is the `to:` line in `templates/shacl_to_pydantic.py.tmpl` — currently
`src/shacl_pydantic_models.py`. A consumer cannot retarget it from `ggen.toml`: there is no
output-path override in the manifest schema.

## Gate

`gates/010_template_pydantic_scan.py` — fail-closed scan over `templates/`: banned
domain literals (zcode, xaas, autofde, ggen-marketplace, praxis, wasm4pm, ex4pm,
affidavit) and hardcoded `class X(...)` lines lacking a Jinja binding exit 1; an
unreadable template file exits 1. Run: `python3 gates/010_template_pydantic_scan.py`.
