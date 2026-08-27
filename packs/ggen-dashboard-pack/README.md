# ggen-dashboard-pack

Reusable ontology-backed manufacturing pack for `ggen-ui` and other ggen ecosystem dashboards.

## What it owns

The pack owns semantic dashboard contracts that are stable across concrete React implementations:

- standing vocabulary: `UNKNOWN | PARTIAL_ALIVE | ALIVE | BLOCKED | BUILD_BROKEN | UNSUPPORTED | REFUSED:<code>`;
- evidence-kind separation: observed, admitted, executed, changed, verified, inferred, refused, blocked, unsupported;
- SELECT / CONSTRUCT / DO authority calculus;
- BRCE as the exclusive DO boundary;
- receipt identity, subject identity, replay-node contracts;
- consumer-defined dashboard projections;
- semantic design tokens.

It does **not** own application-specific business ontology, authentication providers, cloud APIs, vendor chart/grid APIs, or direct actuation.

## Consumer

A sibling marketplace checkout can be consumed with:

```toml
[project]
name = "my-dashboard"
version = "0.1.0"

[ontology]
source = "ontology/dashboard.ttl"

[packs]
ggen-dashboard-pack = { path = "../ggen-marketplace/packs/ggen-dashboard-pack" }

[templates]
dir = "templates"
```

Then:

```bash
ggen sync run
```

The pack projects into:

```text
src/generated/dashboard-contract.ts
src/generated/projections.ts
src/generated/semantic-tokens.css
```

Those files are consequences and must not be hand-edited.

## Qualification

`qualification/consumer.ttl` supplies a synthetic real consumer graph. Marketplace qualification loads the pack through the pinned admitted ggen runtime, runs generation twice in an isolated capsule, and requires deterministic convergence.

Pack gates refuse incomplete projections, duplicated semantic identities, and any non-BRCE authority path that claims DO capability.

## Authority boundary

```text
O -> admit O* -> SELECT -> CONSTRUCT intent -> PREFLIGHT -> BRCE -> consequence -> receipt -> replay
```

The UI may inspect, query, select, construct, preflight, display receipts, and request replay. It cannot grant itself authority, bypass BRCE, or promote standing from inspection alone.
