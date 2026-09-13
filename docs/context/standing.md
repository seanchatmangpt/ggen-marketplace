# Exact-Head Standing: ggen-marketplace

## Current Head State
- **Base Commit**: `00f14b1b966900aa129f16a2e51727ef697823ec`
- **Active Branch**: `docs/rewrite-agents-contract`
- **Timestamp**: `2026-09-13T08:34:00-07:00`
- **Overall Standing**: `ALIVE` (admitted local validation and tests passed)

## Validation Matrix
| Acceptance Boundary | Command | Status | Output Witness |
|---|---|---|---|
| Pack & Diátaxis Schema | `python3.11 scripts/marketplace.py validate` | `ALIVE` | `packs=312 manifests=312 ontologies=463 templates=1800 diataxis=20` |
| Catalog Determinism | `cmp <(python3.11 scripts/marketplace.py catalog) <(...)` | `ALIVE` | Byte-for-byte identical projection |
| Corpus Fingerprint | `python3.11 scripts/marketplace.py fingerprint` | `ALIVE` | `sha256:920b3868d75bdf0bed6abcb1422d29f7e785d945c43d11af6e0f455bfd4299cf` |
| Repository Test Suite | `python3.11 -m pytest tests/test_marketplace.py` | `ALIVE` | `16 passed in 0.09s` |

## Scoped Standing Notes
- `ALIVE` covers marketplace contract conformance, path safety, deterministic projection, and repository unit tests.
- Does not assert external cloud actuation or live consumer runtime state.
