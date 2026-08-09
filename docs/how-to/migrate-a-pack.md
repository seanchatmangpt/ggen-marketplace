# How to migrate a pack

1. Resolve the source repository and source revision to an exact SHA.
2. Record the source pack or subtree Git identity before copying.
3. Copy the pack source without semantic edits in the migration commit.
4. Compare source and destination content/tree identities where the transport permits it.
5. Record provenance separately from later modernization changes.
6. Run `python3 scripts/marketplace.py validate` in the destination.
7. Delete any temporary migration actuator before publication.
8. If modernization is needed, perform it in a later, separately reviewable commit so extraction evidence remains intelligible.

The initial marketplace extraction is documented in [`MIGRATION.md`](../../MIGRATION.md).
