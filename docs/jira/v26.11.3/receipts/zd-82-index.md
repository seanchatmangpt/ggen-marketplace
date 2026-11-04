# ZD-82: v26.11.3 receipts index (RECEIPTS.md)

## Subject

Census of `docs/jira/v26.11.3/receipts/` at main `55925b64b` (re-read after
concurrent ZD-65/ZD-28 pushes) and a one-row-per-receipt index written to
`docs/jira/v26.11.3/RECEIPTS.md`.

## Census (ls, this session)

9 receipt files on disk: ga-2-aoq-gates, xd-7-baseline-counts,
yd-4-marketplace-changelog, zd-12-baseline-reconcile, zd-20-pack-repairs,
zd-28-regression-packs (untracked at census time — indexed), zd-49-gac-registry,
zd-52-warn-typing, zd-62-mkt01-adoption.

- zd-65: NOT on disk at census time — indexed as absent.
- zd-21: receipt lives in ggen, not this repo (expected divergence).

## Standing derivation

Standing per row read from each receipt's `## Standing` / inline standing
section (ALIVE / ALIVE-with-findings / REFUSED-honest as stated by the owning
lane — not re-graded by this lane).

## Counts

| | |
|---|---|
| receipts on disk | 9 |
| rows in RECEIPTS.md | 9 |
| not on disk | zd-65, zd-21 (in ggen) |

## Deliverable

- `docs/jira/v26.11.3/RECEIPTS.md` (new — no README.md or index existed in the dir).

## Commit discipline

Pathspec-scoped add of the two index files only; other lanes hold dirty pack
files and were not touched.
