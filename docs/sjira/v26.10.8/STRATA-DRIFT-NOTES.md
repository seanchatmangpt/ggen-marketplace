# Strata Hardening Wave — Repo-Documentation Drift Notes (L18)

Docs-only lane, 2026-10-13, branch `strata-hardening-wave`. Flag-only lane:
nothing in this list was fixed. Each item re-verified on disk this session
(file read, line re-located); line numbers below are as-found 2026-10-13.

## Findings

| # | location | pinned claim | live value | note |
|---|---|---|---|---|---|
| 1 | `docs/context/standing.md:346` | `templates=1800` (validation matrix row, "Pack & Diátaxis Schema") | 1851 post-deletion | stale; the 1800 figure predates the wave's template deletions |
| 2 | `docs/context/standing.md:348` | corpus fingerprint `sha256:1e9a8aad…` | drifted with the corpus | stale fingerprint; regen blocked until lifecycle entries land |
| 3 | `docs/reference/PACK-INDEX.md:6` | "306 packs: 300 active, 6 deprecated" | 315 pack dirs on disk (measured this session: `ls packs \| wc -l` = 315) | regen blocked until lifecycle entries land |
| 4 | `README.md` 314-count | dispatch brief said README pins a 314 pack count | **NOT FOUND at line level** | grep of `README.md` for `314` returns 0 matches this session; line 9 already reads "315 packs as of 2026-10-12". Recorded as already-corrected / dispatch figure not reproducible on disk |

## In-flight note

- README pack-count: flagged by the wave as being fixed by another lane
  (in-flight). On-disk state at read time (line 9, "315 packs") suggests that
  fix has already landed or the count is maintained elsewhere; integration
  should confirm the fix lane's receipt rather than re-fixing here.

## Method note

Live pack count measured directly (`ls packs | wc -l` = 315). Template live
figure 1851 carried from the wave census (post-deletion); this lane's raw
`find packs -name '*.tera'` count (227 `.tera` at root + nested layout) is
not the same denominator as the census figure, so the census number is cited
as-of-date rather than re-measured under a mismatched method.
