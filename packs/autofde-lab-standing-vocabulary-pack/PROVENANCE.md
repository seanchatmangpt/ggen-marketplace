# Source provenance

The ontology in this pack is lifted from real files in
`seanchatmangpt/autofde-lab` (read at `/Users/sac/gym-ecosystem/vendor/autofde-lab`,
branch `main` at the time of authoring):

- `src/autofde_lab/standing.py` (338 LOC) — the hand-written runtime hierarchy:
  `StandingError` and its `Blocked / Unsupported / Unknown / NotRun / BuildBroken /
  PartialAlive / NotFound` subclasses, plus `TransitionViolation` and its 11
  subclasses, each carrying a `lawful_standing`. Every class name, standing string,
  and lawful standing in `ontology.ttl` is transcribed from that file, not invented.
- `ontology/standing.ttl` — the existing `afl:StandingValue` SKOS scheme
  (`UNKNOWN / PARTIAL_ALIVE / ALIVE / BLOCKED / BUILD_BROKEN / UNSUPPORTED`) that
  already projects `src/autofde_lab/constitution/standing.py` via the root
  `ggen.toml`. This pack does not modify that manifest or its outputs.
- `ggen.toml` (root) and `gymact/ggen.toml` — read to confirm this pack duplicates
  neither manifest's rules. The constitution projection covers the *declarative*
  standing vocabulary; the runtime raisable hierarchy is the uncovered twin.

## What this pack manufactures

`src/autofde_lab/generated/standing_vocabulary.py` (raisable hierarchy) and
`src/autofde_lab/generated/standing_registry.json` (machine-readable registry).
Both land under a `generated/` path so they cannot collide with the existing
hand-written `src/autofde_lab/standing.py`; adoption is a separate, deliberate act.

## Vocabularies reused

`skos:` (concept scheme + prefLabel for standing values), `dct:` (title,
description), `prov:` (a transition violation is a `prov:Entity` — a claim about a
derivation that did not occur). Only `afl:parentClass` and `afl:lawfulStanding` are
minted, because no published vocabulary covers "the standing a claim is entitled to
once an unlawful promotion is reversed".

## Authority boundary

This pack is declarative. It manufactures classification types and a registry; it
performs nothing, binds no capability, and grants no ambient authority.
`gates/010_no_actuation_authority.rq` refuses manufacture if any concept declares a
`urn:gymact:consequence:*` class, if `ALIVE`/`PARTIAL_ALIVE` is presented as a
raisable success standing, or if a concept escapes the pack's SKOS scheme.
Consequential DO remains external, behind GymAct/BRCE admission.
