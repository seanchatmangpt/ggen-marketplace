# mappings/ — non-RDF public standards, reserved

Per the profile architecture: some of the strongest semantic authorities for XaaS are **not RDF
ontologies** and must not be pretended into `owl:imports`/`prof:isProfileOf` targets. `ggen` maps
them into the graph instead (SPARQL CONSTRUCT projections from their real schemas/specs), and they
are tracked here as mapping targets, not admitted ontology sources.

**Not yet built — every file below is a placeholder for real, disclosed follow-on work:**

- `nist-cloud.ttl` — NIST SP 800-145 (cloud characteristics/service models/deployment models) and
  SP 500-292 (provider/consumer/broker/auditor/carrier reference architecture) as the
  classification authority any RDF IaaS/PaaS/SaaS model should be tested against.
- `tosca.ttl` — TOSCA 2.0's topology/node/relationship/capability/requirement/interface/workflow/
  policy calculus, likely the strongest public falsifier for any custom XaaS
  `Capability`/`Requirement`/`Realization` vocabulary.
- `focus.ttl` — FOCUS 1.4 (FinOps cost/usage/billing terminology) — vendor-neutral, not RDF.
- `opentelemetry.ttl` — OpenTelemetry semantic conventions (cloud providers, CI/CD, FaaS,
  databases, messaging, HTTP, resources/traces/metrics/logs).
- `kubernetes.ttl` — the real Kubernetes OpenAPI object model.
- `terraform.ttl` — real provider resource/configuration schemas (the same discipline
  `azure-terraform-pack`/`gh-terraform-pack` already apply per-provider, generalized).

None of these has been fetched or mapped this session. This directory exists so the reserved slot
is visible in the pack structure, not to claim the mapping work is done.
