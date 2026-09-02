# Fortune-5 Required Capabilities Pack

This pack manufactures an independent verifier for the bounded repository-defined Fortune-5 contract.

## Contract

- **6 release truths:** install, compiler, conflict, rendering, trust, proof
- **2 supporting systems:** atomic pack taxonomy, bundle/profile system
- **5 performance governors:** CLI startup, rendering, RDF query, memory, concurrency
- **6 operational controls:** Andon, Poka-Yoke, tracing, chaos resilience, golden signals, error budgets
- **3 proof surfaces each:** positive execution, negative refusal, receipt/replay

The crown is therefore **19 capabilities × 3 surfaces = 57 obligations**.

## Execute

```bash
ggen sync run
cargo test --manifest-path consumer/fortune5-required-foundation/Cargo.toml
bash consumer/fortune5-required-foundation/scripts/verify.sh
```

`RELEASE_STANDING.json` intentionally remains `UNKNOWN`. Only the executed verifier may emit `ALIVE`.

## Portability (GM-02)

This pack is self-contained and generates two crates, not one:

- `consumer/fortune5-required-foundation/` -- the verifier crate (`fortune5-required-foundation`).
- `consumer/ggen-fortune5-capabilities/` -- a vendored, standalone crate
  (`ggen-fortune5-capabilities`) carrying `Fortune5Assessment`,
  `Fortune5Reference`, `Fortune5Standing`, `ALL_FORTUNE5_CAPABILITIES`, and
  `REQUIRED_PROOF_SURFACES`, generated from `templates/vendor/`. It has no
  dependency on `ggen-marketplace` or any path inside that repo's tree.

The verifier's one Cargo dependency (on `ggen-fortune5-capabilities`) is
admitted as ontology data, not a literal template path: see the
`f5:cargo-dependency` individual in `ontology.ttl` and
`queries/dependency.rq`. `f5:dependencyPath` is a path relative to the
generated verifier crate's own directory; it defaults to
`../ggen-fortune5-capabilities` (the sibling crate this same pack also
generates). To vendor the crate elsewhere, or to depend on a published
crates.io/git version instead, edit `f5:dependencyPath` (and, for a
registry/git dependency, `f5:dependencyCrateName` plus the Cargo.toml.tmpl
line shape) in `ontology.ttl`, then re-run `ggen sync run`.

Both crates generate under whatever project runs `ggen sync run` against
this pack -- there is no assumption that the consumer is `ggen-marketplace`
itself, or that a `crates/ggen-marketplace` directory exists anywhere on
disk.
