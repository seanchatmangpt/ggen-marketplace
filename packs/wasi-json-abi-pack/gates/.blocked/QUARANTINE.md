# Quarantine — 2026-10-01, lane BX (spark-closure-courts)

Moved here from `gates/` because `scripts/marketplace.py` refuses every
non-`.rq`/`.py` file in a pack's `gates/` directory
(`GATE_SOURCE_SUFFIXES = frozenset({".rq", ".py"})` at
`scripts/marketplace.py:41`), and this directory held:

- `README.md` — prose index of the three verifier scripts
- `wasm_zero_imports.sh` — import-policy + required-export gate
- `wasm_artifact_pin_check.sh` — artifact pin verification gate
- `wasm_abi_doc_drift.sh` — ABI-doc vs module drift court

These are working, previously-witnessed POSIX-shell gates (ALIVE standing is
recorded inside the README), not broken work: the marketplace admission gate
simply does not admit `.sh` or `.md` as gate sources. Sibling packs'
`gates/` directories contain only `.rq` files, so the repo convention is
`.rq`/`.py` only.

Restore path (either):
- port the three scripts to `.py` verifier gates, or
- widen `GATE_SOURCE_SUFFIXES` in `scripts/marketplace.py` to admit `.sh`
  plus an explicit README allowance.

The scripts remain directly executable in place:
`./wasm_zero_imports.sh [--allow-wasi] ... FILE.wasm` etc.
