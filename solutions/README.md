# Solutions

Consumer scaffolds: a solution dir pins two local packs against one consumer graph and a content
lock; `scripts/deploy_aaif_solution.py` manufactures `dist/` (fail-closed).

## Anatomy: `solutions/enterprise-aaif/`

- `ggen.toml` — pins both packs by relative path (`../../packs/aaif-vanilla-pack`,
  `../../packs/aaif-profile-tailoring-pack`); `[[generation.rules]]` project the tailoring pack's
  SPARQL queries (`queries/10-profile.rq`, `queries/20-profile-summary.rq`) through local
  `templates/*.tmpl` into `dist/profile/`.
- `ontology.ttl` — one graph satisfying the UNION of both pack contracts: `aaif:Agent` facts for
  aaif-vanilla-pack, DeploymentProfile facts for aaif-profile-tailoring-pack. The pack ontology is
  authoritative; local enum individuals exist only to keep this standalone graph closed.
- `profile.json` — the A2A agent-card payload mirrored from the graph; `solution.json` — lock
  (`aaif-solution-lock/v1`): `profile_sha256` + `packs[] {name, path, content_hash}`.

## Lock fields (executable definition: `input_folds` in scripts/deploy_aaif_solution.py)

- `profile_sha256` — `marketplace.fingerprint_paths` fold over every file under the solution dir
  EXCLUDING `solution.json`, any `dist/` path, and ggen runtime dirs (`.ggen`, `.ggen-v2`,
  `.clap-noun-verb`).
- `content_hash` (`sha256:<hex>`) — same fold over each pack tree (path from `packs[].path`); the
  quickstart capsule copies packs ignoring `.clap-noun-verb`, `__pycache__`, and dot-dirs first.
- The lock covers INPUTS only; `dist/` is covered by the consequence digest/receipt `graph_hash`.

## Regeneration (packs changed? recompute, never hand-edit)

`ggen sync run` does NOT update the lock. Any input/pack change makes the deployer refuse
`REFUSED:PROFILE_DIGEST_DRIFT` (exit 9) pre-manufacture, or `REFUSED:INPUT_DRIFT_DURING_MANUFACTURE`
(exit 9, quarantines `dist/`) post-manufacture.
Recompute via `recompute_lock()` in `scripts/run_solution_quickstart.py`; never hand-edit
`solution.json`.

## Profiles

`run_solution_quickstart.py --profile {enterprise,team}` — same scaffold. `team` re-tailors
`ontology.ttl`/`profile.json` in a temp capsule (namespace `team-aaif`, 1 replica, CMEK NONE,
STANDARD FinOps, SIEM_NONE, PQC_NONE), then recomputes the lock before deploy. Values must stay
in the pack ontology's closed enums (`gates/010_profile_enum_closure.rq`); repo files untouched.
