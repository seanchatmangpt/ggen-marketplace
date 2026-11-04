# XD-7: baseline.json counts drift fix

Fixes XA-3 finding: `qualification/baseline.json` counts block said `ALIVE: 292`
while the per-pack tally is 295 (the aoq/cscb/tort pack entries added in commit
608242384 were not reflected in counts).

## Method

Mechanical recompute (no hand-edited number): a python3 script loads the JSON,
tallies `status` values across the `packs` dict, rewrites only the `counts`
block preserving the original key order, and json-dumps with the file's
existing 2-space indentation.

## Commands / exits

- `python3 /tmp/fix_counts.py` — exit 0; old `{'ALIVE': 292, 'REFUSED': 8, 'SKIPPED': 1, 'WARN': 9}` → new `{'ALIVE': 295, 'REFUSED': 8, 'SKIPPED': 1, 'WARN': 9}`
- `jq .counts qualification/baseline.json` — exit 0; shows ALIVE: 295
- Independent recount: `Counter(v['status'] for v in packs.values())` = ALIVE 295 / REFUSED 8 / WARN 9 / SKIPPED 1, total packs 313; `sum(counts.values()) == 313` assertion passed
- `git diff qualification/baseline.json` — ONLY the counts block changed (single line: `"ALIVE": 292` → `"ALIVE": 295`); no other lines touched

## Standing

ALIVE — diff committed and pushed to main (see commit SHA on main). Counts now
derive mechanically from the packs array; any future pack addition must
re-run the recount or the drift class recurs.
