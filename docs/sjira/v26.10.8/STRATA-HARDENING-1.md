# STRATA Family Hardening Wave — Work Order (OPEN)

- **Wave**: strata family hardening, 7 packs (protocol, pn64, valve, cas, signer, temprun, stratus), post-landing hardening of `eec4782d7` / `62f547b7e` / `3792e4ba6` (no sjira receipts at landing).
- **Planning evidence**: 20 Explore lanes + 20 Plan lanes (2026-10-12/13); baseline court `/tmp/wave-baseline-qual.json`: 3 ALIVE (protocol, pn64, valve) / 4 REFUSED (FM-PACK-014 class, `GGEN_PACK_SYNC_FAILED`).
- **Branch**: `strata-hardening-wave` from `main` @ `6a27a31ae`. Fix-forward, explicit pathspec adds, batch-ordered merges.
- **Status**: OPEN 2026-10-13 (coordinator lane L0).

## Items (P1–P19; titles from the planning-wave record)

| # | Item | Batch | Key falsifier |
|---|---|---|---|
| P1 | FM-PACK-014: delete `[dependencies]` ×5, a2a-durability comment | 1 | REFUSED→ALIVE flip |
| P7 | Delete dead `clap_frame.rs.tmpl` | 1 | templates 1852→1851 |
| P18 | Ontology hygiene ×3 packs (declare classes, delete dead vocab, verbOpcode, drop pn: alias) | 1 | sync output byte-identical |
| P9 | v1→v2 manifest migration ×4 packs (temprun→signer→stratus→cas) | 2 | first sync mints output, court ALIVE |
| P6 | Valve `@receipt_len` runtime fix (template + regenerate) | 2 | elixirc 0 warnings, refuse/1 32 bytes |
| P8 | pn64 fire-law equivalence court + ontology.ttl:100 comment | 2 | new test passes, 5 existing pass |
| P14 | pn64 first sync + commit `generated/pn64_masks.rs` (after P8) | 2 | mint-once, double-sync identical |
| P16 | wire projection rule + valve 32-byte cross-graph gate (Python union-graph court) | 2 | positive/negative witnesses |
| P2 | 13 violation-row gates across 7 packs (after P9; temprun needs `st:admissionFuel 3`) | 3 | sync exit 0; mutated-copy refusal |
| P15 | Sync schedule all 7 + `ggen receipt history/verify` per pack | 3 | chains valid, double-sync identical |
| P12 | `tests/test_strata_family_pack.py` 5 courts + sabotage twins | 3 | twins prove courts can fail |
| P13 | CI `strata-packs-court` (`qualify_packs_r18.py --pack` + courts.json + court sh) | 3 | ci_plan dry-run selects it |
| P10 | lifecycle.toml ×7 corrected `intent="review"` entries | 4 | validate + lifecycle listing |
| P11 | README 314→315 + 7 thin READMEs + index regen (after P10) | 4 | thin 112→105, links clean |
| P3 | Diátaxis ×4 + book.ttl nav:216-219 + SUMMARY regen | 4 | nav coverage + doc links tests |
| P4 | PACK_CLASSES ×7 (protocol KernelPack, rest CapabilityPack) + pack-classes.md wording | 4 | catalog pack_class populated |
| P5 | Namespace unification to `https://strata.chatman.ai/ontology#` (big-bang, lockstep) | 1-start | catalog cmp + row-count guard |
| P17 | errc-tracker.md ×7 (citations re-verified; cas push is :293) | 5 | no orphan citations |
| P19 | Activation deferral record (rationale + future checklist; no active.toml edits) | 5 | docs-only |

## Lane partition (same checkout; coordinator owns git)

- **L-protocol**: P2-protocol, P7, P16, P18-protocol (serialized)
- **L-valve**: P6, P2-valve, P16-valve, P18-valve
- **L-pn64**: P8, P14, P2-pn64, P18-pn64
- **L-migrate**: P9 (temprun/signer/stratus/cas), P2 on those packs
- **L-docs**: P3, P10, P11, P19, P20
- Coordinator: integration, batches, commits, receipts.

## Verification gate (before merge)

admit-config → validate → catalog cmp (branch vs main) → fingerprint delta → qualify-marketplace.sh → `qualify_packs.py` strata 7/7 → pytest strata → pytest full (`-q -p no:cacheprovider -n auto --dist worksteal --ignore=tests/test_new_pack.py`) → per-pack sync-twice `cmp -r`.

## Closure format

Per-item `STRATA-<n>-CLOSE.md` per `PACK_FEEDBACK-425-CLOSE.md` shape (Item / Status / Fixing commit / Fix shape / Witnesses / Consumer consequence); `RECEIPT-INDEX.md` rows kept equal to dir contents.
