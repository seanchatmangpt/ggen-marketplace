# EMPIRE OSTAR reconstitution pack

This pack is the clean-room starting point for the EMPIRE case study. It does
not copy the platform-engineering handbook and it does not rename a book-derived
repository. It manufactures a bounded observation study from declared RDF facts.

The case begins with three incompatible or incomplete subjects called OSTAR or
OntoStar. None is declared canonical. Their names, documentation, imports, and
runtime boundaries are observations; they are not authority.

## Rice fence

Rice's theorem prevents a general decision procedure for non-trivial semantic
properties of arbitrary programs. The practical consequence here is precise:
the study must not infer what the legacy estate "really is" or claim unrestricted
program equivalence. It may compare exact artifacts and explicitly named
observable surfaces only.

The generated study therefore begins with:

- `authority_state = NO_AUTHORITY`;
- `universal_equivalence_claimed = false`;
- every candidate capability at `UNKNOWN`;
- every source at `authority = false`;
- unresolved contradictions preserved as observations;
- `direct_actuation = false`.

An explicit, digest-bound authority contract may later assign exactly one of
`PRESERVED`, `SUBSUMED`, `REPLACED`, `ARCHIVED`, or `REFUSED` to every candidate.
That contract is not part of this pack because manufacturing one would fabricate
the very authority the case study is designed to expose.

## Generated consequence

Consuming the pack generates:

`empire/reconstitution/ostar/study.json`

The result is accepted by `ggen-legacy/tools/v26.8.1/authority_vacuum.py observe`.
Observation can construct an evidence-bound candidate state, but neither this
pack nor the observer grants CASTLE `DO` authority.

## Source boundary

The private OSTAR coordinates in the ontology are Git object identities observed
through the GitHub connector. Their bytes were not available to the local clean
room, so the observer must report that subject as `PARTIAL_ALIVE` until an exact
tree is mounted. The public `open-ontologies` subject can be independently
materialized and verified at its exact commit.
