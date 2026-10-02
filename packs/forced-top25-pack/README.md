# forced-top25-pack

Canonical ForcedTop25 capability ecology. **One pack, one version, one admission
unit, nine family modules** - consolidated (2026-09-30, v26.9.30 wave) from nine
`forced-top25-*` packs that were a lane-partition artifact of earlier fan-out
runs, not a durable topology. Drift law applied: "N implementations of one
calculus -> O(N^2) drift; converge on one kernel with N bindings."

## Head-SHA reconciliation policy (the core semantic decision)

The three pre-merge copies of the same mutable 25-target population carried
**conflicting head SHAs for the same repos**:

| copy | source pack | head property | evidence timestamp basis |
|---|---|---|---|
| A | `forced-top25-admissibility-pack/targets/` | `fta:exactCurrentHead` | per-target-file git commit |
| B | `forced-top25-standard-consumer-factory-pack/forced-top25.ttl` | `fta:exactHead` | single-file git commit |
| C | `forced-top25-ocel-fanout-meta-pack` (`targets/`, `closure-demands/`, `replay-demands/`, ontology t01-t25) | none asserted | n/a |

Rule: **for each of the 25 repos, the copy with the NEWEST per-repo evidence
timestamp wins as `targets/population.ttl` truth.** Outcome: copy B (evidence
2026-08-26T00:51:59-07:00) won the 3 repos where it asserted a real SHA
(`ex4pm`, `gymact`, `xaas` - each a REAL_SHA_CONFLICT against copy A's older
heads); copy A won the other 22 (copy B asserted only `UNKNOWN` there, and
`UNKNOWN` carries no head evidence). Copy C asserted no head SHAs, never
competed, and is frozen verbatim under `runs/r90/` with its exact state.

Every divergence is conserved in `ontology/reconciliation.ttl` (repo, losing
SHA, losing source pack, losing/winner evidence timestamps, winner SHA,
conflict class) - nothing silently dropped. Run snapshots r75/r86/r90 are
replay evidence under `runs/<rXX>/`; their exact heads stay frozen as they
were and never compete for population truth.

The two conservation riders merged into the population: the
`fts:controlOnly true` fence on `chatgpt-cloud-elixir` (witnessed only in the
losing copy B record) and per-record `fta:observedAt` evidence stamps.

## Layout

| path | content |
|---|---|
| `ontology/admissibility.ttl` | `fta:` vocabulary, verbatim union (admissibility + admissibility-factory declarations) |
| `ontology/standard-consumer.ttl` | `fts:` vocabulary, verbatim |
| `ontology/r75-realization.ttl` | `c2:` vocabulary, verbatim |
| `ontology/generated-closure.ttl` | `fgc:` vocabulary, verbatim |
| `ontology/qualification-capsule.ttl` | `r86:` vocabulary + UnrdfCheckoutFallback case, verbatim |
| `ontology/r90-fanout.ttl` | `r90:` vocabulary + canonical policy + demand snapshot, verbatim |
| `ontology/cell3-allocation.ttl` | `cell3:` vocabulary, verbatim |
| `ontology/cell3-current-run.ttl` | `alloc:` vocabulary, verbatim - term-disjoint from `cell3:` (verified); both kept as family modules, admission-unit consolidation only |
| `ontology/reconciliation.ttl` | `ftr:` conserved reconciliation records (25 per-repo + 1 snapshot record) |
| `targets/population.ttl` | the reconciled 25-repo population truth (winner copy per repo + evidence stamps) |
| `runs/r75/` | r75 realization snapshot (qualification identities), frozen |
| `runs/r86/` | r86 hosted-startup / preexec observation fixtures, frozen |
| `runs/r90/` | r90 demand population: `targets/`, `closure-demands/`, `replay-demands/`, cycle manifest (r93), frozen |
| `gates/*.rq` | 16 violation-row SELECTs + ORDER BY, family-prefixed exact stems |
| `witnesses/{pass,fail}/` | per-gate witnesses: pass silent, fail fires |
| `qualification/verify.py` | the ONE uniform exact-stem court (exit 0 = ADMITTED) |
| `fixtures/` | prefixed instance fixtures (copy B original, dspygen closure) |
| `queries/`, `templates/` | family-prefixed analysis queries and generation templates |
| `selection/` | cell3 allocation capital (contracts, selectors, sensors, objectives, handoff, reference) |
| `contracts/` | r90 family execution contracts (ash-elixir, python-process, rdf-ontology, rust-wasm) |
| `families/<family>.md` | per absorbed pack's note |
| `tests/` | merged + repointed family courts + reconciliation court |

## Cell3 pair disposition

`cell3:` (allocation) and `alloc:` (current-run) are term-disjoint namespaces;
merging buys no vocabulary unification, so BOTH are kept as family modules
inside the one pack - admission-unit consolidation only, disjointness noted
here and in `families/cell3-allocation.md` / `families/cell3-current-run-allocation.md`.

## Invariants (encoded as gates)

Exact-head identity - no ready without admission - population completeness
(25) - legality before realization - generated artifacts carry validators -
exact source/consumer heads before generation - wasm4pm process-analysis
ownership - lifecycle monotonicity - no ambient DO - control is not fanout -
repo-native authority - one record per repo - evidence-stamped records -
reconciliation winners carried - unified head shape.

## Evidence boundary

Marketplace admission + real-ggen qualification + the uniform exact-stem
witness court only. No execution authority; BRCE remains the sole actuation
boundary.

## Supersession

| absorbed pack (deleted) | version | survives as |
|---|---|---|
| `forced-top25-admissibility-pack` | 26.8.26 | `ontology/admissibility.ttl`, `gates/ftadm_*`, `queries/ftadm_*`, `templates/ftadm_*`, targets -> `targets/population.ttl` |
| `forced-top25-admissibility-factory-pack` | 26.8.26 | fta: declarations -> `ontology/admissibility.ttl`, `queries/ftfac_*`, `templates/ftfac_*`, `tests/test_contract.py`, `tests/test_frontmatter_driver.py` |
| `forced-top25-standard-consumer-factory-pack` | 26.8.26 | `ontology/standard-consumer.ttl`, `queries/ftscf_*`, `templates/ftscf_*`, population copy -> `fixtures/ftscf-forced-top25-copy.ttl`, its 3 real-SHA records won the reconciliation |
| `forced-top25-ocel-fanout-meta-pack` | 0.1.0 | `ontology/r90-fanout.ttl`, `gates/ftr90_*`, `queries/ftr90_*` + `queries/r90-targets/`, `templates/ftr90_*`, `contracts/`, demands -> `runs/r90/` |
| `forced-top25-qualification-capsule-pack` | 26.8.26 | `ontology/qualification-capsule.ttl`, `queries/ftr86_*`, `templates/ftr86_*`, fixtures -> `runs/r86/`, `tests/test_r86_*.py` |
| `forced-top25-r75-realization-composition-pack` | 26.8.26 | `ontology/r75-realization.ttl`, `gates/ftr75_*`, `queries/ftr75_*`, `templates/ftr75_*`, snapshot -> `runs/r75/` |
| `forced-top25-generated-closure-pack` | 26.8.26 | `ontology/generated-closure.ttl`, `gates/ftgc_*`, `queries/ftgc_*`, `templates/ftgc_*`, fixtures -> `fixtures/ftgc-*.ttl` |
| `forced-top25-cell3-allocation-pack` | 26.8.26 | `ontology/cell3-allocation.ttl`, `selection/` |
| `forced-top25-cell3-current-run-allocation-pack` | 26.8.27 | `ontology/cell3-current-run.ttl`, `queries/ftcrun_*`, `templates/ftcrun_*` |

External composition deps of the absorbed packs (documented; `pack.toml` is
FM-PACK-003 minimal): `ggen-ecosystem-ocel-pack`,
`portfolio-epistemic-observability-pack`, `epistemic-sensor-factory-pack`.
`fts:`/`fta:`/`r90:` consumers join by namespace IRI, never by cross-pack
import. Content moved verbatim modulo family-prefix renames; per-pack court
variants replaced by the single uniform court; the 7 ASK-shaped r90 gates were
converted to violation-row SELECTs + ORDER BY (FM gate law) with semantics
preserved (fires iff violation exists).
