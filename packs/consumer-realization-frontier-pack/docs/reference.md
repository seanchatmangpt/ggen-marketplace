# Reference

## Axes

| Axis | Seed values | Purpose |
| --- | ---: | --- |
| RealizationSurface | 5 | CLI, library, workflow, pack-install, generated-adapter routes |
| VerifierStrategy | 5 | Contract, replay, differential, e2e, chaos courts |
| DependencyRelief | 5 | Feature gate, compatibility shim, capsule, isolated runtime, pure query |
| ReceiptStrategy | 3 | Source digest, verifier evidence, replay chain |
| ResilienceStrategy | 3 | Retry budget, circuit breaker, rollback plan |

The five-axis structural frontier is 1,125 combinations per independently admitted consumer. `queries/21-consumer-realization-cross-product.rq` adds consumer binding. `queries/24-authority-transition-frontier.rq` exposes SELECT/CONSTRUCT/DO boundaries for admission; it confers no DO authority. Ten ASK gates and five permanent Python courts form the qualification surface.
