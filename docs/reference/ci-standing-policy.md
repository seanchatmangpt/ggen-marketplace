# CI standing policy

Grounded in a real, same-day 34-repo ecosystem health audit (2026-08-13) across three
reconstitution manifests (`seanchatmangpt/autofde-lab`'s `gym-fleet`/`ecosystem-gap`
manifests plus `seanchatmangpt/ggen-legacy`'s own independent 19-repo program). That audit
found two distinct, real failure classes this policy addresses — not hypothetical concerns.

## The two real failure classes found

**1. CI that never runs on the default branch at all.** 4 repos (`rrgym`, `lifegym`,
`biblegym`, `claudecodegym`) each had a real, currently-passing CI workflow — but every
observed run sat on a working branch (`agent/ggen-ci-boost-v1`). `branch=main` returned zero
runs for all four. The work was real and the fix was real; it simply never crossed into the
branch anyone actually claims as the repository's standing. **This is a merge-discipline gap,
not a CI-authoring gap** — no ontology gate can catch it, since it depends on live run
history against a specific branch, not on how the workflow is declared. Detect it with
`authority/ecosystem-reconstitution/check_head_drift.py` in `autofde-lab` (or an equivalent
live-history check), not a `ggen` gate.

**2. CI declared with no push trigger at all.** A `gha:Workflow` that never lists a push
trigger structurally cannot ever discharge the obligation `gha:EventPush`'s own
`gha:obligationSemantics` names ("the obligation to re-establish the standing of that ref...
comes into existence at the moment of the push") — it can only ever run on PR, manual
dispatch, or schedule, none of which re-establish standing for a push landing on the default
branch. **This is an authoring-time gap, catchable at pack-admission time** — see
`packs/github-actions-pack/gates/030_push_trigger_required.rq`, added in the same pass as
this document.

## The policy

1. **Every repository's primary CI workflow must declare a push trigger, or state explicitly
   why it doesn't.** Enforced by `github-actions-pack`'s gate `030_push_trigger_required.rq`:
   a `gha:Workflow` with neither `gha:trigger gha:EventPush` nor a stated
   `gha:noPushTriggerReason` is refused at `ggen sync` time. Legitimate exemptions (a
   manual-dispatch-only release gate, a `workflow_call` reusable target) are real and allowed
   — they just have to be named, not silently absent.

2. **A green run on a feature branch is not evidence of default-branch standing.** Per this
   session's own standing-law vocabulary, a repo whose only green CI lives on an unmerged
   branch is `PARTIAL_ALIVE` at best, never `ALIVE` — `ALIVE` requires a real, independently
   observed green run against the branch the repository's own `default_branch` field names.
   This is a live-evidence check, not a schema-time one; run it via a drift/history check
   against real `gh api .../actions/runs?branch={default_branch}` results, not asserted from
   a green run's existence alone.

3. **`BUILD_BROKEN` and `UNKNOWN` are not the same finding and must not be conflated.** A
   repository with a real, recent, failing CI run at its current HEAD is `BUILD_BROKEN`. A
   repository with zero CI history on its default branch is `UNKNOWN` — absence of evidence,
   not evidence of failure. The 2026-08-13 audit found both classes present across the 34
   audited repos and kept them separate; any future audit reusing this policy must do the
   same.

## What this policy does not (yet) cover

- **Merge promotion is not automated by this policy.** Nothing here merges a green
  feature-branch CI run into the default branch — per this ecosystem's own standing
  actuation-boundary discipline, that remains a human-directed action, one PR at a time,
  never a policy-triggered automatic merge.
- **Live run-history checking is out of scope for `ggen` gates.** Gate `030` catches the
  authoring defect (no push trigger declared); it cannot and does not check whether a push
  trigger that *is* declared has actually produced a green run recently. That half of the
  policy is enforced by a separate live-history tool (see `check_head_drift.py`'s sibling
  pattern), not by this pack.

## See also

- `packs/github-actions-pack/gates/030_push_trigger_required.rq` — the gate enforcing rule 1.
- `packs/github-actions-pack/qualification/consumer.ttl` — real, passing fixtures proving the
  gate admits legitimate cases (a real push trigger, a stated exemption) without false
  positives.
- `authority/ecosystem-reconstitution/check_head_drift.py` (in `seanchatmangpt/autofde-lab`)
  — the live-history half of rule 2, checking recorded vs. actual default-branch HEAD.
