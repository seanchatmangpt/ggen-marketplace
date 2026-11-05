# shacl-to-fastapi-pack

Projects admitted SHACL/Pydantic contracts into deterministic FastAPI route modules.
Renders one file, `src/wd_fa_api.py`: an `APIRouter` with one typed route per
`sfa:FastAPIProjection` individual, whose handler bodies raise `NotImplementedError`
until an application service supplies execution semantics. Reuses shacl-projection-pack
law by IRI; ships zero domain individuals.

## What It Projects

`src/wd_fa_api.py` (the `to:` line in `templates/fastapi_router.py.tmpl`):

- imports `APIRouter` from `fastapi` and model names from `shacl_pydantic_models`
  (the consumer's own shacl-to-pydantic-pack projection module);
- `{{ routerVar }} = APIRouter()` from the first row's `sfa:routerVar`;
- one decorated handler per `sfa:FastAPIProjection` row, ordered by `?operationId`
  (deterministic; the SPARQL `ORDER BY ?operationId` in the template frontmatter),
  each raising `NotImplementedError` — the projection carries routing and typing,
  never execution semantics or DO authority.

Field mapping (vocabulary `https://ggen.dev/packs/shacl-to-fastapi#`, `sfa:`; shape
linkage via shacl-projection-pack's `sp:derivedFromShape`):

| consumer fact | projection |
|---|---|
| `sfa:moduleName` | declared module name (see truth-telling below: the `to:` path is fixed) |
| `sfa:routerVar` | `APIRouter()` variable |
| `sfa:routePath` + `sfa:httpMethod` | `@router.post("/cases", ...)` |
| `sfa:operationId` | handler name + `operation_id=` |
| `sfa:requestModelName` / `sfa:responseModelName` | payload/response annotations |
| `sfa:consequential` / `sfa:requiresAuthority` | gate-only facts (020 gate) |

## Consumer Contract

python deps: `fastapi` (direct import), `pydantic` (transitive — `response_model=` and
payload annotations must be pydantic BaseModels). The only other import is
`shacl_pydantic_models` — **not a pip package**: it is the consumer's own projected
module from shacl-to-pydantic-pack; deleting that module from the consumer render fails
the import at runtime (`ModuleNotFoundError`). Verified by grep over `templates/`:
`fastapi` is the only direct third-party import.

Beyond deps, the consumer must:

- mint its own `sfa:FastAPIProjection` individuals over real `sh:NodeShape` facts
  (`sp:derivedFromShape`). **Zero individuals is a refusal-free empty projection** —
  `rows[0]` would IndexError at render time; the pack has no guard for the empty case
  (registered gap, not silently papered over);
- render the model module first (shacl-to-pydantic-pack output as
  `shacl_pydantic_models.py` in the same package); the router import resolves against
  it;
- compose shacl-projection-pack for shape-validity law and gate 010 (all ten required
  projection metadata fields present) and gate 020 (a `consequential true` projection
  may never declare `requiresAuthority false`).

## Output Path Is Template-Authored (truth-telling)

The render target is the `to:` line in `templates/fastapi_router.py.tmpl` — currently
`src/wd_fa_api.py`. **A consumer cannot retarget it from `ggen.toml`** (no output-path
override in the manifest schema). Note the drift: `sfa:moduleName` is a declared
projection fact but the `to:` line does not derive from it — renaming the module via
`sfa:moduleName` changes nothing on disk. To retarget, vendor the template into the
consumer's own `[templates].dir` and edit its `to:` line. Do not hand-edit the projected
output.

## Gates

SPARQL witness court (`gate-court.toml`, exact-stem, require_pass + require_fail):

- `gates/010_required.rq` — every `sfa:FastAPIProjection` carries all ten required
  metadata fields; a stripped field yields a row naming the missing predicate.
- `gates/020_authority.rq` — `consequential true` ∧ `requiresAuthority false` is a
  refusal; pass/fail witnesses under `witnesses/`.
- `gates/030_template_literal_scan.py` — fail-closed literal scan over `templates/`:
  no banned domain literals; no hardcoded handler `def` names or route decorators
  without a Jinja binding (projected routes must come from the graph via `{{ ... }}`).
  Any hit exits 1; a missing or unreadable templates dir also exits 1. Mirrors
  shacl-to-zod-pack's `010_template_literal_scan.py`.

## See Also

- `packs/shacl-projection-pack/README.md` — shared shape law
- `packs/shacl-to-pydantic-pack/README.md` — the `shacl_pydantic_models` module
