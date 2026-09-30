# Why CI is path-classified and consolidated

Before consolidation, roughly ninety per-round and per-pack courts were each a separate workflow. A
pull request touching one pack started several runners, each paying runner boot, checkout, Python
setup and dependency installation to run seconds of verification plus a whole-corpus `validate`
that the aggregate CI already ran. Measured locally, every court together costs about a minute and a
half of compute; the dominant cost was the startups, and the queue they created (an admission job
sat queued for minutes behind them).

The claims did not change. Each court's checks moved verbatim into `ci/courts/`, selected by the same
path globs, and executed in one job in parallel. Checks that genuinely need another toolchain,
dependency pin or the network stay dedicated workflows, because sharing an environment with them
would change what they verify.

Three design choices follow from "a cache is an optimization, never a correctness dependency":

- The admission binary is cached because compiling the same pinned crate on every run is pure
  repetition, but a miss rebuilds from source and produces a byte-identical receipt.
- Only `main` writes caches; pull requests read them. A branch cannot poison the state other
  branches restore.
- Path classification can only remove work that provably cannot be affected; unknown change sets and
  the nightly run execute everything, so a missed dependency assumption is caught within a day.

Parallelism is used where it shortens the critical path (`verify`, `qualify` shards and `tests` run
concurrently; the test suite is sharded across CPUs), and avoided where it would only add startups
(courts share one runner).

## See Also

- [CI architecture](../reference/ci-architecture.md)
- [Class closure and consolidation](class-closure-and-consolidation.md)
