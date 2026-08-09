# Reference: provenance

The initial marketplace corpus is bound to:

- source: `seanchatmangpt/ggen`
- source commit: `c37b46015b8e5ab40be771d61aafe3d7c7af084c`
- source root tree: `b592334147fe46964a50b0e3f83df45fa7f62a30`
- source `packs/` tree: `4d70ae027004db829a8c334d201ad8e4f5b75ce1`
- destination initial base: `40a17c2e24a04b5bb2d66f6a0a30d12a8611cb2d`

The migration established destination `packs/` tree equality with the source tree. [`MIGRATION.md`](../../MIGRATION.md) records the execution receipt.

Future pack commits establish new destination identities; they do not alter the historical source identity.
