# rmcp-pack

Typed Rust catalog + reference doc, generated from the real public API of the
`rmcp` crate (the official Rust SDK for the Model Context Protocol,
`rmcp = "2.2"`), grounded by reading the vendored crates.io source directly —
see `ontology.ttl`'s header for the full grounding method and scope
disclosures.

## What It Projects

- `src/rmcp_handler_catalog.rs` — `RMCP_SERVER_METHODS` / `RMCP_CLIENT_METHODS`
  typed const tables (43 handler methods: 27 server + 16 client).
- `src/rmcp_macro_catalog.rs` — `RMCP_MACROS` (7 proc-macro attributes).
- `src/rmcp_transport_catalog.rs` — `RMCP_TRANSPORTS` (7 transports with real
  feature gates).
- `src/rmcp_feature_catalog.rs` — `RMCP_FEATURES` (15 documented features).
- `src/rmcp_stub_handler.rs` — a real, compiling `impl ServerHandler` via
  `#[tool_router]`/`#[tool]`/`#[tool_handler]` against the actual crate.
- `src/rmcp_lib_wiring.rs` — mod aggregator (force: true); add one
  `include!("rmcp_lib_wiring.rs");` line to your `src/lib.rs`.
- `docs/rmcp_reference.md` — SPARQL-projected markdown tables for all 4
  classes.
- `tests/rmcp_handler_catalog_proof.rs` (hand-transcribed),
  `tests/rmcp_handler_catalog_sparql_derived_proof.rs` (live-rebaked),
  `tests/rmcp_stub_handler_proof.rs` (real behavior proof),
  `tests/rmcp_default_handler_proof.rs` (negative-witness proof).

## Consumer Contract

Derived mechanically from the templates' `use` statements: every code-level
import resolves to the single crate `rmcp`.

Cargo deps:

```toml
[dependencies]
rmcp = { version = "2.2", features = ["server", "macros"] }
```

Layout requirement: a cargo lib crate (`src/` + `tests/`). The generated proof
tests read `src/` files via `include_str!("../src/...")`, and the wiring module
expects `include!("rmcp_lib_wiring.rs");` in your `src/lib.rs`. A bare file
drop without the include line compiles the individual modules but leaves them
unreferenced (and skips the wiring seam).

Feature note: the generated code only exercises the server + macros surface.
`client` / transport features are data-only in the catalogs (rows are typed
const records, not live `rmcp::transport` values) and are not required to
compile.

## Rendering

Bind the pack by path in a consumer `ggen.toml`:

```toml
[project]
name = "my-consumer"

[ontology]
source = "ontology.ttl"

[packs]
"rmcp-pack" = { path = "../ggen-marketplace/packs/rmcp-pack" }

[templates]
dir = "local-templates"
```

Notes learned from a real render (same posture as
`packs/shadcn-ui-primitives-pack/README.md`):

- `[ontology]` and `[templates]` are required fields (FM-CONFIG-002); paths
  must be relative (FM-CONFIG-003).
- `[templates].dir` must NOT point at the pack's templates dir when the pack
  is also bound via `[packs]` — templates render twice and FM-WRITE-008 fires
  on the duplicate output. Point it at an empty local dir.
- The EA admission gate requires `ea.graph.json` or `--skip-ea-admission`
  (FM-LAW-015); the scratch consumer used `--skip-ea-admission`.

Then `ggen sync run --skip-ea-admission` renders the 11 files.

## Verification Court

Scratch consumer at `/tmp/g17-court` (cargo init; `rmcp` fetched from
crates.io; consumer `ggen.toml` binding the pack by path). Full command +
exit log: `docs/jira/v26.11.5/receipts/G17.md`.

- ggen 26.11.3 `sync run --skip-ea-admission` → exit 0, 11 files written.
- `cargo test` with `rmcp = { version = "2.2", features = ["server",
  "macros"] }` → real compile + proof runs against the actual crate.
- Anti-vacuity flip: catalog row perturbation → the SPARQL-derived proof
  fails against the stale on-disk catalog (drift-sensitive by design); the
  hand-transcribed and behavior proofs stay green on the true graph.

## See Also

- packs/mcpp-pack (closest structural precedent; mcpp shells out to a real
  binary, rmcp compiles against a real library crate)
- packs/shadcn-ui-primitives-pack (house consumer-contract pattern)
