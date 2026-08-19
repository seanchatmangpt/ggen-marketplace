# How to migrate a pack

Migration preserves authority/provenance first and modernizes second.

## 1. Resolve the source exactly

Record the source repository, source revision SHA, pack/subtree path, and source tree/blob identities when available.

## 2. Classify the source before copying

Identify its semantic authority, generated target ownership, gates/refusals, runtime dependencies, consumers, compatibility seams, and provisional [pack class](../reference/pack-classes.md).

This prevents a migration from accidentally turning a profile or compatibility seam into a new canonical kernel.

## 3. Copy without semantic edits

Copy source bytes into the marketplace in a migration-only commit. Do not combine extraction, modernization, deprecation, or consolidation into the same evidence event.

Compare source and destination tree/content identities where the transport permits it.

## 4. Record provenance separately from authority

Import ancestry proves where bytes came from. After marketplace admission, canonical marketplace source authority remains `seanchatmangpt/ggen-marketplace`; the historical source becomes provenance unless an explicit contract says otherwise.

## 5. Validate destination admission

Run:

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py fingerprint
```

If a real-ggen behavior claim is being preserved, qualify the migrated pack against the same bounded consumer/runtime contract used before migration whenever that evidence is available.

## 6. Modernize in a separate transition

Only after migration identity is receipted should you:

- normalize ontology vocabulary;
- add gates/negative witnesses;
- compose `pack-maturity-pack`;
- split kernel/capability/profile responsibilities;
- create an umbrella;
- deprecate a legacy surface;
- update Level-5 Diátaxis.

Keeping modernization separate makes rollback and equivalence review tractable.

## 7. Preserve compatibility and class closure

If the migrated pack overlaps an existing marketplace family, run [the consolidation procedure](consolidate-a-pack-family.md). Do not delete one copy until semantic equivalence/supersession and consumer migration are proved.

A compatibility pack should name its successor and the seam it preserves.

## 8. Publish a migration receipt

Record source/destination SHA/tree identities, files copied, transport limitations, validation/qualification evidence, source-authority result, compatibility status, modernization deferred, falsifiers, and rollback.

Delete any temporary migration actuator before publication.

The initial marketplace extraction is documented in [`MIGRATION.md`](../../MIGRATION.md).
