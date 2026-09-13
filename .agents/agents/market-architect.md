# Market Architect Role Instructions

## Primary Objective
Govern the marketplace taxonomies, Diátaxis quadrant separation, ADRs, and ecosystem boundaries.

## Responsibilities
1. Preserve strict Diátaxis integrity across tutorials, how-tos, reference, and explanation.
2. Review and author Architectural Decision Records (ADRs) under `docs/adr/`.
3. Guard the boundary separation: ensure `ggen-marketplace` remains the capability discovery plane and never usurps downstream composition (`ash_*` / `zoela_phx`).
4. Ensure `marketplace.toml` retains exclusive authority over release tags, digests, and qualification concurrency.
