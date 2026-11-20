# sjira-marketplace-feedback-pack Standing

Standing: VERIFIED

GAP follow-up 2026-11-19 (ggen 26.11.5). Prior census court left this pack
PARTIAL: union/comma SHACL EXIT=1 on `mf:recurrenceCount` DatatypeConstraint
plus comma-file ClassConstraint on `mf:deltaState` / `mf:OPEN`. Sync was
already EXIT=0.

## Fix (SESSION)

1. `qualification/consumer.ttl` — typed
   `mf:recurrenceCount "3"^^xsd:integer`, `mf:impactScore "8.5"^^xsd:decimal`,
   and local `mf:OPEN` / `mf:QUALIFIED` / `mf:REQUALIFIED a mf:DeltaState`
   so per-file / comma `--files` courts satisfy `sh:class` without a merged
   ontology∪consumer graph.
2. `shapes/mf.shacl.ttl` + `ontology.ttl` — `recurrenceCount` datatype/range
   aligned to `xsd:integer`. ggen 26.11.5 DatatypeConstraint rejects
   `xsd:nonNegativeInteger` even when the consumer literal is correctly typed
   (pyshacl accepts it; peer packs use `xsd:integer`).
3. Mutation fixtures `020` / `030` — local DeltaState individuals + typed
   count/score literals (falsifier semantics unchanged).

## Coordinator evidence (2026-11-19, post follow-up)

cwd: `packs/sjira-marketplace-feedback-pack`. Binary: `ggen 26.11.5`.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/mf.shacl.ttl` | **0** | 57 quads, `shapes_conform: true` |
| `cat ontology.ttl qualification/consumer.ttl > /tmp/mf-union-final.ttl` then validate `--files /tmp/mf-union-final.ttl --shapes shapes/mf.shacl.ttl` | **0** | Preferred union court: 80 quads, `shapes_conform: true` |
| `ggen graph validate --files ontology.ttl,qualification/consumer.ttl --shapes shapes/mf.shacl.ttl` | **0** | Per-file comma court: both conform |
| `ggen graph validate --files qualification/consumer.ttl --shapes shapes/mf.shacl.ttl` | **0** | 26 quads, consumer self-contained for ClassConstraint |
| rdflib gate court: ontology∪qualification → 0 rows on `gates/010..030`; ontology∪each mutation → ≥1 row | **0** | 3/3 positive clean; 3/3 mutations FLIP |
| scratch `ggen sync run --skip-ea-admission` (fresh consumer + `extra_ontologies` consumer) | **0** | wrote `docs/generated/sjira-marketplace-backlog.md` (payment-policy-term row) |
| same scratch replay | **0** | skipped unchanged |

Note: replaying a scratch whose `ggen.lock` was sealed before this GAP edit
returns FM-PACK-008 (content-hash mismatch) — not a pack defect; use a fresh
scratch after pack-content changes.

VERIFIED: union SHACL EXIT=0 and sync EXIT=0.

## Lane 07 re-court (2026-11-19, v26.11.19)

Binary `ggen 26.11.5`. validate + union EXIT=0; rdflib 3/3 clean + 3/3 mutation FLIP; scratch sync with consumer import EXIT=0.
Standing: **VERIFIED**.

## Tip re-court (2026-11-20) — SJ finish residual close

Subject `7ad4b6db`. Binary `ggen 26.11.5`. Ontology / union / comma SHACL
EXIT=0; rdflib gates 010–030 clean; 3/3 mutation FLIP; `qualify_packs`
ALIVE. Marketplace is not the SJ finish blocker — see
`docs/jira/v26.11.20/receipts/sj-pack-sourced-completion-marketplace-not-blocker.md`.
Standing: **VERIFIED**.
