# Reference: catalog command

```bash
python3 scripts/marketplace.py catalog
```

The command emits deterministic UTF-8 JSON to stdout with sorted keys. The root object carries `marketplace_version`, sourced from `[marketplace].version` in `marketplace.toml`. That is the whole-registry snapshot identity and is independent of individual pack SemVer and the pinned upstream ggen runtime identity.

Do not copy a current marketplace/ggen version from documentation. Read executable source:

```bash
python3 scripts/marketplace.py version
```

and inspect/admit `marketplace.toml` for runtime qualification identity.

## Pack records

Records are sorted by pack identity and include the fields defined by the current catalog schema, including pack identity/description/path, derived packaging profile, source/template/gate metadata, deterministic source fingerprints, deterministic archive digest/size, and the projected download URL.

`profile` is one of `projection`, `semantic`, or `project`. It describes packaging shape, not [pack class](pack-classes.md), maturity, or standing.

Archive digest/size are computed from deterministic archive construction rather than a hand-maintained artifact table. The download URL is deterministic metadata; it may still be unavailable until the publication workflow has produced the corresponding release asset.

The root object identifies the catalog schema used by the current implementation. Consumers should branch on the schema value rather than inferring compatibility from marketplace release names.

The catalog is a **projection** and is intentionally not committed as a second editable source of truth. Running the command twice at the same admitted filesystem subject must produce byte-identical stdout.

## `archive`

```bash
python3 scripts/marketplace.py archive
```

Builds every admitted pack's deterministic `.tar.gz` under `dist/packs/` and emits each pack's identity plus SHA-256. Archive construction fixes order and metadata so a from-source rebuild can be compared with the published artifact.

The publication workflow uploads those assets after the relevant main-branch publication event. Archive existence and digest validity prove distribution identity, not consumer runtime behavior or Level-5 maturity.

## `version`

```bash
python3 scripts/marketplace.py version
```

Prints the marketplace's whole-registry version from `marketplace.toml`. The marketplace version, pack versions, and ggen runtime version are three deliberately separate axes:

```text
marketplace snapshot identity
≠ pack semantic/package version
≠ manufacturer/runtime version
```

A versioned marketplace release is a distribution/identity event. It does not automatically upgrade the standing of every included pack; exact-subject qualification and each pack's claimed consumer/domain boundaries retain their own evidence.

## Relationship to Level 5

The catalog is useful Level-5 **reference/distribution** infrastructure because it deterministically projects admitted pack identity/source metadata. It does not carry enough information to establish Level 5 by itself.

Level-5 class/composition information should eventually be projected from admitted semantic class/supersession/dependency facts rather than inferred from directory names. See [Pack classes](pack-classes.md) and [Level-5 maturity contract](level5-maturity-contract.md).
