# htn-fond-powl2-compiler-pack

Standing: **UNVERIFIED / scaffold** — see [`STATUS.md`](STATUS.md).
Hard locks: [`CONSTRAINTS.md`](CONSTRAINTS.md).

- `templates/`, `queries/`, `ontology/`, `qualification/witnesses/` are **empty**
  (no fake codegen).
- Gates under `gates/*.rq` are `SELECT ?violation ?subject` stubs (0 rows = PASS).
- **Do not** pin `fibo/packs.toml` until qualify twice.
