# ggen-marketplace-10 shim court for azure-terraform-pack template mutation

Standing: UNVERIFIED

## Problem

`/Users/sac/ggen-marketplace/packs/azure-terraform-pack/templates/main.tf.tmpl` is validated by a
plan-only
`mock_provider` harness (see `STANDING.md`), with no proof the harness flips on mutation.
`/Users/sac/ggen-marketplace/scripts/audit_vacuity.py` scans stubs only; no shim-court exists in
this repo.

## Acceptance

`bash /Users/sac/ggen-marketplace/scripts/shim_court_azure_terraform.sh` prints BASELINE, BEFORE,
SHIM, AFTER and a
byte-exact sha256 RESTORE line, exit 0; a corrupted restore on a temp copy exits 1.

## Falsifier

Court exits 0 while the shimmed template still passes the same assertions (VACUOUS GATE).

## Owned files

`/Users/sac/ggen-marketplace/scripts/shim_court_azure_terraform.sh`,
`/Users/sac/ggen-marketplace/ci/courts/shim-azure-terraform.sh`

## Depends-on

None.

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/templates/main.tf.tmpl : 97 lines
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md : 142 lines
- /Users/sac/ggen-marketplace/scripts/audit_vacuity.py : 519 lines
- /Users/sac/ggen-marketplace/ci/courts/ : 93 files, 2809 lines total
- /Users/sac/ggen-marketplace/scripts/shim_court_azure_terraform.sh : NEW (0 lines, to be created;
  est. LOC: ~120; basis: BASELINE/BEFORE/SHIM/AFTER/RESTORE phases plus self-check)
- /Users/sac/ggen-marketplace/ci/courts/shim-azure-terraform.sh : NEW (0 lines, to be created; est.
  LOC: ~15; basis: thin wrapper invoking the script)

## Result

Standing: UNVERIFIED (authored, not executed)

Files: /Users/sac/ggen-marketplace/scripts/shim_court_azure_terraform.sh (~85 LOC),
/Users/sac/ggen-marketplace/ci/courts/shim-azure-terraform.sh (~6 LOC). Shim flips restart_policy;
needs terraform + hashicorp/azurerm 3.117.1 (network); absent => loud [SKIP] exit 3.

Acceptance: `bash /Users/sac/ggen-marketplace/scripts/shim_court_azure_terraform.sh; echo $?` and
`bash /Users/sac/ggen-marketplace/scripts/shim_court_azure_terraform.sh --self-check` (exit 0).

## Repair
- shim_court_azure_terraform.sh: EXIT/INT/TERM trap restores template; AFTER must contain "restart_policy drifted"; self-check SKIPs (exit 3) when baseline not green.
- ci/courts/shim-azure-terraform.sh: rc 3 treated as loud [SKIP]; not aborted by set -e.
- Open: ci/courts.json registration not done (LOW).
- Rerun: bash ci/courts/shim-azure-terraform.sh
