# FROZEN-ASOF 2026-11-04

Status note, not a freeze witness. There is no `.ggen/freeze` path
convention in this repo (packs carry only `.ggen/keys/` signing keys),
so no freeze pin is minted here.

The templates in this pack are **hand-law**: they drifted post-baseline
with no pin. Treat the current templates as the standing surface; any
future change must land with its own receipt, not under a frozen pin
that does not exist.

Baseline references:
- pack landing wave: `docs/sjira/v26.10.8/` (strata hardening wave)
- repo fingerprint as-of 2026-10-13:
  `sha256:0c3f12e1a9ce709e6862ece7541e7b85f3e2d0173f878bd0f4fe5cd9d2118ebe`
  (`python3 scripts/marketplace.py fingerprint`, STRATA-DRIFT-NOTES.md
  addendum)
