# delegation-admission-pack

A reusable semantic profile for evidence-bounded delegation, extracted from the
Explain / Verify / Modify / Account obligations in arXiv:2609.29473 and generalized
to the Chatman ecosystem admission boundary.

## Law

```text
AdmissionCapacity =
  min(Explain.scopeUnits,
      Verify.scopeUnits,
      Modify.scopeUnits,
      Account.scopeUnits)

DelegationArtifact.delegationUnits <= AdmissionCapacity
```

The conjunction matters: strength in one evidence channel cannot manufacture
standing in another.

## Gates

- `010_obligations_complete.rq` — all four obligations exist and are bound to
  the exact artifact subject.
- `015_explain_evidence.rq` — Explain PASS with provenance, ontology, rationale.
- `020_independent_verifier.rq` — Verify PASS with verifier set, receipt, and
  `independent=true`.
- `030_capacity_bound.rq` — every obligation has `scopeUnits >= delegationUnits`.
- `040_modify_probe.rq` — Modify PASS includes changed-requirement, result, replay.
- `050_account_receipt.rq` — Account PASS includes authority, consequence,
  receipt, replay, and standing.

Queries use violation-row semantics: **zero rows = admitted by that gate; any row
= refusal**.

## Authority boundary

This pack is declarative. It can refuse a candidate graph; it cannot actuate work,
grant BRCE authority, establish production standing, or infer organizational/legal
responsibility. A consumer may project these facts into SA2A, GymAct, sJira, or
another control plane, but DO remains external.

## Falsifier fixtures

`qualification/fixtures/pos_admitted.ttl` should produce zero rows for all gates.

`qualification/fixtures/neg_capacity_and_independence.ttl` deliberately combines
two violations: a non-independent verifier and delegation beyond one or more
evidence scopes. Gates 020 and 030 must return rows.
