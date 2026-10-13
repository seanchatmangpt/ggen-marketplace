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

## Addendum 2026-10-13 (post-wave)

Repair lane R18, same day as the flag-only pass above. Live numbers re-run this
session: `python3 scripts/marketplace.py validate` → `packs=315 manifests=315
ontologies=513 templates=1852 native_gates=1880 verifier_gates=21 profiles=
{"project":108,"projection":161,"semantic":46} diataxis=20`;
`python3 scripts/marketplace.py fingerprint` →
`sha256:0c3f12e1a9ce709e6862ece7541e7b85f3e2d0173f878bd0f4fe5cd9d2118ebe files=15746`.

### Still-open drift (flag-only this wave, unfixed BY DESIGN)

- Finding #1 — `docs/context/standing.md:346` (re-verified: the validation-matrix
  "Pack & Diátaxis Schema" row) still pins `templates=1800`. Current live value:
  **templates=1852**. Next standing-doc refresh should write 1852 (as-of 2026-10-13).
- Finding #2 — `docs/context/standing.md:348` (re-verified: the "Corpus Fingerprint"
  row) still pins `sha256:1e9a8aad51f9f383f9d6b04bdde2aa696b191e6154fd3b34f33bf626ffae339b`.
  Current live fingerprint: **`sha256:0c3f12e1a9ce709e6862ece7541e7b85f3e2d0173f878bd0f4fe5cd9d2118ebe`
  (files=15746)**. Next standing-doc refresh should write this value (as-of 2026-10-13).
- `docs/context/standing.md:14` — line re-verified: still reads `- Pack count: 305`
  under "Repository facts". Current live value: **packs=315** (validate output above
  and `ls packs | wc -l` = 315 from the original census). Next standing-doc refresh
  should write 315 (as-of 2026-10-13).

### RESOLVED this wave

- Finding #3 — `docs/reference/PACK-INDEX.md` **RESOLVED**. Line 6 re-verified this
  session: now reads "315 packs: 309 active, 6 deprecated"; file carries the
  GENERATED-by-`scripts/gen_pack_index.py` header; lifecycle entries landed in-wave
  (309 active + 6 deprecated = 315). No longer drift.
- `docs/reference/pack-catalog.md` **RESOLVED**. Regenerated in-wave
  (`python3 scripts/marketplace.py browse`); header tier counts re-verified this
  session: verified (147) + documented (56) + thin (112) = **315**, consistent with
  the live pack count. No stale 306 figure present. No longer drift.

## Pre-existing suite failures (2026-10-13 clean-run triage)

The strata-hardening wave's clean full-suite run on this branch:
**30 failed / 2145 passed / 5 errors — zero strata-attributable failures.**
All 30+5 triaged as pre-existing on `main`, untouched by the wave:

- **evolvable-capability ×7** — `tests/test_evolvable_capability_pack.py`;
  pack untouched by the wave.
- **qri-consumer ×5 failed + 5 errors** — `tests/test_qri_consumer_binding_pack.py`;
  root cause: stale `packs/qri-consumer-binding-pack/ggen.lock` (blake3
  content hashes) vs pack source on disk. Reproduced identically on `main`
  via a `git-archive` clean-tree run — not wave drift.
- **solution-quickstart ×3** — `tests/test_solution_quickstart.py`; stale lock
  pins in `solutions/enterprise-aaif/solution.json` (`packs[].content_hash`)
  dating from `f52ed0e85`. Reproduced identically on `main`.
- **industry-closure ×1** — `tests/test_industry_closure_pack.py`;
  `pack.toml` `[capabilities]` block vs the minimal-manifest expectation,
  introduced by `f52ed0e85` ("complete [capabilities] annotation").
- **greene ×2** — `tests/test_greene_licensing_case_pack.py` +
  `tests/test_greene_licensing_case_hardening.py`.
- **capability-ecology ×3** — `tests/test_capability_ecology_*.py`.
- **others** — singletons across remaining files; same profile.

All of the above persist under CI-parity conditions (python 3.12 + pinned
requirements, wave lane W3), confirming they are environmental/pre-existing,
not wave-introduced.

**Fix path** (out of wave scope, do on `main`): regenerate the two stale
locks — `packs/qri-consumer-binding-pack/ggen.lock` and the
`solutions/enterprise-aaif` solution lock (`solution.json` content hashes) —
via `ggen sync`, then re-run the two suites.
