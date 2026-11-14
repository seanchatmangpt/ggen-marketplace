# ggen-marketplace-18

Standing: UNVERIFIED

Title: Deploy the registry to ggen-marketplace.fnox.io once fnox.io is ACTIVE

## Problem

`/Users/sac/fnox/docs/setup/fnox-io-domain.md` lists `ggen-marketplace.fnox.io` as an A
record in zone `fnox-io`. Hosting is authored (`/Users/sac/fnox/infra/gcp/edge/main.tf`)
but not deployed, and fnox.io registration is pending ACTIVE. The marketplace repo has
`/Users/sac/ggen-marketplace/k8s/` and `/Users/sac/ggen-marketplace/packaging/` dirs but no recorded
  deploy receipt for this host.

## Acceptance

- Command: `curl -sf -o /dev/null -w "%{http_code}" https://ggen-marketplace.fnox.io/`
- Expected: `200`; a receipt in `/Users/sac/ggen-marketplace/receipts/` records
  registration state ACTIVE, the apply output, and the curl result.

## Falsifier

The curl returns non-200, or the receipt records registration state other than ACTIVE.

## Owned files

- `/Users/sac/ggen-marketplace/k8s/`
- `/Users/sac/ggen-marketplace/receipts/` (hosting receipt)

## Depends-on

- fnox.io registration ACTIVE; fnox edge Terraform apply

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/k8s/ : 8 files, 7712 lines total
- /Users/sac/ggen-marketplace/packaging/ : 3 files, 21 lines total
- /Users/sac/ggen-marketplace/receipts/ : 188 files, 7299 lines total (hosting receipt NEW, est.
  LOC: 40, basis: registration state + apply output + curl result)
- /Users/sac/fnox/docs/setup/fnox-io-domain.md : 128 lines
- /Users/sac/fnox/infra/gcp/edge/main.tf : 126 lines

## Result

Standing: BLOCKED

Authored `/Users/sac/ggen-marketplace/k8s/registry/registry-edge.yaml` (~45 LOC: Deployment,
Service, Ingress for host ggen-marketplace.fnox.io). Not applied. Placeholder nginx image, no
registry content served. Receipt `/Users/sac/ggen-marketplace/receipts/fnox-io-hosting-2026-11-14.md`
stays BLOCKED: fnox.io registration not ACTIVE, edge Terraform not applied, no curl 200 observed.
Acceptance (coordinator): `curl -sf -o /dev/null -w "%{http_code}" https://ggen-marketplace.fnox.io/`
expect 200 AND body must not be the nginx welcome page (grep -v "Welcome to nginx") and must serve registry content (a bare 200 is vacuous with the placeholder); then record ACTIVE + apply output + curl result in the receipt.

## Repair

W10-04 applied audit-W8-04 fixes (MED/LOW wording, deadline poll, placeholder disclosure, falsifier tightened). Rerun the acceptance command in ## Result.
