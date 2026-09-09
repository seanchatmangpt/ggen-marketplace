# frontier-release-factory-pack

This pack is the reusable semantic/manufacturing layer for **Frontier Release Inversion**:

```text
external release -> observed claims -> bounded opportunity -> benchmark -> working-backwards release
                 -> implementation -> exact-subject evidence -> earned release
```

It deliberately does **not** own RSS polling, GitHub repository creation, deployment, or publication authority. Those are consumer/runtime concerns and must remain behind their own authority boundaries.

## Canonical source

- `ontology.ttl` defines source releases, observed claims, opportunities, benchmarks, working-backwards releases, evidence receipts, earned releases, and the ordered factory stages.
- `gates/010_required_opportunity_fields.rq` refuses an opportunity that lacks its response mode, target repository, required capability, or benchmark.
- `templates/working-backwards-press-release.md.tmpl` projects the target promise before implementation.
- `templates/acceptance-contract.toml.tmpl` projects the machine acceptance/falsifier contract.
- `templates/earned-press-release.md.tmpl` projects only evidence-bearing launch claims after execution.

Consumer-generated files are projections and must not be corrected here. Repair the ontology/template/gate source, then regenerate.

## Required consumer bindings

A consumer generation contract supplies bindings for the selected opportunity and benchmark, including:

```text
release_title
source_url
publisher
observed_claim
reported_metric
reported_cost
customer_problem
response_mode
target_repository
required_capability
benchmark_id
acceptance_predicate
falsifier
launch_claim
```

The earned-release projection additionally requires:

```text
verified_claim
subject_identity
verifier_identity
evidence_ref
replay_ref
standing
```

## Standing fence

Pack validation proves only marketplace structure. A real consumer execution with the matching `ggen` runtime is required before claiming these projections execute correctly. An earned press release must never be generated from source-release prose or a working-backwards draft without independently verified exact-subject evidence.
