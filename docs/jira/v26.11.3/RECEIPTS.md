# RECEIPTS — v26.11.3

Index of receipts under `docs/jira/v26.11.3/receipts/`. Census run 2026-11-04
at main `55925b64b`.

| file | subject | standing |
|---|---|---|
| receipts/ga-2-aoq-gates.md | ga-2 lane: AOQ pack gate courts (PG-A6 step 2) | ALIVE |
| receipts/xd-7-baseline-counts.md | XD-7: baseline.json counts drift fix | ALIVE |
| receipts/yd-4-marketplace-changelog.md | YD-4: Marketplace CHANGELOG v26.11.3 section cut | ALIVE |
| receipts/zd-12-baseline-reconcile.md | ZD-12: baseline-to-disk reconcile (347 packs) | ALIVE (reconcile); ALIVE-with-findings (corpus: 7 REFUSED regressions) |
| receipts/zd-20-pack-repairs.md | ZD-20: repairs for the 7 ZD-12 REFUSED packs | ALIVE (5 repaired); REFUSED-honest (smalt-semconv, smalt-substrate) |
| receipts/zd-28-regression-packs.md | ZD-28: repair the 7 ZD-12 regression packs (ggen 26.10.11 court) | ALIVE (all 7 owned packs) |
| receipts/zd-49-gac-registry.md | ZD-49: gac:Registry individual for graphlaw-ash-capability-pack | ALIVE (gac pack); REFUSED-honest (smalt pair, typed blocker) |
| receipts/zd-52-warn-typing.md | ZD-52: WARN/SKIPPED baseline typing (MKT-03) | ALIVE (typing landed; clap-noun-verb-schema repair staged for a repair lane) |
| receipts/zd-62-mkt01-adoption.md | ZD-62 / MKT-01: adopt ambient ggen 26.11.3 corpus-wide | ALIVE for the adoption commit; honest fail retained (7 packs REFUSED pending ZD-28 integration; ratchet re-run owed post-integration) |

## Counts

- 9 receipts on disk; 9 rows indexed.
- Not on disk here: zd-65 (not landed at census time); zd-21 receipt lives in ggen, not
  this repo.
