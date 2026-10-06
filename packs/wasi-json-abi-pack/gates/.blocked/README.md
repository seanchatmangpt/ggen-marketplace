# Gates — WASM artifact verification (slow rail)

Executable verification gates for the `wasi-json-abi-pack` WASM surface.
POSIX shell + python3 stdlib only; no runtime dependency on any consumer repo.
These are slow-rail scripts (they may branch and allocate); they are never
linked into an authoritative hot path. Every gate below has witnessed firings
against real artifacts — a gate with no witnessed firing carries no bits.

Consolidated provenance (the repo pipelines these gates replace at the point
of check):

| gate | consolidates | repo pipeline |
|---|---|---|
| `wasm_zero_imports.sh` | `scripts/wasm_imports.py` (`--require-zero-imports`, required-export verification) + `tests/wasm_abi.rs` WASI-only assertion | wasm4pm (ex4pm-bindings), graphlaw |
| `wasm_artifact_pin_check.sh` | `registry/ARTIFACTS.sha256` pin format (create-only), `tests/registry_artifacts.rs` pin check + `AFFIDAVIT_REQUIRE_PIN` enforcement, CI "Checksum (must equal the pin)" step | affidavit |
| `wasm_abi_doc_drift.sh` | `scripts/gen_abi.py` regenerate-and-fail-on-drift CI semantics + `tests/abi_roundtrip.rs` exact-symbol-name resolution | wasm4pm (ex4pm-bindings), graphlaw |

## `wasm_zero_imports.sh` — import-policy + required-export gate

- **Purpose:** fail unless the module's import section is empty (default) or
  WASI-only (`--allow-wasi`: `wasi_snapshot_preview1` entries only) plus any
  explicitly allowed `mod.name` pairs; fail unless every named required export
  exists in the export section.
- **Invocation:**
  `./wasm_zero_imports.sh [--allow-wasi] [--allow-import mod.name]... [--require export]... FILE.wasm`
- **Exit:** `0` pass · `1` policy violation (disallowed import / missing
  required export) · `2` usage or malformed wasm.
- **Law guarded:** `gates/060_imports_policy_wasi_only.rq` +
  `gates/080_wasi_import_closure.rq` — the import surface is exactly the WASI
  module (or empty) so the module runs in a bare Wasmex host with no JS glue;
  the ABI contract's named exports are all really present.
- **Witnessed:** graphlaw module (7 wasi imports, pass under `--allow-wasi`,
  refused without it); `wasm4pm_ex4pm_bindings.wasm` (0 imports, pass);
  non-WASI import module `__wbindgen_placeholder__` refused even under
  `--allow-wasi`; missing required export refused.

## `wasm_artifact_pin_check.sh` — artifact pin verification

- **Purpose:** verify a built `.wasm` against a create-only pin file
  (`<kind> <sha256> <bytes> <name>` lines, `#` comments): digest AND byte size
  AND pinned filename must match. Placeholder pins (digest not 64 lowercase
  hex) are never treated as a match. The gate never writes the pin file.
- **Invocation:**
  `./wasm_artifact_pin_check.sh --artifact FILE.wasm --pin PINFILE [--kind wasm] [--name BASENAME]`
- **Enforcement:** `WASM_ARTIFACT_PIN_REQUIRE=1` mirrors affidavit's
  `AFFIDAVIT_REQUIRE_PIN`: with enforcement set, a missing artifact or a pin
  file holding no real pin line is a hard refusal (exit `3`), never a skip.
  Without enforcement those cases exit `0` with an explicit `SKIPPED` line.
  A present-but-wrong pin always fails (exit `1`), enforced or not.
- **Exit:** `0` verified (or explicit skip) · `1` pin mismatch · `2` usage ·
  `3` enforcement violation.
- **Law guarded:** `gates/090_artifact_pin_shape.rq` — a shipped artifact is
  admitted only against a receipted digest+size+name pin; "the pin is a pin,
  not a suggestion" (regenerate after any `src/` change; hand-editing a
  built artifact shows up as a digest mismatch).
- **Witnessed:** fresh-pin pass on `graphlaw_wasm.wasm`
  (sha256 `8bfff66c…e71a8`, 6657549 bytes); one-byte mutation of a COPY
  refused (`digest_mismatch` + `name_mismatch`); real committed affidavit pin
  `5cc37aea…1402 / 660847` verified against the real `affidavit_wasm.wasm`;
  enforcement refusals for missing artifact and for the placeholder-only
  skeleton pin in `generated/ARTIFACTS.sha256`; explicit skip without
  enforcement.

## `wasm_abi_doc_drift.sh` — ABI-document vs module drift court

- **Purpose:** regenerate-and-compare semantics without a toolchain: re-derive
  the module's export section with the same stdlib parser gate 1 vendors, read
  the ABI JSON document's declared `exports`, and fail on drift in either
  direction — a doc export absent from the module (stale doc; renamed or
  removed `#[export_name]` breaks the Wasmex host at call time) or a module
  export absent from the doc (undeclared surface). `--ignore-prefix` exemptions
  are explicit on the command line; the gate never silently prunes (running
  without the needed `--ignore-prefix memory` refuses on `memory`). When the
  doc carries `export_count`, it must equal the declared `exports[]` length.
- **Invocation:**
  `./wasm_abi_doc_drift.sh --abi ABI.json --module FILE.wasm [--ignore-prefix name]...`
  Accepted doc shapes: `{"exports":["name",…]}`,
  `{"exports":[{"export":"name",…},…]}` (wasm4pm `gen_abi.py` shape),
  `{"exports":[{"name":"name",…},…]}`.
- **Exit:** `0` no drift · `1` drift (stale or undeclared surface, or
  `export_count` mismatch) · `2` usage / malformed abi json / malformed wasm.
- **Law guarded:** the ABI document is a projection of the module's export
  section, not an independently hand-edited artifact — mirrors the
  `gen_abi.py` CI drift check and the `abi_roundtrip.rs` law that host symbol
  resolution is by exact exported name.
- **Witnessed:** `docs/abi/ex4pm-bindings.abi.json` (70 declared exports) vs
  `wasm4pm_ex4pm_bindings.wasm` (71 exports) passes with the explicit
  `--ignore-prefix memory`; refuses without it; a doc COPY with one renamed
  export refuses with both a stale-doc and an undeclared-surface violation; a
  doc COPY with one dropped export refuses as undeclared surface.

## Standing

All three gates: **ALIVE** — executed in this session against real artifacts
(graphlaw `graphlaw_wasm.wasm` 6,657,549 B; wasm4pm
`wasm4pm_ex4pm_bindings.wasm`; affidavit `affidavit_wasm.wasm` 284,650 B) with
both admitting and refusing firings recorded above and in the lane report.
Standing is scoped to the exact artifacts and commands in the firing receipts;
re-run the gates after any module rebuild or ABI regeneration.
