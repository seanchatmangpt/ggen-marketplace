# control-plane-invariants-pack

Reusable manufacturing capital for a multi-agent control plane's own
integrity. `ggen sync run` refuses when a subject-identity receipt doesn't
match what an agent claimed, when a claim has no verdict, when two build
leases collide, when a retry attempt changed nothing from the last one, when
a work-queue item is crowned `ALIVE` with no claim behind it, when a
refuted claim leaves its item still crowned, when a pinned/referenced
commit is declared `ACTUALLY_UNRESOLVABLE` without ever being checked
against the real remote, when a dependency-lock check reports `PASS` while
its own stale-entry count is nonzero, or when a production build/projection
carries an unresolved reference to a component whose declared scope is
dev/test-only.

## What the pack ships

| Piece | File | Role |
|---|---|---|
| Vocabulary | `ontology.ttl` | `ctrl:SubjectReceipt`, `ctrl:ClaimsManifest`/`ctrl:Claim`, `ctrl:BuildLease`, `ctrl:WorkQueueItem`, `ctrl:RetryAttempt`, `ctrl:SubjectResolutionCheck`, `ctrl:DependencyLockCheck`, `ctrl:ScopedComponent`/`ctrl:ProductionReference` |
| Gates | `gates/010..090*.rq` | subject mismatch, claim without verdict, lease collision, unchanged retry, crowned-without-claim, refuted-claim-still-alive, premature-unresolvable-verdict, lock-drift-reported-passing, dev-scope-leak-into-production |
| Generated receipt script | `templates/subject_receipt_sh.tmpl` | renders `scripts/subject-receipt.sh` — every agent's mandatory first action; records a real `ctrl:SubjectReceipt` |
| Generated claims runner | `templates/claims_verify_sh.tmpl` | renders `scripts/claims-verify.sh` — runs every unverdicted claim's `evidenceCommand` for real, records `ctrl:literalEvidence`/`ctrl:verdict` |
| Generated report | `templates/control_report_md.tmpl` | renders `CONTROL_REPORT.md`: work queue + claims + leases |
| Bootstrap copy | `bootstrap/claims-verify-bootstrap.sh` | committed, non-generated claims runner for the first run (see below) |

## Consumer contract

1. Declare the control-plane plan in your own ontology source:
   - `ctrl:WorkQueueItem` individuals (`ctrl:itemId`, `ctrl:project`,
     `ctrl:status`, `ctrl:blockingReason` when blocked).
   - `ctrl:ClaimsManifest` + PLAN `ctrl:Claim` individuals
     (`ctrl:claimId`, `ctrl:claimText`, `ctrl:evidenceCommand`,
     `ctrl:partOf`, `ctrl:forItem` pointing at the `ctrl:WorkQueueItem` the
     claim is about) for anything you intend to crown `ALIVE`.
   - `ctrl:BuildLease` individuals as your control plane acquires/releases
     shared resources (`ctrl:resourceKey` unique per resource;
     `ctrl:released` flipped to `true` on release).
   - `ctrl:RetryAttempt` individuals whenever a `ctrl:WorkQueueItem` is
     re-dispatched (`ctrl:attemptNumber` incrementing, `ctrl:hypothesis`
     stating what changed, `ctrl:changedFromPrevious` honestly `false`
     only when nothing actually did).
   - `ctrl:SubjectResolutionCheck` individuals whenever a pinned/referenced
     commit (or other subject ref) needs resolving: `ctrl:refValue`, the
     real `ctrl:localResult` (`FOUND`, `LOCAL_OBJECT_ABSENT`,
     `SHALLOW_FETCH`, or `UNFETCHED_REF`), and only after an actual remote
     lookup (`git ls-remote`/`git fetch` or equivalent) a real
     `ctrl:remoteResult` (`FOUND` or `REMOTE_OBJECT_ABSENT`) before setting
     `ctrl:finalVerdict` to `ACTUALLY_UNRESOLVABLE` — a local miss alone
     never earns that verdict.
   - `ctrl:DependencyLockCheck` individuals whenever a lockfile is
     cross-checked against what is actually materialized on disk:
     `ctrl:lockedPackageCount`, `ctrl:materializedPackageCount`, the
     computed `ctrl:staleEntryCount` (locked minus materialized), optional
     `ctrl:staleEntryName` literals naming the stale entries, and the real
     `ctrl:reportedVerdict` (`PASS` or `FAIL`) the check actually returned
     to its caller/CI — never a verdict typed independent of the count.
   - `ctrl:ScopedComponent` individuals for every dependency/module whose
     availability is scope-limited (`ctrl:componentName`,
     `ctrl:declaredScope` exactly one of `DEV_ONLY`/`TEST_ONLY`/
     `PRODUCTION`, taken from the real manifest declaration — e.g. a
     mix.exs `only: [:dev, :test]` clause), and `ctrl:ProductionReference`
     individuals for every place a production build/projection actually
     references one (`ctrl:referencedComponent`,
     `ctrl:referencingProjection` naming the file/build target making the
     reference).

2. Wire the pack and a local evidence mini-pack in `ggen.toml`:

   ```toml
   [packs]
   control-plane-invariants-pack = { path = "../../packs/control-plane-invariants-pack" }
   control-plane-evidence        = { path = "evidence", lock = false }  # regenerated every run
   ```

3. Two-phase bootstrap for claims (same reason `ggen-verify-pack` and
   `agent-fleet-isolation-pack` need one: the gates run on every sync,
   including the first one that would generate the claims runner itself):
   - **Phase 1**: for each freshly-authored, unverdicted claim, run the
     committed copy once: `bash packs/control-plane-invariants-pack/bootstrap/claims-verify-bootstrap.sh <claim-id> <evidence-command...>`.
     It runs the command for real and appends a real verdict fact to
     `evidence/ontology.ttl`.
   - **Phase 2**: `ggen sync run` now passes gates/020 and generates the
     real `scripts/claims-verify.sh` (which resolves every unverdicted
     claim's `evidenceCommand` from the live union graph instead of CLI
     args); use that for every subsequent claim.

4. Every dispatched agent runs `scripts/subject-receipt.sh <claimed-subject>`
   as its literal first action, before any other tool call. `<claimed-subject>`
   is whatever the agent was told to work on (an absolute repo path is the
   simplest convention — pick one and stay consistent). The script compares
   the real observed `pwd`/`git rev-parse --show-toplevel` against it and
   records `ctrl:matchesClaimed` — gates/010 refuses sync, and the script
   itself exits nonzero, on a real mismatch. This is the false-findings
   failure mode named in the 2026-09-02 Claude Code insights report's "On
   the Horizon" section, applied to subject identity rather than just cwd.

5. A claim's PLAN half (`claimId`/`claimText`/`evidenceCommand`) and its
   EVIDENCE half (`literalEvidence`/`verdict`) are joined by the shared
   `ctrl:claimId` literal — either on one individual (fine for a
   hand-authored fixture) or split across two (the real pipeline: the plan
   individual authored by the orchestrator, the evidence individual
   appended by `scripts/claims-verify.sh`), the same join pattern
   `agent-fleet-isolation-pack` uses for `fleet:name`/`fleet:agentName`.

6. `ggen sync run` refuses on any subject mismatch, any claim without a
   verdict, any lease collision, any unchanged retry after the first, any
   `ALIVE` item with no backing claim, any `REFUTED` claim whose item is
   still `ALIVE`, any `ctrl:SubjectResolutionCheck` with `finalVerdict`
   `ACTUALLY_UNRESOLVABLE` and no `ctrl:remoteResult` recorded, any
   `ctrl:DependencyLockCheck` reporting `PASS` with `staleEntryCount`
   greater than zero, or any `ctrl:ProductionReference` pointing at a
   `ctrl:ScopedComponent` whose `declaredScope` is `DEV_ONLY`/`TEST_ONLY`.
   Once green, sync renders `CONTROL_REPORT.md` from the admitted plan +
   evidence facts.

## Originating incidents (gates 080, 090)

Both new invariants generalize real defects found in this session's ex4pm
planner experiment (`https://github.com/seanchatmangpt/ex4pm`, worktree
`/Users/sac/ex4pm-worktrees/qualification-domain`):

- **Stale dependency lock (gate 080).** Commit
  `08cc60c519d5fc14b3fc5a54412f90fe6678ff03` ("recover: resolve stashed
  mix.lock conflict, land wasm4pm bindings + local WIP") records resolving
  a leftover `git stash pop` conflict on `mix.lock` that had kept a
  `ranch` lock entry with no corresponding materialized `deps/ranch/`
  directory, until `mix deps.get` was rerun to produce a real,
  resolver-validated lockfile. The drift itself was already caught
  correctly by ex4pm's own strict check — the generalized invariant this
  pack encodes is narrower and more durable: no consumer of this class of
  check may ever report a passing verdict while its own stale-entry count
  is nonzero. Gate 080 guards against the check being weakened, not
  against the drift, which a real materialization check (per gate 080's
  own contract) will keep catching on its own.
- **Dev-scope leak into production (gate 090).** In the same worktree,
  `apps/ex4pm_engine/lib/mix/tasks/ex4pm.engine.gen.adapter.ex` does
  `use Igniter.Mix.Task` unconditionally, while
  `apps/ex4pm_engine/mix.exs` declares
  `{:igniter, "~> 0.8.3", only: [:dev, :test]}` — so a `MIX_ENV=prod`
  compile of that file fails, because the dev/test-only dependency is
  never included in the prod dependency tree at all. Gate 090 generalizes
  this: a production build/projection must never carry an unresolved
  reference to a component whose declared scope is `DEV_ONLY`/`TEST_ONLY`.

## Qualification

`qualification/consumer.ttl` is a synthetic green fixture (subject receipt
matching, one `ALIVE` item backed by a `CONFIRMED` claim, one unrelated
`READY` item needing no claim, disjoint unreleased lease keys plus a
released lease sharing a key with no collision, two retry attempts that
both actually changed something, a `SubjectResolutionCheck` genuinely
`ACTUALLY_UNRESOLVABLE` only because a real remote check also came back
absent, a second one `RESOLVED` after a shallow-fetch local miss was found
on the real remote, a `DependencyLockCheck` honestly reporting `FAIL` on a
real stale `ranch` entry plus a second one reporting `PASS` with zero
stale entries, and a `ProductionReference` that only points at a
`PRODUCTION`-scoped component while the `DEV_ONLY`-scoped `Igniter.Mix.Task`
has no `ProductionReference` pointing at it) — proven `0 rows` against all
9 gates with `rdflib`. A companion deliberately-broken fixture (subject
mismatch, a claim with no verdict, two unreleased leases sharing a key, an
unchanged attempt-2 retry, an `ALIVE` item with no claim, a `REFUTED` claim
whose item is still `ALIVE`, a `SubjectResolutionCheck` declared
`ACTUALLY_UNRESOLVABLE` from a `LOCAL_OBJECT_ABSENT` result with no
`ctrl:remoteResult` ever recorded, a `DependencyLockCheck` reporting `PASS`
with `staleEntryCount` 1, and a `ProductionReference` pointing at the
`DEV_ONLY`-scoped `Igniter.Mix.Task` — the ex4pm regressions this pack now
encodes) was built in a scratch directory (not committed to this pack) and
run against the same gates: each fired exactly the row(s) matching its
named violation, confirmed this session — not an eyeball claim.

```
$ python3 run_gates.py qualification/consumer.ttl gates
gates/010_subject_mismatch.rq: 0 row(s)
gates/020_claim_without_verdict.rq: 0 row(s)
gates/030_lease_collision.rq: 0 row(s)
gates/040_unchanged_retry.rq: 0 row(s)
gates/050_crowned_without_claim.rq: 0 row(s)
gates/060_refuted_claim_still_alive.rq: 0 row(s)
gates/070_premature_unresolvable_verdict.rq: 0 row(s)
gates/080_lock_drift_reported_passing.rq: 0 row(s)
gates/090_dev_scope_leak_into_production.rq: 0 row(s)

$ python3 run_gates.py <broken-fixture>.ttl gates
gates/010_subject_mismatch.rq: 1 row(s)
gates/020_claim_without_verdict.rq: 1 row(s)
gates/030_lease_collision.rq: 1 row(s)
gates/040_unchanged_retry.rq: 1 row(s)
gates/050_crowned_without_claim.rq: 1 row(s)
gates/060_refuted_claim_still_alive.rq: 1 row(s)
gates/070_premature_unresolvable_verdict.rq: 1 row(s)
gates/080_lock_drift_reported_passing.rq: 1 row(s)
gates/090_dev_scope_leak_into_production.rq: 1 row(s)
```
