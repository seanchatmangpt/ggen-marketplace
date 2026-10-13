# STRATA-HARDENING-1 — Same-Checkout Lane Partition

> **Status**: IN-FLIGHT 2026-10-13.
> Wave: `STRATA-HARDENING-1` (v26.10.8 campaign, `ggen-marketplace`).
> Convention: `docs/sjira/v26.10.8/_INTEGRATION_RUNBOOK.md`.

## Rules

- One canonical checkout (`/Users/sac/ggen-marketplace`), no worktrees, no clones.
- Lanes own a disjoint pathspec; all work stays inside it.
- **Lanes never run git.** No `git add`/`commit`/`stash`/state commands from any lane.
- **Coordinator (L0) owns all commits**, git transitions, and the sync schedule.
- Shared seams are resolved at integration by the coordinator, not by lanes.
- Commit messages via `git commit -F <file>` at integration time.

## Lane table

| Lane | Pathspec (owned) | Status |
|---|---|---|
| L0 (coordinator) | git transitions, commits, sync schedule, namespace migration, integration | IN-FLIGHT 2026-10-13 |
| L1 | `packs/strata-temprun-pack/**` | IN-FLIGHT 2026-10-13 |
| L2 | `packs/strata-signer-pack/**` | IN-FLIGHT 2026-10-13 |
| L3 | `packs/strata-stratus-pack/**` | IN-FLIGHT 2026-10-13 |
| L4 | `packs/strata-cas-pack/**` | IN-FLIGHT 2026-10-13 |
| L5 | `packs/strata-valve-pack/**` | IN-FLIGHT 2026-10-13 |
| L6 | `packs/strata-pn64-pack/**` | IN-FLIGHT 2026-10-13 |
| L7 | `packs/strata-protocol-pack/**` | IN-FLIGHT 2026-10-13 |
| L8 | `tests/test_strata_family_pack.py` | IN-FLIGHT 2026-10-13 |
| L9 | `tests/test_strata_corpus.py` | IN-FLIGHT 2026-10-13 |
| L10 | `tests/test_strata_firelaw.py`, `tests/test_strata_valve_runtime.py` | IN-FLIGHT 2026-10-13 |
| L11 | `scripts/qualify_packs_r18.py`, `ci/courts.json`, `ci/courts/strata-packs-court.sh` | IN-FLIGHT 2026-10-13 |
| L12 | `lifecycle.toml` | IN-FLIGHT 2026-10-13 |
| L13 | `README.md`, `packs/strata-*/README.md` | IN-FLIGHT 2026-10-13 |
| L14 | `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/` strata files, `docs/book.ttl` | IN-FLIGHT 2026-10-13 |
| L15 | `scripts/marketplace.py`, `docs/reference/pack-classes.md` | IN-FLIGHT 2026-10-13 |
| L16 | `docs/sjira/v26.10.8` strata receipts | IN-FLIGHT 2026-10-13 |
| L17 | `docs/sjira/v26.10.8` strata receipts | IN-FLIGHT 2026-10-13 |
| L18 | `docs/sjira/v26.10.8` strata receipts | IN-FLIGHT 2026-10-13 |
| L19 | `docs/sjira/v26.10.8` strata receipts (this file: `_STRATA_LANES.md`) | IN-FLIGHT 2026-10-13 |

20 execution lanes (L1–L19) + coordinator L0. Per-lane receipt docs land under
`docs/sjira/v26.10.8/` in later batches; landing addenda are recorded in the
runbook, verified on disk at addendum time.
