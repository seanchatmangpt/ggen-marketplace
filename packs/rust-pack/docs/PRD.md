# Product Requirements Document (PRD) — `rust-pack`

**Canonical Marketplace Pack for Ontology-Driven Rust Systems Manufacturing**  
**Version:** 0.1.0  
**Authority:** `urn:ggen:pack:rust-pack`  
**Standard:** Rust Core Team API Guidelines (RFC 430), Unsafe Code Guidelines (UCG), Cargo Workspace Laws  

---

## 0. Claims Reconciliation

This PRD establishes the product authority for `rust-pack` in `~/ggen-marketplace/packs/rust-pack`. It separates verified specification from runtime compiler execution.

| Claim | Ceiling | Standing |
|---|---|---|
| RFC 430 API Guidelines specification exists as SHACL shapes | `REFERENCE_CONFORMANT` | `ALIVE` |
| Cargo workspace topology & dependency inheritance are modeled | `REFERENCE_CONFORMANT` | `ALIVE` |
| Unsafe Code Guidelines (UCG) safety proof invariant is admitted | `REFERENCE_CONFORMANT` | `ALIVE` |
| `#![no_std]` + `alloc` systems tiering is modeled | `REFERENCE_CONFORMANT` | `ALIVE` |
| 64-byte alignment (`#[repr(align(64))]`) for `avec` Arrow parity is modeled | `REFERENCE_CONFORMANT` | `ALIVE` |
| Branchless constant-time execution model for `bcinr` parity is modeled | `REFERENCE_CONFORMANT` | `ALIVE` |
| Freestanding C ABI with panic-unwind suppression is modeled | `REFERENCE_CONFORMANT` | `ALIVE` |
| Generated code compiles under `cargo check` and `clippy -- -D warnings` | `COMPILER_VERIFIED` | `PARTIAL_ALIVE` |
| Generated unsafe kernels pass Miri without undefined behavior | `MIRI_VERIFIED` | `PARTIAL_ALIVE` |

`RELEASE_CONTROL.md` governs claim ceilings. Pack standing remains bound to exact compiler and court receipts.

---

## 1. Product Thesis

Handwritten Rust systems scaffolding is repetitive, error-prone, and violates the doctrine of **After Code Reading** (Section 21 of `AGENTS.md`): code is intermediate manufacturing material; the product is a verified business capability.

When human engineers manually scaffold Cargo manifests, multi-crate workspaces, module hierarchies, `unsafe` FFI wrappers, and trait implementations, they frequently introduce:
1. **Cargo Drift**: Fragmented dependency versions, missing MSRVs, and circular feature flags.
2. **Soundness & FFI Hazards**: Unwinding across `extern "C"` boundaries, unaligned SIMD pointer casts, missing `// SAFETY:` rationale, and aliasing violations under Miri.
3. **API Ergonomics Gaps**: Missing canonical traits (`Debug`, `Clone`, `Display`, `Error`), inconsistent naming conventions, and non-extensible public enums.

`rust-pack` solves this by providing the **definitive Rust Core Team-grade projectional manufacturing pack**. It compiles an admitted RDF ontology $\mathcal{O}^*$ into clean, idiomatic, high-performance Rust workspaces, modules, and C ABI bridges that are indistinguishable from code authored by the Rust Core Team.

---

## 2. Stakeholders & User Personas

| Council / Persona | Primary Demands | `rust-pack` Solution |
|---|---|---|
| **Cargo Team** | Workspace unification, strict version inheritance, clean feature graphs, deterministic MSRV. | Emits `[workspace.dependencies]`, `rust-version = "1.82.0"`, `resolver = "2"`, and additive-only feature flags. |
| **Libs Team** | RFC 430 conformance, canonical trait derivations, standard error types, non-exhaustive evolution. | Auto-derives standard traits, creates custom error enums implementing `std::error::Error`, and applies `#[non_exhaustive]`. |
| **Lang & Compiler Team** | Zero-cost abstractions, monomorphization control, `#[inline]` hints, strict type invariants (`NonZeroU32`, newtypes). | Generates niche-optimized newtypes, transparent representations, and separates `const fn` from runtime kernels. |
| **Unsafe Code Guidelines (UCG)** | Zero undefined behavior (UB), strict pointer provenance, 64-byte alignment, Miri cleanliness. | Mandates automated `// SAFETY:` proof comments, 64-byte alignment for SIMD/Arrow, and `catch_unwind` FFI guards. |
| **Embedded & Systems** | `#![no_std]` core by default, optional `alloc`, no hidden heap allocation. | Tiered architecture where core crates are `#![no_std]`, gating `std` behind explicit features. |

---

## 3. Delivered Capabilities

### Capability 1: Cargo Workspace & Multi-Crate Topology
- Manufactures root `Cargo.toml` with `[workspace]`, `resolver = "2"`, and `[workspace.dependencies]`.
- Manufactures per-crate `Cargo.toml` with `version.workspace = true`, `edition.workspace = true`, `license.workspace = true`.
- Enforces strict single-source versioning across the entire crate cluster.

### Capability 2: Idiomatic Type System & RFC 430 Conformance
- **Structs**: Tuple structs, unit structs, record structs, with explicit `#[repr(C)]`, `#[repr(transparent)]`, or `#[repr(align(64))]`.
- **Enums**: Fieldless and tagged enums with `#[non_exhaustive]` on public surfaces.
- **Traits**: Automatic, sound derivation of `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash`, `Default`.
- **Errors**: Dedicated `Error` enum with `thiserror`-compatible or manual `std::fmt::Display` and `std::error::Error` implementations, including source chaining.

### Capability 3: Substrate Connectors (`avec` & `bcinr`)
- **`avec` Connector**:
  - Direct zero-copy export to Apache Arrow C Data Interface (`ArrowArray`, `ArrowSchema`).
  - Strict 64-byte buffer alignment (`#[repr(align(64))]`) for AVX-512 / ARM NEON vectorization.
  - Zero-allocation columnar table projections.
- **`bcinr` Connector**:
  - Constant-time branchless integer primitives (`select_u32`, `min_u32`, `max_u32`, `add_sat`).
  - Bitwise masking and CMOV sequence guarantees without conditional jumps.
  - Integration with `bcinr-powl` workflow schedulers.

### Capability 4: Sound FFI & Zero-Import C ABI
- Manufactures `inc/<name>.h` freestanding C header with zero external imports (only `<stdint.h>`, `<stddef.h>`, `<stdbool.h>`).
- Manufactures `extern "C"` wrappers with `#[no_mangle]`.
- Panic Safety: Every FFI boundary wraps callbacks in `std::panic::catch_unwind` or abort guards to eliminate foreign-stack unwinding (UB).

### Capability 5: Systems Tiering (`no_std` + `alloc`)
- Every manufactured library crate includes:
  ```rust
  #![no_std]
  #[cfg(feature = "alloc")]
  extern crate alloc;
  ```
- Isolates `std` dependencies to specific IO/CLI integration crates.

---

## 4. Non-Goals & Exclusions

1. **No Domain Invention**: `rust-pack` generates the architecture, signatures, memory layouts, traits, and FFI boundaries; irreducible domain logic resides in custom handlers or agent-ported kernels.
2. **No Compiler Bypassing**: `rust-pack` will not generate code that relies on unstable nightly features unless explicitly requested; default target is stable Rust 1.82.0+.
3. **No Unadmitted Actuation**: The pack generates code as intermediate material; it carries no ambient authority to deploy or execute without receipts.

---

## 5. Acceptance Criteria

```text
cargo fmt -- --check = PASS
cargo check --workspace --all-targets = PASS
cargo clippy --workspace --all-targets -- -D warnings = PASS
cargo test --workspace = PASS
cargo miri test (ffi & arena targets) = PASS (Zero Undefined Behavior)
64-byte alignment check on SIMD buffers = PASS
SHACL refusal gates (010..050) = PASS (0 violations)
```
