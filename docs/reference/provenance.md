# Reference: provenance

The initial marketplace corpus was imported from:

- source: `seanchatmangpt/ggen`
- source commit: `c37b46015b8e5ab40be771d61aafe3d7c7af084c`
- source root tree: `b592334147fe46964a50b0e3f83df45fa7f62a30`
- source `packs/` tree: `4d70ae027004db829a8c334d201ad8e4f5b75ce1`
- destination initial base: `40a17c2e24a04b5bb2d66f6a0a30d12a8611cb2d`

The migration established destination `packs/` tree equality with the source tree. [`MIGRATION.md`](../../MIGRATION.md) records the execution receipt.

That identity is **historical import provenance, not current source authority**. After admission into this repository, the canonical marketplace pack bytes are the exact `packs/` tree of the marketplace subject being qualified. Later changes in `ggen`, a local checkout, or any other mirror do not silently rewrite or supersede those bytes.

## Current authority law

Current operational source/manufacturer identity is carried by `marketplace.toml` and must be read/admitted from that file rather than duplicated in documentation. It identifies the canonical marketplace repository/branch and the exact qualifier/manufacturer release identity plus platform asset digests.

`scripts/verify_source_authority.py` binds those roles to a deterministic pack-corpus fingerprint. `scripts/install-ggen.sh` additionally verifies the admitted ggen release identity before accepting the digest-pinned binary.

Future pack commits establish new destination identities; they do not alter historical import identities and cannot transfer pack authority back to an origin or mirror repository.

## Provenance during consolidation

Pack-family consolidation creates a second kind of provenance obligation. When duplicated semantics are factored into a kernel/capability/umbrella, preserve:

- exact predecessor pack SHAs/versions;
- semantic facts moved, mapped, or intentionally left separate;
- generated target ownership before/after;
- consumer/compatibility relationships;
- negative witnesses before/after;
- supersession/deprecation edges;
- rollback path.

A physical merge does not erase the histories of the predecessor packs. A CompatibilityPack remains provenance-relevant until its consumers have an evidenced migration path.

See [Pack classes](pack-classes.md), [Class closure and consolidation](../explanation/class-closure-and-consolidation.md), and [How to consolidate a pack family](../how-to/consolidate-a-pack-family.md).
