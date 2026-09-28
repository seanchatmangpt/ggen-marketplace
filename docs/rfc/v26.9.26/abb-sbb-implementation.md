# RFC v26.9.26 — ABB/SBB marketplace implementation seed

## Ownership
This repository owns reusable **industry architecture packs** and **SBB qualification packs**, not the canonical enterprise-architecture ontology.

Consume the canonical v26.9.26 EA semantics from `chatman-ecosystem`.

## Definition of done
1. Add an `enterprise-architecture-pack` that projects/imports the canonical EA vocabulary without copying ownership.
2. Represent industry capability maps, value streams, ABB catalogs, architecture contracts, SBB candidate profiles, transition patterns and governance rules as reusable pack assets.
3. Add SHACL/SPARQL gates for:
   - vendor/product typed as ABB -> REFUSED;
   - Pack typed as enterprise architecture -> REFUSED;
   - qualified SBB without immutable subject/evidence -> REFUSED;
   - candidate SBB exceeding authority ceiling -> REFUSED;
   - UNKNOWN promoted to QUALIFIED/ALIVE -> REFUSED.
4. Add at least one worked industry fixture with one ABB and >=2 candidate SBBs.
5. Add one positive qualified SBB and one typed refusal.
6. Generate a deterministic QualificationReceipt projection and prove second-run byte identity.
7. Expose the pack to ggen manufacture and autofde-lab qualification.
8. No consequential DO authority in marketplace assets.

Success means packs are executable architecture semantics, not documentation.
