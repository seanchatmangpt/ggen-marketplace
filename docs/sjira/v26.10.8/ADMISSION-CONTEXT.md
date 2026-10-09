# ADMISSION-CONTEXT

Resolution context for backlog item [43]: two `castle-goal` refusal rows in
`docs/sjira/v26.10.8/ADMISSION-LEDGER.jsonl` reference a repo path that does
not exist on disk. Evidence-first; ledger untouched (append-only). Written
2026-10-08.

## The rows

`ADMISSION-LEDGER.jsonl` lines 36 and 75 (round 1 and round 2 retry):

```json
{"admitted": false, "detail": "no docs/sjira/v26.10.8*/WORKGRAPH.ttl under /Users/sac/castle-goal", "order": null, "refusal_reason": "no_workgraph", "repo": "castle-goal", "ts": "2026-10-08T22:10:39.463077+00:00"}
{"admitted": false, "order": null, "refusal_reason": "no_workgraph: no docs/sjira/v26.10.8*/WORKGRAPH.ttl and no /Users/sac/castle-goal checkout on disk", "repo": "castle-goal", "round": 2, "ts": "2026-10-08T22:22:51.791104+00:00"}
```

## Investigation (all commands real, this session)

1. `/Users/sac/castle-goal` does not exist. `/Users/sac/castle` does.
   - `ls /Users/sac/castle-goal` → `No such file or directory`
   - `ls -d /Users/sac/castle` → exists; git status `## main...origin/main`
     (in sync), HEAD `6692936f6ea8257d814995437f2b5c9cb54ff128`.
2. Remote: `git -C /Users/sac/castle remote -v` →
   `https://github.com/seanchatmangpt/castle` (fetch/push).
3. No repo named `castle-goal` anywhere in fleet config: `grep -rn
   "castle-goal" /Users/sac/ggen-ecosystem` → 0 hits across `ecosystem.ttl`,
   `ecosystem.lock.toml`, all ontology/profiles trees.
4. The only source of the string `castle-goal` in the fleet is the admitter
   driver itself: `/Users/sac/ggen-marketplace/scripts/admit_workgraphs.py`
   line 40 (`REPOS = [..., "castle-goal", ...]`).
5. Castle's v26.10.8 sJira surface is `docs/sjira/v26.10.8/goal.ttl` — a
   GoalCheckpoint graph. Its header law (goal.ttl lines 21-26) states:
   "This file contains no authored sj:WorkOrder and no authored sj:Receipt.
   WorkOrders are compiler projections; receipts are observations."
6. `find /Users/sac/castle/docs -name "WORKGRAPH.ttl"` → 0 files. Castle has
   no WORKGRAPH.ttl at any revision of docs/ on disk.

## Finding

`castle-goal` is a stale entry in the admitter driver's `REPOS` list
(`scripts/admit_workgraphs.py:40`). There is no repository of that name. The
real repo is `castle` (`seanchatmangpt/castle`, checkout `/Users/sac/castle`).

Re-pathing does NOT unlock admission, because even at the correct path the
refusal is substantively correct, for two independent reasons:

1. The driver's glob (`scripts/admit_workgraphs.py:205`) matches only
   `docs/sjira/v26.10.8*/WORKGRAPH.ttl`. Castle carries
   `docs/sjira/v26.10.8/goal.ttl` (GoalCheckpoint goal graph), not a
   WORKGRAPH.ttl.
2. Even if the glob were extended, castle's goal graph carries **zero
   authored sj:WorkOrder by law** (goal.ttl lines 21-26). There is nothing
   for the admission kernel to admit; a re-run would correctly refuse with
   `zero_work_orders` — same BLOCKED standing, correct reason.

## Resolution: typed retirement (not re-path)

The two `castle-goal` rows retire with typed retirement rationale; they are
not re-pathed to castle. Rationale (each part load-bearing):

1. Referent failure: the subject repo `castle-goal` does not exist; the rows
   were produced by a driver misconfiguration, not by an order. There is no
   admitted order to preserve.
2. Substantive failure: re-pathing to castle cannot succeed because castle
   v26.10.8 has zero authored WorkOrders by its own graph law (goal.ttl
   lines 21-26).

## Corrected rows for a future re-admission run

None. A future run should correct the driver (replace `castle-goal` with
`castle` in `scripts/admit_workgraphs.py:40` — driver fix, not ledger fix)
and drop castle from the fleet-admission scope entirely, or the driver will
re-mint the same refusal rows forever. The correct handling of castle's
v26.10.8 surface is the GoalCheckpoint shape path (marketplace precedent
commit `5f2bb8b35` "feat(shapes): GoalCheckpoint doc-graph shape (castle
precedent)"), not the WorkOrder admission driver.

GoalCheckpoint validation for castle's goal.ttl already exists and passed:
`/Users/sac/castle/docs/sjira/v26.10.8/GOAL-SHACL-VALIDATION.md`.

## Standing

- Two `castle-goal` ledger rows: **RETIRED** (typed: referent failure in
  driver config; no order subject exists, and the intended subject repo
  carries zero authored WorkOrders by graph law).
- The ledger rows themselves are untouched (append-only law). Retirement is
  recorded here, not by editing ADMISSION-LEDGER.jsonl.

## Falsifier

- A `castle-goal` repository appears on disk or in a fleet manifest → this
  document is stale, re-open.
- Castle grows an authored sj:WorkOrder under `docs/sjira/v26.10.8*` →
  re-admission via the corrected driver becomes meaningful, re-open.
- The GoalCheckpoint shape path (marketplace `5f2bb8b35`) is retired before
  this retirement stands → re-open.
