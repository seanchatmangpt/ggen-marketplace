# ADR-0002: Formal star-toml Configuration Admission Boundary

## Status
Accepted

## Context
Running qualification and installer scripts directly from raw, unparsed TOML configuration creates ambient execution risks and hides malformed parameters until runtime crashes occur.

## Decision
`marketplace.toml` declares marketplace operational law and is treated as raw observation ($O$) until formally admitted through `star-toml` / `scripts/admit-config.sh`. Scripts may execute only upon receiving an admitted JSON witness with `q_config=1`.

## Consequences
- No scripts duplicate release tags, digests, worker counts, or timeouts.
- Raw configuration has zero ambient execution authority.
- Qualification requires `GGEN_MARKETPLACE_ADMITTED_CONFIG` witness file.
