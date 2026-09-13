# ADR-0003: Ecosystem Topology and Composition Boundary

## Status
Accepted

## Context
As the `ggen` and `ash_*` ecosystem expanded to power applications like `ZOELA`, boundaries between reusable capability discovery, reusable machinery, and application composition roots became prone to leakage and circular dependencies.

## Decision
Establish the immutable unidirectional ecosystem topology:
$$\text{ggen-marketplace} \longrightarrow \text{ash\_*} \longrightarrow \text{ZOELA} \longrightarrow \text{ZOE Marketplace / Clients}$$

- `ggen-marketplace` owns reusable pack source and marketplace discovery.
- `ash_*` owns reusable Ash/Elixir machinery and **must not** depend on `ZOELA`.
- `ZOELA` (`zoela_phx`) is the admitted application composition root.
- Consumers and client applications (e.g. Expo) are downstream projections.

## Consequences
- No application composition code belongs in `ggen-marketplace`.
- Pack sources remain portable across any ggen-compliant consumer.
- Invariants are verified at the boundaries between layers.
