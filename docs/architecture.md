# Current Observed Architecture: ggen-marketplace

## 1. Repository Purpose
`ggen-marketplace` is the canonical corpus of reusable, ontology-backed manufacturing units called **ggen packs**.

## 2. Directory Layout & Components
```text
ggen-marketplace/
├── marketplace.toml      # Marketplace operational law (release pins, asset digests, qualification limits)
├── packs/                # Canonical pack source directories (312 packs)
│   └── <pack-name>/
│       ├── pack.toml     # Identity manifest ([pack] name, version, description)
│       ├── ontology.ttl  # Admitted RDF graph(s)
│       ├── templates/    # Optional projection templates (.tmpl, .tera)
│       └── gates/        # Optional invariant gates (.rq, .py)
├── scripts/              # Local-first acceptance tooling
│   ├── marketplace.py    # Zero-dependency CLI: validate, catalog, archive, fingerprint
│   ├── admit-config.sh   # Formal star-toml configuration admission wrapper
│   └── qualify-marketplace.sh # Qualification execution against admitted config
└── docs/                 # Strictly separated Diátaxis documentation
    ├── tutorials/
    ├── how-to/
    ├── reference/
    └── explanation/
```

## 3. Core Operational Pipeline
1. `marketplace.toml` declared operational parameters $\rightarrow$ Admitted via `star-toml` (`q_config=1`).
2. `scripts/marketplace.py validate` checks pack manifests, RDF presence, and Diátaxis completeness.
3. `scripts/marketplace.py catalog` synthesizes a deterministic JSON projection across all packs.
4. `scripts/marketplace.py fingerprint` computes a SHA-256 digest over the entire pack tree.
