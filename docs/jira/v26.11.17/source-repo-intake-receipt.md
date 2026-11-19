# v26.11.17 source-repo intake receipt

Standing: PARTIAL

Branch `feat/v26.11.17-source-repo-intake`, base HEAD 1cf20b3f7. Nothing committed.

## Subject

Conversion of ~/fnox, ~/arcus, ~/smalt, ~/ash_pplan, ~/ash_a2a into packs or merges. Lanes were
authored by `ggen-author` agents without a shell; the coordinator ran the checks below.

## Outcome per source repo

| Source | Action | Pack(s) | Class (hypothesis) |
|---|---|---|---|
| fnox | merge + new | `fnox-gcp-broker-pack` (gates 050, 060, 2 fixtures added), `fnox-boundary-payload-pack` 0.1.0 | Profile, Capability |
| arcus | new | `arcus-pack` 0.1.0, `gcp-dialect-pack` 0.1.0 | Capability, Capability |
| smalt | new | `smalt-k8s-pack` 0.1.0 | Profile |
| ash_pplan | new | `ash-pplan-core-pack` 0.1.0 (no pack owned `w3id.org/ash-pplan#`) | Kernel |
| ash_a2a | merge: no change; new umbrella | `a2a-conformance-pack` unchanged, `sa2a-umbrella-pack` 0.1.0 | Evidence, Umbrella |

`gcp-dialect-pack` (Pub/Sub wire laws) is not equivalent to `gcp-terraform-pack` (HCL/IAM):
intent `keep-separate`. Upstream `priv/sa2a_conformance/*` is domain-specific (engine fixtures,
BLAKE3 digests, `sa2a_*` refusal codes): no equivalence to `a2a-conformance-pack` shown.

## Commands and results

- `python3 scripts/marketplace.py validate` (after moving xstate-v5-machine-pack
  `gates/{baselines,shapes}.toml` to `config/` and repointing gates 010/020 defaults, receipt and
  fixture notes): `validated packs=371 ... native_gates=2256`, exit 0. Before that move, the only
  refusals were `GATE_SOURCE_EXTENSION` on those two files (committed in 746acf918, outside this
  intake). Gates 010/020 were not executed after the move: UNVERIFIED.
- `bash scripts/admit-config.sh marketplace.toml ...`: `REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED`
  (unknown field `registry`); `marketplace.toml` is unmodified by this work. `catalog` then
  refused `ACTIVE_SCOPE_ORDER` (two adjacent `trade-reticle-*` entries in
  `marketplace.active.toml` out of order, from 331d416c5-era registration); swapped them.
  After that: `catalog` twice is byte-identical (54390 bytes, active scope of 29 packs; the new
  packs are not in `marketplace.active.toml`), `fingerprint` = sha256:d124faa2...11de7 files=22924.
  The admit-config refusal (`[registry.fnox_io]` in `marketplace.toml`, fnox hosting work) is not
  fixed; `qualify-marketplace.sh` and per-pack qualification remain UNVERIFIED.
- `python3 scripts/qualify_packs.py --pack <name>` (real ggen 26.11.5, two-pass isolated capsule),
  all seven new/extended packs: `qualified packs=1`, rc 0 (fnox-gcp-broker-pack, fnox-boundary-
  payload-pack, arcus-pack, gcp-dialect-pack, smalt-k8s-pack, ash-pplan-core-pack,
  sa2a-umbrella-pack). Fixes needed first: payload template dropped unsupported Tera `| string`
  filter; ash-pplan-core-pack EEx templates ported to Tera (FM-PACK-005) and its projection
  SELECTs moved from `gates/` to `queries/` with the inverted companions promoted to `gates/`
  (FM-PACK-013: any gate row refuses). Qualification proves load + two-pass convergence only;
  generated output vs source (fnox `boundary_models.py`, AshPPlan catalogs) is UNVERIFIED.
- `find <new packs> -type l`: empty.
- pytest `python3.11 -m pytest tests/ scripts/ --continue-on-collection-errors`, same command on
  the base archive (1cf20b3f7) and on the branch:
  base 187 failed / 2001 passed / 116 errors; branch 188 failed / 2007 passed / 109 errors.
  Non-passing ids (FAILED+ERROR): base 303, branch 297. The only ids non-passing on the branch
  and not on base are 6 `tests/test_solution_quickstart.py` tests, which were ERROR (setup) on
  base and FAIL on branch; a re-run shows `REFUSED:SIM_EXITED:sim exited before /healthz`
  (sim process start, not pack content). No test naming a new pack fails. The base and branch runs
  differ in environment (scratch dir vs checkout), so the quickstart delta is not a clean diff.
- `ggen sync`, gate rows for 050/060, qualification: not run. UNVERIFIED.

## Open edges

- fnox `LICENSE` is all-rights-reserved; `fnox-boundary-payload-pack` copies
  `ontology/boundary/payload-shapes.ttl`. Owner confirmation required before it lands.
- `arcus-pack` gates 110/120/130 pass vacuously (classes defined in other arcus packs);
  hard-coded `/Users/sac/cgap` paths; `.go.tmpl` extension.
- `smalt-k8s-pack`: `containers` query groups by an unselected variable; gate 050 hard-codes smalt names.
- `ash-pplan-core-pack`: ~690 lines of the source ontology unread; gates 020/030 return no rows
  without consumer plans.
- Rollback: delete the new pack directories and the `PACK_CLASSES` additions; broker-pack edits are
  additive (gates 050/060, fixtures, `pack.toml` gate list, STANDING note).
