# Reference: pack classes

Marketplace **profiles** (`projection`, `semantic`, `project`) describe packaging shape. Pack **classes** describe semantic responsibility and composition role. The two taxonomies are independent.

The class model exists to prevent a flat directory of pack instances from becoming a flat set of competing semantic authorities.

## KernelPack

Owns a reusable semantic/calculus foundation shared by many consumers or families.

Examples of kernel concerns include maturity, standing, authority, consequence IR, public-ontology mappings, admission calculus, or a reusable projection grammar.

A kernel should avoid domain-specific specimen facts that force unrelated consumers into the same ABox.

## CapabilityPack

Adds one orthogonal reusable capability over an admitted kernel or public vocabulary. A capability pack should be independently composable when its dependency contract is satisfied.

Examples include routing, verification, receipt generation, SHACL projection, or a protocol feature.

## ProfilePack

Binds kernels/capabilities to a specific product, platform, deployment shape, organization, UI, documentation product, or operational profile.

Profiles should carry the semantic delta rather than copy the whole kernel ontology. They are the preferred destination for concrete defaults and domain-specific projections.

## WorldPack

Defines an executable/simulatable world, information partition, action space, falsifiers, or evaluation environment. World semantics must remain separate when combining them would change the environment being evaluated.

A WorldPack can consume shared GymAct/world kernels without becoming equivalent to another domain world.

## CompatibilityPack

Preserves a historical contract for existing consumers after a successor architecture exists. Compatibility packs should name the successor, document the preserved seam, and avoid receiving new features that belong in the successor family.

Compatibility is not authority to keep two competing canonical models indefinitely.

## EvidencePack

Defines receipts, evidence schemas, audit/certification mappings, provenance, or standing derivation. Evidence packs may observe/bind consequences but do not gain consequential DO authority merely because they can attest to them.

## ReleaseControlPack

Defines release/publish state transitions, gates, rollback, or release evidence. A release-control pack may manufacture a release intent or verification artifact; actual publication remains a distinct consequential boundary unless explicitly admitted.

## UmbrellaPack

Provides a stable consumer entry point that composes a family of kernels and capability packs. An umbrella owns composition/default selection, not duplicated domain semantics.

Use an umbrella when consumers normally need a coherent bundle but advanced consumers benefit from selecting modules independently.

## Class assignment rules

A pack may have more than one secondary role, but one role should explain its primary semantic responsibility. Class assignment should be based on what semantic authority the pack owns, not its name.

Do not infer equivalence from shared suffixes such as `-pack`, `-ui`, `-terraform`, `-mcp`, or `-world`. Before consolidation, compare:

- RDF classes/properties/individuals and imported vocabularies;
- gate/refusal semantics;
- generated target ownership;
- qualification subjects;
- external/runtime dependencies;
- authority ceiling;
- compatibility obligations;
- consumer inventory.

## Composition conflicts

Composition must fail closed or require explicit resolution when two packs attempt incompatible ownership of the same semantic or generated target.

Common conflict classes include:

- competing canonical definitions for the same concept;
- two projections owning the same path with different semantics;
- incompatible authority joins;
- mutually exclusive runtime versions;
- profile defaults that cannot be simultaneously satisfied;
- a compatibility pack silently overriding its successor.

## Consolidation target

The desired marketplace topology is not "few directories." It is:

```text
small set of canonical classes/kernels
        + orthogonal capabilities
        + explicit umbrellas
        + many parameterized profiles/worlds
```

A large number of pack instances is healthy when semantic authority is not duplicated. See [Class closure and consolidation](../explanation/class-closure-and-consolidation.md) and [How to consolidate a pack family](../how-to/consolidate-a-pack-family.md).
