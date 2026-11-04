# Architecture Requirements Document (ARD) — `rust-pack`

**Canonical Marketplace Pack for Ontology-Driven Rust Systems Manufacturing**  
**Version:** 0.1.0  
**Authority:** `urn:ggen:pack:rust-pack`  
**Governing Standard:** Chatman Equation $A = \mu(\mathcal{O}^*), R = \text{receipt}(A)$, Unsafe Code Guidelines (UCG)  

---

## 0. Claims Reconciliation

This ARD defines the target architecture, ontology vocabulary, refusal gates, and template pipeline for `rust-pack`.

| Architecture Claim | Ceiling | Standing |
|---|---|---|
| Complete `rust:` RDF vocabulary & SHACL shapes specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| Fail-closed SPARQL refusal gates (010..050) specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| UCG-compliant `// SAFETY:` rationale generation specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| 64-byte aligned SIMD memory layout (`avec` parity) specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| Branchless CMOV execution model (`bcinr` parity) specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| Zero-import FFI shell and panic-boundary architecture specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| Template suite (`workspace`, `crate`, `lib_rs`, `c_abi`) specified | `REFERENCE_CONFORMANT` | `ALIVE` |
| End-to-end compiler execution across targets | `COMPILER_VERIFIED` | `PARTIAL_ALIVE` |

---

## 1. Architectural Style & Mathematical Equation

`rust-pack` operates as a projectional ontology compiler under the **Chatman Equation**:

$$A = \mu(\mathcal{O}^*), \quad R = \text{receipt}(A)$$

Where:
- $\mathcal{O}^*$: Admitted, grounded RDF ontology specifying the Rust workspace, crate boundaries, types, memory alignments, and FFI surfaces.
- $\mu$: Deterministic SPARQL CONSTRUCT/SELECT queries and Tera template expansions.
- $A$: Generated Rust crates, manifests, source modules, and C headers.
- $R$: 5-field receipt ({identity, authority, consequence, replay, standing}) certifying compilation, lint cleanliness, and Miri pass.

```text
Admitted Ontology O* (rust_contract.ttl)
            │
            ▼ SPARQL Extraction (queries/rust/*.rq)
   Projectional Engine (ggen)
            │
            ▼ Tera Expansion (templates/rust/*.tera)
   Manufactured Rust Substrate
   ├── Cargo.toml               [Workspace manifest]
   ├── crates/<crate>/          [no_std + alloc libraries]
   ├── inc/<crate>.h            [Freestanding C ABI]
   └── tests/<crate>_court.rs   [Chicago TDD boundary courts]
            │
            ▼ Verification Ladder (cargo check, clippy, miri)
   Standing Receipt R
```

---

## 2. Domain Ontology Model (`urn:ggen:rust:#`)

The pack defines the authoritative `rust:` vocabulary in `ontology.ttl`:

### 2.1 Workspace & Crate Structure
- **`rust:Workspace`**:
  - `rust:resolverVersion "2"`
  - `rust:memberCrate (rust:Crate ...)`
  - `rust:workspaceDependency (rust:Dependency ...)`
  - `rust:profile (rust:Profile ...)`
- **`rust:Crate`**:
  - `rust:crateName xsd:string`
  - `rust:crateType ("lib" | "bin" | "proc-macro")`
  - `rust:isNoStd xsd:boolean`
  - `rust:hasAlloc xsd:boolean`
  - `rust:msrv xsd:string` (e.g. `"1.82.0"`)
  - `rust:edition ("2021" | "2024")`
  - `rust:crateModule (rust:Module ...)`

### 2.2 Data Types & Memory Representation
- **`rust:Struct`**:
  - `rust:repr ("C" | "transparent" | "align(64)")`
  - `rust:derives (rust:Trait ...)`
  - `rust:hasField (rust:Field ...)`
- **`rust:Enum`**:
  - `rust:isNonExhaustive xsd:boolean`
  - `rust:repr ("u8" | "u16" | "u32" | "C")`
  - `rust:hasVariant (rust:Variant ...)`
- **`rust:MemoryModel`**:
  - `rust:byteAlignment xsd:integer` (default 64 for SIMD/Arrow)
  - `rust:allocationPolicy ("ZeroAllocationArena" | "CallerProvided" | "HeapAlloc")`

### 2.3 Functions, Safety Proofs & FFI
- **`rust:Function`**:
  - `rust:visibility ("pub" | "pub(crate)" | "private")`
  - `rust:isConst xsd:boolean`
  - `rust:isUnsafe xsd:boolean`
  - `rust:isInline xsd:boolean`
  - `rust:safetyProof xsd:string` (mandatory if `isUnsafe = true`)
  - `rust:hasParameter (rust:Parameter ...)`
  - `rust:returnType xsd:string`
- **`rust:FfiExport`**:
  - `rust:symbolName xsd:string`
  - `rust:unwindProtection ("CatchUnwind" | "AbortOnPanic")`

---

## 3. Unsafe Code Guidelines (UCG) Invariants

To guarantee that generated systems code passes **Miri** without undefined behavior:

1. **Pointer Provenance Invariant**: Raw pointers (`*const T`, `*mut T`) must be constructed from valid references or aligned allocations. Pointer arithmetic must not cross allocation boundaries.
2. **Alignment Invariant**: SIMD buffers and Arrow vector slots must satisfy `addr % 64 == 0`. Unaligned pointer casts are strictly prohibited.
3. **Aliasing Invariant**: No mutable reference `&mut T` may coexist with any other reference to the same memory location.
4. **FFI Panic Invariant**: No Rust panic may unwind across `extern "C"` boundaries:
   ```rust
   #[no_mangle]
   pub extern "C" fn stardf_buffer_data(...) -> int32_t {
       std::panic::catch_unwind(|| {
           // Kernel logic
           0
       }).unwrap_or(-1)
   }
   ```

---

## 4. Fail-Closed Refusal Gates (`gates/*.rq`)

Every gate has an associated pass witness (0 rows) and fail witness ($\ge 1$ row):

| Gate | Refusal Condition |
|---|---|
| `010_api_naming.rq` | Struct/Enum not in `UpperCamelCase`, or function/module not in `snake_case`. |
| `020_unsafe_safety_proof.rq` | An `isUnsafe = true` function lacks an explicit `rust:safetyProof` explanation. |
| `030_alignment_invariant.rq` | A buffer slot bound to Arrow/SIMD has `byteAlignment != 64`. |
| `040_ffi_unwind_guard.rq` | An `extern "C"` export lacks `rust:unwindProtection`. |
| `050_workspace_inheritance.rq` | A member crate specifies a literal version for a dependency present in `[workspace.dependencies]`. |

---

## 5. Substrate Connectors

### 5.1 `avec` Columnar Connector
- Generates Arrow C Data Interface bindings using `avec_c_data.h`.
- Projects columnar structs with:
  ```rust
  #[repr(C, align(64))]
  pub struct ArrowBufferSlot {
      pub ptr: *const u8,
      pub len: usize,
  }
  ```
- Ensures zero-copy release handoffs via `atomic_release_swap`.

### 5.2 `bcinr` Branchless Connector
- Maps arithmetic and masking operations to `bcinr-logic`:
  ```rust
  use bcinr_logic::mask::{select_u32, min_u32, max_u32};
  use bcinr_logic::fix::add_sat;
  ```
- Generates CMOV sequences preventing branch mispredictions in hot scan loops.

---

## 6. Verification Ladder

```text
Stage 1: ggen SPARQL gate verification (010..050 = 0 violations)
Stage 2: rustfmt syntax verification (cargo fmt -- --check)
Stage 3: Compiler check across targets (cargo check --workspace --all-targets)
Stage 4: Clippy linter gate (cargo clippy --workspace --all-targets -- -D warnings)
Stage 5: Test courts (cargo test --workspace)
Stage 6: Soundness gate under Miri (cargo miri test)
Stage 7: Receipt validation (validate_receipt.py)
```
