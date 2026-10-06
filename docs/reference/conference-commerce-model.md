# Conference Commerce Model

Reference for the AGNTCon conference-commerce simulation (CG lanes, v26.10.5):
the event's exhibitor floor replayed as GCP Marketplace commerce over the
real sim and real marketplace machinery.

## Event-to-commerce mapping

| Conference concept | Commerce object | Machinery |
|---|---|---|
| Registration | Entitlement purchase | account + entitlement `:approve` on the sim |
| Attendee badge | Signed credential | ES256 (P-256), verified only by the pinned affidavit WASM |
| Session attendance | Usage metering | `:report` usage ops through the Service Control sim |
| Sponsor tier | Plan level | `sponsor`/`platinum` -> `enterprise-aaif`; others -> `team-aaif` |
| Exhibitor booth | Pack + qualification | `marketplace.py catalog`; demos run `qualify_packs.py` |

Machinery root: `k8s/gcp-marketplace-sim/server.py`.

## Court families

All courts live in `tests/` over the CG1 fixture
(`test_conference_commerce_fixture.py`: real sim subprocess, real approvals,
real deployer subprocess — no mocks).

Registration — `test_conference_registration_court.py`:
entitlement gate before manufacture; purchase precedes wire actuation;
idempotent double-purchase; expired card refused pre-wire.
Provisioning — `test_conference_provisioning_court.py`:
pay-before-manufacture deploy (`deploy_aaif_solution.py`); unique
per-customer digest; byte-identical redeploy; receipt chain +1, no forks.
Metering — `test_conference_metering_court.py`:
every report admitted; quota overflow refused (`RESOURCE_EXHAUSTED`),
moves no units; per-tenant attribution.
Billing — `test_conference_billing_court.py`:
revenue conservation; the sim summary is held against an independently
computed sum, never read back.
Isolation — `test_conference_isolation_court.py`:
multi-tenant boundary; cross-customer fetch is 404 (not 403); no manifest
bleed; no cross-tenant actuation or misattributed usage.
DoD cross-check — `test_conference_dod_crosscheck_court.py`:
the definition-of-done court on sim evidence; PARTIAL_ALIVE, never ALIVE;
billing-authority cardinality and subject-mismatch typed refusals.
Signed credential — `test_conference_signed_credential_court.py`:
key-trust story; host signs (ES256/DER, low-s); pinned WASM sole verifier;
domain-separated subject digest.
MCP booth — `test_conference_mcp_booth_court.py`:
a demo is a real qualification; injected defect must FAIL; catalog
determinism holds while the event runs.

## Honest scope

Simulated (sim-mode, `PARTIAL_ALIVE` standing):

- protocol behavior of the purchase/metering/deploy surfaces at bounded
  scale (25 companies; 10-customer courts);
- entitlement gating, quota refusals, revenue conservation at the sim
  boundary.

Not simulated / not claimed:

- real GCP billing or provider push notifications;
- real vendor onboarding, contracting, or invoicing;
- real 1,000-company scale — companies are 25 named fixtures;
- ALIVE standing for purchases: the DoD court refuses ALIVE without
  `exact_provider` evidence by construction.

## Thesis tie

The event's companies are mu over admitted purchases: each company acts only
after its entitlement `:approve` (A = mu(O*); purchases are the admitted O*).
Paid-delivery receipts form the commerce chain — one link per customer, no
forks, idempotent under redeploy — so the receipt chain is the ledger.
Standing is the tier model: `enterprise-aaif` and `team-aaif` are standing
levels a company holds by purchase, and the DoD court caps the whole event
at PARTIAL_ALIVE until a real provider boundary is exercised.

## See Also

- `docs/reference/pack-classes.md`
- `packs/chatman-marketplace-commerce-dod-pack/`
