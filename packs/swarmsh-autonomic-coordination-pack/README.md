# swarmsh Autonomic Coordination Pack — v26.8.25

This pack makes swarm coordination an **AccumulatedExecutableKnowledge** asset instead of a handwritten orchestration convention. One semantic model manufactures non-actuating shell, Rust, reference, and qualification projections for `swarmsh` and `swarmsh-v2`.

## Architecture

```text
public ontology + swarmsh projection facts
        |
        v
     SPARQL
        |
        v
       ggen  (CONSTRUCT only)
        |
        +--> shell capability projection
        +--> Rust capability projection
        +--> qualification contract
        +--> reference / release standing
                    |
                    v
          exact-head consumer courts
                    |
                    v
             runtime BRCE (DO)
                    |
                    v
               receipt/replay
```

The generated projections contain **facts, not execution primitives**. They cannot spawn a process, acquire a lease, write coordination state, or invoke a model. Consequential authority remains an explicit runtime concern.

## Generate

From this directory, run the repository-supported ggen generation command against `ggen.toml`. Generation uses `ontology.ttl` plus the SPARQL queries under `queries/` and writes only to the declared `consumer/` projection tree.

A consumer release court should regenerate into an isolated directory and compare the result with its committed generated projection. Any diff is semantic/manufacturing drift and fails the release.

## Qualification contract

v26.8.25 requires all of the following before a consumer may claim `ALIVE`:

1. deterministic regeneration from the admitted pack,
2. exact-head runtime qualification,
3. receipt-bound output integrity and tamper refusal,
4. replay that reconstructs evidence without repeating DO,
5. zero ambient DO authority for generated/model policy surfaces.

Generation itself leaves release standing `UNKNOWN`; only consumer evidence can promote it.

## Extension law

Add a capability to `ontology.ttl`, not separately to shell and Rust. Give it a named authority class, proof surface, outcome, and falsifier. Query/template changes must preserve deterministic ordering. If a new capability needs an executable primitive, implement that irreducible primitive in the runtime and keep this pack as the semantic manufacturer.
