# rust-pack Resolutions

Coordinator RESOLVE lane output. Merges recon lanes L1-L5 into one resolved
contract for write lanes L6-L10. Authority: PRD/ARD at `docs/` (do not
redesign), exemplar `packs/avec-pack` for convention. Each resolution cites
its authority. Commit nothing (integration lane owns git).

## 1. Structural contract (from L1, exemplar-verified)

Top-level file set (exactly):

```text
packs/rust-pack/
  README.md
  pack.toml
  gate-court.toml
  ontology.ttl
  gates/010_*.rq … 050_*.rq        (5 gates, snake_case stems, see §5)
  witnesses/pass/<stem>.ttl        (exact-stem match, 1 per gate)
  witnesses/fail/<stem>.ttl        (exact-stem match, 1 per gate)
  templates/*.tmpl                 (Tera, disjoint `to:` targets)
  qualification/consumer.ttl       (bounded positive specimen)
  qualification/validate_receipt.py
  qualification.toml               (registered divergences)
  docs/PRD.md, docs/ARD.md         (existing, do not edit)
```

No `ggen.toml` inside the pack; consumers pin via their own `[packs]` table.

## 2. Consumability contract (from L2, ggen-engine + marketplace.py)

Hard refusals to avoid (real gates, fail-closed):

- `pack.toml` `[pack]` CLOSED key set: `name`, `version`, `description`
  only (`marketplace.py:87`). `name` MUST equal `rust-pack`
  (PACK_DIRECTORY_IDENTITY). `version` MUST match strict semver
  (PACK_VERSION_SEMVER). `description` non-empty, ends with
  "Grants no execution authority."
- At least one `.ttl` at pack root: `ontology.ttl`
  (cures current `REFUSED:ONTOLOGY_SOURCE_MISSING:rust-pack`).
- `templates/`: only `.tmpl`/`.tera`/`.eex`, at least one (FM-PACK-005).
- `gates/`: `.rq`/`.py`/`.sh` suffixes only. `targets.toml` optional with
  `[targets] languages`; NEVER a `targets` key in pack.toml.
- No symlinks anywhere under `packs/`.
- Optional `[capabilities]` (`provides`/`requires`/`dialects`) admitted;
  closed dialect vocab.

## 3. Resolutions for L3 gaps (decide + authority)

R1 — Gate 010 name predicate (L3#2, ARD.md:131).
DECIDE: extend vocabulary with `rust:itemName xsd:string`, carried by every
`rust:Struct`, `rust:Enum`, `rust:Function`, `rust:Module` individual.
Authority: ARD §2.1 defines the domain classes; packs own their vocabulary
per L1 §7 (avec defines `av:` vocabulary inside ontology.ttl). Gate 010
classifies via `rdf:type` (Struct/Enum → UpperCamelCase; Function/Module →
snake_case REGEX from L4 chicago-tdd 030_value_constraints pattern).

R2 — Gate 050 crate-local dependency vocabulary (L3#1, ARD.md:135).
DECIDE: extend with `rust:Crate rust:dependsOn rust:Dependency` and
`rust:Dependency rust:versionLiteral xsd:string`. Gate 050 fires when a
crate's `dependsOn` target is also a `rust:Workspace
rust:workspaceDependency` member AND the edge carries `versionLiteral`.
Authority: same pack-owned-vocabulary rule; the workspace inheritance
surface is concrete (PRD.md:58-60).

R3 — Gate 030 buffer-slot class (L3#3, ARD.md:133).
DECIDE: extend with `rust:BufferSlot` class, `rust:simdProfile
("Arrow" | "SIMD" | "None")`, `rust:byteAlignment xsd:integer`.
Gate fires when `simdProfile != "None"` and `byteAlignment != 64`.
Authority: ARD §2.2 MemoryModel + UCG Alignment Invariant (ARD.md:111-112).

R4 — SHACL vs SPARQL contradiction (L3#4, PRD.md:111 vs ARD.md:16,125).
DECIDE: SPARQL violation-row `.rq` gates. Authority: ARD.md:12 states
"Fail-closed SPARQL refusal gates (010..050)" — the PRD's "SHACL" wording
is a terminology slip; the exemplar and court runner are SPARQL. Shape
discipline stays as rdfs:domain/range in ontology.ttl.

R5 — Miri contradiction (L3#5, PRD.md:97/109, ARD.md:171).
DECIDE: Miri is a CONSUMER-side stage, not a pack-admission gate. The pack
never executes cargo (L4 §5: no peer pack has cargo-executing gates; L5 §3:
miri not installed). Register
`ACCEPTED-WARN:miri-nightly-consumer-side` in `qualification.toml` citing
PRD.md:97 stable-toolchain law; document `rustup component add miri` as the
consumer replay prerequisite. Authority: L4 clap-noun-verb
qualification.toml ACCEPTED-WARN convention.

R6 — Witness format/court config (L3#6, under-specified).
DECIDE: avec-pack convention verbatim — `gate-court.toml` with
`schema = "ggen.semantic-gate-witness-court/1"`, `case_key = "exact-stem"`,
`runner = "python3 qualification/verify.py"` (informational, copy verbatim
per L5 §7), `gate_dir = "gates"`, `pass_dir = "witnesses/pass"`,
`fail_dir = "witnesses/fail"`, `require_pass = true`, `require_fail =
true`. Exactly one pass + one fail TTL per gate (10 witnesses). Authority:
L1 §3/§5, L5 §5 real court run.

R7 — Template suite (L3#7, ARD.md:169 vs ARD.md:50).
DECIDE: FIVE templates, not four — the four ARD-table templates plus the
court-test template the pipeline diagram requires. C-header output path:
`inc/<crate>.h` at workspace root (ARD.md:49 diagram wins over PRD.md:79).
Variables: see §6.

R8 — Crate↔item linkage (L3#8).
DECIDE: `rust:Crate rust:defines <item>` links every Struct/Enum/Function/
Module to its owning crate; `rust:crateModule` remains for Module nesting.
Authority: multi-crate projection (crates/<crate>/ targets) is a PRD
requirement; one-way links cannot project per-crate file fan-out.

R9 — ontology.ttl / pack.toml conventions (L3#9).
DECIDE: prefixes `rust: <urn:ggen:rust:#>` (ARD.md:7 authority) and
`p: <https://seanchatmangpt.github.io/packs/rust-pack#>` (house convention,
L1 §7). Version: `0.1.0` (PRD.md:4 is the pack's own declared version;
CalVer-vs-semver divergence noted — both pass PACK_VERSION_SEMVER; PRD is
authority for rust-pack). Header comment carries the projection law per
L1 §7. Every individual cites a spec URL in an rdfs:comment.

R10 — validate_receipt.py (L3#10).
DECIDE: ship `qualification/validate_receipt.py` inside the pack; validates
the 5 receipt fields named at ARD.md:37 as present, non-empty strings;
exit 1 on any missing field. Authority: receipt 5-field law (operating
doctrine R=5 fields) + ARD Stage 7.

R11 — rust:profile / rust:Profile dead vocabulary (L3#11).
DECIDE: DROP from ontology.ttl. Authority: ERRC asymmetry — delete
outranks generate; it appears in no capability, gate, or template.

R12 — thiserror vs no_std (L3#12, PRD.md:66/84-89).
DECIDE: core crates (`isNoStd = true`) use manual error enums; `std`
integration crates may use thiserror. Authority: PRD.md:90 isolates std to
IO/CLI integration crates; thiserror is std-oriented (L3).

R13 — bin/proc-macro tiering (L3#13, ARD.md:70 vs PRD.md:84).
DECIDE: no_std gate obligation binds only crates with `crateType "lib"`;
`bin`/`proc-macro` crates may set `isNoStd = false`. Template models the
`#![no_std] extern crate alloc` shell for lib kernels only. Authority:
PRD.md:84-90 ("every manufactured library crate", std integration crates).

R14 — resolver/edition (L3#14).
DECIDE: `resolverVersion "2"` fixed (PRD.md:47 authority); edition default
`"2021"` in vocabulary, `"2024"` permitted per crate; resolver does not
follow edition (declared literal). Authority: PRD pins resolver; ARD
permits edition values.

R15-R19 — Untestable prose requirements (L3#15-19).
DECIDE: `bcinr-powl` integration, CMOV misprediction prevention,
"indistinguishable from Core Team" rhetoric, and `atomic_release_swap`
zero-copy handoffs are NON-GATING prose. No gate, template, or acceptance
command covers them; they are registered in `qualification.toml` as
`ACCEPTED-WARN:untestable-prose-requirement` with citations. The 64-byte
alignment check (L3#19) is covered at the ontology layer by gate 030 — that
is the admitted layer for pack admission; compiled-layer verification is
consumer-side (mirrors R5).

## 4. Reuse decisions (from L4)

- Gate .rq conventions: `# MESSAGE:` first line, violation-row SELECT
  (0 rows = pass), pack PREFIX, `ORDER BY` deterministic, `?problem`/
  `?violation` BIND(CONCAT) diagnostics.
- Gate shape sources: chicago-tdd 030_value_constraints REGEX pattern for
  RFC 430 naming (010); 020_single_valued pattern where single-valued;
  avec 050 nested-aggregate pattern if a continuity invariant is needed.
- Templates: Tera frontmatter `to:` (disjoint) + `sparql:` named rows;
  `force: true` on always-regenerated files; Rust headers
  `//! GENERATED by ggen from ...`; `#![forbid(unsafe_code)]` on safe
  templates, deliberately relaxed with named `#[allow(...)]` scopes in the
  FFI shell template (new invention, gated by gate 040 vocabulary —
  disclosed as the pack's own contribution).
- MSRV from the graph (`rust:msrv`), never hardcoded.
- Proof-test pair per praxis-core: one hand-transcribed literal test, one
  SPARQL-derived test, both `include_str!`-anchored — satisfied by the
  court-test template (R7).
- qualification/consumer.ttl: one minimal specimen (one crate, edition,
  msrv, one unsafe fn with safetyProof, one BufferSlot, one FfiExport, one
  dependsOn inheritance edge) that all five gates run against.
- No cargo-executing gates inside the pack (L4 §5) — consumer-side ladder.

## 5. Verify ladder (from L5, all real commands)

From `/Users/sac/ggen-marketplace`:

1. `python3 scripts/check_gate_witness_courts.py --packs packs` → exit 0;
   rust-pack row: `standing: ALIVE`, `case_count: 5`, `require_pass: true`,
   `require_fail: true`.
2. Gate semantics (rdflib, no arq/roqet): per stem, pass witness + gate →
   0 rows; fail witness + gate → >=1 row.
3. `python3 scripts/marketplace.py check rust-pack` → exit 0 (baseline is
   REFUSED:ONTOLOGY_SOURCE_MISSING:rust-pack — flips when content lands).
4. Rust ladder (consumer-side, disclosed as such): `cargo fmt -- --check`,
   `cargo check --workspace --all-targets`, `cargo clippy --workspace
   --all-targets -- -D warnings`, `cargo test --workspace` on a rendered
   consumer workspace; Miri per R5.
5. `ggen sync run` twice in a consumer project; sha256-identical generated
   tree; second run `"written": []`.
6. `qualification/validate_receipt.py` on the receipt → exit 0 (R10).

`scripts/verify_marketplace_packs.py` lives in ggen-legacy, not here; do
not reference it from rust-pack receipts.

## 6. Resolved contract for write lanes L6-L10

### L6 — ontology lane (owns: `ontology.ttl`, `qualification/consumer.ttl`)

- `ontology.ttl` with prefixes `rust:` and `p:`; classes: Workspace,
  Crate, Struct, Enum, MemoryModel, BufferSlot, Function, FfiExport,
  Module, Dependency, Parameter, Field, Variant, Trait, Profile is DROPPED
  (R11).
- Resolved-vocabulary additions: `rust:itemName` (R1), `rust:dependsOn` +
  `rust:versionLiteral` (R2), `rust:simdProfile` + BufferSlot (R3),
  `rust:defines` (R8).
- >=1 `p:Subject` individual with `p:subjectId`, Promise individuals with
  `p:backedBy` (court-facing pair, L1 §7).
- Spec-URL rdfs:comment per individual; projection-law header (L1 §7).

### L7 — gates lane (owns: `gates/` — exactly these 5 files — plus `gate-court.toml`)

- `gates/010_api_naming.rq` — itemName regex per class (R1).
- `gates/020_unsafe_safety_proof.rq` — isUnsafe=true without safetyProof.
- `gates/030_alignment_invariant.rq` — BufferSlot simdProfile != "None"
  with byteAlignment != 64 (R3).
- `gates/040_ffi_unwind_guard.rq` — FfiExport without unwindProtection.
- `gates/050_workspace_inheritance.rq` — dependsOn a workspace dependency
  with versionLiteral (R2).
- All: `# MESSAGE:` line 1, violation-row SELECT, ORDER BY, anti-vacuity
  comment naming the fail-witness mutation.
- `gate-court.toml`: exact R6 block, `runner` copied verbatim.

### L8 — templates lane (owns: `templates/` — exactly these 5 files)

- `workspace_cargo_toml.tmpl` → `Cargo.toml` (resolver "2", workspace
  dependencies, member fan-out).
- `crate_cargo_toml.tmpl` → `crates/{{ row.crateName }}/Cargo.toml`
  (edition, msrv from graph, no_std/alloc features, inheritance).
- `lib_rs.tmpl` → `crates/{{ row.crateName }}/src/lib.rs`
  (`#![no_std]` shell, forbid(unsafe_code), module tree).
- `c_abi_h.tmpl` → `inc/{{ row.crateName }}.h` (FfiExport projections,
  R7 path resolution).
- `crate_court_test.tmpl` →
  `crates/{{ row.crateName }}/tests/{{ row.crateName }}_court.rs`
  (praxis-core two-proof pattern, R7).
- Targets disjoint; `force: true` on regenerated sources; header comment
  `//! GENERATED by ggen from the admitted rust-pack ontology.ttl. Do not
  edit.` Template variables come from SPARQL rows over: `crateName`,
  `edition`, `msrv`, `crateType`, `isNoStd`, `hasAlloc`, `resolverVersion`,
  `itemName`, `visibility`, `isUnsafe`, `safetyProof`, `symbolName`,
  `unwindProtection`, `byteAlignment`, `simdProfile`, `versionLiteral`.

### L9 — witnesses lane (owns: `witnesses/pass/` and `witnesses/fail/`)

Exactly 10 files (1 pass + 1 fail per gate stem, byte-matched stems):
`010_api_naming.ttl`, `020_unsafe_safety_proof.ttl`,
`030_alignment_invariant.ttl`, `040_ffi_unwind_guard.ttl`,
`050_workspace_inheritance.ttl` in each of pass/ and fail/. Pass: 2-8
triples, `# PASS witness:` header, zero rows. Fail: same minus/breaking
the load-bearing triple, distinct IRIs, trailing
`# Deliberately missing ...` comment, >=1 row. No ontology.ttl load.

### L10 — manifest lane (owns: `pack.toml` (edit existing), `README.md`, `qualification.toml`, `qualification/validate_receipt.py`)

- `pack.toml` `[pack]`: `name = "rust-pack"`, `version = "0.1.0"`,
  multi-line description ending "Grants no execution authority." Nothing
  else in `[pack]` (closed key set). Optional
  `[capabilities] provides = ["urn:ggen:pack:rust-pack"]`.
- `README.md`: H1 `rust-pack`, Layout / What the graph models / Gates
  table / Projections table / Standing (real receipt block of the §5
  ladder) / Evidence boundary / See Also.
- `qualification.toml`: ACCEPTED-WARN rows for R5
  (miri-nightly-consumer-side) and R15-R19
  (untestable-prose-requirement), each with citation.
- `qualification/validate_receipt.py` per R10; `consumer.ttl` is L6's.

## Cross-lane notes

- Shared-seam file: none — leases above are disjoint. `docs/` untouched.
- Compile-freeze SLA: not applicable (no shared compile surface; gates are
  text + rdflib). Disclose any minimal unblock in both receipts.
- Pre-existing, NOT this wave's regression:
  `REFUSED:ONTOLOGY_SOURCE_MISSING:rust-pack` and
  `smalt-core-pack` MANIFEST/ONTOLOGY refusals under marketplace-wide
  check; miri uninstalled; `qualification/verify.py` runner path
  nonexistent anywhere (informational field, L5 §7).
