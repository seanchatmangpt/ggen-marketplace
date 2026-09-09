# regression-fixtures-pack

A **documented regression corpus** of 9 historical Claude-orchestration
failure classes -- an ontology plus fixture specifications, not an execution
gym. `ggen sync run` refuses on structural problems in the corpus itself
(a fixture missing required fields, two fixtures sharing a name, a loosely
worded refusal code, a fabricated gate citation, or a stale member count) --
it never attempts to execute or reproduce the underlying failures.

## Scope: what this pack actually is (and is not)

This pack is a **corpus**, not a **gym**. Concretely:

- Each `fixtures/*.md` file is a plain-text specification: a name, a setup
  (how to construct the exact broken state), the expected sensor/gate
  verdict, and -- where a real corresponding gate already exists elsewhere
  in this marketplace -- a citation to it by file path.
- These files are read by a human or an agent, not executed by this pack.
  Nothing here spins up a sandbox, dispatches a real agent into a
  deliberately broken repo, or checks that the expected refusal actually
  fires against a live reproduction.
- No generic execution gym (a harness that takes a fixture spec, constructs
  the broken state for real, dispatches an agent or a sensor against it, and
  checks the real observed verdict against the expected one) exists
  anywhere in this marketplace as of authoring time. This was checked
  against the current pack census (`packs/*/` listing at authoring time) --
  no pack named `*-gym-*` or otherwise scoped to generically executing a
  fixture spec was found. `packs/gdmcp-pack`, `packs/ww3gym-planning-pack`,
  `packs/wasm4pm-sandbox-pack`, and `packs/chatgptgym-gymact-bridge-pack` are
  the closest-named neighbors and were checked; none is a generic
  fixture-execution runtime for this corpus's shape (they are scoped to
  their own domains: MCP/game-theory planning, WASM sandboxing, and a
  ChatGPTGym/GymAct consumer bridge whose DO surface is bounded to
  simulation/reset intents behind its own admission chain, not a generic
  regression-fixture runner).
- The 5 gates this pack ships (`gates/010`..`050`) validate the **RDF
  registration** of a fixture corpus (are the required fields present, are
  names unique, is a refusal code well-formed, does a citation look like a
  real path, does a declared count match the real asserted count) -- they
  do not and cannot validate that the underlying historical failure was
  actually, mechanically reproduced. That would be QUALIFICATION-phase work
  for a future execution gym, not something a static RDF corpus can do on
  its own.

### What a future generic execution gym would need

To actually *run* these fixtures (not just document them), a future pack
would need, at minimum:

1. A **setup materializer** per failure class: real code that constructs the
   exact broken state described in each fixture's Setup section (spins up
   git worktrees for `wrong-subject`, advances a repo past a recorded base
   SHA for `stale-plan`, declares colliding `fleet:BuildCacheDir` paths and
   dispatches two real subprocesses for `build-collision`, etc.) -- not
   generic across classes, since the broken states themselves are not
   generic.
2. A **verdict harness** that runs the real, already-cited gate (where one
   exists) or a new one (where this corpus names a gap) against the
   materialized state and captures its real, literal output.
3. A **comparator** that checks the harness's real output against each
   fixture's `rfx:expectedBehavior` string (or a more structured successor
   to that free-text field) and reports PASS/FAIL per fixture, plus an
   aggregate corpus-level report.
4. For the 3 fixtures this corpus names as currently gate-less
   (`unbounded-loop`, `unchanged-retry`, and the live-process-dependency
   half of `destructive-dependency`) -- the actual missing gates
   themselves, built and qualified independently before a gym could
   exercise them.

None of the above exists yet. Building it is out of scope for this pack;
this pack's job is to make the corpus real and precisely specified so that
work is buildable later without re-deriving the failure taxonomy from
scratch.

## What the pack ships

| Piece | File | Role |
|---|---|---|
| Vocabulary | `ontology.ttl` | `rfx:RegressionFixture` (one documented failure class), `rfx:FixtureCorpus` (the named collection) |
| Gates | `gates/010..050*.rq` | required fields, duplicate names, malformed refusal codes, fabricated gate citations, corpus member-count drift |
| Fixture specs | `fixtures/*.md` | the 9 documented failure classes, plain text, not executed |
| Qualification (green) | `qualification/consumer.ttl` | the real 9-member corpus registered as `rfx:RegressionFixture` individuals -- proven `0 rows` against all 5 gates with `rdflib` 7.6.0 |
| Qualification (broken) | `qualification/broken.ttl` | deliberately-broken fixture proving each gate fires exactly the row matching its named violation -- confirmed this session, not an eyeball claim |

## The 9 fixtures

| Fixture | Failure class | Real corresponding gate cited? |
|---|---|---|
| `wrong-subject.md` | subject-identity | Yes -- `agent-fleet-isolation-pack`, `evidence-capital-admission-pack`, `epistemic-sensor-factory-pack` |
| `stale-plan.md` | plan-staleness | Partially -- `epistemic-sensor-factory-pack`'s `LINEAGE` check covers ancestor-descent; content-region re-hashing does not exist yet |
| `build-collision.md` | resource-contention | Yes -- `agent-fleet-isolation-pack/gates/020_buildcache_collision.rq` |
| `false-claim.md` | false-claim | Yes, for the tamper-replay shape -- `evidence-capital-*` family, `challenger-value-framing-pack` |
| `unbounded-loop.md` | unbounded-directive | No -- named as a real, documented gap |
| `unchanged-retry.md` | retry-without-hypothesis | No -- named as a real, documented gap |
| `destructive-dependency.md` | destructive-deletion | Partially -- `repo-load-path-pack/gates/040_spof_is_blocking.rq` covers the general shape; live-process/binary dependency specifically does not exist yet |
| `placeholder-evidence.md` | placeholder-evidence | Yes -- `runtime-evidence-authenticity-pack/gates/02_evidence_origin.rq`, `03_dynamic_source.rq` |
| `dirty-diverged-repo.md` | ground-truth-override | Real, cited incident (`~/.claude/big-loop/tracker.md` Cycle 12); no standing gate re-runs the ancestor check live over time -- named as a real, documented gap |

No fixture invents a gate that does not exist. Where no real gate exists,
the fixture says so plainly and names what a future gate would need.

## Consumer contract

1. Wire the pack in `ggen.toml`:

   ```toml
   [packs]
   regression-fixtures-pack = { path = "../../packs/regression-fixtures-pack" }
   ```

2. Register your own `rfx:RegressionFixture` individuals in your own
   ontology source (or extend this pack's `fixtures/` and
   `qualification/consumer.ttl` directly), following the shape in
   `qualification/consumer.ttl`.

3. `ggen sync run` refuses on any missing required field, duplicate name,
   malformed refusal code, fabricated citation shape, or corpus
   member-count drift.

## Qualification

`qualification/consumer.ttl` registers the real 9-fixture corpus this pack
ships and is proven `0 rows` against all 5 gates with `rdflib` 7.6.0.
`qualification/broken.ttl` is a deliberately-broken companion fixture
(missing setup, a duplicate name, a loose refusal code, a fabricated
citation, and a wrong member count) run against the same 5 gates this
session -- each gate fired exactly the row matching its named violation:

```
gates/010_required_fields.rq -> 1 row (missing-setup, "setup")
gates/020_duplicate_name.rq -> 1 row (duplicate-name, b-dup-a, b-dup-b)
gates/030_malformed_refusal_code.rq -> 1 row (loose-refusal)
gates/040_uncited_gate_shape.rq -> 1 row (fake-citation, "some/made/up/path.rq")
gates/050_corpus_count_drift.rq -> 1 row (b-corpus, declared=2, actual=5)
```

One real bug was caught and fixed during this qualification run:
`gates/020_duplicate_name.rq`'s original `FILTER(?fixtureA < ?fixtureB)`
compared two `URIRef` terms directly, which `rdflib` 7.6.0's SPARQL engine
silently excludes from `<` ordering (0 rows even against a real duplicate
pair) -- fixed to `FILTER(STR(?fixtureA) < STR(?fixtureB))`, re-verified
firing correctly. This is exactly the kind of thing this pack's own
`dirty-diverged-repo.md` fixture and this account's verification-discipline
rules exist to catch: a gate's own claimed behavior is only as trustworthy
as the last time it was actually re-run against a real violation, not the
last time someone eyeballed its SPARQL text.

## See also

- `packs/agent-fleet-isolation-pack/` -- the fleet-plan-level isolation
  gates this corpus's `wrong-subject.md` and `build-collision.md` fixtures
  cite directly.
- `packs/evidence-capital-admission-pack/`, `packs/runtime-evidence-authenticity-pack/`,
  `packs/evidence-capital-realization-pack/` -- the evidence-authenticity
  and tamper-replay families this corpus's `placeholder-evidence.md` and
  `false-claim.md` fixtures cite directly.
- `packs/epistemic-sensor-factory-pack/tools/consumer_court.py` -- the real,
  executable subject-identity/lineage sensor cited by three fixtures here.
