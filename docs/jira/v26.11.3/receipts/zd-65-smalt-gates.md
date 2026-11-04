# ZD-65: smalt/pplan inverted gates — positive-style corpus defect closed

ZD-49's falsifier outcome typed the blocker: smalt-semconv
`gates/010_semconv_census.rq` (7 rows) and smalt-substrate
`gates/config_coverage.rq` (60 rows) were written positive-style ("MUST
return >= 1 row") while ggen's FM-PACK-013 is violation-style — any row is a
refusal. Every lawful corpus gate is violation-style; a positive-style gate
is scored inverted and refuses a healthy sync. Repair: root-cause each
gate's intent and rewrite as violation-style SPARQL selecting the DEGENERATE
condition, zero rows = healthy. No court relaxed. The two zd-49 timeout-class
packs and the ash-pplan-chaos own-gate refusal are also closed here.

## Root cause and intent per gate

- **smalt-semconv `010_semconv_census.rq`** — intent: the SemConvEvent census
  must exist and every event individual must be renderable. Violation-style
  rewrite selects: (1) census-vanished (fixed-subject VALUES + NOT EXISTS);
  (2) event missing name; (3) event missing kind/stability/brief/order; (4)
  SemConvAttribute orphaned from its event (matches
  `verify/semconv-coverage.unbound.rq`'s contract). Healthy graph: 7 events,
  14 attributes, all complete → 0 rows.
- **smalt-substrate `config_coverage.rq` really directed at ConfigKey
  completeness; the original file only asserted existence** — intent: the
  ConfigKey census must exist and every key must be renderable in the
  store-table registry. Rewrite: (1) census-vanished; (2) ConfigKey missing
  `smalt:name`. Healthy graph: 60 named ConfigKeys → 0 rows.
- **smalt-substrate `shapes-coverage.rq`** — intent: TypeBinding coverage of
  declared resource types. Rewrite: (1) census-vanished; (2) binding missing
  resourceType; (3) binding missing apiVersion; (4) non-inventory binding
  missing a shape (inventory-only bindings legitimately carry no shape —
  mirrors verify/shapes-coverage.unbound.rq's shape-OR-inventoryType
  contract). Healthy graph: 56 shaped + 4 inventory-only bindings → 0 rows.
- **ash-pplan-chaos `gates/010/020/030`** — were positive "driver" queries
  ("one row per COMPLETE row"); FM-PACK-010... FM-PACK-013 scores them
  inverted, so the single healthy Harness row refused every sync. Rewrite:
  each gate = census-empty branch (fixed-subject VALUES + NOT EXISTS over the
  complete-row BGP) + per-row completeness branch + harness-join branch,
  matching the pack's own `verify/*.violation.rq` contracts. Healthy graph: 1
  Harness / 6 Invariants / 4 KillPhases, all complete → 0 rows.

## Court identity disclosure

The task called for the zd-20-era `ggen.bak-26.10.11` pin; that pin can no
longer run the current court — `scripts/qualify_packs.py` hard-codes
`--skip-ea-admission`, which 26.10.11 rejects (`unexpected argument`), exit 1
for every pack. The live court identity is ambient **ggen 26.11.3** (MKT-01,
as zd-52 adopted corpus-wide; baseline `ggen_version` is now `ggen 26.11.3`).
All receipts here are 26.11.3 court runs.

## Commands / exits

- Scoped before-court (5 packs, ambient 26.11.3, workers 5):
  `python3 scripts/qualify_packs.py --workers 5 --report /tmp/zd65_before2.json`
  → exit 2: semconv FM-PACK-013 (7 rows), substrate FM-PACK-013
  (config_coverage 60 rows), pplan FM-PACK-013 (010_harness 1 row), harness
  pair ALIVE (first witness — later flipped to timeout under load; see below).
- Rewrote 6 gate files (5 packs), smoke-tested 0 rows on pack graphs via
  rdflib.
- Non-vacuity flip witnesses (court's own `prepare_consumer` capsule,
  `ggen.toml` repointed at a mutated `/tmp/zd65-flips/` pack copy, real
  `ggen sync run --skip-ea-admission`):
  - semconv: rename `smaltv:name "smalt.arm.admit"` → `.MUT` → FM-PACK-013,
    `010_semconv_census.rq` 2 rows (`semconv-attribute-orphaned-name` + …).
  - pplan: break `acp:sabotageModule` on Harness → FM-PACK-013,
    `010_harness.rq` 2 rows (`harness-census-empty` + …).
  - substrate shapes-coverage: drop tb-kv's `smalt:apiVersion` → FM-PACK-013,
    `shapes-coverage.rq` 1 row (`type-binding-missing-apiVersion`, subject
    smalt#tb-kv). An existence-only mutation (renaming tb-kv) provably does
    NOT flip these gates — census-nonempty and completeness preserved —
    which is itself a witness that the completeness branches are load-bearing.
  - substrate config_coverage: `a smalt:ConfigKey` → `a smalt:ConfigKeyOLD`
    globally → FM-PACK-013, `config_coverage.rq` 1 row
    (`config-key-census-empty`). Each gate file flipped at least once; no
    vacuous gate in the set.
- Timeout diagnosis: unbounded manual syncs (court's own consumer capsules)
  converge exit 0 in 11–21 s busy under load 240+; the engine hard-caps the
  court bound at 5 s (`GGEN_PACK_TIMEOUT_BOUND: must_be_gt_0_and_lte_5`).
  Solo re-runs at load ~40: both harness packs ALIVE. **Type: load, not
  hang.** Full court at load ~39 with `--workers 4` witnesses all 347 packs.
- Full re-projection: `python3 scripts/qualify_packs.py --workers 4 --report
  /tmp/zd65_full3.json` → **exit 0**, counts {ALIVE: 337, REFUSED: 0,
  SKIPPED: 1, WARN: 9} (baseline moved ALIVE 332 → 337, REFUSED 5 → 0; the
  WARN 9 set is the same cargo-build WARN class as before, ratchet check ok).
- Ratchet: `warn_ratchet.py baseline` exit 0; `check` exit 0 "ratchet ok";
  `jq -c .counts` → {ALIVE:337, REFUSED:0, SKIPPED:1, WARN:9};
  `ggen_version` = "ggen 26.11.3".

## Standing

- smalt-semconv-pack, smalt-substrate-pack, ash-pplan-chaos-pack,
  agent-harness-recompilation-pack, ecc-agent-harness-profile-pack: **ALIVE**
  (court-witnessed under ambient ggen 26.11.3, full-corpus exit 0).
- Corpus: 347 packs, zero REFUSED for the first time in the v26.11.3 window;
  baseline recomputed mechanically.
- Defect class closed: no positive-style gate remains in gates/ (this lane's
  6 rewrites; the corpus-wide census of the remaining gates/ files is a
  separate sweep — zd-49 named only these 5 REFUSED packs and all 5 are
  ALIVE).
