# NIST Cyber-Resiliency Generational Pack

This pack turns **NIST SP 800-160 Vol. 2 Rev. 1 cyber-resiliency constructs** into
machine-queryable semantic constraints without pretending that the Marketplace's
generational-remanufacture policy is itself a NIST requirement.

## Authority boundary

The pack is **semantic only**. It grants no filesystem, cloud, deployment, network,
or runtime actuation authority.

    NIST source anchors
      -> technique vocabulary
      -> consumer-declared resiliency profile
      -> SPARQL refusals
      -> bounded manufacture intent
      -> existing BRCE / governed runtime

The pack reuses existing Marketplace authority rather than embedding a second executor:

- `governed-runtime-adapter-pack` owns execution-mode, authority, resource-budget,
  replay, and receipt constraints.
- `supply-chain-evidence-pack` owns executable supply-chain evidence courts.
- `receipt-provenance-unification-pack` owns receipt/provenance validation.
- Fortune-5 architecture/deployment packs remain owners of provider-specific and
  enterprise deployment projections.

## NIST-derived surface

The ontology carries all fourteen cyber-resiliency techniques named by
SP 800-160 Vol. 2 Rev. 1: Adaptive Response, Analytic Monitoring, Contextual
Awareness, Coordinated Protection, Deception, Diversity, Dynamic Positioning,
Non-Persistence, Privilege Restriction, Realignment, Redundancy, Segmentation,
Substantiated Integrity, and Unpredictability.

## Marketplace extension: generational remanufacture

The following policy is **not represented as a NIST requirement**:

- each manufactured generation has a bounded generation identity;
- semantic/source/manufacturing identities are digest-bound;
- implementation inheritance is refused;
- compatibility obligation is refused;
- prior implementations may be evidence, but receive no standing merely because
  they previously existed;
- non-persistence, positioning, diversity, and other resiliency techniques are
  expressed as current-generation manufacture parameters;
- every admitted generation requires receipt identity.

This exposes the customer-facing control contract without publishing any private
generative equation.

## Cost-assessment boundary

Marketplace cost assessments are explicitly non-NIST facts. They identify where
generative manufacturing can reduce marginal software-change cost while retaining
the fact that independent compute, storage, regions, and other physical resources
remain intrinsically non-free.

## Sources

- NIST SP 800-160 Vol. 2 Rev. 1 — Developing Cyber-Resilient Systems
- NIST SP 800-53 Rev. 5 — Security and Privacy Controls
- NIST OSCAL — machine-readable security-control representation
