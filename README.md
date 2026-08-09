# ggen Marketplace

The canonical repository of reusable **ggen packs**.

A pack is an ontology-backed manufacturing or semantic bundle: a manifest declares identity, RDF states admitted facts, templates may project those facts into consumer artifacts, and gates may refuse invalid inputs or verify pack-specific invariants. Generated consumer files are consequences of the pack; they are not a second source of truth.

## Quick start

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog
python3 scripts/marketplace.py fingerprint
```

To consume a projection pack from a local checkout:

```toml
[packs]
ggen-combinatorial-maximalism-pack = { path = "../ggen-marketplace/packs/ggen-combinatorial-maximalism-pack" }
```

Then run `ggen sync run` from the consumer project.

## Admitted pack profiles

The marketplace preserves real ggen pack diversity instead of forcing every pack into one scaffold:

- **projection** — manifest + RDF + `.tmpl`/`.tera` templates;
- **semantic** — manifest + RDF, with optional gates/catalogs and no required template;
- **project** — a self-contained `ggen.toml` project with RDF and optional templates/rules/queries.

Every admitted profile still requires `pack.toml`, a SemVer identity, a non-empty description, and at least one RDF Turtle source at the pack root or under `ontology/`.

The permanent catalog is the set of admitted manifests under `packs/`. `scripts/marketplace.py catalog` is a deterministic **projection**; this repository deliberately does not maintain a second hand-edited catalog file.

## Documentation — Diátaxis

- **Tutorials** — [`docs/tutorials/`](docs/tutorials/first-pack.md)
- **How-to guides** — [`docs/how-to/`](docs/how-to/publish-a-pack.md)
- **Reference** — [`docs/reference/`](docs/reference/pack-contract.md)
- **Explanation** — [`docs/explanation/`](docs/explanation/why-a-separate-marketplace.md)

Start at [`docs/index.md`](docs/index.md).

## Provenance

The initial corpus was imported byte-for-byte from `seanchatmangpt/ggen` at commit `c37b46015b8e5ab40be771d61aafe3d7c7af084c`; source and destination initially shared `packs/` tree `4d70ae027004db829a8c334d201ad8e4f5b75ce1`. After that receipt was established, marketplace admission removed source directories that explicitly documented themselves as orphaned/non-pack research artifacts and repaired incomplete manifest metadata. See [`MIGRATION.md`](MIGRATION.md).

## Scope and standing

This repository owns reusable pack source and marketplace documentation. The ggen runtime remains responsible for interpreting and executing packs. Repository validation proves marketplace admission, deterministic catalog projection, and documentation presence. It does **not** by itself prove generated consumer consequences, external-system behavior, live-cloud authority, benchmark standing, or BRCE DO authority.

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md), and [`SECURITY.md`](SECURITY.md).
