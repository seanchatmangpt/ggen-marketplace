# fnox-gcp-broker-pack

Tier-3 GCP broker topology for fnox (ARD v26.11.16) as ontology-backed capital. The graph is the
source; `infra/gcp/broker/*.tf` and `topology.md` are projections.

## Layout

```text
pack.toml                      identity (+ [metadata], [capabilities], [validation].gates)
ggen.toml                      frontmatter-schema generation contract: [project] name, ontology source, templates dir (no version, no [validation] — both are declarative-schema markers under ggen 26.11.5)
ontology/fnox-gcp-broker.ttl   gtf: (from gcp-terraform-pack) + fgb: broker vocabulary and instances
shapes/fgb.shacl.ttl           SHACL twin of the gates (pyshacl)
gates/0NN_*.rq                 SPARQL gates: any row = refusal
templates/*.tf.tera            Terraform projections (one output file each)
templates/topology.md.tera     projection receipt
tests/mutations/*.ttl          falsifier fixtures (union with the ontology -> gates must refuse)
```

## What the ontology declares

- `fgb:topic_pplan_actuation` — Pub/Sub topic `pplan-actuation`, `fgb:messageOrdering true`,
  `fgb:dedupAttribute "durable_intent_token"`.
- `fgb:sub_platform_signal` — push subscription with OIDC token (`fgb:sa_push`) to
  `https://platform.fnox.io/gcp/signal`.
- `fgb:bucket_intake_pdfs` -> `fgb:trigger_intake_finalize` (Eventarc `object.v1.finalized`) ->
  `fgb:svc_intake` (Document AI + Vertex `gemini-2.5-flash`, provenance `pdf_ingest`).
- `fgb:worker_{twilio,sendgrid,stripe}` — one Cloud Run egress worker per vendor, each
  `fgb:accessesSecret` exactly one `fgb:Secret` with `roles/secretmanager.secretAccessor`.
- `fgb:gateway_webhooks` — API Gateway ingress routes for inbound vendor webhooks.
- `fgb:wi_platform` — Workload Identity binding for `fgb:sa_platform`.
- `fgb:constraint_zero_static_key` — forbids `google_service_account_key`; rendered as the org policy
  `constraints/iam.disableServiceAccountKeyCreation`.

## Refusals

| gate | refuses | falsifier |
|---|---|---|
| `gates/010_topic_dedup.rq` | topic without ordering / `durable_intent_token` dedup | `tests/mutations/topic_no_dedup.ttl` |
| `gates/020_worker_single_secret.rq` | egress worker with secret cardinality != 1 | `tests/mutations/worker_two_secrets.ttl` |
| `gates/030_zero_static_key.rq` | any `google_service_account_key` / `fgb:StaticKey` | `tests/mutations/static_key.ttl` |
| `gates/040_push_oidc.rq` | push without OIDC/https/topic; service without SA; bucket without intake trigger | `tests/mutations/push_no_oidc.ttl` |

Every falsifier is an additive sibling of the same declared class (a union court cannot delete
triples), so each fixture adds one mutant node and the gate must name it in >= 1 row while the
other three gates stay at 0 rows.

## Court

Validation commands and the mutation court are listed in the fnox receipt
`docs/jira/v26.11.16/receipts/L19-gcp-broker-pack.md`; `STANDING.md` here moves only from that
receipt's exit codes.

## Authority

Generated Terraform has no DO authority. `terraform apply` against a real project is a separately
admitted transition (marketplace AGENTS.md: SELECT -> CONSTRUCT -> DO).
