# Strata Ledger Pack — Template Baseline (Hand Law)

The templates of this pack, **as of the git SHA and date below, are the law**.
Any post-baseline edit to `templates/*.tera` without an accompanying freeze
witness (`.ggen/freeze/strata-ledger-pack/*.blake3` refreshed via
`ggen sync run`) is **unauthorized drift**.

## Baseline identity

- Repo: `ggen-marketplace`
- Baseline git SHA: `5842ccb5be92bb767c308efb196d12fde7dba78a`
- Baseline date: 2026-10-13 (post-Oct-10 baseline; 4 template commits after
  the Oct-10 baseline had accumulated with in-repo `generated/` copies
  unwitnessed and zero freeze declarations — this file closes that gap)

## Pinned template blob SHAs (git ls-tree HEAD)

| template | blob sha |
|---|---|
| `templates/kernel_laws.rs.tera` | `231d1ed28a5fe38b3d9bb0f588b1f280fb90a002` |
| `templates/ledger_consts.rs.tera` | `8365cb2314dc75d5ce206d3a64d5ce098a2fef4e` |
| `templates/ledger_state.rs.tera` | `2d1a8773feb6747438a902fd552e12c61be941d7` |

## Freeze policy

All three templates now declare `freeze_policy: checksum` with
`freeze_slots_dir: .ggen/freeze/strata-ledger-pack` (pattern per
`packs/aoq-pack/templates/status_band_rs.tmpl:4-5`). Regeneration is skipped
rather than silently clobbering hand-edited generated output; witnesses are
committed in-repo.

## Drift law

1. Edit a template → run `ggen sync run` → refresh witnesses → single commit
   containing template + generated + witness diff.
2. A template blob sha differing from the table above with no witness refresh
   in the same history is unauthorized drift; refuse regeneration from it.
