# Reference: validation contract

`python3 scripts/marketplace.py validate` is the local repository-admission entry point. It scans the complete corpus and reports the complete observed refusal set rather than stopping at the first defect.

## Repository admission refusals

The validator refuses when, among other contract failures:

- `packs/` is absent or empty;
- a symlink appears under `packs/`;
- `pack.toml` is missing/malformed or lacks `[pack]`;
- a pack name is empty, duplicated, or differs from its directory;
- a version is not SemVer;
- a description is empty;
- a pack has no Turtle/RDF source at its root or under `ontology/`;
- a visible template source has an unsupported extension;
- `gates/`, when present, has an invalid shape/source form;
- a required repository Diátaxis document is absent or empty.

Dotfiles under template/gate directories are treated as scaffolding, not executable source. Refusals use typed `REFUSED:*` outputs and a nonzero exit.

## What success proves

A successful repository validation proves the structural/source/documentation contract actually implemented by the validator for that exact tree. It does **not** prove:

- real ggen manufacture for every pack;
- deterministic replay;
- generated consumer correctness;
- domain negative witnesses;
- Level-5 maturity for every pack;
- external API/cloud behavior;
- consequential DO authority.

Those are separate courts.

## Operational configuration is a separate admission

`marketplace.toml` must be admitted through `scripts/admit-config.sh` before qualification law (ggen runtime identity, timeout/worker bounds, release asset digests) becomes executable.

Repository validation must not silently promote raw `marketplace.toml` values to admitted operational authority.

## Level-5 validation

Level-5 documentation/consumer obligations are layered on top of repository admission. `pack-maturity-pack` can generate a structural Diátaxis court and generic regeneration/receipt courts in a composing consumer. Domain packs remain responsible for their own semantic completeness, negative witnesses, runtime behavior, authority ceiling, and composition/class closure.

The intended documentation refusal namespace is `L5-DOC-001..010`; those refusals block the Level-5 documentation claim without implying unrelated repository/runtime failure.

See [Level-5 maturity contract](level5-maturity-contract.md).

## CI relationship

CI calls the same local commands and adds exact-subject identity, all-pack qualification, source-mutation, vacuity, and other repository courts. CI is orchestration/evidence, not a second competing acceptance implementation.

A workflow definition is not evidence of a successful run; standing requires observed execution against the exact admitted subject.
