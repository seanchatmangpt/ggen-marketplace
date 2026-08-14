# Explanation: source of truth

A pack should answer “what is admitted?” before it answers “what file was emitted?”. RDF is the semantic source, the manifest gives pack identity, templates project admitted facts, and gates reject invalid facts before writes.

For marketplace distribution, **the admitted `packs/` bytes in this repository are canonical**. A pack may have been imported from `ggen`, GymAct, AutoFDE Lab, or another source repository, and another repository may later carry a byte-identical mirror. Those relationships are provenance only after admission here. Branch ancestry in an import source cannot silently move marketplace source authority away from `seanchatmangpt/ggen-marketplace`.

This is deliberately separate from manufacture authority. `marketplace.toml` pins the exact `ggen` release tag, the commit that tag resolves to, and each release-asset digest. The installer verifies tag → commit identity before accepting a digest-pinned binary. ggen qualifies and manufactures from marketplace source; it does not become a second authority for the pack bytes merely because it executes them.

The source-authority chain is therefore:

```text
pack RDF / templates / gates in ggen-marketplace
        ↓ admission
canonical marketplace pack source
        ↓ exact ggen tag + commit + asset digest
qualification / deterministic manufacture
        ↓
consumer consequence + receipt
```

`scripts/verify_source_authority.py` fails closed if a mirror is promoted to authority, the canonical repository/branch identity drifts, the ggen release loses exact commit identity, the platform digest matrix is malformed, or the pack corpus contains symlinks. It also emits a deterministic SHA-256 fingerprint over the admitted pack corpus so an exact marketplace subject can be bound to its actual source bytes.

This is why the marketplace does not keep a hand-edited `catalog.json`. Such a file would duplicate manifest facts and eventually drift. Instead, `scripts/marketplace.py catalog` computes a deterministic projection whenever a machine or human needs catalog JSON.

The same principle applies to consumer outputs: when an emitted file disagrees with the pack source, fix the ontology/template/gate boundary and regenerate rather than blessing the drift in place.
