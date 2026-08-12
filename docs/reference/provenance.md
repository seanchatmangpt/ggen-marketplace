# Reference: provenance

The initial marketplace corpus was imported from:

- source: `seanchatmangpt/ggen`
- source commit: `c37b46015b8e5ab40be771d61aafe3d7c7af084c`
- source root tree: `b592334147fe46964a50b0e3f83df45fa7f62a30`
- source `packs/` tree: `4d70ae027004db829a8c334d201ad8e4f5b75ce1`
- destination initial base: `40a17c2e24a04b5bb2d66f6a0a30d12a8611cb2d`

The migration established destination `packs/` tree equality with the source tree. [`MIGRATION.md`](../../MIGRATION.md) records the execution receipt.

That identity is **historical import provenance, not current source authority**. After admission into this repository, the canonical marketplace pack bytes are the exact `packs/` tree of the marketplace subject being qualified. Later changes in `ggen`, a local checkout, or any other mirror do not silently rewrite or supersede those bytes.

Current operational law is carried by `marketplace.toml`:

- `source_authority.repository = "seanchatmangpt/ggen-marketplace"`;
- `source_authority.canonical_branch = "main"`;
- `source_authority.mirrors_are_provenance_only = true`;
- `ggen.version` plus `ggen.release_commit` identify the qualifier/manufacturer;
- each platform release asset is independently SHA-256 pinned.

`scripts/verify_source_authority.py` binds those roles to a deterministic pack-corpus fingerprint. `scripts/install-ggen.sh` additionally refuses a release tag whose Git ref no longer resolves to the admitted `ggen.release_commit` before it accepts the digest-pinned binary.

Future pack commits establish new destination identities; they do not alter historical import identities and cannot transfer pack authority back to an origin or mirror repository.
