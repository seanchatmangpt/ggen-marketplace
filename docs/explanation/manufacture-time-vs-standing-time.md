# Why manufacture time and standing time are different clocks

Conventional planning assumes `output ∝ human time`: more weeks, more engineers, more changes. A plan drawn that way orders its calendar as discovery → design → implementation → integration → validation.

Ontology-first manufacture has a different production function:

```text
O* → retrieve → compose → generate → verify → A        (A = μ(O))
```

Reuse, composition, and generators mean much of what a conventional plan schedules as "implementation" can be constructed at the start. The marketplace's own order is `REUSE → COMPOSE → EXTEND → INVENT`: novel software is the residual, not the starting assumption.

## Two clocks

| Clock | Measures | Governed by |
|---|---|---|
| **Manufacture time** | time from admitted requirement to a constructed, replayable artifact | generators, packs, ontology, composition |
| **Standing time** | time until the artifact's claims are observed, admitted, authorized, and evidenced | requirements, authority, evidence, external dependencies, consequence |

A calendar that treats the first clock as if it were the second measures the wrong thing. Conversely, a short first clock is not a claim about the second.

## The fence that keeps this honest

Constructed is not alive. The repository's standing law applies in full:

- generated existence is not correctness;
- inspection is not execution;
- a workflow definition is not a successful run;
- historical success at another SHA is not current exact-subject evidence.

So "manufactured on day one" names a `CONSTRUCT` result whose standing is `UNKNOWN` until evidence moves it. The remaining calendar is not idle time after the software is done; it is the work of moving standing, and much of it is typed blockage (`BLOCKED:<reason>`) that only someone with the relevant access, authority, or environment can clear. Nothing on that path may be shortcut by mocking execution into `ALIVE`, and nothing in manufacture grants `DO` authority.

## Compounding, and what would prove it

The compounding claim is that improving a generator, pack, ontology, or court today lowers tomorrow's manufacture time (`T_{n+1} < T_n`) while widening what tomorrow can reach (`R_{n+1} > R_n`). This is a hypothesis about the system, not a property guaranteed by activity. Commit counts measure activity, not reach, and cannot distinguish a compounding generator from a busy one.

The falsifiable form is a series of exact-subject measurements: the same pack source, manufactured through successive toolchain states, with wall-clock recorded. [`manufacture_timing.py`](../reference/manufacture-timing-contract.md) produces that comparison from qualification reports and refuses to pair subjects whose source changed. `R_n` has no comparable instrument yet; do not claim it from timing.

## What this does and does not support

It supports re-drawing an engagement plan as a ledger of standing transitions, each with a typed blocker, instead of a schedule of implementation phases; see [the engagement standing ledger](../reference/engagement-standing-ledger.md).

It does not support claims that external observation, customer outcome, benchmark result, or consequential actuation happened, and it does not make a short manufacture interval a service-level promise. See [Security and authority](security-and-authority.md).
