# frozen-duckdb-pack

Domain laws of [frozen-duckdb](https://github.com/seanchatmangpt/frozen-duckdb)
as marketplace facts, so consumer repos **consume them instead of hand-rolling**
`build.rs`, fetch scripts and cache plumbing. Distilled from the frozen-duckdb
repository at the v1.5.5 wave (`docs/sjira/v26.9.21`, `HANDWRITTEN.md` rows
TR4–TR7 — this pack is the intended owner pack of several of those ledger rows,
so adopting it is the paydown path).

## The five laws (skos:notation handles)

| handle | law |
|---|---|
| `version-pinning` | The consumer crate version mirrors the bundled upstream DuckDB engine release; the upstream duckdb-rs crate encodes the engine as `MAJOR.(MAJOR*10000+MINOR*100+PATCH).0` — crate `1.10505.0` = engine `1.5.5`. Derived pins (crates.io, clone branches, test workspaces) translate by the formula, never by guess. |
| `release-asset-name` | Release assets are `libduckdb_{arch}.{dylib\|so}` matching the `ensure_binary()` download URLs (`{base}/v{version}/libduckdb_{arch}.{ext}`); macOS assets are universal (arm64+x86_64) since DuckDB 1.5.x; Linux assets may 404 pre-tag — pinned local compile is the fallback. |
| `cache-normalization` | Every acquisition path normalizes `~/.frozen-duckdb/cache/v{version}-{arch}/`: arch-suffixed binary, pinned headers under `duckdb/` (bindgen reads `{cache}/duckdb/duckdb.h`), plain link name `libduckdb.{dylib,so}` beside the arch binary so `-lduckdb` resolves. |
| `docs-rs-no-link` | Under `DOCS_RS=1` the build script generates bindings from vendored headers and skips library lookup, linking and rpath emission — rustdoc never links, so docs.rs typechecks without the dylib. The script re-runs on `DOCS_RS` transitions. |
| `soname-rpath` | DuckDB >= 1.5 dylibs carry the neutral install name `@rpath/libduckdb.dylib` (no versioned soname); consumers embed `-Wl,-rpath,{lib_dir}` at link time (a link-time `-L` does not survive to load time); compat symlinks `libduckdb.dylib`/`.1.dylib`/`.1.4.dylib` keep older loaders working. |

## Structure

```
pack.toml                      pack identity (name/version/description)
ontology.ttl                   the laws + evidence anchors (semantic source)
gates/010_law_completeness.rq  SPARQL: every law carries notation/title/description
gates/015_evidence_anchors.rq  SPARQL: every prov:wasDerivedFrom resolves to a labeled entity
gates/020_version_encoding.rq  SPARQL: version-maps satisfy the encoding arithmetic
gates/030_structural_check.py  executable structural check script (pack + fixture shape,
                               asset naming, version pins, cache layout)
templates/frozen_duckdb_laws.md.tmpl   -> docs/frozen-duckdb-laws.md
templates/sys_build_rs.tmpl            -> crates/frozen-duckdb-sys/build.rs
qualification/consumer.ttl     deterministic fixture = frozen-duckdb 1.5.5 state
```

## Vocabulary law

Standard vocabularies only: classes and predicates come exclusively from
`rdf:`, `rdfs:`, `dcterms:`, `skos:`, `prov:`, `xsd:`. Laws are `skos:Concept`
members of one `skos:Collection` (`<urn:frozen-duckdb:laws>`); their stable
handles are `skos:notation` literals; evidence anchors are `prov:Entity`
individuals whose `rdfs:label` names a repo-relative path in frozen-duckdb;
version correspondences are `prov:Collection` version-maps of `prov:value`
entities. No private predicate/class namespace is introduced, so no
failed-edge justification is required. Individual IRIs use the pack-scoped
`urn:frozen-duckdb:*` scheme (identifiers, not vocabulary).

## Consumer adoption contract

1. Declare the pack (path form, as with any local pack):
   ```toml
   [packs]
   "frozen-duckdb-pack" = { path = ".../packs/frozen-duckdb-pack" }
   ```
   (or the marketplace name after admission, via `[[ontology.pack]]`).
2. Assert your repo's facts in your domain ontology with the same shape as
   `qualification/consumer.ttl`: one version-map (`duckdb-rs crate version` +
   `DuckDB engine release` members), your release assets, cache directories,
   and build-policy entities — all `prov:Entity` with `prov:value`, anchored
   where possible with `prov:wasDerivedFrom`.
3. Render the consequences (`ggen sync run`): the law reference and the
   frozen-duckdb-sys `build.rs` are projected from your facts + the pack laws.
4. The gates run over the merged graph: zero rows on
   `010`/`015`/`020` is the pass condition, and
   `gates/030_structural_check.py` exits 0. Gate 020 catches wrong pins
   arithmetically (e.g. pinning `1.10506.0` against engine `1.5.5` refuses).

## Constructor deviation (recorded per ticket C6-PACK)

The canonical entry path is `ggen-self-pack` / `ggen pack new` (per
`packs/pack-authoring-pack`'s deprecation note). In this environment:

- `ggen pack new frozen-duckdb-pack --description ... --version 0.1.0`
  exited **0 but created zero files** (silent no-op; run twice, output
  preserved in the ticket receipt).
- Its documented prerequisite `ggen init self` does not exist on the pinned
  CLI generation: `ggen init self` → `error: unexpected argument 'self'`
  (exit 2). The materializer exists as the separate top-level verb
  `ggen init-self`, but running it here would materialize the embedded
  constructor over the **existing** `packs/ggen-self-pack/` — touching
  another pack, which ticket C6 forbids.

The pack was therefore authored directly, following the structural shape of a
recent clean pack (`packs/readme-diataxis-pack`: `pack.toml` + `ontology.ttl`
+ `templates/` + `gates/` + `README.md`, plus `qualification/consumer.ttl` for
gate fixtures). No constructor output was hand-edited because none was
produced.

## Evidence base (frozen-duckdb @ v1.5.5 wave 4)

- `Cargo.toml` — `[workspace.package] version = "1.5.5"`.
- `crates/frozen-duckdb-builder/src/lib.rs` — `ensure_binary`,
  `ensure_headers`, `ensure_link_name`, `release_asset_name_for`,
  `download_from_github_release` (laws 2, 3).
- `crates/frozen-duckdb-sys/build.rs` — `DOCS_RS` branch, rpath link-arg
  (laws 4, 5).
- `prebuilt/setup_env.sh` — asset law + install-name compat symlinks
  (laws 2, 5).
- `test-dependency/Cargo.toml` + `HANDWRITTEN.md` — `duckdb = "1.10505"` pin
  (law 1).
- `docs/sjira/v26.9.21/MILESTONE.md` — universal macOS dylib, TR7 verify list
  (laws 1, 2).
