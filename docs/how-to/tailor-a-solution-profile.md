# Tailor a solution from a deployment profile

Use this guide when you have an admitted profile (from
`how-to/ingest-a-profile.md`) and need a new deployable AAIF solution
directory tailored to it.

## Named inputs
- `examples/profiles/{enterprise,team}.json` — admitted profile templates;
  copy the one closest to your customer shape.
- `packs/aaif-profile-tailoring-pack/ontology.ttl` — canonical closed
  enumeration of every deployment enum value.
- `solutions/enterprise-aaif/` — the reference solution to clone.
- `scripts/profile_intake.py`, `scripts/deploy_aaif_solution.py` — tooling.

## Steps
### 1. Copy and edit the profile
```bash
cp examples/profiles/enterprise.json examples/profiles/acme.json
```

Edit the `deployment` block. Enum-valued fields accept only values
enumerated in `packs/aaif-profile-tailoring-pack/ontology.ttl` — a closed
set; any other value projects `UNSUPPORTED`.

Shortcut: `python3 scripts/run_solution_quickstart.py --profile team`
exercises the alternate enum corner end-to-end without manual capsule work.

### 2. Admit the profile with a lock
```bash
python3 scripts/profile_intake.py examples/profiles/acme.json \
  --out solutions/acme-aaif --lock
```
Writes `profile.json`, `profile.ttl`, `profile.lock.json` (sha256 fingerprint
over the normalized inputs).

### 3. Create the solution directory
```bash
cp -R solutions/enterprise-aaif/ solutions/<slug>-aaif/
```
Update in the copy:
- `ggen.toml` — set `[project] name = "<slug>-aaif"` (leave `[[packs]]`
  paths and `[ontology]` intact).
- `ontology.ttl` — update deployment-profile individuals to your chosen
  enum values from the tailoring ontology.

Re-admit so the lock covers the new inputs:
```bash
python3 scripts/profile_intake.py solutions/<slug>-aaif/profile.json \
  --out solutions/<slug>-aaif --lock
```
Digests: `scripts/deploy_aaif_solution.py` validates them via
`check_lock_digests` — profile digest plus per-pack content hashes must
match the solution inputs or the deployer refuses with exit 9
(`REFUSED:PROFILE_DIGEST_DRIFT`).

### 4. Deploy to the kind rail
```bash
python3 scripts/deploy_aaif_solution.py \
  --solution solutions/<slug>-aaif --out dist/<slug> --target kind
```

Expected consequence: a `dist/` bundle — rendered templates,
`solution.json` with recomputed digests, receipts under `receipts/`.
Tests exercise the same boundary via `tests/test_aaif_deployment_court.py`.

## Falsifiers
- Edit a solution input after locking without re-locking -> exit 9
  (`REFUSED:PROFILE_DIGEST_DRIFT`).
- Enum value absent from `packs/aaif-profile-tailoring-pack/ontology.ttl`
  -> gate refusal (`UNSUPPORTED` projection, typed exit).

## Authority ceiling

`--target kind` is `PARTIAL_ALIVE` (local sim only). Real GCP procurement
via `--target gke` is `BLOCKED` (vendor onboarding). Never present
kind-rail receipts as GCP evidence.

## Rollback

All artifacts are derived: delete `solutions/<slug>-aaif/`, `dist/<slug>`,
and any `receipts/` entries minted by the run. The quickstart
(`scripts/run_solution_quickstart.py`) detects committed-lock drift
(`REFUSED:LOCK_DRIFT`) and requires `--accept-drift` to regenerate
the lock deliberately. `solutions/enterprise-aaif/`
and `examples/profiles/` are never modified.
