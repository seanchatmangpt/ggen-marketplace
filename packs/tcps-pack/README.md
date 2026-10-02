# tcps-pack

Toyota Production System (TCPS) crate family (豊田コード生産方式) — **one pack,
one version, one admission unit, five crate modules**, consolidated (2026-09-30
wave) from `tcps-core-pack`, `tcps-cli-pack`, `tcps-ffi-pack`, `tcps-std-pack`,
`tcps-wasm-pack` (v0.1.0 each). Applies the drift law ("N implementations of
one calculus → O(N²) drift; converge on one kernel with N bindings") via the
capability-ecology precedent: `tcps-core` stays the kernel module (its content
anchors); the other crates are disjoint-namespace modules.

## Layout

| path | content |
|---|---|
| `ontology/{core,cli,ffi,std,wasm}.ttl` | one module per crate, per-crate namespaces verbatim (`…/packs/tcps-core#`, `…/packs/tcps-cli#`, `…/packs/tcps-ffi#`, `…/packs/tcps-std#`, `…/packs/tcps-wasm#`) |
| `gates/<crate>_<stem>.rq` | 10 violation-row SELECTs, family-prefixed exact stems (core ×2, cli ×1, ffi ×3, std ×2, wasm ×2), `ORDER BY`-deterministic |
| `witnesses/{pass,fail}/<gate-stem>.ttl` | exact-stem witnesses — pass must be silent, fail must fire |
| `qualification/verify.py` | the ONE uniform court (exact-stem, exit 0 = ADMITTED) |
| `templates/` | all 40 per-crate templates, output targets conserved and disjoint (`src/*.rs`, `crates/tcps-{cli,ffi,std,wasm}/**`); only the colliding FILE names gained family prefixes (`cargo_toml.tmpl` ×4, `lib.rs.rs` ×4 → `<crate>_…`) |
| `families/<crate>.md` | each absorbed pack's notes: namespace, individuals, template targets, gates |
| `reference/製品版/` | the ONE canonical vendored product snapshot (132 files, moved from tcps-core-pack) |
| `source-manifest.json` | the kernel's 43 ordered crate sources, sha256-verified against the snapshot |

## Module join doctrine

The five modules are joined by the consumer Cargo workspace (`tcps-core = {
path = "../..", package = "tcps-generated" }` in the cli crate's manifest), never
by cross-module graph references: every `dependsOnModule` edge lives inside its
own crate's namespace. The namespace IRIs are byte-verbatim from the absorbed
packs — two modules spell their prefix `tcps:` (core, cli) over DIFFERENT IRI
spaces, which is safe because prefixes are per-document syntax and the IRIs are
disjoint.

## Court

`python3 packs/tcps-pack/qualification/verify.py` — for each of the 10 gates,
the union ontology + `witnesses/pass/<stem>.ttl` must yield zero rows and the
union ontology + `witnesses/fail/<stem>.ttl` must yield ≥1 row. Exit 0 =
ADMITTED. Same uniform-court shape as `capability-ecology-pack`.

## Vendored snapshot dedup (provenance without duplication)

`tcps-release-pack/reference/` (91 files — ALL byte-identical to this pack's
canonical `reference/製品版/`) and tcps-core-pack's second internal snapshot
`豊田コード生産方式_v26.7.19/` (40 files: 27 byte-identical, 13 unique to the
older revision) were retired to manifests:

- `tcps-release-pack/SOURCE_MANIFEST.sha256` — sha256 + canonical origin per
  attested file (release can still prove what it was built against).
- `reference/SOURCE_MANIFEST.retired-豊田コード生産方式_v26.7.19.sha256` —
  sha256 + retired path per file of the second snapshot.

## Evidence boundary

Marketplace admission + real-ggen qualification + the exact-stem witness court
only. No execution authority; BRCE remains the sole actuation boundary.

## Supersession

Replaces `tcps-core-pack`, `tcps-cli-pack`, `tcps-ffi-pack`, `tcps-std-pack`,
`tcps-wasm-pack` (v0.1.0 each) — content moved verbatim (ontologies,
gates, non-colliding template names byte-identical; colliding template FILE
names family-prefixed, contents byte-identical); per-pack ad-hoc gate dirs
replaced by the single uniform court. `tcps-release-pack` stays a separate
pack (its 85 `infra/**` targets are its own release-engineering surface).
