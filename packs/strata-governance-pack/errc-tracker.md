# errc-tracker.md — strata-governance-pack X5/T11 construction lane

ERRC pass over the X5 candidate 1 construction (2026-10-13 session).

## Eliminate

- **No wall-clock, no RNG** anywhere in ontology, gates, or generated
  module — the diff is a pure function of the graph.
- **No cross-pack require.** `requires = []` with the FM-PACK-018
  documentation-only note; the seal relationship to strata-chain-pack is
  carried in ontology comments, never a dependency edge.
- **No second catalog.** The diff table is DERIVED by
  `queries/governance_report.rq`; no hand-maintained constant list exists
  outside ontology.ttl.

## Reduce

- **One ontology, one rule, one artifact**: 13 sealed constants x 13
  projections reduce to 13 diff rows; the law reduces to string equality
  over the sealed/projected lexical forms plus bidirectional coverage.
- **Gate 020 reuses the family V7 pattern** (presence + malformed arms)
  instead of a new gate shape.

## Raise

- **Fail-closed both directions**: 010 refuses drift, unprojected seals,
  AND uncommitted projections — an out-of-constitution constant cannot
  enter silently and a sealed constant cannot vanish from projection.
- **Tamper-evident seals**: each `SealedConstant` carries
  `st:sealedDigest = SHA-256("NAME=value")`; the generated module
  re-derives every digest with its own zero-crate FIPS 180-4 SHA-256
  (`seal_digests_rederive`), so an ontology edit to a sealed value breaks
  the build test as well as the gate.
- **Falsifier is executable twice**: once in SPARQL (gate 010 over the
  mutated graph — rdflib mutation witness), once in Rust
  (`out_of_constitution_edit_refused` unit test). Both cite the
  commitment by name.

## Create

- **`GovernanceCommitment` / `SealedConstant` / `ProjectedConstant` /
  `ConstantDiff` classes** — the constitutional-diff vocabulary, new in
  the strata family (X5 candidate 1).
- **`verify_constitution()`** — the law as a typed Rust function returning
  `Result<(), ConstitutionalDrift>` with the commitment named in the error.
