# Source provenance

Ontology derived mechanically from the real ggen-ecosystem repository at
`/Users/sac/gym-ecosystem/vendor/ggen-ecosystem`, branch `chore/crown-submodule-sync-ggen`.

## Source files the ontology derives from

- `contracts/standing-transitions/st01-*.json` .. `st50-*.json` — 50 hand-written contract
  documents (8 `kind: foundation`, 42 `kind: transition`). Every individual in
  `ontology.ttl` carries `prov:hadPrimarySource` naming its exact source file.
- `docs/STANDING.md` — the seven admitted standings and their definitions
  (`UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`,
  `REFUSED:<type>`), lifted verbatim as `skos:definition`.
- `scripts/ecosystem_alive.py`, `scripts/dod_engine.py` — the consumers that currently
  restate the standing vocabulary as inline string literals; `generated/standing_vocabulary.py`
  is the artifact that replaces those literals with one generated source.

## Vocabularies reused

`skos:` (ConceptScheme/Concept/prefLabel/definition for the standing enum), `dcterms:`
(identifier/title/description/source), `prov:` (hadPrimarySource for per-individual citation).
`eco:` (`https://ggen.dev/ecosystem#`) is the repo's own existing namespace, reused not minted.
Only `urn:ggen-ecosystem:standing:` individual identifiers are minted.

## What it manufactures

| Output | Replaces |
| --- | --- |
| `generated/standing_vocabulary.py` | hand-kept standing literals in `scripts/*.py` |
| `generated/STANDING-TRANSITIONS.md` | the prose transition table restated in `docs/STANDING.md` |
| `generated/standing-court.rq` | the absent per-transition falsifier court |

## Authority boundary

Every generated artifact is CONSTRUCT-ceiling. `gates/010_authority_boundary.rq` refuses
manufacture if any transition declares `eco:authorityEffect` other than `NONE`, if any
foundation contract declares an authority ceiling above `CONSTRUCT`, if a transition names a
standing outside the admitted seven, or if an `ALIVE` promotion drops the exact-subject
requirement. This pack carries no runtime actuation authority; consequential DO stays behind
GymAct/BRCE admission, matching `contracts/standing-transitions/st07-authority-non-escalation.json`.

## Verification

`ggen sync run` at ggen 26.8.28 wrote all three outputs, graph hash
`1fa9dda754b0be1d12a97ed9bc2385aaed805201c615770c3e5bf3d9be996a9c`; a second run skipped all
three as `unchanged: content identical` (deterministic replay). The authority gate returns
0 rows and the generated court returns 0 rows against the ontology.
