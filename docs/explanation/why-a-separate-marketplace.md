# Explanation: why a separate marketplace

Packs and the ggen runtime change for different reasons. Runtime code defines **how lawful manufacture works**; packs encode reusable semantic/manufacturing knowledge that can evolve, compose, qualify, deprecate, and be distributed independently.

Keeping the corpus in a dedicated repository creates an explicit ownership boundary:

```text
ggen runtime        → interpretation / manufacture machinery
ggen-marketplace    → canonical reusable pack source / distribution / qualification
consumer repositories → domain execution / consequential authority
```

That separation avoids copying the runtime into the marketplace and avoids turning marketplace metadata into a second implementation of ggen.

## Marketplace as accumulated executable knowledge

The repository is not intended to become a flat bag of templates. Its durable value comes from accumulating **admitted reusable knowledge**:

- public and pack-specific ontology facts;
- deterministic projections;
- admission gates and negative witnesses;
- qualification fixtures;
- receipts/replay contracts;
- documentation/provenance;
- class/composition/supersession relationships.

As the corpus grows, the goal is class closure rather than ever more independent authorities. Shared protocol/lifecycle/maturity/projection truth should move into canonical kernels/capabilities; products/environments should become small profiles/worlds; normal consumers can use umbrellas without hiding the underlying modules.

This is why 100+ pack instances are not intrinsically a problem. Duplicate semantic authority is the problem.

## Independent maturity

A separate marketplace also allows pack maturity to be evaluated independently from runtime maturity. A ggen release can be healthy while one pack's domain court is broken; a pack can have excellent semantic/source maturity while an external consumer remains blocked; marketplace qualification can establish deterministic manufacture without granting production authority.

The [Level-5 maturity contract](../reference/level5-maturity-contract.md) makes those boundaries explicit.

## Provenance and modernization

The marketplace extraction began with byte-identical source provenance, then added repository-local admission, qualification, documentation, and maturity law. Extraction and modernization therefore remain distinguishable evidence events.

Future consolidation should follow the same rule: preserve exact before-state provenance, prove the shared semantic class, migrate consumers, then deprecate/delete only the redundant authority that is actually superseded.

See [Class closure and consolidation](class-closure-and-consolidation.md).
