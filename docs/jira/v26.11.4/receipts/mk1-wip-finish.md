# MK-1 WIP-Finish: kafka-wire-pack + smalt-substrate-pack

Standing: PASS

Lane: MK-1 (WIP-finish), repo /Users/sac/ggen-marketplace. Prior session crashed
mid-lane; dirty tree inherited. Coordinator owns git — no commits made.

## Inventory + classification (git status, 2026-11-05)

kafka-wire-pack (one coherent change-set: served-version-matrix correction
KD-190 / KD-HC-1 / KD-HC-3, 2026-11-04):

- `packs/kafka-wire-pack/ontology.ttl` — servedMax corrections: vr-fetch 2→3
  (KD-190), vr-metadata 4→3 (KD-HC-1 transitive cap: advertising v4 makes
  clients send Fetch v4, unserved → crash-only), vr-api-versions 0→2
  (KD-HC-3: kafkajs negotiates via ApiVersions). Plus provenance comment.
- `templates/kafka_api_keys_rs.tmpl`, `kafka_error_codes.ex.tmpl`,
  `kafka_group_api_keys.ex.tmpl`, `records_go.tmpl`, `status_rs.tmpl` —
  frontmatter stripped, marked `DEFERRED (lane R2-I 2026-11-05)` so consumer
  sync self-discovery skips unconsumed projection targets.
- `templates/wire_ex.tmpl` — KD-COVERS: KD-190, KD-HC-1, KD-HC-3 annotation
  added; `version_matrix_rows/0` and `crc_domains/0` accessors added.
- `witnesses/pass/050_version_matrix_closure.ttl` and `witnesses/fail/...` —
  vr-fetch servedMax 2→3 in both, keeping the pass/fail corpus consistent with
  the ontology change (fail witness still violates closure via Produce
  servedMax 9 ≥ flexibleFrom 9, so the gate still flips).

smalt-substrate-pack:

- `packs/smalt-substrate-pack/ontology.ttl` — single data-fact correction:
  `smalt:st-smalt_eh_checkpoints` `smalt:persisted false → true` (premise-rot:
  the checkpoints table is persisted now that the DETS snapshot restore
  capability landed). No gate constrains `smalt:persisted` (grep of
  `gates/*.rq` + `queries/store_tables.rq` shows it projected only), so no
  gate impact.

## Gate

Canonical gate per `packs/kafka-wire-pack/gate-court.toml`
(`runner = "python3 qualification/verify.py"`, 9 SPARQL closure gates with
required pass+fail witnesses, exact-stem court):

```
cd /Users/sac/ggen-marketplace/packs/kafka-wire-pack
python3 qualification/verify.py
```

Result: verdict CONFORMANT, 9 gates, 9 flips (all FLIP-OK), EXIT=0.
Each gate runs on its own witnesses; 080_template_linkage FLIP-OK confirms the
frontmatter-stripped templates stay linked; 050_version_matrix_closure FLIP-OK
confirms witness corpus consistency with the servedMax corrections.

smalt-substrate-pack has no standalone court runner; its ontology edit is a
single unconstrained data fact — covered by the inventory above.

## Owned files

All 10 modified files listed under Inventory; no new files created except this
receipt. Untracked: none. Working tree left for coordinator.
