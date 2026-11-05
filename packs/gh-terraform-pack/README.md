# gh-terraform-pack

Terraform GitHub-management pack: projects HCL for managing GitHub repos/teams/
branch protection/secrets/webhooks/org security, plus a `gh`-CLI shell-script
library, from RDF individuals (`ghtf:` / `ghcli:`) whose bodies are verbatim
HCL/bash modeled on real repos. Templates echo stored literals; the ontology is
the source of truth — never edit generated files.

## What it projects

- `infra/terraform/github/` — versions.tf (provider pin), backend.tf/providers.tf
  (S3+DynamoDB+KMS, GCS, or Terraform Cloud remote per `ghtf:BackendConfig`),
  repository.tf, branch-protection.tf, teams.tf, secrets.tf, webhooks.tf,
  org-security.tf, orgs/<alias>/{repos,backend,providers}.tf (multi-org),
  outputs.tf, variables.tf, README.md
- `docs/gh-terraform/` — resource/data-source catalogs, fleet-model, policy-gate
  and L5-status docs
- `scripts/gh/` — `gh`-CLI shell library (PRs, issues, runs, releases, drift,
  fleet census, accept/apply/verify with drift injection), driven by
  `ghcli:Command` individuals
- `.github/workflows/` drift workflow (via `tcps_drift_workflow_yml.tmpl`)

## Consumer contract

Derived mechanically from the pack's own template provider blocks / HCL bodies:

- **terraform >= 1.5** — to `init`/`fmt`/`validate` the projected `*.tf`
- **provider `integrations/github` v5.41.0** — pinned by the
  `ghtf:RequiredProviders` HCL body emitted into `versions.tf`
- **`gh` CLI + `jq`** — required by the `scripts/gh/*.sh` shell library
- **Backend credentials (plan/apply time)** — s3 kind needs AWS creds (bucket +
  DynamoDB lock + KMS key); gcs kind needs GCS creds; remote kind needs
  Terraform Cloud token. Credentials only — no `aws`/`google` provider block is
  emitted.

Individuals (`ghtf:ManagedRepo`, `ghtf:OrgTenant`, `ghtf:BackendConfig`,
`ghcli:Command`, ...) ship inside the pack ontology; a consumer composes the
pack by path in `ggen.toml` `[packs]` and may overlay/extend individuals in its
own ontology. The three gates (`gates/010_required.rq` structural completeness,
`020_fleet.rq` composition law, `030_policy.rq` policy-as-code refusal:
critical-tier review minimums, deprecated-without-successor, SSO-required
webhook auth) run over the merged graph during `ggen sync run`.

## Qualification court (2026-11-05, G18)

Scratch consumer at `/tmp` (`[project]` + `[ontology]` + `[packs]` +
`[templates]` ggen.toml), `ggen sync run --skip-ea-admission` → 20 `.tf` files
under `infra/terraform/github/`. Court tier reached:

- `terraform fmt -check -recursive` → exit 0 (all 20 `.tf` files fmt-clean)
- `terraform init -backend=false` → exit 0 (resolved and downloaded
  integrations/github at the pinned 5.41.0)
- `terraform validate` → **BLOCKED in this environment**: init downloads and
  code-signs the provider binary, then `validate` times out "waiting for plugin
  to start" (sandbox blocks the plugin's localhost gRPC handshake). Recorded
  honestly; not a pack defect.
- Anti-vacuity flip: an unbalanced-`{` shim injected into the
  `ghtf:MainBranchProtection` `hclBody` re-synced into a fresh consumer made
  `terraform fmt -check -recursive` exit 2 (`Unclosed configuration block`) —
  the court reads the pack ontology, not a canned pass. Shim restored
  byte-exact (sha256 verified).

## Pre-existing defect fixed by this refactor

Before G18, the org-security projection declared
`github_branch_protection "main"` colliding with `branch-protection.tf`'s
`github_branch_protection "main"` (duplicate resource address → `terraform
init` exit 1), and the same body was not `terraform fmt`-clean. Fixed in the
ontology (renamed to `github_branch_protection "org_main"` + fmt alignment);
court now passes `init` + `fmt -check`.
