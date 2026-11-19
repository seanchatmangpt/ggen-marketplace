# issue-platform-controls-pack Standing

Standing: VERIFIED

Coordinator GAP follow-up 2026-11-19 (ggen 26.11.5, rdflib 7.1.4). Prior
PARTIAL was dep-gate pollution: unscoped mount of
`~/ggen_igniter/priv/ggen/semantic-jira-pack` under `[packs]` false-fails
FM-PACK-013 on ADR-0010 witness-driver `gates/010_work_order_subjects.rq`
(37 rows). Admitted court scopes the dep to real SJ SEMANTICS + real SJ
`verify/` offender LAW — does not weaken SJ execution gates.

## Admitted sync court (pack contract)

```sh
SJ_COURT=$(qualification/materialize_sj_dep_court.sh)
# → byte copy of real ontology.ttl
# → gates/*.rq = real verify/*.unbound.rq (offender, 0 rows = PASS)
# → witness-driver gates/ + full SJ projection templates omitted
```

Scratch consumer mounts `issue-platform-controls-pack` + `$SJ_COURT` as
`semantic-jira-pack` (satisfies `urn:ggen:pack:semantic-jira-pack`).
Missing real tree → script exit 2 `BLOCKED:missing-semantic-jira-pack`.

Unscoped igniter-tree mount remains intentionally red (ADR-0010 ≠
FM-PACK-013 impedance) and is not the VERIFIED evidence path.

## Commands + exits (2026-11-19)

cwd: `packs/issue-platform-controls-pack`. Binary: `ggen 26.11.5`.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/ip.shacl.ttl` | **0** | `shapes_conform: true` |
| `ggen graph validate --files ontology.ttl,qualification/consumer.ttl --shapes shapes/ip.shacl.ttl` | **0** | |
| union `ontology∪qualification` → validate `--shapes` | **0** | |
| rdflib gates 010–050: pos 0 rows (also 0 ∪ real SJ ontology); each mutation ≥1 | **0** | |
| `qualification/materialize_sj_dep_court.sh` | **0** | ontology byte-identical to real; 6 verify LAW gates |
| scratch `ggen sync run --skip-ea-admission` + scoped `$SJ_COURT` | **0** | wrote inventory + projection + sj-dep stub |
| replay sync (same scratch) | **0** | `written=[]`, same `graph_hash_hex` |
| scratch sync + unscoped real igniter tree (contrast, not evidence) | **1** | `[FM-PACK-013]` `010_work_order_subjects.rq` → 37 rows |

VERIFIED: validate + rdflib + scoped real-SJ sync (+ replay) all EXIT=0.

## Lane 07 re-court (2026-11-19, v26.11.19)

Durable admitted sync: `qualification/run_admitted_sync_court.sh`
(relative pack symlinks + local scratch marker; pack templates from mount;
SJ = scoped verify LAW only). Binary `ggen 26.11.5`.

| Command | EXIT |
|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/ip.shacl.ttl` | **0** |
| rdflib gates 010–050 clean; each mutation ≥1 FLIP | **0** |
| `qualification/materialize_sj_dep_court.sh` | **0** |
| `qualification/run_admitted_sync_court.sh` (sync + replay) | **0** |

Unscoped igniter mount remains intentionally red (not evidence).
Standing: **VERIFIED**
