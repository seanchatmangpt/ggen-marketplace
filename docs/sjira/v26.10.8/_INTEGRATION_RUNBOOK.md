# v26.10.8 Campaign — Integration Runbook

> **Status**: runbook seed for the v26.10.8 campaign in `ggen-marketplace`.
> Shape follows the house format (`xaas/docs/sjira/v26.10.7/_INTEGRATION_RUNBOOK.md`):
> conventions, lane table, landing addenda recording actually-landed work verified
> per-commit via `git log`/`git show --stat`.

## Conventions

- **Lane partition**: each lane owns a disjoint pathspec under `packs/` (and its own
  `docs/sjira/v26.10.8/` receipts). Lanes never `git add` bare — explicit pathspec
  only; commit messages via `git commit -F <file>`. Coordinator owns transitions.
- **Receipts under the campaign dir**: per-lane receipts, landing batches, and this
  runbook all live in `docs/sjira/v26.10.8/`.
- **Courts are Chicago-style**: real ggen sync / real subprocess courts on real pack
  surfaces; assert on final state (file bytes, triple counts, validator exits), not
  on call counts. No mocks.
- **Landing addenda**: each wave appends an addendum below with SHA, paths, court
  result, receipt path — verified on disk at addendum time, not recalled from memory.

## Lane table

| Lane | Pathspec (owned) | Work |
|---|---|---|
| wasmex/docs | `packs/rust-wasi-wasmex-pack/` receipts, `docs/sjira/v26.10.8/UNIFIED-WASM-PACK.md` | unified WASM pack receipt (landed, `199ba7f0f`) |
| chaos-pack | `packs/ash-pplan-chaos-pack/` | violation-gate relocation to `verify/` (landed, `684d95144`) |
| extension-pack | `packs/ash-extension-pack/`, `packs/ash-extension-pack/tests/` | section-level `{:one_of, ...}` + SchemaField superclass + gate scope (landed, `99a1b156a`) |
| runbook (this lane) | `docs/sjira/v26.10.8/` | this runbook + `LANDING-BATCH-1.md` |

## Landing addendum — 2026-10-08 (wave 1)

Verified per-commit in `/Users/sac/ggen-marketplace` (`git show --stat` per SHA,
re-run at addendum time; HEAD at `68c351ed0`). Each landing: SHA, paths, court
result, receipt path. Full batch detail in `LANDING-BATCH-1.md`.

| SHA | Landing | Paths | Court result | Receipt |
|---|---|---|---|---|
| `684d95144` | chaos-pack W984ic relocation of violation gates to `verify/` | `packs/ash-pplan-chaos-pack/gates/010_harness.rq`, `020_invariants.rq`, `030_kill_phases.rq`, `verify/010_harness.violation.rq`, `020_invariants.violation.rq`, `030_kill_phases.violation.rq` (6 files, +76/−21) | gate relocation; courts below (4-court matrix) | `LANDING-BATCH-1.md` |
| `99a1b156a` | extension-pack section-level `{:one_of, [...]}` enums + `SchemaField` superclass + dead-surface gate scoped to `aex:*` | `packs/ash-extension-pack/templates/extension.ex.tmpl`, `packs/ash-extension-pack/ontology.ttl`, `packs/ash-extension-pack/gates/120_spark_dead_surface.rq` (3 files, +36/−2) | `test_ash_extension_install_template.py` 2 passed / 1 skipped, exit 0; rapper renders 1945 triples; `marketplace.py validate` exit 0 | `LANDING-BATCH-1.md` |
| `199ba7f0f` | rust-wasi-wasmex-pack unified receipt relocation under the campaign dir | `docs/sjira/v26.10.8/UNIFIED-WASM-PACK.md` (+80) | docs-only | `UNIFIED-WASM-PACK.md` |

### Witnessed facts (this wave)

- **4-court Chicago matrix: 28/28 passed** (12 + 5 + 4 + 7), real pm4py, exit 0.
- **Affidavit W803a ALIVE** — `ggen sync` byte-identical no-op; artifact pin
  `5cc37aea…` match; pin court 3/3; determinism `cmp` IDENTICAL.
- **ferroplan W803b ALIVE** — `just wasm-gen` byte-identical; `wasm-gen-check` OK;
  `abi_ontology_drift` 17 passed; `copy_drift` 8 passed.

### Open items (disclosed, not landed this wave)

- **Receipt pins unreachable at `e987f3717`** — disclosed; pin receipts still to follow.
- **`.tool-versions` uncommitted** — present as untracked in the checkout, not landed.
- **Lane receipts to follow** — per-lane receipt docs land in later batches.
