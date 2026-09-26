# Exact-Head Standing: ggen-marketplace

## Current Head State
- **Base Commit**: `aa2d6721076134cf0f8f71f7d4a135fe06771deb`
- **Active Branch**: `main`
- **Release Version**: `v26.9.22 (#479) and v26.9.23-int (#483) merged; no tag cut`
- **Timestamp**: `2026-09-25` (re-measure audit)
- **Overall Standing**: `ALIVE` (validate, fingerprint and test-suite witnesses recomputed at this head 2026-09-25; closure-episode, catalog-determinism and SPARQL-ceiling rows carried unchanged from the `c04bb6dd3` audit — see provenance notes below)

## Validation Matrix
| Acceptance Boundary | Command | Status | Output Witness |
|---|---|---|---|
| Pack & Diátaxis Schema | `python3.11 scripts/marketplace.py validate` | `ALIVE` | `packs=327 manifests=327 ontologies=483 templates=1870 native_gates=1554 verifier_gates=41 profiles={"project":124,"projection":164,"semantic":39} diataxis=20` (exit 0) |
| Catalog Determinism | `cmp <(python3.11 scripts/marketplace.py catalog) <(...)` | `ALIVE` | Byte-for-byte identical projection |
| Corpus Fingerprint | `python3.11 scripts/marketplace.py fingerprint` | `ALIVE` | `sha256:4250caa7fae153f89499613e9021bce2d9e4de5491ea39a3ee9be14d27a5090c files=14589` |
| Repository Test Suite | `PYTHONPATH=scripts python3.11 -m pytest tests/test_marketplace.py` | `ALIVE` | `16 passed in 0.09s` |
| HDDL×FOND Closure Episode | `python3.11 domains/repo-closure/verifier/verify_closure_episode.py` | `ALIVE` | `[VALID] Episode lawfully verified and bound for replay` |
| SPARQL Ceilings & Authority | `gates/010_select_ceiling.rq` + `gates/020_mx_authority_ceiling.rq` | `ALIVE` | `SELECT/CONSTRUCT` read-only ceilings admitted; zero ambient DO authority |

Witness provenance (2026-09-24 audit at `c04bb6dd3`): only `packs` and `manifests` were recomputed (`find packs -maxdepth 2 -name pack.toml | wc -l` → 326). The remaining counts (ontologies, templates, native/verifier gates, diataxis) are unchanged from the `00f14b1b9` witness — carried forward, not re-measured.

Witness provenance (2026-09-25 re-measure at `aa2d67210`): the Pack & Diátaxis Schema, Corpus Fingerprint and Repository Test Suite rows were re-measured at this head. `packs` recount 326 → 327 vs the 2026-09-24 `c04bb6dd3` witness: new pack `semantic-case-study-pack@0.1.0` admitted at this head (`aa2d67210`). Repository Test Suite: the bare form `python3.11 -m pytest tests/test_marketplace.py` fails collection in this environment (`ModuleNotFoundError: No module named 'marketplace_scope'` — the test exec's `scripts/marketplace.py`, whose `from marketplace_scope import select_packs` needs `scripts/` on the path); the row records the working invocation with `PYTHONPATH=scripts`. HDDL×FOND Closure Episode, Catalog Determinism and SPARQL Ceilings rows are carried unchanged from the `c04bb6dd3` audit of 2026-09-24 (which itself carried non-pack rows from `00f14b1b9`).

## Scoped Standing Notes
- `ALIVE` covers marketplace contract conformance, path safety, deterministic projection, and repository unit tests.
- Does not assert external cloud actuation or live consumer runtime state.
