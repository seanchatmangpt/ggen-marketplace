# sa2a-fastapi-pack

Projects protocol-integration Capability semantics into a Python/FastAPI SA2A
HTTP gateway surface. Results are candidates, never authority: every route
body raises `NotImplementedError` and the consumer supplies the actual
producer at application composition time.

## What It Projects

- `src/sa2a_gateway.py` — one `APIRouter` per `s2a:FastAPISA2ASurface`,
  pydantic `SA2ARequest`/`SA2AResult` models, and a `CAPABILITIES` table
  carrying each projection's `semantic_definition`, `observation_scope`,
  `mutation_scope`, `requires_authority`, and `receipt_semantics`.
- `POST {mount_path}/tasks/{capability_id}` — returns 404-shaped `KeyError`
  for unknown capability ids; a typed `NotImplementedError` stub for known
  ones.

## Consumer Contract

Python deps (derived mechanically from the template's non-stdlib imports):

- `fastapi`
- `pydantic`

Peer context: the consumer's ontology must supply `pi:Capability`
individuals plus an `s2a:FastAPISA2ASurface` with `s2a:CapabilityProjection`
metadata (see `qualification/consumer.ttl` for a working example). The pack
projects the gateway over them and defines no capability semantics itself.
`requires_authority` and the scope vocabularies (`none/idempotent/
consequential`, `none/read_only/read_write`, `none/logged/sealed_receipt`)
are the closed value sets mirrored from the ema: descriptor contract.

## Gates

- `gates/010_descriptor.rq` — every `s2a:CapabilityProjection` must bind a
  capability + id, use only the closed scope vocabularies, and refuses any
  projection with `mutationScope "consequential"` and
  `requiresAuthority false`.

Gate witnesses live in `witnesses/pass/` and `witnesses/fail/`
(`gate-court.toml` requires both; `case_key = "exact-stem"`).

## Court

Scratch-consumer court: bind the pack by path in a consumer `ggen.toml`,
run `ggen sync run` (gates execute during sync; a fail-witness case exists so
the gate's refusal path is exercised), then verify the projected
`src/sa2a_gateway.py` with the py_compile tier and a real import against the
installed fastapi/pydantic. Anti-vacuity flip: uninstalling fastapi must
turn the import into `ModuleNotFoundError` — an import that still passes
without the declared dependency is a vacuous contract.
