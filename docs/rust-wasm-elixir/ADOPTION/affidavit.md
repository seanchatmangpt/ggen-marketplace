# ADOPTION DOSSIER — affidavit (reference adoption)

> **Historical receipt (2026-10-01 measurements).** Current consumer wiring: see
> `affidavit` docs/WASM.md (`~/affidavit/docs/WASM.md` in the sibling checkout).

Standing: **ALIVE** (reference pattern verified by file + CI inspection in this session; render re-execution not run in this session — gates below are the re-proof path).

## 1. Current state (evidence, all measured 2026-10-01)

Pipeline surface (`wc -l`):

| File | Lines | Origin |
|---|---:|---|
| `~/affidavit/affidavit-wasm/src/ffi.rs` | 174 | RENDERED — header: "Rendered by ggen (wasi-json-abi-pack)"; consumed query `ffi.rq` |
| `~/affidavit/affidavit-wasm/src/abi_meta.rs` | 47 | RENDERED — header: "Rendered by ggen (wasi-json-abi-pack)"; query `meta.rq` |
| `~/affidavit/affidavit-wasm/src/lib.rs` | 43 | hand-written (crate root) |
| `~/affidavit/affidavit-wasm/src/abi.rs` | 709 | hand-written (op bodies — real domain logic) |
| `~/affidavit/affidavit-wasm/src/crypto.rs` | 192 | hand-written (BLAKE3 domain) |
| `~/affidavit/affidavit-wasm/src/external_evidence.rs` | 334 | hand-written (domain) |
| `~/affidavit/affidavit-wasm/src/receipt.rs` | 392 | hand-written (domain) |
| `~/affidavit/ontology/affi-wasm.ttl` | 114 | hand-written SOURCE (the ontology is upstream, not a projection) |
| `~/affidavit/affidavit-wasm/templates/artifact_pin.json.tmpl` | 38 | consumer-side template (pin projection) |
| `~/affidavit/affidavit-wasm/registry/ARTIFACTS.sha256` | 9 | rendered (template `wasm_artifacts.sha256.tmpl`) |
| `~/affidavit/affidavit-wasm/registry/artifact-pin.json` | 38 | rendered (local `artifact_pin.json.tmpl`) |
| `~/affidavit/affidavit-wasm/registry/capability-registry.json` | 74 | rendered (`wasm_capability_registry.json.tmpl`) |
| `~/affidavit/affidavit-wasm/registry/op-examples.json` | 42 | rendered (`wasm_op_examples.json.tmpl`) |
| `~/affidavit/.github/workflows/affidavit-wasm.yml` | 157 | hand-written CI (drift court + determinism + wasmi runtime) |

Pack consumption (grep `wasi-json-abi` in `~/affidavit/ggen.toml`): 6 renders declared — `ffi.rq`→`wasm_ffi.rs.tmpl`, `meta.rq`→`wasm_abi_meta.rs.tmpl`, `cargo.rq`→`wasm_cargo_config.toml.tmpl`, `registry.rq`→`wasm_capability_registry.json.tmpl`, `examples.rq`→`wasm_op_examples.json.tmpl`, `registry.rq`→`wasm_artifacts.sha256.tmpl`. Pack path: `../ggen-marketplace/packs/wasi-json-abi-pack` (pack.toml version 26.9.29).

Hand-rolled today: the four domain modules (abi/crypto/external_evidence/receipt = 1,627 lines) and the CI court. Nothing in the FFI shell is hand-rolled — this is the convergence target.

## 2. Consolidation actions

affidavit is the reference; the actions are hardening, not migration.

1. Re-render proof in-session: from `~/affidavit` run `ggen sync` (its ggen.toml drive), then `git diff --exit-code -- affidavit-wasm/registry affidavit-wasm/src/ffi.rs affidavit-wasm/src/abi_meta.rs affidavit-wasm/.cargo/config.toml`. Gate: zero diff (this exact gate is already CI line 74-75).
2. Wire the marketplace gates being built under `packs/wasi-json-abi-pack/gates/` (010_module_required_props … 100_alloc_discipline_closed, 10 gate files measured) into `affidavit-wasm.yml` after the drift check, evaluated against `ontology/affi-wasm.ttl`. Gate: court runner exits 0 on the ontology's witness pairs (`gate-court.toml` schema `ggen.semantic-gate-witness-court/1`, require_pass + require_fail).
3. Promote `artifact-pin.json.tmpl` from consumer-side to pack-side (render it from `registry.rq` like `ARTIFACTS.sha256`), then re-render and re-pin. Gate: `git diff --exit-code -- affidavit-wasm/registry/artifact-pin.json` after render.
4. Add the second-generator identity check (C20 pattern): render the FFI shell with the frozen marketplace ggen identity and the ambient one; `cmp` outputs. Gate: byte-identical, else REFUSED.

## 3. UNSUPPORTED ledger rows

- `UNSUPPORTED(wasi-json-abi-pack, artifact-pin.json render)` — pin projection currently lives in the consumer (`affidavit-wasm/templates/artifact_pin.json.tmpl`, 38 lines). Pack must own a `wasm_artifact_pin.json.tmpl`.
- `UNSUPPORTED(wasi-json-abi-pack, marketplace-gate CI step)` — no template/fragment renders the gates-into-CI job; consumers hand-write ~20 CI lines each.

## 4. 比 measurement

Manufactured (src + registry): 174 + 47 + 9 + 38 + 74 + 42 = **384 lines**.
Pipeline total (src 1,891 + registry 163) = **2,054 lines**.
比 = 384 / 2,054 = **18.7%**.
Post action-3 (pin moved to pack render): +38 consumer template retired, manufactured 422/2,016 = **20.9%**. The 1,627 domain lines (abi/crypto/external_evidence/receipt) are lawful hand-written residue — they are the product semantics, covered by `HANDWRITTEN.md` at repo root (file observed).

## 5. Falsifier

Adoption failed if: `ggen sync` produces a diff in `ffi.rs`/`abi_meta.rs`/`registry/*` while the committed artifact is admitted (drift court fires, `git diff --exit-code` non-zero) — proving the render and the admitted artifact diverged; or the wasmi differential suite (`affidavit-wasm/tests/wasm_abi.rs`, present in `ls tests/`) passes on a mutated ontology render, proving the registry gate is vacuous.

## 6. Risk / rollback

Snapshot before any re-render: `git -C ~/affidavit stash list` must be empty-clean and `git -C ~/affidavit rev-parse HEAD` recorded; rollback = `git -C ~/affidavit checkout -- affidavit-wasm/registry affidavit-wasm/src/ffi.rs affidavit-wasm/src/abi_meta.rs`. The deterministic double-build (`cmp` of two target dirs, CI lines 95-98) is the guard against nondeterministic renders. Registry pin mismatch = typed `DigestMismatch` refusal, not silent re-pin.
