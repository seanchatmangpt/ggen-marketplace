# ADR-0001: Deterministic Catalog Projection

## Status
Accepted

## Context
A marketplace catalog must accurately index all available packs, their metadata, profiles, and download hashes. Storing a hand-maintained `catalog.json` in git invariably leads to drift, PR merge conflicts, and stale metadata when packs are edited.

## Decision
The marketplace catalog is not a source file. It is a strictly deterministic projection computed on demand by `scripts/marketplace.py catalog`.

## Consequences
- No `catalog.json` is committed to git.
- Determinism is enforced in CI by generating the catalog twice and comparing byte-for-byte (`cmp`).
- Release workflows project the catalog artifact at tagged release boundaries.
