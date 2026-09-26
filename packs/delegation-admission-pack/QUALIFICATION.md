# Qualification — delegation-admission-pack 0.2.0

## Executable semantic court

The pack is admitted by violation-row SELECT gates. The canonical anti-vacuity
court is `qualification/verify.py`, which loads `ontology.ttl` plus the exact-stem
PASS or FAIL witness for every gate and executes the gate with rdflib 7.6.0.

For every gate:

```text
PASS witness -> exactly 0 violation rows
FAIL witness -> at least 1 violation row
```

The correspondence itself is fail-closed through `gate-court.toml`: every gate
must have one PASS witness and one FAIL witness, with no orphan witness.

## Gate matrix

| gate | admitted edge | targeted FAIL witness |
|---|---|---|
| 005_artifact_shape | subject, delegation, boundary and authority-scope header present | missing boundary |
| 006_header_cardinality | one distinct value for each projected header predicate | two boundary values |
| 007_numeric_domain | delegation/scope counts are non-negative integers | negative delegation and scope |
| 010_obligations_complete | Explain/Verify/Modify/Account present and exact-subject bound | Account missing |
| 011_obligation_cardinality | exactly one evidence node per obligation | two Explain nodes |
| 015_explain_evidence | PASS + provenance + ontology + rationale | provenance missing |
| 020_independent_verifier | PASS + verifier set + receipt + independent=true | self-verification |
| 030_capacity_bound | every obligation scope covers delegation | Verify scope below delegation |
| 040_modify_probe | PASS + changed requirement + result + replay | changed-requirement id missing |
| 050_account_receipt | PASS + authority + consequence + receipt + replay + standing | receipt missing |

The ontology's shipped example is also clean under all ten gates. Legacy
`qualification/fixtures/pos_admitted.ttl` and
`neg_capacity_and_independence.ttl` remain broad integration fixtures; exact-stem
witnesses are the per-gate anti-vacuity authority.

## Generated AutoFDE transport

`templates/autofde_cases.json.tmpl` is a deterministic projection from admitted RDF
to `generated/delegation-admission-cases.json`:

```text
schema = autofde-lab.delegation-admission-batch/1
ontology facts -> SPARQL rows -> generated batch -> AutoFDE batch court
```

The source gates make every projection-driving header and obligation single-valued,
so one RDF artifact cannot expand into ambiguous Cartesian-product JSON cases.
The generated batch is a projection, never a second source of truth.

## Exact-head workflow

`.github/workflows/delegation-admission-pack.yml` checks out the exact PR head,
installs rdflib 7.6.0, and executes `qualification/verify.py`.

Repository-level courts remain additive:

```bash
python3 scripts/marketplace.py validate
python3 scripts/check_gate_witness_courts.py
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
```

## Standing ceiling

Passing these courts establishes semantic/profile admission for this exact pack
source only. It does not execute consumer systems, grant BRCE DO authority, prove
production behavior, or establish organizational/legal standing.
