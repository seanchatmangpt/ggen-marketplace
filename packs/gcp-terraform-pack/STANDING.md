# gcp-terraform-pack Standing

Standing: UNVERIFIED

Authored, not executed. See docs/DIVERGENCES.md.

## Repair (W9-08)

Standing: BLOCKED. No ggen manifest or template binding exists, so gates/*.rq never run and
`ggen sync run` + diff against infra/gcp/iam/main.tf is unsatisfiable. Body-line ordering is
unmodeled (see ontology.ttl gtf:hcl). Inventory is incomplete for edge/cloudrun/budget/gpu.
gates/020 is vacuous while all arcusStatus values are UNVERIFIED. iam emission omits
locals.runtime_sas and would fail terraform validate.
