# pm4vitest

vitest-native process-intelligence test library. Mirror of pm4pytest's
architecture for TypeScript: process-bound OCEL tracking, token-based-replay
conformance, causal-pair SLA bounds, and TAP v13 / JUnit XML reporters —
**zero dependencies (vitest peer only)**.

## API

### `Pm4Session`

```ts
import { Pm4Session, assertConformance, assertSla, toTAP13, toJUnitXml } from 'pm4vitest';

const s = new Pm4Session();
s.registerObject('o1', 'Order', { total: 42 });
s.emitEvent('e1', 'order_placed', { objectIds: ['o1'] });
s.emitEvent('e2', 'payment_received', { objectIds: ['o1'], timestamp: someDate, attributes: { amount: 42 } });
s.getTrace(); // ordered activity trace
```

### `assertConformance(sessionOrTrace, validPaths, { minFitness = 1.0 })`

Token-based replay over the Petri-net/FSM valid-path set. Each valid path
becomes a parallel branch in a block-structured net (shared `__start__` place,
one transition per activity, last activity of each path produces the shared
`__end__` place). Replay uses bounded backtracking choosing the firing
sequence that minimizes `(missing, remaining)`; fitness is the standard TBR
formula:

```
fitness = 0.5 * (1 - missing/consumed) + 0.5 * (1 - remaining/produced)
```

`consumed` counts firing consumptions plus missing-token substitutions;
`produced` counts the initial marking plus firings. Throws a vitest
`AssertionError` (chai's, via vitest's re-export) whose diagnostic block names
the exact missing mandatory transitions and remaining/unconsumed tokens, plus
the best-matching valid path (LCS).

`refuteConformance(trace, validPaths)` — illegal-sequence verification:
passes when the trace does NOT perfectly fit the valid-path set; throws when
it conforms.

### `assertSla(sessionOrTrace, startActivity, endActivity, { maxSeconds })`

Causal-pair duration bound: first `startActivity`, first `endActivity` after
it; throws if the pair is broken or the duration exceeds the bound.

### Reporters

`toTAP13(outcomes)` (TAP v13 with YAML diagnostic blocks) and
`toJUnitXml(outcomes, suiteName?)` for CI consumption.

## Prior-art decision (documented per prior-art-first law)

Before hand-rolling the engine, wasm4pm was evaluated as the TBR engine
(`~/wasm4pm/wasm4pm/pkg` — `@wasm4pm/core`, exposing
`check_token_based_replay(eventlog_handle, petri_net_handle, activity_key)`,
plus `token_replay_fitness` and alignment engines). Rejected on two grounds:

1. **Dependency weight**: the WASM binary is 7.3 MB; pm4vitest's contract is
   zero deps except the vitest peer, and embedding the binary would make a
   test-only library heavier than most apps that use it.
2. **API shape**: the WASM surface is registry-handle/XES-shaped. There is no
   export that constructs a net from a *valid-path set* (the pm4vitest
   contract); the nearest path is XES serialization + inductive-miner
   discovery, and a discovered permissive net makes fitness 1.0 for every
   trace — `assertConformance` would vacuously pass. The branch-net over
   valid paths preserves the exact-fitness semantics the assertions need.

`wasm4pm-compat-ts` (`@wasm4pm/compat-ts`) provides Zod binding schemas for
the compat domain types, not a replay engine, so it does not resolve either
point. The fitness formula is retained verbatim as the documented contract;
the engine behind it is the documented local implementation.

## Development

```sh
npm install
npx vitest run   # self-test suite (gate)
npx tsc --noEmit # strict typecheck (gate)
```
