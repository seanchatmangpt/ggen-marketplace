# AAIF deployer contract

Contract for `scripts/deploy_aaif_solution.py`, the single ordered entry
point from an intake profile to an actuation plan. This document is the
reference for the flow, the refusal ladder, the receipt chain rule, and the
typed standings.

Standing scope: the contract's sim/kind rail is `PARTIAL_ALIVE`. Real GCP
procurement and real GKE actuation are `BLOCKED` (vendor onboarding).

## Inputs and outputs

- Input: a solution directory produced by `scripts/profile_intake.py`
  (normalized `profile.json`, `profile.ttl`, optional `profile.lock.json`).
- Commerce configuration: `monetization.toml` at the repository root,
  loaded by `scripts/marketplace_monetization.py`.
- Outputs: a manufactured dist tree (`--out`) with `actuation_plan.json`
  written inside it, and a paid-delivery receipt under
  `<receipts-dir>/paid-delivery/`.

## Command-line interface

The observed `argparse` surface of `scripts/deploy_aaif_solution.py`:

```bash
python3 scripts/deploy_aaif_solution.py \
  --solution <solution-dir> \
  --out <dist-dir> \
  [--target kind|gke] \
  [--config monetization.toml] \
  [--entitlement-id <id>] \
  [--region <region>] \
  [--project <gcloud-project>] \
  [--receipts-dir <dir>] \
  [--actuate] \
  [--timeout-seconds <float>]
```

`--solution` and `--out` are required; `--target` defaults to `kind`;
`--config` defaults to `<repo>/monetization.toml`; `--receipts-dir`
defaults to `<repo>/receipts`; `--entitlement-id` defaults to the
solution slug (the `--solution` basename); `--region` defaults to the
`AAIF_TARGET_REGION` environment variable. The gke rail additionally
requires `gcloud` and `kubectl` on PATH and a matching gcloud project
(the `--project` value, else `GCP_PROJECT`).

## The 10-step flow

1. **Monetization admission** — load and validate `monetization.toml`
   (closed key set; exactly one billing authority).
2. **Profile digest check** — recompute the intake fingerprint; refuse on
   mismatch with `profile.lock.json`.
3. **Entitlement gate** — call the entitlement seam
   (`scripts/entitlement.py` `decide()`) and require an active entitlement
   *before* any manufacture. Pay-before-manufacture is an invariant: no
   `dist/` may exist when this step refuses.
4. **Manufacture** — run `ggen sync` over the solution's two-pack lock.
5. **Pack gates re-run** — re-evaluate the pack gates against the
   manufactured output, before any write is admitted.
6. **Namespace-scope check** — the plan may contain the two Namespace
   objects; ClusterRoles, webhook configurations, and CRDs are refused.
7. **Consequence digest** — fingerprint the manufactured consequence tree.
8. **Paid-delivery receipt** — append to the receipt chain.
9. **Actuation plan** — emit `actuation_plan.json`.
10. **Optional actuation** — with `--actuate`, apply the plan via the
    customer's own `gcloud`/`kubectl`; without it, the run stops after the
    plan is emitted.

## Refusal and exit-code table

Quoted from the module docstring and `Refused` call sites of
`scripts/deploy_aaif_solution.py`. Deployer-emitted refusals print as
`REFUSED:<CODE>:<detail>`; entitlement sub-results pass through under
their own names.

| Exit | Class |
| --- | --- |
| 2 | Config / validation (python gate, lock, `dist/` exists, budget) |
| 3 | Entitlement endpoint unreachable |
| 4 | Entitlement not active / not found |
| 5 | Invalid entitlement response |
| 6 | Monetization registry invalid (schema, keys, cardinality) |
| 7 | ggen runtime not found |
| 8 | Gate / scope violation (gate row, cluster-scoped manifest, residency) |
| 9 | Digest drift (lock drift, non-monotonic grant) |
| 10 | gcloud/kubectl tooling or project mismatch |
| 12 | ggen sync actuation failure |
| 13 | Paid-delivery receipt write/read failure |

Typed refusal codes per exit, quoted from the `Refused` call sites:

- exit 2: `REFUSED:PYTHON_3_11_REQUIRED`,
  `REFUSED:SOLUTION_LOCK_MISSING`, `REFUSED:SOLUTION_LOCK_INVALID`,
  `REFUSED:DIST_ALREADY_EXISTS`, `REFUSED:BUDGET_EXCEEDED`
- exit 3: `REFUSED_ENTITLEMENT_UNREACHABLE`,
  `REFUSED_ENTITLEMENT_PROVIDER_UNREACHABLE`,
  `REFUSED_ENTITLEMENT_ENDPOINT_NOT_GOOGLE`
- exit 4: `REFUSED_ENTITLEMENT_NOT_ACTIVE`,
  `REFUSED_ENTITLEMENT_NOT_FOUND`
- exit 5: `REFUSED:ENTITLEMENT_INVALID_RESPONSE:<detail>`
  (including the `REFUSED_BACKEND_UNKNOWN` detail)
- exit 6: `REFUSED:MONETIZATION_REGISTRY_INVALID:<problems>`,
  `REFUSED_BILLING_AUTHORITY_CARDINALITY`
- exit 7: `REFUSED:GGEN_NOT_FOUND`
- exit 8: `REFUSED:SOLUTION_GATE_VIOLATION`,
  `REFUSED:MANIFEST_CLUSTER_SCOPED`, `REFUSED:MANIFEST_UNPARSEABLE`,
  `REFUSED:YAML_PARSER_UNAVAILABLE`, `REFUSED:DATA_RESIDENCY_VIOLATION`,
  `REFUSED:RESIDENCY_CONFLICT`
- exit 9: `REFUSED:PROFILE_DIGEST_DRIFT`, `REFUSED:NON_MONOTONIC_GRANT`,
  `REFUSED:INPUT_DRIFT_DURING_MANUFACTURE`
- exit 10: `REFUSED:GKE_TOOLING_MISSING`, `REFUSED:GCLOUD_PROJECT_MISMATCH`
- exit 12: `REFUSED:GGEN_SYNC_FAILED`
- exit 13: `REFUSED:RECEIPT_WRITE_FAILED`, `REFUSED:RECEIPT_READ_FAILED`

The entitlement CLI itself uses a narrower table
(0 = ok, 3 = unreachable, 4 = not active, 5 = invalid, 6 = registry
invalid); the deployer maps its sub-results into the ladder above.

## Receipt chain rule

Paid-delivery receipts use schema `ggen-receipt/v2` with the chain rule
`"paid-delivery-chain/v1"`: a plain fold
`chain_hash_hex = sha256(prev_chain_hash_hex ‖ payload_hash_hex)`, genesis
`prev_chain_hash_hex` = 64 zeros, `ts_ns = 0` always (replayable, not
timestamped). Layout: `receipts/paid-delivery/<slug>.json` one envelope per
delivery, `receipts/paid-delivery/chain.jsonl` append-only, one compact JSON
envelope per line. Verification is the es-chain verify-walk
(`scripts/es_chain_qualify.py`); a tampered line fails the walk. Out-of-band
anchoring: every append rewrites `receipts/paid-delivery/HEAD` to the chain
head hash, and `verify --anchor <hash-or-HEAD-file>` refuses with
`REFUSED_ANCHOR_MISMATCH` (naming both hexes) if the final chain head differs.

## Solution lock regeneration

`scripts/regen_solution_lock.py --check`/`--regen` recomputes pack folds via
the deployer's own `input_folds` (the same helper the quickstart imports);
a stale lock exits 9 with `REFUSED:LOCK_STALE` plus the diff. The quickstart
(`scripts/run_solution_quickstart.py`) refuses `REFUSED:LOCK_DRIFT` on
repo-vs-lock drift (`--accept-drift` regenerates deliberately) and
`REFUSED:SYMLINK_IN_SOURCE` on any symlink in source.

## Typed standings

- `backend_standing`: `SIMULATED` when the monetization backend is `sim`;
  the vocabulary also carries `EXACT_PROVIDER` for the real backend. With
  `backend = "real"`, the seam refuses with
  `REFUSED_ENTITLEMENT_REAL_NOT_PERMITTED` and the run is `BLOCKED` — real
  vendor onboarding is the only flip, and it is a registry line plus an
  external onboarding act, not a code path.
- `target_standing`: kind targets report the local rail's standing;
  `gke` targets report `BLOCKED` until a real actuation receipt exists.
  Plan bytes are identical for both targets on the same inputs.

The executable source for these fields is
`scripts/entitlement.py` and `scripts/deploy_aaif_solution.py`; this
document does not restate their internal counts or current standing values.

## Security posture

The commerce plane verifies entitlements instead of trusting them.

- **JWT verification** (`scripts/entitlement.py` `_verify_jwt`): the record's
  JWT must be RS256 (alg checked; `none` is refused), with a non-empty `kid`
  resolved through the x509 metadata map fetched from
  `{base_url}/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com`.
  The signing key is the certificate's public key. Claims checked: `iss` must
  match exactly one backend-scoped value — the metadata URL actually fetched on
  the sim rail, the canonical Google robot URL on the real rail (never both) —
  `aud` must equal the provider id, and `exp` must be a positive
  integer in the future.
- **Loopback pinning**: an `AAIF_ENTITLEMENT_ENDPOINT` override must resolve
  to a loopback host unless `AAIF_ENTITLEMENT_ALLOW_REMOTE=1` is set;
  otherwise the decision is `REFUSED_ENDPOINT_NOT_LOOPBACK`.
- **Id validation**: `entitlement_id` is interpolated into URLs, so only
  `^[A-Za-z0-9._-]{1,128}$` is accepted (`REFUSED_ID_INVALID`).
- **Receipt chain fold** (`scripts/paid_delivery_receipt.py`): verify
  recomputes the chain hash over every envelope and refuses on any field,
  schema, chain-rule, timestamp, payload-hash, prev-chain, or fold mismatch;
  per-slug files must match their chain lines exactly. Append rewrites the
  `HEAD` anchor file with the new chain head hash.
- **HEAD anchor**: tamper evidence is *comparison, not unforgeability* — the
  anchor proves nothing by itself; detection requires comparing `HEAD`
  against an out-of-band copy of the head hash taken at grant time. An
  attacker who rewrites the whole chain including `HEAD` is not stopped by
  the anchor alone.
- **Forged-prior refusal** (`scripts/deploy_aaif_solution.py`
  `prior_receipt`): a prior receipt grants redeploy only if the slug file
  exists, the FULL chain verifies, and the stored `payload_hash_hex`
  recomputes from the embedded payload. Anything else — forged, corrupt, or
  unverifiable — is `REFUSED:PRIOR_RECEIPT_INVALID` (exit 13); redeploy is
  never granted from an unverified receipt.
- **Sim `:report` gate** (`k8s/gcp-marketplace-sim/server.py`): usage
  reports must correlate a consumerId to an `ENTITLEMENT_ACTIVE` record
  (directly or through the consumer->entitlement binding); an unresolvable
  or inactive consumer gets HTTP 403 `ENTITLEMENT_REQUIRED` and no revenue
  or report record is counted.

## See also

- `tutorials/deploy-an-aaif-solution.md`
- `how-to/run-the-kind-commerce-rail.md`
- `explanation/aaif-commerce-seams.md`
