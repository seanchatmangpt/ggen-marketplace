# v26.10.8 — Landing Batch 1 Receipt

Batch of three commits landed in `ggen-marketplace` under the v26.10.8 campaign.
Each row verified via `git show --stat` at addendum time (2026-10-08).

## Commits

| SHA (full) | Subject | Pathspec |
|---|---|---|
| `684d95144dfac4ad222f6202090e136bdfaed145` | refactor(ash-pplan-chaos-pack): relocate violation gates to verify/ (W984ic) | `packs/ash-pplan-chaos-pack/gates/010_harness.rq`, `packs/ash-pplan-chaos-pack/gates/020_invariants.rq`, `packs/ash-pplan-chaos-pack/gates/030_kill_phases.rq`, `packs/ash-pplan-chaos-pack/verify/010_harness.violation.rq`, `packs/ash-pplan-chaos-pack/verify/020_invariants.violation.rq`, `packs/ash-pplan-chaos-pack/verify/030_kill_phases.violation.rq` |
| `99a1b156aee4f75c3fdddefd0d12ad103e166758` | feat(ash-extension-pack): render section-level {:one_of, [...]} enums; scope dead-surface gate to aex:* | `packs/ash-extension-pack/gates/120_spark_dead_surface.rq`, `packs/ash-extension-pack/ontology.ttl`, `packs/ash-extension-pack/templates/extension.ex.tmpl` |
| `199ba7f0f490f6db60e0c63621e541905241a161` | docs(sjira): land rust-wasi-wasmex-pack unified receipt under v26.10.8 campaign | `docs/sjira/v26.10.8/UNIFIED-WASM-PACK.md` |

## Court outputs

- **extension-pack (`99a1b156a`)**: `test_ash_extension_install_template.py` —
  2 passed / 1 skipped, exit 0. Rapper render: 1945 triples. `marketplace.py
  validate`: exit 0.
- **Chaos matrix (batch-wide)**: 4-court Chicago matrix 28/28 passed (12 + 5 + 4 + 7),
  real pm4py, exit 0.
- **Affidavit W803a**: ALIVE — `ggen sync` byte-identical no-op; artifact pin
  `5cc37aea…` match; pin court 3/3; determinism `cmp` IDENTICAL.
- **ferroplan W803b**: ALIVE — `just wasm-gen` byte-identical; `wasm-gen-check` OK;
  `abi_ontology_drift` 17 passed; `copy_drift` 8 passed.

## Open items (disclosed)

- Receipt pins unreachable at `e987f3717`; pin receipts to follow.
- `.tool-versions` uncommitted (untracked in checkout).
- Per-lane receipt docs to follow in later batches.
