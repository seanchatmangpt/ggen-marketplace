# ggen-marketplace v26.11.3 closure seal — wave-closing seal receipt

Date: 2026-11-04. Lane: ZD-132 (seal lane). This receipt's own actuation
touches only two files (this closure + its own receipt
`../receipts/zd-132-marketplace-closure.md`); every code deliverable landed
via receipted lanes cited below. Every standing word is re-read from the
cited receipt bodies on disk, never memory.

## Exact subject

`/Users/sac/ggen-marketplace` main @
`7364405a048ae64da3039c4bdbf8cfbf9c224ae6`, pushed to origin (origin/main
verified equal at seal time via `git fetch && git rev-parse HEAD
origin/main`). The two seal files are landed by this very seal commit.

## Deliverables with standing (from receipt bodies)

- **Baseline 313→347 reconcile**: ALIVE (zd-12, `0e94adbb8`). Full
  mechanical re-run of the qualification court + `warn_ratchet.py baseline`
  re-projection, no hand-written JSON: 2 phantom entries dropped
  (a2a-security, a2a-v1-protocol — pack dirs absent on disk), 36 packs
  added (29 ALIVE / 7 REFUSED, real FM-PACK-005/FM-GEN-008 defects),
  14 existing changed.
- **MKT-01 adoption**: ALIVE (zd-62, `55925b64b`). Ambient ggen 26.11.3 is
  the corpus-wide qualification court identity via the disclosed
  `--skip-ea-admission` opt-out on both `sync run` invocations in
  `scripts/qualify_packs.py` (lawful per ggen `sync.rs:346-351`; ZB-10
  census 6/6 sampled packs refused without it). Adoption-time counts ALIVE
  326 / WARN 13 / REFUSED 7 / SKIPPED 1 of 347.
- **Corpus 347/347 qualified, zero REFUSED**: ALIVE (zd-28 `808c621c4` +
  zd-65 `9d042c2cf`; final counts {ALIVE 337, WARN 9, SKIPPED 1,
  REFUSED 0}). zd-20 repaired 5 of the 7 zd-12 REFUSED packs with real
  file-level repairs (`d451e63e4`); zd-49 landed the vendored
  `gac:Registry` individual from the real graphlaw registry
  (`b408361c1`), unblocking the 2 blocked smalt packs; zd-65 rewrote the
  inverted positive-style gates violation-style (6 gate files, per-gate
  non-vacuity flip witnesses) and typed the timeout pair as load-class;
  zd-28 closed the remaining zd-12 regressions through the pinned
  26.10.11 court.
- **WARN typing**: ALIVE (zd-52, `74397a441`). All 11 WARN/SKIPPED entries
  typed mechanically via `warn_class` + `annotation` fields: 9
  ratchet-residue (`ACCEPTED-WARN:*`), 1 real-signal
  (`REPAIR-LANE:composition-closure-claim-unwitnessed-by-court` on
  clap-noun-verb-schema-pack — closed by zd-28's requires-closure repair),
  1 skipped harness limitation
  (`SKIPPED:GGEN_PACK_GENERATED_BUILD_NEEDS_WORKSPACE_ROOT`, tcps-pack).
- **4 pack families' gates** (zd-28 cross-pack edits, disclosed; none
  relaxes a passing contract): ash-extension-core 020 NestedEntity arm
  ported from ash-extension-pack's canonical gate; pptx-presentation
  010/020/030 inventory-SELECTs converted to violation-checks;
  strategic-doctrine 050 residual-budget arms scoped to the doctrine
  namespace; clap-noun-verb crate/behavior/boundary/routing full-compiler-
  closure `requires` (court-witnessed for schema-pack).
- **zd-65 gate families**: smalt-semconv `010_semconv_census.rq`,
  smalt-substrate `config_coverage.rq` + `shapes-coverage.rq`,
  ash-pplan-chaos `010/020/030` — each census-empty + per-row
  completeness branches, healthy graph 0 rows, each gate flipped at least
  once on a mutated /tmp pack copy (no vacuous gate in the set).

### Pack-lock scope note

The ratchet baseline (`qualification/baseline.json`) is corpus-wide — all
347 packs under `packs/` — and is NOT scoped to `marketplace.active.toml`'s
20-pack `[active]` set; the ratchet never gates the active set, only the
corpus. `ggen.lock` at repo root is the root-manifest sync lock, not a
per-pack lock; no per-pack lock artifact exists in this repo.

## Receipt count (re-read at seal time)

`ls docs/jira/v26.11.3/receipts | wc -l` → **12** pre-seal; **14** after
this seal lands its two files.

## BLOCKED / DEFERRED (carried, not claimed)

- **Tags unminted**: no v26.11.3 tag minted on this repo (CHANGELOG
  carries the `[v26.11.3] — 2026-11-04` section; the tag does not exist).
- **Court identity mixed in the landed baseline field**: the ambient court
  identity is ggen 26.11.3 (zd-62/zd-65, `--skip-ea-admission` opt-out
  disclosed in the court script's docstring), but
  `qualification/baseline.json:ggen_version` reads `"ggen 26.10.11"` —
  zd-28's final full re-projection ran the pinned 26.10.11 court (the
  then-working-tree script carried an uncommitted cross-lane
  `--skip-ea-admission` edit the pinned binary rejects) and its mechanical
  re-projection overwrote zd-65's `"ggen 26.11.3"` field. Disclosed in
  zd-28's own receipt, not silently mixed; next full-corpus re-projection
  under ambient 26.11.3 will restamp the field mechanically.

## Falsifiers

- Any cited receipt's standing word disagrees with its body on disk.
- A cited gate command re-run now exits non-zero (load-class harness-pack
  timeouts re-typed per zd-65 if they fire).
- The landed baseline counts disagree with a fresh `jq -c .counts
  qualification/baseline.json`.
- Receipt count in this file disagrees with a fresh `ls | wc -l`.
- origin/main ≠ HEAD for the subject SHA recorded above.

## Verification ladder (this seal's own runs, marketplace @ 7364405a0)

- 3-pack qualify sample (ambient ggen 26.11.3, workers 3):
  `python3 scripts/qualify_packs.py --workers 3 --pack a2a-conformance-pack
  --pack typer-azure-pack --pack clap-noun-verb-crate-pack --report
  /tmp/seal_sample.json` → **exit 0**, `qualified packs=3
  profiles={"project":1,"projection":2,"semantic":0} ggen="ggen 26.11.3"`
  (clap-noun-verb-crate WARN non-blocking per
  CARGO_BUILD_CHECK_BLOCKING=False).
- `python3 scripts/warn_ratchet.py check /tmp/seal_sample.json --subset`
  → exit 0, `ratchet ok counts={"ALIVE": 2, "REFUSED": 0, "SKIPPED": 0,
  "WARN": 1}` (2 ALIVE + 1 WARN, matching baseline classes).
- `jq -e . qualification/baseline.json` → valid;
  `jq -c .counts` → `{ALIVE:337, REFUSED:0, SKIPPED:1, WARN:9}`
  (347 packs).
- `git rev-parse HEAD origin/main` → equal (`7364405a0…`), after
  `git fetch`.
