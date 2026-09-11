# stale-plan

**Failure class**: plan-staleness

## Name

A plan (implementation plan, admission decision, dispatch instructions) is
authored against repo state at commit SHA `X`. Before the plan is actuated,
the repo moves to SHA `Y` (someone else merges, a concurrent agent commits,
a rebase lands) — the plan's premises (file contents, line numbers, which
branch is canonical) may now be false, but nothing re-checks this before
acting on it.

## Setup

1. Author a plan (or admission record) that embeds an exact base commit,
   e.g. `admitted_target_base: <SHA-X>`.
2. Advance the real repo's `HEAD` past `SHA-X` via an unrelated commit —
   a merge, a second agent's commit, or a manual `git commit` — so the
   plan's base is now an ancestor of `HEAD`, not `HEAD` itself.
3. Attempt to actuate the plan without re-deriving it against the new
   `HEAD` (no re-read of the files it names, no re-check that its line
   numbers/anchors still hold).

## Expected sensor/gate behavior

The plan must be treated as invalidated the moment its base SHA no longer
equals the real current `HEAD` — not silently actuated, and not silently
treated as still-ancestor-compatible without a fresh re-admission. The
correct response is re-admit: re-derive the plan against the real current
state, then re-check it, before any tool call that depends on its stale
premises executes. A plan whose base is merely an ancestor of `HEAD` (not
equal to it) is a weaker, still-real hazard: intervening commits between
base and `HEAD` may have changed exactly the file regions the plan
reasons about, so lineage-descent alone does not certify the plan's
content premises are still true.

## Existing gate citation

- `packs/epistemic-sensor-factory-pack/tools/consumer_court.py` — the
  `LINEAGE` refusal branch runs a real `git merge-base --is-ancestor <base>
  <actual>` check and refuses with `LINEAGE` the instant the actual `HEAD`
  does not descend from the plan's `admitted_target_base`. This fixture's
  scenario is the case that check is specifically built to catch: a plan
  whose base has been superseded.
- `packs/repo-reconciliation-pack/` (see its README's 照合・再認証 —
  "verification/re-authentication" — framing) differentiates observed,
  designed, manufactured, and operational state precisely so that a stale
  premise in one layer is caught as a real diff rather than assumed still
  true; the same discipline this fixture names for a stale plan.

No new gate is invented here; the `LINEAGE` check above already encodes
the ancestor-descent half of this fixture. The stronger claim — that
merely being a descendant does not certify unchanged premises within the
plan's named regions — is documented here as the still-open half no cited
gate currently covers; a future gate would need to re-hash the exact file
regions the plan cites and compare them against the plan's authoring-time
digest, not just check commit-graph ancestry.
