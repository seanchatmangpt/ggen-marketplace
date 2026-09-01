# v26.9.1 Jira Plan — ggen-marketplace

## Charter (Define)

This workstream targets the beam4pm process-model pack lineage: closing the
commercial-parity gap between `beam4pm_pro` and comparable Process Mining/Process
Intelligence products (Celonis, Apromore) while transplanting proven recipes from the
sibling `ex4pm`/`xaas` codebase into `beam4pm-process-model-pack`.

Two branch names named in the task hint the intended shape of this work:

- `feat/beam4pm-transplants-from-ex4pm-xaas` — port recipes already built and proven
  in `ex4pm`/`xaas` (an adjacent, presumably more mature codebase) into the
  marketplace pack, rather than re-deriving them from scratch.
- `feat/beam4pm-pro-p0-capabilities` — close named P0 (highest-priority) gaps in the
  `beam4pm_pro` commercial tier's capability list.

Real git history confirms both branches were merged (PR #403 and PR #404) on
2026-08-31, and a third, related branch (`feat/pro-ocpm-simulation`, merged as PR
#405) shipped OCPM discovery + what-if simulation recipes the same day. Read
together, the charter for this workstream is: **close beam4pm_pro's process-mining
capability gaps against named commercial competitors (OCPM, what-if simulation,
AshAi read tools, per-record doc fan-out), landing each gap-closure as its own
reviewed PR into `main`, with `pack.toml` version bumps and `gaps/0` functions naming
remaining scope honestly rather than overclaiming completeness.**

Scope for v26.9.1 as measured below: the three PRs above are **already merged**. This
plan's job is to (a) record the real state so nothing is re-done, (b) surface what
real work remains unmerged elsewhere in the repo that a v26.9.1 cut should evaluate,
and (c) set the gates for the next capability tranche in this same lineage.

## Measure

Real state captured via `git clone` of
`https://github.com/seanchatmangpt/ggen-marketplace.git` and `git log`/`git branch -a`
against every ref, not assumed from branch names alone.

### The two named branches — both already merged into `main`

**`feat/beam4pm-transplants-from-ex4pm-xaas`**
- Latest SHA: `39b027b989535d41ebdfeff03c350bb3f747149b`
- Latest date: 2026-08-31 17:07:29 -0700
- Latest message: `feat(beam4pm-process-model-pack): AshAi read tools + per-record-type
  doc fan-out (transplanted from ex4pm/xaas)`
- Diff vs. `main`: 0 commits ahead (merged via PR #404, merge commit `880b6621`)

**`feat/beam4pm-pro-p0-capabilities`**
- Latest SHA: `d8a7bce4bbf532199808b097167468e4f3c17b9f`
- Latest date: 2026-08-31 15:30:58 -0700
- Latest message: `feat(beam4pm-process-model-pack): five beam4pm_pro P0 gap-closure
  capabilities`
- Diff vs. `main`: 0 commits ahead (merged via PR #403, merge commit `674fc91e`)

### A third, directly related branch also merged the same day

**`feat/pro-ocpm-simulation`**
- Latest SHA: `e2cde86e0071abd6844f52aa81b6be145efaa8ab`
- Latest date: 2026-08-31 21:38:04 -0700
- Latest message: `docs(beam4pm-process-model-pack): name Triplex as
  deliberately-not-adopted in Pro.Tenancy (0.1.5)`
- Diff vs. `main`: 0 commits ahead (merged via PR #405, merge commit `20a8732b`)

### `main`'s tip reflects all three merges, in commit order

```
20a8732b  feat: OCPM discovery + what-if simulation recipes (PRO-011/012) (#405)
880b6621  Merge PR #404 from feat/beam4pm-transplants-from-ex4pm-xaas
39b027b9  feat(beam4pm-process-model-pack): AshAi read tools + doc fan-out
674fc91e  Merge PR #403 from feat/beam4pm-pro-p0-capabilities
d8a7bce4  feat(beam4pm-process-model-pack): five beam4pm_pro P0 gap-closure capabilities
5770db92  Merge pull request #402 from seanchatmangpt/fix/cloudrun-google-provider-v8
```

### Repo-wide branch census (as of this clone)

`git branch -a` lists **170+ remote branches**. Filtering to branches with commits
strictly newer than `main`'s merge base (i.e., not yet merged) surfaces roughly 150
unmerged branches spanning many independent lineages — `cell1`–`cell5` (TPS/Heijunka
closure-capital work), `develop/*`, `measure/*`, `explore/*`, `implement/*` (DMEDI-
named portfolio-selection and capital-realization work from 2026-08-24 through
2026-08-27), plus one-off `feat/*` and `fix/*` branches. These are **not part of the
beam4pm-process-model-pack lineage** this plan's charter covers and are out of scope
for v26.9.1's beam4pm gate — they are flagged here only because a full portfolio-level
sweep (the user's separate control plane) would need to triage them independently.

The only branch genuinely within 24h of this plan's baseline (2026-08-31) that is
**not** part of the merged trio is `feat/pro-ocpm-simulation` itself, and it is
already merged (see table above) — so real Measure-phase evidence shows **zero
unmerged work remaining in the named beam4pm transplant/P0 lineage** as of this
clone.

## Explore

Branch names and merged content imply the following competing/complementary
approaches already explored within this lineage, plus options for the next tranche:

1. **Transplant vs. re-derive.** `feat/beam4pm-transplants-from-ex4pm-xaas` chose to
   port working code from `ex4pm`/`xaas` rather than reimplement AshAi read tools and
   per-record-type doc fan-out from a blank slate. This is the lower-risk, faster
   option when a working reference implementation already exists in a sibling repo —
   already executed and merged.
2. **P0 gap-closure batch vs. one-at-a-time PRs.** `feat/beam4pm-pro-p0-capabilities`
   landed five P0 capabilities in a single PR (`d8a7bce4`) rather than five separate
   PRs. This traded review granularity for landing velocity — already executed and
   merged; the tradeoff is worth naming for the next tranche's decision (see Develop).
3. **OCPM/simulation as its own PR vs. folded into the P0 batch.**
   `feat/pro-ocpm-simulation` (PRO-011/012) was kept as a separate, later PR (#405)
   rather than folded into the five-capability P0 batch (#403). This is the
   `errc-cycle`-shaped choice of treating each competitor-parity gap as an
   independently reviewable "Create" item rather than batching all gap-closures
   together — the pattern this plan recommends continuing for the next tranche.
4. **Next-tranche candidates named by the merged commits' own `gaps/0` functions.**
   The `e861e2dc` commit's own gap declaration says it deliberately does **not**
   include object-centric Petri net synthesis or discrete-event/throughput
   simulation. These are real, named, unaddressed gaps — not guesses — and are the
   most concrete "what's next" candidates this plan can point to without inventing
   new scope.
5. **Portfolio-level alternative not yet merged.** The 150+ unmerged branches outside
   this lineage (cell1-cell5, develop/measure/explore/implement DMEDI branches)
   represent an entirely separate exploration track (capital-realization/portfolio-
   selection research) running concurrently. Whether any of those branches should be
   promoted alongside this beam4pm tranche in the same v26.9.1 cut is a portfolio-
   level decision out of this plan's scope (see Charter) — named here so it is not
   silently dropped.

## Develop

Concrete next engineering steps, scoped to the beam4pm-process-model-pack lineage
this plan actually covers:

1. **Confirm merged state stays green.** Since all three source branches are already
   merged, the first concrete step is not new feature code — it is running the
   existing verification gate (`marketplace.py validate`, referenced in commit
   `20a8732b`'s message as passing "207 packs, 1528 templates") against current
   `main` to confirm no regression was introduced by the three-way merge sequence
   (`674fc91e` → `880b6621` → `20a8732b`).
2. **Object-centric Petri net synthesis (named gap from `e861e2dc`).** Implement as a
   new EEx recipe template (`beam4pm_pro_ocpn_synthesis{,_test}.ex.eex`) following the
   same pattern as `beam4pm_pro_ocpm_discovery.ex.eex` — operate on runtime OCEL data
   passed by the caller, name any remaining scope gaps via `gaps/0`, bump `pack.toml`
   patch version, and land as its own PR (continuing pattern #3 from Explore).
3. **Discrete-event/throughput simulation (named gap from `e861e2dc`).** Implement as
   a new recipe (`beam4pm_pro_throughput_simulation{,_test}.ex.eex`) extending
   `beam4pm_pro_simulation.ex.eex`'s BFS/DFS primitives with time-stepped event
   processing; same PR-per-gap discipline.
4. **Delete or archive fully-merged branches.** `feat/beam4pm-transplants-from-
   ex4pm-xaas`, `feat/beam4pm-pro-p0-capabilities`, and `feat/pro-ocpm-simulation`
   are 0 commits ahead of `main` and can be deleted from `origin` without losing any
   commit (all reachable from `main`) — a housekeeping step, not a code change,
   recommended before the next tranche starts so branch listings stay legible.
5. **Portfolio triage (deferred).** The 150+ unmerged non-beam4pm branches are not
   actioned by this plan; flag them to the portfolio-level control plane per this
   repo's own `~/.claude/rules/local-dfcm-manufacturing-engine.md` division of labor
   (Claude = local research/manufacturing; portfolio system = cross-repo
   orchestration) rather than triaging them here.

## Implement

### Merge order

The three source branches for this tranche are already merged in the correct
dependency order (verified by the real commit graph on `main`):

1. `feat/beam4pm-pro-p0-capabilities` → PR #403 → merge `674fc91e`
2. `feat/beam4pm-transplants-from-ex4pm-xaas` → PR #404 → merge `880b6621`
3. `feat/pro-ocpm-simulation` → PR #405 → merge `20a8732b`

For the next tranche (Develop steps 2-3 above), the same order discipline applies:
land the object-centric Petri net synthesis recipe and the throughput simulation
recipe as **two separate PRs**, each gated independently, rather than one combined
PR — following the pattern Explore item #3 already validated as this lineage's
working convention.

### Verification / test gates

- `marketplace.py validate` must report the same or higher pack/template counts
  post-merge as pre-merge (baseline from `20a8732b`: 207 packs, 1528 templates) —
  regression in either count blocks merge.
- Each new `.ex.eex` recipe must ship with its paired `_test.ex.eex` in the same
  commit (the convention every commit in this lineage already follows).
- Each new recipe must expose a `gaps/0` function naming what it deliberately does
  not cover, per this repo's `no-overclaiming` discipline — a recipe without a
  `gaps/0` function is not mergeable under this lineage's own established pattern.
- `pack.toml` version bump is required per merged capability addition (pattern:
  0.1.3 → 0.1.4 → 0.1.5 already observed across the three merged commits).

### Rollout / monitoring

- No rollout beyond `git merge` to `main` is required — this is a template/recipe
  pack, not a deployed service; "rollout" means the recipe becomes available to any
  consumer running `ggen sync` against a manifest that references
  `beam4pm-process-model-pack`.
- Monitoring: re-run `marketplace.py validate` on a recurring cadence (this repo
  already has CI workflows under `.github/workflows/` for this purpose) to catch any
  future regression introduced by unrelated concurrent branches merging into `main`.
- Branch hygiene: delete the three merged branches (`feat/beam4pm-transplants-from-
  ex4pm-xaas`, `feat/beam4pm-pro-p0-capabilities`, `feat/pro-ocpm-simulation`) from
  `origin` once this plan is reviewed, to keep `git branch -a` output legible for the
  next contributor doing this same Measure-phase exercise.

---

Last Updated: 2026-09-01
