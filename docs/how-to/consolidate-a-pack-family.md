# How to consolidate a pack family

Use this procedure when several packs appear to duplicate the same semantic or manufacturing responsibility. The goal is class closure, not fewer directories at any cost.

## 1. Freeze the family subject

Record the exact marketplace SHA and the candidate pack names. Do not add/remove candidates mid-audit without starting a new receipt.

For every candidate collect:

```text
pack.toml
RDF/Turtle sources
gates/
templates/ or project generation rules
qualification inputs
README/docs
generated target paths
known consumers
runtime/toolchain dependencies
authority ceiling
```

## 2. Assign provisional classes

Use [Pack classes](../reference/pack-classes.md): KernelPack, CapabilityPack, ProfilePack, WorldPack, CompatibilityPack, EvidencePack, ReleaseControlPack, or UmbrellaPack.

Class assignment is a hypothesis. The source and consumer graph must confirm it.

## 3. Compare semantic authority

Build a pairwise map of classes/properties/individuals/imported vocabularies and identify facts that are:

- byte/term equivalent;
- logically equivalent;
- overlapping but not equivalent;
- domain-specific;
- legacy compatibility-only.

Only the first two are immediate canonicalization candidates. Overlap requires an explicit mapping or preserved separation.

## 4. Compare generated target ownership

List every path/pattern each pack may manufacture. Refuse a proposed composition when two packs claim the same target with incompatible semantics.

If multiple product packs use the same rendering engine but different domain facts, factor the rendering grammar into a kernel/capability and keep the products as profiles.

## 5. Compare admission and negative witnesses

Two packs are not equivalent if they admit/refuse different subjects in a consequential way. Run each family's positive and negative witnesses before refactoring, then rerun the same witnesses after refactoring.

Preserve typed refusal identities or document the migration if refusal names are intentionally superseded.

## 6. Compare execution and authority

Identify what each pack can construct and what, if anything, its consumer may actuate.

A consolidation must not widen:

```text
SELECT → CONSTRUCT → DO
```

If two modules have different DO owners, keep the authority boundary explicit even if their semantic vocabulary is unified.

## 7. Choose the least irreversible consolidation

Prefer, in order:

1. canonical shared ontology/import;
2. shared query/template/projection kernel;
3. orthogonal capability extraction;
4. umbrella composition;
5. profile conversion;
6. deprecation with named successor;
7. physical deletion only after consumer migration is proved.

This order preserves maximal reversible combinations while removing duplicated truth early.

## 8. Preserve compatibility

For a legacy pack, record:

- successor pack(s);
- exact compatibility seam retained;
- known consumers;
- migration recipe;
- date/version at which new features stop landing in the legacy surface;
- negative controls proving the successor does not accidentally import legacy specimen behavior.

Do not hide compatibility status in prose alone when a machine-readable lifecycle vocabulary is available.

## 9. Re-run marketplace and consumer courts

Run canonical marketplace acceptance:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

Then run each affected family's real consumer/runtime courts and negative witnesses. Marketplace qualification alone does not prove a migrated consumer still behaves correctly.

## 10. Publish a consolidation receipt

Record:

- exact base/head;
- family inventory;
- before/after class assignments;
- semantic facts moved vs preserved;
- generated target ownership before/after;
- admission/refusal correspondence;
- consumer migration evidence;
- authority ceiling before/after;
- replay/receipt results;
- deleted/deprecated surfaces;
- rollback;
- unresolved non-equivalences.

If one member cannot lawfully consolidate, leave it separate and continue with the proved subset. A failed pairwise edge does not invalidate the entire family graph.
