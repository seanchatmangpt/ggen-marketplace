# ZD-85: changelog touch — append YD-4 stragglers to [v26.11.3]

YD-4 cut the [v26.11.3] section (9378fd833) before zd-12/20/49/52/62 landed.
This lane appended the missing entries to the existing section — no header cut,
no prior entry rewritten.

## Entries appended (all grounded in on-disk receipts + git log)

- zd-12 baseline-to-disk reconcile: 313→347 entries, ALIVE 295→322, 2 phantom
  drops / 36 adds / 14 changes (commit 0e94adbb8)
- zd-20 pack repairs: 5 ALIVE via real file-level repairs, 2 smalt packs
  honestly blocked (commit d451e63e4)
- zd-49 gac:Registry individual, baseline re-projected 327/9 → 332/5
  (commit b408361c1)
- zd-52 WARN/SKIPPED typing: 9 ratchet-residue / 1 real-signal / 1 skipped
  (commit 74397a441)
- zd-62 MKT-01 ambient ggen 26.11.3 adoption with disclosed
  `--skip-ea-admission` opt-out (commit 55925b64b)

zd-65 (smalt gate inversion repairs): NOT landed — no receipt in
`docs/jira/v26.11.3/receipts/`, no commit in `git log` — per the task's
"if landed" clause, no entry was written. Condition observed, not assumed.

## Files (pathspec)

- `CHANGELOG.md` — 5 bullet entries appended to [v26.11.3] (house style:
  single-line bullets citing commit + receipt path, matching the section's
  existing entries)
- `docs/jira/v26.11.3/receipts/zd-85-changelog-touch.md` — this receipt

## Commands / exits

- `git pull --ff-only` → "Already up to date." (exit 0); base 55925b64b
- `awk 'length>100'` spot-check: new entry lines match the section's
  pre-existing long-bullet style (lines 10-15 pre-date this lane)
- `grep -n '^## \['` → headers strictly descending: v26.11.3 / v26.10.8 /
  v26.10.7 / v26.10.1 / v26.9.30
- `git diff --stat CHANGELOG.md` → 1 file changed, 5 insertions(+)
- `git commit -F <msgfile> -- CHANGELOG.md docs/jira/v26.11.3/receipts/zd-85-changelog-touch.md`
  → exit recorded below; `git push` (pathspec-scoped commit, bounded retry ×3)

## Standing

ALIVE on exact subject: entries re-read from receipts on disk + commits in
`git log --oneline -15`; zd-65 non-landing verified by absence of receipt
file and commit. No other lane's dirty working-tree files touched (working
tree carried in-flight edits from other lanes; staged via explicit pathspec
only).
