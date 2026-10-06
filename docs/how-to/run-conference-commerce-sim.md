# Run the Conference-Commerce Simulation

How to run the conference-commerce courts: a simulation in which every company at
a trade-show event becomes a GCP Marketplace customer and is taken through
registration, credentialing, provisioning, metering, billing, and isolation
courts over the real marketplace machinery.

## Run it

From the repo root:

```bash
python3 -m pytest tests/test_conference_*.py -q
```

Prerequisite: `ggen` on `PATH` (courts refuse with
`REFUSED:GGEN_NOT_FOUND` otherwise). No Docker/Postgres or other external
services are required — the simulation is in-process over the real marketplace
calculus (`scripts/marketplace.py`) and the fixture in
`tests/test_conference_commerce_fixture.py`.

CI runs the same files through the full-suite job (`.github/workflows/ci.yml`,
`tests` job) with no dedicated wiring: the default `pytest tests/` invocation
already collects `tests/test_conference_*.py`.

## What it simulates

Each simulated conference attendee company registers as a marketplace customer,
receives signed credentials, is provisioned (graph-hash-unique per customer,
byte-identical on redeploy), is metered and billed, and is fenced from every
other customer's artifacts. The courts assert on final state (Chicago style):
real generated manifests, real receipts, real admission decisions — no mocks.

## Court families and what each proves

| File | Court | Proves |
|---|---|---
| `tests/test_conference_commerce_fixture.py` | Fixture | Shared in-process fixture: registration of every company, singleton teardown |
| `tests/test_conference_registration_court.py` | Registration | Every company can be admitted as a customer over the real marketplace source calculus |
| `tests/test_conference_signed_credential_court.py` | Signed credentials | Credential issuance/verification over the affidavit wasm verify surface (ED25519/ES256K) |
| `tests/test_conference_provisioning_court.py` | Provisioning | Full artifact set per customer; actuation plans target the customer solution; graph hash unique per customer; byte-identical redeploy; receipt chain grows exactly once per deploy |
| `tests/test_conference_metering_court.py` | Metering | Every report admitted with distinct units; billing summary matches an independently computed expected total |
| `tests/test_conference_billing_court.py` | Billing | Billing over metered usage with receipted totals |
| `tests/test_conference_isolation_court.py` | Isolation | No manifest or receipt bleed between customers; account list vs. detail scoping |
| `tests/test_conference_dod_crosscheck_court.py` | DoD crosscheck | Conference DoD crosschecked against real marketplace machinery |
| `tests/test_conference_mcp_booth_court.py` | MCP booth | Conference-sim MCP booth over real marketplace machinery |

## Known dependencies between courts

Metering asserts it runs after the admission court (shared fixture state) —
run the suite as a whole (single pytest invocation), not per-file, when
exercising fixture-dependent courts.
