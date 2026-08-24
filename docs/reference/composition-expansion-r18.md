# Composition Expansion R18 Reference

R18 turns admitted R17 opportunity portfolios into reversible composition candidates. It is a SELECT/CONSTRUCT surface only: no query or ontology fact grants DO authority.

## Candidate families

- **PairCandidate**: two compatible reversible portfolio members.
- **TriadCandidate**: three distinct reversible members connected by compatible edges.
- **BridgeCandidate**: a member exposing a `missingPrimitive` paired with another member exposing that primitive as `sharedCapability`.
- **Capability-space frontier**: reversible candidates without an explicit `dominatedBy` edge, ordered by expected capability-space and reuse deltas.

## Required evidence

Candidate standing is meaningful only when source portfolio identity, reversibility, expected deltas, qualification surface, and authority are explicit. Absence of an edge is UNKNOWN, not incompatibility. A failed composition edge removes only that edge; it does not refute adjacent candidates.

## Authority boundary

R18 queries manufacture candidate descriptions. They must not actuate external systems. Consequential execution remains behind BRCE admission and receipt/replay.

## Falsifiers

A candidate is not admitted when it depends on a non-reversible member, carries an explicit `dominatedBy` edge for frontier membership, or requires an unavailable primitive without a bridge candidate. Exact consumer execution remains required before SUBJECT_ALIVE standing.
