# ggen Marketplace

The canonical repository of reusable **ggen packs**.

A pack is an ontology-backed manufacturing bundle: a manifest declares its identity, RDF states the admitted facts, templates project those facts into consumer artifacts, and optional SPARQL gates refuse invalid inputs before writes occur. Generated consumer files are consequences of the pack; they are not a second source of truth.

## Quick start

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog
python3 scripts/marketplace.py fingerprint
```

To consume a pack from a local checkout:

```toml
[packs]
ggen-combinatorial-maximalism-pack = { path = "../ggen-marketplace/packs/ggen-combinatorial-maximalism-pack" }
```

Then run `ggen sync run` from the consumer project.

## Repository contract

```text
packs/<pack-name>/
├── pack.toml       # identity: name, semantic version, description
├── ontology.ttl    # admitted RDF facts
├── templates/      # one or more ggen templates
├── gates/          # optional SPARQL refusal gates
└── README.md       # optional pack-specific documentation
```

The permanent catalog is the set of `pack.toml` manifests under `packs/`. `scripts/marketplace.py catalog` is a deterministic **projection** of those manifests; this repository deliberately does not maintain a second hand-edited catalog file.

## Documentation — Diátaxis

The documentation is organized by user need, not by file type:

- **Tutorials** — learn by completing a guided result: [`docs/tutorials/`](docs/tutorials/first-pack.md)
- **How-to guides** — accomplish a specific task: [`docs/how-to/`](docs/how-to/publish-a-pack.md)
- **Reference** — exact contracts and commands: [`docs/reference/`](docs/reference/pack-contract.md)
- **Explanation** — understand the architecture and tradeoffs: [`docs/explanation/`](docs/explanation/why-a-separate-marketplace.md)

Start at [`docs/index.md`](docs/index.md).

## Provenance

The initial corpus was imported byte-for-byte from `seanchatmangpt/ggen` at commit `c37b46015b8e5ab40be771d61aafe3d7c7af084c`. The source and destination `packs/` Git tree for that migration is `4d70ae027004db829a8c334d201ad8e4f5b75ce1`. See [`MIGRATION.md`](MIGRATION.md).

## Scope and standing

This repository owns reusable pack source and marketplace documentation. The ggen runtime remains responsible for interpreting and executing packs. Repository validation proves marketplace structure, manifest integrity, deterministic catalog projection, and documentation presence. It does **not** by itself prove generated consumer consequences, external system behavior, live-cloud authority, benchmark standing, or BRCE DO authority.

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md), and [`SECURITY.md`](SECURITY.md).
