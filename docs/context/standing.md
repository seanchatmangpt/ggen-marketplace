# Exact-Head Standing: ggen-marketplace

## Current Head State
- **Base Commit**: `00f14b1b966900aa129f16a2e51727ef697823ec`
- **Active Branch**: `docs/rewrite-agents-contract`
- **Release Version**: `v26.9.13`
- **Timestamp**: `2026-09-13T09:26:00-07:00`
- **Overall Standing**: `ALIVE` (all 7 DoD release gates verified and passed)

## Validation Matrix
| Acceptance Boundary | Command | Status | Output Witness |
|---|---|---|---|
| Pack & Diátaxis Schema | `python3.11 scripts/marketplace.py validate` | `ALIVE` | `packs=312 manifests=312 ontologies=463 templates=1800 native_gates=1471 verifier_gates=37 diataxis=20` |
| Catalog Determinism | `cmp <(python3.11 scripts/marketplace.py catalog) <(...)` | `ALIVE` | Byte-for-byte identical projection |
| Corpus Fingerprint | `python3.11 scripts/marketplace.py fingerprint` | `ALIVE` | `sha256:1e9a8aad51f9f383f9d6b04bdde2aa696b191e6154fd3b34f33bf626ffae339b` |
| Repository Test Suite | `python3.11 -m pytest tests/test_marketplace.py` | `ALIVE` | `16 passed in 0.07s` |
| HDDL×FOND Closure Episode | `python3.11 domains/repo-closure/verifier/verify_closure_episode.py` | `ALIVE` | `[VALID] Episode lawfully verified and bound for replay` |
| SPARQL Ceilings & Authority | `gates/010_select_ceiling.rq` + `gates/020_mx_authority_ceiling.rq` | `ALIVE` | `SELECT/CONSTRUCT` read-only ceilings admitted; zero ambient DO authority |

## Scoped Standing Notes
- `ALIVE` covers marketplace contract conformance, path safety, deterministic projection, and repository unit tests.
- Does not assert external cloud actuation or live consumer runtime state.
