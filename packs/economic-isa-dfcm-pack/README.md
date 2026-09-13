# economic-isa-dfcm-pack

Ontology-first manufacturing surface for the canonical economic ISA defined by `seanchatmangpt/ex4pm` PR #45.

## DfCM law

The pack maximizes reuse while preserving distinctions:

`semantic identity != event != plan != authority != economic value`

The ontology is the pack input. `ggen.toml` deterministically projects the assigned registry to `generated/economic_isa.registry.tsv`; downstream language adapters consume that manufactured registry rather than inventing another vocabulary.

The registry preserves four byte states: assigned, unknown (`0x00`), unassigned/reserved, and escape (`0xFF`). Category membership never implies assignment. Escape requires an external extension identifier.

The authority lattice is orthogonal: `OBSERVE -> SELECT -> CONSTRUCT -> DO` is not an implication chain. An economic opcode can be observed, selected, constructed, serialized, or projected without granting DO authority. Runtime engines must independently admit an authority receipt before actuation.

## Manufacture

Run ggen against this directory using `ggen.toml`. Re-running with unchanged `ontology.ttl`, query, and template must reproduce byte-for-byte identical output.

## Change rule

Change the canonical vocabulary upstream first. Then update `ontology.ttl` and regenerate. Never hand-edit generated projections to create a new opcode meaning.
