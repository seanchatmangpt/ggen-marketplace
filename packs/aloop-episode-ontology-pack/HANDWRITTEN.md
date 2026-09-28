# HANDWRITTEN.md — aloop-episode-ontology-pack

The pack IS the authored surface (法面): every file below is hand-authored RDF or
hand-authored gate SPARQL manufactured once, so that consumers never hand-write an
episode harness again (the repeated harness — gate execution, fixture injection,
standing bookkeeping — projects through `ggen sync run` in the consumer, driven by
this ontology). No generated files ship in this pack; nothing here is a projection
of another source, so there is no reconciliation manifest and no 不一致 surface.

| path | what | why hand-authored (once) | date |
|---|---|---|---|
| pack.toml | pack admission record + authority boundary | pack authorship is the marketplace's lawful write surface | 2026-09-25 |
| ontology.ttl | ALOOP episode model: 19 object classes (prov-anchored), 28 event classes (OCEL 2.0 name parity), 15 qualifier properties, closed two-axis standing vocabulary, autonomy epoch, dogfood instance of episode ALOOP-ZCODE-DOGFOOD-001 | one-time ontology authorship; custom `aloop:` minted only after the failed-edge record against prov / OCEL 2.0 / EARL / oslc_cm / dcterms (recorded in-file) | 2026-09-25 |
| gates/010_episode_integrity.rq | violation-row gate: event→episode binding, episode→objective, WorkOrder dual-type | gate authorship is pack authorship; runs via FM-PACK-013 in consumers | 2026-09-25 |
| gates/020_human_causal_edge.rq | human-causal-edge detector (post-epoch actuation × human agent) | same; Lane 1 crown input, Lane 9/10 analysis vocabulary | 2026-09-25 |
| gates/030_closed_standings.rq | closed standing vocabulary enforcement (two axes) | same | 2026-09-25 |
| templates/episode_summary.json.tmpl | projects episode/provider standing + all three gate verdicts to generated/episode_summary.json in a consumer sync | pack ships >= 1 template (FM-PACK-005, witnessed by real ggen sync); the render is the consumer-facing projection of the gates | 2026-09-25 |

Ledger position: zero 産面 bytes. No consumer repo was touched by authoring this
pack; the dogfood instance names episode ALOOP-ZCODE-DOGFOOD-001 as data, not as
authority. Nothing claimed: actuation authority, provider-selection policy, planner
semantics, OCEL interchange serialization (see pack.toml boundary).
